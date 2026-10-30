"""P5b (30.10.2026): A/B-Sieger im Hero, Karte vor Verkaufsstart, Kaufweg ohne Fehler 500.

Der Kaufweg-Test fängt, was P5 übersah: eine Vorlage oder ein Stück mit kaputtem Bild
(``bild_statisch`` ohne Datei im Manifest) legte Startseite und Warenkorb mit 500 lahm.
"""
import os
from decimal import Decimal
from unittest import mock

from django.test import override_settings

from .. import luviq_daten
from ..models import Cart, CartItem, Order
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt
from .test_zahlung import LIEFERADRESSE


class HeroSiegerTest(LuviqTestCase):
    def setUp(self):
        self.engel = erzeuge_produkt(
            'Engel-Shirt, mit Bleiche gemalt', slug='engel-shirt-handgebleicht', nummer=6,
            masse='Größe M', material='100 % Baumwolle')

    def text(self):
        return self.hole('/').content.decode()

    def test_hero_text_knoepfe_und_ereignisse(self):
        html = self.text()
        self.assertIn('Mit Bleiche gemalt. Jedes Stück gibt es nur einmal.', html)
        self.assertIn('Nº 006 · Engel-Shirt', html)
        self.assertIn('Luisa Brehler aus Lübeck zieht die Farbe mit Bleiche aus dem Stoff', html)
        self.assertIn('data-ereignis="hero_engel"', html)
        self.assertIn('data-ereignis="hero_motiv"', html)
        self.assertIn('Engel-Shirt ansehen', html)
        self.assertIn('Eigenes Motiv anfragen', html)
        self.assertIn(f'href="{self.engel.get_absolute_url()}" data-ereignis="hero_engel"', html)
        self.assertIn('Studiobild (KI) aus dem echten Foto', html)

    def test_datum_nur_vor_dem_verkaufsstart(self):
        self.assertIn('Nº 006 · Engel-Shirt · ab ', self.text())
        with override_settings(VERKAUF_AKTIV=True):
            kopf = self.text().split('<h1')[0]
            self.assertNotIn('Engel-Shirt · ab', kopf)

    def test_ohne_engel_stueck_fuehrt_der_knopf_auf_die_uebersicht(self):
        self.engel.delete()
        self.assertIn('href="/produkte/" data-ereignis="hero_engel"', self.text())

    def test_markensatz_ist_die_ueberschrift_des_anfrageabschnitts(self):
        html = self.text()
        self.assertIn(f'id="anfragen-titel">{luviq_daten.MARKENSATZ}</h2>', html)
        self.assertNotIn(f'id="markensatz">{luviq_daten.MARKENSATZ}', html)

    def test_echt_text_ehrlich_zum_studiobild(self):
        self.assertIn('Handyfoto vom echten Stück. Das Bild oben ist daraus als Studiobild '
                      'erstellt (KI).', self.text())

    def test_karte_vor_verkauf_zeigt_groesse_material_und_datum_ohne_preis(self):
        for pfad in ('/', '/produkte/'):
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                self.assertRegex(html, r'Größe M · 100 % Baumwolle · Preis ab \d\d\.\d\d\.')
                self.assertNotIn('49,90', html)

    def test_alsfeld_satz(self):
        self.assertIn('angefangen in Alsfeld, heute in Lübeck', self.text())

    def test_lead_hat_hoechstens_45_woerter_und_nennt_luebeck(self):
        self.assertLessEqual(len(luviq_daten.LEAD.split()), 45)
        self.assertIn('Lübeck', luviq_daten.LEAD)

    def test_login_markiert_motiv_anfragen_nicht_als_aktiv(self):
        html = self.hole('/login/').content.decode()
        self.assertNotIn('aria-current="page">Motiv anfragen', html)

    def test_llms_txt_nennt_bleiche_und_luebeck(self):
        t = self.hole('/llms.txt').content.decode()
        self.assertIn('Bleiche', t)
        self.assertIn('heute in Luebeck', t)


@override_settings(PAYPAL_CLIENT_ID='test-client-id')
@mock.patch.dict(os.environ, {'PAYPAL_SECRET': 'test-secret', 'PAYPAL_MODE': 'sandbox'})
class KaufwegOhne500Test(LuviqTestCase):
    """Warenkorb, Kasse, Profil, Zahlung: alles 200 (oder die geplante Umleitung), nie 500 –
    auch wenn ein Stück ein Bild trägt, das es im Manifest nicht gibt."""

    def setUp(self):
        self.kundin = erzeuge_benutzer('kundin')
        self.kundin.profile.email_verified = True
        self.kundin.profile.save()
        self.produkt = erzeuge_produkt(
            'Bemalte Jacke', preis=Decimal('80.00'), lagerbestand=1,
            bild_statisch='shop1/images/gibt-es-nicht/x-{w}.webp@600#600x750')
        self.client.force_login(self.kundin)

    def test_startseite_und_karte_mit_kaputtem_bild_liefern_200(self):
        for pfad in ('/', '/produkte/', self.produkt.get_absolute_url()):
            with self.subTest(pfad=pfad):
                self.assertEqual(self.hole(pfad).status_code, 200)

    def test_kaufweg_liefert_mit_verkauf_200(self):
        with override_settings(VERKAUF_AKTIV=True):
            self.assertEqual(self.hole('/warenkorb/').status_code, 200)
            korb, _ = Cart.objects.get_or_create(user=self.kundin)
            CartItem.objects.create(cart=korb, produkt_name=self.produkt.name,
                                    produkt_preis=self.produkt.preis, menge=1)
            self.assertEqual(self.hole('/warenkorb/').status_code, 200)
            self.assertEqual(self.hole('/checkout/').status_code, 200)
            self.assertEqual(self.hole('/profil/').status_code, 200)
            antwort = self.sende('/checkout/', LIEFERADRESSE)
            self.assertEqual(antwort.status_code, 302)
            bestellung = Order.objects.get(user=self.kundin)
            self.assertEqual(self.hole(f'/payment/{bestellung.id}/').status_code, 200)
            self.assertEqual(self.hole('/profil/').status_code, 200)
            bestellung.status = 'paid'
            bestellung.save()
            self.assertEqual(self.hole(f'/payment/success/{bestellung.id}/').status_code, 200)

    def test_kaufweg_ohne_verkauf_leitet_um_statt_500(self):
        for pfad in ('/warenkorb/', '/checkout/'):
            with self.subTest(pfad=pfad):
                self.assertEqual(self.hole(pfad).status_code, 302)
        self.assertEqual(self.hole('/profil/').status_code, 200)
