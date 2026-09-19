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
from ._basis import (KAUFWEG_WISSENSSEITEN, OEFFENTLICHE_SEITEN, LuviqTestCase,
                     erzeuge_benutzer, erzeuge_produkt)

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

    def test_kaufbeitraege_im_wissen_leiten_um_und_fehlen_ueberall(self):
        """Seit 18.09.2026 abends: Bestellen, Widerruf und Konto leiten ohne
        Verkauf mit 302 (nicht 301 – sie kommen zurück) auf /wissen/ und
        stehen weder in der Übersicht noch in Sitemap, llms.txt und Feed."""
        sitemap = self.hole('/sitemap.xml').content.decode()
        llms = self.hole('/llms.txt').content.decode()
        feed = self.hole('/feed/').content.decode()
        uebersicht = self.hole('/wissen/').content.decode()
        for pfad in KAUFWEG_WISSENSSEITEN:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(antwort.status_code, 302)
                self.assertEqual(antwort['Location'], '/wissen/')
                for text in (sitemap, llms, feed, uebersicht):
                    self.assertNotIn(pfad, text)
        for titel in ('Wie bestelle und bezahle ich', 'Widerruf und Rücksendung',
                      'warum braucht der Kauf ein Konto'):
            self.assertNotIn(titel, uebersicht)

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
        # Seit dem Umbau „Nachtausgabe" (19.09.2026) heißt der Knopf auf der
        # Startseite „Eintragen" (Vorlage); „Auf die Warteliste" steht auf
        # der Stückseite, dort ist es die Haupthandlung.
        self.assertContains(self.hole(self.produktseite), 'Auf die Warteliste')

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

        # Seit dem Umbau „Nachtausgabe" (19.09.2026) zeigt die Startseite gar
        # keine Gästebuch-Beiträge mehr (Bauplan § 2) – erst recht keine der
        # Betreiberin als Stimmen anderer.
        start = self.hole('/').content.decode()
        for text in ('Beitrag vom Adminkonto', 'Beitrag von luisabre', 'Beitrag vom Team', 'Beitrag einer Kundin'):
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

    def test_kaufbeitraege_antworten_und_stehen_in_der_uebersicht(self):
        """Gegenprobe zur 302-Umleitung: mit Verkauf sind die drei Beiträge
        wie bisher da – mit ``h1``, FAQ- und Article-Schema."""
        uebersicht = self.hole('/wissen/').content.decode()
        for pfad in KAUFWEG_WISSENSSEITEN:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(antwort.status_code, 200)
                html = antwort.content.decode()
                self.assertIn('<h1', html)
                ld = _json_ld(html)
                self.assertIn('FAQPage', ld)
                self.assertIn('Article', ld)
                self.assertIn(f'href="{pfad}"', uebersicht)

    def test_llms_txt_mit_preisen(self):
        llms = self.hole('/llms.txt').content.decode()
        self.assertRegex(llms, r'87[.,]50 EUR')
        self.assertIn('19 UStG', llms)


# ---------------------------------------------------------------------------
# Archiv statt „kommender Drop" (18.09.2026 abends)
# ---------------------------------------------------------------------------

#: Aussagen, die ohne Verkauf nirgends öffentlich stehen dürfen: die Stücke
#: gehören nicht zum kommenden Drop (sie sind vergeben), und nichts behauptet
#: einen stattgefundenen Verkauf, Kundschaft oder Versand.
VERBOTEN_IM_ARCHIV = [
    'Kommender Drop', 'kommenden Drop', 'gehört zum', 'gehören zum ersten Drop',
    'Noch kein Verkauf · Start', 'Verkauft wird dieses Stück', 'Vorschau',
    '(Sold)', 'ausverkauft', 'sold out', 'Sold out',
    'Kundinnen und Kunden', 'unsere Kunden', 'Shopbesitzer',
    'verkauft ausschließlich', 'versendet deutschlandweit', 'versendet wird',
    'Versendet wird', 'Wie kaufe ich',
]


