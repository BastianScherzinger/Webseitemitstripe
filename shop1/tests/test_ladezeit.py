"""Ladezeit: was im ausgelieferten Dokument darüber entscheidet.

Gemessen wird hier nichts – Messwerte hingen an Netz und Hosting. Geprüft
werden die Angaben, ohne die keine Messung gut ausfallen kann.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings

from ..templatetags.custom_tags import cloud
from ._basis import OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_produkt

TEMPLATE_VERZEICHNIS = Path(settings.BASE_DIR)

#: Produktbild-Einbindungen müssen über den Cloudinary-Filter laufen, sonst
#: liefert Cloudinary das Original statt WebP/AVIF in passender Grösse.
BILDTEMPLATES = [
    'shop1/templates/shop1/index.html',
    'shop1/templates/shop1/produkte.html',
    'shop1/templates/shop1/produkt_detail.html',
    'shop1/templates/shop1/warenkorb.html',
]


class _Bildsammler(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bilder = []
        self.vorladungen = []

    def handle_starttag(self, tag, attrs):
        werte = dict(attrs)
        if tag == 'img':
            self.bilder.append(werte)
        elif tag == 'link' and werte.get('rel') == 'preload':
            self.vorladungen.append(werte)


def _sammle(html):
    sammler = _Bildsammler()
    sammler.feed(html)
    return sammler


class BildladenTest(LuviqTestCase):
    """Wann welches Bild geladen wird."""

    def setUp(self):
        erzeuge_produkt('Bemalte Bomberjacke')

    def test_jedes_bild_sagt_wann_es_geladen_wird(self):
        """Verhindert, dass ein Bild weit unterhalb des Bildschirms sofort
        geladen wird und dem sichtbaren Bereich die Bandbreite wegnimmt."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                for bild in _sammle(self.hole(pfad).content.decode()).bilder:
                    self.assertIn(
                        bild.get('loading'), ('lazy', 'eager'),
                        f'{pfad}: <img src="{bild.get("src", "?")[:60]}"> '
                        f'ohne loading-Angabe',
                    )

    def test_hoechstens_ein_bild_je_seite_hat_vorfahrt(self):
        """Verhindert, dass mehrere Bilder gleichzeitig um die Vorfahrt
        streiten – dann wird keines davon schnell fertig. ``fetchpriority``
        darf pro Seite nur das eine grösste Bild im ersten Bildschirm tragen."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                bilder = _sammle(self.hole(pfad).content.decode()).bilder
                vorrang = [b for b in bilder if b.get('fetchpriority') == 'high']
                self.assertLessEqual(
                    len(vorrang), 1,
                    f'{pfad}: {len(vorrang)} Bilder mit fetchpriority="high"',
                )

    def test_bilder_unterhalb_des_ersten_bildschirms_werden_nachgeladen(self):
        """Verhindert, dass eine Bilderstrecke vollständig beim Seitenaufbau
        geladen wird. Sofort geladen werden dürfen nur die wenigen Bilder, die
        beim Öffnen tatsächlich sichtbar sind."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                bilder = _sammle(self.hole(pfad).content.decode()).bilder
                sofort = [b for b in bilder if b.get('loading') == 'eager']
                self.assertLessEqual(
                    len(sofort), 2,
                    f'{pfad}: {len(sofort)} Bilder mit loading="eager"',
                )

    def test_das_bild_im_ersten_bildschirm_wird_vorgeladen(self):
        """Verhindert, dass der Browser das grösste sichtbare Bild erst
        entdeckt, wenn er den ``<body>`` übersetzt hat. Das ist auf der
        Startseite der grösste Einzelposten der Ladezeit."""
        seite = self.hole('/').content.decode()
        sammlung = _sammle(seite)
        bilder = [v for v in sammlung.vorladungen if v.get('as') == 'image']
        self.assertTrue(bilder, 'Die Startseite lädt kein Bild vorab')
        self.assertTrue(
            any(b.get('fetchpriority') == 'high' for b in sammlung.bilder),
            'Kein Bild der Startseite ist als vorrangig gekennzeichnet',
        )

    def test_bilder_mit_festem_rahmen_nennen_ihre_masse(self):
        """Verhindert Layoutsprünge beim Nachladen: ohne ``width`` und
        ``height`` weiss der Browser die Bildgrösse erst, wenn das Bild da ist,
        und schiebt dann den Text darunter weg."""
        ausgenommen = {
            # Hauptbild der Produktseite: läuft ohne Beschnitt (c_limit), das
            # Seitenverhältnis steht deshalb erst mit dem Bild fest.
            'produkt_detail',
        }
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                for bild in _sammle(self.hole(pfad).content.decode()).bilder:
                    if any(name in bild.get('class', '') for name in ausgenommen):
                        continue
                    hat_masse = bild.get('width') and bild.get('height')
                    hat_stil = 'width' in bild.get('style', '')
                    self.assertTrue(
                        hat_masse or hat_stil,
                        f'{pfad}: <img src="{bild.get("src", "?")[:60]}"> '
                        f'ohne width/height',
                    )


