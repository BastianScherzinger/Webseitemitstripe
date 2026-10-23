"""Schub 23.10.2026: Archivkarte ohne Foto, Lübeck als Sitz, Schema und FAQ."""

from ._basis import LuviqTestCase, erzeuge_produkt


class ArchivkarteOhneFotoTest(LuviqTestCase):

    def test_stueck_ohne_foto_zeigt_hinweis_statt_leerer_kachel(self):
        erzeuge_produkt(name='Stück ohne Foto')
        html = self.hole('/').content.decode()
        self.assertIn('<figure data-ohne-foto>', html)
        self.assertIn('Stück ohne Foto', html)

    def test_hinweis_steht_nur_ohne_foto(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('data-ohne-foto', html)


class SitzUndProfileTest(LuviqTestCase):

    def test_stueckbeschreibung_nennt_luebeck_nicht_alsfeld_als_sitz(self):
        from ..models import (META_BESCHREIBUNG_ZUSATZ_OHNE_VERKAUF,
                              META_BESCHREIBUNG_ZUSATZ_OHNE_VERKAUF_OHNE_ANFRAGE)
        for text in (META_BESCHREIBUNG_ZUSATZ_OHNE_VERKAUF,
                     META_BESCHREIBUNG_ZUSATZ_OHNE_VERKAUF_OHNE_ANFRAGE):
            self.assertIn('Luviq Universe in Lübeck', text)
            self.assertNotIn('Alsfeld', text)

    def test_sameas_kommt_aus_der_einen_quelle(self):
        import json
        import re
        from .. import luviq_daten
        html = self.hole('/').content.decode()
        org = None
        for roh in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
            for knoten in json.loads(roh).get('@graph', []):
                if knoten.get('@id', '').endswith('/#organization'):
                    org = knoten
        self.assertIsNotNone(org)
        self.assertEqual(org['sameAs'], list(luviq_daten.PROFILE))
        self.assertEqual(org['address']['addressLocality'], 'Lübeck')


class MotivFaqTest(LuviqTestCase):

    def test_faq_steht_sichtbar_ohne_schema_vor_dem_verkauf(self):
        from .. import luviq_daten
        html = self.hole('/motiv-anfragen/').content.decode()
        for frage, antwort in luviq_daten.FAQ_MOTIV:
            self.assertIn(f'<h2 class="lv-serif">{frage}</h2>', html)
            self.assertIn(antwort, html)
        self.assertNotIn('"FAQPage"', html)

    def test_faq_schema_erst_mit_verkauf_und_wortgleich(self):
        import json
        import re
        from django.test import override_settings
        from .. import luviq_daten
        with override_settings(VERKAUF_AKTIV=True):
            html = self.hole('/motiv-anfragen/').content.decode()
        faq = None
        for roh in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
            daten = json.loads(roh)
            if daten.get('@type') == 'FAQPage':
                faq = daten
        self.assertIsNotNone(faq)
        paare = [(q['name'], q['acceptedAnswer']['text']) for q in faq['mainEntity']]
        self.assertEqual(paare, list(luviq_daten.FAQ_MOTIV))

    def test_faq_texte_sind_json_sicher_und_ohne_preis_oder_zusage(self):
        from .. import luviq_daten
        for frage, antwort in luviq_daten.FAQ_MOTIV:
            for text in (frage, antwort):
                self.assertNotIn('"', text)
                self.assertNotIn('\\', text)
                self.assertNotIn('€', text)


class LlmsMotivFragenTest(LuviqTestCase):

    def test_llms_nennt_die_motivfragen_mit_und_ohne_verkauf(self):
        from django.test import override_settings
        for verkauf in (False, True):
            with self.subTest(verkauf=verkauf), override_settings(VERKAUF_AKTIV=verkauf):
                text = self.hole('/llms.txt').content.decode()
                self.assertIn('### Ist eine Motivanfrage schon eine Bestellung?', text)
                self.assertIn('### Wie pflege ich ein handbemaltes Stueck?', text)
                self.assertIn('30 Grad C', text)
                self.assertTrue(text.isascii())


class FotoHinweisStilTest(LuviqTestCase):

    def test_stylesheet_hat_die_regel_fuer_stuecke_ohne_foto(self):
        from django.conf import settings
        css = (settings.BASE_DIR / 'shop1' / 'static' / 'shop1' / 'luviq.css').read_text(encoding='utf-8')
        self.assertIn('figure[data-ohne-foto]::after{content:"Foto folgt"', css)
