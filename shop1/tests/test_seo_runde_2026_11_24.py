"""SEO-Runde 24.11.2026 (Search-Console-Auswertung): keine Beschreibung mehr mitten im Satz.

Live standen bei allen fünf Archivstücken Beschreibungen wie „Schwarzer Hoodie mit schmalem – Nº 004 …“,
und die Stückbeschreibung in der llms.txt brach mitten im Satz ab. Dazu die Ratgeber-Snippets, die nach
den belegten Suchanfragen („mit Bleiche bemalen“, „was ist bleach“) umgestellt wurden."""
from django.test import override_settings

from ..models import META_BESCHREIBUNG_MAX
from ._basis import LuviqTestCase, erzeuge_produkt


class ArchivBeschreibungTest(LuviqTestCase):
    def test_vergebenes_stueck_hat_vollstaendigen_kern_statt_abgeschnittenem_satz(self):
        with override_settings(VERKAUF_AKTIV=True, ANFRAGESHOP=True):
            p = erzeuge_produkt(
                'Hoodie mit Rückenmotiv', vergeben=True,
                beschreibung='Schwarzer Hoodie mit schmalem Motiv auf dem Rücken, von Hand mit Bleiche gemalt.')
            text = p.meta_description
        self.assertTrue(text.startswith('Hoodie mit Rückenmotiv'), text)
        self.assertNotIn('schmalem –', text)
        self.assertLessEqual(len(text), META_BESCHREIBUNG_MAX)
        self.assertTrue(text.endswith('anfragen.'), text)


class LlmsStueckTextTest(LuviqTestCase):
    def test_lange_stueckbeschreibung_endet_am_satzende(self):
        satz = 'Ein Satz mit genug Wörtern, damit die Zeile lang wird und die Grenze erreicht. '
        p = erzeuge_produkt('Langes Stück', beschreibung=satz * 8)
        with override_settings(VERKAUF_AKTIV=True, ANFRAGESHOP=True):
            text = self.hole('/llms.txt').content.decode()
        zeile = [z for z in text.splitlines() if 'Langes Stück' in z][0]
        self.assertTrue(zeile.rstrip().endswith(('.', '…')), zeile[-60:])
        self.assertIsNotNone(p.pk)


class RatgeberSnippetTest(LuviqTestCase):
    def test_anleitung_und_bleach_painting_tragen_die_belegten_begriffe(self):
        html = self.hole('/wissen/bleach-painting-anleitung/').content.decode()
        self.assertIn('<title>T-Shirt mit Bleiche bemalen: Anleitung | Luviq</title>', html)
        html = self.hole('/wissen/bleach-painting/').content.decode()
        self.assertIn('Auf Deutsch Bleichmalerei', html.split('</head>')[0])
