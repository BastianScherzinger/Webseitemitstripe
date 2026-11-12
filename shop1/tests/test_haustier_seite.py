"""Haustier aufs Shirt (``/haustier-shirt/``, Entwurf 12.11.2026): Schalter, Kopfangaben, Schema, Preise.

Die Seite gibt es nur mit ``HAUSTIER_SEITE_AKTIV`` (Vorgabe aus: 404, nicht in Sitemap, llms.txt, llms-full.txt).
Prüfbefehl: python manage.py test shop1.tests.test_haustier_seite
"""

import json
import re
from decimal import Decimal

from django.test import override_settings

from shop1 import luviq_daten
from ._basis import LuviqTestCase, erzeuge_produkt
from .test_seo import BESCHREIBUNG_MAX, BESCHREIBUNG_MIN, HANDLUNGSVERBEN, ORT_ODER_NUTZEN

PFAD = '/haustier-shirt/'


def _json_ld(html):
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def _knoten(html):
    """Alle JSON-LD-Knoten, auch aus einem ``@graph``."""
    liste = []
    for block in _json_ld(html):
        liste += block.get('@graph', [block]) if isinstance(block, dict) else block
    return liste


def _text(html):
    haupt = re.search(r'<main.*?</main>', html, re.S)
    ohne = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', haupt.group(0) if haupt else html, flags=re.S)
    return ' '.join(re.sub(r'<[^>]+>', ' ', ohne).split())


class SchalterAusTest(LuviqTestCase):
    """Vorgabe aus: die Seite ist unsichtbar, bis Luisa Ja gesagt hat."""

    @override_settings(HAUSTIER_SEITE_AKTIV=False)
    def test_ohne_schalter_ist_die_seite_404_und_nirgends_genannt(self):
        self.assertEqual(self.hole(PFAD).status_code, 404)
        self.assertNotIn('haustier-shirt', self.hole('/sitemap.xml').content.decode())
        self.assertNotIn('haustier-shirt', self.hole('/llms.txt').content.decode())
        self.assertNotIn('haustier-shirt', self.hole('/llms-full.txt').content.decode())

    def test_die_vorgabe_ist_aus(self):
        """Verhindert, dass die Seite ohne Luisas Ja ausgeliefert wird, wenn die Umgebungsvariable fehlt."""
        from django.conf import settings
        import os
        if 'HAUSTIER_SEITE_AKTIV' not in os.environ:
            self.assertFalse(settings.HAUSTIER_SEITE_AKTIV)

    @override_settings(HAUSTIER_SEITE_AKTIV=False)
    def test_andere_seiten_verlinken_die_adresse_nicht(self):
        for pfad in ('/', '/motiv-anfragen/', '/produkte/', '/ueber_uns/', '/wissen/bleach-painting/'):
            self.assertNotIn(PFAD, self.hole(pfad).content.decode(), pfad)


