"""P4 (29.10.2026): Stücke-Seiten, Band „Verkauft“, wischbare Galerie, Engel-Shirt Nº 006.

Prüft: das Band „Verkauft“ (Text im DOM) auf Karte, Startseite und Stückseite nur bei vergebenen Stücken;
die Galerie (mehrere Bilder, Zähler, Skript mit Nonce, ohne Zusatzbild keine Steuerung); das Anlegen des
Engel-Shirts per Management-Befehl (idempotent, überschreibt nichts); die Product-Daten mit und ohne Verkauf.
"""
import json
import re
from decimal import Decimal

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from .. import luviq_daten, produktbilder
from ..models import Produkt, ProduktBild
from ._basis import LuviqTestCase, erzeuge_produkt

STATISCH = 'shop1/images/luviq/hero-engel-45-{w}.webp@480,640,800#800x999'


def _ld(antwort):
    """Alle JSON-LD-Knoten der Seite als Liste."""
    html = antwort.content.decode()
    roh = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    return [json.loads(r) for r in roh]


class VerkauftBandTest(LuviqTestCase):
    def setUp(self):
        self.alt = erzeuge_produkt('Custom Hoodie', vergeben=True, bild_statisch=STATISCH)
        self.neu = erzeuge_produkt('Neues Stück', bild_statisch=STATISCH)

    def test_band_steht_nur_bei_vergebenem_stueck(self):
        seite = self.hole(self.alt.get_absolute_url()).content.decode()
        self.assertIn('lv-verkauft', seite)
        self.assertIn(f'<span>{luviq_daten.REFERENZ_WORT}</span>', seite)
        self.assertNotIn('Verkauft', seite)
        self.assertNotIn('lv-verkauft', self.hole(self.neu.get_absolute_url()).content.decode())

    def test_band_auf_uebersicht_und_startseite(self):
        for pfad in ('/produkte/', '/'):
            html = self.hole(pfad).content.decode()
            self.assertEqual(html.count('class="lv-verkauft"'), 1, pfad)
            self.assertIn('Vergeben', html)

    def test_verfuegbares_stueck_steht_vor_dem_archiv(self):
        html = self.hole('/').content.decode()
        self.assertIn('id="stuecke"', html)
        self.assertLess(html.index('id="stuecke"'), html.index('id="archiv"'))
        self.assertNotIn('Neues Stück</a></h3>', html.split('id="archiv"', 1)[1])

    def test_ausverkauftes_stueck_zaehlt_als_verkauft(self):
        self.neu.lagerbestand = 0
        self.neu.save()
        seite = self.hole(self.neu.get_absolute_url()).content.decode()
        self.assertIn(f'<span>{luviq_daten.VERKAUFT_WORT}</span>', seite)

    def test_nirgends_verkauft_fuer_archivstuecke(self):
        for pfad in ('/', '/produkte/'):
            html = self.hole(pfad).content.decode()
            self.assertNotIn('>Verkauft<', html, pfad)
            self.assertNotIn('schon verkauft', html, pfad)

    def test_brotkrume_stuecke_fuer_verfuegbare_archiv_fuer_vergebene(self):
        neu = self.hole(self.neu.get_absolute_url()).content.decode()
        self.assertIn('>Stücke</a></li>', neu)
        self.assertIn('"name": "Stücke"', neu)
        alt = self.hole(self.alt.get_absolute_url()).content.decode()
        self.assertIn('>Archiv</a></li>', alt)

    def test_kein_preis_ohne_verkauf(self):
        html = self.hole('/produkte/').content.decode()
        self.assertNotIn('49,90', html)
        self.assertNotIn('49.90', html)

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_zeigt_nur_das_verfuegbare_den_preis(self):
        self.assertContains(self.hole(self.neu.get_absolute_url()), '49,90')
        seite = self.hole(self.alt.get_absolute_url()).content.decode()
        self.assertNotIn('In den Warenkorb', seite)
        self.assertNotIn('Anmelden und kaufen', seite)


