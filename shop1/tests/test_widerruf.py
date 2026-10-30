"""Widerrufsfunktion (§ 356a BGB), Rechtstexte und Bestellweg zum Verkaufsstart (30.10.2026).

Belege und Quellen: ``Analysen\\luviq-2026-10-30-recht\\BERICHT.md``.
"""

import os
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.test import Client, override_settings
from django.utils import timezone

from .. import startsperre
from ..models import Cart, CartItem, Order, OrderItem, Widerruf
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

_MAIL_W = 'shop1.views.widerruf.send_brevo_email'
_MAIL_K = 'shop1.views.checkout.send_brevo_email'
_BANK = {'BANK_IBAN': 'DE00 0000 0000 0000 0000 00', 'BANK_INHABER': 'Luisa Brehler'}


def _formzeit_alt():
    """Ein Zeitstempel, der älter als die Mindestzeit des Spamschutzes ist."""
    from django.core import signing
    from .. import spamschutz
    import time
    return signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ)


def _bestellung(email='kundin@example.org', **felder):
    werte = dict(vorname='Kim', nachname='Muster', email=email, adresse='Weg 1', stadt='Lübeck',
                 postleitzahl='23552', land='Deutschland', gesamt_betrag=Decimal('60.00'))
    werte.update(felder)
    return Order.objects.create(**werte)


