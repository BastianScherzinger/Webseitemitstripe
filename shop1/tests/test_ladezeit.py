"""Ladezeit: was im ausgelieferten Dokument darüber entscheidet.

Gemessen wird hier nichts – Messwerte hingen an Netz und Hosting. Geprüft
werden die Angaben, ohne die keine Messung gut ausfallen kann.
"""

import re
from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings

from tools import kritisches_css, schriften_zuschneiden

from ..management.commands import bildmasse_nachtragen
from ..templatetags.custom_tags import cloud, cloud_srcset
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
            # Seitenverhältnis steht erst mit den Maßen des Originals fest
            # (Produkt.bild_masse). Ohne gespeicherte Maße entfällt die Angabe;
            # test_stueckseite_nennt_die_masse_des_originals prüft den Fall mit Maßen.
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
            'https://res.cloudinary.com/demo/image/upload/f_auto,q_auto/v1/produkte/jacke.webp',
        )
        self.assertIn('f_auto,q_auto,w_800,h_1000,c_fill/', cloud(url, 'w_800,h_1000,c_fill'))

    def test_die_adresse_nennt_ein_modernes_format(self):
        """Verhindert, dass die Adresse wieder auf .jpg oder .png endet (PF15).
        Mit ``f_auto`` ist die Endung nur der Rückfall für Browser ohne
        modernes Format – steht dort JPEG, bekommen diese das alte Format,
        und die Messung zählt jedes Produktbild als altes Format."""
        basis = 'https://res.cloudinary.com/demo/image/upload/'
        faelle = {
            'v1/a/foto.JPG': 'f_auto,q_auto,w_200/v1/a/foto.webp',
            'v1/a/Photoroom_1.png': 'f_auto,q_auto,w_200/v1/a/Photoroom_1.webp',
            'v1/a/ohne_endung': 'f_auto,q_auto,w_200/v1/a/ohne_endung.webp',
            'v1/a/schon.avif': 'f_auto,q_auto,w_200/v1/a/schon.avif',
            'v1/a/schon.webp': 'f_auto,q_auto,w_200/v1/a/schon.webp',
            'v1/a/bild.png?_a=x': 'f_auto,q_auto,w_200/v1/a/bild.webp?_a=x',
        }
        for quelle, ziel in faelle.items():
            with self.subTest(quelle=quelle):
                self.assertEqual(cloud(basis + quelle, 'w_200'), basis + ziel)

    def test_produktbilder_der_startseite_enden_auf_webp(self):
        """Verhindert, dass eine Einbindung den Filter umgeht und die Seite
        wieder Bilder im alten Format nennt – an der ausgelieferten Seite
        geprüft, so wie die Messung sie liest."""
        from unittest import mock

        from ..models import Produkt

        erzeuge_produkt('Bemalte Bomberjacke')
        adresse = 'https://res.cloudinary.com/demo/image/upload/v1/media/produkte/IMG_1.jpg'
        with mock.patch.object(Produkt.bild.field.storage, 'url', return_value=adresse):
            Produkt.objects.update(bild='produkte/IMG_1.jpg')
            bilder = _sammle(self.hole('/').content.decode()).bilder
        cloudinary = [b['src'] for b in bilder if '/image/upload/' in b.get('src', '')]
        self.assertTrue(cloudinary, 'Die Startseite zeigt kein Produktbild')
        for quelle in cloudinary:
            self.assertTrue(quelle.endswith('.webp'), quelle)

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