class GalerieTest(LuviqTestCase):
    def test_zwei_bilder_geben_zaehler_punkte_und_skript(self):
        p = erzeuge_produkt('Galeriestück', bild_statisch=STATISCH)
        ProduktBild.objects.create(produkt=p, position=1, alt='Zweites Foto',
                                   bild_statisch='shop1/images/luviq/hero-engel-45-{w}.webp@480,640,800#800x999')
        antwort = self.hole(p.get_absolute_url())
        html = antwort.content.decode()
        self.assertEqual(html.count('class="lv-galerie-bild"'), 2)
        self.assertIn('data-galerie-zaehler', html)
        self.assertIn('<span data-galerie-nummer>1</span> / 2', html)
        self.assertEqual(html.count('data-galerie-nr='), 2)
        self.assertIn('alt="Zweites Foto"', html)
        # nur das erste Bild lädt sofort und mit Vorrang
        self.assertEqual(html.count('fetchpriority="high"'), 2)  # Preload + erstes Bild
        # Skript nur mit Nonce, keine Handler-Attribute
        skript = re.search(r'<script nonce="([^"]+)">\s*\(function \(\) \{\s*\'use strict\';\s*// Galerie', html)
        self.assertIsNotNone(skript)
        self.assertNotIn(' onclick=', html)

    def test_ein_bild_gibt_keine_steuerung(self):
        p = erzeuge_produkt('Einzelbild', bild_statisch=STATISCH)
        html = self.hole(p.get_absolute_url()).content.decode()
        self.assertIn('data-galerie', html)
        self.assertNotIn('data-galerie-zaehler', html)
        self.assertNotIn('// Galerie', html)

    def test_stueck_ohne_bild_bleibt_ohne_fehler(self):
        p = erzeuge_produkt('Ohne Bild')
        self.assertEqual(self.hole(p.get_absolute_url()).status_code, 200)
        self.assertEqual(self.hole('/produkte/').status_code, 200)

    def test_galerie_reihenfolge_haupt_dann_zusatz(self):
        p = erzeuge_produkt('Reihe', bild_statisch=STATISCH)
        ProduktBild.objects.create(produkt=p, position=2, alt='B', bild_statisch=STATISCH)
        ProduktBild.objects.create(produkt=p, position=1, alt='A', bild_statisch=STATISCH)
        self.assertEqual([b.alt for b in p.galerie()][1:], ['A', 'B'])


class BildSpezifikationTest(SimpleTestCase):
    def test_statisches_bild_wird_gelesen(self):
        self.assertEqual(produktbilder.statisches_bild(STATISCH),
                         ('shop1/images/luviq/hero-engel-45-{w}.webp', [480, 640, 800], (800, 999)))

    def test_kaputte_angaben_ergeben_none(self):
        for spec in ('', 'x.webp', 'a-{w}.webp@480', 'a-{w}.webp@#10x10', 'a-{w}.webp@480#axb'):
            self.assertIsNone(produktbilder.statisches_bild(spec), spec)


