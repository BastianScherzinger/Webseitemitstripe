"""Schub 30.10.2026 (Analyse-Umsetzung): Banner, Schema, Gästebuch, Entwurfsartikel."""

import json
import re

from django.test import override_settings

from ._basis import LuviqTestCase, erzeuge_produkt

ENTWUERFE = ('/wissen/bleach-painting/', '/wissen/bleichfleck-uebermalen/')


def _schema(html):
    knoten = []
    for roh in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        daten = json.loads(roh)
        knoten += daten.get('@graph', [daten])
    return knoten


class EinwilligungsbannerTest(LuviqTestCase):

    @override_settings(EINWILLIGUNG_DIENST='Google Analytics', EINWILLIGUNG_SKRIPT='https://example.invalid/x.js')
    def test_titel_ist_ein_absatz_und_der_wortlaut_bleibt(self):
        html = self.hole('/').content.decode()
        self.assertIn('<p class="lv-einwilligung-titel" id="lv-einwilligung-titel">Kurz mitzählen?</p>', html)
        self.assertNotIn('<h2 class="lv-einwilligung-titel"', html)
        self.assertIn('Nur für unsere Statistik: keine Werbung, wir verkaufen keine Daten.', html)
        # Beide Knöpfe gleich gestaltet (gleichwertiges Ablehnen).
        self.assertEqual(html.count('class="lv-einwilligung-knopf"'), 2)


