"""``shop1/views/motiv.py`` direkt: Prüfung, Doppelsperre, Mailtext, Empfänger.

``test_motivanfrage`` geht über das Formular; hier stehen die Hilfsfunktionen
einzeln, damit ein Fehler an der Prüfung nicht erst als „Seite antwortet
anders“ auffällt.
"""

from unittest import mock

from django.test import SimpleTestCase, override_settings

from ..models import Motivanfrage
from ..views import motiv
from ._basis import LuviqTestCase

GUELTIG = {'richtung': 'tier', 'teil': 'hoodie', 'platzierung': 'ruecken',
           'bedeutung': 'Ein Drache.', 'instagram': '@erika.muster', 'email': ''}


class PruefeTest(SimpleTestCase):

    def test_eine_gueltige_eingabe_wird_bereinigt(self):
        werte, fehler = motiv.pruefe(dict(GUELTIG, bedeutung='  Ein Drache.  '))
        self.assertIsNone(fehler)
        self.assertEqual((werte['instagram'], werte['bedeutung']), ('erika.muster', 'Ein Drache.'))

    def test_jede_auswahl_ist_pflicht_und_nur_aus_der_liste(self):
        for feld in ('richtung', 'teil', 'platzierung'):
            for wert in ('', 'erfunden'):
                with self.subTest(feld=feld, wert=wert):
                    _, fehler = motiv.pruefe(dict(GUELTIG, **{feld: wert}))
                    self.assertTrue(fehler)

    def test_ohne_kontakt_gibt_es_keine_antwortmoeglichkeit(self):
        _, fehler = motiv.pruefe(dict(GUELTIG, instagram='', email=''))
        self.assertIn('Instagram', fehler)

    def test_instagram_nur_im_muster_der_plattform(self):
        for ok in ('erika', '@erika.muster', 'a_b.c9'):
            with self.subTest(ok=ok):
                self.assertIsNone(motiv.pruefe(dict(GUELTIG, instagram=ok))[1])
        for schlecht in ('mit leerzeichen', 'x' * 32, 'https://instagram.com/x', '@@x'):
            with self.subTest(schlecht=schlecht):
                self.assertTrue(motiv.pruefe(dict(GUELTIG, instagram=schlecht))[1])

    def test_die_mailadresse_wird_geprueft(self):
        self.assertTrue(motiv.pruefe(dict(GUELTIG, instagram='', email='kein-at'))[1])
        self.assertIsNone(motiv.pruefe(dict(GUELTIG, instagram='', email='erika@example.invalid'))[1])

    def test_die_grenzen_der_freitexte_gelten_mit_zeilenumbruch_als_ein_zeichen(self):
        grenze = motiv.LAENGEN['bedeutung']
        self.assertIsNone(motiv.pruefe(dict(GUELTIG, bedeutung='a\r\n' * (grenze // 2)))[1])
        self.assertTrue(motiv.pruefe(dict(GUELTIG, bedeutung='a' * (grenze + 1)))[1])

    def test_fehlende_felder_sind_leer_nicht_ein_fehler_im_programm(self):
        werte, fehler = motiv.pruefe({})
        self.assertTrue(fehler)
        self.assertEqual(werte['richtung'], '')


class DoppeltSchluesselTest(SimpleTestCase):

    def test_gleiche_eingabe_gleicher_schluessel_unabhaengig_von_der_schreibweise(self):
        a = motiv._doppelt_schluessel(dict(GUELTIG))
        self.assertEqual(a, motiv._doppelt_schluessel(dict(GUELTIG, bedeutung='EIN DRACHE.')))
        self.assertNotEqual(a, motiv._doppelt_schluessel(dict(GUELTIG, teil='jeans')))
        self.assertTrue(a.startswith('motiv-doppelt:'))
        self.assertNotIn('Drache', a)


class EmpfaengerTest(SimpleTestCase):

    @override_settings(MOTIV_EMPFAENGER='atelier@example.invalid')
    def test_der_eigene_empfaenger_hat_vorrang(self):
        self.assertEqual(motiv.empfaenger(), 'atelier@example.invalid')

    @override_settings(MOTIV_EMPFAENGER='', DEFAULT_FROM_EMAIL='absender@example.invalid')
    def test_sonst_admin_email_und_zuletzt_der_absender(self):
        with mock.patch.dict('os.environ', {'ADMIN_EMAIL': 'luisa@example.invalid'}):
            self.assertEqual(motiv.empfaenger(), 'luisa@example.invalid')
        with mock.patch.dict('os.environ', clear=False) as umgebung:
            umgebung.pop('ADMIN_EMAIL', None)
            self.assertEqual(motiv.empfaenger(), 'absender@example.invalid')


class MailTextTest(LuviqTestCase):

    def anfrage(self, **felder):
        return Motivanfrage(**dict(GUELTIG, **dict({'instagram': 'erika.muster'}, **felder)))

    def test_betreff_felder_und_text_nennen_die_angaben(self):
        betreff, html, text = motiv._mail(self.anfrage(email='erika@example.invalid'))
        self.assertEqual(betreff, 'Motivanfrage: Tier auf Hoodie')
        for stueck in ('Richtung: Tier', 'Teil: Hoodie', '@erika.muster', 'erika@example.invalid'):
            self.assertIn(stueck, text)
        self.assertIn('Admin-Panel', text)

    def test_ohne_angabe_steht_ein_strich_und_kein_at_allein(self):
        _, _, text = motiv._mail(self.anfrage(instagram='', email='x@example.invalid'))
        self.assertIn('Instagram: –', text)

    def test_die_felder_markieren_instagram_und_mail_als_verweis(self):
        felder = motiv._felder(self.anfrage(email='e@example.invalid'))
        self.assertEqual([f[2] for f in felder if len(f) == 3], ['insta', 'mail'])
        self.assertEqual(felder[3][1], '@erika.muster')

    def test_nutzertext_steht_maskiert_im_html(self):
        _, html, _ = motiv._mail(self.anfrage(bedeutung='<script>x()</script>'))
        self.assertNotIn('<script>x()', html)


class SeiteTest(LuviqTestCase):

    def test_die_danke_seite_wird_nie_zwischengespeichert(self):
        antwort = self.hole('/motiv-anfragen/danke/')
        self.assertIn('no-cache', antwort['Cache-Control'])
