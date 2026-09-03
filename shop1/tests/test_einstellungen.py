"""Die Einstellungen im Betriebsmodus.

Fast jede Sicherheitseinstellung dieses Projekts hängt am ``DEBUG``-Schalter
(``mainweb/settings.py``). Ein versehentliches ``DEBUG=True`` in der
Betriebsumgebung schaltet in einem Zug HSTS, die HTTPS-Weiterleitung, sichere
Cookies und die Hostprüfung ab – ohne dass die Seite anders aussähe. Die Tests
hier laden die Einstellungsdatei mit gesetzten Umgebungsvariablen ein zweites
Mal und prüfen das Ergebnis, statt sich auf den gerade geladenen Zustand zu
verlassen.
"""

import importlib.util
import os
import re
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit

from django.conf import settings
from django.test import modify_settings, override_settings

from ..models import Comment, PageVisit, Produkt, VisitorLog, Werbung
from ..routers import WerbungRouter
from ._basis import ADMIN_SEITEN, OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_produkt

_SETTINGS_PFAD = Path(settings.BASE_DIR) / 'mainweb' / 'settings.py'

#: Umgebung einer echten Railway-Bereitstellung, so weit sie für die
#: Sicherheitseinstellungen zählt.
BETRIEBSUMGEBUNG = {
    'DEBUG': 'False',
    'SECRET_KEY': 'ein-zufaelliger-schluessel-nur-fuer-diesen-test',
    'ALLOWED_HOSTS_EXTRA': 'https://www.luviq-alsfeld.com/',
}


def lade_einstellungen(umgebung):
    """Führt ``mainweb/settings.py`` mit gesetzter Umgebung erneut aus.

    Bewusst unter eigenem Modulnamen: der laufende Testprozess behält seine
    Einstellungen, geprüft wird eine frische Auswertung der Datei.
    """
    spezifikation = importlib.util.spec_from_file_location(
        'mainweb._einstellungspruefung', _SETTINGS_PFAD
    )
    modul = importlib.util.module_from_spec(spezifikation)
    with mock.patch.dict(os.environ, umgebung, clear=False):
        spezifikation.loader.exec_module(modul)
    return modul