@override_settings(HAUSTIER_SEITE_AKTIV=True)
class SchalterAnTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.html = self.hole(PFAD).content.decode()

    def test_seite_antwortet_200_und_ist_indexierbar(self):
        antwort = self.hole(PFAD)
        self.assertEqual(antwort.status_code, 200)
        self.assertIn('<meta name="robots" content="index, follow">', self.html)
        self.assertIn(f'<link rel="canonical" href="https://testserver{PFAD}">', self.html)

    def test_titel_beschreibung_h1(self):
        titel = re.search(r'<title>(.*?)</title>', self.html, re.S).group(1).strip()
        self.assertEqual(titel, 'Haustier aufs Shirt: nach Foto mit Bleiche gemalt | Luviq')
        self.assertTrue(25 <= len(titel) <= 70, len(titel))
        self.assertTrue(any(w in titel.lower() for w in ORT_ODER_NUTZEN), 'Titel nennt weder Ort noch Nutzen')
        beschreibung = re.search(r'<meta name="description" content="([^"]*)"', self.html).group(1)
        self.assertTrue(BESCHREIBUNG_MIN <= len(beschreibung) <= BESCHREIBUNG_MAX, len(beschreibung))
        letztes = re.findall(r'[\wäöüß]+', beschreibung.lower())[-1]
        self.assertIn(letztes, HANDLUNGSVERBEN)
        self.assertEqual(len(re.findall(r'<h1[ >]', self.html)), 1)
        self.assertIn('Dein Haustier aufs Shirt – von Hand mit Bleiche gemalt', self.html)

    def test_knopf_fuehrt_zum_formular_mit_vorwahl_tier(self):
        self.assertIn('href="/motiv-anfragen/?richtung=tier"', self.html)
        # Die Vorwahl gibt es schon (views/motiv.py): Richtung Tier ist angehakt.
        formular = self.hole('/motiv-anfragen/?richtung=tier').content.decode()
        self.assertRegex(formular, r'value="tier"[^>]*checked')

    def test_schema_service_faq_und_brotkrume(self):
        knoten = _knoten(self.html)
        arten = {k.get('@type') for k in knoten}
        self.assertTrue({'Service', 'FAQPage', 'BreadcrumbList', 'WebPage'} <= arten, arten)
        dienst = next(k for k in knoten if k.get('@type') == 'Service')
        self.assertNotIn('offers', dienst, 'kein Preis: den legt Luisa fest')
        self.assertNotIn('image', dienst, 'kein Beispielbild erfunden')
        self.assertTrue(dienst['provider']['@id'].endswith('/#organization'))
        faq = next(k for k in knoten if k.get('@type') == 'FAQPage')
        self.assertEqual([(f['name'], f['acceptedAnswer']['text']) for f in faq['mainEntity']],
                         luviq_daten.FAQ_HAUSTIER)
        for frage, antwort in luviq_daten.FAQ_HAUSTIER:  # wortgleich sichtbar
            self.assertIn(f'<h2 class="lv-serif">{frage}</h2>', self.html)
            self.assertIn(antwort, _text(self.html))
        kruemel = next(k for k in knoten if k.get('@type') == 'BreadcrumbList')
        self.assertEqual([e['name'] for e in kruemel['itemListElement']], ['Startseite', 'Haustier aufs Shirt'])
        seite = next(k for k in knoten if k.get('@type') == 'WebPage')
        self.assertEqual(seite['name'], 'Haustier aufs Shirt')
        self.assertEqual(seite['dateModified'], '2026-11-12')

    def test_widerrufssatz_ist_wortgleich_aus_luviq_daten(self):
        self.assertEqual(dict(luviq_daten.FAQ_HAUSTIER)['Kann ich das Shirt zurückgeben?'],
                         luviq_daten.AUFTRAG_WIDERRUF_SATZ)
        self.assertIn(luviq_daten.AUFTRAG_WIDERRUF_SATZ, _text(self.html))

    def test_faq_ohne_anfuehrungszeichen_und_backslashes(self):
        for frage, antwort in luviq_daten.FAQ_HAUSTIER:
            for zeichen in ('"', '\\'):
                self.assertNotIn(zeichen, frage + antwort)

    def test_kein_beispielbild_und_kein_bild_in_der_seite(self):
        haupt = re.search(r'<main.*?</main>', self.html, re.S).group(0)
        self.assertNotIn('<img', haupt)
        self.assertNotIn('<picture', haupt)

    def test_kein_preis_ausser_dem_engel_vergleich(self):
        """Ohne Verkauf steht keine Euro-Zahl auf der Seite; mit Verkauf nur der Engel-Preis aus den Produktdaten."""
        self.assertNotRegex(_text(self.html), r'\d\s*(€|Euro|EUR)')
        with override_settings(VERKAUF_AKTIV=True):
            text = _text(self.hole(PFAD).content.decode())
        self.assertRegex(text, r'Engel-Shirt gibt es für 69 € inkl\. Versand innerhalb Deutschlands')
        self.assertEqual(re.findall(r'\d+(?:,\d+)?\s*€', text), ['69 €'])
        self.assertEqual(luviq_daten.engel_preis_text(), '69 €')
        self.assertEqual(Decimal(luviq_daten.ENGEL_STUECK['preis']), Decimal('69.00'))

    def test_preis_satz_nennt_luisa_als_festleger(self):
        self.assertIn('Den Preis legt Luisa fest und schickt ihn dir mit den Vorschlägen', _text(self.html))

    def test_sitemap_llms_und_volltext_nennen_die_seite(self):
        sitemap = self.hole('/sitemap.xml').content.decode()
        self.assertIn(f'<loc>https://testserver{PFAD}</loc>', sitemap)
        self.assertRegex(sitemap, r'<loc>https://testserver/haustier-shirt/</loc>\s*<lastmod>2026-11-12</lastmod>')
        llms = self.hole('/llms.txt').content.decode()
        self.assertIn(f'(https://testserver{PFAD})', llms)
        for frage, _antwort in luviq_daten.FAQ_HAUSTIER[:3]:
            self.assertIn(f'### {frage}', llms)
        self.assertIn(f'Adresse: https://testserver{PFAD}', self.hole('/llms-full.txt').content.decode())

    def test_ohne_motivanfrage_fuehrt_der_knopf_zur_warteliste(self):
        with override_settings(MOTIVANFRAGE_AKTIV=False):
            html = self.hole(PFAD).content.decode()
        self.assertNotIn('richtung=tier', html)
        self.assertIn('#warteliste', html)


class ProduktSchemaTest(LuviqTestCase):
    """Product-Schema des Engel-Shirts: ``color`` und ``returnFees`` (nur, was die Daten belegen)."""

    @override_settings(VERKAUF_AKTIV=True)
    def test_color_nur_beim_engel_shirt(self):
        engel = erzeuge_produkt(name='Engel-Shirt, mit Bleiche gemalt', slug=luviq_daten.ENGEL_STUECK['slug'],
                                preis=Decimal('69.00'), lagerbestand=1, vergeben=False, serie=True)
        anderes = erzeuge_produkt(name='Andere Jacke', preis=Decimal('59.00'), lagerbestand=1, vergeben=False)
        produkt = next(k for k in _knoten(self.hole(engel.get_absolute_url()).content.decode())
                       if k.get('@type') == 'Product')
        self.assertEqual(produkt['color'], 'Schwarz')
        fremd = next(k for k in _knoten(self.hole(anderes.get_absolute_url()).content.decode())
                     if k.get('@type') == 'Product')
        self.assertNotIn('color', fremd)

    @override_settings(VERKAUF_AKTIV=True)
    def test_return_fees_in_regel_und_offer(self):
        engel = erzeuge_produkt(name='Engel-Shirt, mit Bleiche gemalt', slug=luviq_daten.ENGEL_STUECK['slug'],
                                preis=Decimal('69.00'), lagerbestand=1, vergeben=False, serie=True)
        knoten = _knoten(self.hole(engel.get_absolute_url()).content.decode())
        regel = next(k for k in knoten if k.get('@id', '').endswith('/#organization') and k.get('name'))['hasMerchantReturnPolicy']
        fees = 'https://schema.org/ReturnFeesCustomerResponsibility'
        self.assertEqual(regel['returnFees'], fees)
        produkt = next(k for k in knoten if k.get('@type') == 'Product')
        self.assertEqual(produkt['offers']['hasMerchantReturnPolicy']['returnFees'], fees)