class StildateienGepacktTest(LuviqTestCase):
    """Die Stildateien vor dem ersten Inhalt gehen gepackt raus (PF26)."""

    def test_start_packt_die_statischen_dateien_nach_dem_sammeln(self):
        """Verhindert, dass der Packschritt aus ``start.sh`` verschwindet oder
        vor ``collectstatic`` rutscht – ``--clear`` löschte die .gz-Dateien
        dann wieder. WhiteNoise packt nicht selbst, es liefert nur eine
        vorhandene ``datei.gz`` aus; ohne sie gehen beide Stildateien, auf die
        der erste Inhalt wartet, ungepackt raus."""
        start = (Path(settings.BASE_DIR) / 'start.sh').read_text(encoding='utf-8')
        befehle = [z.strip() for z in start.splitlines() if z.strip().startswith(('python', 'exec'))]
        packen = [z for z in befehle if 'whitenoise.compress' in z]
        self.assertEqual(len(packen), 1, befehle)
        self.assertIn(f' {Path(settings.STATIC_ROOT).name} ', packen[0] + ' ')
        self.assertIn('||', packen[0], 'Der Packschritt darf den Start nicht abbrechen')
        stelle = befehle.index(packen[0])
        sammeln = next(i for i, z in enumerate(befehle) if 'collectstatic' in z)
        server = next(i for i, z in enumerate(befehle) if 'gunicorn' in z)
        self.assertLess(sammeln, stelle)
        self.assertLess(stelle, server)

    def test_gepackt_sind_die_stildateien_weniger_als_ein_drittel(self):
        """Hält fest, was der Schritt bringt: dieselbe Packung wie beim Start,
        an den echten Stildateien gemessen."""
        import shutil
        import tempfile

        from whitenoise.compress import Compressor

        packer = Compressor(use_brotli=False, quiet=True)
        with tempfile.TemporaryDirectory() as ordner:
            for name in ('tailwind.css', 'style.css'):
                quelle = Path(settings.BASE_DIR) / 'shop1' / 'static' / 'shop1' / name
                ziel = Path(ordner) / name
                shutil.copyfile(quelle, ziel)
                with self.subTest(datei=name):
                    self.assertTrue(packer.should_compress(name))
                    gepackt = packer.compress(str(ziel))
                    self.assertEqual(gepackt, [str(ziel) + '.gz'])
                    self.assertLess(Path(gepackt[0]).stat().st_size * 3, quelle.stat().st_size)


#: Cloudinary-Adresse für Tests der Bildangaben (Filter ``cloud_srcset``, Archiv, Stückseite).
CLOUD_URL = 'https://res.cloudinary.com/demo/image/upload/v1/media/produkte/IMG_1.jpg'


