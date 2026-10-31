"""Direktkauf ohne Konto: keine Seite widerspricht dem Kaufweg (31.10.2026).

Mit ``VERKAUF_AKTIV`` und ``DIREKTKAUF`` darf auf keiner öffentlichen Seite (sichtbarer Text,
Meta-Beschreibungen, JSON-LD) mehr stehen, dass ein Konto, ein Warenkorb oder PayPal nötig sei oder
dass der Shop erst öffne. Die FAQ-Schemas der Wissensseiten müssen wortgleich zur Seite bleiben.

Prüfbefehl: python manage.py test shop1.tests.test_direktkauf_texte
"""

import json
import re
from decimal import Decimal

from django.test import override_settings

from ._basis import INDEXIERBARE_SEITEN, INHALTSSEITEN, LuviqTestCase, erzeuge_produkt
from .test_geo import FAQ_SEITEN, sichtbarer_text, schema_knoten, ueberschriften

#: Aussagen des alten Login-Wegs und der Vorverkaufszeit.
VERBOTEN = re.compile(
    r'Warenkorb|PayPal|frühestens|Willkommensrabatt|Konto (ist )?(bei Luviq Universe ohnehin )?nötig|'
    r'Anmeldung nötig|braucht ein Konto|Eröffnung des Shops|Anmelden und kaufen|Auf die Warteliste|'
    r'Zur Warteliste|Neue Stücke mit dem ersten Drop|noch nicht im Verkauf|kein Verkauf',
    re.I)

_META = re.compile(r'<meta[^>]+(?:name|property)="(?:description|og:description|og:title|twitter:description)"'
                   r'[^>]+content="([^"]*)"', re.I)


@override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
class DirektkaufTexteTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.enter = self.settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
        self.enter.enable()
        self.addCleanup(self.enter.disable)
        self.stueck = erzeuge_produkt(
            name='Engel-Shirt', preis=Decimal('69.00'), masse='Größe M', material='Baumwolle',
            lagerbestand=1, aktiv=True, vergeben=False, zustand='Neu, von Hand bemalt')

    def test_kein_widerspruch_zum_direktkauf(self):
        seiten = sorted((set(INHALTSSEITEN) | {f'/produkt/{self.stueck.slug}/', '/produkte/', '/', '/agb/', '/datenschutz/'})
                        - {'/impressum/'})
        for pfad in seiten:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                if antwort.status_code != 200:
                    continue
                html = antwort.content.decode()
                text = sichtbarer_text(html) + ' ' + ' '.join(_META.findall(html))
                for knoten in schema_knoten(html):
                    text += ' ' + json.dumps(knoten, ensure_ascii=False)
                treffer = VERBOTEN.search(text)
                self.assertIsNone(treffer, f'{pfad}: "{treffer.group(0) if treffer else ""}" widerspricht dem Direktkauf: '
                                  f'{text[max(0, (treffer.start() if treffer else 0) - 80):(treffer.end() if treffer else 0) + 80]}')

    def test_faq_schema_bleibt_wortgleich_zur_seite(self):
        for pfad in FAQ_SEITEN:
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                text = sichtbarer_text(html)
                titel = ueberschriften(html)
                fragen = [f for k in schema_knoten(html) if k.get('@type') == 'FAQPage'
                          for f in k.get('mainEntity', [])]
                self.assertTrue(fragen)
                for frage in fragen:
                    self.assertIn(' '.join(frage['name'].split()), titel)
                    self.assertIn(' '.join(frage['acceptedAnswer']['text'].split()), text)

    def test_bestellbeitrag_und_kontobeitrag_nennen_den_direktkauf(self):
        best = sichtbarer_text(self.hole('/wissen/bestellen-und-bezahlen/').content.decode())
        self.assertIn('ohne Konto', best)
        self.assertIn('Zahlungspflichtig bestellen', best)
        self.assertIn('Voraus per Überweisung', best)
        konto = sichtbarer_text(self.hole('/wissen/konto-und-daten/').content.decode())
        self.assertIn('Nein. Bestellt wird ohne Konto', konto)

    def test_stueckkarten_tragen_den_kaufknopf(self):
        for pfad in ('/', '/produkte/'):
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                self.assertIn(f'href="/produkt/{self.stueck.slug}/#bestellen"', html)
                self.assertIn('Direkt kaufen · 69 €', html)

    def test_stueckkarten_ohne_direktkauf_ohne_kaufknopf(self):
        with self.settings(DIREKTKAUF=False):
            self.assertNotIn('Direkt kaufen', self.hole('/produkte/').content.decode())

    def test_vormerken_statt_warteliste_bei_aktivem_verkauf(self):
        html = self.hole('/').content.decode()
        self.assertIn('Für das nächste Stück vormerken', sichtbarer_text(html))
        self.assertNotIn('Warteliste', sichtbarer_text(html))

    def test_fusslink_bleach_painting_auf_jeder_seite(self):
        for pfad in ('/', '/kontakt/', '/produkte/'):
            self.assertIn('href="/wissen/bleach-painting/"', self.hole(pfad).content.decode())

    def test_motiv_anfragen_titel_und_links(self):
        html = self.hole('/motiv-anfragen/').content.decode()
        self.assertIn('<title>Kleidung bemalen lassen: sag, was du willst | Luviq Lübeck</title>', html)
        self.assertIn('href="/wissen/bleach-painting/"', html)
        self.assertIn('href="/wissen/bleichfleck-uebermalen/"', html)

    def test_engel_snippet_mit_preis_nur_bei_verkauf(self):
        from shop1 import luviq_daten
        d = luviq_daten.ENGEL_STUECK
        engel = erzeuge_produkt(name='Engel-Shirt, mit Bleiche gemalt', slug=d['slug'], preis=Decimal('69.00'),
                                seo_titel=d['seo_titel'], seo_beschreibung=d['seo_beschreibung'],
                                lagerbestand=1, aktiv=True, vergeben=False)
        self.assertEqual(engel.meta_title, 'Engel-Shirt Nº 006: handbemaltes Unikat, 69 € | Luviq')
        self.assertIn('Größe M, 69 €', engel.meta_description)
        self.assertLessEqual(len(engel.meta_description), 160)
        with self.settings(VERKAUF_AKTIV=False):
            self.assertEqual(engel.meta_title, d['seo_titel'])
            self.assertEqual(engel.meta_description, d['seo_beschreibung'])
        engel.seo_titel = 'Luisas eigener Titel'
        self.assertEqual(engel.meta_title, 'Luisas eigener Titel')

    def test_cookie_hinweis_verdraengt_die_leisten(self):
        import pathlib
        css = (pathlib.Path(__file__).resolve().parents[1] / 'static' / 'shop1' / 'einwilligung.css').read_text(encoding='utf-8')
        self.assertIn('.lv-einwilligung:not([hidden])) .lv-leiste', css)
        self.assertIn('.lv-einwilligung:not([hidden])) .lv-kaufleiste', css)
