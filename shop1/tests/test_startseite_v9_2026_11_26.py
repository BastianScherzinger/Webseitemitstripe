"""Startseite v9 „Bleach Art“ (26.11.2026, Bastian: „Passt, bau das genau so ein“).

Ersetzt die Prüfungen der alten Startseite (Hero Engel-Shirt, Stückband, Warteliste), die mit dem Umbau entfielen.
Prüfbefehl: python manage.py test shop1.tests.test_startseite_v9_2026_11_26
"""

import re
from html.parser import HTMLParser

from shop1 import luviq_daten
from ._basis import LuviqTestCase
from .test_geo import schema_knoten, sichtbarer_text


class StartseiteV9Test(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.html = self.hole('/').content.decode()
        self.text = sichtbarer_text(self.html)

    def test_titel_beschreibung_und_genau_eine_h1(self):
        self.assertIn('<title>Bleach Art: Shirts &amp; Hoodies bemalen lassen | Luviq Lübeck</title>', self.html)
        self.assertIn(f'<meta name="description" content="{luviq_daten.START_BESCHREIBUNG}">', self.html)
        self.assertEqual(len(re.findall(r'<h1[ >]', self.html)), 1)
        self.assertEqual(self.html.count('<title>'), 1)

    def test_kein_preis_und_keine_gedankenstriche(self):
        self.assertNotIn('€', self.text)
        self.assertNotRegex(self.text, r'\d\s*(Euro|EUR)\b')
        self.assertNotIn('–', self.text)
        self.assertNotIn('—', self.text)

    def test_alle_bilder_laden_sofort_und_nur_das_erste_hat_vorrang(self):
        self.assertNotIn('loading="lazy"', self.html)
        bilder = re.findall(r'<img [^>]*>', self.html)
        self.assertGreaterEqual(len(bilder), 14)
        for bild in bilder:
            self.assertIn('width="', bild)
            self.assertIn('height="', bild)
            self.assertIn('loading="eager"', bild)
        self.assertEqual(sum('fetchpriority="high"' in b for b in bilder), 1)
        self.assertIn('fetchpriority="high"', bilder[0])
        self.assertRegex(self.html, r'<link rel="preload" as="image" type="image/webp" fetchpriority="high" href="[^"]*ganz-vorne-luviq[^"]*"')

    def test_eigener_kopf_fuss_und_leiste_ohne_den_alten_shopkopf(self):
        self.assertIn('<header class="kopf">', self.html)
        self.assertNotIn('lv-kopf', self.html)
        self.assertNotIn('lv-fuss"', self.html)
        self.assertIn('<nav class="leiste"', self.html)
        self.assertRegex(self.html, r'startseite(\.[0-9a-f]+)?\.css')
        self.assertNotRegex(self.html, r'luviq(\.[0-9a-f]+)?\.css')

    def test_anfragewege_whatsapp_und_mail(self):
        self.assertIn(f'href="{luviq_daten.START_WHATSAPP}"', self.html)
        self.assertIn('href="mailto:brehlerluisa@gmail.com?subject=Motiv%20anfragen&amp;body=', self.html)
        self.assertIn('0176 2490 8402', self.text)
        self.assertNotRegex(self.html.split('<body', 1)[1].split('<script', 1)[0], r'<form[ >]')

    def test_fuss_verlinkt_die_unterseiten(self):
        fuss = self.html[self.html.index('<footer class="fuss">'):]
        for adresse in ('/produkte/', '/motiv-anfragen/', '/wissen/', '/kontakt/', '/gaestebuch/', '/liefergebiet/',
                        '/impressum/', '/datenschutz/', '#arbeiten', '#fragen'):
            with self.subTest(adresse=adresse):
                self.assertIn(f'href="{adresse}', fuss)

    def test_faq_schema_ist_deckungsgleich_mit_den_acht_fragen(self):
        self.assertEqual(len(luviq_daten.START_FRAGEN), 8)
        faq = [k for k in schema_knoten(self.html) if k.get('@type') == 'FAQPage']
        self.assertEqual(len(faq), 1)
        fragen = [(f['name'], f['acceptedAnswer']['text']) for f in faq[0]['mainEntity']]
        self.assertEqual(fragen, list(luviq_daten.START_FRAGEN))
        for frage, antwort in fragen:
            self.assertIn(' '.join(frage.split()), self.text)
            self.assertIn(' '.join(antwort.split()), self.text)

    def test_schema_ohne_preis_mit_service_telefon_und_ohne_doppelte_knoten(self):
        knoten = schema_knoten(self.html)
        dienste = [k for k in knoten if k.get('@type') == 'Service']
        self.assertEqual(len(dienste), 1)
        self.assertEqual(dienste[0]['name'], 'Bleach Art auf Kleidung nach Wunschmotiv')
        self.assertNotIn('offers', dienste[0])
        self.assertEqual(len([k for k in knoten if k.get('@id', '').endswith('/#organization')]), 1)
        orga = next(k for k in knoten if k.get('@id', '').endswith('/#organization'))
        self.assertEqual(orga['contactPoint']['telephone'], '+49 176 24908402')
        person = next(k for k in knoten if k.get('@id', '').endswith('/#luisa'))
        self.assertEqual(person['jobTitle'], 'Bleach-Art-Malerin')
        self.assertNotIn('Offer', self.html.split('</head>')[0].replace('"@type": "OfferShippingDetails"', ''))
        self.assertNotRegex(self.html.split('</head>')[0], r'"(price|lowPrice|highPrice)"')

    def test_die_texte_stehen_wortgleich_auf_der_seite(self):
        for _, _, _, fett, rest in luviq_daten.START_SLIDES:
            self.assertIn(rest, self.text)
        for titel, text in luviq_daten.START_SCHRITTE:
            self.assertIn(titel, self.text)
            self.assertIn(text, self.text)
        for teil in luviq_daten.START_BLEACH:
            self.assertIn(teil.strip('. '), self.text)
        self.assertGreaterEqual(len(''.join(luviq_daten.START_BLEACH)), 90)

    def test_rechtlich_noetige_fusslinks_bleiben(self):
        self.assertRegex(self.html, rf'©\s*\d{{4}}\s+Luviq')

    def test_alle_bilddateien_sind_da(self):
        from django.contrib.staticfiles import finders
        for m in re.findall(r'src="/static/(shop1/images/start/[^"]+?)\.[0-9a-f]{12}(\.webp)"', self.html):
            self.assertTrue(finders.find(m[0] + m[1]), m)


class StartseiteV9Paket2Test(LuviqTestCase):
    """Paket 2 und 3 (26.11.2026): Text, tote Warteliste-Verweise, Preise, Referenzstücke, Fuß."""

    def setUp(self):
        super().setUp()
        self.html = self.hole('/').content.decode()
        self.text = sichtbarer_text(self.html)

    def test_keine_tageszahl_und_luisa_text(self):
        self.assertNotIn('2 bis 5 Tage', self.text)
        self.assertIn('auf ein Shirt, einen Hoodie oder Pullover', self.text)
        self.assertNotIn('dein Shirt', self.text)

    def test_fragen_sind_h3_und_ratgeberlinks_stehen(self):
        self.assertEqual(len(re.findall(r'<dt><h3>', self.html)), 8)
        self.assertIn('href="/wissen/bleach-painting/"', self.html)
        self.assertIn('href="/wissen/pflege-handbemalte-kleidung/"', self.html)

    def test_keine_toten_wartelisteverweise_mehr(self):
        for pfad in ('/', '/produkte/', '/ueber_uns/', '/kontakt/', '/liefergebiet/', '/motiv-anfragen/'):
            seite = self.hole(pfad).content.decode()
            with self.subTest(pfad=pfad):
                self.assertNotIn('#warteliste', seite)
                self.assertNotIn('#newsletter-form', seite)

    def test_fuss_ohne_doppelte_links(self):
        fuss = self.html[self.html.index('<footer class="fuss">'):]
        self.assertEqual(fuss.count('href="/ueber_uns/"'), 1)
        self.assertEqual(fuss.count('href="/kontakt/"'), 1)
        self.assertIn('Bleach Painting erklärt', fuss)

    def test_llms_ohne_preis_und_referenzstuecke_ohne_index(self):
        from ._basis import erzeuge_produkt
        ref = erzeuge_produkt('Custom Referenz', nummer=1, vergeben=True)
        text = self.hole('/llms.txt').content.decode()
        self.assertNotIn(' EUR', text)
        sitemap = self.hole('/sitemap.xml').content.decode()
        self.assertNotIn(ref.get_absolute_url(), sitemap)
        seite = self.hole(ref.get_absolute_url())
        self.assertEqual(seite.status_code, 200)
        self.assertIn('<meta name="robots" content="noindex, follow">', seite.content.decode())
