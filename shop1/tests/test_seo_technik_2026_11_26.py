"""Paket 8 (26.11.2026): SEO-Technik nach dem Live-Befund (K3, W1, W7, W14, W15, W16).

Alles an der echten, gerenderten Seite gemessen, keine Zahl aus dem Befund übernommen."""
import html as htmllib
import re

from ._basis import LuviqTestCase, erzeuge_produkt
from .test_geo import schema_knoten

SEITEN = ['/', '/produkte/', '/motiv-anfragen/', '/ueber_uns/', '/liefergebiet/', '/kontakt/', '/impressum/',
          '/agb/', '/wissen/', '/wissen/bleach-painting/', '/gaestebuch/', '/datenschutz/']


def _feld(seite, muster):
    treffer = re.search(muster, seite, re.S)
    return htmllib.unescape(treffer.group(1)).strip() if treffer else None


def titel(seite):
    return _feld(seite, r'<title>(.*?)</title>')


def og_titel(seite):
    return _feld(seite, r'<meta property="og:title" content="(.*?)">')


def beschreibung(seite):
    return _feld(seite, r'<meta name="description" content="(.*?)">')


class SeoTechnikTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.enterContext(self.settings(ANFRAGESHOP=True, VERKAUF_AKTIV=False))
        self.stueck = erzeuge_produkt('Technikstueck', preis=69, lagerbestand=1)

    def seite(self, pfad):
        return self.hole(pfad).content.decode()

    def test_og_title_ist_der_title_auf_jeder_seite(self):
        for pfad in SEITEN + [self.stueck.get_absolute_url()]:
            with self.subTest(pfad=pfad):
                s = self.seite(pfad)
                self.assertTrue(titel(s))
                self.assertEqual(og_titel(s), titel(s))

    def test_titel_mit_bundesweitem_signal_und_hoechstens_60_zeichen(self):
        erwartet = {
            '/produkte/': 'Handbemalte Stücke aus Lübeck, bundesweit | Luviq',
            '/motiv-anfragen/': 'Shirt bemalen lassen: Motiv anfragen, bundesweit | Luviq',
            '/ueber_uns/': 'Luisa Brehler: Malerin aus Lübeck, bundesweit | Luviq',
            '/liefergebiet/': 'Versand in Deutschland, Übergabe in Lübeck | Luviq',
        }
        for pfad, soll in erwartet.items():
            with self.subTest(pfad=pfad):
                t = titel(self.seite(pfad))
                self.assertEqual(t, soll)
                self.assertLessEqual(len(t), 60)
                self.assertTrue(re.search(r'bundesweit|Deutschland', t))
        # /motiv-anfragen/ zielt auf das Suchwort der Seite (Platz 6 bei „shirt bemalen lassen“), die Startseite bleibt wie sie ist
        self.assertIn('bemalen lassen', titel(self.seite('/motiv-anfragen/')))
        self.assertEqual(titel(self.seite('/')), 'Bleach Art: Shirts & Hoodies bemalen lassen | Luviq Lübeck')

    def test_ratgeber_titel_bleiben_unveraendert(self):
        self.assertEqual(titel(self.seite('/wissen/bleach-painting/')),
                         'Was ist Bleach Painting? Ratgeber zur Bleichmalerei | Luviq')

    def test_beschreibungen_140_bis_160_zeichen_wo_sie_neu_gesetzt_wurden(self):
        for pfad in ('/', '/liefergebiet/', '/kontakt/'):
            with self.subTest(pfad=pfad):
                self.assertTrue(140 <= len(beschreibung(self.seite(pfad))) <= 160, pfad)
        self.assertIn('Aus Lübeck, Versand in ganz Deutschland', beschreibung(self.seite('/')))

    def test_alsfeld_ist_kein_einzugsgebiet_im_schema(self):
        for pfad in SEITEN:
            for knoten in schema_knoten(self.seite(pfad)):
                gebiet = knoten.get('areaServed')
                if gebiet is None:
                    continue
                orte = gebiet if isinstance(gebiet, list) else [gebiet]
                namen = [o.get('name') if isinstance(o, dict) else o for o in orte]
                with self.subTest(pfad=pfad, typ=knoten.get('@type')):
                    self.assertNotIn('Alsfeld', namen)
        service = next(k for k in schema_knoten(self.seite('/motiv-anfragen/')) if str(k.get('@id', '')).endswith('#motivanfrage'))
        self.assertEqual([(o['@type'], o['name']) for o in service['areaServed']],
                         [('City', 'Lübeck'), ('Country', 'Deutschland')])

    def test_impressum_hat_je_id_nur_einen_knoten_mit_der_anschrift_des_impressums(self):
        s = self.seite('/impressum/')
        knoten = schema_knoten(s)
        ids = [k['@id'] for k in knoten if '@id' in k]
        self.assertEqual(len(ids), len(set(ids)), f'doppelte @id: {sorted(ids)}')
        org = next(k for k in knoten if str(k.get('@id', '')).endswith('/#organization'))
        self.assertEqual(org['name'], 'Luviq')
        self.assertIn('Luviq Universe', org['alternateName'])
        adresse = org['address']
        # wortgleich zum sichtbaren Impressum
        sichtbar = re.sub(r'<script.*?</script>', '', s, flags=re.S)
        for wert in (adresse['streetAddress'], adresse['postalCode'], adresse['addressLocality']):
            self.assertIn(wert, sichtbar)

    def test_breadcrumb_heisst_stuecke_wie_die_navigation(self):
        s = self.seite('/produkte/')
        namen = [e['name'] for k in schema_knoten(s) if k.get('@type') == 'BreadcrumbList'
                 for e in k['itemListElement']]
        self.assertEqual(namen, ['Startseite', 'Stücke'])
        self.assertIn('<li aria-current="page">Stücke</li>', s)
        self.assertNotIn('<li aria-current="page">Shop</li>', s)
