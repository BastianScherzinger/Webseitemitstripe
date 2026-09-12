"""Prüfbefehl für jeden Verweis, den die Seite selbst ausspricht.

Der zweite eigene Prüfbefehl neben ``pruefe_seite`` – und er sieht etwas
anderes an. ``pruefe_seite`` ruft **die Adressen der Sitemap** ab und prüft
je Seite Kopfangaben, JSON-LD und Schutzkopfzeilen. Was dabei niemand
bemerkt: ein Verweis **innerhalb** einer dieser Seiten, der ins Leere führt.
Ein Tippfehler in einem ``href``, eine umbenannte Route, ein Produkt, das
deaktiviert wurde, während die Startseite noch darauf zeigt – all das
beantwortet die Seite mit 404, und kein Test und kein Startlauf meldet es,
weil der Pfad in keiner Liste steht. Genau diese Lücke schliesst dieser
Befehl: er nimmt jede öffentliche Seite, liest ihre Verweise und ruft sie ab.

Geprüft werden drei Dinge:

1. **Jeder interne Verweis kommt an.** Startpunkte sind ``/``, alle Adressen
   der ``sitemap.xml`` und alle Adressen der ``llms.txt``; von dort aus jeder
   ``<a href>``. Alles ab 400 ist ein Fehler, eine Weiterleitung eine
   Warnung – ein Verweis auf die eigene Seite sollte die Zieladresse gleich
   nennen, statt den Besucher einen Umweg laufen zu lassen. Ausgenommen ist
   die Weiterleitung auf ``LOGIN_URL``: bei ``/warenkorb/`` und den
   Kontoseiten ist sie der Schutz selbst und stünde sonst in jedem Lauf.
2. **Die Adressen der llms.txt stimmen.** ``pruefe_seite`` prüft nur die
   Sitemap; die llms.txt nennt dieselben Seiten noch einmal von Hand
   aufgeschrieben und kann deshalb auseinanderlaufen.
3. **Kein fremder Verweis läuft über ``http://``.** Ein Ziel ohne TLS ist ein
   Bruch in der Kette, die HSTS und die Content-Security-Policy aufbauen.
   Fremde Adressen werden **nicht** abgerufen: dieser Befehl läuft auch beim
   Containerstart und in der Prüfstrecke, und keiner von beiden soll auf
   fremde Server zugreifen.

Wie ``pruefe_seite`` läuft alles über den Django-Testclient im selben
Prozess, mit abgeschaltetem Besuchsprotokoll und in einer Transaktion je
Datenbank, die am Ende zurückgerollt wird. Adressen, die etwas verändern
(Warenkorb, Abmeldung, Werbeklick, Kommentar), werden nicht abgerufen,
sondern nur gezählt – sie stehen in ``KEINE_PRUEFUNG`` mit dem Grund.

    python manage.py pruefe_links
    python manage.py pruefe_links --streng   # Warnungen zählen wie Fehler
"""

import os
import re
from unittest import mock
from urllib.parse import urljoin, urlsplit

from django.core.management.base import BaseCommand
from django.db import transaction

# Denselben Host nehmen wie der Seitenprüfbefehl: die Wahl hängt an
# ALLOWED_HOSTS und ist dort begründet. Zwei Fassungen derselben Wahl wären
# zwei Fassungen, die auseinanderlaufen können.
from .pruefe_seite import pruefhost

_LOC = re.compile(r'<loc>(.*?)</loc>', re.DOTALL)
_ANKER = re.compile(r'<a\b[^>]*?\bhref\s*=\s*(["\'])(.*?)\1', re.I | re.DOTALL)
#: Markdown-Verweis der llms.txt: ``[Titel](https://…)``.
_MD_LINK = re.compile(r'\]\((https?://[^)\s]+)\)')

#: Pfadanfänge, die nicht abgerufen werden, mit dem Grund. Jeder von ihnen
#: verändert etwas oder beendet eine Sitzung; ein Prüflauf, der sie anfasst,
#: misst nicht mehr die Seite, sondern sich selbst. Die Transaktion würde die
#: Spuren zwar zurückrollen, aber ``/werbung/klick/`` schickt den Abruf
#: ausserdem auf einen fremden Server weiter.
KEINE_PRUEFUNG = (
    ('/warenkorb/add/', 'legt etwas in den Warenkorb'),
    ('/warenkorb/remove/', 'nimmt etwas aus dem Warenkorb'),
    ('/warenkorb/update/', 'ändert den Warenkorb'),
    ('/comment/', 'schreibt, mag oder löscht einen Kommentar'),
    ('/werbung/klick/', 'zählt einen Werbeklick und leitet nach aussen'),
    ('/logout/', 'beendet die Sitzung'),
    ('/delete-account/', 'löscht ein Konto'),
    ('/resend-verification/', 'verschickt eine Mail'),
    ('/newsletter/subscribe/', 'trägt eine Adresse ein'),
    ('/paypal/capture/', 'bucht eine Zahlung ab'),
    ('/verify/', 'verbraucht einen einmaligen Bestätigungsschlüssel'),
)


