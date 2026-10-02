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

    @override_settings(VERKAUF_AKTIV=False)
    def test_aus_ist_aus(self):
        self.assertFalse(verkauf.verkauf_aktiv())
        self.assertEqual(verkauf.verkauf_kontext(None), {'verkauf_aktiv': False})

    @override_settings(VERKAUF_AKTIV=True)
    def test_an_ist_an(self):
        self.assertTrue(verkauf.verkauf_aktiv())
        self.assertEqual(verkauf.verkauf_kontext(None), {'verkauf_aktiv': True})

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

    @override_settings(VERKAUF_AKTIV=False)
    def test_jede_kaufroute_wird_zur_warteliste_umgeleitet_ohne_die_view_zu_rufen(self):
        for name in sorted(verkauf.KAUFROUTEN):
            with self.subTest(route=name):
                anfrage = _anfrage(name)
                antwort = _middleware().process_view(anfrage, mock.Mock(), (), {})
                self.assertEqual(antwort.status_code, 302)
                self.assertEqual(antwort['Location'], '/#newsletter-form')
                self.assertEqual([str(m) for m in anfrage._messages], [verkauf.HINWEIS])

    @override_settings(VERKAUF_AKTIV=False)
    def test_der_paypal_abruf_bekommt_json_mit_status_409(self):
        """Ein ``fetch`` kann mit einer HTML-Weiterleitung nichts anfangen."""
        antwort = _middleware().process_view(_anfrage('paypal_capture'), mock.Mock(), (), {})
        self.assertEqual(antwort.status_code, 409)
        self.assertEqual(json.loads(antwort.content),
                         {'error': verkauf.HINWEIS, 'verkauf_aktiv': False})

    @override_settings(VERKAUF_AKTIV=False)
    def test_andere_routen_und_unaufgeloeste_adressen_bleiben_unberuehrt(self):
        for name in ('home', 'kontakt', 'login', 'admin_dashboard', None):
            with self.subTest(route=name):
                self.assertIsNone(_middleware().process_view(_anfrage(name), mock.Mock(), (), {}))

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_geht_alles_durch(self):
        for name in sorted(verkauf.KAUFROUTEN | verkauf.KAUFROUTEN_JSON):
            with self.subTest(route=name):
                self.assertIsNone(_middleware().process_view(_anfrage(name), mock.Mock(), (), {}))

    def test_der_aufruf_reicht_die_anfrage_unveraendert_weiter(self):
        self.assertEqual(_middleware()(_anfrage('home')).content, b'ok')

    def test_der_hinweis_nennt_weder_preis_noch_kauf(self):
        for wort in ('€', 'Preis', 'kaufen', 'bestellen', 'verkauft'):
            with self.subTest(wort=wort):
                self.assertNotIn(wort, verkauf.HINWEIS)
        self.assertTrue(verkauf.WARTELISTE_ANKER.startswith('#'))