class BildgroessenTest(LuviqTestCase):
    """srcset/sizes, Vorrang und Maße der Produktbilder (PF16, PF17, PF18, PF19, PF24, PF25)."""

    def test_srcset_nennt_mehrere_breiten_mit_beschnitt(self):
        """Verhindert, dass ein Handy dieselbe 600-px-Karte lädt wie ein
        Großbildschirm (PF16/PF24)."""
        srcset = cloud_srcset(CLOUD_URL, '300,450,600;c_fill;1.25')
        eintraege = srcset.split(', ')
        self.assertEqual(len(eintraege), 3, srcset)
        self.assertIn('w_300,h_375,c_fill', eintraege[0])
        self.assertTrue(eintraege[0].endswith(' 300w'))
        self.assertIn('w_600,h_750,c_fill', eintraege[2])
        for eintrag in eintraege:
            self.assertIn('f_auto,q_auto', eintrag)
            self.assertIn('.webp ', eintrag)

    def test_srcset_ohne_beschnitt_nimmt_c_limit(self):
        self.assertIn('w_900,c_limit', cloud_srcset(CLOUD_URL, '600,900,1200'))

    def test_srcset_fuer_lokale_bilder_bleibt_gueltig(self):
        """Im Entwicklungsmodus gibt es nur das Original: ein Eintrag mit der
        größten Breite, kein leeres ``srcset=""``."""
        self.assertEqual(cloud_srcset('/media/produkte/a.jpg', '300,450,600'),
                         '/media/produkte/a.jpg 600w')
        self.assertEqual(cloud_srcset(CLOUD_URL, ''), '')

    def _archiv_mit_bildern(self, anzahl=3):
        from unittest import mock

        from ..models import Produkt

        for n in range(anzahl):
            erzeuge_produkt(f'Stück {n}', bild=f'produkte/IMG_{n}.jpg')
        return mock.patch.object(
            Produkt.bild.field.storage, 'url',
            side_effect=lambda name: CLOUD_URL.replace('IMG_1', name.rsplit('/', 1)[-1][:-4]),
        )

    def test_archiv_laedt_nur_das_erste_bild_sofort_und_mit_vorrang(self):
        """Verhindert, dass das LCP-Bild von /produkte/ lazy lädt (PF17) oder
        ohne Vorrang (PF18), und dass mehr als ein Bild um die Vorfahrt
        streitet."""
        with self._archiv_mit_bildern():
            bilder = _sammle(self.hole('/produkte/').content.decode()).bilder
        karten = [b for b in bilder if 'IMG_' in b.get('src', '')]
        self.assertEqual(len(karten), 3)
        self.assertEqual(karten[0].get('loading'), 'eager')
        self.assertEqual(karten[0].get('fetchpriority'), 'high')
        for bild in karten[1:]:
            self.assertEqual(bild.get('loading'), 'lazy')
            self.assertIsNone(bild.get('fetchpriority'))

    def test_archiv_laedt_das_erste_bild_vor_und_wortgleich(self):
        """Verhindert zwei Fassungen desselben Bilds: ``imagesrcset`` und
        ``imagesizes`` des Preloads müssen wörtlich zu ``srcset``/``sizes``
        der ersten Karte passen (PF19)."""
        with self._archiv_mit_bildern():
            sammlung = _sammle(self.hole('/produkte/').content.decode())
        vorlade = [v for v in sammlung.vorladungen if v.get('as') == 'image']
        self.assertEqual(len(vorlade), 1)
        karte = next(b for b in sammlung.bilder if 'IMG_' in b.get('src', ''))
        self.assertEqual(vorlade[0]['imagesrcset'], karte['srcset'])
        self.assertEqual(vorlade[0]['imagesizes'], karte['sizes'])
        self.assertEqual(vorlade[0].get('fetchpriority'), 'high')
        self.assertTrue(vorlade[0].get('href'))

    def test_jede_karte_bietet_mehrere_groessen_an(self):
        with self._archiv_mit_bildern():
            for pfad in ('/produkte/', '/'):
                with self.subTest(pfad=pfad):
                    bilder = _sammle(self.hole(pfad).content.decode()).bilder
                    karten = [b for b in bilder if 'IMG_' in b.get('src', '')]
                    self.assertTrue(karten)
                    for bild in karten:
                        self.assertEqual(bild['srcset'].count(' 300w'), 1, bild['srcset'])
                        self.assertIn(' 600w', bild['srcset'])
                        self.assertTrue(bild.get('sizes'))

    def test_startseite_laedt_keine_karte_mit_vorrang(self):
        """Auf der Startseite ist das Hero-Foto das LCP-Bild, nicht die Karte."""
        with self._archiv_mit_bildern():
            bilder = _sammle(self.hole('/').content.decode()).bilder
        karten = [b for b in bilder if 'IMG_' in b.get('src', '')]
        self.assertTrue(karten)
        for bild in karten:
            self.assertEqual(bild.get('loading'), 'lazy')
            self.assertIsNone(bild.get('fetchpriority'))

    def test_vorladen_nennt_eine_adresse_als_rueckfall(self):
        """Ein Vorladen ohne ``href`` lesen Prüfwerkzeuge (und Browser ohne
        ``imagesrcset``) nicht (PF19)."""
        vorlade = [v for v in _sammle(self.hole('/').content.decode()).vorladungen
                   if v.get('as') == 'image']
        self.assertTrue(vorlade)
        for eintrag in vorlade:
            self.assertTrue(eintrag.get('href'), eintrag)
            self.assertTrue(eintrag.get('imagesrcset'), eintrag)

    def test_produkt_merkt_die_masse_eines_neuen_uploads(self):
        """Verhindert, dass ein neues Hauptbild ohne Maße gespeichert wird (PF25)."""
        import io
        import tempfile

        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import override_settings
        from PIL import Image

        puffer = io.BytesIO()
        Image.new('RGB', (1107, 2400), 'white').save(puffer, 'PNG')
        with tempfile.TemporaryDirectory() as ordner, override_settings(MEDIA_ROOT=ordner):
            produkt = erzeuge_produkt(
                'Mit Bild', bild=SimpleUploadedFile('a.png', puffer.getvalue(), 'image/png'))
        produkt.refresh_from_db()
        self.assertEqual((produkt.bild_breite, produkt.bild_hoehe), (1107, 2400))
        self.assertEqual(produkt.bild_masse, (1107, 2400))

    def test_masse_werden_wie_cloudinary_auf_1200_begrenzt(self):
        """Cloudinary liefert höchstens 1200 px Breite, das Verhältnis bleibt."""
        produkt = erzeuge_produkt('Breit', bild='produkte/a.jpg', bild_breite=3024, bild_hoehe=4032)
        self.assertEqual(produkt.bild_masse, (1200, 1600))
        ohne = erzeuge_produkt('Ohne', bild='produkte/b.jpg')
        self.assertIsNone(ohne.bild_masse)

    def test_stueckseite_nennt_die_masse_des_originals(self):
        """Verhindert den Layoutsprung beim Laden des Hauptbilds (PF25)."""
        from unittest import mock

        from ..models import Produkt

        produkt = erzeuge_produkt('Mit Maßen', bild='produkte/a.jpg',
                                  bild_breite=1200, bild_hoehe=1500)
        with mock.patch.object(Produkt.bild.field.storage, 'url', return_value=CLOUD_URL):
            seite = self.hole(produkt.get_absolute_url()).content.decode()
        bild = next(b for b in _sammle(seite).bilder if 'produkt_detail' in b.get('class', ''))
        self.assertEqual((bild['width'], bild['height']), ('1200', '1500'))
        self.assertEqual(bild.get('fetchpriority'), 'high')
        self.assertIn('w_900,c_limit', bild['src'])
        self.assertEqual(bild['srcset'].count(' 600w'), 1)

    def test_nachtragen_fuellt_fehlende_masse(self):
        """Verhindert, dass die vorhandenen Produkte nach dem Deploy ohne
        Maße bleiben: der Befehl liest sie aus der Bilddatei."""
        import io
        import tempfile

        from django.core.management import call_command
        from django.test import override_settings
        from PIL import Image

        with tempfile.TemporaryDirectory() as ordner, override_settings(MEDIA_ROOT=ordner):
            (Path(ordner) / 'produkte').mkdir()
            Image.new('RGB', (800, 600), 'white').save(Path(ordner) / 'produkte' / 'x.png')
            produkt = erzeuge_produkt('Alt', bild='produkte/x.png')
            kaputt = erzeuge_produkt('Fehlt', bild='produkte/gibt-es-nicht.png')
            ausgabe = io.StringIO()
            with self.assertLogs('shop1.management.commands.bildmasse_nachtragen', 'WARNING'):
                call_command(bildmasse_nachtragen.Command(), stdout=ausgabe, stderr=io.StringIO())
            with self.assertLogs('shop1.management.commands.bildmasse_nachtragen', 'WARNING'):
                call_command(bildmasse_nachtragen.Command(), stdout=io.StringIO(), stderr=io.StringIO())
        produkt.refresh_from_db()
        kaputt.refresh_from_db()
        self.assertEqual((produkt.bild_breite, produkt.bild_hoehe), (800, 600))
        self.assertIsNone(kaputt.bild_breite, 'Ein fehlendes Bild darf den Lauf nicht stoppen')
        self.assertIn('nachgetragen: 1', ausgabe.getvalue())


