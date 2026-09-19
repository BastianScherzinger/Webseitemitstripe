"""Motiv anfragen (``/motiv-anfragen/``) – Luisas Anfrage-System, Stufe 1.

Seit dem Umbau „Nachtausgabe" (19.09.2026) der zweite Weg, auf dem Fremde
Daten in dieses Projekt schreiben. Geprüft wird, was die Funktion rechtlich
und praktisch trägt: Anfrage ohne Preis und Zusage, Mail **nur** an Luisa,
nie an die eingetippte Adresse, Spam still verworfen, Schalter wirkt.

Der Mailversand wird in jedem Test ersetzt (siehe ``test_formulare``).
"""

from unittest import mock

from django.test import override_settings

from .. import spamschutz
from ..models import Motivanfrage
from ._basis import LuviqTestCase

_MAIL = 'shop1.views.motiv.send_brevo_email'

GUELTIG = {
    'richtung': 'tier',
    'teil': 'hoodie',
    'platzierung': 'ruecken',
    'bedeutung': 'Ein Drache für meinen Bruder, eher verspielt als böse.',
    'instagram': '@erika.muster',
    'email': '',
}


class AnzeigeTest(LuviqTestCase):

    def test_die_seite_antwortet_und_zeigt_alle_auswahlen(self):
        html = self.hole('/motiv-anfragen/').content.decode()
        for wert in ('tier', 'symbol', 'pflanze', 'himmel', 'abstrakt', 'offen',
                     'hoodie', 'sweatshirt', 'jeans', 'shirt', 'eigenes', 'ruecken', 'vorne'):
            with self.subTest(wert=wert):
                self.assertIn(f'value="{wert}"', html)
        self.assertEqual(html.count('<fieldset>'), 3)
        self.assertEqual(html.count('<legend>'), 3)

    def test_die_richtung_laesst_sich_ueber_die_adresse_vorbelegen(self):
        html = self.hole('/motiv-anfragen/?richtung=himmel').content.decode()
        self.assertRegex(html, r'value="himmel" required checked')
        self.assertNotRegex(html, r'value="tier" required checked')

    def test_eine_unbekannte_vorbelegung_wird_ignoriert(self):
        html = self.hole('/motiv-anfragen/?richtung=<script>').content.decode()
        self.assertNotIn(' checked', html)
        self.assertNotIn('<script>"', html)

    def test_die_seite_nennt_keinen_preis_und_keine_zusage(self):
        """Stufe 1 ohne Gewerbe: eine Anfrage, keine Bestellung (Bauplan § 3e)."""
        html = self.hole('/motiv-anfragen/').content.decode()
        self.assertIn('keine Bestellung', html)
        for wort in ('€', 'Preis', 'kaufen', 'garantiert', 'Lieferzeit'):
            with self.subTest(wort=wort):
                self.assertNotIn(wort, html)

    def test_die_startseite_verlinkt_jede_richtung(self):
        html = self.hole('/').content.decode()
        for wert in ('tier', 'symbol', 'pflanze', 'himmel', 'abstrakt', 'offen'):
            with self.subTest(wert=wert):
                self.assertIn(f'href="/motiv-anfragen/?richtung={wert}"', html)

    def test_das_formular_traegt_zeitstempel_und_versteckte_falle(self):
        import re
        html = self.hole('/motiv-anfragen/').content.decode()
        self.assertIn('name="formzeit"', html)
        feld = re.search(rf'<input[^>]*name="{spamschutz.FELD_FALLE}"[^>]*>', html).group(0)
        for merkmal in ('aria-hidden="true"', 'tabindex="-1"', 'autocomplete="off"', 'class="lv-falle"'):
            self.assertIn(merkmal, feld)

    def test_die_danke_seite_ist_noindex_und_zeigt_nichts_aus_der_anfrage(self):
        antwort = self.hole('/motiv-anfragen/danke/')
        self.assertEqual(antwort.status_code, 200)
        self.assertContains(antwort, 'noindex')
        self.assertContains(antwort, 'melde mich persönlich')


