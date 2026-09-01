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

from ..models import Comment, PageVisit, Produkt, VisitorLog, Werbung
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