class SchriftdateienTest(LuviqTestCase):
    """Wenige Schriftdateien, jede mit font-display (PF27, VL16, S03)."""

    CSS = Path(settings.BASE_DIR) / 'shop1' / 'static' / 'shop1' / 'luviq.css'

    def test_hoechstens_vier_schriftdateien(self):
        """Verhindert, dass wieder je Schrift zwei Dateien (latin + latin-ext)
        hinzukommen: jede Datei ist ein Abruf vor dem ersten lesbaren Text."""
        css = self.CSS.read_text(encoding='utf-8')
        dateien = set(re.findall(r'url\(\s*["\']?([^"\')]+\.woff2?)', css))
        self.assertLessEqual(len(dateien), 4, sorted(dateien))
        for datei in dateien:
            self.assertTrue((self.CSS.parent / datei).exists(), datei)

    def test_jede_schriftregel_traegt_font_display(self):
        css = self.CSS.read_text(encoding='utf-8')
        regeln = re.findall(r'@font-face\s*\{[^}]*\}', css)
        self.assertGreaterEqual(len(regeln), 6)
        for regel in regeln:
            self.assertIn('font-display', regel, regel[:80])

    def test_die_vorgeladenen_schriften_gibt_es(self):
        """Verhindert einen Preload auf eine Datei, die es nicht mehr gibt
        (nach dem Umbenennen der Schriften)."""
        seite = self.hole('/').content.decode()
        schriften = [v for v in _sammle(seite).vorladungen if v.get('as') == 'font']
        self.assertTrue(schriften)
        for eintrag in schriften:
            stamm = eintrag['href'].rsplit('/', 1)[-1].split('.')[0]
            treffer = list((self.CSS.parent / 'fonts').glob(stamm + '.woff2'))
            self.assertTrue(treffer, f'{stamm}: keine Datei in fonts/')


