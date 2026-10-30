"""Runde 3 (30.10.2026): Engel-Galerie mit echten Fotos, Versand im Preis, Rückgabe-Schema,
Foto von Luisa, Ratgeber veröffentlicht, Bild-Sitemap."""

import importlib
import io
import json
import re
from decimal import Decimal

from django.apps import apps
from django.core.management import call_command
from django.test import override_settings

from .. import luviq_daten
from ..models import Produkt, ProduktBild
from ._basis import LuviqTestCase, erzeuge_produkt

ENGEL = '/produkt/engel-shirt-handgebleicht/'


def _knoten(html):
    knoten = []
    for roh in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S):
        daten = json.loads(roh)
        knoten += daten.get('@graph', [daten])
    return knoten


class _MitEngel(LuviqTestCase):

    def setUp(self):
        call_command('luviq_engel_anlegen', stdout=io.StringIO())
        self.engel = Produkt.objects.get(slug='engel-shirt-handgebleicht')


class EngelGalerieTest(_MitEngel):

    def test_reihenfolge_ruecken_ki_ruecken_echt_vorne_echt_arbeitsplatz(self):
        galerie = self.engel.galerie()
        self.assertEqual(len(galerie), 4)
        self.assertIn('hero-engel-45', galerie[0].original)
        self.assertIn('engel-echt-45', galerie[1].original)
        self.assertIn('engel-vorne-echt-45', galerie[2].original)
        self.assertIn('engel-arbeitsplatz-45', galerie[3].original)
        self.assertEqual([b.ist_ki for b in galerie], [True, False, False, False])
        # Platz 2 bleibt für das KI-Studiobild der Vorderseite frei.
        self.assertEqual(list(self.engel.zusatzbilder.values_list('position', flat=True)), [1, 3, 4])

    def test_jedes_bild_sagt_ehrlich_was_es_ist(self):
        html = self.hole(ENGEL).content.decode()
        unterschriften = re.findall(r'<p class="lv-galerie-unterschrift">(.*?)</p>', html)
        self.assertEqual(unterschriften, ['Studiobild (KI) aus dem echten Foto', 'Echtes Foto: Rücken',
                                          'Echtes Foto: vorne, Luviq-Zeichen',
                                          'Echtes Foto: auf Luisas Arbeitstisch'])
        alts = re.findall(r'<li class="lv-galerie-bild"[^>]*>\s*<img[^>]*alt="([^"]*)"', html)
        self.assertTrue(alts[0].startswith('Studiobild (KI) aus dem echten Foto'))
        for alt in alts[1:]:
            self.assertTrue(alt.startswith('Echtes Foto'), alt)

    def test_nur_das_erste_bild_laedt_sofort_alle_mit_srcset(self):
        html = self.hole(ENGEL).content.decode()
        bilder = re.findall(r'<li class="lv-galerie-bild"[^>]*>\s*(<img[^>]*>)', html)
        self.assertEqual(len(bilder), 4)
        self.assertIn('loading="eager"', bilder[0])
        for img in bilder[1:]:
            self.assertIn('loading="lazy"', img)
        for img in bilder:
            self.assertIn('.webp 600w' if 'stuecke/' in img else '.webp 480w', img)

    def test_beschreibung_ohne_foto_folgt(self):
        self.assertNotIn('Foto folgt', self.engel.beschreibung)
        self.assertNotIn('Foto folgt', self.hole(ENGEL).content.decode())

    def test_ki_zusatzbild_wird_im_alt_text_genannt(self):
        ProduktBild.objects.create(produkt=self.engel, position=2, ist_ki=True,
                                   bild_statisch='shop1/images/stuecke/engel-echt-45-{w}.webp@600,900,960#960x1200',
                                   breite=960, hoehe=1200, alt='Vorderseite auf Holzbügel')
        galerie = self.engel.galerie()
        self.assertEqual(galerie[2].alt, 'Studiobild (KI) aus dem echten Foto: Vorderseite auf Holzbügel')
        self.assertEqual(galerie[2].unterschrift, 'Studiobild (KI) aus dem echten Foto')

    def test_alle_bilder_im_schema_und_in_der_sitemap(self):
        html = self.hole(ENGEL).content.decode()
        knoten = next(k for k in _knoten(html) if k.get('@type') in ('VisualArtwork', 'Product'))
        self.assertEqual(len(knoten['image']), 4)
        sitemap = self.hole('/sitemap.xml').content.decode()
        eintrag = sitemap.split('engel-shirt-handgebleicht/</loc>', 1)[1].split('</url>', 1)[0]
        self.assertEqual(eintrag.count('<image:image>'), 4)
        self.assertIn('engel-vorne-echt-45-960', eintrag)
        self.assertIn('<image:title>Echtes Foto: das Engel-Shirt', eintrag)


class OhneKiKeineUnterschriftTest(LuviqTestCase):

    def test_archivstueck_bleibt_wie_bisher(self):
        p = erzeuge_produkt('Stück ohne KI')
        html = self.hole(p.get_absolute_url()).content.decode()
        self.assertNotIn('lv-galerie-unterschrift', html)