class SchemaProfileTest(LuviqTestCase):

    def test_organization_und_person_tragen_ihre_profile(self):
        from .. import luviq_daten
        knoten = _schema(self.hole('/').content.decode())
        org = next(k for k in knoten if k.get('@id', '').endswith('/#organization'))
        person = next(k for k in knoten if k.get('@id', '').endswith('/#luisa') and k.get('sameAs'))
        self.assertIn('https://www.pinterest.com/luviqarchive/', org['sameAs'])
        self.assertIn('https://www.provenexpert.com/de-de/luviq/', org['sameAs'])
        self.assertEqual(person['sameAs'], list(luviq_daten.PROFILE_PERSON))
        self.assertNotIn('facebook', ' '.join(org['sameAs']))
        self.assertNotIn('linkedin', ' '.join(org['sameAs']))

    @override_settings(VERKAUF_AKTIV=True)
    def test_kein_offercatalog_mit_vintage_jacken(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('OfferCatalog', html)
        self.assertNotIn('Vintage-Jacken', html)


class KiBildEhrlichTest(LuviqTestCase):

    def test_hero_alt_nennt_das_ki_studiobild(self):
        from .. import luviq_daten
        self.assertTrue(luviq_daten.HERO_STUECK['alt'].startswith('Studiobild (KI) aus dem echten Foto'))
        self.assertIn('Studiobild (KI)', self.hole('/').content.decode())

    def test_hauptbild_des_engel_shirts_und_sitemap_nennen_es(self):
        from .. import luviq_daten
        from ..models import Produkt
        p = erzeuge_produkt('Engel-Shirt, mit Bleiche gemalt')
        p.bild_statisch = luviq_daten.ENGEL_STUECK['bild_statisch']
        p.bild_breite, p.bild_hoehe = 800, 999
        p.save()
        p = Produkt.objects.get(pk=p.pk)
        self.assertTrue(p.bild_ist_ki)
        self.assertTrue(p.hauptbild().alt.startswith('Studiobild (KI) aus dem echten Foto:'))
        sitemap = self.hole('/sitemap.xml').content.decode()
        self.assertIn('<image:title>Studiobild (KI) aus dem echten Foto: Engel-Shirt', sitemap)


class GaestebuchTest(LuviqTestCase):

    def test_noindex_follow_nicht_in_sitemap_und_llms_txt(self):
        html = self.hole('/gaestebuch/').content.decode()
        self.assertIn('<meta name="robots" content="noindex, follow">', html)
        self.assertNotIn('/gaestebuch/', self.hole('/sitemap.xml').content.decode())
        self.assertNotIn('/gaestebuch/', self.hole('/llms.txt').content.decode())


class OhnePrivatadresseImWissenTest(LuviqTestCase):

    def test_uebersicht_nennt_weder_strasse_noch_gmail(self):
        from ..luviq_daten import ANBIETERIN
        for verkauf in (False, True):
            with override_settings(VERKAUF_AKTIV=verkauf):
                html = self.hole('/wissen/').content.decode()
                html = html.split('<main', 1)[1].split('</main>', 1)[0]
                self.assertNotIn(ANBIETERIN['strasse'], html)
                self.assertNotIn('gmail.com', html)
                self.assertIn('stehen im Impressum', html)


class EntwurfsartikelTest(LuviqTestCase):
    """Bleach Painting und Bleichfleck: seit Runde 3 (30.10.2026) veröffentlicht.

    Vorher (Entwurf) prüfte ``test_noindex_und_nirgends_angeboten`` das Gegenteil; umgeschrieben,
    nicht gelöscht: jetzt indexierbar und in Übersicht, Sitemap, llms.txt und Feed angeboten."""

    def test_indexierbar_und_ueberall_angeboten(self):
        for pfad in ENTWUERFE:
            html = self.hole(pfad).content.decode()
            self.assertIn('<meta name="robots" content="index, follow">', html, pfad)
            for andere in ('/wissen/', '/sitemap.xml', '/llms.txt', '/feed/'):
                self.assertIn(pfad, self.hole(andere).content.decode(), f'{pfad} in {andere}')

    def test_artikelschema_mit_uhrzeit_und_zone(self):
        for pfad in ENTWUERFE:
            artikel = next(k for k in _schema(self.hole(pfad).content.decode()) if k.get('@type') == 'Article')
            for feld in ('datePublished', 'dateModified'):
                self.assertRegex(artikel[feld], r'^2026-10-30T\d{2}:\d{2}:\d{2}\+01:00$', f'{pfad} {feld}')
            self.assertTrue(artikel['author']['@id'].endswith('#luisa'))

    def test_antwortsatz_steht_in_den_ersten_40_woertern(self):
        for pfad, stichwort in zip(ENTWUERFE, ('Bleichmalerei', 'überdecken')):
            html = self.hole(pfad).content.decode()
            lead = re.search(r'<p class="lv-wissen-lead">(.*?)</p>', html, re.S).group(1)
            erste_40 = ' '.join(lead.split()[:40])
            self.assertIn(stichwort, erste_40, pfad)

    def test_ueberschriften_sind_fragen_und_beide_artikel_verlinken_sich(self):
        for pfad in ENTWUERFE:
            html = self.hole(pfad).content.decode()
            h2 = re.findall(r'<h2 class="lv-serif">(.*?)</h2>', html)
            self.assertGreaterEqual(len(h2), 5, pfad)
            for frage in h2:
                self.assertTrue(frage.endswith('?'), f'{pfad}: {frage}')
        self.assertIn('/wissen/bleach-painting/', self.hole('/wissen/bleichfleck-uebermalen/').content.decode())

    def test_keine_erfundenen_zahlen(self):
        """Außer dem belegten Erfahrungswert (2 bis 5 Tage), Pflege (30 °C) und dem Engel-Shirt
        (100 % Baumwolle) steht keine Zahl mit Einheit im Text."""
        erlaubt = {'2 bis 5 Tage', '30 °C', '100 %'}
        for pfad in ENTWUERFE:
            html = self.hole(pfad).content.decode()
            haupt = html.split('<main', 1)[-1]
            text = re.sub(r'<script.*?</script>', '', haupt, flags=re.S)
            text = re.sub(r'<[^>]+>', ' ', text)
            for treffer in re.findall(r'\d+(?: bis \d+)? (?:Tage|°C|%|€|Euro|Minuten|Stunden|Jahre|Monate|Wochen)', text):
                self.assertIn(treffer, erlaubt, f'{pfad}: {treffer}')
