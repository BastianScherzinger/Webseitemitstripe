import logging
import os
import threading
from django.utils import timezone
from django.db.models import F
from .models import PageVisit, VisitorLog

_log = logging.getLogger('shop1')

_SKIP = ('/static/', '/media/', '/admin/', '/favicon', '/robots.txt',
         '/sitemap.xml', '/health', '/__debug__')

_PRIVATE = ('127.', '10.', '192.168.', '::1', '172.16.', '172.17.',
            '172.18.', '172.19.', '172.20.', '172.21.', '172.22.',
            '172.23.', '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.')


def _geo_enrich(log_pk, ip):
    """Background thread: look up geo data for a local VisitorLog entry."""
    import urllib.request as _req
    import json as _json
    try:
        if not ip or any(ip.startswith(p) for p in _PRIVATE):
            return
        url = f'https://ip-api.com/json/{ip}?fields=status,country,countryCode,city'
        with _req.urlopen(url, timeout=4) as resp:
            data = _json.loads(resp.read())
        if data.get('status') == 'success':
            VisitorLog.objects.filter(pk=log_pk).update(
                country=data.get('country', ''),
                country_code=data.get('countryCode', ''),
                city=data.get('city', ''),
            )
    except Exception:
        pass


def _mirror_to_pystore(ip, path, ua, seite):
    """Background thread: Schreibt den Besuch zusätzlich in die pystore-DB.

    Nur aktiv wenn PYSTORE_DATABASE_URL gesetzt ist (separate DB).
    """
    import urllib.request as _req
    import json as _json
    try:
        from .models import PyStoreVisitorLog
        log_obj = PyStoreVisitorLog.objects.using('pystore').create(
            ip_address=ip,
            path=path,
            user_agent=ua,
            seite=seite,
        )
        # Geo-Anreicherung auch für pystore-Eintrag
        if ip and not any(ip.startswith(p) for p in _PRIVATE):
            try:
                url = f'https://ip-api.com/json/{ip}?fields=status,country,countryCode,city'
                with _req.urlopen(url, timeout=4) as resp:
                    data = _json.loads(resp.read())
                if data.get('status') == 'success':
                    PyStoreVisitorLog.objects.using('pystore').filter(pk=log_obj.pk).update(
                        country=data.get('country', ''),
                        country_code=data.get('countryCode', ''),
                        city=data.get('city', ''),
                    )
            except Exception:
                pass
    except Exception as e:
        _log.error('PyStoreVisitorLog mirror error: %s', e)


class PageVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        path = request.path
        if any(path.startswith(s) for s in _SKIP):
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
        site_name = os.getenv('SITE_NAME', 'pystore')

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

        # ── VisitorLog: one entry per unique path per session (30-min window) ──
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
                if diff < 1800:
                    should_log = False
            except Exception:
                pass

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
                _log.debug('VisitorLog created: ip=%s path=%s site=%s', ip, path, site_name)
                threading.Thread(target=_geo_enrich, args=(log_obj.pk, ip), daemon=True).start()

                # Spiegle den Eintrag zusätzlich in die pystore-DB (sichtbar in pystore-Admin)
                if os.getenv('PYSTORE_DATABASE_URL'):
                    threading.Thread(
                        target=_mirror_to_pystore,
                        args=(ip, path, ua, site_name),
                        daemon=True,
                    ).start()
            except Exception as e:
                _log.error('VisitorLog create error: ip=%s path=%s err=%s', ip, path, e)

    @staticmethod
    def _get_ip(request):
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