class Command(BaseCommand):
    help = ('Ruft jeden Verweis jeder öffentlichen Seite ab und meldet tote '
            'interne Links, Umwege über Weiterleitungen und fremde Ziele '
            'ohne TLS.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--streng', action='store_true',
            help='Warnungen ebenfalls als Fehler werten (Exitcode 1).',
        )

    def handle(self, *args, **optionen):
        self.fehler = []
        self.warnungen = []
        self.gezaehlt = {'seiten': 0, 'ziele': 0, 'extern': 0,
                         'ausgelassen': 0, 'geschuetzt': 0}

        self._pruefe()

        for text in self.warnungen:
            self.stdout.write(self.style.WARNING(f'WARNUNG  {text}'))
        for text in self.fehler:
            self.stdout.write(self.style.ERROR(f'FEHLER   {text}'))

        z = self.gezaehlt
        self.stdout.write(
            f"Verweise: {z['seiten']} Seiten gelesen, {z['ziele']} eigene "
            f"Adressen abgerufen, davon {z['geschuetzt']} hinter der "
            f"Anmeldung; {z['extern']} fremde Ziele nur geprüft, "
            f"{z['ausgelassen']} verändernde Adressen ausgelassen."
        )
        if not self.fehler and not self.warnungen:
            self.stdout.write(self.style.SUCCESS('Jeder Verweis kommt an.'))
        else:
            self.stdout.write(
                f'\n{len(self.fehler)} Fehler, {len(self.warnungen)} Warnungen.'
            )

        if self.fehler or (optionen['streng'] and self.warnungen):
            raise SystemExit(1)

    # ── Ablauf ─────────────────────────────────────────────────────────

    def _pruefe(self):
        """Rahmen wie in ``pruefe_seite``: kein Besuchsprotokoll, keine Spur
        in einer der beiden Datenbanken."""
        from django.test import Client

        from ...middleware import TRACKING_ENV

        client = Client(HTTP_HOST=pruefhost(), raise_request_exception=False)
        try:
            with mock.patch.dict(os.environ, {TRACKING_ENV: 'False'}), \
                    transaction.atomic(using='default'), \
                    transaction.atomic(using='pystore'):
                self._pruefe_mit(client)
                transaction.set_rollback(True, using='default')
                transaction.set_rollback(True, using='pystore')
        except Exception as fehler:
            self.fehler.append(
                f'Die Verweisprüfung ist abgebrochen: '
                f'{type(fehler).__name__}: {fehler}'
            )

    def _pruefe_mit(self, client):
        startseiten = self._startseiten(client)
        ziele = {}          # Pfad → Menge der Seiten, die ihn nennen
        extern = {}         # vollständige Adresse → Menge der Quellen

        for pfad in startseiten:
            antwort = self._hole(client, pfad)
            if antwort is None or antwort.status_code != 200:
                # Dass die Seite selbst antwortet, prüft pruefe_seite; hier
                # zählt nur, dass ihre Verweise nicht gelesen werden können.
                code = 'Ausnahme' if antwort is None else antwort.status_code
                self.fehler.append(
                    f'{pfad} antwortet mit {code} – die Verweise dieser Seite '
                    f'liessen sich nicht prüfen.'
                )
                continue
            self.gezaehlt['seiten'] += 1
            self._sammle(pfad, antwort.content.decode('utf-8', 'replace'),
                         ziele, extern)

        for ziel in sorted(ziele):
            if ziel in startseiten:
                continue        # oben schon abgerufen
            self._pruefe_ziel(client, ziel, sorted(ziele[ziel]))

        for adresse in sorted(extern):
            self.gezaehlt['extern'] += 1
            if urlsplit(adresse).scheme == 'http':
                quellen = ', '.join(sorted(extern[adresse])[:3])
                self.warnungen.append(
                    f'{adresse} wird über http:// verwiesen (genannt auf '
                    f'{quellen}).'
                )

    # ── Einzelschritte ─────────────────────────────────────────────────

    def _startseiten(self, client):
        """``/`` plus alle Adressen aus Sitemap und llms.txt.

        Beide Listen entstehen getrennt (die Sitemap aus dem Register, die
        llms.txt von Hand geschrieben) – eine Adresse, die nur in einer von
        beiden steht, ist genau der Fall, den dieser Befehl finden soll.
        """
        pfade = {'/'}

        sitemap = self._hole(client, '/sitemap.xml')
        if sitemap is None or sitemap.status_code != 200:
            self.fehler.append('/sitemap.xml ist nicht abrufbar.')
        else:
            for adresse in _LOC.findall(sitemap.content.decode('utf-8', 'replace')):
                pfade.add(urlsplit(adresse.strip()).path or '/')

        llms = self._hole(client, '/llms.txt')
        if llms is None or llms.status_code != 200:
            self.fehler.append('/llms.txt ist nicht abrufbar.')
        else:
            for adresse in _MD_LINK.findall(llms.content.decode('utf-8', 'replace')):
                pfad = urlsplit(adresse).path or '/'
                antwort = self._hole(client, pfad)
                if antwort is None or antwort.status_code != 200:
                    code = 'Ausnahme' if antwort is None else antwort.status_code
                    self.fehler.append(
                        f'{pfad} steht in der llms.txt, antwortet aber mit {code}.'
                    )
                else:
                    pfade.add(pfad)

        return pfade

    def _sammle(self, quelle, html, ziele, extern):
        """Trägt jeden ``<a href>`` der Seite in eine der beiden Sammlungen."""
        eigener_host = pruefhost()
        for _, roh in _ANKER.findall(html):
            verweis = roh.strip().replace('&amp;', '&')
            if not verweis or verweis.startswith(('#', 'mailto:', 'tel:',
                                                  'javascript:', 'data:')):
                continue
            teile = urlsplit(verweis)
            if teile.scheme and teile.scheme not in ('http', 'https'):
                continue
            if teile.netloc and teile.hostname != eigener_host:
                extern.setdefault(verweis.split('#')[0], set()).add(quelle)
                continue
            # Eigene Seite: relativ auflösen, Anker und Abfrage abtrennen.
            pfad = urlsplit(urljoin(quelle, verweis)).path or '/'
            ziele.setdefault(pfad, set()).add(quelle)

    def _pruefe_ziel(self, client, pfad, quellen):
        grund = self._ausgelassen(pfad)
        if grund:
            self.gezaehlt['ausgelassen'] += 1
            return

        antwort = self._hole(client, pfad)
        if antwort is None:
            return          # _hole hat den Fehler schon vermerkt
        self.gezaehlt['ziele'] += 1
        woher = ', '.join(quellen[:3]) + (' …' if len(quellen) > 3 else '')

        if antwort.status_code in (301, 302, 307, 308):
            ziel = antwort.headers.get('Location', '?')
            if self._fuehrt_zur_anmeldung(ziel):
                # Warenkorb, Konto, Bestellung: die Weiterleitung auf die
                # Anmeldung ist hier der Schutz selbst, kein Umweg. Sie bei
                # jedem Lauf zu melden hiesse, den Befehl zu einer Meldung zu
                # machen, über die man hinwegliest.
                self.gezaehlt['geschuetzt'] += 1
                return
            weiter = self._hole(client, urlsplit(urljoin(pfad, ziel)).path or '/')
            if weiter is not None and weiter.status_code >= 400:
                self.fehler.append(
                    f'{pfad} (verlinkt auf {woher}) leitet auf {ziel} weiter, '
                    f'und dort steht {weiter.status_code}.'
                )
            else:
                self.warnungen.append(
                    f'{pfad} (verlinkt auf {woher}) antwortet mit '
                    f'{antwort.status_code} auf {ziel} – der Verweis könnte '
                    f'die Zieladresse gleich nennen.'
                )
        elif antwort.status_code >= 400:
            self.fehler.append(
                f'{pfad} antwortet mit {antwort.status_code}, verlinkt auf {woher}.'
            )

    @staticmethod
    def _fuehrt_zur_anmeldung(ziel):
        from django.conf import settings

        return (urlsplit(ziel).path or '/').startswith(
            getattr(settings, 'LOGIN_URL', '/login/'))

    @staticmethod
    def _ausgelassen(pfad):
        for anfang, grund in KEINE_PRUEFUNG:
            if pfad.startswith(anfang):
                return grund
        return None

    def _hole(self, client, pfad):
        """Ein Abruf über HTTPS ohne Weiterleitungsverfolgung.

        ``secure=True`` ist Pflicht: ``SECURE_SSL_REDIRECT`` beantwortet im
        Betriebsmodus jeden HTTP-Abruf mit 301, und dann prüft der Befehl nur
        noch die Weiterleitung. Ein 500 mit hinterlegter Ausnahme wird mit
        Typ und Text gemeldet, sonst stünde hier nur eine Zahl.
        """
        antwort = client.get(pfad, secure=True)
        if antwort.status_code >= 500 and getattr(antwort, 'exc_info', None):
            ausnahme = antwort.exc_info[1]
            self.fehler.append(
                f'{pfad} wirft {type(ausnahme).__name__}: {ausnahme}'
            )
            return None
        return antwort
