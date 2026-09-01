"""Prüfbefehl für die laufende Umgebung.

Ergänzt die Testsuite, ersetzt sie nicht. Die Tests prüfen den Code; dieser
Befehl prüft das, was erst zur Laufzeit feststeht: gesetzte
Umgebungsvariablen, erreichbare Datenbanken, vorhandene statische Dateien.
Genau die Fehlerklasse, die in einem grünen Testlauf unsichtbar bleibt und
den Container erst beim Start oder – schlimmer – erst im Betrieb umwirft.

    python manage.py pruefe_seite
    python manage.py pruefe_seite --streng   # Warnungen zählen wie Fehler
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Prüft die laufende Umgebung: Variablen, Datenbanken, statische Dateien.'

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
