"""Texte und Werte aus ``shop1/luviq_daten.py`` – direkt, nicht über die Seiten.

Die Seitentests (``test_inhalt``, ``test_geo``) prüfen, was der Besucher liest.
Hier steht, was die Funktionen selbst zusagen: der Drop-Termin ist ein
Zeitpunkt oder ``None`` (nie ein Fehler), die Nummer kollidiert nie mit dem
Archiv, und die Auswahllisten der Motivanfrage haben stabile Schlüssel.
"""

from datetime import datetime, timedelta, timezone as utc
from unittest import mock

from django.db import DatabaseError
from django.test import SimpleTestCase
from django.utils import timezone

from .. import luviq_daten
from ._basis import LuviqTestCase, erzeuge_produkt

JETZT = datetime(2026, 10, 2, 12, 0, tzinfo=utc.utc)


class DropTerminTest(SimpleTestCase):

    def test_ein_kuenftiger_termin_kommt_als_zeitpunkt_zurueck(self):
        with mock.patch.dict('os.environ', {'DROP_TERMIN': '2026-10-08T18:00+02:00'}):
            termin = luviq_daten.drop_termin(JETZT)
        self.assertEqual(termin, datetime(2026, 10, 8, 16, 0, tzinfo=utc.utc))

    def test_leer_unlesbar_oder_abgelaufen_heisst_kein_termin(self):
        """Verhindert einen Countdown ins Leere: lieber „in Arbeit“."""
        for roh in ('', '   ', 'bald', '2026-13-45', '2026-10-01T18:00+02:00'):
            with self.subTest(roh=roh), mock.patch.dict('os.environ', {'DROP_TERMIN': roh}):
                self.assertIsNone(luviq_daten.drop_termin(JETZT))

    def test_ein_termin_ohne_zone_gilt_in_berliner_zeit(self):
        with mock.patch.dict('os.environ', {'DROP_TERMIN': '2026-10-08T18:00'}):
            termin = luviq_daten.drop_termin(JETZT)
        self.assertEqual(timezone.localtime(termin).hour, 18)

    def test_der_termintext_nennt_wochentag_datum_und_uhrzeit(self):
        donnerstag = datetime(2026, 10, 8, 16, 0, tzinfo=utc.utc)   # 18:00 Berlin
        self.assertEqual(luviq_daten.termin_text(donnerstag), 'Donnerstag, 08.10., 18 Uhr')
        halb = datetime(2026, 10, 8, 16, 30, tzinfo=utc.utc)
        self.assertEqual(luviq_daten.termin_text(halb), 'Donnerstag, 08.10., 18:30 Uhr')

    def test_das_laufband_nennt_ohne_termin_keine_ausgabe(self):
        ohne = luviq_daten.laufband('006', None)
        self.assertEqual(ohne[1], 'Die nächste Ausgabe ist in Arbeit')
        mit = luviq_daten.laufband('006', datetime(2026, 10, 8, 16, 0, tzinfo=utc.utc))
        self.assertIn('Nº 006 erscheint Donnerstag, 08.10., 18 Uhr', mit)
        self.assertEqual(ohne[0], mit[0])
        self.assertEqual(len(ohne), 3)


class DropKontextTest(LuviqTestCase):

    def test_mit_termin_laeuft_der_countdown_in_zweistelligen_teilen(self):
        jetzt = datetime(2026, 10, 8, 16, 0, tzinfo=utc.utc) - timedelta(days=2, hours=3, minutes=4, seconds=5)
        with mock.patch.dict('os.environ', {'DROP_TERMIN': '2026-10-08T18:00+02:00', 'DROP_NUMMER': '6'}):
            kontext = luviq_daten.drop_kontext(jetzt)
        self.assertEqual(kontext['rest'], {'d': '02', 'h': '03', 'm': '04', 's': '05'})
        self.assertEqual(kontext['nummer'], '006')
        self.assertEqual(kontext['monat'], 'Oktober 2026')
        self.assertEqual(kontext['termin_text'], 'Donnerstag, 08.10., 18 Uhr')
        self.assertTrue(kontext['termin_iso'].startswith('2026-10-08T18:00'))

    def test_ohne_termin_gibt_es_keine_uhr_und_den_monat_von_jetzt(self):
        with mock.patch.dict('os.environ', {'DROP_TERMIN': '', 'DROP_NUMMER': ''}):
            kontext = luviq_daten.drop_kontext(JETZT)
        self.assertEqual((kontext['rest'], kontext['termin'], kontext['termin_iso'],
                          kontext['termin_text']), ({}, None, '', ''))
        self.assertEqual(kontext['monat'], 'Oktober 2026')
        self.assertEqual(kontext['teaser'], luviq_daten.TEASER)


