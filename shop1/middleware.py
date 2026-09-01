import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone
from django.db.models import F
from .models import PageVisit, VisitorLog

_log = logging.getLogger('shop1')

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


#: Geo-Lookups laufen in einem festen, kleinen Pool statt in einem neuen
#: Betriebssystem-Thread je Seitenaufruf. Die Semaphore zählt die belegten
#: Plätze: ist der Pool voll, entfällt der Lookup für diesen Eintrag –
#: Land und Stadt bleiben dann leer, die Antwort wartet nie.
GEO_PLAETZE = 4
_geo_pool = ThreadPoolExecutor(max_workers=GEO_PLAETZE, thread_name_prefix='geo')
_geo_frei = threading.BoundedSemaphore(GEO_PLAETZE)

_SKIP = ('/static/', '/media/', '/admin/', '/favicon', '/robots.txt',
         '/sitemap.xml', '/llms.txt', '/health', '/__debug__')

_PRIVATE = ('127.', '10.', '192.168.', '::1', '172.16.', '172.17.',
            '172.18.', '172.19.', '172.20.', '172.21.', '172.22.',
            '172.23.', '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.',
            '100.64.', '100.65.', '100.66.', '100.67.', '100.68.',
            '100.69.', '100.70.', '100.71.', '100.72.', '100.73.',
            '100.74.', '100.75.', '100.76.', '100.77.', '100.78.',
            '100.79.', '100.80.', '100.81.', '100.82.', '100.83.',
            '100.84.', '100.85.', '100.86.', '100.87.', '100.88.',
            '100.89.', '100.90.', '100.91.', '100.92.', '100.93.',
            '100.94.', '100.95.', '100.96.', '100.97.', '100.98.',
            '100.99.', '100.100.', '100.101.', '100.102.', '100.103.',
            '100.104.', '100.105.', '100.106.', '100.107.', '100.108.',
            '100.109.', '100.110.', '100.111.', '100.112.', '100.113.',
            '100.114.', '100.115.', '100.116.', '100.117.', '100.118.',
            '100.119.', '100.120.', '100.121.', '100.122.', '100.123.',
            '100.124.', '100.125.', '100.126.', '100.127.')


def _geo_einreihen(log_pk, ip):
    """Reiht den Geo-Lookup in den Pool ein; False, wenn er ausgelassen wird.

    Ausgelassen wird er für leere und private Adressen (dafür gibt es nichts
    nachzuschlagen) und wenn alle GEO_PLAETZE belegt sind. Den Platz gibt
    ``_geo_enrich`` am Ende wieder frei.
    """
    if not ip or any(ip.startswith(p) for p in _PRIVATE):
        return False
    if not _geo_frei.acquire(blocking=False):
        _log.info('Geo-Lookup ausgelassen, Pool voll: pk=%s ip=%s', log_pk, ip)
        return False
    try:
        _geo_pool.submit(_geo_enrich, log_pk, ip)
    except RuntimeError:
        # Pool bereits heruntergefahren (Prozessende) – Platz zurückgeben.
        _geo_frei.release()
        return False
    return True


def _geo_enrich(log_pk, ip):
    """Pool-Thread: Geo-Daten nachschlagen und VisitorLog aktualisieren.

    VisitorLog wird via WerbungRouter in pystore-DB geschrieben – Connection
    muss im Thread explizit verwaltet werden. Läuft nur über
    ``_geo_einreihen``; das ``finally`` gibt den Pool-Platz zurück.
    """
    from django.db import close_old_connections, connections
    import urllib.request as _req
    import json as _json
    try:
        close_old_connections()
        url = f'http://ip-api.com/json/{ip}?fields=status,country,countryCode,city'
        with _req.urlopen(url, timeout=4) as resp:
            data = _json.loads(resp.read())
        if data.get('status') == 'success':
            VisitorLog.objects.filter(pk=log_pk).update(
                country=data.get('country', ''),
                country_code=data.get('countryCode', ''),
                city=data.get('city', ''),
            )
            _log.debug('_geo_enrich: ok pk=%s ip=%s city=%s', log_pk, ip, data.get('city'))
        else:
            _log.warning('_geo_enrich: ip-api fail ip=%s status=%s', ip, data.get('status'))
    except Exception as e:
        _log.warning('_geo_enrich: error ip=%s: %s', ip, e)
    finally:
        try:
            connections['pystore'].close()
        except Exception:
            pass
        _geo_frei.release()