class MigrationNachtragTest(LuviqTestCase):
    """0031 trägt die neuen Fotos in eine bestehende Datenbank nach – genau einmal, ohne Doppel."""

    def test_traegt_nach_und_ersetzt_nur_den_alten_text(self):
        modul = importlib.import_module('shop1.migrations.0031_engel_galerie_runde3')
        p = Produkt.objects.create(name='Engel-Shirt, mit Bleiche gemalt', slug='engel-shirt-handgebleicht',
                                   preis=Decimal('69.00'), beschreibung=modul.ALT_TEXT, lagerbestand=1,
                                   bild_statisch=luviq_daten.ENGEL_STUECK['bild_statisch'])
        ProduktBild.objects.create(produkt=p, position=1, bild_statisch=modul.RUECKEN, breite=960, hoehe=1200)
        modul.vorwaerts(apps, None)
        modul.vorwaerts(apps, None)  # zweiter Lauf: nichts doppelt
        p.refresh_from_db()
        self.assertEqual(p.beschreibung, modul.NEU_TEXT)
        self.assertEqual(p.zusatzbilder.count(), 3)
        self.assertEqual(p.zusatzbilder.get(position=1).unterschrift, 'Echtes Foto: Rücken')

    def test_von_luisa_geaenderter_text_bleibt(self):
        modul = importlib.import_module('shop1.migrations.0031_engel_galerie_runde3')
        p = Produkt.objects.create(name='Engel', slug='engel-shirt-handgebleicht', preis=Decimal('69.00'),
                                   beschreibung='Luisas eigener Text', lagerbestand=1)
        modul.vorwaerts(apps, None)
        p.refresh_from_db()
        self.assertEqual(p.beschreibung, 'Luisas eigener Text')


class VersandUndRueckgabeTest(_MitEngel):

    def test_versand_ist_im_preis(self):
        self.assertEqual(luviq_daten.VERSAND['kosten'], 0)

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_steht_inkl_versand_und_der_umtauschsatz(self):
        html = self.hole(ENGEL).content.decode()
        self.assertIn('69,00 € <span class="lv-stueck-preis-zusatz">inkl. Versand innerhalb Deutschlands</span>', html)
        self.assertIn(luviq_daten.UMTAUSCH_SATZ, html)
        liefer = self.hole('/liefergebiet/').content.decode()
        self.assertIn('<h3>Was kostet der Versand?</h3>', liefer)
        self.assertIn('Der Versand innerhalb Deutschlands ist im Preis enthalten.', liefer)
        self.assertIn('im Preis enthalten', self.hole('/kontakt/').content.decode())
        self.assertIn('inkl. Versand', self.hole('/produkte/').content.decode())

    def test_ohne_verkauf_kein_preis_und_kein_versandsatz(self):
        html = self.hole(ENGEL).content.decode()
        self.assertNotIn('inkl. Versand', html)
        self.assertNotIn('Was kostet der Versand?', self.hole('/liefergebiet/').content.decode())

    @override_settings(VERKAUF_AKTIV=True)
    def test_nie_keine_rueckgabe_ohne_widerrufsrecht(self):
        """„Kein Umtausch“ darf nie ohne den Hinweis auf das gesetzliche Widerrufsrecht stehen,
        und „keine Rückgabe“ steht nirgends (§ 312g BGB: fertige Unikate sind widerrufbar)."""
        for pfad in (ENGEL, '/liefergebiet/', '/produkte/', '/kontakt/', '/'):
            with self.subTest(pfad=pfad):
                text = self.hole(pfad).content.decode()
                self.assertNotRegex(text, r'(?i)keine Rückgabe|kein Rückgaberecht')
                if 'keinen Umtausch' in text:
                    self.assertIn('gesetzliches Widerrufsrecht (14 Tage) bleibt davon unberührt', text)

    def test_auftragsarbeit_ohne_widerrufsrecht_bei_motiv_anfragen(self):
        html = self.hole('/motiv-anfragen/').content.decode()
        self.assertIn('§ 312g Abs. 2 Nr. 1 BGB', html)
        self.assertIn('Kann ich ein Stück nach meinem Motiv zurückgeben?', html)

    @override_settings(VERKAUF_AKTIV=True)
    def test_schema_versand_und_rueckgabe_mit_verkauf(self):
        knoten = _knoten(self.hole(ENGEL).content.decode())
        org = next(k for k in knoten if k.get('@id', '').endswith('/#organization') and k.get('name'))
        regel = org['hasMerchantReturnPolicy']
        self.assertEqual(regel['@type'], 'MerchantReturnPolicy')
        self.assertTrue(regel['@id'].endswith('/#rueckgabe'))
        self.assertEqual(regel['returnPolicyCategory'], 'https://schema.org/MerchantReturnFiniteReturnWindow')
        self.assertEqual(regel['merchantReturnDays'], 14)
        self.assertEqual(regel['returnMethod'], 'https://schema.org/ReturnByMail')
        self.assertEqual(regel['applicableCountry'], 'DE')
        self.assertNotIn('returnFees', regel)  # nicht belegt (Widerrufsbelehrung fehlt)
        produkt = next(k for k in knoten if k.get('@type') == 'Product')
        angebot = produkt['offers']
        self.assertEqual(angebot['hasMerchantReturnPolicy'], {'@id': regel['@id']})
        versand = angebot['shippingDetails']
        self.assertEqual(versand['shippingRate'], {'@type': 'MonetaryAmount', 'value': '0.00', 'currency': 'EUR'})
        self.assertEqual(versand['shippingDestination']['addressCountry'], 'DE')
        zeit = versand['deliveryTime']['handlingTime']
        self.assertEqual((zeit['minValue'], zeit['maxValue'], zeit['unitCode']), (1, 2, 'DAY'))
        # Seit der Gegenprüfung (M1, 30.10.2026) gilt eine verbindliche Lieferfrist von 5 Werktagen:
        # Laufzeit = Frist minus Bearbeitung (höchstens 3 Tage).
        self.assertEqual(versand['deliveryTime']['transitTime']['maxValue'], 3)
        # Produktübersicht: dieselben Angaben je Offer.
        uebersicht = _knoten(self.hole('/produkte/').content.decode())
        for k in uebersicht:
            if k.get('@type') == 'Product':
                self.assertIn('shippingDetails', k['offers'])

    def test_ohne_verkauf_kein_haendlerschema(self):
        for pfad in (ENGEL, '/', '/produkte/'):
            html = self.hole(pfad).content.decode()
            self.assertNotIn('MerchantReturnPolicy', html)
            self.assertNotIn('OfferShippingDetails', html)


