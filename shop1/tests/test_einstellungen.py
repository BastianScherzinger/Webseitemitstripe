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
from pathlib import Path
from unittest import mock

from django.conf import settings

from ..models import Comment, Produkt, VisitorLog, Werbung
from ..routers import WerbungRouter
from ._basis import LuviqTestCase

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

    def test_ein_http_abruf_wird_auf_https_umgeleitet(self):
        """Belegt, dass ``SECURE_SSL_REDIRECT`` greift – und begründet zugleich,
        warum alle übrigen Tests dieser Suite ``secure=True`` benutzen."""
        antwort = self.client.get('/')
        self.assertEqual(antwort.status_code, 301)
        self.assertTrue(antwort['Location'].startswith('https://'))


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