class EngelAnlegenTest(LuviqTestCase):
    def anlegen(self):
        call_command('luviq_engel_anlegen', stdout=_Stumm())

    def test_legt_das_stueck_einmal_an(self):
        self.anlegen()
        self.anlegen()
        d = luviq_daten.ENGEL_STUECK
        stuecke = Produkt.objects.filter(slug=d['slug'])
        self.assertEqual(stuecke.count(), 1)
        p = stuecke.get()
        self.assertEqual(p.preis, Decimal('69.00'))
        self.assertEqual((p.nummer, p.masse, p.material), (6, 'Größe M', '100 % Baumwolle'))
        self.assertTrue(p.aktiv and not p.vergeben and p.kaufbar)
        # Runde 3: Rücken echt, Vorderseite echt, Arbeitstisch (Platz 2 für das KI-Bild vorne frei).
        self.assertEqual(p.zusatzbilder.count(), 3)
        self.assertEqual(len(p.galerie()), 4)

    def test_ueberschreibt_nichts(self):
        self.anlegen()
        p = Produkt.objects.get(slug=luviq_daten.ENGEL_STUECK['slug'])
        p.name, p.preis, p.aktiv = 'Von Luisa geändert', Decimal('75.00'), False
        p.save()
        self.anlegen()
        p.refresh_from_db()
        self.assertEqual((p.name, p.preis, p.aktiv), ('Von Luisa geändert', Decimal('75.00'), False))
        self.assertEqual(Produkt.objects.count(), 1)

    def test_belegte_nummer_6_wird_nicht_doppelt_vergeben(self):
        erzeuge_produkt('Anderes', nummer=6)
        self.anlegen()
        engel = Produkt.objects.get(slug=luviq_daten.ENGEL_STUECK['slug'])
        self.assertNotEqual(engel.nummer, 6)

    def test_engel_ist_neu(self):
        """Bastian 30.10.2026: das Engel-Shirt ist neu – „Neu“, nie „Gebraucht“."""
        self.anlegen()
        engel = Produkt.objects.get(slug='engel-shirt-handgebleicht')
        self.assertEqual(engel.zustand, 'Neu')
        self.assertTrue(engel.ist_neu)
        html = self.hole('/produkt/engel-shirt-handgebleicht/').content.decode()
        self.assertNotIn('Gebraucht', html)
        self.assertIn('<dt>Stück</dt><dd>Neu</dd>', html)

    def test_leerer_zustand_wird_nachgetragen(self):
        self.anlegen()
        Produkt.objects.filter(slug='engel-shirt-handgebleicht').update(zustand='')
        self.anlegen()
        self.assertEqual(Produkt.objects.get(slug='engel-shirt-handgebleicht').zustand, 'Neu')

    def test_altstueck_behaelt_den_zustand(self):
        p = erzeuge_produkt('Alt')
        self.assertIn('Gebraucht (Second Hand)', self.hole(p.get_absolute_url()).content.decode())

    def test_seite_ohne_verkauf_ohne_preis_mit_visualartwork(self):
        self.anlegen()
        antwort = self.hole('/produkt/engel-shirt-handgebleicht/')
        html = antwort.content.decode()
        self.assertEqual(antwort.status_code, 200)
        self.assertNotIn('69,00', html)
        self.assertIn('Größe M', html)
        self.assertIn('100 % Baumwolle', html)
        self.assertIn('nichts ist aufgedruckt', html)
        knoten = [k for k in _ld(antwort) if k.get('@type') in ('VisualArtwork', 'Product')]
        self.assertEqual([k['@type'] for k in knoten], ['VisualArtwork'])
        self.assertNotIn('offers', knoten[0])
        self.assertEqual(len(knoten[0]['image']), 4)  # Runde 3: alle Galeriebilder
        # keine erfundenen Angaben
        self.assertNotIn(' cm', luviq_daten.ENGEL_STUECK['masse'])

    @override_settings(VERKAUF_AKTIV=True)
    def test_seite_mit_verkauf_zeigt_preis_und_product_offer(self):
        self.anlegen()
        antwort = self.hole('/produkt/engel-shirt-handgebleicht/')
        self.assertContains(antwort, '69,00')
        produkt = [k for k in _ld(antwort) if k.get('@type') == 'Product'][0]
        self.assertEqual(produkt['offers']['price'], '69.00')
        self.assertEqual(produkt['offers']['priceCurrency'], 'EUR')
        self.assertEqual(produkt['offers']['availability'], 'https://schema.org/InStock')

    def test_startseite_zeigt_engel_vor_dem_archiv_mit_ansehen_link(self):
        self.anlegen()
        html = self.hole('/').content.decode()
        abschnitt = html.split('id="stuecke"', 1)[1].split('</section>', 1)[0]
        self.assertIn('Engel-Shirt, mit Bleiche gemalt', abschnitt)
        self.assertIn('/produkt/engel-shirt-handgebleicht/', abschnitt)
        self.assertIn('Größe M', abschnitt)

    def test_sitemap_nennt_das_statische_bild(self):
        self.anlegen()
        xml = self.hole('/sitemap.xml').content.decode()
        self.assertIn('/produkt/engel-shirt-handgebleicht/', xml)
        self.assertIn('hero-engel-45-800', xml)


class _Stumm:
    def write(self, *a, **k):
        pass

    def flush(self):
        pass
