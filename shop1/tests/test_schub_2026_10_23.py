"""Schub 23.10.2026: Archivkarte ohne Foto, Lübeck als Sitz, Schema und FAQ."""

from ._basis import LuviqTestCase, erzeuge_produkt


class ArchivkarteOhneFotoTest(LuviqTestCase):

    def test_stueck_ohne_foto_zeigt_hinweis_statt_leerer_kachel(self):
        erzeuge_produkt(name='Stück ohne Foto')
        html = self.hole('/').content.decode()
        self.assertIn('class="lv-ohne-bild">Foto folgt</span>', html)
        self.assertIn('Stück ohne Foto', html)

    def test_hinweis_steht_nur_ohne_foto(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('lv-ohne-bild">', html)


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
