"""Paket 5 (26.11.2026): Unterseiten im Rahmen der Startseite v9 (Kopf, Fuß, Daumenleiste), Hauptknopf auf den fünf
Kurzseiten, Messpunkte an allen Kontaktlinks, WhatsApp-Text, Banner am PC."""
import re
import sys
from pathlib import Path

from django.conf import settings

from ._basis import LuviqTestCase, erzeuge_produkt
from .test_geo import sichtbarer_text

OEFFENTLICH = ['/produkte/', '/ueber_uns/', '/motiv-anfragen/', '/liefergebiet/', '/kontakt/', '/wissen/',
               '/wissen/bleach-painting/', '/gaestebuch/', '/impressum/', '/datenschutz/']
KURZ = ['/produkte/', '/ueber_uns/', '/motiv-anfragen/', '/liefergebiet/', '/kontakt/']
STATIC = Path(settings.BASE_DIR) / 'shop1' / 'static' / 'shop1'


class UnterseitenRahmenTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.enterContext(self.settings(ANFRAGESHOP=True, VERKAUF_AKTIV=False))
        self.stueck = erzeuge_produkt('Rahmenstueck', preis=69, lagerbestand=1)

    def seiten(self):
        return OEFFENTLICH + [self.stueck.get_absolute_url(), '/gibt-es-nicht-xyz/']

    def test_rahmen_der_startseite_auf_allen_unterseiten(self):
        for pfad in self.seiten():
            html = self.hole(pfad).content.decode()
            with self.subTest(pfad=pfad):
                self.assertIn('<header class="kopf">', html)
                self.assertIn('<footer class="fuss">', html)
                self.assertRegex(html, r'<body class="[^"]*\blv-rahmen\b')
                self.assertIn('shop1/rahmen', html)
                self.assertNotIn('class="lv-kopf"', html)
                self.assertNotIn('class="lv-fuss"', html)
                self.assertNotIn('class="lv-hinweis"', html)
                self.assertIn('href="/#arbeiten"', html)
                self.assertIn('href="/#fragen"', html)
                self.assertRegex(html, r'class="k-wa" href="https://wa\.me/4917624908402')
                self.assertEqual(len(re.findall(r'<h1\b', html)), 1)

    def test_startseite_bleibt_ohne_rahmenklasse_und_rahmenstil(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('lv-rahmen', html)
        self.assertNotIn('rahmen.css', html)
        self.assertNotIn('rahmen.js', html)
        self.assertIn('href="#arbeiten"', html)
        self.assertIn('id="top"', html)

    def test_daumenleiste_auf_unterseiten_ausser_rechts_und_konto(self):
        for pfad in ('/produkte/', '/ueber_uns/', '/liefergebiet/', '/kontakt/', '/wissen/'):
            with self.subTest(pfad=pfad):
                self.assertContains(self.hole(pfad), '<nav class="leiste"')
        for pfad in ('/impressum/', '/datenschutz/', '/motiv-anfragen/'):
            with self.subTest(pfad=pfad):
                self.assertNotContains(self.hole(pfad), '<nav class="leiste"')

    def test_auszug_in_rahmen_css_stimmt_mit_startseite_css_ueberein(self):
        sys.path.insert(0, str(Path(settings.BASE_DIR) / 'tools'))
        try:
            import rahmen_css_bauen as b
        finally:
            sys.path.pop(0)
        css = (STATIC / 'rahmen.css').read_text(encoding='utf-8')
        auszug = css[css.index(b.ANFANG):css.index(b.ENDE) + len(b.ENDE)]
        self.assertEqual(auszug.replace('\r\n', '\n'), b.bauen(),
                         'rahmen.css ist veraltet: python tools/rahmen_css_bauen.py ausführen')

    def test_kurzseiten_haben_genau_einen_hauptknopf_whatsapp_und_den_mail_link(self):
        for pfad in KURZ:
            html = self.hole(pfad).content.decode()
            body = html[html.index('<main'):html.index('</main>')]
            with self.subTest(pfad=pfad):
                self.assertEqual(len(re.findall(r'<a class="knopf"', body)), 1)
                self.assertRegex(body, r'<a class="knopf" href="https://wa\.me/4917624908402[^"]*"[^>]*>Per WhatsApp anfragen')
                self.assertIn('href="mailto:brehlerluisa@gmail.com', body)

    def test_whatsapp_text_endet_nicht_auf_auslassungspunkte(self):
        import urllib.parse as u
        from shop1 import luviq_daten
        text = u.unquote(u.urlparse(luviq_daten.START_WHATSAPP).query.split('text=')[1])
        self.assertEqual(text, 'Hallo Luisa, ich hätte gern ein Motiv auf einem Shirt, Hoodie oder Pullover.')
        self.assertNotIn('…', text)

    def test_kein_gedankenstrich_im_sichtbaren_text_der_kurzseiten(self):
        for pfad in ('/produkte/', '/motiv-anfragen/', '/liefergebiet/', '/kontakt/'):
            html = self.hole(pfad).content.decode()
            main = html[html.index('<main'):html.index('</main>')]
            with self.subTest(pfad=pfad):
                text = sichtbarer_text(main)
                if pfad == '/kontakt/':
                    # der Datenschutzhinweis am Formular ist Rechtstext und bleibt unverändert
                    text = text.replace('Datenschutzerklärung – in der Fußzeile', '')
                self.assertNotRegex(text, r'[—–]')

    def test_motiv_anfragen_ueberschrift_ohne_gedankenstrich(self):
        html = self.hole('/motiv-anfragen/').content.decode()
        self.assertIn('id="anfrage-titel">Sag mir, was du willst, ich mal’s dir.</h1>', html)

    def test_kontakt_nennt_die_zeitangaben_weiter_nur_dort(self):
        text = sichtbarer_text(self.hole('/kontakt/').content.decode())
        self.assertIn('2 bis 5 Tage', text)
        for pfad in ('/', '/ueber_uns/', '/liefergebiet/'):
            self.assertNotIn('2 Stunden', sichtbarer_text(self.hole(pfad).content.decode()), pfad)


class MesspunkteTest(LuviqTestCase):
    """Alle Kontaktlinks (WhatsApp, Mail, Instagram) tragen `data-ereignis` (einwilligung.js zählt sie nur nach Einwilligung)."""

    def links_ohne_ereignis(self, html):
        fehlt = []
        for m in re.finditer(r'<a\b[^>]*href="(https://wa\.me/[^"]*|mailto:[^"]*|https://www\.instagram\.com/[^"]*)"[^>]*>', html):
            if 'data-ereignis=' not in m.group(0):
                fehlt.append(m.group(0)[:120])
        return fehlt

    def test_startseite_alle_kontaktlinks_gemessen(self):
        html = self.hole('/').content.decode()
        body = html[html.index('<body'):]
        self.assertEqual(self.links_ohne_ereignis(body), [])
        namen = set(re.findall(r'data-ereignis="([a-z_]+)"', body))
        for n in ('hero_whatsapp', 'hero_mail', 'kopf_whatsapp', 'luisa_whatsapp', 'luisa_mail', 'luisa_instagram',
                  'galerie_whatsapp', 'galerie_instagram', 'fragen_whatsapp', 'kontakt_whatsapp', 'kontakt_mail',
                  'leiste_whatsapp', 'leiste_mail', 'fuss_whatsapp', 'fuss_mail', 'fuss_instagram'):
            self.assertIn(n, namen)

    def test_unterseiten_rahmen_und_hauptknopf_gemessen(self):
        for pfad in ('/ueber_uns/', '/kontakt/', '/liefergebiet/', '/produkte/'):
            html = self.hole(pfad).content.decode()
            body = html[html.index('<body'):]
            with self.subTest(pfad=pfad):
                self.assertEqual(self.links_ohne_ereignis(body), [])
                self.assertIn('data-ereignis="kopf_whatsapp"', body)
                self.assertIn('data-ereignis="fuss_whatsapp"', body)


class BannerPcTest(LuviqTestCase):
    def test_banner_am_pc_kompakter_kasten_unten_rechts(self):
        css = (STATIC / 'einwilligung.css').read_text(encoding='utf-8')
        self.assertRegex(css, r'@media \(min-width:1000px\)\{\s*\.lv-einwilligung\{left:auto;right:24px;bottom:24px')
