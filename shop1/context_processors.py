import os
from django.conf import settings
from django.core.cache import cache


def shop_owner_check(request):
    is_shop_owner = False
    if request.user.is_authenticated:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        if request.user.username == admin_username or request.user.is_superuser:
            is_shop_owner = True

    # Cart count
    cart_count = 0
    if request.user.is_authenticated:
        try:
            from .models import Cart
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                cart_count = cart.anzahl_items
        except Exception:
            pass

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
            pass

    return {
        'is_shop_owner': is_shop_owner,
        'cart_count': cart_count,
        'werbung_aktiv': werbung_aktiv,
        'GOOGLE_REVIEW_URL': getattr(settings, 'GOOGLE_REVIEW_URL', ''),
    }