class BildformatTest(LuviqTestCase):
    """Der Cloudinary-Filter liefert modernes Format und passende Grösse."""

    def test_der_filter_setzt_format_und_qualitaet(self):
        """Verhindert, dass ``f_auto,q_auto`` beim Umbauen des Filters
        verlorengeht – Cloudinary liefert dann wieder das Original-JPEG
        statt WebP oder AVIF."""
        url = 'https://res.cloudinary.com/demo/image/upload/v1/produkte/jacke.jpg'
        self.assertEqual(
            cloud(url),
            'https://res.cloudinary.com/demo/image/upload/f_auto,q_auto/v1/produkte/jacke.jpg',
        )
        self.assertIn('f_auto,q_auto,w_800,h_1000,c_fill/', cloud(url, 'w_800,h_1000,c_fill'))

    def test_der_filter_laesst_fremde_adressen_unveraendert(self):
        """Verhindert, dass lokale ``/media/``-Adressen im Entwicklungsmodus
        oder Werbebilder von fremden Servern verstümmelt werden."""
        for url in ('/media/produkte/jacke.jpg', 'https://example.invalid/bild.png', ''):
            with self.subTest(url=url):
                self.assertEqual(cloud(url, 'w_400'), url)

    def test_kein_produktbild_umgeht_den_filter(self):
        """Verhindert den Zustand, den dieser Lauf vorgefunden hat: der Filter
        war vorhanden, wurde aber nur an zwei von sechs Einbindungen benutzt –
        die übrigen luden das unskalierte Original."""
        # Nur <img>-Einbindungen. In JSON-LD und og:image gehört die
        # Originaladresse, dort wird bewusst nicht skaliert.
        muster = re.compile(r'<img[^>]*?src="\{\{\s*[\w.]*bild(?:\.url)?\s*\}\}"', re.DOTALL)
        for datei in BILDTEMPLATES:
            pfad = TEMPLATE_VERZEICHNIS / datei
            with self.subTest(datei=datei):
                treffer = muster.findall(pfad.read_text(encoding='utf-8'))
                self.assertFalse(
                    treffer,
                    f'{datei} bindet ein Produktbild ohne |cloud ein: {treffer}',
                )


class SchriftenTest(LuviqTestCase):
    """Webfonts dürfen den Text nicht verstecken, bis sie geladen sind."""

    def test_schriften_blockieren_die_textanzeige_nicht(self):
        """Verhindert, dass die Seite sekundenlang ohne Text dasteht, weil der
        Browser auf eine Schriftdatei von einem fremden Server wartet."""
        seite = self.hole('/').content.decode()
        for stelle in re.findall(r'fonts\.googleapis\.com/css2[^"\']+', seite):
            with self.subTest(stelle=stelle[:60]):
                self.assertIn('display=swap', stelle)
