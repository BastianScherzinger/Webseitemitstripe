"""Direktkauf ohne Konto: Bestellung, Reservierung und Schutzmechanismen.

Prüfbefehl (hier nicht ausgeführt):
python manage.py test shop1.tests.test_direktkauf_2026_10_31
"""

import os
import time
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest import mock

from django.core import signing
from django.core.cache import cache
from django.test import Client, override_settings

from shop1 import spamschutz, startsperre
from shop1.models import Order, OrderItem
from shop1.views.direktkauf import mail_an_kundin
from ._basis import LuviqTestCase, erzeuge_produkt


_MAIL = 'shop1.views.direktkauf.send_brevo_email'


def _formzeit_alt():
    """Gültig signierte Formularzeit außerhalb der Mindestwartezeit."""
    return signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ)


class DirektkaufTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.produkt = erzeuge_produkt(
            name='Engel-Shirt', preis=Decimal('69.00'), masse='Größe M',
            material='Baumwolle', lagerbestand=1, aktiv=True,
            vergeben=False, zustand='Neu, von Hand bemalt',
        )
        self.assertTrue(self.produkt.kaufbar)
        self.assertFalse(self.produkt.pflichtangaben_fehlen)
        self.stueckpfad = f'/produkt/{self.produkt.slug}/'
        self.bestellpfad = f'/bestellen/{self.produkt.slug}/'
        # Auch bei einem unerwarteten Durchrutschen darf keine echte Mail gehen.
        self.mail = self.enterContext(mock.patch(_MAIL))

    def daten(self, **abweichungen):
        daten = {
            'name': 'Kim Muster', 'email': 'kundin@example.org',
            'strasse': 'Testweg 1', 'plz': '23552', 'stadt': 'Lübeck',
            'lieferart': 'versand', 'zustimmung': 'ja',
            'formzeit': _formzeit_alt(),
        }
        daten.update(abweichungen)
        return daten

    # Methodendekoratoren greifen nach dem DIREKTKAUF=False der Basisklasse.
    @override_settings(VERKAUF_AKTIV=False, DIREKTKAUF=True)
    def test_verkauf_aus_leitet_um_und_verhindert_bestellungen(self):
        for methode in (self.hole, self.sende):
            with self.subTest(methode=methode.__name__):
                antwort = (methode(self.bestellpfad, self.daten())
                           if methode == self.sende else methode(self.bestellpfad))
                self.assertRedirects(antwort, '/#newsletter-form', status_code=302,
                                     fetch_redirect_response=False)
        self.assertNotContains(self.hole(self.stueckpfad), 'Zahlungspflichtig bestellen')
        self.assertEqual(Order.objects.count(), 0)
        self.mail.assert_not_called()

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_stueckseite_zeigt_direktkauf_statt_login_und_warenkorb(self):
        antwort = self.hole(self.stueckpfad)
        for text in ('id="bestellen"', 'Zahlungspflichtig bestellen', 'Gesamtpreis'):
            self.assertContains(antwort, text)
        for text in ('Anmelden und kaufen', 'In den Warenkorb'):
            self.assertNotContains(antwort, text)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_gueltige_bestellung_speichert_posten_mailt_und_zeigt_danke(self):
        antwort = self.sende(self.bestellpfad, self.daten())
        self.assertRedirects(antwort, '/bestellen/danke/', status_code=302,
                             fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 1)
        bestellung = Order.objects.get()
        self.assertIsNone(bestellung.user)
        self.assertEqual(bestellung.status, 'pending')
        self.assertEqual(bestellung.payment_method, 'bank_transfer')
        self.assertEqual(bestellung.gesamt_betrag, Decimal('69.00'))
        self.assertEqual(OrderItem.objects.count(), 1)
        posten = bestellung.items.get()
        self.assertEqual(posten.produkt_ref, self.produkt.pk)
        self.assertEqual(posten.produkt_preis, Decimal('69.00'))
        self.assertEqual(posten.menge, 1)
        self.assertEqual(self.mail.call_count, 2)
        self.assertCountEqual(
            [aufruf.args[2] for aufruf in self.mail.call_args_list],
            ['kundin@example.org', 'brehlerluisa@gmail.com'],
        )
        self.assertContains(self.hole('/bestellen/danke/'), 'Rechnung mit den Zahlungsdaten')

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_reservierung_verhindert_doppelkauf_stornierung_gibt_stueck_frei(self):
        self.assertRedirects(self.sende(self.bestellpfad, self.daten()),
                             '/bestellen/danke/', fetch_redirect_response=False)
        bestellung = Order.objects.get()
        self.assertContains(self.hole(self.stueckpfad), 'Reserviert')
        # Neue Sitzung und leerer Cache: die Datenbank muss die Reservierung tragen.
        self.client = Client()
        cache.clear()
        self.mail.reset_mock()
        antwort = self.sende(self.bestellpfad, self.daten(email='zweite@example.org'))
        self.assertEqual(antwort.status_code, 409)
        self.assertEqual(Order.objects.count(), 1)
        self.mail.assert_not_called()
        bestellung.status = 'cancelled'
        bestellung.save(update_fields=['status'])
        self.assertContains(self.hole(self.stueckpfad), 'Zahlungspflichtig bestellen')
        antwort = self.sende(self.bestellpfad, self.daten(email='zweite@example.org'))
        self.assertRedirects(antwort, '/bestellen/danke/', fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Order.objects.filter(status='pending').count(), 1)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_honigtopf_leitet_still_um_ohne_bestellung_und_mails(self):
        antwort = self.sende(self.bestellpfad, self.daten(website='x'))
        self.assertRedirects(antwort, '/bestellen/danke/', fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 0)
        self.mail.assert_not_called()
        self.kopie_versand.assert_not_called()

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_fehlende_oder_ungueltige_pflichtfelder_werden_abgelehnt(self):
        for feld, wert in (('zustimmung', None), ('email', 'ungueltig'),
                           ('name', 'Kim'), ('strasse', '')):
            with self.subTest(feld=feld):
                daten = self.daten(**{feld: wert})
                if wert is None:
                    daten.pop(feld)
                self.assertEqual(self.sende(self.bestellpfad, daten).status_code, 400)
                self.assertEqual(Order.objects.count(), 0)
        self.mail.assert_not_called()

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_abholung_braucht_keine_anschrift(self):
        daten = self.daten(lieferart='abholung')
        for feld in ('strasse', 'plz', 'stadt'):
            daten.pop(feld)
        self.assertRedirects(self.sende(self.bestellpfad, daten),
                             '/bestellen/danke/', fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().adresse, 'Abholung in Lübeck nach Absprache')

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_csrf_token_ist_pflicht(self):
        self.client = Client(enforce_csrf_checks=True)
        self.assertEqual(self.sende(self.bestellpfad, self.daten()).status_code, 403)
        self.assertEqual(Order.objects.count(), 0)
        self.mail.assert_not_called()

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_neunte_fehlhafte_anfrage_wird_gedrosselt(self):
        # Auch ungültige Eingaben zählen; derselbe Client behält dieselbe IP.
        for nummer in range(1, 10):
            with self.subTest(anfrage=nummer):
                antwort = self.sende(self.bestellpfad, self.daten(zustimmung=''))
                self.assertEqual(antwort.status_code, 400 if nummer <= 8 else 429)
        self.assertEqual(Order.objects.count(), 0)
        self.mail.assert_not_called()

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_login_kaufweg_leitet_auf_produkte_um(self):
        for pfad in ('/warenkorb/', '/checkout/'):
            with self.subTest(pfad=pfad):
                self.assertRedirects(self.hole(pfad), '/produkte/', status_code=302,
                                     fetch_redirect_response=False)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_kundinnenmail_nennt_rechnung_preis_widerruf_und_bestellnummer(self):
        self.assertRedirects(self.sende(self.bestellpfad, self.daten()),
                             '/bestellen/danke/', fetch_redirect_response=False)
        bestellung = Order.objects.get()
        self.mail.reset_mock()
        mail_an_kundin(bestellung)
        self.mail.assert_called_once()
        aufruf = self.mail.call_args
        self.assertIn(f'#{bestellung.pk}', aufruf.args[0])
        self.assertEqual(aufruf.args[2], 'kundin@example.org')
        for fassung in (aufruf.args[1], aufruf.kwargs['text_content']):
            for text in ('Rechnung', '69.00', 'Widerruf'):
                with self.subTest(text=text, fassung='HTML' if fassung == aufruf.args[1] else 'Text'):
                    self.assertIn(text, fassung)


