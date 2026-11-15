"""Der Verkaufsschalter als Baustein: ``shop1/verkauf.py`` direkt.

``test_verkauf`` prüft die Seiten in beiden Zuständen; hier stehen die drei
Bausteine selbst – ``verkauf_aktiv``, der Kontextprozessor und die
Middleware –, damit eine Änderung an ihnen nicht erst an einer Seite auffällt.
"""

import json
from unittest import mock

from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from .. import verkauf


def _anfrage(url_name):
    anfrage = RequestFactory().get('/x/')
    anfrage.session = {}
    anfrage._messages = FallbackStorage(anfrage)
    anfrage.resolver_match = mock.Mock(url_name=url_name) if url_name else None
    return anfrage


def _middleware():
    return verkauf.VerkaufsschalterMiddleware(lambda anfrage: HttpResponse('ok'))


class SchalterTest(SimpleTestCase):

    @override_settings(VERKAUF_AKTIV=False, ANFRAGESHOP=False)
    def test_aus_ist_aus(self):
        self.assertFalse(verkauf.verkauf_aktiv())
        self.assertEqual(verkauf.verkauf_kontext(None), {'verkauf_aktiv': False, 'shop_oeffnet': verkauf.oeffnungs_satz(),
                          'verkauf_ab': verkauf.verkauf_ab(),
                          'direktkauf_aktiv': False, 'anfrage_shop': False, 'shop_sichtbar': False})

    @override_settings(VERKAUF_AKTIV=True, ANFRAGESHOP=False)
    def test_an_ist_an(self):
        self.assertTrue(verkauf.verkauf_aktiv())
        self.assertEqual(verkauf.verkauf_kontext(None), {'verkauf_aktiv': True, 'shop_oeffnet': '', 'verkauf_ab': '',
                          'direktkauf_aktiv': True, 'anfrage_shop': False, 'shop_sichtbar': True})

    @override_settings(VERKAUF_AKTIV=True, ANFRAGESHOP=True)
    def test_an_mit_anfrageshop(self):
        self.assertTrue(verkauf.verkauf_kontext(None)['anfrage_shop'])

    @override_settings(VERKAUF_AKTIV=False, ANFRAGESHOP=True)
    def test_anfrageshop_haengt_nicht_am_verkauf(self):
        """Bastian 14.11.2026: Startsperre gilt nur für den Kaufweg, der Anfrage-Shop läuft auch ohne Verkauf."""
        kontext = verkauf.verkauf_kontext(None)
        self.assertTrue(kontext['anfrage_shop'])
        self.assertTrue(kontext['shop_sichtbar'])
        self.assertFalse(kontext['verkauf_aktiv'])
        self.assertEqual(kontext['shop_oeffnet'], '')

    def test_fehlt_die_einstellung_ist_der_verkauf_aus(self):
        """Rechtslage: ohne ausdrückliches Einschalten wird nie verkauft."""
        from django.conf import settings
        with override_settings():
            del settings.VERKAUF_AKTIV
            self.assertFalse(verkauf.verkauf_aktiv())

    def test_die_vorgabe_der_einstellungen_ist_aus(self):
        """Kein Gewerbe angemeldet: der Schalter steht in dieser Suite auf aus."""
        from django.conf import settings
        self.assertFalse(settings.VERKAUF_AKTIV)


class MiddlewareTest(SimpleTestCase):

    @override_settings(VERKAUF_AKTIV=False, ANFRAGESHOP=False)
    def test_jede_kaufroute_wird_zur_warteliste_umgeleitet_ohne_die_view_zu_rufen(self):
        for name in sorted(verkauf.KAUFROUTEN):
            with self.subTest(route=name):
                anfrage = _anfrage(name)
                antwort = _middleware().process_view(anfrage, mock.Mock(), (), {})
                self.assertEqual(antwort.status_code, 302)
                self.assertEqual(antwort['Location'], '/#newsletter-form')
                self.assertEqual([str(m) for m in anfrage._messages], [verkauf.hinweis()])

    @override_settings(VERKAUF_AKTIV=False, ANFRAGESHOP=False)
    def test_der_paypal_abruf_bekommt_json_mit_status_409(self):
        """Ein ``fetch`` kann mit einer HTML-Weiterleitung nichts anfangen."""
        antwort = _middleware().process_view(_anfrage('paypal_capture'), mock.Mock(), (), {})
        self.assertEqual(antwort.status_code, 409)
        self.assertEqual(json.loads(antwort.content),
                         {'error': verkauf.hinweis(), 'verkauf_aktiv': False})

    @override_settings(VERKAUF_AKTIV=False, ANFRAGESHOP=False)
    def test_andere_routen_und_unaufgeloeste_adressen_bleiben_unberuehrt(self):
        for name in ('home', 'kontakt', 'login', 'admin_dashboard', None):
            with self.subTest(route=name):
                self.assertIsNone(_middleware().process_view(_anfrage(name), mock.Mock(), (), {}))

    @override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=False, ANFRAGESHOP=False)
    def test_mit_verkauf_geht_alles_durch(self):
        for name in sorted(verkauf.KAUFROUTEN | verkauf.KAUFROUTEN_JSON):
            with self.subTest(route=name):
                self.assertIsNone(_middleware().process_view(_anfrage(name), mock.Mock(), (), {}))

    @override_settings(VERKAUF_AKTIV=False, ANFRAGESHOP=True)
    def test_anfrageshop_sperrt_den_kaufweg_auch_ohne_verkauf(self):
        for name in sorted(verkauf.KAUFROUTEN | verkauf.ANFRAGESHOP_GESPERRT):
            with self.subTest(route=name):
                antwort = _middleware().process_view(_anfrage(name), mock.Mock(), (), {})
                self.assertEqual(antwort.status_code, 302)
                self.assertEqual(antwort['Location'], '/produkte/')
        antwort = _middleware().process_view(_anfrage('paypal_capture'), mock.Mock(), (), {})
        self.assertEqual(antwort.status_code, 409)
        self.assertEqual(_middleware().process_view(_anfrage('register'), mock.Mock(), (), {}).status_code, 302)
        for name in ('home', 'kontakt', 'login', 'admin_dashboard', 'produkte', None):
            with self.subTest(route=name):
                self.assertIsNone(_middleware().process_view(_anfrage(name), mock.Mock(), (), {}))

    def test_der_aufruf_reicht_die_anfrage_unveraendert_weiter(self):
        self.assertEqual(_middleware()(_anfrage('home')).content, b'ok')

    def test_der_hinweis_nennt_weder_preis_noch_kauf(self):
        for wort in ('€', 'Preis', 'kaufen', 'bestellen', 'verkauft'):
            with self.subTest(wort=wort):
                self.assertNotIn(wort, verkauf.hinweis())
        self.assertTrue(verkauf.WARTELISTE_ANKER.startswith('#'))
