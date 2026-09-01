"""Prüfbefehl für die laufende Umgebung und die ausgelieferte Seite.

Ergänzt die Testsuite, ersetzt sie nicht. Die Tests prüfen den Code; dieser
Befehl prüft das, was erst zur Laufzeit feststeht: gesetzte
Umgebungsvariablen, erreichbare Datenbanken, vorhandene statische Dateien –
und seit Schritt 39 die Seite, wie sie mit den **echten** Daten und
Einstellungen ausgeliefert würde: jede Sitemap-Adresse, die Kopfangaben,
das JSON-LD, die Schutzkopfzeilen und die aktiven Produkte. Genau die
Fehlerklasse, die in einem grünen Testlauf unsichtbar bleibt und den
Container erst beim Start oder – schlimmer – erst im Betrieb umwirft.

Die Seitenabrufe laufen über den Django-Testclient im selben Prozess, ohne
Netzzugriff, mit abgeschaltetem Besuchsprotokoll und in einer Transaktion,
die am Ende zurückgerollt wird: der Prüflauf hinterlässt keine Spuren –
keine Sitzung, keinen Besuchseintrag, keine Werbe-Impression.

    python manage.py pruefe_seite
    python manage.py pruefe_seite --streng   # Warnungen zählen wie Fehler
"""

import json
import os
import re
from collections import Counter
from unittest import mock
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections, transaction

#: Länge der ``meta description`` auf Inhaltsseiten – dieselbe Spanne wie in
#: ``tests/test_seo.py``. Produktseiten dürfen kürzer sein (ihre Beschreibung
#: ist gepflegter Inhalt, kein Code); zu lang ist auch dort ein Fehler.
BESCHREIBUNG_MIN, BESCHREIBUNG_MAX = 110, 175

#: Direktiven, die die Content-Security-Policy tragen muss (Schritt 36).
CSP_PFLICHT = ("frame-ancestors 'none'", "base-uri 'self'",
               "form-action 'self'", "object-src 'none'")