class KritischesCssTest(LuviqTestCase):
    """Critical CSS je Seitentyp inline, luviq.css lädt nach (VL16)."""

    #: Seite → Seitentyp (Datei ``shop1/stile/kritisch-<typ>.html``).
    SEITEN = {
        '/': 'start',
        '/produkte/': 'archiv',
        '/ueber_uns/': 'luisa',
        '/motiv-anfragen/': 'anfrage',
        '/motiv-anfragen/danke/': 'danke',
    }

    @staticmethod
    def _werkzeug():
        return kritisches_css

    def test_die_dateien_sind_aktuell(self):
        """Verhindert, dass luviq.css geändert wird und das inline gesetzte
        Stück veraltet – die Dateien werden nie von Hand gepflegt."""
        modul = self._werkzeug()
        css = modul.QUELLE.read_text(encoding='utf-8')
        for profil in modul.PROFILE:
            with self.subTest(profil=profil):
                self.assertEqual(
                    modul.ziel(profil).read_text(encoding='utf-8'), modul.vorlage(css, profil),
                    f'kritisch-{profil}.html ist veraltet: python tools/kritisches_css.py',
                )

    def test_jeder_seitentyp_ist_klein_und_traegt_den_ersten_bildschirm(self):
        modul = self._werkzeug()
        erwartet = {
            'start': ('.lv-hero{', '.lv-pano'),
            'archiv': ('.lv-raster{', '.lv-karte{'),
            'stueck': ('.lv-stueck{', '.lv-stueck-bild'),
            'luisa': ('.lv-luisa{', '.lv-ablauf'),
            'anfrage': ('.lv-formular{', '.lv-feld{'),
            'danke': ('.lv-danke{', '.lv-recht'),
        }
        for profil, muster in erwartet.items():
            with self.subTest(profil=profil):
                text = modul.ziel(profil).read_text(encoding='utf-8')
                self.assertLess(len(text.encode('utf-8')), 20_000)
                for stueck in ('@font-face', ':root{', '.lv-kopf{') + muster:
                    self.assertIn(stueck, text)
                self.assertNotIn('latin-ext', text)
                self.assertNotIn('.lv-alt main', text)
                self.assertNotIn('{{', text.replace("{% static", ''))

    def test_neue_seiten_setzen_den_stil_inline_und_laden_den_rest_nach(self):
        modul = self._werkzeug()
        for pfad, profil in self.SEITEN.items():
            with self.subTest(pfad=pfad):
                kopf = self.hole(pfad).content.decode().split('</head>')[0]
                self.assertIn('<style>', kopf)
                self.assertIn('.lv-kopf{', kopf)
                self.assertNotIn('{%', kopf)
                self.assertNotIn('url("fonts/', kopf, 'Schriftadressen müssen gehasht sein')
                self.assertRegex(kopf, r'url\("/static/shop1/fonts/[^"]+\.woff2"\)')
                self.assertRegex(
                    kopf,
                    r'<link rel="stylesheet" href="[^"]*luviq[^"]*\.css" media="print" data-schrift-nachladen>')
                self.assertRegex(
                    kopf, r'<noscript><link rel="stylesheet" href="[^"]*luviq[^"]*\.css"></noscript>')
        self.assertIn('.lv-hero{', self.hole('/').content.decode())
        self.assertNotIn('.lv-hero{', self.hole('/produkte/').content.decode().split('</head>')[0])
        self.assertIn('.lv-fuss{', self.hole('/motiv-anfragen/danke/').content.decode())

    def test_stueckseite_traegt_das_stueck_css(self):
        produkt = erzeuge_produkt('Mit Stil')
        kopf = self.hole(produkt.get_absolute_url()).content.decode().split('</head>')[0]
        self.assertIn('.lv-stueck{', kopf)
        self.assertNotIn('.lv-raster{', kopf)

    def test_alte_seiten_laden_luviq_css_weiter_blockierend(self):
        """Die Alt-Schicht (Konto, Kasse, Wissen, Rechtstexte) bleibt bei der
        bisherigen Reihenfolge: Tailwind, style.css, luviq.css – ohne
        Zwischenzustand."""
        kopf = self.hole('/kontakt/').content.decode().split('</head>')[0]
        self.assertRegex(kopf, r'<link rel="stylesheet" href="[^"]*luviq[^"]*\.css">')
        self.assertNotIn('<style>.', kopf)
        self.assertNotIn('media="print" data-schrift-nachladen', kopf.split('luviq')[0][-300:])


