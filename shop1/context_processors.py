import os
from django.db.models import F
from django.utils import timezone


def shop_owner_check(request):
    is_shop_owner = False
    if request.user.is_authenticated:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        if request.user.username == admin_username or request.user.is_superuser:
            is_shop_owner = True

    # ═══ WERBUNG: Impressionen zählen + aktive Ads für Templates bereitstellen ═══
    werbung_aktiv = []
    if '/shop-admin/' not in request.path and '/static/' not in request.path:
        try:
            from .models import Werbung, WerbungStat
            site_name = os.getenv('SITE_NAME', 'luviq')
            today = timezone.now().date()
            for w in Werbung.objects.filter(aktiv=True):
                w.refresh_from_db()
                if w.ist_aktiv:
                    Werbung.objects.filter(id=w.id).update(impressionen=F('impressionen') + 1)
                    stat, _ = WerbungStat.objects.get_or_create(
                        werbung=w, seite=site_name, datum=today
                    )
                    WerbungStat.objects.filter(id=stat.id).update(impressionen=F('impressionen') + 1)
                    werbung_aktiv.append(w)
        except Exception:
            pass

    return {
        'is_shop_owner': is_shop_owner,
        'werbung_aktiv': werbung_aktiv,
    }