class ArchivOhneVerkaufTest(_Grundlage):
    """Ohne Verkauf erscheinen die Stücke neutral als Archiv bisheriger Stücke."""

    def test_karten_karussell_und_produktseite_zeigen_das_archiv(self):
        # Archivnummer aus dem Feld ``nummer`` (Migration 0024), auf den
        # Karten als „Nº 001" + „vergeben", auf der Stückseite zusätzlich
        # „Nº 001 · Archiv · Bereits vergeben …".
        nummer = f'Nº {self.produkt.archiv_nummer}'
        for pfad in ('/', '/produkte/', self.produktseite):
            with self.subTest(pfad=pfad):
                self.assertContains(self.hole(pfad), nummer)
                self.assertContains(self.hole(pfad), 'vergeben')
        self.assertContains(self.hole(self.produktseite), f'{nummer} · Archiv')
        produktseite = self.hole(self.produktseite).content.decode()
        self.assertIn('Dieses Stück ist bereits vergeben. Neue Stücke gibt es mit dem ersten '
                      'Drop – trag dich in die Warteliste ein', produktseite)
        self.assertIn('aus dem Archiv der bisherigen Stücke', produktseite)
        self.assertIn('Bereits vergeben · Neue Stücke mit dem ersten Drop', produktseite)

    def test_keine_seite_behauptet_kommenden_drop_oder_verkauf(self):
        for pfad in self.seiten() + ['/llms.txt', '/feed/']:
            html = self.hole(pfad).content.decode()
            for satz in VERBOTEN_IM_ARCHIV:
                with self.subTest(pfad=pfad, satz=satz):
                    self.assertNotIn(satz, html)

    def test_titel_und_beschreibung_ohne_kaufen(self):
        html = self.hole(self.produktseite).content.decode()
        titel = re.search(r'<title>(.*?)</title>', html, re.S).group(1)
        self.assertNotIn('kaufen', titel)
        self.assertIn('Archiv', self.produkt.meta_description)
        self.assertIn('Archiv', re.search(r'<title>(.*?)</title>',
                                          self.hole('/produkte/').content.decode(), re.S).group(1))

    def test_ueberschriften_heissen_archiv(self):
        self.assertContains(self.hole('/produkte/'), 'id="archiv-titel">Das Archiv</h1>')
        self.assertContains(self.hole('/'), 'id="archiv-titel">Das Archiv</h2>')
        self.assertContains(self.hole('/'), 'Diese Stücke sind vergeben')

    def test_llms_txt_nennt_das_archiv(self):
        llms = self.hole('/llms.txt').content.decode()
        self.assertIn('## Archiv: bisherige Einzelstuecke (bereits vergeben)', llms)
        self.assertNotIn('ersten Drops', llms)
        self.assertIn(self.produktseite, llms)

    def test_gaestebuch_kennzeichnet_die_betreiberin(self):
        chefin = User.objects.create_superuser('chefin', 'c@example.org', 'ein-langes-passwort')
        beitrag = Comment.objects.create(user=self.kundin, text='Schoen bemalt')
        Comment.objects.create(user=chefin, text='Danke', parent=beitrag, is_admin_reply=True)
        html = self.hole('/gaestebuch/').content.decode()
        self.assertIn('Betreiberin', html)
        self.assertNotIn('Shopbesitzer', html)


@override_settings(VERKAUF_AKTIV=True)
class ArchivMitVerkaufTest(_Grundlage):
    """Mit Verkauf ist alles wie vor dem Archiv-Umbau."""

    def test_preis_statt_archivnummer(self):
        for pfad in ('/', '/produkte/', self.produktseite):
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                self.assertNotIn('· Archiv', html)
                self.assertNotIn('<span>vergeben</span>', html)
                self.assertRegex(html, r'87[.,]50 €')
        self.assertContains(self.hole('/'), 'Jedes Stück gibt es genau einmal.')

    def test_titel_mit_kaufen_und_antwortsatz_mit_preis(self):
        html = self.hole(self.produktseite).content.decode()
        self.assertIn('Schalterstueck kaufen – Luviq Universe, Alsfeld', html)
        self.assertIn('Schalterstueck ist ein handbemaltes 1-of-1 Unikat von Luisa Brehler aus '
                      '36304 Alsfeld in Hessen und kostet 87,50 €', html)
        self.assertNotIn('Archiv', self.produkt.meta_description)

    def test_gaestebuch_wie_bisher(self):
        chefin = User.objects.create_superuser('chefin', 'c@example.org', 'ein-langes-passwort')
        beitrag = Comment.objects.create(user=self.kundin, text='Schoen bemalt')
        Comment.objects.create(user=chefin, text='Danke', parent=beitrag, is_admin_reply=True)
        html = self.hole('/gaestebuch/').content.decode()
        self.assertIn('Shopbesitzer', html)
        self.assertIn('Kundinnen und Kunden', html)