class AbsendenTest(LuviqTestCase):

    def test_eine_gueltige_anfrage_wird_gespeichert_und_einmal_an_luisa_gemailt(self):
        with mock.patch(_MAIL) as versand, mock.patch.dict('os.environ', {'ADMIN_EMAIL': 'luisa@example.invalid'}):
            antwort = self.sende('/motiv-anfragen/', GUELTIG)
        self.assertRedirects(antwort, '/motiv-anfragen/danke/', fetch_redirect_response=False)
        self.assertEqual(Motivanfrage.objects.count(), 1)
        anfrage = Motivanfrage.objects.get()
        self.assertEqual(anfrage.instagram, 'erika.muster')
        self.assertEqual(anfrage.status, 'neu')
        self.assertTrue(anfrage.mail_gestartet)
        self.assertEqual(versand.call_count, 1)
        self.assertEqual(versand.call_args.args[2], 'luisa@example.invalid')

    @override_settings(MOTIV_EMPFAENGER='atelier@example.invalid')
    def test_ein_eigener_empfaenger_hat_vorrang(self):
        with mock.patch(_MAIL) as versand:
            self.sende('/motiv-anfragen/', GUELTIG)
        self.assertEqual(versand.call_args.args[2], 'atelier@example.invalid')

    def test_an_die_eingetippte_adresse_geht_keine_mail(self):
        """Lehre vom 17.09.2026: Bots tragen fremde Adressen ein. Die Adresse
        der Absenderin steht höchstens als Antwortadresse in Luisas Mail."""
        daten = dict(GUELTIG, email='opfer@example.invalid')
        with mock.patch(_MAIL) as versand:
            self.sende('/motiv-anfragen/', daten)
        self.assertEqual(versand.call_count, 1)
        empfaenger = [aufruf.args[2] for aufruf in versand.call_args_list]
        self.assertNotIn('opfer@example.invalid', empfaenger)

    def test_nutzertext_wird_in_der_mail_maskiert(self):
        daten = dict(GUELTIG, bedeutung='<b>fett</b> & <script>x</script>')
        with mock.patch(_MAIL) as versand:
            self.sende('/motiv-anfragen/', daten)
        html = versand.call_args.args[1]
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_jede_auswahl_ist_pflicht(self):
        for feld in ('richtung', 'teil', 'platzierung'):
            with self.subTest(feld=feld), mock.patch(_MAIL) as versand:
                daten = dict(GUELTIG)
                daten.pop(feld)
                antwort = self.sende('/motiv-anfragen/', daten)
                self.assertEqual(antwort.status_code, 200)
                self.assertContains(antwort, 'role="alert"')
                versand.assert_not_called()
        self.assertEqual(Motivanfrage.objects.count(), 0)

    def test_eine_erfundene_auswahl_wird_abgewiesen(self):
        with mock.patch(_MAIL) as versand:
            self.sende('/motiv-anfragen/', dict(GUELTIG, richtung='einhorn'))
        versand.assert_not_called()
        self.assertEqual(Motivanfrage.objects.count(), 0)

    def test_ohne_instagram_und_ohne_mail_geht_nichts_hinaus(self):
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/motiv-anfragen/', dict(GUELTIG, instagram='', email=''))
        self.assertContains(antwort, 'Instagram-Namen oder deine E-Mail-Adresse')
        versand.assert_not_called()

    def test_eins_von_beiden_genuegt(self):
        for daten in (dict(GUELTIG, email=''), dict(GUELTIG, instagram='', email='erika@example.invalid')):
            with self.subTest(daten=daten), mock.patch(_MAIL) as versand:
                antwort = self.sende('/motiv-anfragen/', dict(daten, bedeutung=daten['bedeutung'] + str(id(daten))))
                self.assertEqual(antwort.status_code, 302)
                self.assertEqual(versand.call_count, 1)

    def test_ungueltige_kontaktangaben_werden_abgewiesen(self):
        for daten in (dict(GUELTIG, instagram='https://instagram.com/x'),
                      dict(GUELTIG, instagram='', email='keine-adresse')):
            with self.subTest(daten=daten), mock.patch(_MAIL) as versand:
                self.sende('/motiv-anfragen/', daten)
                versand.assert_not_called()

    def test_ueberlanger_text_wird_abgewiesen(self):
        with mock.patch(_MAIL) as versand:
            self.sende('/motiv-anfragen/', dict(GUELTIG, bedeutung='x' * 1501))
        versand.assert_not_called()

    def test_spam_wird_still_verworfen(self):
        """Die Falle ist ausgefüllt: dieselbe Danke-Seite, aber weder Eintrag noch Mail."""
        daten = dict(GUELTIG, **{spamschutz.FELD_FALLE: 'https://spam.example'})
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/motiv-anfragen/', daten)
        self.assertRedirects(antwort, '/motiv-anfragen/danke/', fetch_redirect_response=False)
        versand.assert_not_called()
        self.assertEqual(Motivanfrage.objects.count(), 0)

    def test_ein_doppelklick_speichert_nur_einmal(self):
        with mock.patch(_MAIL) as versand:
            self.sende('/motiv-anfragen/', GUELTIG)
            self.sende('/motiv-anfragen/', GUELTIG)
        self.assertEqual(Motivanfrage.objects.count(), 1)
        self.assertEqual(versand.call_count, 1)

    def test_scheitert_der_versand_bleibt_die_anfrage_gespeichert(self):
        with mock.patch(_MAIL, side_effect=RuntimeError('Brevo weg')):
            antwort = self.sende('/motiv-anfragen/', GUELTIG)
        self.assertEqual(antwort.status_code, 302)
        anfrage = Motivanfrage.objects.get()
        self.assertFalse(anfrage.mail_gestartet)

    def test_viele_anfragen_derselben_adresse_werden_gedrosselt(self):
        from ..views._helpers import ANFRAGE_GRENZE
        with mock.patch(_MAIL):
            for nummer in range(ANFRAGE_GRENZE):
                self.sende('/motiv-anfragen/', dict(GUELTIG, bedeutung=f'Anfrage {nummer}'))
            antwort = self.sende('/motiv-anfragen/', dict(GUELTIG, bedeutung='eine zu viel'))
        self.assertEqual(antwort.status_code, 429)


