"""Betriebsbefehle und Betriebsadressen direkt aufgerufen (PJ03, 02.10.2026).

``besucher_aufraeumen`` (EIG51) hatte keinen Test. ``pruefe_abwehr`` und
``views/betrieb.py`` waren nur über ``call_command('…')`` und über ihre Adressen
geprüft; hier werden ihre Funktionen zusätzlich unmittelbar aufgerufen –
``faelle()`` Fall für Fall und ``security_txt_text()`` ohne Umweg über die URL.
"""
import os
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import RequestFactory, override_settings
from django.utils import timezone

from shop1 import spamschutz
from shop1.management.commands import besucher_aufraeumen, pruefe_abwehr
from shop1.models import VisitorLog
from shop1.views import betrieb

from ._basis import LuviqTestCase


class BesucherAufraeumenTest(LuviqTestCase):
    """EIG51: alte Besuchereinträge der eigenen Seite verschwinden nach der Frist."""

    def _eintrag(self, tage_alt, seite='luviq'):
        eintrag = VisitorLog.objects.using('pystore').create(path='/', seite=seite)
        VisitorLog.objects.using('pystore').filter(pk=eintrag.pk).update(
            timestamp=timezone.now() - timedelta(days=tage_alt))
        return eintrag

    def _lauf(self, *argumente, umgebung=None):
        ausgabe = StringIO()
        with mock.patch.dict(os.environ, umgebung or {}, clear=False):
            if umgebung is None:
                os.environ.pop('BESUCHER_AUFBEWAHRUNG_TAGE', None)
            os.environ.setdefault('SITE_NAME', 'luviq')
            call_command(besucher_aufraeumen.Command(), *argumente, stdout=ausgabe)
        return ausgabe.getvalue()

    def test_ohne_frist_wird_nichts_geloescht(self):
        self._eintrag(400)
        text = self._lauf()
        self.assertIn('nichts gelöscht', text)
        self.assertIn(str(besucher_aufraeumen.VORSCHLAG_TAGE), text)
        self.assertEqual(VisitorLog.objects.using('pystore').count(), 1)

    def test_mit_frist_gehen_nur_alte_eintraege_der_eigenen_seite(self):
        self._eintrag(120)
        self._eintrag(10)
        self._eintrag(120, seite='pystore')
        text = self._lauf('--tage', '90')
        self.assertIn('1 Besuchereinträge', text)
        uebrig = VisitorLog.objects.using('pystore')
        self.assertEqual(uebrig.count(), 2)
        self.assertTrue(uebrig.filter(seite='pystore').exists())

    def test_trocken_zaehlt_nur(self):
        self._eintrag(120)
        text = self._lauf('--tage', '90', '--trocken')
        self.assertIn('trocken', text)
        self.assertEqual(VisitorLog.objects.using('pystore').count(), 1)

    def test_frist_aus_der_umgebung(self):
        self._eintrag(120)
        self._lauf(umgebung={'BESUCHER_AUFBEWAHRUNG_TAGE': '30'})
        self.assertEqual(VisitorLog.objects.using('pystore').count(), 0)

    def test_unsinnige_fristen_werden_abgewiesen(self):
        with self.assertRaises(CommandError):
            self._lauf('--tage', '0')
        with self.assertRaises(CommandError):
            self._lauf(umgebung={'BESUCHER_AUFBEWAHRUNG_TAGE': 'neunzig'})


class AbwehrFaelleTest(LuviqTestCase):
    """``pruefe_abwehr.faelle()`` Fall für Fall gegen ``spamschutz.bewerte``."""

    def test_jeder_fall_landet_auf_der_richtigen_seite_der_schwelle(self):
        jetzt = 1_800_000_000
        faelle = pruefe_abwehr.faelle(jetzt)
        self.assertTrue(any(soll for _, _, soll in faelle))
        self.assertTrue(any(not soll for _, _, soll in faelle))
        for bezeichnung, daten, soll_geblockt in faelle:
            with self.subTest(bezeichnung):
                punkte, _ = spamschutz.bewerte(daten, jetzt)
                self.assertEqual(punkte >= spamschutz.SCHWELLE, soll_geblockt)


class BetriebFunktionenTest(LuviqTestCase):
    """``views/betrieb.py`` ohne Umweg über die Adressen."""

    @override_settings(SECURITY_TXT_EXPIRES='2027-06-30T00:00:00Z')
    def test_security_txt_text_hat_die_pflichtfelder(self):
        anfrage = RequestFactory().get('/.well-known/security.txt', HTTP_HOST='testserver')
        text = betrieb.security_txt_text(anfrage)
        self.assertIn('Contact: mailto:', text)
        self.assertIn('Expires: 2027-06-30T00:00:00Z', text)
        self.assertIn('/.well-known/security.txt', text)

    def test_gesundheit_antwortet_ok(self):
        antwort = betrieb.gesundheit(RequestFactory().get('/health/'))
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.content, b'ok')
