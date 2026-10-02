"""Betrieb und Sicherheit der Auslieferung (Paket L2-B1, 02.10.2026).

Permissions-Policy (SI07, VL04), Content-Security-Policy ohne ``'unsafe-eval'``
und ohne Fremdhost (SI09, PF31), Gesundheitsadresse (BT11), ``security.txt``
(SI25, EIG60), Urheberrechtsangabe (RE13) und die öffentliche Adresse für
``canonical``, Sitemap und ``robots.txt``.
"""
import hashlib
import re
from datetime import date
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.db import DatabaseError
from django.test import override_settings

from ._basis import OEFFENTLICHE_SEITEN, LuviqTestCase

WURZEL = Path(__file__).resolve().parents[2]


class PermissionsPolicyTest(LuviqTestCase):
    """SI07 / VL04: Geräterechte, die die Seite nie braucht, sind aus."""

    def test_jede_oeffentliche_seite_traegt_die_permissions_policy(self):
        """Verhindert die Rückkehr zum Zustand vom 01.10.2026: keine
        ``Permissions-Policy`` auf 15 von 15 Seiten."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                wert = self.hole(pfad)['Permissions-Policy']
                for merkmal in ('geolocation=()', 'camera=()', 'microphone=()',
                                'usb=()', 'browsing-topics=()'):
                    self.assertIn(merkmal, wert)

    def test_die_kasse_behaelt_das_zahlungsfenster(self):
        """Verhindert, dass ``payment=()`` den Kauf nach dem Einschalten des
        Verkaufs bricht: die eigene Seite und PayPal bleiben berechtigt."""
        wert = self.hole('/')['Permissions-Policy']
        self.assertIn('payment=(self "https://*.paypal.com")', wert)

    def test_auch_text_antworten_tragen_sie(self):
        self.assertIn('geolocation=()', self.hole('/robots.txt')['Permissions-Policy'])

    def test_eine_selbst_gesetzte_kopfzeile_bleibt(self):
        from django.http import HttpResponse

        from ..middleware import PermissionsPolicyMiddleware

        def ansicht(request):
            antwort = HttpResponse('x')
            antwort['Permissions-Policy'] = 'camera=(self)'
            return antwort

        antwort = PermissionsPolicyMiddleware(ansicht)(mock.Mock())
        self.assertEqual(antwort['Permissions-Policy'], 'camera=(self)')


class ContentSecurityPolicyOhneEvalTest(LuviqTestCase):
    """SI09 / PF31: kein ``'unsafe-eval'``, kein Fremdhost außer PayPal."""

    def test_script_src_enthaelt_weder_eval_noch_jsdelivr(self):
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                csp = self.hole(pfad)['Content-Security-Policy']
                script_src = next(t for t in csp.split('; ') if t.startswith('script-src'))
                self.assertNotIn('unsafe-eval', script_src)
                self.assertNotIn('jsdelivr', script_src)
                self.assertNotIn('unsafe-inline', script_src)

    def test_keine_vorlage_laedt_etwas_von_einem_cdn_oder_nutzt_alpine(self):
        """Verhindert, dass ein Fremdabruf oder ein Alpine-Ausdruck still
        zurückkehrt – Alpine liefe ohne ``'unsafe-eval'`` ohnehin nicht."""
        vorlagen = list((WURZEL / 'templates').rglob('*.html')) + \
            list((WURZEL / 'shop1' / 'templates').rglob('*.html'))
        self.assertGreater(len(vorlagen), 30)
        for vorlage in vorlagen:
            text = vorlage.read_text(encoding='utf-8')
            with self.subTest(vorlage=vorlage.name):
                self.assertNotRegex(text, r'<script[^>]+src="https?://(?!(?:www\.)?paypal)')
                # Attributform (x-data="…", x-show="…", x-intersect.once="…"); ein
                # Erwähnen im Kommentar („Alpine-x-show“) zählt nicht.
                self.assertNotRegex(text, r'\sx-(?:data|show|intersect|init|collapse)[.=\s>]')
                self.assertNotIn('cdn.jsdelivr.net', text)

    def test_chart_js_liegt_im_projekt_und_ist_unveraendert(self):
        """Chart.js 4.4.0 stammt aus dem npm-Tarball (``dist/chart.umd.js``,
        npm-Integrität ``sha512-vQEj6d+z…`` am 02.10.2026 gegen die Datei der
        Registry geprüft). Einzige Änderung: die letzte Zeile
        ``//# sourceMappingURL=…`` ist entfernt – die Map liegt nicht im
        Projekt, und ManifestStaticFilesStorage scheiterte an dem Verweis.
        Dieser SHA-256 der Datei hält fest, dass niemand sie unbemerkt ändert."""
        datei = WURZEL / 'shop1' / 'static' / 'shop1' / 'chart-4.4.0.umd.js'
        self.assertEqual(
            hashlib.sha256(datei.read_bytes()).hexdigest(),
            '4189ade3d07862981d2a92e0629d48a83ae840260122bc1fac01094e4b1c0aa2',
        )
        self.assertIn(b'Chart.js v4.4.0', datei.read_bytes()[:200])

    def test_die_seitenskripte_liegen_auf_der_eigenen_adresse(self):
        html = self.hole('/gaestebuch/').content.decode()
        self.assertRegex(html, r'<script defer src="/static/shop1/luviq[^"]*\.js"></script>')


class CsrfCookieTest(LuviqTestCase):
    """SI16: das CSRF-Cookie trägt HttpOnly; Skripte lesen das Token aus dem <meta>."""

    def test_das_csrf_cookie_ist_httponly(self):
        self.assertTrue(settings.CSRF_COOKIE_HTTPONLY)

    def test_kein_skript_liest_das_token_aus_dem_cookie(self):
        """Verhindert, dass die Newsletter-Anmeldung der Startseite wieder
        ``document.cookie`` liest – bei HttpOnly bekäme sie ein leeres Token
        und jede Anmeldung scheiterte mit 403."""
        for ordner in (WURZEL / 'templates', WURZEL / 'shop1' / 'templates', WURZEL / 'shop1' / 'static'):
            for datei in list(ordner.rglob('*.html')) + list(ordner.rglob('luviq.js')):
                with self.subTest(datei=datei.name):
                    self.assertNotIn('document.cookie', datei.read_text(encoding='utf-8'))

    def test_die_startseite_traegt_das_token_im_meta(self):
        html = self.hole('/').content.decode()
        self.assertRegex(html, r'<meta name="csrf-token" content="[A-Za-z0-9]{20,}">')
        self.assertIn("meta[name=\"csrf-token\"]", html)


