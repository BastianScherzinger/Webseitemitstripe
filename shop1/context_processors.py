import logging
import os
from django.conf import settings
from django.core.cache import cache

from .seiten_stand import seite_fuer

_log = logging.getLogger('shop1')


def shop_owner_check(request):
    is_shop_owner = False
    if request.user.is_authenticated:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        if request.user.username == admin_username or request.user.is_superuser:
            is_shop_owner = True

    # Warenkorb-Zähler im Kopf jeder Seite. Läuft bei jedem Abruf eines
    # angemeldeten Nutzers – deshalb eine einzige SUM-Abfrage über die Posten
    # statt Warenkorb laden und die Posten in Python aufsummieren (zwei
    # Abfragen plus Objektaufbau). Ohne Warenkorb oder ohne Posten ergibt
    # SUM NULL, daraus wird 0 – wie bisher.
    cart_count = 0
    if request.user.is_authenticated:
        try:
            from django.db.models import Sum
            from .models import CartItem
            cart_count = CartItem.objects.filter(
                cart__user=request.user
            ).aggregate(summe=Sum('menge'))['summe'] or 0
        except Exception:
            _log.exception('Warenkorb-Zählung im Context Processor fehlgeschlagen')

    # Aktive Werbung aus Cache
    werbung_aktiv = []
    _skip = ('/static/', '/shop-admin/', '/admin/', '/media/', '/favicon')
    if not any(request.path.startswith(s) for s in _skip):
        try:
            cache_key = 'werbung_aktiv_list'
            werbung_aktiv = cache.get(cache_key)
            if werbung_aktiv is None:
                from .models import Werbung
                werbung_aktiv = [w for w in Werbung.objects.filter(aktiv=True) if w.ist_aktiv]
                cache.set(cache_key, werbung_aktiv, 60)
        except Exception:
            _log.exception('Aktive Werbung konnte nicht geladen werden')

    # Stand der aktuellen Seite für den WebPage-Knoten in base.html: reines
    # Nachschlagen im Register, kein Datenbankzugriff. resolver_match fehlt
    # bei Fehlerseiten, url_name bei namenlosen Routen – beides ergibt None,
    # und base.html lässt name/dateModified dann weg.
    treffer = getattr(request, 'resolver_match', None)
    seite = seite_fuer(treffer.url_name if treffer else None)

    return {
        'is_shop_owner': is_shop_owner,
        'cart_count': cart_count,
        'werbung_aktiv': werbung_aktiv,
        'GOOGLE_REVIEW_URL': getattr(settings, 'GOOGLE_REVIEW_URL', ''),
        'seite': seite,
    }