class WiderrufsfunktionTest(LuviqTestCase):

    def daten(self, **ueber):
        d = {'name': 'Kim Muster', 'vertrag': '#1', 'umfang': '', 'email': 'kundin@example.org',
             'formzeit': _formzeit_alt()}
        d.update(ueber)
        return d

    def test_ohne_anmeldung_und_ohne_verkauf_erreichbar(self):
        antwort = self.hole('/vertrag-widerrufen/')
        self.assertEqual(antwort.status_code, 200)
        html = antwort.content.decode()
        self.assertIn('<h1 class="lv-serif lv-satz" id="widerruf-titel">Vertrag widerrufen</h1>', html)
        # § 356a Abs. 3 BGB: Bestätigungsfunktion mit dem gesetzlichen Wortlaut.
        self.assertIn('>Widerruf bestätigen</button>', html)
        self.assertIn('noindex', html)
        for feld in ('name="name"', 'name="vertrag"', 'name="email"', 'name="csrfmiddlewaretoken"'):
            self.assertIn(feld, html)

    def test_widerruf_wird_gespeichert_zugeordnet_und_bestaetigt(self):
        bestellung = _bestellung()
        with mock.patch(_MAIL_W) as mail:
            antwort = self.sende('/vertrag-widerrufen/', self.daten(vertrag=f'Bestellung #{bestellung.pk}'))
        self.assertRedirects(antwort, '/vertrag-widerrufen/eingang/', fetch_redirect_response=False)
        w = Widerruf.objects.get()
        self.assertEqual(w.bestellung, bestellung)
        self.assertFalse(w.spamverdacht)
        self.assertTrue(w.bestaetigung_gestartet)
        # Eingangsbestätigung an die Kundin + Mail an Luisa.
        empfaenger = [c.args[2] for c in mail.call_args_list]
        self.assertIn('kundin@example.org', empfaenger)
        self.assertEqual(len(empfaenger), 2)
        kunde = next(c for c in mail.call_args_list if c.args[2] == 'kundin@example.org')
        eingang = timezone.localtime(w.eingegangen_am).strftime('%d.%m.%Y, %H:%M Uhr')
        for inhalt in (kunde.args[1], kunde.kwargs['text_content']):
            self.assertIn(eingang, inhalt)         # § 356a Abs. 4: Datum und Uhrzeit
            self.assertIn('Kim Muster', inhalt)    # Inhalt der Erklärung
            self.assertIn(f'Bestellung #{bestellung.pk}', inhalt)
        self.assertIn('Eingangsbestätigung', kunde.args[0])
        # Bestätigungsseite zeigt den eigenen Widerruf.
        seite = self.hole('/vertrag-widerrufen/eingang/')
        self.assertContains(seite, eingang)
        self.assertContains(seite, 'Dein Widerruf ist eingegangen.')
        # Kopie an die Betreuung.
        self.assertTrue(self.kopie_versand.called)

    def test_ohne_passende_bestellung_trotzdem_gespeichert_und_bestaetigt(self):
        _bestellung(email='andere@example.org')
        with mock.patch(_MAIL_W) as mail:
            self.sende('/vertrag-widerrufen/', self.daten(vertrag='#1'))
        w = Widerruf.objects.get()
        self.assertIsNone(w.bestellung)      # E-Mail passt nicht → keine fremde Zuordnung
        self.assertTrue(mail.called)

    def test_pflichtangaben_fehlen(self):
        for feld in ('name', 'vertrag', 'email'):
            with self.subTest(feld=feld), mock.patch(_MAIL_W) as mail:
                antwort = self.sende('/vertrag-widerrufen/', self.daten(**{feld: ''}))
                self.assertEqual(antwort.status_code, 200)
                mail.assert_not_called()
        self.assertFalse(Widerruf.objects.exists())

    def test_spamverdacht_speichert_aber_mailt_nicht(self):
        with mock.patch(_MAIL_W) as mail:
            self.sende('/vertrag-widerrufen/', self.daten(website='https://spam.example'))
        w = Widerruf.objects.get()
        self.assertTrue(w.spamverdacht)
        mail.assert_not_called()
        self.assertFalse(self.kopie_versand.called)

    def test_csrf_ist_pflicht(self):
        client = Client(enforce_csrf_checks=True)
        antwort = client.post('/vertrag-widerrufen/', self.daten(), secure=True)
        self.assertEqual(antwort.status_code, 403)
        self.assertFalse(Widerruf.objects.exists())

    def test_drosselung_je_ip(self):
        with mock.patch(_MAIL_W):
            for i in range(5):
                self.sende('/vertrag-widerrufen/', self.daten(vertrag=f'#{i + 10}'))
            antwort = self.sende('/vertrag-widerrufen/', self.daten(vertrag='#99'))
        self.assertEqual(antwort.status_code, 429)

    def test_eingangsseite_ohne_eigenen_widerruf_leitet_um(self):
        self.assertRedirects(self.hole('/vertrag-widerrufen/eingang/'), '/vertrag-widerrufen/',
                             fetch_redirect_response=False)

    def test_eingabe_wird_in_der_mail_nicht_als_html_ausgegeben(self):
        with mock.patch(_MAIL_W) as mail:
            self.sende('/vertrag-widerrufen/', self.daten(name='<b>Kim</b>', umfang='<script>x</script>'))
        kunde = next(c for c in mail.call_args_list if c.args[2] == 'kundin@example.org')
        self.assertNotIn('<script>x', kunde.args[1])
        self.assertNotIn('<b>Kim</b>', kunde.args[1])

    def test_startsperre_kennt_die_funktion(self):
        self.assertTrue(startsperre.WIDERRUFSFUNKTION_VORHANDEN)
        self.assertFalse(any('356a' in g for g in startsperre.sperrgruende(
            heute=timezone.localdate(), umgebung={'LUCID_REGISTRIERNUMMER': 'x'})))


class WiderrufsKnopfTest(LuviqTestCase):
    """§ 356a Abs. 1 BGB: „Vertrag widerrufen“ während jeder Widerrufsfrist ständig verfügbar."""

    KNOPF = '<a class="lv-fuss-widerruf" href="/vertrag-widerrufen/">Vertrag widerrufen</a>'

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_auf_jeder_seite(self):
        for pfad in ('/', '/produkte/', '/kontakt/', '/impressum/', '/agb/', '/datenschutz/'):
            with self.subTest(pfad=pfad):
                self.assertContains(self.hole(pfad), self.KNOPF)

    @override_settings(VERKAUF_AKTIV=False)
    def test_ohne_verkauf_und_ohne_bestellungen_nicht_im_fuss(self):
        self.assertNotContains(self.hole('/'), self.KNOPF)

    @override_settings(VERKAUF_AKTIV=False)
    def test_ohne_verkauf_bleibt_er_nach_einer_bestellung(self):
        _bestellung()
        self.assertContains(self.hole('/'), self.KNOPF)
        alt = _bestellung()
        Order.objects.update(erstellt_am=timezone.now() - timedelta(days=120))
        from django.core.cache import cache
        cache.delete('widerruf_knopf')
        self.assertNotContains(self.hole('/'), self.KNOPF)
        self.assertTrue(alt.pk)


