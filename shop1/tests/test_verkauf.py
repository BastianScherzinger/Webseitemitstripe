"""Verkaufsschalter (``shop1/verkauf.py``, ``settings.VERKAUF_AKTIV``).

Solange kein Gewerbe angemeldet ist, steht der Schalter auf aus (Vorgabe) und
die Seite ist eine „Marke im Aufbau": keine Preise, kein Warenkorb, keine
Kasse, kein PayPal-Skript, keine Sätze zu § 19 UStG, Zahlung oder Versand,
kein ``Offer`` im Schema, AGB nicht verlinkt und ``noindex``. Mit
``VERKAUF_AKTIV=True`` muss alles zurückkommen – der Schalter darf den Shop
verstecken, aber nicht beschädigen. Beide Zustände stehen hier.

Die übrigen Kauftests (``test_warenkorb``, ``test_zahlung``, …) laufen mit
``@override_settings(VERKAUF_AKTIV=True)``; sie prüfen den Shop dahinter.
"""

import json
import re
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import override_settings

from ..models import Comment, Order
from ._basis import OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

PREIS = Decimal('87.50')

#: Kaufwege, die ohne Verkauf umleiten müssen – jeweils GET und POST.
KAUFWEGE = [
    '/warenkorb/',
    '/warenkorb/add/{pid}/',
    '/warenkorb/remove/Stueck/',
    '/warenkorb/update/Stueck/',
    '/checkout/',
    '/payment/{oid}/',
    '/payment/success/{oid}/',
    '/payment/cancel/',
]

#: Sätze, die ohne Verkauf in keiner öffentlichen Ausgabe stehen dürfen.
VERBOTEN_OHNE_VERKAUF = ['19 UStG', 'Endpreis', 'Kleinunternehm', 'Willkommensrabatt',
                         'In den Warenkorb', 'Add to Orbit']

#: Zahlungsarten dürfen nur noch in den AGB und im Wissensbereich stehen – dort
#: ist jede Seite noindex und trägt oben den Hinweis „gilt ab Eröffnung des
#: Shops" – und in der Datenschutzerklärung, die sagt, dass PayPal nicht
#: geladen wird.
ZAHLUNG = ['Vorab-Überweisung', 'PayPal']


def _json_ld(html):
    """Alle JSON-LD-Blöcke einer Seite als Text."""
    return '\n'.join(re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S))


class _Grundlage(LuviqTestCase):
    def setUp(self):
        self.produkt = erzeuge_produkt('Schalterstueck', preis=PREIS, lagerbestand=1)
        self.produktseite = self.produkt.get_absolute_url()
        self.kundin = erzeuge_benutzer('kundin')
        self.bestellung = Order.objects.create(
            user=self.kundin, vorname='K', nachname='D', email='k@example.org',
            adresse='Weg 1', stadt='Alsfeld', postleitzahl='36304', land='DE',
            gesamt_betrag=PREIS)

    def seiten(self):
        return OEFFENTLICHE_SEITEN + [self.produktseite]


