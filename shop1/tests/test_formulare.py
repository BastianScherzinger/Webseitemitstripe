"""Kontakt- und Newsletterformular – die einzigen Wege, auf denen Fremde
Daten in dieses Projekt schreiben.

Der Mailversand wird in jedem Test ersetzt. ``send_brevo_email`` startet einen
Thread und ruft die Brevo-HTTP-Schnittstelle auf; ein Test, der das echte
Verhalten benutzt, wäre langsam, netzabhängig und würde tatsächlich Post
verschicken.
"""

import json
from unittest import mock

from django.test import Client
from django.urls import reverse

from ..models import KontaktAnfrage, Subscriber
from ..views._helpers import ANFRAGE_GRENZE
from ._basis import LuviqTestCase

_MAIL = 'shop1.views.shop.send_brevo_email'

GUELTIGE_ANFRAGE = {
    'name': 'Erika Musterfrau',
    'email': 'erika@example.invalid',
    'betreff': 'Frage zu einer Jacke',
    'nachricht': 'Gibt es die bemalte Jeansjacke auch in Größe M?',
}


class KontaktformularTest(LuviqTestCase):
    """Das Anfrageformular – wenn es bricht, kommt keine Anfrage mehr an."""

    def test_gueltige_anfrage_wird_genau_einmal_verschickt(self):
        """Verhindert den unauffälligsten aller Ausfälle: das Formular meldet
        Erfolg, verschickt aber nichts – oder verschickt doppelt."""
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(versand.call_count, 1)

    def test_nach_dem_absenden_steht_die_bestaetigung_auf_eigener_adresse(self):
        """Verhindert, dass die Bestätigung wieder als Meldung auf ``/kontakt/``
        erscheint (KV07): ohne eigene Adresse ist kein abgeschicktes Formular
        zählbar, und Neuladen schickte die Anfrage ein zweites Mal ab."""
        # Ohne follow=True: der Testclient folgte der Weiterleitung über HTTP
        # und prüfte dann nur die 301 von SECURE_SSL_REDIRECT (_basis, Punkt 1).
        with mock.patch(_MAIL) as versand:
            weiter = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertEqual(weiter.status_code, 302)
        antwort = self.hole(weiter['Location'])
        self.assertEqual(antwort.status_code, 200)
        self.assertTemplateUsed(antwort, 'shop1/kontakt_danke.html')
        self.assertContains(antwort, 'Deine Nachricht ist abgeschickt.')
        self.assertNotContains(antwort, 'erfolgreich gesendet')
        self.assertEqual(versand.call_count, 1)

    def test_scheitert_der_versand_bleibt_die_anfrage_gespeichert(self):
        """Verhindert, dass ein kaputter Mailweg eine Anfrage verschluckt
        (MW18): sie steht vor dem Versand in ``KontaktAnfrage``, und die
        Besucherin sieht die Bestätigung statt einer Aufforderung, es noch
        einmal zu versuchen."""
        with mock.patch(_MAIL, side_effect=RuntimeError('kein Versand')):
            antwort = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        anfrage = KontaktAnfrage.objects.get()
        self.assertEqual(anfrage.email, GUELTIGE_ANFRAGE['email'])
        self.assertEqual(anfrage.nachricht, GUELTIGE_ANFRAGE['nachricht'])
        self.assertFalse(anfrage.mail_gestartet)

    def test_die_anfrage_steht_in_der_datenbank_bevor_die_mail_startet(self):
        """Verhindert, dass die Reihenfolge still kippt: im Augenblick des
        Versands ist die Anfrage schon gespeichert, danach als versandt
        vermerkt."""
        gezaehlt = []
        with mock.patch(_MAIL, side_effect=lambda *a, **k: gezaehlt.append(
                KontaktAnfrage.objects.filter(betreff=GUELTIGE_ANFRAGE['betreff']).count())):
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertEqual(gezaehlt, [1])
        self.assertTrue(KontaktAnfrage.objects.get().mail_gestartet)

    def test_ohne_speicher_geht_die_anfrage_trotzdem_als_mail_hinaus(self):
        """Gegenprobe: fällt die Datenbank aus, trägt der Mailweg die Anfrage
        allein – die Besucherin sieht die Bestätigung."""
        from django.db import DatabaseError
        with mock.patch.object(KontaktAnfrage.objects, 'create', side_effect=DatabaseError('weg')), \
                mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(versand.call_count, 1)

    def test_scheitern_speicher_und_versand_bleibt_die_anfrage_auf_der_kontaktseite(self):
        """Gegenprobe: ist die Anfrage weder gespeichert noch verschickt, darf
        sie nicht auf die Bestätigung führen."""
        from django.db import DatabaseError
        with mock.patch.object(KontaktAnfrage.objects, 'create', side_effect=DatabaseError('weg')), \
                mock.patch(_MAIL, side_effect=RuntimeError('kein Versand')):
            antwort = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertEqual(antwort.status_code, 200)
        self.assertTemplateUsed(antwort, 'shop1/kontakt.html')
        self.assertContains(antwort, 'Problem beim Senden')

    def test_die_anfragen_stehen_in_der_verwaltung(self):
        """Verhindert, dass gespeicherte Anfragen nur per Datenbankzugriff
        lesbar sind: das Modell ist im Django-Admin registriert."""
        from django.contrib import admin
        self.assertIn(KontaktAnfrage, admin.site._registry)

    def test_abgewiesene_anfragen_werden_nicht_gespeichert(self):
        """Verhindert, dass ungültige Eingaben die Tabelle füllen."""
        with mock.patch(_MAIL):
            self.sende('/kontakt/', dict(GUELTIGE_ANFRAGE, email='keine-adresse'))
            self.sende('/kontakt/', {})
        self.assertFalse(KontaktAnfrage.objects.exists())

    def test_leeres_formular_verschickt_nichts_und_meldet_das(self):
        """Verhindert, dass ein leeres Formular als gültige Anfrage durchgeht –
        das Postfach der Betreiberin füllt sich sonst mit Leermeldungen."""
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', {})
        self.assertEqual(antwort.status_code, 200)
        versand.assert_not_called()
        self.assertContains(antwort, 'Bitte fülle alle Felder aus')

    def test_jedes_pflichtfeld_wird_einzeln_verlangt(self):
        """Verhindert, dass eine Anfrage ohne Absenderadresse oder ohne Text
        ankommt und niemand darauf antworten kann."""
        for feld in GUELTIGE_ANFRAGE:
            daten = dict(GUELTIGE_ANFRAGE, **{feld: ''})
            with self.subTest(feld=feld), mock.patch(_MAIL) as versand:
                antwort = self.sende('/kontakt/', daten)
                versand.assert_not_called()
                self.assertContains(antwort, 'Bitte fülle alle Felder aus')

    def test_reine_leerzeichen_gelten_nicht_als_ausgefuellt(self):
        """Verhindert den billigsten Spamtrick auf diesem Formular: alle Felder
        mit einem Leerzeichen füllen. Ohne Prüfung auf echten Inhalt zählt das
        als gültige Anfrage und erzeugt eine leere Mail."""
        daten = {feld: '   ' for feld in GUELTIGE_ANFRAGE}
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', daten)
        versand.assert_not_called()
        self.assertContains(antwort, 'Bitte fülle alle Felder aus')

    def test_ungueltige_absenderadresse_verschickt_nichts(self):
        """Verhindert Anfragen, auf die niemand antworten kann (FO06): das
        ``type="email"`` im Formular umgeht jeder Abruf ohne Browser."""
        for adresse in ('keine-adresse', 'a@b', 'erika@@example.invalid'):
            daten = dict(GUELTIGE_ANFRAGE, email=adresse)
            with self.subTest(adresse=adresse), mock.patch(_MAIL) as versand:
                antwort = self.sende('/kontakt/', daten)
                self.assertEqual(antwort.status_code, 200)
                versand.assert_not_called()
                self.assertContains(antwort, 'gültige E-Mail-Adresse')

    def test_ueberlange_eingaben_verschicken_nichts(self):
        """Verhindert, dass ein Skript ein Megabyte Text in die Mail an die
        Betreiberin schreibt (FO06) – jedes Feld hat eine Obergrenze."""
        from ..views.shop import KONTAKT_LAENGEN
        for feld, grenze in KONTAKT_LAENGEN.items():
            wert = 'x' * (grenze + 1)
            if feld == 'email':
                wert = 'x' * (grenze - len('@example.invalid') + 1) + '@example.invalid'
            daten = dict(GUELTIGE_ANFRAGE, **{feld: wert})
            with self.subTest(feld=feld), mock.patch(_MAIL) as versand:
                antwort = self.sende('/kontakt/', daten)
                versand.assert_not_called()
                self.assertContains(antwort, 'zu lang')

    def test_jedes_feld_begrenzt_die_eingabe_wie_der_server(self):
        """Verhindert, dass jemand einen langen Text schreibt und erst nach dem
        Absenden „zu lang“ liest (FO07): ``maxlength`` im Formular entspricht
        genau der Grenze, die ``kontakt_fehler`` prüft."""
        import re
        from ..views.shop import KONTAKT_LAENGEN
        inhalt = self.hole('/kontakt/').content.decode()
        form = inhalt.split('name="formzeit"', 1)[1].split('</form>', 1)[0]
        for feld, grenze in KONTAKT_LAENGEN.items():
            with self.subTest(feld=feld):
                tag = re.search(rf'<(?:input|textarea)[^>]*name="{feld}"[^>]*>', form).group(0)
                self.assertIn(f'maxlength="{grenze}"', tag)

    def test_eine_nachricht_an_der_grenze_mit_zeilenumbruechen_geht_durch(self):
        """Verhindert, dass der Server ablehnt, was ``maxlength`` erlaubt hat:
        der Browser zählt einen Umbruch als ein Zeichen, schickt aber ``\\r\\n``."""
        from ..views.shop import KONTAKT_LAENGEN
        grenze = KONTAKT_LAENGEN['nachricht']
        nachricht = ('x' * 9 + '\r\n') * (grenze // 10)
        self.assertGreater(len(nachricht), grenze)
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', dict(GUELTIGE_ANFRAGE, nachricht=nachricht))
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(versand.call_count, 1)

    def test_zeilenumbrueche_gelangen_nicht_in_die_betreffzeile(self):
        """Verhindert das Einschleusen von Kopfzeilen (Header Injection): ein
        Zeilenumbruch im Betreff könnte sonst zusätzliche Empfänger oder einen
        fremden Absender in die Mail schreiben."""
        daten = dict(
            GUELTIGE_ANFRAGE,
            betreff='Hallo\r\nBcc: fremder@example.invalid',
            name='Ich\nX-Spam: nein',
        )
        with mock.patch(_MAIL) as versand:
            self.sende('/kontakt/', daten)
        betreff = versand.call_args.args[0]
        self.assertNotIn('\n', betreff)
        self.assertNotIn('\r', betreff)

    def test_jedes_pflichtfeld_ist_sichtbar_gekennzeichnet(self):
        """Verhindert, dass ein Pflichtfeld erst nach dem Absenden auffällt
        (FO04): jedes ``required``-Feld trägt den Stern in der Beschriftung,
        „Pflichtfeld“ im zugänglichen Namen, und die Seite erklärt den Stern."""
        import re
        inhalt = self.hole('/kontakt/').content.decode()
        form = inhalt.split('name="formzeit"', 1)[1].split('</form>', 1)[0]
        felder = re.findall(r'<label[^>]*>([^<]*)</label>\s*<(?:input|textarea)([^>]*)>', form)
        pflicht = [(label, attrs) for label, attrs in felder if ' required' in attrs]
        self.assertEqual(len(pflicht), 4)
        for label, attrs in pflicht:
            with self.subTest(label=label):
                self.assertTrue(label.strip().endswith('*'))
                self.assertRegex(attrs, r'aria-label="[^"]*\(Pflichtfeld\)"')
        self.assertIn('mit einem Stern (*) gekennzeichnet', inhalt)

    def test_das_formular_nennt_den_datenschutz(self):
        """Verhindert, dass jemand Namen und Adresse abschickt, ohne zu lesen,
        was damit geschieht (KV05, Art. 13 DSGVO): der Hinweis steht **im**
        Formular, nennt die Datenschutzerklärung mit ihrer Adresse und die
        Stelle für Auskunft und Löschung."""
        inhalt = self.hole('/kontakt/').content.decode()
        form = inhalt.split('name="formzeit"', 1)[1].split('</form>', 1)[0]
        self.assertIn('Datenschutz', form)
        self.assertIn(reverse('datenschutz'), form)
        self.assertIn('Löschung', form)

    def test_anfrage_ohne_csrf_token_wird_abgewiesen(self):
        """Verhindert, dass eine fremde Seite im Namen einer Besucherin
        Anfragen abschickt – der CSRF-Schutz muss an diesem Formular greifen."""
        streng = Client(enforce_csrf_checks=True)
        with mock.patch(_MAIL) as versand:
            antwort = streng.post('/kontakt/', GUELTIGE_ANFRAGE, secure=True)
        self.assertEqual(antwort.status_code, 403)
        versand.assert_not_called()


class DoppeltesAbsendenTest(LuviqTestCase):
    """Ein Doppelklick erzeugt keine zweite Mail (FO03)."""

    def test_eine_wortgleiche_zweite_anfrage_verschickt_nichts_und_bestaetigt(self):
        """Verhindert zwei Mails aus einem Doppelklick – der Absender sieht
        trotzdem die Bestätigung, nicht eine Fehlermeldung."""
        with mock.patch(_MAIL) as versand:
            erste = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
            zweite = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertRedirects(erste, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertRedirects(zweite, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(versand.call_count, 1)

    def test_eine_echte_zweite_anfrage_geht_hinaus(self):
        """Gegenprobe: eine zweite Frage mit anderem Text oder Betreff ist
        kein Doppel und darf nicht stumm verschwinden."""
        with mock.patch(_MAIL) as versand:
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
            self.sende('/kontakt/', dict(GUELTIGE_ANFRAGE, nachricht='Und in Größe L?'))
            self.sende('/kontakt/', dict(GUELTIGE_ANFRAGE, betreff='Frage zum Versand'))
        self.assertEqual(versand.call_count, 3)

    def test_nach_dem_zeitfenster_geht_dieselbe_anfrage_wieder_hinaus(self):
        """Verhindert, dass eine bewusst wiederholte Anfrage für immer
        verschluckt wird: der Merker gilt nur kurz."""
        from django.core.cache import cache
        from ..views.shop import _doppelt_schluessel
        with mock.patch(_MAIL) as versand:
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
            cache.delete(_doppelt_schluessel(GUELTIGE_ANFRAGE['email'],
                                             GUELTIGE_ANFRAGE['betreff'],
                                             GUELTIGE_ANFRAGE['nachricht']))
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertEqual(versand.call_count, 2)

    def test_nach_einem_fehlgeschlagenen_versand_zaehlt_der_neue_versuch(self):
        """Verhindert, dass eine Anfrage, die weder gespeichert noch versandt
        wurde, beim zweiten Versuch als Doppel verworfen wird."""
        from django.db import DatabaseError
        with mock.patch.object(KontaktAnfrage.objects, 'create', side_effect=DatabaseError('weg')), \
                mock.patch(_MAIL, side_effect=RuntimeError('kein Versand')):
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(versand.call_count, 1)

    def test_ein_doppelklick_speichert_die_anfrage_nur_einmal(self):
        """Verhindert zwei gleiche Einträge in der Verwaltung (FO03, MW18)."""
        with mock.patch(_MAIL):
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertEqual(KontaktAnfrage.objects.count(), 1)

    def test_die_formulare_sperren_ihren_knopf_beim_absenden(self):
        """Verhindert, dass die Absendesperre im Browser still entfällt: das
        Kontaktformular trägt das Merkmal, das Skript in base.html wertet es
        aus, und die Newsletter-Anmeldung sperrt ihren Knopf selbst."""
        kontakt = self.hole('/kontakt/').content.decode()
        self.assertIn('data-einmal-absenden', kontakt.split('name="formzeit"')[0].rsplit('<form', 1)[1])
        self.assertIn("attr(form, 'data-einmal-absenden')", kontakt)
        startseite = self.hole('/').content.decode()
        self.assertIn('knopf.disabled = true;', startseite)
        self.assertIn("form.setAttribute('aria-busy', 'true');", startseite)


class KontaktDankeTest(LuviqTestCase):
    """Die Bestätigungsseite ``/kontakt/danke/`` (KV07)."""

    def test_die_seite_ist_direkt_abrufbar_und_zeigt_nichts_aus_einer_anfrage(self):
        """Verhindert, dass die Adresse nur im Ablauf funktioniert: ein
        Messwerkzeug oder ein Werbekonto ruft sie direkt auf. Sie darf dabei
        keine Daten einer früheren Anfrage zeigen."""
        with mock.patch(_MAIL):
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        fremd = Client()
        antwort = fremd.get('/kontakt/danke/', secure=True)
        self.assertEqual(antwort.status_code, 200)
        for wert in GUELTIGE_ANFRAGE.values():
            self.assertNotContains(antwort, wert)

    def test_die_seite_steht_nicht_im_suchindex(self):
        """Verhindert, dass eine Bestätigung ohne eigenen Inhalt in der
        Trefferliste landet: ``noindex, follow``, weder in der Sitemap noch in
        llms.txt."""
        inhalt = self.hole('/kontakt/danke/').content.decode()
        self.assertIn('<meta name="robots" content="noindex, follow">', inhalt)
        self.assertNotIn('/kontakt/danke/', self.hole('/sitemap.xml').content.decode())
        self.assertNotIn('/kontakt/danke/', self.hole('/llms.txt').content.decode())

    def test_die_seite_wird_nicht_zwischengespeichert(self):
        """Verhindert, dass ein Zwischenspeicher die Bestätigung ausliefert,
        ohne dass der Aufruf den Server erreicht – er fehlte dann im
        Besuchsprotokoll, an dem sich ein Abschluss ablesen lässt."""
        antwort = self.hole('/kontakt/danke/')
        self.assertIn('no-store', antwort['Cache-Control'])

    def test_die_seite_nennt_keine_andere_adresse_als_die_kontaktseite(self):
        """Verhindert erfundene Kontaktwege auf der Bestätigung: die E-Mail-
        Adresse muss dieselbe sein, die ``/kontakt/`` nennt."""
        danke = self.hole('/kontakt/danke/').content.decode()
        kontakt = self.hole('/kontakt/').content.decode()
        self.assertIn('mailto:brehlerluisa@gmail.com', danke)
        self.assertIn('mailto:brehlerluisa@gmail.com', kontakt)
        self.assertNotIn('tel:', danke)


class NewsletterTest(LuviqTestCase):
    """Die Newsletter-Anmeldung schreibt ohne Anmeldung in die Datenbank."""

    def test_anmeldung_legt_genau_einen_eintrag_an(self):
        """Verhindert, dass die Anmeldung Erfolg meldet, ohne zu speichern."""
        antwort = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.filter(email='neu@example.invalid').count(), 1)

    def test_anmeldung_ohne_adresse_wird_abgewiesen(self):
        """Verhindert leere Datensätze in der Abonnentenliste, an die später
        kein Newsletter zugestellt werden kann."""
        antwort = self.sende('/newsletter/subscribe/', {'email': '   '})
        self.assertEqual(antwort.status_code, 400)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_anmeldung_mit_ungueltiger_adresse_wird_abgewiesen(self):
        """Verhindert Datensätze, an die kein Newsletter zugestellt werden
        kann (FO06) – auch als JSON, wie das Skript der Startseite schickt."""
        for adresse in ('keine-adresse', 'a@b', 'x' * 250 + '@example.invalid'):
            with self.subTest(adresse=adresse):
                antwort = self.client.post(
                    '/newsletter/subscribe/', json.dumps({'email': adresse}),
                    content_type='application/json', secure=True)
                self.assertEqual(antwort.status_code, 400)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_zweite_anmeldung_erzeugt_keinen_zweiten_eintrag(self):
        """Verhindert doppelte Zustellung an dieselbe Adresse und – weil das
        Feld ``unique`` ist – einen Serverfehler beim zweiten Absenden."""
        Subscriber.objects.create(email='schon.da@example.invalid')
        antwort = self.sende('/newsletter/subscribe/', {'email': 'schon.da@example.invalid'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_nur_eine_neue_anmeldung_meldet_einen_abschluss(self):
        """Verhindert doppelt gezählte Anmeldungen (FO08): das Skript der
        Startseite löst sein Ereignis nur bei ``neu`` aus, eine Wiederholung
        derselben Adresse darf das nicht melden."""
        erste = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        zweite = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        self.assertIs(erste.json().get('neu'), True)
        self.assertNotIn('neu', zweite.json())

    def test_die_startseite_zaehlt_die_anmeldung_ohne_personendaten(self):
        """Verhindert, dass die Anmeldung wieder unzählbar auf der Seite
        endet (FO08) – und dass das Ereignis die Adresse mitschickt."""
        inhalt = self.hole('/').content.decode()
        self.assertIn("window.dataLayer.push({ event: 'generate_lead', lead_quelle: 'newsletter' })",
                      inhalt)
        self.assertIn('response.ok && data.neu', inhalt)
        push = inhalt.split('window.dataLayer.push(', 1)[1].split(')', 1)[0]
        self.assertNotIn('email', push)

    def test_anmeldung_per_get_ist_nicht_moeglich(self):
        """Verhindert, dass ein vorab geladener Link oder ein Bild in einer Mail
        fremde Adressen in die Abonnentenliste schreibt."""
        antwort = self.hole('/newsletter/subscribe/')
        self.assertEqual(antwort.status_code, 405)
        self.assertEqual(Subscriber.objects.count(), 0)


class NewsletterOptInTest(LuviqTestCase):
    """Double-Opt-in (17.09.2026): Bots haben auf der Agenturseite fremde
    Adressen eingetragen, und die Seite hat sie angeschrieben. Hier landete
    jede eingetippte Adresse ohne Rückfrage in der Newsletter-Liste."""

    _VERSAND = 'shop1.utils.send_brevo_email'

    def test_anmeldung_schickt_nur_einen_bestaetigungslink(self):
        with mock.patch(self._VERSAND) as versand:
            self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        self.assertFalse(Subscriber.objects.get().bestaetigt)
        self.assertEqual(versand.call_count, 1)
        _betreff, html, empfaenger = versand.call_args.args[:3]
        self.assertEqual(empfaenger, 'neu@example.invalid')
        self.assertIn('/newsletter/bestaetigen/?t=', html)

    def test_hoechstens_ein_link_je_adresse_am_tag(self):
        with mock.patch(self._VERSAND) as versand:
            for nummer in range(3):
                self.sende('/newsletter/subscribe/', {'email': 'opfer@example.invalid'},
                           REMOTE_ADDR=f'198.51.100.{nummer}')
        self.assertEqual(versand.call_count, 1)

    def test_der_link_bestaetigt_die_adresse(self):
        from django.core import signing
        from ..views.legal import _NEWSLETTER_SALT
        Subscriber.objects.create(email='neu@example.invalid')
        token = signing.dumps({'e': 'neu@example.invalid'}, salt=_NEWSLETTER_SALT)
        self.hole(f'/newsletter/bestaetigen/?t={token}')
        self.assertTrue(Subscriber.objects.get().bestaetigt)

    def test_ein_gefaelschter_link_bestaetigt_nichts(self):
        Subscriber.objects.create(email='neu@example.invalid')
        self.hole('/newsletter/bestaetigen/?t=gefaelscht')
        self.assertFalse(Subscriber.objects.get().bestaetigt)


class DrosselungTest(LuviqTestCase):
    """Obergrenze je IP-Adresse für beide Anfragewege (FO09)."""

    def _kontakt(self, **meta):
        # Je Aufruf ein anderer Text: wortgleiche Anfragen führt FO03 zusammen.
        self._nummer = getattr(self, '_nummer', 0) + 1
        daten = dict(GUELTIGE_ANFRAGE, nachricht=f"{GUELTIGE_ANFRAGE['nachricht']} ({self._nummer})")
        return self.sende('/kontakt/', daten, **meta)

    def test_ueber_der_grenze_wird_keine_nachricht_mehr_verschickt(self):
        """Verhindert, dass eine Schleife das Postfach der Betreiberin füllt:
        nach fünf Anfragen einer Adresse antwortet das Formular mit 429."""
        with mock.patch(_MAIL) as versand:
            for _ in range(ANFRAGE_GRENZE):
                self.assertEqual(self._kontakt().status_code, 302)
            antwort = self._kontakt()
        self.assertContains(antwort, 'mehrere Nachrichten', status_code=429)
        self.assertEqual(versand.call_count, ANFRAGE_GRENZE)

    def test_eine_andere_adresse_ist_nicht_betroffen(self):
        """Gegenprobe: die Grenze gilt je Absender, nicht für alle Besucher."""
        with mock.patch(_MAIL) as versand:
            for _ in range(ANFRAGE_GRENZE + 1):
                self._kontakt(REMOTE_ADDR='198.51.100.1')
            antwort = self._kontakt(REMOTE_ADDR='198.51.100.2')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(versand.call_count, ANFRAGE_GRENZE + 1)

    def test_ein_selbst_gesetzter_weiterleitungskopf_umgeht_die_grenze_nicht(self):
        """Verhindert den einfachsten Umweg: der Absender setzt den ersten
        Eintrag von ``X-Forwarded-For`` bei jeder Anfrage neu. Gezählt wird
        der Eintrag, den der Proxy anhängt."""
        with mock.patch(_MAIL):
            for nummer in range(ANFRAGE_GRENZE):
                self._kontakt(HTTP_X_FORWARDED_FOR=f'10.0.0.{nummer}, 203.0.113.7')
            antwort = self._kontakt(HTTP_X_FORWARDED_FOR='10.0.0.99, 203.0.113.7')
        self.assertEqual(antwort.status_code, 429)

    def test_der_newsletter_nimmt_ueber_der_grenze_keine_adresse_mehr_an(self):
        """Verhindert, dass ein Skript die Abonnentenliste mit fremden
        Adressen füllt."""
        for nummer in range(ANFRAGE_GRENZE):
            antwort = self.sende('/newsletter/subscribe/', {'email': f'n{nummer}@example.invalid'})
            self.assertEqual(antwort.status_code, 200)
        antwort = self.sende('/newsletter/subscribe/', {'email': 'zuviel@example.invalid'})
        self.assertEqual(antwort.status_code, 429)
        self.assertIn('error', antwort.json())
        self.assertEqual(Subscriber.objects.count(), ANFRAGE_GRENZE)


class KontaktSpamschutzTest(LuviqTestCase):
    """Bot-Spam wird still verworfen (Anlass: Lamborghini-„Gewinnspiel“, 16.09.2026)."""

    LAMBORGHINI = {
        'name': 'RobertBoobe',
        'email': 'cosmas133@live.com',
        'betreff': 'THE LAMBORGHINI AVENTADOR SWEEPSTAKES CLOSES SOON',
        'nachricht': 'You are a snap away from an Lamborghini Aventador '
                     'https://telegra.ph/Win-a-new-Lamborghini-Aventador-today-Message-ID-24459-09-14',
    }

    def test_die_lamborghini_mail_wird_nicht_verschickt(self):
        with mock.patch(_MAIL) as versand, self.assertLogs('shop1', level='WARNING'):
            antwort = self.sende('/kontakt/', self.LAMBORGHINI)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        versand.assert_not_called()

    def test_die_falle_verwirft_auch_eine_harmlose_nachricht(self):
        with mock.patch(_MAIL) as versand:
            self.sende('/kontakt/', dict(GUELTIGE_ANFRAGE, webseite='https://x.example'))
        versand.assert_not_called()

    def test_ein_mensch_mit_einem_link_kommt_durch(self):
        """Eine Kundin darf auf ein Bild verweisen — ein Link allein blockt nicht."""
        from .. import spamschutz
        daten = dict(GUELTIGE_ANFRAGE,
                     nachricht='So eine Jacke wie hier: https://instagram.com/p/abc',
                     formzeit=spamschutz.zeitstempel())
        import time
        punkte, gruende = spamschutz.bewerte(daten, jetzt=time.time() + 60)
        self.assertLess(punkte, spamschutz.SCHWELLE, gruende)

    def test_das_formular_traegt_zeitstempel_und_falle(self):
        inhalt = self.hole('/kontakt/').content.decode()
        self.assertIn('name="formzeit"', inhalt)
        self.assertIn('name="webseite"', inhalt)
        self.assertIn('tabindex="-1"', inhalt)

    def test_das_fallenfeld_ist_an_sich_selbst_versteckt(self):
        """Verhindert, dass die Falle einen Menschen trifft (KV06): sie darf
        auch dann weder sichtbar noch erreichbar noch automatisch ausfuellbar
        sein, wenn der umgebende Kasten einmal wegfaellt oder ein spaeterer
        Stil ihn sichtbar macht. Das Feld traegt seine Kennzeichen deshalb
        selbst."""
        import re
        from .. import spamschutz
        inhalt = self.hole('/kontakt/').content.decode()
        feld = re.search(rf'<input[^>]*name="{spamschutz.FELD_FALLE}"[^>]*>', inhalt).group(0)
        self.assertIn('aria-hidden="true"', feld)
        self.assertIn('tabindex="-1"', feld)
        self.assertIn('autocomplete="off"', feld)
        self.assertRegex(feld, r'style="[^"]*left:-10000px')
        # Sichtbar ist nur, was ein Bot fuer ein echtes Feld halten soll:
        # ein unverfaenglicher Name, kein „honeypot“ oder „hp“ im Markup.
        self.assertNotIn('honey', inhalt.lower())
