"""Eigene Middleware: kanonischer Host, Content-Security-Policy, Besuchsprotokoll.

Reihenfolge in ``settings.MIDDLEWARE``: ``CanonicalHostMiddleware`` ganz vorn,
``ContentSecurityPolicyMiddleware`` nach WhiteNoise, ``PageVisitMiddleware``
zuletzt.
"""
import hashlib
import hmac
import logging
import os
import re
import secrets
from urllib.parse import urlsplit
from django.conf import settings
from django.http import HttpResponsePermanentRedirect
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import F
from .models import PageVisit, TagesBesucher, VisitorLog

_log = logging.getLogger('shop1')


# ═══ KANONISCHER HOST ══════════════════════════════════════════════════════

def kanonischer_host():
    """``settings.CANONICAL_HOST`` in Kleinbuchstaben, leer = abgeschaltet.

    Je Anfrage gelesen, damit Tests den Wert überschreiben können und ein
    Umschalten der Variablen ohne Neustart wirkt.
    """
    return str(getattr(settings, 'CANONICAL_HOST', '') or '').strip().lower()


def nebenvariante(host):
    """Die jeweils andere www-Schreibweise: ``www.x.de`` ↔ ``x.de``."""
    return host[4:] if host.startswith('www.') else f'www.{host}'


class CanonicalHostMiddleware:
    """Leitet die www-/Nicht-www-Nebenvariante per 301 auf CANONICAL_HOST.

    Bewusst eng: umgeleitet wird ausschliesslich der Host, der sich vom
    kanonischen nur durch das ``www.`` unterscheidet. Die Railway-Adresse,
    ``localhost`` und jeder andere erlaubte Host bleiben, wie sie sind – eine
    breitere Regel könnte den Deploy-Zugang oder die Health-Checks treffen
    und im schlimmsten Fall eine Endlosschleife bauen. Der kanonische Host
    selbst wird nie umgeleitet, deshalb kann es keine Schleife geben.

    Pfad und Query bleiben erhalten; das Schema ist ``https``, sobald die
    Anfrage sicher ist oder ``SECURE_SSL_REDIRECT`` gilt – so entsteht eine
    einzige Weiterleitung statt der Kette http → https → www.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ziel = kanonischer_host()
        if ziel:
            # get_host() prüft gegen ALLOWED_HOSTS; DisallowedHost wird von
            # Django wie überall sonst zu 400.
            host = (urlsplit('//' + request.get_host()).hostname or '').lower()
            if host == nebenvariante(ziel):
                sicher = request.is_secure() or getattr(settings, 'SECURE_SSL_REDIRECT', False)
                schema = 'https' if sicher else 'http'
                return HttpResponsePermanentRedirect(
                    f'{schema}://{ziel}{request.get_full_path()}'
                )
        return self.get_response(request)


# ═══ CONTENT-SECURITY-POLICY ═══════════════════════════════════════════════

#: Betriebsarten der Richtlinie, gesetzt über ``settings.CSP_MODUS``
#: (Umgebungsvariable ``CSP_MODUS``). Die Erklärung der Quellen und der
#: Reihenfolge report-only → scharf steht in ``mainweb/settings.py``.
CSP_REPORT_ONLY = 'report-only'
CSP_SCHARF = 'scharf'
CSP_AUS = 'aus'

#: Betriebsart → Name der Kopfzeile.
CSP_KOPF = {
    CSP_REPORT_ONLY: 'Content-Security-Policy-Report-Only',
    CSP_SCHARF: 'Content-Security-Policy',
}


def csp_wert(quellen=None, nonce=None):
    """Die Richtlinie als Kopfzeilenwert, ``direktive quelle quelle; …``.

    Mit ``nonce`` bekommt ``script-src`` die Quelle ``'nonce-…'`` angehängt:
    nur Inline-Skripte mit genau diesem ``nonce``-Attribut laufen (SI09).
    """
    if quellen is None:
        quellen = settings.CSP_QUELLEN
    teile = []
    for direktive, werte in quellen.items():
        if nonce and direktive == 'script-src':
            werte = [*werte, f"'nonce-{nonce}'"]
        teile.append(f'{direktive} {" ".join(werte)}')
    return '; '.join(teile)


def neue_nonce():
    """Zufallswert für eine einzelne Antwort – 18 Byte, URL-sicher kodiert."""
    return secrets.token_urlsafe(18)


def csp_kopfname():
    """Name der zu setzenden Kopfzeile oder ``None`` (``CSP_MODUS=aus``).

    Ein unbekannter Wert der Variablen fällt auf Report-Only zurück: ein
    Tippfehler darf weder die Seite blockieren noch die Richtlinie still
    abschalten.
    """
    modus = str(getattr(settings, 'CSP_MODUS', CSP_REPORT_ONLY)).strip().lower()
    if modus == CSP_AUS:
        return None
    return CSP_KOPF.get(modus, CSP_KOPF[CSP_REPORT_ONLY])


class ContentSecurityPolicyMiddleware:
    """Setzt die Content-Security-Policy aus ``settings.CSP_QUELLEN``.

    Eine Kopfzeile, die eine View selbst gesetzt hat, bleibt unangetastet.
    Die Betriebsart wird je Antwort gelesen, damit ein Umschalten von
    ``CSP_MODUS`` ohne Neustart wirkt und Tests beide Kopfzeilen prüfen
    können.

    Jede Anfrage bekommt vor der View eine eigene Nonce
    (``request.csp_nonce``); der Kontextprozessor ``csp_nonce`` reicht sie
    als ``{{ csp_nonce }}`` an die Vorlagen weiter, und dieselbe Nonce steht
    danach im ``script-src`` der Antwort. Eine Nonce gilt nur, solange die
    Seite nicht zwischengespeichert wird – ``cache_page`` liegt deshalb nur
    auf ``sitemap.xml`` und ``llms.txt``, die kein Skript enthalten.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = neue_nonce()
        response = self.get_response(request)
        kopf = csp_kopfname()
        if kopf and not any(response.has_header(k) for k in CSP_KOPF.values()):
            response[kopf] = csp_wert(nonce=request.csp_nonce)
        return response