class LuisaFotoTest(LuviqTestCase):

    def test_kontakt_und_luisa_seite_zeigen_das_brustbild(self):
        for pfad in ('/kontakt/', '/ueber_uns/'):
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                self.assertRegex(html, r'<img src="[^"]*luisa-brustbild-420[^"]*" srcset="[^"]*280w[^"]*570w"')
                self.assertIn('alt="Luisa Brehler, die Malerin hinter Luviq"', html)

    def test_person_schema_hat_ein_bild(self):
        knoten = _knoten(self.hole('/').content.decode())
        person = next(k for k in knoten if k.get('@id', '').endswith('/#luisa') and k.get('sameAs'))
        self.assertIn('luisa-brustbild-570', person['image'])

    def test_bild_sitemap_kennt_das_foto(self):
        sitemap = self.hole('/sitemap.xml').content.decode()
        for seite in ('/ueber_uns/', '/kontakt/'):
            eintrag = sitemap.split(f'{seite}</loc>', 1)[1].split('</url>', 1)[0]
            self.assertIn('luisa-brustbild-570', eintrag)


class RatgeberRunde3Test(LuviqTestCase):

    def test_bleach_artikel_mit_echtem_foto_im_schema_und_in_der_sitemap(self):
        html = self.hole('/wissen/bleach-painting/').content.decode()
        self.assertIn('<figure class="lv-wissen-bild">', html)
        artikel = next(k for k in _knoten(html) if k.get('@type') == 'Article')
        self.assertIn('engel-arbeitsplatz-45', artikel['image'])
        sitemap = self.hole('/sitemap.xml').content.decode()
        eintrag = sitemap.split('/wissen/bleach-painting/</loc>', 1)[1].split('</url>', 1)[0]
        self.assertIn('engel-arbeitsplatz-45-960', eintrag)

    def test_sicherheit_nie_essig_zum_neutralisieren(self):
        html = self.hole('/wissen/bleach-painting/').content.decode()
        self.assertIn('Muss man Bleiche nach dem Malen neutralisieren?', html)
        self.assertIn('aber nie Essig', html)
        self.assertIn('Chlorgas', html)
        self.assertIn('Natriumthiosulfat', html)

    def test_interne_links(self):
        self.assertIn('href="/wissen/bleach-painting/"', self.hole('/wissen/pflege-handbemalte-kleidung/').content.decode())
        self.assertIn('href="/wissen/bleach-painting/"', self.hole('/ueber_uns/').content.decode())
        fleck = self.hole('/wissen/bleichfleck-uebermalen/').content.decode()
        self.assertIn('href="/wissen/pflege-handbemalte-kleidung/"', fleck)
        self.assertIn('href="/motiv-anfragen/"', fleck)

    def test_stueckseite_verlinkt_den_ratgeber(self):
        call_command('luviq_engel_anlegen', stdout=io.StringIO())
        html = self.hole(ENGEL).content.decode()
        self.assertIn('href="/wissen/bleach-painting/">Was ist Bleach Painting?</a>', html)
        self.assertIn(f'href="{ENGEL}">Engel-Shirt</a>', self.hole('/wissen/bleach-painting/').content.decode())
