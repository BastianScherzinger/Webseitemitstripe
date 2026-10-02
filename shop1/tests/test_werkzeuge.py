"""Die beiden Werkzeuge in ``tools/``: ``mailvorschau.py`` und ``schriften_zuschneiden.py``.

Beide laufen von Hand, nie im Betrieb. Dass sie hier getestet werden, hat
einen Grund: ``mailvorschau`` ist der einzige Weg, die gestalteten Mails zu
sehen, ohne eine zu verschicken – und ``schriften_zuschneiden`` erzeugt die
Schriftdateien, auf die ``luviq.css`` verweist. Ein stiller Bruch fiele erst
bei der nächsten Mail oder der nächsten Schrift auf.
"""

import os
import re
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from tools import mailvorschau, schriften_zuschneiden

from .. import mails
from ._basis import LuviqTestCase

#: ``tools`` ist kein Paket mit ``__init__``, aber der Projektordner liegt beim Testlauf
#: auf dem Suchpfad – so lädt ``from tools import …`` die Skripte wie jedes Modul.
WURZEL = Path(settings.BASE_DIR)


class MailvorschauTest(LuviqTestCase):

    ERWARTET = {'admin-kontakt.html', 'admin.html', 'admin-motiv.html', 'bastian.html',
                'bastian-motiv.html', 'bastian-registrierung.html', 'kunde.html',
                'kunde-newsletter.html'}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vorschau = mailvorschau

    def test_schreibt_alle_vorschauen_und_verschickt_nichts(self):
        original = mails.send_brevo_email
        with tempfile.TemporaryDirectory() as ordner, \
                mock.patch.dict(os.environ, {'BETREIBER_KOPIE_AN': 'echt@example.invalid'}):
            self.vorschau.main(Path(ordner) / 'neu' / 'unterordner')
            ziel = Path(ordner) / 'neu' / 'unterordner'
            self.assertEqual({p.name for p in ziel.iterdir()}, self.ERWARTET)
            for datei in ziel.iterdir():
                with self.subTest(datei=datei.name):
                    html = datei.read_text(encoding='utf-8')
                    self.assertIn('<html', html.lower())
            self.assertEqual((ziel / 'admin.html').read_text(encoding='utf-8'),
                             (ziel / 'admin-kontakt.html').read_text(encoding='utf-8'))
            # Nutzertext wird maskiert, nichts Fremdes steht im Skriptpfad.
            self.assertNotIn('<script>alert', (ziel / 'admin-kontakt.html').read_text(encoding='utf-8'))
            # Die Umgebung ist wiederhergestellt, der Versandweg ersetzt-und-zurückgesetzt.
            self.assertEqual(os.environ['BETREIBER_KOPIE_AN'], 'echt@example.invalid')
        self.assertIs(mails.send_brevo_email, original)

    def test_die_umgebungshilfe_stellt_werte_wieder_her_auch_bei_fehlern(self):
        with mock.patch.dict(os.environ, {'VORSCHAU_A': 'alt'}):
            os.environ.pop('VORSCHAU_B', None)
            with self.assertRaises(RuntimeError):
                with self.vorschau._env(VORSCHAU_A='neu', VORSCHAU_B='neu'):
                    self.assertEqual(os.environ['VORSCHAU_A'], 'neu')
                    raise RuntimeError('Abbruch')
            self.assertEqual(os.environ['VORSCHAU_A'], 'alt')
            self.assertNotIn('VORSCHAU_B', os.environ)

    def test_der_beispieltext_enthaelt_den_script_versuch(self):
        """Sonst prüfte die Vorschau die Maskierung gar nicht."""
        self.assertIn('<script>', self.vorschau.LANG)


class SchriftenZuschneidenTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schriften = schriften_zuschneiden

    def test_jede_quelle_liegt_im_repository(self):
        for name in self.schriften.AUFTRAG:
            with self.subTest(quelle=name):
                self.assertTrue((self.schriften.QUELLE / name).is_file())
        for name, (datei, *_rest) in self.schriften.ERSATZ.items():
            with self.subTest(ersatz=name):
                self.assertIn(datei, self.schriften.AUFTRAG)

    def test_die_ausgabedateien_sind_genau_die_der_stylesheet(self):
        """Verhindert eine Schrift, die das Skript erzeugt und kein CSS
        braucht – oder ein CSS, das auf eine nie erzeugte Datei zeigt."""
        erzeugt = {name.replace('-wght', '') for name in self.schriften.AUFTRAG}
        css = (WURZEL / 'shop1' / 'static' / 'shop1' / 'luviq.css').read_text(encoding='utf-8')
        genannt = set(re.findall(r'url\("fonts/([^"]+\.woff2)"\)', css))
        self.assertEqual(erzeugt, genannt)
        for name in erzeugt:
            self.assertTrue((self.schriften.ZIEL / name).is_file(), name)

    def test_je_familie_entstehen_genau_zwei_teile(self):
        """Das Skript soll je Familie genau zwei Teile (latin, latin-ext) erzeugen."""
        familien = {}
        for name in self.schriften.AUFTRAG:
            familien.setdefault(name.split('-latin')[0], []).append(name)
        self.assertEqual(len(familien), 3)
        self.assertTrue(all(len(teile) == 2 for teile in familien.values()))

    def test_die_breite_summiert_die_vorschuebe_geteilt_durch_einheiten(self):
        font = mock.MagicMock()
        font.getBestCmap.return_value = {ord('a'): 'a', ord('b'): 'b'}
        daten = {'head': mock.Mock(unitsPerEm=1000), 'hmtx': {'a': (500, 0), 'b': (250, 0)}}
        font.__getitem__.side_effect = daten.__getitem__
        self.assertAlmostEqual(self.schriften._breite(font, 'aab'), 1.25)
        # Zeichen ohne Eintrag zählen nicht – kein KeyError.
        self.assertAlmostEqual(self.schriften._breite(font, 'a?'), 0.5)

    def test_das_skript_schneidet_zu_und_kopiert_die_lizenzen(self):
        try:
            import brotli  # noqa: F401
            import fontTools  # noqa: F401
        except ImportError:
            self.skipTest('fontTools/brotli nicht installiert (nur Werkzeug, nicht Teil des Betriebs)')
        with tempfile.TemporaryDirectory() as ordner, \
                mock.patch.object(self.schriften, 'ZIEL', Path(ordner) / 'fonts'), \
                mock.patch.object(self.schriften, '_ersatzwerte') as ersatz, \
                mock.patch('builtins.print'):
            self.assertEqual(self.schriften.main(), 0)
            ziel = Path(ordner) / 'fonts'
            erzeugt = {p.name for p in ziel.glob('*.woff2')}
            self.assertEqual(erzeugt, {n.replace('-wght', '') for n in self.schriften.AUFTRAG})
            self.assertTrue(all(p.stat().st_size > 1000 for p in ziel.glob('*.woff2')))
            self.assertEqual({p.name for p in ziel.glob('OFL-*.txt')},
                             {p.name for p in self.schriften.QUELLE.glob('OFL-*.txt')})
            ersatz.assert_called_once_with()

    def test_die_pfade_zeigen_in_dieses_projekt(self):
        self.assertEqual(Path(self.schriften.WURZEL).resolve(), WURZEL.resolve())
        self.assertTrue(str(self.schriften.ZIEL).endswith(os.path.join('shop1', 'static', 'shop1', 'fonts')))
        self.assertIn('tools', self.schriften.__file__)