# ═══ BESUCHSPROTOKOLL ══════════════════════════════════════════════════════

#: Umgebungsvariable, die das Besuchsprotokoll abschaltet. Vorgabe: an.
#: Gedacht für den Fall, dass die pystore-Datenbank hakt – dann wartete
#: sonst jeder Besucher beim synchronen VisitorLog-Schreiben auf den
#: Verbindungstimeout. Wird je Anfrage gelesen, damit ein Umschalten ohne
#: Neustart wirkt und Tests beide Seiten prüfen können.
TRACKING_ENV = 'VISITOR_TRACKING'
_AUS = {'0', 'false', 'off', 'no', 'nein', 'aus'}


def tracking_aktiv():
    """True, solange VISITOR_TRACKING nicht ausdrücklich auf aus steht."""
    return os.getenv(TRACKING_ENV, 'True').strip().lower() not in _AUS


_SKIP = ('/static/', '/media/', '/admin/', '/favicon', '/robots.txt',
         '/sitemap.xml', '/llms.txt', '/health', '/__debug__')

#: Abrufe, die nicht von einem Menschen im Browser kommen. Sie zählen nicht
#: als Besuch; ohne Browserkennung zählt ein Abruf ebenfalls nicht.
_BOT = re.compile(
    r'bot|crawl|spider|slurp|preview|scan|monitor|curl|wget|python|httpx|'
    r'aiohttp|java/|go-http|okhttp|headless|lighthouse|pingdom|uptime|'
    r'facebookexternalhit|whatsapp|telegram|discord|semrush|ahrefs',
    re.IGNORECASE,
)


def ist_bot(ua):
    """True für leere Browserkennungen und bekannte Bots, Crawler, Werkzeuge."""
    return not ua or bool(_BOT.search(ua))


def geraeteklasse(ua):
    """Grobe Geräteklasse und Browserfamilie statt der vollen Kennung.

    Mehr braucht die Statistik nicht; die volle Kennung wäre zusammen mit
    anderen Merkmalen ein Wiedererkennungsmerkmal.
    """
    if re.search(r'iPad|Tablet', ua):
        geraet = 'Tablet'
    elif re.search(r'Mobi|Android|iPhone', ua):
        geraet = 'Handy'
    else:
        geraet = 'Desktop'
    for muster, name in ((r'Edg/', 'Edge'), (r'Firefox/', 'Firefox'),
                         (r'SamsungBrowser/', 'Samsung'), (r'Chrome/', 'Chrome'),
                         (r'Safari/', 'Safari')):
        if re.search(muster, ua):
            return f'{geraet} · {name}'
    return geraet


