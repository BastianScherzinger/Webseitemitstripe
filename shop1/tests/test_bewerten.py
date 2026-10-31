"""Bewertungsbitte (30.10.2026): ``/bewerten/`` und ``/bewerten/alle/``.

Ziel des QR-Codes auf dem Bild für WhatsApp. Nur geprüfte Formularadressen, Google zuerst,
noindex, nicht in Sitemap und llms.txt, keine Sterne und keine Gegenleistung.
"""

from django.conf import settings

from ._basis import LuviqTestCase
from .. import luviq_daten


class BewertenTest(LuviqTestCase):

    def test_kurzadresse_leitet_zu_google(self):
        antwort = self.hole('/bewerten/')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], 'https://g.page/r/CTDc6lSl1eXAECE/review')

    def test_alle_portale_als_knopf_google_zuerst(self):
        html = self.hole('/bewerten/alle/').content.decode()
        google = html.index('href="https://g.page/r/CTDc6lSl1eXAECE/review"')
        proven = html.index('href="https://www.provenexpert.com/luviq/ffk7/"')
        self.assertLess(google, proven)
        self.assertIn('href="/gaestebuch/"', html)
        self.assertEqual(len(luviq_daten.BEWERTUNGSPORTALE), 2)

    def test_noindex_und_nicht_in_sitemap_oder_llms(self):
        html = self.hole('/bewerten/alle/').content.decode()
        self.assertIn('<meta name="robots" content="noindex, follow">', html)
        for adresse in ('/sitemap.xml', '/llms.txt'):
            self.assertNotIn('/bewerten/', self.hole(adresse).content.decode(), adresse)

    def test_keine_sterne_und_keine_gegenleistung(self):
        html = self.hole('/bewerten/alle/').content.decode()
        self.assertNotIn('★', html)
        for wort in ('Gutschein', 'Rabatt', 'Gewinnspiel', 'aggregateRating'):
            self.assertNotIn(wort, html)
        self.assertIn('es gibt nichts dafür', html)

    def test_vorgabe_des_google_knopfs_ist_das_bewertungsformular(self):
        self.assertEqual(settings.GOOGLE_REVIEW_URL, luviq_daten.GOOGLE_BEWERTEN)