@override_settings(MOTIVANFRAGE_AKTIV=False)
class AbgeschaltetTest(LuviqTestCase):

    def test_die_seite_sagt_gerade_keine_anfragen_und_hat_kein_formular(self):
        html = self.hole('/motiv-anfragen/').content.decode()
        self.assertIn('keine neuen Motivanfragen', html)
        self.assertNotIn('name="richtung"', html)

    def test_absenden_speichert_und_mailt_nichts(self):
        with mock.patch(_MAIL) as versand:
            self.sende('/motiv-anfragen/', GUELTIG)
        versand.assert_not_called()
        self.assertEqual(Motivanfrage.objects.count(), 0)

    def test_die_startseite_zeigt_keinen_anfrageknopf(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('href="/motiv-anfragen/', html)


class AdminTest(LuviqTestCase):

    def test_die_liste_ist_nur_fuer_die_betreiberin(self):
        from django.contrib.auth.models import User
        self.assertNotEqual(self.hole('/shop-admin/motivanfragen/').status_code, 200)
        chefin = User.objects.create_superuser('chefin', 'c@example.invalid', 'ein-langes-passwort')
        self.client.force_login(chefin)
        Motivanfrage.objects.create(richtung='tier', teil='jeans', platzierung='vorne', instagram='erika')
        antwort = self.hole('/shop-admin/motivanfragen/')
        self.assertEqual(antwort.status_code, 200)
        self.assertContains(antwort, '@erika')

    def test_der_status_laesst_sich_setzen(self):
        from django.contrib.auth.models import User
        chefin = User.objects.create_superuser('chefin', 'c@example.invalid', 'ein-langes-passwort')
        self.client.force_login(chefin)
        anfrage = Motivanfrage.objects.create(richtung='tier', teil='jeans', platzierung='vorne', instagram='erika')
        self.sende('/shop-admin/motivanfragen/', {'anfrage': anfrage.pk, 'status': 'erledigt'})
        anfrage.refresh_from_db()
        self.assertEqual(anfrage.status, 'erledigt')