class OhneVerkaufTest(_Grundlage):
    """Vorgabe: ``VERKAUF_AKTIV`` aus."""

    def test_die_vorgabe_ist_aus(self):
        """Verhindert, dass der Shop nach einem Deploy ohne Variable wieder
        verkauft – ohne Gewerbeanmeldung wäre das angreifbar."""
        from django.conf import settings
        self.assertFalse(settings.VERKAUF_AKTIV)

    def test_keine_seite_nennt_preis_steuer_oder_kaufweg(self):
        """Keine Preise, kein § 19 UStG, kein Warenkorb-Knopf – weder für Gäste
        noch für Angemeldete."""
        for angemeldet in (False, True):
            if angemeldet:
                self.client.force_login(self.kundin)
            for pfad in self.seiten():
                with self.subTest(pfad=pfad, angemeldet=angemeldet):
                    html = self.hole(pfad).content.decode()
                    self.assertNotIn('87,50', html)
                    self.assertNotIn('87.50', html)
                    for satz in VERBOTEN_OHNE_VERKAUF:
                        self.assertNotIn(satz, html)
                    if not pfad.startswith('/wissen/') and pfad not in ('/agb/', '/datenschutz/'):
                        for satz in ZAHLUNG:
                            self.assertNotIn(satz, html)
                    self.assertNotIn('/warenkorb/', html)
                    self.assertNotIn('/checkout/', html)

    def test_kein_paypal_skript(self):
        for pfad in self.seiten():
            with self.subTest(pfad=pfad):
                self.assertNotIn('paypal.com/sdk', self.hole(pfad).content.decode())

    def test_kaufwege_leiten_freundlich_auf_die_warteliste(self):
        """Nie ein 500, nie die View selbst: jeder Kaufweg endet auf der
        Warteliste der Startseite, mit Hinweis."""
        self.client.force_login(self.kundin)
        for muster in KAUFWEGE:
            pfad = muster.format(pid=self.produkt.id, oid=self.bestellung.id)
            for methode in (self.hole, self.sende):
                with self.subTest(pfad=pfad, methode=methode.__name__):
                    antwort = methode(pfad)
                    self.assertEqual(antwort.status_code, 302)
                    self.assertEqual(antwort['Location'], '/#newsletter-form')
        antwort = self.hole('/warenkorb/', follow=True)
        self.assertContains(antwort, 'Der Shop öffnet mit dem ersten Drop')

    def test_kaufwege_leiten_auch_gaeste_um(self):
        for muster in KAUFWEGE:
            pfad = muster.format(pid=self.produkt.id, oid=self.bestellung.id)
            with self.subTest(pfad=pfad):
                self.assertEqual(self.hole(pfad)['Location'], '/#newsletter-form')

    def test_der_paypal_rueckruf_antwortet_mit_json(self):
        """Das Skript der Bezahlseite erwartet JSON – eine Weiterleitung auf
        HTML wäre dort ein unlesbarer Fehler."""
        self.client.force_login(self.kundin)
        antwort = self.sende(f'/paypal/capture/{self.bestellung.id}/',
                             json.dumps({'paypal_order_id': 'X'}), content_type='application/json')
        self.assertEqual(antwort.status_code, 409)
        self.assertFalse(antwort.json()['verkauf_aktiv'])
        self.bestellung.refresh_from_db()
        self.assertEqual(self.bestellung.status, 'pending')

    def test_kein_angebot_im_schema(self):
        for pfad in ('/', '/produkte/', self.produktseite):
            with self.subTest(pfad=pfad):
                ld = _json_ld(self.hole(pfad).content.decode())
                for wort in ('"Offer"', 'OfferCatalog', '"price"', 'availability', 'priceRange',
                             'paymentAccepted', 'LocalBusiness', 'ClothingStore'):
                    self.assertNotIn(wort, ld)
                self.assertIn('"Organization"', ld)

    def test_agb_nicht_verlinkt_aber_erreichbar_und_noindex(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('href="/agb/"', html)
        agb = self.hole('/agb/')
        self.assertEqual(agb.status_code, 200)
        self.assertContains(agb, 'noindex, follow')
        self.assertContains(agb, 'gelten erst ab Eröffnung des Shops')
        self.assertNotIn('/agb/', self.hole('/sitemap.xml').content.decode())
        self.assertNotIn('/agb/', self.hole('/llms.txt').content.decode())

    def test_kaufbeitraege_im_wissen_sind_noindex_und_aus_sitemap_und_llms(self):
        sitemap = self.hole('/sitemap.xml').content.decode()
        llms = self.hole('/llms.txt').content.decode()
        for pfad in ('/wissen/bestellen-und-bezahlen/', '/wissen/widerruf-und-ruecksendung/',
                     '/wissen/konto-und-daten/'):
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertContains(antwort, 'noindex, follow')
                self.assertContains(antwort, 'ab Eröffnung des Shops')
                self.assertNotIn(pfad, sitemap)
                self.assertNotIn(pfad, llms)

    def test_llms_txt_ohne_kaufangaben(self):
        llms = self.hole('/llms.txt').content.decode()
        for wort in ('EUR', '19 UStG', 'PayPal', 'Ueberweisung', 'Versand', 'Werktag'):
            self.assertNotIn(wort, llms)
        self.assertIn('kein Verkauf', llms)
        self.assertIn(self.produktseite, llms)

    def test_impressum_ddg_ohne_os_plattform_mit_hinweis(self):
        html = self.hole('/impressum/').content.decode()
        self.assertIn('§ 5 DDG', html)
        self.assertNotIn('§ 5 TMG', html)
        self.assertNotIn('ec.europa.eu/consumers/odr', html)
        self.assertIn('Marke im Aufbau. Derzeit findet kein Verkauf statt.', html)
        self.assertIn('Grünberger Str. 16', html)
        self.assertIn('brehlerluisa@gmail.com', html)

    def test_die_warteliste_ist_das_ziel(self):
        """Ziel „Auf die Warteliste" ist die vorhandene Newsletter-Anmeldung
        mit Double-Opt-in – kein zweites Formular."""
        self.assertContains(self.hole('/'), 'id="newsletter-form"')
        self.assertContains(self.hole(self.produktseite), 'href="/#newsletter-form"')
        self.assertContains(self.hole('/'), 'Auf die Warteliste')

    def test_datenschutz_beschreibt_den_zustand_ohne_verkauf(self):
        html = self.hole('/datenschutz/').content.decode()
        self.assertIn('keine Bestellungen an und verarbeitet keine Zahlungsdaten', html)
        self.assertIn('Double-Opt-in', html)
        self.assertNotIn('ip-api.com', html)
        self.assertIn('kein Cookie', html)


class BewertungenTest(_Grundlage):
    """UWG Anh. Nr. 23b/23c: keine fest eingetippten Sterne, und Beiträge der
    Betreiberin stehen auf der Startseite nicht als Stimmen anderer."""

    def test_keine_festen_sterne_und_keine_erfundene_durchschnittsnote(self):
        Comment.objects.create(user=self.kundin, text='Schoen bemalt')
        for pfad in ('/', '/gaestebuch/'):
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                self.assertNotIn('★', html)
                self.assertNotIn('>5.0<', html)
                self.assertNotIn('Community &amp; Bewertungen', html)

    def test_beitraege_der_betreiberin_fehlen_auf_der_startseite(self):
        chefin = User.objects.create_superuser('shopbesitzer', 'a@example.org', 'ein-langes-passwort')
        luisa = erzeuge_benutzer('luisabre')
        mitarbeit = erzeuge_benutzer('team', is_staff=True)
        Comment.objects.create(user=chefin, text='Beitrag vom Adminkonto')
        Comment.objects.create(user=luisa, text='Beitrag von luisabre')
        Comment.objects.create(user=mitarbeit, text='Beitrag vom Team')
        Comment.objects.create(user=self.kundin, text='Beitrag einer Kundin')

        start = self.hole('/').content.decode()
        self.assertIn('Beitrag einer Kundin', start)
        for text in ('Beitrag vom Adminkonto', 'Beitrag von luisabre', 'Beitrag vom Team'):
            self.assertNotIn(text, start)
        # Im Gästebuch bleiben alle stehen – gelöscht wird nichts.
        gaestebuch = self.hole('/gaestebuch/').content.decode()
        for text in ('Beitrag vom Adminkonto', 'Beitrag von luisabre', 'Beitrag einer Kundin'):
            self.assertIn(text, gaestebuch)
        self.assertEqual(Comment.objects.count(), 4)

    def test_kein_platzhalter_im_registrierungsformular(self):
        html = self.hole('/register/').content.decode()
        for rest in ('Musterstraße', '12345', '123456', 'info@luviq.universe'):
            self.assertNotIn(rest, html)


class AdminBleibtTest(_Grundlage):
    """Ohne Verkauf bleiben die Bestellungen im Panel erreichbar."""

    def test_bestellungen_im_panel(self):
        chefin = User.objects.create_superuser('chefin', 'c@example.org', 'ein-langes-passwort')
        self.client.force_login(chefin)
        self.assertEqual(self.hole('/shop-admin/orders/').status_code, 200)
        self.assertEqual(self.hole(f'/shop-admin/orders/{self.bestellung.id}/').status_code, 200)


@override_settings(VERKAUF_AKTIV=True)
class MitVerkaufTest(_Grundlage):
    """``VERKAUF_AKTIV=1``: der bisherige Shop ist unverändert zurück."""

    def test_preise_und_steuerhinweis_sind_zurueck(self):
        for pfad in ('/', '/produkte/', self.produktseite):
            with self.subTest(pfad=pfad):
                self.assertRegex(self.hole(pfad).content.decode(), r'87[.,]50 €')
        self.assertContains(self.hole('/produkte/'), '§ 19 UStG')

    def test_warenkorb_knopf_und_warenkorb(self):
        self.client.force_login(self.kundin)
        self.assertContains(self.hole(self.produktseite), f'/warenkorb/add/{self.produkt.id}/')
        self.assertEqual(self.hole('/warenkorb/').status_code, 200)
        self.hole(f'/warenkorb/add/{self.produkt.id}/')
        self.assertEqual(self.kundin.cart.items.count(), 1)

    def test_angebot_im_schema_und_agb_im_fuss(self):
        self.assertIn('"Offer"', _json_ld(self.hole(self.produktseite).content.decode()))
        self.assertIn('LocalBusiness', _json_ld(self.hole('/').content.decode()))
        self.assertContains(self.hole('/'), 'href="/agb/"')
        self.assertContains(self.hole('/agb/'), 'index, follow')
        self.assertIn('/agb/', self.hole('/sitemap.xml').content.decode())

    def test_kaufbeitraege_wieder_im_index(self):
        sitemap = self.hole('/sitemap.xml').content.decode()
        self.assertIn('/wissen/bestellen-und-bezahlen/', sitemap)
        self.assertNotIn('noindex', self.hole('/wissen/bestellen-und-bezahlen/').content.decode()
                         .split('name="robots" content="')[1][:8])

    def test_llms_txt_mit_preisen(self):
        llms = self.hole('/llms.txt').content.decode()
        self.assertRegex(llms, r'87[.,]50 EUR')
        self.assertIn('19 UStG', llms)