class DropNummerTest(LuviqTestCase):

    def test_eine_feste_nummer_wird_dreistellig(self):
        with mock.patch.dict('os.environ', {'DROP_NUMMER': '7'}):
            self.assertEqual(luviq_daten.drop_nummer(), '007')

    def test_das_vorab_angelegte_drop_stueck_nennt_seine_eigene_nummer(self):
        """EIG123: Der Countdown nennt die Nummer des hochgeladenen Drop-Stücks
        (kleinste Nummer über dem Archiv), nicht die übernächste."""
        erzeuge_produkt('Eins', vergeben=True)
        zwei = erzeuge_produkt('Zwei', vergeben=True)
        drop = erzeuge_produkt('Drop')
        erzeuge_produkt('Danach')
        with mock.patch.dict('os.environ', {'DROP_NUMMER': ''}):
            self.assertEqual(luviq_daten.drop_nummer(), f'{drop.nummer:03d}')
        self.assertEqual(drop.nummer, zwei.nummer + 1)

    def test_ohne_drop_stueck_kommt_die_naechste_freie_archivnummer(self):
        """Verhindert, dass der Drop eine Nummer bekommt, die im Archiv schon vergeben ist."""
        erzeuge_produkt('Eins', vergeben=True)
        zwei = erzeuge_produkt('Zwei', vergeben=True)
        with mock.patch.dict('os.environ', {'DROP_NUMMER': ''}):
            self.assertEqual(luviq_daten.drop_nummer(), f'{zwei.nummer + 1:03d}')

    def test_eine_unlesbare_feste_nummer_faellt_auf_das_archiv_zurueck(self):
        with mock.patch.dict('os.environ', {'DROP_NUMMER': 'sechs'}):
            self.assertEqual(luviq_daten.drop_nummer(), '001')

    def test_eine_nicht_lesbare_tabelle_laesst_die_seite_nicht_abstuerzen(self):
        """Verhindert einen 500 auf jeder Seite (Kontextprozessor), wenn die
        Datenbank gerade nicht antwortet; der Fehler steht im Protokoll."""
        with mock.patch.dict('os.environ', {'DROP_NUMMER': ''}), \
                mock.patch('shop1.models.Produkt.objects') as objekte, \
                self.assertLogs('shop1', level='WARNING') as protokoll:
            objekte.filter.side_effect = DatabaseError('kaputt')
            self.assertEqual(luviq_daten.drop_nummer(), '001')
        self.assertIn('Archivnummern nicht lesbar', protokoll.output[0])

    def test_ein_anderer_fehler_wird_nicht_verschluckt(self):
        with mock.patch.dict('os.environ', {'DROP_NUMMER': ''}), \
                mock.patch('shop1.models.Produkt.objects') as objekte:
            objekte.filter.side_effect = RuntimeError('Programmfehler')
            with self.assertRaises(RuntimeError):
                luviq_daten.drop_nummer()


class AuswahllistenTest(SimpleTestCase):

    def test_schluessel_sind_eindeutig_und_das_modell_zeigt_ihre_namen(self):
        from ..models import Motivanfrage
        for liste, feld in ((luviq_daten.RICHTUNGEN, 'richtung'), (luviq_daten.TEILE, 'teil'),
                            (luviq_daten.PLATZIERUNGEN, 'platzierung')):
            with self.subTest(feld=feld):
                schluessel = [s for s, _ in liste]
                self.assertEqual(len(schluessel), len(set(schluessel)))
                for schluessel_, name in liste:
                    anfrage = Motivanfrage(**{feld: schluessel_})
                    self.assertEqual(getattr(anfrage, f'get_{feld}_display')(), name)

    def test_die_stationen_und_schritte_haben_text(self):
        for station in luviq_daten.ANFRAGE_STATIONEN + luviq_daten.ANFRAGE_ABLAUF:
            self.assertTrue(all(teil.strip() for teil in station))
        self.assertEqual(len(luviq_daten.SCHRITTE), 5)
        for titel, text, bild, alt in luviq_daten.SCHRITTE:
            self.assertTrue(titel and text and bild and alt)

    def test_keine_zusage_und_kein_preis_in_den_festen_texten(self):
        """Ohne Gewerbe: Dauer ist ein Erfahrungswert, nichts davon ein Preis."""
        alles = ' '.join([luviq_daten.LEAD, luviq_daten.DAUER, luviq_daten.MARKENSATZ]
                         + [t for s in luviq_daten.ANFRAGE_STATIONEN for t in s])
        for wort in ('€', 'Euro', 'Preis', 'kaufen', 'garantiert'):
            with self.subTest(wort=wort):
                self.assertNotIn(wort, alles)
