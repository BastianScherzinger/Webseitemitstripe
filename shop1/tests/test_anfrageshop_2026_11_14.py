"""Anfrage-Shop (14.11.2026, Bastian: „einfacher Shop mit Anfragen wie Rümpelwerk, Mollie später“).

Geprüft wird: Stückseite zeigt Preis und Anfrageformular statt Kaufweg, Navigation ohne Konto/Panel/Warenkorb,
Kaufrouten und Rabattlinks leiten um, die Anfrage wird gespeichert und geht nur an Luisa (nie an die eingetippte
Adresse), Spam wird still verworfen, ``ANFRAGESHOP=0`` bringt den Direktkauf unverändert zurück.

Prüfbefehl: python manage.py test shop1.tests.test_anfrageshop_2026_11_14
"""

import re
import time
from decimal import Decimal
from unittest import mock

from django.core import signing
from django.core.cache import cache
from django.test import override_settings

from shop1 import spamschutz
from shop1.models import Order, Stueckanfrage
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

_MAIL = 'shop1.views.stueckanfrage.send_brevo_email'


def _formzeit_alt():
    return signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ)


# Klassendekorator greift vor dem ANFRAGESHOP=False der Basisklasse? Nein: die Basis schaltet in _pre_setup um;
# deshalb setzt setUp die Werte erneut (siehe unten).
class AnfrageShopTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        einstellungen = self.settings(VERKAUF_AKTIV=False, DIREKTKAUF=True, ANFRAGESHOP=True,
                                      MOTIV_EMPFAENGER='luisa@example.invalid')
        einstellungen.enable()
        self.addCleanup(einstellungen.disable)
        self.produkt = erzeuge_produkt(
            name='Engel-Shirt', preis=Decimal('69.00'), masse='Größe M', material='Baumwolle',
            lagerbestand=1, aktiv=True, vergeben=False, zustand='Neu, von Hand bemalt')
        self.assertTrue(self.produkt.kaufbar)
        self.stueck = f'/produkt/{self.produkt.slug}/'
        self.anfrage = f'/anfragen/{self.produkt.slug}/'
        self.mail = self.enterContext(mock.patch(_MAIL))

    def daten(self, **abweichung):
        daten = {'name': 'Kim Muster', 'email': 'kundin@example.org', 'anzahl': '1', 'groesse': 'M',
                 'nachricht': 'Gibt es das auch in L?', 'zustimmung': 'ja', 'formzeit': _formzeit_alt()}
        daten.update(abweichung)
        return daten

    def test_stueckseite_zeigt_preis_und_anfrage_statt_kaufweg(self):
        html = self.hole(self.stueck).content.decode()
        # 26.11.2026: kein Preis auf der Seite (Bastians Regel seit 20.11.), Luisa nennt ihn auf Anfrage
        self.assertNotIn('69,00', html)
        self.assertIn('Den Preis nennt Luisa dir auf Anfrage, bevor etwas gemalt oder verschickt wird', html)
        self.assertIn('id="anfragen"', html)
        self.assertIn('Stück anfragen', html)
        for weg in ('Zahlungspflichtig bestellen', 'Jetzt bestellen', 'id="bestellen"', 'Rabattcode',
                    'In den Warenkorb', 'Anmelden und kaufen', 'Konto anlegen'):
            with self.subTest(weg=weg):
                self.assertNotIn(weg, html)

    def test_schema_ohne_offer(self):
        html = self.hole(self.stueck).content.decode()
        self.assertIn('"@type": "VisualArtwork"', html)
        self.assertNotIn('"@type": "Offer"', html)

    def test_navigation_ohne_konto_panel_warenkorb(self):
        admin = erzeuge_benutzer('admin', is_superuser=True, is_staff=True)
        self.client.force_login(admin)
        # HTML-Kommentare (Entwicklernotizen im Quelltext) zählen nicht als sichtbarer Text.
        html = re.sub(r'<!--.*?-->', '', self.hole('/').content.decode(), flags=re.S)
        for wort in ('class="lv-konto"', 'lv-menue-klein" href="/profil/', '/shop-admin/dashboard/', '/warenkorb/'):
            with self.subTest(wort=wort):
                self.assertNotIn(wort, html)
        self.assertNotIn('Jetzt bestellen', html)

    def test_kaufrouten_und_rabattlinks_leiten_um(self):
        for pfad in ('/warenkorb/', '/checkout/', f'/bestellen/{self.produkt.slug}/', '/bestellen/danke/',
                     '/rabatt/WILLKOMMEN/'):
            with self.subTest(pfad=pfad):
                self.assertRedirects(self.hole(pfad), '/produkte/', fetch_redirect_response=False)
        self.assertRedirects(self.hole('/register/'), '/', fetch_redirect_response=False)
        self.assertEqual(self.hole('/login/').status_code, 200)  # Luisas Panel bleibt erreichbar
        self.assertEqual(self.sende('/paypal/create/1/').status_code, 409)

    def test_gueltige_anfrage_wird_gespeichert_und_geht_nur_an_luisa(self):
        antwort = self.sende(self.anfrage, self.daten())
        self.assertRedirects(antwort, '/anfragen/danke/', fetch_redirect_response=False)
        a = Stueckanfrage.objects.get()
        self.assertEqual((a.produkt_name, a.anzahl, a.groesse, a.email), ('Engel-Shirt', 1, 'M', 'kundin@example.org'))
        self.assertTrue(a.mail_gestartet)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(self.mail.call_count, 1)
        args, kwargs = self.mail.call_args
        self.assertEqual(args[2], 'luisa@example.invalid')
        self.assertEqual(kwargs['reply_to'], 'kundin@example.org')
        self.assertEqual(self.kopie_versand.call_count, 1)
        self.produkt.refresh_from_db()
        self.assertEqual(self.produkt.lagerbestand, 1)  # nichts reserviert

    def test_pflichtangaben_werden_geprueft(self):
        for feld, wert in (('name', ''), ('email', ''), ('email', 'kein-mail'), ('anzahl', '0'), ('anzahl', '9'),
                           ('anzahl', 'x'), ('zustimmung', '')):
            with self.subTest(feld=feld, wert=wert):
                cache.clear()  # die Drosselung je IP soll die Feldprüfung nicht verdecken
                antwort = self.sende(self.anfrage, self.daten(**{feld: wert}))
                self.assertEqual(antwort.status_code, 200)
                self.assertContains(antwort, 'role="alert"')
        self.assertEqual(Stueckanfrage.objects.count(), 0)
        self.mail.assert_not_called()

    def test_spam_wird_still_verworfen(self):
        antwort = self.sende(self.anfrage, self.daten(**{spamschutz.FELD_FALLE: 'http://spam.example'}))
        self.assertRedirects(antwort, '/anfragen/danke/', fetch_redirect_response=False)
        self.assertEqual(Stueckanfrage.objects.count(), 0)
        self.mail.assert_not_called()

    def test_doppelt_abgeschickt_wird_zusammengefuehrt(self):
        self.sende(self.anfrage, self.daten())
        self.sende(self.anfrage, self.daten())
        self.assertEqual(Stueckanfrage.objects.count(), 1)

    def test_get_leitet_auf_die_stueckseite_und_danke_ist_noindex(self):
        self.assertRedirects(self.hole(self.anfrage), self.stueck, fetch_redirect_response=False)
        self.assertContains(self.hole('/anfragen/danke/'), 'noindex')

    def test_vergebenes_stueck_nimmt_keine_anfrage(self):
        self.produkt.vergeben = True
        self.produkt.save()
        antwort = self.sende(self.anfrage, self.daten())
        self.assertRedirects(antwort, self.stueck, fetch_redirect_response=False)
        self.assertEqual(Stueckanfrage.objects.count(), 0)

    def test_kaufweg_wissensbeitraege_sind_ausgeblendet(self):
        self.assertRedirects(self.hole('/wissen/bestellen-und-bezahlen/'), '/wissen/', fetch_redirect_response=False)

    def test_schalter_aus_bringt_direktkauf_zurueck(self):
        with override_settings(ANFRAGESHOP=False, VERKAUF_AKTIV=True):
            html = self.hole(self.stueck).content.decode()
            self.assertIn('Zahlungspflichtig bestellen', html)
            self.assertNotIn('id="anfragen"', html)
            self.assertEqual(self.hole(f'/bestellen/{self.produkt.slug}/').status_code, 200)

    def test_ohne_anfrageshop_und_ohne_verkauf_bleibt_die_warteliste(self):
        with override_settings(ANFRAGESHOP=False, VERKAUF_AKTIV=False):
            html = self.hole(self.stueck).content.decode()
            self.assertNotIn('id="anfragen"', html)
            self.assertIn('Warteliste', html)
            self.assertRedirects(self.sende(self.anfrage, self.daten()), self.stueck, fetch_redirect_response=False)

    def test_anfrageshop_hangt_nicht_am_verkauf(self):
        from shop1 import verkauf
        self.assertFalse(verkauf.verkauf_aktiv())
        self.assertTrue(verkauf.anfrageshop_aktiv())
        with override_settings(ANFRAGESHOP=False):
            self.assertFalse(verkauf.anfrageshop_aktiv())

    def test_kaufrouten_bleiben_ohne_verkauf_gesperrt(self):
        for pfad in (f'/bestellen/{self.produkt.slug}/', '/warenkorb/', '/checkout/', '/register/'):
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(antwort.status_code, 302, pfad)
                self.assertNotIn('/login', antwort['Location'])

    def test_seiten_ohne_verkauf_haben_keine_kaufsaetze_und_keine_kauf_fusszeilen(self):
        self._pruefe_seiten_ohne_kaufsaetze()

    def test_seiten_mit_verkauf_und_anfrageshop_haben_keine_kaufsaetze_und_keine_kauf_fusszeilen(self):
        """So läuft es live: VERKAUF_AKTIV wirkt, trotzdem steht nur die Anfrage auf der Seite."""
        with override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True, ANFRAGESHOP=True):
            self._pruefe_seiten_ohne_kaufsaetze()
            html = self.hole(self.stueck).content.decode()
            self.assertNotIn('Jetzt bestellen', html)
            self.assertNotIn('"Offer"', html)
            self.assertIn('id="anfragen"', html)

    def _pruefe_seiten_ohne_kaufsaetze(self):
        verboten = ('Zahlungspflichtig', 'Jetzt bestellen', 'In den Warenkorb', 'Rabattcode', 'Zur Kasse',
                    'Widerrufsbelehrung', 'Muster-Widerrufsformular', 'Vertrag widerrufen', 'PayPal',
                    'Vorab-Überweisung', 'Zahlungslink', 'zum Kauf', 'Bestellvorgang', 'Der Shop öffnet',
                    'noch nicht geöffnet', 'Auf die Warteliste', 'nicht zu kaufen', 'kaufen', 'AGB',
                    'noch nicht im Verkauf', 'ersten Drop', 'im Aufbau', 'Werktage')
        for pfad in ('/', '/produkte/', self.stueck, '/kontakt/', '/liefergebiet/', '/ueber_uns/', '/wissen/',
                     '/gaestebuch/'):
            antwort = self.hole(pfad)
            if antwort.status_code != 200:
                continue
            html = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', '', antwort.content.decode(),
                          flags=re.S)
            text = re.sub(r'<[^>]+>', ' ', html)
            for wort in verboten:
                with self.subTest(pfad=pfad, wort=wort):
                    self.assertNotIn(wort, text)

    def test_schema_ohne_offer_ohne_verkauf(self):
        html = self.hole(self.stueck).content.decode()
        self.assertNotIn('"Offer"', html)
        self.assertNotIn('"@type": "Product"', html)
        self.assertNotIn('"Offer"', self.hole('/produkte/').content.decode())