class WerkzeugeTest(LuviqTestCase):
    """Die beiden Werkzeuge hinter Schriften und Critical CSS (``tools/``)."""

    FONTS = Path(settings.BASE_DIR) / 'shop1' / 'static' / 'shop1' / 'fonts'

    def test_jede_ausgabe_des_schriftwerkzeugs_liegt_im_ordner(self):
        """Verhindert, dass das Werkzeug eine Datei erzeugt, die der Ordner nicht
        hat (oder umgekehrt): die Namen im Werkzeug und in ``luviq.css`` müssen übereinstimmen."""
        css = (self.FONTS.parent / 'luviq.css').read_text(encoding='utf-8')
        erwartet = set(schriften_zuschneiden.ZUSAMMEN) | set(schriften_zuschneiden.ZUGESCHNITTEN)
        erwartet |= {name.replace('-wght', '') for name in schriften_zuschneiden.AUFTRAG}
        self.assertEqual(len(erwartet), 4, sorted(erwartet))
        for name in erwartet:
            with self.subTest(datei=name):
                self.assertTrue((self.FONTS / name).exists())
                self.assertIn(f'fonts/{name}', css)
        im_ordner = {p.name for p in self.FONTS.glob('*.woff2')}
        self.assertEqual(im_ordner, erwartet, 'Verwaiste Schriftdatei im Ordner')

    def test_die_bereiche_des_werkzeugs_stehen_in_der_stilvorlage(self):
        css = (self.FONTS.parent / 'luviq.css').read_text(encoding='utf-8')
        self.assertIn(schriften_zuschneiden.LATIN, css)
        self.assertIn(schriften_zuschneiden.LATIN_EXT, css)

    def test_die_zusammengefuehrten_schriften_tragen_beide_zeichenbereiche(self):
        """Verhindert, dass beim Zusammenlegen von latin und latin-ext Zeichen
        verlorengehen: Umlaute, ß, Nº und ein Buchstabe nur aus latin-ext."""
        import importlib.util
        from unittest import SkipTest

        if importlib.util.find_spec('fontTools') is None:
            raise SkipTest('fontTools nicht installiert')
        from fontTools.ttLib import TTFont

        for name in ('cormorant-garamond-italic.woff2', 'jetbrains-mono-normal.woff2'):
            with self.subTest(datei=name):
                schrift = TTFont(self.FONTS / name)
                zeichen = schrift.getBestCmap()
                for z in 'äöüßÄÖÜ€º·—ł':
                    self.assertIn(ord(z), zeichen, f'{name}: {z!r} fehlt')
        mono = TTFont(self.FONTS / 'jetbrains-mono-normal.woff2')
        achsen = {a.axisTag: (a.minValue, a.maxValue) for a in mono['fvar'].axes}
        self.assertEqual(achsen, {'wght': (400.0, 500.0)})

    def test_kritisches_css_laesst_andere_seiten_und_die_alt_schicht_draussen(self):
        css = (
            '.lv-kopf{color:red}.lv-alt main p{margin:0}.lv-warteliste{padding:1px}'
            '.lv-hero,.lv-teaser{gap:2px}@media (max-width:1023px){.lv-hero{x:1}.lv-chip{x:2}}'
        )
        start = kritisches_css.kritisch(css, 'start')
        self.assertIn('.lv-kopf{color:red}', start)
        self.assertIn('.lv-hero,.lv-teaser{gap:2px}', start)  # eine erlaubte Auswahl genügt
        self.assertIn('@media (max-width:1023px){.lv-hero{x:1}', start)
        self.assertNotIn('.lv-alt', start)
        self.assertNotIn('.lv-warteliste', start)
        self.assertNotIn('.lv-chip{', kritisches_css.kritisch(css, 'archiv'))

    def test_kritisches_css_haelt_zeichenketten_und_calc_ganz(self):
        css = ('@font-face{font-family:"Cormorant Garamond";src:url("fonts/a.woff2") format("woff2")}'
               '.lv-kopf{padding:calc(100vw - 10px) 2px; content: "a  b" }')
        text = kritisches_css.vorlage(css, 'archiv')
        self.assertIn('font-family:"Cormorant Garamond"', text)
        self.assertIn("{% static 'shop1/fonts/a.woff2' %}", text)
        self.assertIn('calc(100vw - 10px)', text)
        self.assertIn('content:"a  b"', text)

    def test_kritisches_css_lehnt_vorlagensyntax_im_css_ab(self):
        with self.assertRaises(ValueError):
            kritisches_css.vorlage('.lv-kopf{content:"{{ x }}"}', 'start')
