"""SEO/GEO-Upgrade vom 02.11.2026 (Schema ohne Privatdaten, Archiv ohne Angebot, Engel-FAQ, Anleitung).

Prüfbefehl: python manage.py test shop1.tests.test_seo_upgrade_2026_11_02
"""

import json
import re
from decimal import Decimal

from django.test import override_settings

from shop1 import luviq_daten
from ._basis import LuviqTestCase, erzeuge_produkt


def _json_ld(html):
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def _roh_ld(html):
    return ' '.join(re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S))


class _Daten(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.engel = erzeuge_produkt(
            name='Engel-Shirt, mit Bleiche gemalt', slug=luviq_daten.ENGEL_STUECK['slug'], preis=Decimal('69.00'),
            masse='Größe M (Second-Hand-Shirt), Maße auf Anfrage', material='100 % Baumwolle', lagerbestand=1,
            vergeben=False, zustand='Gebraucht (Second Hand), von Hand mit Bleiche gemalt', serie=True,
            bearbeitungstage=3, technik='Mit Bleiche von Hand gemalt')
        self.archiv = erzeuge_produkt(
            name='Custom Hoodie mit Print', preis=Decimal('59.00'), lagerbestand=1, vergeben=True,
            zustand='Gebraucht', nummer=3)


class SchemaOhnePrivatdatenTest(_Daten):
    """A1/A3: keine Straße, PLZ oder E-Mail im Schema; Online-Shop statt Ladengeschäft."""

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_kein_privatdatum_im_json_ld_jeder_inhaltsseite(self):
        for pfad in ('/', '/kontakt/', '/produkte/', '/ueber_uns/', f'/produkt/{self.engel.slug}/',
                     '/wissen/', '/wissen/groesse-bei-einzelstuecken/'):
            ld = _roh_ld(self.hole(pfad).content.decode())
            for verboten in (luviq_daten.ANBIETERIN['strasse'], luviq_daten.ANBIETERIN['plz'], '@gmail.com',
                             'streetAddress', 'postalCode'):
                with self.subTest(pfad=pfad, verboten=verboten):
                    if pfad.startswith('/wissen/groesse') and verboten == '@gmail.com':
                        continue  # sichtbarer FAQ-Text der Größenseite nennt die Kontaktadresse, Schema = Text
                    self.assertNotIn(verboten, ld)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_organisation_ist_online_shop_mit_kontaktseite(self):
        knoten = next(k for k in _json_ld(self.hole('/').content.decode())
                      for k in k.get('@graph', [k]) if str(k.get('@id', '')).endswith('/#organization'))
        self.assertEqual(knoten['@type'], ['Organization', 'OnlineStore'])
        self.assertEqual(knoten['address']['addressLocality'], 'Lübeck')
        self.assertEqual(knoten['areaServed'], {'@type': 'Country', 'name': 'Deutschland'})
        self.assertNotIn('priceRange', knoten)
        self.assertNotIn('email', knoten)
        self.assertTrue(knoten['contactPoint']['url'].endswith('/kontakt/'))
        for typ in ('LocalBusiness', 'ClothingStore'):
            self.assertNotIn(typ, json.dumps(knoten))


class ArchivOhneAngebotTest(_Daten):
    """A2: Archivstücke tragen weder Offer noch Preis noch SoldOut im Schema."""

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_archivstueck_hat_kein_offer(self):
        html = self.hole(f'/produkt/{self.archiv.slug}/').content.decode()
        ld = _roh_ld(html)
        for wort in ('"offers"', 'SoldOut', 'OutOfStock', '"price"', 'availability'):
            self.assertNotIn(wort, ld)
        self.assertIn('VisualArtwork', ld)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_uebersicht_zeigt_offer_nur_fuer_das_kaufbare_stueck(self):
        html = self.hole('/produkte/').content.decode()
        knoten = [k for b in _json_ld(html) for k in b.get('@graph', [b])]
        archiv = next(k for k in knoten if k.get('name') == self.archiv.name)
        engel = next(k for k in knoten if k.get('name') == self.engel.name)
        self.assertNotIn('offers', archiv)
        self.assertEqual(archiv['@type'], 'VisualArtwork')
        self.assertEqual(engel['@type'], 'Product')
        self.assertEqual(engel['offers']['availability'], 'https://schema.org/InStock')

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_sichtbar_nie_verkauft_auf_dem_archivstueck(self):
        html = self.hole(f'/produkt/{self.archiv.slug}/').content.decode()
        self.assertNotIn('Verkauft', re.sub(r'<script.*?</script>', '', html, flags=re.S))

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_llms_txt_trennt_bestellbare_stuecke_und_archiv(self):
        text = self.hole('/llms.txt').content.decode()
        oben, archiv = text.split('### Archiv (vergeben, nicht bestellbar, ohne Preis)', 1)
        archiv = archiv.split('\n## ', 1)[0]
        self.assertIn('69.00 EUR', oben)
        self.assertNotIn('59.00', archiv)
        self.assertNotIn('EUR', archiv)
        self.assertIn(self.archiv.name, archiv)
        self.assertNotIn(self.archiv.name, oben)


class EngelSeiteTest(_Daten):
    """A5/A4: sichtbare FAQ = FAQPage, mehr Inhaltslinks auf das Engel-Shirt."""

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_faq_ist_sichtbar_und_im_schema_wortgleich(self):
        html = self.hole(f'/produkt/{self.engel.slug}/').content.decode()
        faq = next(k for k in _json_ld(html) if k.get('@type') == 'FAQPage')
        sichtbar = ' '.join(re.sub(r'<[^>]+>', ' ', re.sub(r'<script.*?</script>', '', html, flags=re.S)).split())
        import html as h
        sichtbar = h.unescape(sichtbar)
        self.assertEqual(len(faq['mainEntity']), 6)
        for frage in faq['mainEntity']:
            with self.subTest(frage=frage['name']):
                self.assertIn(frage['name'], sichtbar)
                self.assertIn(' '.join(frage['acceptedAnswer']['text'].split()), sichtbar)
        self.assertIn('T-Shirt mit Engel', sichtbar)
        alles = json.dumps(faq, ensure_ascii=False)
        self.assertIn('Größe M', alles)
        self.assertIn('Bearbeitung dauert ca. 3 Werktage', alles)
        for tabu in ('Rabatt', 'Code', '%'):
            self.assertNotIn(tabu, alles.replace('100 %', ''))

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_engel_seite_verlinkt_pflege_groesse_und_versand(self):
        html = self.hole(f'/produkt/{self.engel.slug}/').content.decode()
        for ziel in ('/wissen/pflege-handbemalte-kleidung/', '/wissen/groesse-bei-einzelstuecken/', '/liefergebiet/'):
            self.assertIn(f'href="{ziel}"', html)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_archivstueck_hat_keine_engel_faq(self):
        html = self.hole(f'/produkt/{self.archiv.slug}/').content.decode()
        self.assertNotIn('"FAQPage"', html)

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_acht_seiten_verlinken_das_engel_shirt_im_text(self):
        ziel = f'href="/produkt/{self.engel.slug}/"'
        for pfad in ('/wissen/pflege-handbemalte-kleidung/', '/wissen/groesse-bei-einzelstuecken/',
                     '/wissen/upcycling-mode-second-hand-vintage/', '/wissen/bleichfleck-uebermalen/',
                     '/wissen/bestellen-und-bezahlen/', '/ueber_uns/', '/liefergebiet/', '/motiv-anfragen/'):
            with self.subTest(pfad=pfad):
                self.assertIn(ziel, self.hole(pfad).content.decode())


class StartseiteTest(_Daten):
    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
    def test_startseite_sagt_ehrlich_kein_laden(self):
        html = self.hole('/').content.decode()
        self.assertIn('Einen Laden zum Anschauen gibt es nicht: Luviq ist ein Online-Shop', html)

    @override_settings(VERKAUF_AKTIV=False)
    def test_ohne_verkauf_keine_bestellaussage(self):
        html = self.hole('/').content.decode()
        self.assertIn('Einen Laden zum Anschauen gibt es nicht.', html)
        self.assertNotIn('bestellt wird auf dieser Seite', html)


class BleichflecksEntfernenTest(_Daten):
    """A7: neuer Abschnitt mit Antwort zuerst und geprüften Quellen."""

    def test_abschnitt_und_schema(self):
        html = self.hole('/wissen/bleichfleck-uebermalen/').content.decode()
        frage = 'Lassen sich Bleichflecken aus Kleidung entfernen?'
        self.assertIn(f'<h2 class="lv-serif">{frage}</h2>', html)
        faq = next(k for k in _json_ld(html) if k.get('@type') == 'FAQPage')
        self.assertIn(frage, [f['name'] for f in faq['mainEntity']])
        self.assertIn('https://www.bfr.bund.de/cm/350/risiko-vergiftungsunfaelle-bei-kindern.pdf', html)
        self.assertIn('https://www.verbraucherzentrale.de/sites/default/files/2018-10/chemie_im_haushalt.pdf', html)


class AnleitungTest(_Daten):
    """B1: neue Seite /wissen/bleach-painting-anleitung/."""
    PFAD = '/wissen/bleach-painting-anleitung/'

    def test_seite_ist_indexierbar_in_sitemap_und_llms(self):
        antwort = self.hole(self.PFAD)
        self.assertEqual(antwort.status_code, 200)
        html = antwort.content.decode()
        self.assertIn('index, follow', html)
        self.assertIn(self.PFAD, self.hole('/sitemap.xml').content.decode())
        self.assertIn(self.PFAD, self.hole('/llms.txt').content.decode())
        self.assertIn(self.PFAD, self.hole('/wissen/').content.decode())

    def test_quellen_und_keine_gesundheitsversprechen(self):
        html = self.hole(self.PFAD).content.decode()
        sichtbar = re.sub(r'<script.*?</script>', '', html, flags=re.S)
        for quelle in ('bfr.bund.de/cm/350/risiko-vergiftungsunfaelle-bei-kindern.pdf',
                       'bfr.bund.de/presseinformation/vorsicht-vor-vergiftungen-im-haushalt-und-hobbybereich/',
                       'verbraucherzentrale.de/sites/default/files/2018-10/chemie_im_haushalt.pdf'):
            self.assertIn(quelle, html)
        self.assertIn('Nie ein chlorhaltiges Produkt mit anderen Reinigern mischen. Es kann gefährliches Chlorgas entstehen!',
                      sichtbar)
        for versprechen in ('ungefährlich', 'gesundheitlich unbedenklich', 'garantiert', 'risikofrei'):
            self.assertNotIn(versprechen, sichtbar.lower())

    def test_verlinkung_rein_und_raus(self):
        for von in ('/wissen/bleach-painting/', '/wissen/bleichfleck-uebermalen/',
                    '/wissen/pflege-handbemalte-kleidung/'):
            with self.subTest(von=von):
                self.assertIn(f'href="{self.PFAD}"', self.hole(von).content.decode())
        self.assertIn(f'href="{self.PFAD}"', self.hole('/wissen/').content.decode())
        html = self.hole(self.PFAD).content.decode()
        for ziel in ('/wissen/bleach-painting/', '/wissen/bleichfleck-uebermalen/',
                     '/wissen/pflege-handbemalte-kleidung/', '/motiv-anfragen/',
                     f'/produkt/{self.engel.slug}/'):
            with self.subTest(ziel=ziel):
                self.assertIn(f'href="{ziel}"', html)