class PageVisitMiddleware:
    """Zählt Besuche (PageVisit, VisitorLog) nach jeder Antwort.

    Die Datenbankschreibvorgänge laufen bewusst synchron im Anfragezyklus:
    sie hängen an der Session (``visited_paths``, ``last_visit_date``), und
    ein Thread machte die Reihenfolge der Session-Schreibvorgänge
    unbestimmt. Nur der Geo-Lookup läuft nebenher, im festen Pool oben.
    ``VISITOR_TRACKING`` schaltet das Ganze ab.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if any(path.startswith(s) for s in _SKIP):
            return response
        if not tracking_aktiv():
            return response
        try:
            self._track(request)
        except Exception as e:
            _log.error('PageVisitMiddleware error: %s', e)
        return response

    def _track(self, request):
        today = timezone.localdate()
        today_str = today.isoformat()
        ip = self._get_ip(request)
        path = request.path[:255]
        ua = request.META.get('HTTP_USER_AGENT', '')[:500]
        site_name = os.getenv('SITE_NAME') or 'luviq'

        # ── PageVisit: once per session per day ──
        if request.session.get('last_visit_date') != today_str:
            try:
                v, created = PageVisit.objects.get_or_create(
                    date=today, defaults={'visits': 1}
                )
                if not created:
                    PageVisit.objects.filter(date=today).update(visits=F('visits') + 1)
                request.session['last_visit_date'] = today_str
            except Exception as e:
                _log.error('PageVisit error: %s', e)

        # ── VisitorLog: one entry per unique path per session (5-min window) ──
        # 5 Minuten, nicht 30: massgeblich ist "diff < 300" weiter unten.
        visited = request.session.get('visited_paths', {})
        now_iso = timezone.now().isoformat()
        last_seen = visited.get(path, '')
        should_log = True

        if last_seen:
            try:
                from datetime import datetime
                last_dt = datetime.fromisoformat(last_seen)
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.get_current_timezone())
                diff = (timezone.now() - last_dt).total_seconds()
                if diff < 300:
                    should_log = False
            except Exception:
                _log.exception('Zeitstempel in visited_paths nicht lesbar: %r', last_seen)

        # ── Admin-Benachrichtigung pro Seitenbesuch: bewusst deaktiviert. ──
        # Frueher wurde hier pro (vermeintlich neuem) Besucher eine Admin-Mail
        # verschickt. Das hat trotz Bot-Filter/Session-Dedup zu einer Mail-Flut
        # gefuehrt (Clients/Bots ohne Cookies gelten bei jedem Hit als "neu")
        # und Brevo ueberlastet. Besucher werden weiterhin still in VisitorLog
        # protokolliert (Admin-Dashboard), aber ohne E-Mail-Versand.

        if should_log:
            try:
                log_obj = VisitorLog.objects.create(
                    ip_address=ip,
                    path=path,
                    user_agent=ua,
                    seite=site_name,
                )
                visited[path] = now_iso
                if len(visited) > 40:
                    visited = dict(sorted(visited.items(), key=lambda x: x[1], reverse=True)[:40])
                request.session['visited_paths'] = visited
                request.session.modified = True
                _log.info('VisitorLog created: ip=%s path=%s site=%s', ip, path, site_name)
                _geo_einreihen(log_obj.pk, ip)
            except Exception as e:
                _log.error('VisitorLog create error: ip=%s path=%s err=%s', ip, path, e)

    @staticmethod
    def _get_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
