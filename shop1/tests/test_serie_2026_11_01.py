"""Engel-Shirt als Serienstück (Bastian 01.11.2026): mehrfach bestellbar, nie reserviert, nie ausverkauft.

Prüfbefehl: python manage.py test shop1.tests.test_serie_2026_11_01
"""

import json
import re
import time
from decimal import Decimal
from unittest import mock

from django.core import signing
from django.core.cache import cache
from django.test import Client, override_settings

from shop1 import luviq_daten, spamschutz
from shop1.models import Order, Produkt
from shop1.views.checkout import reserviert
from ._basis import LuviqTestCase, erzeuge_produkt

_MAIL = 'shop1.views.direktkauf.send_brevo_email'


def _formzeit_alt():
    return signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ)


def _json_ld(html):
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


class SerieTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.serie = erzeuge_produkt(
            name='Engel-Shirt', preis=Decimal('69.00'), masse='Größe M (Second-Hand-Shirt), Maße auf Anfrage',
            material='100 % Baumwolle', lagerbestand=1, aktiv=True, vergeben=False,
            zustand='Gebraucht (Second Hand), von Hand mit Bleiche gemalt', serie=True, bearbeitungstage=3,
            bild_statisch='shop1/images/luviq/hero-engel-45-{w}.webp@480,640,800#800x999')
        self.einzel = erzeuge_produkt(
            name='Einzelstück', preis=Decimal('50.00'), masse='Größe L', material='Baumwolle',
            lagerbestand=1, aktiv=True, vergeben=False, zustand='Gebraucht')
        self.mail = self.enterContext(mock.patch(_MAIL))

    def daten(self, **ab):
        d = {'name': 'Kim Muster', 'email': 'kundin@example.org', 'strasse': 'Testweg 1', 'plz': '23552',
             'stadt': 'Lübeck', 'lieferart': 'versand', 'zustimmung': 'ja', 'formzeit': _formzeit_alt()}
        d.update(ab)
        return d

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_serienstueck_bleibt_nach_der_bestellung_bestellbar(self):
        pfad = f'/bestellen/{self.serie.slug}/'
        self.assertRedirects(self.sende(pfad, self.daten()), '/bestellen/danke/', fetch_redirect_response=False)
        self.assertEqual(reserviert(self.serie), 0)
        self.assertTrue(Produkt.objects.get(pk=self.serie.pk).kaufbar)
        seite = self.hole(f'/produkt/{self.serie.slug}/')
        self.assertContains(seite, 'Zahlungspflichtig bestellen')
        self.assertNotContains(seite, 'Reserviert')
        # zweite Bestellung einer anderen Person, neue Sitzung
        self.client = Client()
        cache.clear()
        antwort = self.sende(pfad, self.daten(email='zweite@example.org', name='Lea Beispiel'))
        self.assertRedirects(antwort, '/bestellen/danke/', fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 2)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_einzelstueck_wird_weiter_reserviert(self):
        pfad = f'/bestellen/{self.einzel.slug}/'
        self.assertRedirects(self.sende(pfad, self.daten()), '/bestellen/danke/', fetch_redirect_response=False)
        self.assertEqual(reserviert(self.einzel), 1)
        self.assertContains(self.hole(f'/produkt/{self.einzel.slug}/'), 'Reserviert')

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_bezahlte_serienbestellung_verbraucht_den_bestand_nicht_einzelstueck_schon(self):
        from shop1.views.checkout import bestellung_abschliessen
        for produkt, serie in ((self.serie, True), (self.einzel, False)):
            self.client = Client()
            cache.clear()
            self.sende(f'/bestellen/{produkt.slug}/', self.daten(email=f'{produkt.pk}@example.org'))
            order = Order.objects.filter(items__produkt_ref=produkt.pk).get()
            self.assertTrue(bestellung_abschliessen(order))
            p = Produkt.objects.get(pk=produkt.pk)
            with self.subTest(serie=serie):
                self.assertEqual(p.kaufbar, serie)
                self.assertEqual(p.vergeben, not serie)
                self.assertEqual(p.lagerbestand, 1 if serie else 0)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_produktseite_nennt_groesse_bearbeitung_und_keine_einmal_behauptung(self):
        seite = self.hole(f'/produkt/{self.serie.slug}/')
        for text in ('Größe M (Second-Hand-Shirt)', 'Bearbeitung ca. 3 Werktage', 'Jetzt bestellen', '69,00'):
            self.assertContains(seite, text)
        html = seite.content.decode()
        for verboten in ('gibt es nur einmal', 'genau einmal', 'nur einmal vorhanden', 'Rückgabe gibt es nicht',
                         'keine Rückgabe'):
            self.assertNotIn(verboten, html)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_schema_ist_haendlertauglich(self):
        html = self.hole(f'/produkt/{self.serie.slug}/').content.decode()
        produkt = next(b for b in _json_ld(html) if b.get('@type') == 'Product')
        self.assertEqual(produkt['brand']['name'], 'Luviq')
        self.assertEqual(produkt['size'], 'M')
        self.assertTrue(produkt['image'])
        offer = produkt['offers']
        self.assertEqual(offer['price'], '69.00')
        self.assertEqual(offer['availability'], 'https://schema.org/InStock')
        self.assertEqual(offer['itemCondition'], 'https://schema.org/UsedCondition')
        zeit = offer['shippingDetails']['deliveryTime']
        self.assertEqual(zeit['handlingTime']['minValue'], 3)
        self.assertEqual(zeit['handlingTime']['maxValue'], 3)
        self.assertEqual(zeit['transitTime']['maxValue'], luviq_daten.VERSAND['lieferfrist_werktage'] - 3)
        rueck = offer['hasMerchantReturnPolicy']
        self.assertEqual(rueck['merchantReturnDays'], 14)
        self.assertEqual(rueck['applicableCountry'], 'DE')

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_mail_nennt_bearbeitungszeit_und_keine_reservierung(self):
        pfad = f'/bestellen/{self.serie.slug}/'
        self.sende(pfad, self.daten())
        kundenmail = next(a for a in self.mail.call_args_list if a.args[2] == 'kundin@example.org')
        text = kundenmail.kwargs.get('text_content', '').split('---')[0]  # nur der persönliche Teil, ohne Vertragsunterlagen
        self.assertIn('Bearbeitungszeit beträgt ca. 3 Werktage', text)
        self.assertNotIn('reserviert', text)
        self.assertNotIn('nur einmal', text)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_startseite_hat_kaufkarte_cta_und_startfilm_ohne_autoplay(self):
        html = self.hole('/').content.decode()
        self.assertIn('lv-kaufkarte', html)
        self.assertIn(f'/produkt/{self.serie.slug}/#bestellen', html)
        self.assertIn('Jetzt bestellen', html)
        video = re.search(r'<video[^>]*>', html).group(0)
        self.assertIn('preload="none"', video)
        self.assertNotIn('autoplay', video)
        self.assertIn('"VideoObject"', html)
        self.assertIn('Frühere Stücke', html)
        self.assertNotIn('Jedes Stück gibt es nur einmal', html)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_agb_nennt_bearbeitungszeit_der_serienstuecke(self):
        html = self.hole('/agb/').content.decode()
        i = html.find('Zahlungseingang')
        self.assertIn('Bearbeitungszeit ca. 3 Werktage; sie ist in dieser Frist enthalten', ' '.join(html.split()), html[i-200:i+300])

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_widerruf_bleibt_unveraendert_und_keine_rueckgabe_ausgeschlossen(self):
        html = self.hole('/agb/').content.decode()
        self.assertIn('14 Tage', html)
        self.assertNotIn('Rückgabe gibt es nicht', html)