class RechtstexteTest(LuviqTestCase):

    @override_settings(VERKAUF_AKTIV=True)
    def test_agb_seite_zeigt_agb_belehrung_und_formular(self):
        html = self.hole('/agb/').content.decode()
        for satz in (
            '§ 2 Vertragsschluss',
            'Zahlungspflichtig bestellen',
            'Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen.',
            'die Waren in Besitz genommen haben bzw. hat.',
            'Sie können Ihr Widerrufsrecht auch online unter',
            '/vertrag-widerrufen/',
            'Sie tragen die unmittelbaren Kosten der Rücksendung der Waren.',
            'Wir können die Rückzahlung verweigern, bis wir die Waren wieder zurückerhalten haben',
            'Muster-Widerrufsformular',
            '(*) Unzutreffendes streichen.',
            '§ 312g Abs. 2 Nr. 1 BGB',
            'Gemäß § 19 UStG wird keine Umsatzsteuer berechnet',
            'nicht bereit und nicht verpflichtet',
        ):
            with self.subTest(satz=satz):
                self.assertIn(satz, html)
        self.assertNotIn('GENERATOR-TEXT-FEHLT', html)
        self.assertNotIn('ec.europa.eu/consumers/odr', html)   # OS-Plattform abgeschaltet
        self.assertNotIn('Telefon', html.split('Widerrufsbelehrung', 1)[1].split('Muster-Widerrufsformular')[0])

    @override_settings(VERKAUF_AKTIV=True)
    def test_ueberweisung_nur_wenn_angeboten(self):
        with mock.patch.dict(os.environ, {'BANK_IBAN': ''}):
            self.assertNotIn('Vorkasse per Überweisung', self.hole('/agb/').content.decode())
        with mock.patch.dict(os.environ, _BANK):
            self.assertIn('Vorkasse per Überweisung', self.hole('/agb/').content.decode())

    def test_datenschutz_nennt_widerruf_hosting_und_mailweg(self):
        html = self.hole('/datenschutz/').content.decode()
        for satz in ('Railway', 'Cloudinary', 'Gmail', 'Vertrag widerrufen', 'django-axes', 'Double-Opt-in',
                     'Landeszentrum für Datenschutz Schleswig-Holstein'):
            self.assertIn(satz, html)
        self.assertNotIn('GENERATOR-TEXT-FEHLT', html)

    @override_settings(VERKAUF_AKTIV=True)
    def test_datenschutz_mit_verkauf_nennt_zahlung_versand_aufbewahrung(self):
        html = self.hole('/datenschutz/').content.decode()
        for satz in ('PayPal (Europe) S.à r.l. et Cie, S.C.A.', 'Versanddienstleister', '§ 147 Abgabenordnung'):
            self.assertIn(satz, html)