class AlterVerkaufsslugTest(LuviqTestCase):
    """Die alte Adresse mit Verkaufsvermerk leitet per 301 auf die neue."""

    def test_alter_slug_leitet_dauerhaft_um(self):
        stueck = erzeuge_produkt('Custom Pants')
        self.assertEqual(stueck.slug, 'custom-pants')
        for alt in ('/produkt/custom-pants-sold/', '/produkt/custom-pants-verkauft/',
                    '/produkt/custom-pants-sold-1/'):
            with self.subTest(alt=alt):
                antwort = self.hole(alt)
                self.assertEqual(antwort.status_code, 301)
                self.assertEqual(antwort['Location'], '/produkt/custom-pants/')

    def test_mit_kollisionszaehler(self):
        erzeuge_produkt('Custom Pants', aktiv=False)
        zweites = erzeuge_produkt('Custom Pants')
        self.assertEqual(zweites.slug, 'custom-pants-1')
        self.assertEqual(self.hole('/produkt/custom-pants-sold/')['Location'],
                         '/produkt/custom-pants-1/')

    def test_unbekannt_bleibt_404(self):
        self.assertEqual(self.hole('/produkt/gibt-es-nicht-sold/').status_code, 404)
        self.assertEqual(self.hole('/produkt/gibt-es-nicht/').status_code, 404)

    def test_ein_echter_slug_mit_sold_wird_nicht_umgeleitet(self):
        """Hat ein Stück heute (noch) einen solchen Slug, zeigt es sich selbst."""
        stueck = erzeuge_produkt('Irgendwas', slug='irgendwas-sold')
        self.assertEqual(self.hole('/produkt/irgendwas-sold/').status_code, 200)
        self.assertEqual(stueck.get_absolute_url(), '/produkt/irgendwas-sold/')


class VerkaufsvermerkMigrationTest(LuviqTestCase):
    """Migration 0022: Verkaufsvermerke fallen aus Namen, Beschreibungen und Slugs."""

    def _migration(self):
        import importlib
        return importlib.import_module('shop1.migrations.0022_produktnamen_ohne_verkaufsvermerk')

    def test_regeln_fuer_den_anhang(self):
        m = self._migration()
        faelle = {
            'Custom Pants (Sold)': 'Custom Pants',
            'Custom Pants (sold)': 'Custom Pants',
            'Custom Pants Sold': 'Custom Pants',
            'Jacke - Verkauft': 'Jacke',
            'Hoodie mit backprint -ausverkauft': 'Hoodie mit backprint',
            'Hoodie [SOLD OUT]': 'Hoodie',
            'Sold': 'Sold',
            'Sold Jacke': 'Sold Jacke',
            'Das Stück ist unverkauft': 'Das Stück ist unverkauft',
            'Gold': 'Gold',
            '': '',
        }
        for alt, neu in faelle.items():
            with self.subTest(alt=alt):
                self.assertEqual(m.ohne_vermerk(alt), neu)

    def test_bereinigen_an_der_datenbank(self):
        from django.apps import apps

        m = self._migration()
        hose = erzeuge_produkt('Custom Pants (Sold)', beschreibung='Pants with custom print')
        hoodie = erzeuge_produkt('Custom print hoodie',
                                 beschreibung='Custom hoodie mit print -ausverkauft')
        self.assertEqual(hose.slug, 'custom-pants-sold')
        m.bereinigen(apps, None)
        hose.refresh_from_db()
        hoodie.refresh_from_db()
        self.assertEqual(hose.name, 'Custom Pants')
        self.assertEqual(hose.slug, 'custom-pants')
        self.assertEqual(hose.beschreibung, 'Pants with custom print')
        self.assertEqual(hoodie.name, 'Custom print hoodie')
        self.assertEqual(hoodie.slug, 'custom-print-hoodie')
        self.assertEqual(hoodie.beschreibung, 'Custom hoodie mit print')
        # Die alte Adresse führt per 301 zur neuen.
        antwort = self.hole('/produkt/custom-pants-sold/')
        self.assertEqual(antwort.status_code, 301)
        self.assertEqual(antwort['Location'], '/produkt/custom-pants/')


class ArchivMetaangabenTest(LuviqTestCase):
    """Ohne Verkauf: Titel ohne „kaufen", Beschreibung mit Archiv-Zusatz –
    in denselben Grenzen wie mit Verkauf (``test_seo.ProduktMetaangabenTest``)."""

    def test_titel_und_beschreibung_in_den_grenzen(self):
        from ..models import (META_BESCHREIBUNG_MAX, META_BESCHREIBUNG_ZUSATZ_OHNE_VERKAUF,
                              META_TITEL_MAX, META_TITEL_ZUSAETZE_OHNE_VERKAUF)

        kurz = erzeuge_produkt('Bemalte Jacke', beschreibung='Handbemalt.')
        self.assertEqual(kurz.meta_title, 'Bemalte Jacke' + META_TITEL_ZUSAETZE_OHNE_VERKAUF[0])
        self.assertEqual(kurz.meta_description, 'Handbemalt.' + META_BESCHREIBUNG_ZUSATZ_OHNE_VERKAUF)
        lang = erzeuge_produkt('Handbemalte Vintage Jeansjacke mit dem Sonnenblumenmotiv und Ranken',
                               beschreibung='Wort ' * 100)
        self.assertLessEqual(len(lang.meta_title), META_TITEL_MAX)
        self.assertNotIn('kaufen', lang.meta_title)
        self.assertLessEqual(len(lang.meta_description), META_BESCHREIBUNG_MAX)
        self.assertTrue(lang.meta_description.endswith(META_BESCHREIBUNG_ZUSATZ_OHNE_VERKAUF))