class BetriebsmodusTest(LuviqTestCase):
    """Was gelten muss, sobald ``DEBUG`` aus ist."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.betrieb = lade_einstellungen(BETRIEBSUMGEBUNG)

    def test_debug_ist_aus(self):
        """Verhindert, dass Besucher bei einem Fehler den vollständigen
        Programmablauf samt Einstellungen zu sehen bekommen."""
        self.assertFalse(self.betrieb.DEBUG)

    def test_sitzungs_und_csrf_cookies_werden_nur_ueber_https_gesendet(self):
        """Verhindert, dass ein Sitzungs-Cookie über eine unverschlüsselte
        Verbindung mitgelesen und das Konto übernommen werden kann."""
        self.assertTrue(self.betrieb.SESSION_COOKIE_SECURE)
        self.assertTrue(self.betrieb.CSRF_COOKIE_SECURE)
        self.assertTrue(self.betrieb.SESSION_COOKIE_HTTPONLY)

    def test_https_wird_erzwungen_und_per_hsts_vorgemerkt(self):
        """Verhindert, dass ein Erstaufruf über HTTP abgefangen wird, bevor die
        Weiterleitung greift."""
        self.assertTrue(self.betrieb.SECURE_SSL_REDIRECT)
        self.assertGreaterEqual(self.betrieb.SECURE_HSTS_SECONDS, 31536000)
        self.assertTrue(self.betrieb.SECURE_HSTS_INCLUDE_SUBDOMAINS)

    def test_die_hostliste_ist_nicht_offen(self):
        """Verhindert Host-Header-Angriffe: mit ``ALLOWED_HOSTS = ['*']``
        beantwortet die Seite Anfragen unter jedem beliebigen Namen und baut
        Links und Bestätigungsmails auf einen fremden Host."""
        self.assertNotIn('*', self.betrieb.ALLOWED_HOSTS)
        self.assertIn('www.luviq-alsfeld.com', self.betrieb.ALLOWED_HOSTS)
        self.assertIn('luviq-alsfeld.com', self.betrieb.ALLOWED_HOSTS)

    def test_unsicherer_secret_key_bricht_den_start_ab(self):
        """Verhindert das Ausliefern mit dem mitgelieferten Beispielschlüssel –
        damit liessen sich Sitzungen und Passwort-Rücksetzlinks fälschen."""
        with self.assertRaises(RuntimeError):
            lade_einstellungen(dict(BETRIEBSUMGEBUNG,
                                    SECRET_KEY='django-insecure-CHANGE_THIS_IN_PRODUCTION'))

    def test_ohne_debug_variable_gilt_der_betriebsmodus_samt_startschutz(self):
        """Verhindert, dass die Vorgabe kippt: fehlt ``DEBUG`` in der Umgebung
        (der Normalfall in Railway), muss der Betriebsmodus gelten – und der
        Startschutz muss auch dann greifen. Eine Vorgabe ``DEBUG=True`` wäre
        der teuerste Ein-Zeilen-Fehler des Projekts, denn kein Test und keine
        Prüfung würde ihn vor dem Deploy sehen."""
        ohne_debug = {k: v for k, v in BETRIEBSUMGEBUNG.items() if k != 'DEBUG'}
        ohne_debug['DEBUG'] = ''   # leer = nicht gesetzt; .env darf nicht nachfüllen
        betrieb = lade_einstellungen(ohne_debug)
        self.assertFalse(betrieb.DEBUG)
        self.assertTrue(betrieb.SECURE_SSL_REDIRECT)
        with self.assertRaises(RuntimeError):
            lade_einstellungen(dict(ohne_debug,
                                    SECRET_KEY='django-insecure-CHANGE_THIS_IN_PRODUCTION'))

    def test_der_kanonische_host_wird_bereinigt_und_samt_nebenvariante_erlaubt(self):
        """Verhindert zwei Ausfälle der Weiterleitung aus Schritt 37: ein
        ``CANONICAL_HOST`` mit Schema oder Schrägstrich (``https://www.x.de/``)
        würde nie mit einem Hostnamen übereinstimmen, und eine Nebenvariante,
        die nicht in ``ALLOWED_HOSTS`` steht, bekäme 400 statt 301."""
        betrieb = lade_einstellungen(dict(BETRIEBSUMGEBUNG,
                                          CANONICAL_HOST='https://www.Shop.example/'))
        self.assertEqual(betrieb.CANONICAL_HOST, 'www.shop.example')
        self.assertIn('www.shop.example', betrieb.ALLOWED_HOSTS)
        self.assertIn('shop.example', betrieb.ALLOWED_HOSTS)
        self.assertIn('https://www.shop.example', betrieb.CSRF_TRUSTED_ORIGINS)
        self.assertIn('https://shop.example', betrieb.CSRF_TRUSTED_ORIGINS)

        ohne = lade_einstellungen(dict(BETRIEBSUMGEBUNG, CANONICAL_HOST=''))
        self.assertEqual(ohne.CANONICAL_HOST, '')

    def test_kein_geheimnis_steht_fest_im_quelltext(self):
        """Verhindert, dass ein Schlüssel oder Passwort in die Versionsverwaltung
        gerät: jedes Geheimnis muss aus der Umgebung kommen."""
        quelltext = _SETTINGS_PFAD.read_text(encoding='utf-8')
        for name in ('SECRET_KEY', 'EMAIL_HOST_PASSWORD', 'EMAIL_HOST_USER',
                     'PAYPAL_CLIENT_ID'):
            with self.subTest(name=name):
                self.assertIn(f"os.getenv('{name}'", quelltext)

    def test_die_sperre_gegen_wiederholtes_raten_ist_scharf(self):
        """Verhindert, dass der Brute-Force-Schutz beim Aufräumen der
        Einstellungen still abgeschaltet wird."""
        self.assertIn('axes', self.betrieb.INSTALLED_APPS)
        self.assertLessEqual(self.betrieb.AXES_FAILURE_LIMIT, 10)
        self.assertEqual(
            self.betrieb.AXES_LOCKOUT_PARAMETERS, [['username', 'ip_address']]
        )


class SchutzkoepfeTest(LuviqTestCase):
    """Was tatsächlich in einer Antwort steht – nicht, was eingestellt ist."""

    def test_jede_antwort_traegt_die_schutzkoepfe(self):
        """Verhindert, dass eine Middleware aus der Reihenfolge fällt und die
        Schutzköpfe zwar eingestellt, aber nicht mehr gesendet werden."""
        antwort = self.hole('/')
        self.assertEqual(antwort['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(antwort['X-Frame-Options'], 'DENY')
        self.assertEqual(antwort['Referrer-Policy'], 'strict-origin-when-cross-origin')

    def test_html_antworten_werden_komprimiert_ausgeliefert(self):
        """Verhindert, dass die Kompression beim Umsortieren der Middleware
        still wegfällt: eine unkomprimierte Startseite ist ein Vielfaches
        grösser, und kein Messwerkzeug würde das als Fehler melden – nur als
        langsam. Geprüft wird die tatsächliche Antwort, nicht die Einstellung."""
        antwort = self.hole('/', HTTP_ACCEPT_ENCODING='gzip')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.get('Content-Encoding'), 'gzip')
        # Ein Client ohne gzip-Unterstützung bekommt weiterhin Klartext.
        self.assertIsNone(self.hole('/').get('Content-Encoding'))

    def test_ein_http_abruf_wird_auf_https_umgeleitet(self):
        """Belegt, dass ``SECURE_SSL_REDIRECT`` greift – und begründet zugleich,
        warum alle übrigen Tests dieser Suite ``secure=True`` benutzen."""
        antwort = self.client.get('/')
        self.assertEqual(antwort.status_code, 301)
        self.assertTrue(antwort['Location'].startswith('https://'))

    def test_https_antworten_tragen_hsts_mit_einem_jahr_und_subdomains(self):
        """Verhindert, dass HSTS still wegfällt – etwa weil jemand den
        ``if not DEBUG``-Block in ``settings.py`` umbaut. Ohne die Kopfzeile
        fragt der Browser beim nächsten Besuch wieder per HTTP an, und der
        erste Abruf ist abfangbar. Geprüft wird die gesendete Kopfzeile auf
        zwei Seiten, nicht die Einstellung."""
        for pfad in ('/', '/produkte/'):
            with self.subTest(pfad=pfad):
                hsts = self.hole(pfad).get('Strict-Transport-Security', '')
                self.assertRegex(hsts, r'max-age=(\d+)', f'{pfad}: HSTS fehlt')
                self.assertGreaterEqual(int(re.search(r'max-age=(\d+)', hsts).group(1)), 31536000)
                self.assertIn('includeSubDomains', hsts)
                self.assertIn('preload', hsts)


def _quelle_erlaubt(url, quellen):
    """Deckt eine CSP-Quellliste die Adresse ``url``?

    Versteht die Formen, die in ``CSP_QUELLEN`` vorkommen: ``https:``
    (jede HTTPS-Adresse), ``https://host`` und ``https://*.host``.
    """
    host = (urlsplit(url).hostname or '').lower()
    for quelle in quellen:
        if quelle == 'https:' and url.startswith('https://'):
            return True
        if not quelle.startswith('https://'):
            continue
        muster = (urlsplit(quelle).hostname or '').lower()
        if muster.startswith('*.') and host.endswith(muster[1:]):
            return True
        if host == muster:
            return True
    return False


#: Was eine Seite von fremden Hosts einbindet, je Direktive: das Muster
#: findet die Adresse, die Direktive muss sie erlauben. ``.src = '…'`` ist
#: das Nachladen von Three.js in ``index.html``.
_FREMDQUELLEN = (
    ('script-src', re.compile(r'<script[^>]+src="(https://[^"]+)"')),
    ('script-src', re.compile(r'''\.src\s*=\s*['"](https://[^'"]+)['"]''')),
    ('style-src', re.compile(r'<link[^>]+rel="stylesheet"[^>]+href="(https://[^"]+)"')),
    ('style-src', re.compile(r'<link[^>]+href="(https://[^"]+)"[^>]+rel="stylesheet"')),
    ('frame-src', re.compile(r'<iframe[^>]+src="(https://[^"]+)"')),
)


class ContentSecurityPolicyTest(LuviqTestCase):
    """Die Content-Security-Policy aus Schritt 36 – gesetzt, scharf an den
    richtigen Stellen, und weit genug für alles, was die Seite einbindet."""

    SCHARFE_DIREKTIVEN = ("frame-ancestors 'none'", "base-uri 'self'",
                          "form-action 'self'", "object-src 'none'")

    def test_die_csp_ist_gesetzt_und_haelt_die_scharfen_direktiven(self):
        """Verhindert, dass die Richtlinie still verschwindet oder eine der
        vier scharfen Direktiven verliert: ohne ``frame-ancestors`` lässt sich
        die Seite in eine fremde Seite einbetten (Clickjacking), ohne
        ``form-action`` kann eingeschleuster Code das Anmeldeformular an einen
        fremden Server schicken, ohne ``base-uri`` lassen sich alle relativen
        Adressen umbiegen, ohne ``object-src`` laufen Plugins.

        Vorgabe ist Report-Only; ``scharf`` schaltet auf die blockierende
        Kopfzeile mit demselben Inhalt um; ``aus`` sendet keine."""
        antwort = self.hole('/')
        self.assertFalse(antwort.has_header('Content-Security-Policy'),
                         'Vorgabe muss Report-Only sein, bis der Browser geprüft ist')
        richtlinie = antwort.get('Content-Security-Policy-Report-Only', '')
        self.assertTrue(richtlinie, 'Keine Content-Security-Policy-Report-Only auf /')
        for direktive in self.SCHARFE_DIREKTIVEN:
            with self.subTest(direktive=direktive):
                self.assertIn(direktive, richtlinie)

        with self.settings(CSP_MODUS='scharf'):
            scharf = self.hole('/')
        self.assertEqual(scharf.get('Content-Security-Policy'), richtlinie)
        self.assertFalse(scharf.has_header('Content-Security-Policy-Report-Only'))

        with self.settings(CSP_MODUS='aus'):
            aus = self.hole('/')
        self.assertFalse(aus.has_header('Content-Security-Policy'))
        self.assertFalse(aus.has_header('Content-Security-Policy-Report-Only'))

        with self.settings(CSP_MODUS='tippfehler'):
            tippfehler = self.hole('/')
        self.assertEqual(tippfehler.get('Content-Security-Policy-Report-Only'), richtlinie,
                         'Ein unbekannter Modus muss auf Report-Only zurückfallen')

    def test_die_csp_kommt_aus_der_eigenen_middleware(self):
        """Gegenbeweis zum Test darüber: ohne ``ContentSecurityPolicyMiddleware``
        darf keine Kopfzeile mehr kommen – sonst prüfte der Test oben etwas
        anderes als die Middleware, und ihr Ausbau bliebe unbemerkt."""
        with modify_settings(MIDDLEWARE={'remove': ['shop1.middleware.ContentSecurityPolicyMiddleware']}):
            antwort = self.hole('/')
        self.assertFalse(antwort.has_header('Content-Security-Policy'))
        self.assertFalse(antwort.has_header('Content-Security-Policy-Report-Only'))

    def test_die_csp_erlaubt_jede_fremdquelle_die_die_seiten_einbinden(self):
        """Verhindert die teuerste Wirkung einer CSP: dass sie die Seite
        bricht. Jeder fremde Host, den eine öffentliche Seite oder das
        Admin-Panel per ``<script src>``, Stylesheet, Iframe oder Nachladen
        einbindet (Alpine.js, GSAP, Three.js, Chart.js, Google Fonts, die
        Karte), muss in der passenden Direktive stehen. Ein neues CDN in
        einem Template fällt hier auf, bevor der Browser es blockiert –
        auch dann, wenn die Richtlinie noch als Report-Only läuft.

        Der Test schlägt auch an, wenn er gar keine Fremdquelle findet: dann
        hat sich die Suchweise von den Templates entfernt."""
        from django.contrib.auth.models import User

        admin = User.objects.create_superuser('inhaberin', 'i@example.invalid', 'x' * 20)
        self.client.force_login(admin)

        gefunden = 0
        for pfad in OEFFENTLICHE_SEITEN + ADMIN_SEITEN:
            html = self.hole(pfad).content.decode()
            for direktive, muster in _FREMDQUELLEN:
                for url in muster.findall(html):
                    gefunden += 1
                    with self.subTest(pfad=pfad, direktive=direktive, url=url[:60]):
                        self.assertTrue(
                            _quelle_erlaubt(url, settings.CSP_QUELLEN[direktive]),
                            f'{pfad} bindet {url} ein, {direktive} erlaubt es nicht',
                        )
        self.assertGreaterEqual(gefunden, 5, 'Kaum Fremdquellen gefunden – Suchmuster prüfen')

    def test_die_csp_deckt_paypal_auf_der_bezahlseite(self):
        """Verhindert den schlimmsten Fall aus dem Plan: der Checkout
        funktioniert nicht und niemand merkt es. ``payment.html`` lädt das
        PayPal-SDK von ``www.paypal.com``; das SDK rendert seine Knöpfe in
        Iframes von ``*.paypal.com``, lädt Bilder und Skripte von
        ``*.paypalobjects.com`` und meldet an ``*.paypal.com`` zurück. Die
        Bezahlseite selbst braucht eine Bestellung und ist hier nicht
        abrufbar – geprüft wird deshalb die Richtlinie gegen die im Template
        eingebundene Adresse und gegen die Hosts, die das SDK nachlädt."""
        vorlage = Path(settings.BASE_DIR) / 'shop1' / 'templates' / 'shop1' / 'payment.html'
        sdk = re.findall(r'<script src="(https://[^"?]+)', vorlage.read_text(encoding='utf-8'))
        self.assertTrue(sdk, 'payment.html bindet kein PayPal-SDK mehr ein')
        quellen = settings.CSP_QUELLEN
        for url in sdk:
            with self.subTest(url=url):
                self.assertTrue(_quelle_erlaubt(url, quellen['script-src']))
        for host in ('https://www.paypal.com/x', 'https://www.sandbox.paypal.com/x',
                     'https://www.paypalobjects.com/x'):
            with self.subTest(host=host):
                self.assertTrue(_quelle_erlaubt(host, quellen['script-src']))
                self.assertTrue(_quelle_erlaubt(host, quellen['img-src']))
        for host in ('https://www.paypal.com/x', 'https://www.sandbox.paypal.com/x'):
            with self.subTest(host=host):
                self.assertTrue(_quelle_erlaubt(host, quellen['frame-src']))
                self.assertTrue(_quelle_erlaubt(host, quellen['connect-src']))


@override_settings(
    CANONICAL_HOST='www.luviq-alsfeld.com',
    ALLOWED_HOSTS=['www.luviq-alsfeld.com', 'luviq-alsfeld.com',
                   '.up.railway.app', 'localhost', 'testserver'],
)
class KanonischerHostTest(LuviqTestCase):
    """Die Weiterleitung aus Schritt 37 – genau die vier Fälle des Plans."""

    def test_der_kanonische_host_antwortet_direkt_mit_200(self):
        """Verhindert die Endlosschleife: der kanonische Host selbst darf
        nie umgeleitet werden. Genau so würde eine falsche Regel die Seite
        unerreichbar machen – und zwar erst im Betrieb."""
        antwort = self.hole('/', HTTP_HOST='www.luviq-alsfeld.com')
        self.assertEqual(antwort.status_code, 200)

    def test_die_nebenvariante_wird_per_301_mit_vollem_pfad_umgeleitet(self):
        """Verhindert die Rückkehr zum Zustand vor Schritt 37: beide
        Schreibweisen lieferten 200, und Google durfte sich eine aussuchen.
        Die Weiterleitung muss dauerhaft (301) sein, Pfad und Query erhalten
        und aus einem HTTP-Aufruf in **einer** Antwort auf die HTTPS-Adresse
        des kanonischen Hosts führen – nicht erst auf https://luviq-alsfeld.com
        und von dort weiter."""
        antwort = self.hole('/produkte/?seite=2', HTTP_HOST='luviq-alsfeld.com')
        self.assertEqual(antwort.status_code, 301)
        self.assertEqual(antwort['Location'], 'https://www.luviq-alsfeld.com/produkte/?seite=2')

        unsicher = self.client.get('/kontakt/', HTTP_HOST='luviq-alsfeld.com')
        self.assertEqual(unsicher.status_code, 301)
        self.assertEqual(unsicher['Location'], 'https://www.luviq-alsfeld.com/kontakt/')

    def test_die_railway_adresse_wird_nicht_umgeleitet(self):
        """Verhindert, dass die Regel den Deploy-Zugang trifft: Railway
        spricht die Anwendung unter ``*.up.railway.app`` an (Health-Check,
        Vorschau). ``PREPEND_WWW`` hätte genau das kaputtgemacht."""
        antwort = self.hole('/', HTTP_HOST='luviq-luisa-production.up.railway.app')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(self.hole('/', HTTP_HOST='localhost').status_code, 200)

    def test_ohne_variable_wird_nichts_umgeleitet(self):
        """Verhindert, dass die Middleware ohne ``CANONICAL_HOST`` etwas
        rät – etwa aus ``SITE_URL`` oder ``ALLOWED_HOSTS`` – und lokal oder
        in einer Vorschau-Umgebung Weiterleitungen erzeugt."""
        with self.settings(CANONICAL_HOST=''):
            antwort = self.hole('/', HTTP_HOST='luviq-alsfeld.com')
        self.assertEqual(antwort.status_code, 200)


class DatenbankweicheTest(LuviqTestCase):
    """``WerbungRouter`` – die Weiche zwischen Shop- und pystore-Datenbank."""

    def setUp(self):
        self.router = WerbungRouter()

    def test_werbung_und_besucherprotokoll_gehen_in_die_pystore_datenbank(self):
        """Verhindert, dass site-übergreifende Werbedaten in die Shop-Datenbank
        rutschen und dem pystore-Projekt fehlen."""
        for modell in (Werbung, VisitorLog):
            with self.subTest(modell=modell.__name__):
                self.assertEqual(self.router.db_for_write(modell), 'pystore')
                self.assertEqual(self.router.db_for_read(modell), 'pystore')

    def test_shop_modelle_bleiben_in_der_eigenen_datenbank(self):
        """Verhindert, dass Produkte oder Kommentare versehentlich in die
        fremdverwaltete pystore-Datenbank geschrieben werden."""
        for modell in (Produkt, Comment):
            with self.subTest(modell=modell.__name__):
                self.assertIsNone(self.router.db_for_write(modell))

    def test_fremdverwaltete_pystore_datenbank_wird_nicht_migriert(self):
        """Verhindert, dass dieses Projekt Migrationen in einer Datenbank
        ausführt, die dem pystore-Projekt gehört."""
        with self.settings(PYSTORE_IS_EXTERNAL=True):
            self.assertFalse(self.router.allow_migrate('pystore', 'shop1', 'visitorlog'))
            self.assertFalse(self.router.allow_migrate('default', 'shop1', 'werbung'))

    def test_eigene_pystore_datenbank_wird_sehr_wohl_migriert(self):
        """Verhindert den Rückfall in den Zustand, in dem ohne
        ``PYSTORE_DATABASE_URL`` gar keine Werbe- und Besuchertabellen
        entstehen – lokal wie im Testlauf fehlten sie dann vollständig."""
        with self.settings(PYSTORE_IS_EXTERNAL=False):
            self.assertIsNone(self.router.allow_migrate('pystore', 'shop1', 'visitorlog'))
            self.assertIsNone(self.router.allow_migrate('default', 'shop1', 'werbung'))


class PruefbefehlTest(LuviqTestCase):
    """``python manage.py pruefe_seite`` – die Prüfung der laufenden Umgebung.

    Sie prüft, was die Testsuite bauartbedingt nicht sehen kann: gesetzte
    Umgebungsvariablen, erreichbare Datenbanken, vorhandene statische Dateien.
    """

    def _laufe(self, **optionen):
        from io import StringIO

        from django.core.management import call_command

        ausgabe = StringIO()
        try:
            call_command('pruefe_seite', stdout=ausgabe, stderr=ausgabe, **optionen)
            code = 0
        except SystemExit as ende:
            code = ende.code
        return code, ausgabe.getvalue()

    def test_exitcode_und_bericht_des_befehls_stimmen_ueberein(self):
        """Verhindert die zwei Arten, auf die der Prüfbefehl in ``start.sh``
        unbrauchbar würde: er bricht den Start mit Exitcode 1 ab, ohne einen
        einzigen FEHLER zu nennen – oder er nennt einen FEHLER, endet aber mit
        0, und der Container startet trotzdem.

        Geprüft wird der Vertrag zwischen Bericht und Exitcode: die Summenzeile
        zählt genau die ausgegebenen FEHLER- und WARNUNG-Zeilen, und der
        Exitcode ist genau dann 1, wenn mindestens ein FEHLER gemeldet wurde.
        Das gilt unabhängig davon, wie die Umgebung des Testlaufs gerade
        aussieht."""
        import re

        code, text = self._laufe()
        fehler = [z for z in text.splitlines() if z.startswith('FEHLER')]
        warnungen = [z for z in text.splitlines() if z.startswith('WARNUNG')]

        summe = re.search(r'(\d+) Fehler, (\d+) Warnungen\.', text)
        if summe:
            self.assertEqual(int(summe.group(1)), len(fehler), text)
            self.assertEqual(int(summe.group(2)), len(warnungen), text)
            self.assertTrue(fehler or warnungen, text)
        else:
            self.assertIn('Alles in Ordnung.', text)
            self.assertFalse(fehler or warnungen, text)

        self.assertEqual(code, 1 if fehler else 0, text)

    def test_debug_wird_als_fehler_gemeldet(self):
        """Verhindert ein unbemerktes DEBUG=True in der Betriebsumgebung –
        der teuerste Ein-Schalter-Fehler im ganzen Projekt."""
        with self.settings(DEBUG=True):
            code, text = self._laufe()
        self.assertEqual(code, 1)
        self.assertIn('DEBUG ist an', text)

    def test_offene_hostliste_wird_als_fehler_gemeldet(self):
        """Verhindert ALLOWED_HOSTS = ['*'] im Betrieb."""
        with self.settings(ALLOWED_HOSTS=['*']):
            code, text = self._laufe()
        self.assertEqual(code, 1)
        self.assertIn('ALLOWED_HOSTS', text)

    def test_unsicherer_secret_key_wird_als_fehler_gemeldet(self):
        """Verhindert das Ausliefern mit dem Beispielschlüssel."""
        with self.settings(SECRET_KEY='django-insecure-CHANGE_THIS_IN_PRODUCTION'):
            code, text = self._laufe()
        self.assertEqual(code, 1)
        self.assertIn('SECRET_KEY', text)

    def test_fehlende_admin_zugangsdaten_werden_gemeldet(self):
        """Verhindert einen Start ohne Superuser: ``start.sh`` legt ihn nur an,
        wenn ADMIN_USERNAME und ADMIN_PASSWORD gesetzt sind."""
        with mock.patch.dict(os.environ, {}, clear=True):
            code, text = self._laufe()
        self.assertEqual(code, 1)
        self.assertIn('ADMIN_USERNAME', text)
        self.assertIn('ADMIN_PASSWORD', text)

    def test_streng_macht_warnungen_zu_fehlern(self):
        """Verhindert, dass Warnungen im Dauerbetrieb ignoriert werden – für
        einen Einsatz in start.sh oder einer Prüfstrecke."""
        with mock.patch.dict(os.environ, {
            'ADMIN_USERNAME': 'shopbesitzer', 'ADMIN_PASSWORD': 'x' * 20,
        }, clear=True):
            ohne, _ = self._laufe()
            mit, text = self._laufe(streng=True)
        self.assertEqual(ohne, 0)
        self.assertEqual(mit, 1)
        self.assertIn('WARNUNG', text)

    # ── Die ausgelieferte Seite (Schritt 39) ───────────────────────────

    def test_der_befehl_ruft_jede_sitemap_adresse_ab_und_findet_nichts(self):
        """Verhindert, dass die Seitenprüfung still nichts prüft: der
        Bericht muss belegen, dass jede Sitemap-Adresse – die statischen
        Seiten und die Produktseite – abgerufen wurde, und darf im sauberen
        Zustand keinen FEHLER daraus melden. Nur so ist ein FEHLER im
        Container-Log später ein echter Befund."""
        erzeuge_produkt('Bemalte Bomberjacke')
        with mock.patch.dict(os.environ, {
            'ADMIN_USERNAME': 'shopbesitzer', 'ADMIN_PASSWORD': 'x' * 20,
        }):
            code, text = self._laufe()
        self.assertEqual(code, 0, text)
        treffer = re.search(r'(\d+) von (\d+) Sitemap-Adressen', text)
        self.assertIsNotNone(treffer, text)
        self.assertEqual(treffer.group(1), treffer.group(2), text)
        # Soll: jeder <loc> der ausgelieferten Sitemap – acht statische Seiten,
        # die freigegebenen Wissensseiten und die Produktseite.
        sitemap = self.hole('/sitemap.xml').content.decode()
        self.assertEqual(int(treffer.group(1)), sitemap.count('<loc>'), text)
        self.assertGreaterEqual(int(treffer.group(1)), 9, text)

    def test_ein_aktives_produkt_ohne_beschreibung_wird_als_fehler_gemeldet(self):
        """Verhindert, dass ein Produkt mit leerem Pflichtwert unbemerkt in
        Sitemap, llms.txt und Übersicht steht. ``update()`` umgeht ``save()``
        und das Formular – so entsteht der Zustand, den keine Eingabemaske
        mehr zulässt, aber eine alte Zeile in der Datenbank haben kann."""
        produkt = erzeuge_produkt('Bemalte Bomberjacke')
        Produkt.objects.filter(pk=produkt.pk).update(beschreibung='   ')
        code, text = self._laufe()
        self.assertEqual(code, 1)
        self.assertRegex(text, r'FEHLER.*Bemalte Bomberjacke.*ohne beschreibung')

    def test_eine_fehlende_csp_wird_als_fehler_gemeldet(self):
        """Verhindert, dass die Richtlinie aus Schritt 36 abgeschaltet wird
        (``CSP_MODUS=aus``) und niemand es merkt: der Prüfbefehl im
        Container-Start muss es als FEHLER nennen. Als Report-Only ist es
        eine WARNUNG – der Hinweis, nach der Browserprüfung scharf zu
        schalten."""
        with self.settings(CSP_MODUS='aus'):
            code, text = self._laufe()
        self.assertEqual(code, 1)
        self.assertRegex(text, r'FEHLER.*Content-Security-Policy')

        _, text = self._laufe()
        self.assertRegex(text, r'WARNUNG.*Content-Security-Policy.*Report-Only')

    def test_der_befehl_hinterlaesst_keine_spuren(self):
        """Verhindert, dass der Prüflauf beim Container-Start selbst Daten
        erzeugt: ``startseite()`` zählt bei jedem Abruf von ``/`` eine
        Impression je aktiver Werbung (0,25 ct, dem Werbekunden berechnet),
        und die Middleware schriebe einen Besuchseintrag. Beides muss nach
        dem Lauf unverändert sein – die Abrufe laufen in einer zurück-
        gerollten Transaktion und mit abgeschaltetem Protokoll."""
        werbung = Werbung.objects.create(titel='Probe', link='https://example.invalid/', budget=10)
        self.assertTrue(werbung.ist_aktiv)

        self._laufe()

        werbung.refresh_from_db()
        self.assertEqual(werbung.impressionen, 0)
        self.assertEqual(VisitorLog.objects.count(), 0)
        self.assertEqual(PageVisit.objects.count(), 0)


class AusgabecacheTest(LuviqTestCase):
    """sitemap.xml und llms.txt kommen nach dem ersten Abruf aus dem Cache."""

    def test_sitemap_und_llms_txt_fragen_die_datenbank_nur_einmal(self):
        """Verhindert, dass jeder Crawler-Abruf der Sitemap alle aktiven
        Produkte neu aus der Datenbank lädt – bei einem Crawler-Schwarm war
        das die teuerste ungecachte Abfrage des Shops. Der zweite Abruf muss
        ohne eine einzige Datenbankabfrage auskommen und dieselbe Antwort
        liefern."""
        from ._basis import erzeuge_produkt

        erzeuge_produkt('Gecachtes Stueck')
        for pfad in ('/sitemap.xml', '/llms.txt'):
            with self.subTest(pfad=pfad):
                erster = self.hole(pfad)
                self.assertEqual(erster.status_code, 200)
                self.assertIn('gecachtes-stueck', erster.content.decode())
                with self.assertNumQueries(0):
                    zweiter = self.hole(pfad)
                self.assertEqual(zweiter.content, erster.content)


class BesucherprotokollTest(LuviqTestCase):
    """``PageVisitMiddleware`` läuft bei jeder Antwort mit."""

    def test_ein_seitenabruf_wird_protokolliert(self):
        """Verhindert, dass das Besucherprotokoll unbemerkt versiegt – im
        Admin-Dashboard fiele das erst Wochen später auf."""
        self.hole('/')
        self.assertEqual(VisitorLog.objects.filter(path='/').count(), 1)

    def test_derselbe_pfad_wird_im_selben_zeitfenster_nur_einmal_gezaehlt(self):
        """Verhindert, dass ein Neuladen der Seite das Protokoll aufbläht. Das
        Fenster beträgt 5 Minuten (``diff < 300`` in ``middleware.py``)."""
        self.hole('/')
        self.hole('/')
        self.hole('/')
        self.assertEqual(VisitorLog.objects.filter(path='/').count(), 1)

    def test_verschiedene_pfade_werden_getrennt_protokolliert(self):
        """Gegenprobe: eine zu grobe Entdopplung würde alle Unterseiten
        verschlucken und die Statistik wertlos machen."""
        self.hole('/')
        self.hole('/produkte/')
        self.assertEqual(VisitorLog.objects.count(), 2)

    def test_statische_dateien_und_sitemap_werden_nicht_protokolliert(self):
        """Verhindert, dass jeder Crawler-Abruf der Sitemap als Besuch zählt."""
        self.hole('/sitemap.xml')
        self.hole('/robots.txt')
        self.assertEqual(VisitorLog.objects.count(), 0)

    def test_der_abschalter_stoppt_das_protokoll_und_die_vorgabe_ist_an(self):
        """Verhindert zweierlei: dass ``VISITOR_TRACKING=False`` ohne Wirkung
        bleibt – dann liesse sich das Protokoll bei hakender pystore-Datenbank
        nicht abschalten, und jeder Besucher wartete auf den Verbindungs-
        timeout – und dass die Vorgabe umkippt und das Protokoll ohne die
        Variable still versiegt."""
        from ..middleware import TRACKING_ENV

        with mock.patch.dict(os.environ, {TRACKING_ENV: 'False'}):
            antwort = self.hole('/')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(VisitorLog.objects.count(), 0)
        self.assertEqual(PageVisit.objects.count(), 0)

        with mock.patch.dict(os.environ, {}):
            os.environ.pop(TRACKING_ENV, None)
            self.hole('/produkte/')
        self.assertEqual(VisitorLog.objects.count(), 1)
        self.assertEqual(PageVisit.objects.count(), 1)

    def test_der_geo_lookup_laeuft_im_pool_und_entfaellt_wenn_er_voll_ist(self):
        """Verhindert die Rückkehr zum neuen Betriebssystem-Thread je
        Seitenaufruf ohne Obergrenze – und dass ein voller Pool eine
        Warteschlange aufbaut statt den Lookup auszulassen. Kein Netzzugriff:
        ``submit`` wird abgefangen, der Lookup selbst läuft nie."""
        from .. import middleware

        with mock.patch.object(middleware._geo_pool, 'submit') as submit:
            # Private Adresse (Testclient): nichts nachzuschlagen.
            self.hole('/')
            submit.assert_not_called()

            # Öffentliche Adresse: genau ein Auftrag in den Pool.
            self.hole('/produkte/', REMOTE_ADDR='203.0.113.5')
            submit.assert_called_once()
            self.assertIs(submit.call_args.args[0], middleware._geo_enrich)
            middleware._geo_frei.release()   # der abgefangene Lookup gibt nie frei

            # Alle Plätze belegt: der Lookup entfällt, nichts wird eingereiht.
            belegt = [middleware._geo_frei.acquire(blocking=False)
                      for _ in range(middleware.GEO_PLAETZE)]
            try:
                self.assertTrue(all(belegt))
                self.assertFalse(middleware._geo_einreihen(99, '203.0.113.5'))
                submit.assert_called_once()
            finally:
                for _ in belegt:
                    middleware._geo_frei.release()