def tageskennung(ip, ua, datum):
    """Kurzer Schlüssel für „derselbe Besucher heute".

    HMAC über Datum, IP-Adresse und Browserkennung. Die IP-Adresse selbst
    wird nirgends gespeichert, und weil das Datum im Schlüssel steckt, ist
    derselbe Mensch morgen ein anderer Wert. Die Zeilen von gestern löscht
    ``_aufraeumen`` beim ersten Abruf des neuen Tages.
    """
    roh = f'{datum.isoformat()}|{ip}|{ua}'.encode('utf-8')
    return hmac.new(settings.SECRET_KEY.encode('utf-8'), roh, hashlib.sha256).hexdigest()[:16]


_aufgeraeumt_am = None


def _aufraeumen(heute):
    """Löscht Tageskennungen der Vortage – einmal je Prozess und Tag."""
    global _aufgeraeumt_am
    if _aufgeraeumt_am == heute:
        return
    TagesBesucher.objects.filter(datum__lt=heute).delete()
    _aufgeraeumt_am = heute


class PageVisitMiddleware:
    """Zählt Besucher je Tag, ohne Cookie, ohne IP-Adresse, ohne Fremddienst.

    Ein Besucher ist eine Tageskennung (siehe ``tageskennung``). Neue
    Kennung des Tages → ``PageVisit`` +1; neuer Pfad dieser Kennung am Tag →
    ein ``VisitorLog``-Eintrag ohne IP-Adresse, nur mit Geräteklasse. Gezählt
    werden nur erfolgreiche HTML-Abrufe per GET von Browsern, keine Bots und
    kein Vorladen. Die Sitzung wird nicht angefasst, es entsteht also kein
    Cookie. ``VISITOR_TRACKING`` schaltet das Ganze ab.

    Die Sperren gegen Bots (``django-axes``, Drosselung, Spamschutz) sehen
    die IP-Adresse weiterhin im Arbeitsspeicher – davon ist hier nichts
    berührt.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if any(path.startswith(s) for s in _SKIP):
            return response
        if not tracking_aktiv() or not self._zaehlbar(request, response):
            return response
        try:
            self._track(request)
        except Exception as e:
            _log.error('PageVisitMiddleware error: %s', e)
        return response

    @staticmethod
    def _zaehlbar(request, response):
        if request.method != 'GET' or response.status_code != 200:
            return False
        if not response.get('Content-Type', '').startswith('text/html'):
            return False
        vorladen = (request.META.get('HTTP_SEC_PURPOSE', '') + request.META.get('HTTP_PURPOSE', ''))
        if 'prefetch' in vorladen.lower():
            return False
        return not ist_bot(request.META.get('HTTP_USER_AGENT', ''))

    def _track(self, request):
        heute = timezone.localdate()
        _aufraeumen(heute)
        ua = request.META.get('HTTP_USER_AGENT', '')[:500]
        kennung = tageskennung(self._get_ip(request), ua, heute)
        path = request.path[:255]
        site_name = os.getenv('SITE_NAME') or 'luviq'

        neu_heute = not TagesBesucher.objects.filter(datum=heute, kennung=kennung).exists()
        try:
            _, pfad_neu = TagesBesucher.objects.get_or_create(datum=heute, kennung=kennung, pfad=path)
        except IntegrityError:
            # Zwei gleichzeitige Abrufe desselben Besuchers: der andere zählt.
            return
        if neu_heute:
            _, angelegt = PageVisit.objects.get_or_create(date=heute, defaults={'visits': 1})
            if not angelegt:
                PageVisit.objects.filter(date=heute).update(visits=F('visits') + 1)
        if pfad_neu:
            try:
                VisitorLog.objects.create(ip_address=None, path=path,
                                          user_agent=geraeteklasse(ua), seite=site_name)
            except Exception as e:
                _log.error('VisitorLog create error: path=%s err=%s', path, e)

    @staticmethod
    def _get_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
