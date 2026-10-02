"""Die Prüfbefehle melden ihre Ausnahmen nicht nur im Bericht, sondern auch im Protokoll.

Vorher fingen ``pruefe_seite``, ``pruefe_mail`` und ``pruefe_links`` breite
Ausnahmen ab und schrieben sie nur in die Fehlerliste des Laufs. Das ist
kein Verschlucken – der Lauf endet rot –, aber die Ablaufspur (Traceback)
ging verloren. Jetzt steht sie im Protokoll ``shop1`` (Railway-Log).
Der Bericht selbst bleibt unverändert; geprüft wird beides.
"""

from unittest import mock

from django.test import SimpleTestCase

from ..management.commands import pruefe_links, pruefe_mail, pruefe_seite


def _befehl(klasse):
    befehl = klasse()
    befehl.fehler, befehl.warnungen = [], []
    return befehl


class PruefeSeiteProtokollTest(SimpleTestCase):
    databases = {'default', 'pystore'}

    def test_eine_nicht_erreichbare_datenbank_steht_im_bericht_und_im_protokoll(self):
        befehl = _befehl(pruefe_seite.Command)
        with mock.patch.object(pruefe_seite, 'connections') as verbindungen, \
                self.assertLogs('shop1', level='WARNING') as protokoll:
            verbindungen.__getitem__.return_value.cursor.side_effect = RuntimeError('weg')
            befehl._pruefe_datenbanken()
        self.assertTrue(any('nicht erreichbar: weg' in f for f in befehl.fehler), befehl.fehler)
        self.assertTrue(any('Datenbank default nicht erreichbar' in z for z in protokoll.output))
        self.assertTrue(any('RuntimeError' in z for z in protokoll.output))   # Traceback dabei

    def test_nicht_lesbare_tabellen_ergeben_keine_falschmeldung_aber_eine_spur(self):
        befehl = _befehl(pruefe_seite.Command)
        with mock.patch.object(pruefe_seite, 'connections') as verbindungen, \
                self.assertLogs('shop1', level='WARNING') as protokoll:
            verbindungen.__getitem__.return_value.introspection.table_names.side_effect = RuntimeError('x')
            self.assertEqual(befehl._fehlende_tabellen('pystore'), [])
        self.assertIn('Tabellen von pystore nicht lesbar', protokoll.output[0])

    def test_nicht_lesbare_produkte_stehen_im_bericht_und_im_protokoll(self):
        befehl = _befehl(pruefe_seite.Command)
        with mock.patch('shop1.models.Produkt.objects') as objekte, \
                self.assertLogs('shop1', level='WARNING') as protokoll:
            objekte.filter.side_effect = RuntimeError('tabelle fehlt')
            befehl._pruefe_produkte()
        self.assertEqual(befehl.fehler, ['Produkte nicht lesbar: tabelle fehlt'])
        self.assertIn('Produkte nicht lesbar', protokoll.output[0])

    def test_bricht_die_seitenpruefung_ab_steht_der_abbruch_im_protokoll(self):
        befehl = _befehl(pruefe_seite.Command)
        with mock.patch.object(befehl, '_pruefe_seiten_mit', side_effect=RuntimeError('kaputt')), \
                self.assertLogs('shop1', level='ERROR') as protokoll:
            befehl._pruefe_ausgelieferte_seite()
        self.assertTrue(befehl.fehler[0].startswith('Die Prüfung der ausgelieferten Seite ist abgebrochen'))
        self.assertIn('Traceback', protokoll.output[0])


class PruefeLinksProtokollTest(SimpleTestCase):
    databases = {'default', 'pystore'}

    def test_bricht_die_verweispruefung_ab_steht_der_abbruch_im_protokoll(self):
        befehl = _befehl(pruefe_links.Command)
        with mock.patch.object(befehl, '_pruefe_mit', side_effect=RuntimeError('kaputt')), \
                self.assertLogs('shop1', level='ERROR') as protokoll:
            befehl._pruefe()
        self.assertTrue(befehl.fehler[0].startswith('Die Verweisprüfung ist abgebrochen'))
        self.assertIn('Traceback', protokoll.output[0])


class PruefeMailProtokollTest(SimpleTestCase):

    def test_keine_smtp_verbindung_steht_im_bericht_und_im_protokoll(self):
        befehl = _befehl(pruefe_mail.Command)
        verbindung = mock.Mock()
        verbindung.open.side_effect = OSError('Netz gesperrt')
        with mock.patch.object(pruefe_mail.Command, '_nutzt_smtp', return_value=True),\
                mock.patch.object(pruefe_mail, 'get_connection', return_value=verbindung),\
                self.assertLogs('shop1', level='WARNING') as protokoll:
            befehl._pruefe_smtp_anmeldung()
        self.assertIn('Keine SMTP-Verbindung', befehl.fehler[0])
        self.assertIn('Netz gesperrt', befehl.fehler[0])
        self.assertIn('keine SMTP-Verbindung', protokoll.output[0])

    def test_eine_abgewiesene_anmeldung_bleibt_ein_eigener_fall(self):
        """Der engere ``except`` davor fängt die Anmeldung – sie ist kein Netzfehler."""
        import smtplib
        befehl = _befehl(pruefe_mail.Command)
        verbindung = mock.Mock()
        verbindung.open.side_effect = smtplib.SMTPAuthenticationError(535, b'nein')
        with mock.patch.object(pruefe_mail.Command, '_nutzt_smtp', return_value=True),\
                mock.patch.object(pruefe_mail, 'get_connection', return_value=verbindung):
            befehl._pruefe_smtp_anmeldung()
        self.assertIn('weist die Anmeldung zurück', befehl.fehler[0])
        self.assertNotIn('Brevo', befehl.fehler[0])

    def test_eine_gescheiterte_testmail_steht_im_bericht_und_im_protokoll(self):
        befehl = _befehl(pruefe_mail.Command)
        with mock.patch.dict('os.environ', {'BREVO_API_KEY': ''}),\
                mock.patch('django.core.mail.EmailMultiAlternatives.send', side_effect=OSError('aus')),\
                self.assertLogs('shop1', level='WARNING') as protokoll:
            befehl._sende_testmail('niemand@example.invalid')
        self.assertIn('Testmail über SMTP gescheitert (OSError): aus', befehl.fehler[0])
        self.assertIn('Testmail über SMTP gescheitert', protokoll.output[0])

    def test_die_beschreibungen_der_befehle_sind_da(self):
        for klasse in (pruefe_seite.Command, pruefe_links.Command, pruefe_mail.Command):
            with self.subTest(befehl=klasse.__module__):
                self.assertTrue(klasse.__doc__ and klasse.__doc__.strip())
                self.assertTrue(klasse.help)