class StartsperreDatumTest(LuviqTestCase):
    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_berliner_datum_entscheidet_ueber_verkaufsbeginn(self):
        # Ende Oktober gilt MEZ: 22:30 UTC ist noch derselbe Kalendertag.
        # Zusätzlich prüft 23:30 UTC am 30.10. den gewünschten Wechsel zum 31.10.
        faelle = (
            (datetime(2026, 10, 31, 23, 30, tzinfo=timezone.utc), date(2026, 11, 1), False),
            (datetime(2026, 10, 30, 22, 30, tzinfo=timezone.utc), date(2026, 10, 30), True),
            (datetime(2026, 10, 30, 23, 30, tzinfo=timezone.utc), date(2026, 10, 31), True),
        )
        # fruehester_tag liest os.environ, nicht das umgebung-Argument.
        with mock.patch.dict(os.environ, {'VERKAUF_FRUEHESTENS': '2026-11-01'}):
            for jetzt, erwarteter_tag, gesperrt in faelle:
                with self.subTest(jetzt=jetzt):
                    heute = startsperre.heute_berlin(jetzt)
                    self.assertEqual(heute, erwarteter_tag)
                    gruende = startsperre.sperrgruende(
                        heute=heute, umgebung={'LUCID_REGISTRIERNUMMER': 'x'},
                    )
                    self.assertEqual(any(g.startswith('Verkauf erst ab') for g in gruende), gesperrt)