class BestellwegTest(LuviqTestCase):

    def setUp(self):
        self.kundin = erzeuge_benutzer('wkundin', email='wk@example.org')
        self.kundin.profile.email_verified = True
        self.kundin.profile.has_welcome_discount = False
        self.kundin.profile.save()
        self.client.force_login(self.kundin)
        self.produkt = erzeuge_produkt('Neues Shirt', preis=Decimal('60.00'), zustand='Neu, von Hand bemalt, 1-of-1')

    def legen(self, produkt=None):
        produkt = produkt or self.produkt
        korb, _ = Cart.objects.get_or_create(user=self.kundin)
        CartItem.objects.create(cart=korb, produkt_name=produkt.name, produkt_ref=produkt.id,
                                produkt_preis=produkt.preis, menge=1)

    def adresse(self, **ueber):
        d = {'vorname': 'Kim', 'nachname': 'Muster', 'email': 'wk@example.org', 'adresse': 'Weg 1',
             'stadt': 'Lübeck', 'postleitzahl': '23552', 'land': 'Deutschland', 'payment_method': 'paypal'}
        d.update(ueber)
        return d

    @override_settings(VERKAUF_AKTIV=True)
    def test_kasse_zeigt_pflichtangaben_vor_dem_knopf(self):
        self.legen()
        html = self.hole('/checkout/').content.decode()
        vor_knopf = html.split('Zahlungspflichtig bestellen')[0]
        for satz in ('Neues Shirt · Neu, von Hand bemalt, 1-of-1', 'Lieferung nur innerhalb Deutschlands',
                     'Akzeptierte Zahlungsarten: PayPal', 'eu-gewaehrleistung-hinweis-de', 'Gesetzliche Gewährleistung'):
            self.assertIn(satz, vor_knopf)
        self.assertIn('#widerruf', html)
        self.assertIn('readonly', html.split('id="kasse-land"')[1][:200])

    @override_settings(VERKAUF_AKTIV=True)
    def test_ausland_wird_abgelehnt(self):
        self.legen()
        with mock.patch(_MAIL_K):
            self.sende('/checkout/', self.adresse(land='Österreich'))
        self.assertFalse(Order.objects.exists())

    @override_settings(VERKAUF_AKTIV=True)
    def test_paypal_bestellung_bekommt_eingangsbestaetigung(self):
        self.legen()
        with mock.patch(_MAIL_K) as mail:
            self.sende('/checkout/', self.adresse())
        order = Order.objects.get()
        self.assertEqual(order.land, 'Deutschland')
        mail.assert_called_once()
        self.assertEqual(mail.call_args.args[0], f'Eingang deiner Bestellung #{order.pk}')
        self.assertIn('noch keine Annahme', mail.call_args.kwargs['text_content'])

    @override_settings(VERKAUF_AKTIV=True)
    def test_bestellbestaetigung_traegt_vertragsunterlagen(self):
        from ..views.checkout import send_order_confirmation_email
        order = _bestellung(email='wk@example.org', user=self.kundin)
        OrderItem.objects.create(order=order, produkt_name=self.produkt.name, produkt_preis=Decimal('60.00'),
                                 produkt_ref=self.produkt.pk, menge=1)
        with mock.patch(_MAIL_K) as mail:
            send_order_confirmation_email(order)
        html, text = mail.call_args.args[1], mail.call_args.kwargs['text_content']
        for inhalt in (html, text):
            for satz in ('Allgemeine Geschäftsbedingungen', '§ 2 Vertragsschluss', 'Widerrufsbelehrung',
                         'Muster-Widerrufsformular', 'Vertrag widerrufen', 'Neu, von Hand bemalt, 1-of-1',
                         'Gemäß § 19 UStG'):
                self.assertIn(satz, inhalt)
        self.assertIn('/vertrag-widerrufen/', html)

    @override_settings(VERKAUF_AKTIV=True)
    def test_ueberweisung_ist_annahme_mit_unterlagen_und_reserviert(self):
        self.legen()
        with mock.patch(_MAIL_K) as mail, mock.patch.dict(os.environ, _BANK):
            self.sende('/checkout/', self.adresse(payment_method='bank_transfer'))
        order = Order.objects.get()
        self.assertTrue(mail.call_args.args[0].startswith('Bestellbestätigung und Zahlungsinformationen'))
        for inhalt in (mail.call_args.args[1], mail.call_args.kwargs['text_content']):
            self.assertIn('Kaufvertrag ist geschlossen', inhalt)
            self.assertIn('Muster-Widerrufsformular', inhalt)
        # Das Einzelstück ist reserviert: eine zweite Kundin kann es nicht kaufen.
        from ..views.checkout import _verfuegbarkeit, reserviert
        self.assertEqual(reserviert(self.produkt), 1)
        posten = list(order.items.all())
        self.assertTrue(_verfuegbarkeit(posten))
        self.assertEqual(_verfuegbarkeit(posten, ausser=order), [])
        Order.objects.filter(pk=order.pk).update(status='cancelled')
        self.assertEqual(reserviert(self.produkt), 0)

    @override_settings(VERKAUF_AKTIV=True)
    def test_warenkorb_nennt_lieferland_und_zahlungsarten(self):
        self.legen()
        self.assertContains(self.hole('/warenkorb/'), 'Lieferung nur innerhalb Deutschlands. Akzeptierte Zahlungsarten: PayPal')