_TITEL = re.compile(r'<title>(.*?)</title>', re.DOTALL)
_BESCHREIBUNG = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"')
_CANONICAL = re.compile(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"')
_ROBOTS = re.compile(r'<meta\s+name="robots"\s+content="([^"]*)"')
_LOC = re.compile(r'<loc>(.*?)</loc>')
_JSONLD = re.compile(
    r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', re.DOTALL
)


class Command(BaseCommand):
    help = ('Prüft die laufende Umgebung (Variablen, Datenbanken, statische '
            'Dateien) und die ausgelieferte Seite (Sitemap, Kopfangaben, '
            'JSON-LD, Schutzkopfzeilen, Produkte).')

    def add_arguments(self, parser):
        parser.add_argument(
            '--streng', action='store_true',
            help='Warnungen ebenfalls als Fehler werten (Exitcode 1).',
        )

    def handle(self, *args, **optionen):
        self.fehler = []
        self.warnungen = []

        self._pruefe_geheimnisse()
        self._pruefe_betriebsmodus()
        self._pruefe_hosts()
        self._pruefe_datenbanken()
        self._pruefe_statische_dateien()
        self._pruefe_dienste()
        self._pruefe_produkte()
        self._pruefe_ausgelieferte_seite()

        for text in self.warnungen:
            self.stdout.write(self.style.WARNING(f'WARNUNG  {text}'))
        for text in self.fehler:
            self.stdout.write(self.style.ERROR(f'FEHLER   {text}'))

        if not self.fehler and not self.warnungen:
            self.stdout.write(self.style.SUCCESS('Alles in Ordnung.'))
        else:
            self.stdout.write(
                f'\n{len(self.fehler)} Fehler, {len(self.warnungen)} Warnungen.'
            )

        if self.fehler or (optionen['streng'] and self.warnungen):
            raise SystemExit(1)

    # ── Einzelprüfungen ────────────────────────────────────────────────

    def _pruefe_geheimnisse(self):
        if settings.SECRET_KEY.startswith('django-insecure-'):
            self.fehler.append(
                'SECRET_KEY ist der mitgelieferte Beispielwert. Damit lassen '
                'sich Sitzungen und Passwort-Ruecksetzlinks faelschen.'
            )
        elif len(settings.SECRET_KEY) < 40:
            self.warnungen.append(
                f'SECRET_KEY ist nur {len(settings.SECRET_KEY)} Zeichen lang; '
                f'Django erzeugt 50.'
            )

    def _pruefe_betriebsmodus(self):
        if settings.DEBUG:
            self.fehler.append(
                'DEBUG ist an. Besucher sehen bei jedem Fehler den vollen '
                'Programmablauf samt Einstellungen, und HSTS, die '
                'HTTPS-Weiterleitung sowie sichere Cookies sind abgeschaltet.'
            )
            return
        for name in ('SECURE_SSL_REDIRECT', 'SESSION_COOKIE_SECURE',
                     'CSRF_COOKIE_SECURE', 'SECURE_CONTENT_TYPE_NOSNIFF'):
            if not getattr(settings, name, False):
                self.fehler.append(f'{name} ist aus, obwohl DEBUG aus ist.')
        if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
            self.warnungen.append('SECURE_HSTS_SECONDS ist nicht gesetzt.')

    def _pruefe_hosts(self):
        if '*' in settings.ALLOWED_HOSTS:
            self.fehler.append(
                'ALLOWED_HOSTS enthaelt "*". Die Seite beantwortet Anfragen '
                'unter jedem Namen und baut Links und Mails auf fremde Hosts.'
            )
        if not os.getenv('ALLOWED_HOSTS_EXTRA'):
            self.warnungen.append(
                'ALLOWED_HOSTS_EXTRA ist nicht gesetzt – die eigene Domain '
                'ist damit nicht erlaubt, nur *.up.railway.app.'
            )

        seiten_host = settings.SITE_URL.split('://')[-1].strip('/').split('/')[0]
        erlaubt = any(
            seiten_host == h or (h.startswith('.') and seiten_host.endswith(h))
            for h in settings.ALLOWED_HOSTS
        )
        if not erlaubt:
            self.warnungen.append(
                f'SITE_URL zeigt auf "{seiten_host}", dieser Host steht nicht '
                f'in ALLOWED_HOSTS. Links in Bestell- und Benachrichtigungs'
                f'mails fuehren dann ins Leere.'
            )

        if os.getenv('ADMIN_URL', 'admin/').strip('/') == 'admin':
            self.warnungen.append(
                'ADMIN_URL steht auf dem Standardpfad /admin/. Scanner-Bots '
                'probieren genau den zuerst.'
            )

    def _pruefe_datenbanken(self):
        for alias in ('default', 'pystore'):
            try:
                connections[alias].cursor().close()
            except Exception as fehler:
                self.fehler.append(f'Datenbank "{alias}" nicht erreichbar: {fehler}')

        if settings.PYSTORE_IS_EXTERNAL:
            fehlend = self._fehlende_tabellen('pystore')
            if fehlend:
                self.fehler.append(
                    f'In der pystore-Datenbank fehlen Tabellen: '
                    f'{", ".join(fehlend)}. Werbung und Besucherprotokoll '
                    f'laufen dorthin und wuerden verloren gehen.'
                )
        else:
            self.warnungen.append(
                'PYSTORE_DATABASE_URL ist nicht gesetzt – Werbe- und '
                'Besucherdaten landen in der Shop-Datenbank.'
            )

    def _fehlende_tabellen(self, alias):
        try:
            vorhanden = set(connections[alias].introspection.table_names())
        except Exception:
            return []
        return [t for t in ('shop1_werbung', 'shop1_werbungstat', 'shop1_visitorlog')
                if t not in vorhanden]

    def _pruefe_statische_dateien(self):
        speicher = settings.STORAGES['staticfiles']['BACKEND']
        if 'Manifest' not in speicher:
            return
        manifest = settings.STATIC_ROOT / 'staticfiles.json'
        if not manifest.exists():
            self.fehler.append(
                'staticfiles.json fehlt. Mit ManifestStaticFilesStorage '
                'scheitert dann jede Seite, die {% static %} benutzt – also '
                'jede. "collectstatic" muss vor dem Start laufen.'
            )

    def _pruefe_dienste(self):
        pflicht = {
            'ADMIN_USERNAME': 'ohne sie legt start.sh keinen Superuser an',
            'ADMIN_PASSWORD': 'ohne sie legt start.sh keinen Superuser an',
        }
        empfohlen = {
            'BREVO_API_KEY': 'ohne ihn wird keine Bestell- oder '
                             'Kontaktmail zugestellt',
            'CLOUDINARY_URL': 'ohne ihn liegen hochgeladene Produktbilder im '
                              'Container und sind nach dem naechsten Deploy weg',
            'DEFAULT_FROM_EMAIL': 'ohne ihn verschickt der Shop als '
                                  'noreply@luviq-shop.de',
            'ADMIN_EMAIL': 'ohne sie gehen Kontaktanfragen an '
                           'DEFAULT_FROM_EMAIL',
            'SITE_URL': 'ohne sie zeigen Mail-Links auf die Railway-Adresse',
        }
        for name, grund in pflicht.items():
            if not os.getenv(name):
                self.fehler.append(f'{name} ist nicht gesetzt – {grund}.')
        for name, grund in empfohlen.items():
            if not os.getenv(name):
                self.warnungen.append(f'{name} ist nicht gesetzt – {grund}.')

    # ── Daten ──────────────────────────────────────────────────────────

    def _pruefe_produkte(self):
        """Kein aktives Produkt ohne Pflichtwert, keine doppelte Kennung.

        Ein aktives Produkt steht in Sitemap, llms.txt und Produktübersicht;
        fehlt Name, Preis, Beschreibung oder Slug, liefert eine dieser
        Stellen leere Angaben oder eine Adresse ohne Kennung aus. Der Slug
        ist in der Datenbank eindeutig – die Prüfung fängt den Tag ab, an
        dem eine Migration das aufhebt oder Slugs nur in der Schreibweise
        abweichen.
        """
        from ...models import Produkt

        try:
            aktive = list(Produkt.objects.filter(aktiv=True)
                          .values('id', 'name', 'slug', 'preis', 'beschreibung', 'bild'))
        except Exception as fehler:
            self.fehler.append(f'Produkte nicht lesbar: {fehler}')
            return

        for p in aktive:
            leer = [feld for feld in ('name', 'slug', 'beschreibung')
                    if not (p[feld] or '').strip()]
            if p['preis'] is None:
                leer.append('preis')
            if leer:
                self.fehler.append(
                    f'Aktives Produkt #{p["id"]} „{p["name"] or "?"}“ ohne '
                    f'{", ".join(leer)} – es steht so in Sitemap und Übersicht.'
                )
            if not p['bild']:
                self.warnungen.append(
                    f'Aktives Produkt #{p["id"]} „{p["name"]}“ hat kein Bild.'
                )

        zaehler = Counter((p['slug'] or '').strip().lower() for p in aktive if p['slug'])
        for slug, anzahl in sorted(zaehler.items()):
            if anzahl > 1:
                self.fehler.append(
                    f'Slug „{slug}“ ist {anzahl}-mal vergeben – nur eines der '
                    f'Produkte ist unter seiner Adresse erreichbar.'
                )

    # ── Ausgelieferte Seite ────────────────────────────────────────────

    def _pruefhost(self):
        """Ein Host, den ALLOWED_HOSTS annimmt: der kanonische, sonst der
        aus SITE_URL, sonst localhost (steht im Betrieb immer drin)."""
        kandidaten = [
            getattr(settings, 'CANONICAL_HOST', ''),
            urlsplit(settings.SITE_URL).hostname or '',
            'localhost',
        ]
        erlaubt = settings.ALLOWED_HOSTS
        for host in kandidaten:
            if not host:
                continue
            if '*' in erlaubt or any(
                host == h or (h.startswith('.') and host.endswith(h)) for h in erlaubt
            ):
                return host
        return 'localhost'

    def _pruefe_ausgelieferte_seite(self):
        """Ruft jede Sitemap-Adresse über den Testclient ab und prüft die
        Antwort. Läuft in einer Transaktion je Datenbank, die am Ende
        zurückgerollt wird, und mit abgeschaltetem Besuchsprotokoll."""
        from django.test import Client

        from ...middleware import TRACKING_ENV

        client = Client(HTTP_HOST=self._pruefhost(), raise_request_exception=False)
        umgebung = {TRACKING_ENV: 'False'}
        try:
            with mock.patch.dict(os.environ, umgebung), \
                    transaction.atomic(using='default'), \
                    transaction.atomic(using='pystore'):
                self._pruefe_seiten_mit(client)
                transaction.set_rollback(True, using='default')
                transaction.set_rollback(True, using='pystore')
        except Exception as fehler:
            self.fehler.append(
                f'Die Prüfung der ausgelieferten Seite ist abgebrochen: '
                f'{type(fehler).__name__}: {fehler}'
            )

    def _hole(self, client, pfad):
        antwort = client.get(pfad, secure=True)
        if antwort.status_code >= 500 and getattr(antwort, 'exc_info', None):
            ausnahme = antwort.exc_info[1]
            self.fehler.append(
                f'{pfad} wirft {type(ausnahme).__name__}: {ausnahme}'
            )
        return antwort

    def _pruefe_seiten_mit(self, client):
        sitemap = self._hole(client, '/sitemap.xml')
        if sitemap.status_code != 200:
            self.fehler.append(f'/sitemap.xml antwortet mit {sitemap.status_code}.')
            return
        adressen = _LOC.findall(sitemap.content.decode('utf-8', 'replace'))
        if len(adressen) < 8:
            self.fehler.append(
                f'Die Sitemap nennt nur {len(adressen)} Adressen – sie wirkt unvollständig.'
            )

        produktpfade = self._produktpfade()
        geprueft = 0
        for adresse in adressen:
            pfad = urlsplit(adresse).path or '/'
            antwort = self._hole(client, pfad)
            if antwort.status_code != 200:
                self.fehler.append(
                    f'{pfad} steht in der Sitemap, antwortet aber mit {antwort.status_code}.'
                )
                continue
            geprueft += 1
            self._pruefe_kopf(pfad, antwort.content.decode('utf-8', 'replace'),
                              ist_produkt=pfad in produktpfade)

        self._pruefe_schutzkopfzeilen(self._hole(client, '/'))
        self.stdout.write(
            f'Ausgelieferte Seite: {geprueft} von {len(adressen)} Sitemap-Adressen '
            f'antworten mit 200 und wurden geprüft.'
        )

    @staticmethod
    def _produktpfade():
        from ...models import Produkt
        return {p.get_absolute_url() for p in Produkt.objects.filter(aktiv=True)}

    def _pruefe_kopf(self, pfad, html, ist_produkt):
        titel = [t.strip() for t in _TITEL.findall(html)]
        if len(titel) != 1 or not titel[0]:
            self.fehler.append(f'{pfad} hat {len(titel)} Titel statt genau einem.')
        elif not 25 <= len(titel[0]) <= 70:
            self.warnungen.append(f'{pfad}: Titel hat {len(titel[0])} Zeichen (25–70).')

        beschreibungen = [b.strip() for b in _BESCHREIBUNG.findall(html)]
        if len(beschreibungen) != 1 or not beschreibungen[0]:
            self.fehler.append(f'{pfad} hat {len(beschreibungen)} Beschreibungen statt genau einer.')
        else:
            laenge = len(beschreibungen[0])
            if laenge > BESCHREIBUNG_MAX:
                self.fehler.append(
                    f'{pfad}: Beschreibung hat {laenge} Zeichen, höchstens {BESCHREIBUNG_MAX}.'
                )
            elif laenge < BESCHREIBUNG_MIN:
                (self.warnungen if ist_produkt else self.fehler).append(
                    f'{pfad}: Beschreibung hat {laenge} Zeichen, mindestens {BESCHREIBUNG_MIN}.'
                )

        canonical = _CANONICAL.findall(html)
        if len(canonical) != 1:
            self.fehler.append(f'{pfad} hat {len(canonical)} canonical statt genau einem.')
        elif urlsplit(canonical[0]).path != pfad:
            self.fehler.append(f'{pfad} kanonisiert auf {canonical[0]}.')

        robots = _ROBOTS.findall(html)
        if not robots:
            self.fehler.append(f'{pfad} hat keine robots-Angabe.')
        elif 'noindex' in robots[0]:
            self.fehler.append(f'{pfad} steht in der Sitemap, verbietet aber die Aufnahme (noindex).')

        self._pruefe_jsonld(pfad, html, ist_produkt)

    def _pruefe_jsonld(self, pfad, html, ist_produkt):
        knoten = []
        bloecke = _JSONLD.findall(html)
        if not bloecke:
            self.fehler.append(f'{pfad} hat kein JSON-LD.')
            return
        for nummer, block in enumerate(bloecke):
            try:
                daten = json.loads(block)
            except json.JSONDecodeError as fehler:
                self.fehler.append(f'{pfad}: JSON-LD-Block {nummer} ist ungültig: {fehler}')
                continue
            knoten.extend(daten['@graph'] if isinstance(daten, dict) and '@graph' in daten
                          else daten if isinstance(daten, list) else [daten])

        typen = set()
        for k in knoten:
            typ = k.get('@type', '') if isinstance(k, dict) else ''
            typen.update(typ if isinstance(typ, list) else [typ])

        erwartet = {'Organization'}
        erwartet.add('Product' if ist_produkt else 'WebPage')
        if pfad != '/':
            erwartet.add('BreadcrumbList')
        fehlend = sorted(erwartet - typen)
        if fehlend:
            self.fehler.append(f'{pfad}: im JSON-LD fehlen die Knoten {", ".join(fehlend)}.')

    def _pruefe_schutzkopfzeilen(self, antwort):
        erwartet = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
        }
        for name, wert in erwartet.items():
            if antwort.get(name) != wert:
                self.fehler.append(
                    f'Kopfzeile {name} fehlt oder ist „{antwort.get(name)}“ statt „{wert}“.'
                )
        if not settings.DEBUG and not antwort.get('Strict-Transport-Security'):
            self.fehler.append('Kopfzeile Strict-Transport-Security fehlt.')

        csp = antwort.get('Content-Security-Policy') or antwort.get('Content-Security-Policy-Report-Only')
        if not csp:
            self.fehler.append(
                'Keine Content-Security-Policy in der Antwort – weder scharf '
                'noch als Report-Only (CSP_MODUS, Schritt 36).'
            )
            return
        fehlend = [d for d in CSP_PFLICHT if d not in csp]
        if fehlend:
            self.fehler.append(
                f'Content-Security-Policy ohne {", ".join(fehlend)}.'
            )
        if antwort.get('Content-Security-Policy-Report-Only') and not antwort.get('Content-Security-Policy'):
            self.warnungen.append(
                'Content-Security-Policy läuft noch als Report-Only – nach der '
                'Prüfung im Browser CSP_MODUS=scharf setzen.'
            )
