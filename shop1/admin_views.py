"""Admin/Shopbesitzer-Views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings
from functools import wraps
from django.db.models import Count, Q
import os
from .forms import ProduktForm, AdminUserEditForm, AdminUserCreationForm
from .models import Produkt, UserProfile, Order, OrderItem


def is_admin(user):
    """Prüft ob Benutzer der echte Shopbesitzer (Admin) ist"""
    if not user.is_authenticated:
        return False
    admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
    return user.username == admin_username or user.is_superuser


def is_staff_member(user):
    """Prüft ob Benutzer 'Mitarbeiter' Rechte hat (Produktverwaltung)"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_required(view_func):
    """Decorator - nur 'Admins' (is_staff) können zugreifen"""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(request, 'Du hast keine Berechtigung für diese Admin-Seite.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapped


def product_manager_required(view_func):
    """Decorator - 'Admins' (is_staff) ODER 'Superuser' (is_superuser) können zugreifen"""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not (is_admin(request.user) or is_staff_member(request.user)):
            messages.error(request, 'Du hast keine Berechtigung für die Produktverwaltung.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapped


@product_manager_required
def admin_dashboard(request):
    """Admin/Superuser Dashboard - Übersicht"""
    try:
        produkte_count = Produkt.objects.count()
        aktive_count = Produkt.objects.filter(aktiv=True).count()
        user_count = User.objects.count()

        orders_count = Order.objects.count()
        orders_paid = Order.objects.filter(status='paid').count()
        orders_pending = Order.objects.filter(status='pending').count()
        orders_failed = Order.objects.filter(status='failed').count()
    except Exception as e:
        print(f"Dashboard query error: {e}")
        produkte_count = aktive_count = user_count = orders_count = orders_paid = orders_pending = orders_failed = 0

    try:
        werbung_count = Werbung.objects.count()
        werbung_aktiv_count = Werbung.objects.filter(aktiv=True).count()
    except Exception:
        werbung_count = werbung_aktiv_count = 0

    context = {
        'produkte_count': produkte_count,
        'aktive_count': aktive_count,
        'user_count': user_count,
        'orders_count': orders_count,
        'orders_paid': orders_paid,
        'orders_pending': orders_pending,
        'orders_failed': orders_failed,
        'werbung_count': werbung_count,
        'werbung_aktiv_count': werbung_aktiv_count,
        'is_admin': is_admin(request.user),
        'is_staff_member': is_staff_member(request.user),
    }
    return render(request, 'shop1/admin/dashboard.html', context)


@product_manager_required
def admin_produkte_list(request):
    """Admin/Mitarbeiter - Liste aller Produkte"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_produkte')
        
        if selected_ids and action:
            if action == 'activate':
                Produkt.objects.filter(id__in=selected_ids).update(aktiv=True)
                messages.success(request, f'✅ {len(selected_ids)} Produkte wurden aktiviert!')
            elif action == 'deactivate':
                Produkt.objects.filter(id__in=selected_ids).update(aktiv=False)
                messages.success(request, f'✅ {len(selected_ids)} Produkte wurden deaktiviert!')
            elif action == 'delete':
                count, _ = Produkt.objects.filter(id__in=selected_ids).delete()
                messages.success(request, f'✅ {count} Produkte wurden gelöscht!')
        return redirect('admin_produkte_list')

    produkte = Produkt.objects.all().order_by('-erstellt_am')
    
    context = {
        'produkte': produkte,
    }
    return render(request, 'shop1/admin/produkte_list.html', context)


import logging as _logging
from django.utils import timezone
from datetime import timedelta
import json
from .models import PageVisit, Werbung, WerbungStat, VisitorLog

_log = _logging.getLogger('shop1')


def _upload_werbung_bild(file_obj):
    """Lädt ein Werbebild auf Cloudinary hoch (WERBUNG_CLOUDINARY_URL für separates Konto)."""
    try:
        import cloudinary.uploader
        from urllib.parse import urlparse
        werbung_url = os.getenv('WERBUNG_CLOUDINARY_URL', '')
        kwargs = {'folder': 'werbung', 'resource_type': 'image'}
        if werbung_url:
            p = urlparse(werbung_url)
            kwargs.update({'cloud_name': p.hostname, 'api_key': p.username, 'api_secret': p.password})
        result = cloudinary.uploader.upload(file_obj, **kwargs)
        return result.get('secure_url', '')
    except Exception as e:
        _log.error('werbung cloudinary upload error: %s', e)
        return ''


# ═══ WERBUNG ADMIN ═══

@admin_required
def admin_werbung_list(request):
    """Werbungen verwalten – Budget, Klicks, Views + Charts (nur eigene Kampagnen)."""
    from django.db.models import Sum
    from django.db.models.functions import Lower
    from datetime import timedelta

    site_name = os.getenv('SITE_NAME', 'luviq')

    # Nur Kampagnen dieser Site zeigen (Link enthält SITE_NAME, z.B. 'luviq')
    qs = Werbung.objects.order_by('-erstellt_am')
    if site_name:
        qs = qs.filter(link__icontains=site_name)
    werbungen = list(qs)
    aktiv_count = sum(1 for w in werbungen if w.ist_aktiv)

    SITE_COLORS = {
        'luviq':       '#f97316',
        'pystore':     '#38bdf8',
        'tutorials':   '#4ade80',
        'pixvault':    '#c084fc',
        'familienzone':'#f43f5e',
    }
    FALLBACK_COLORS = ['#fbbf24', '#a78bfa', '#34d399', '#fb923c']
    own_ids = [w.id for w in werbungen]

    # ── Chart 1: Reichweite nach Plattform (Balken, gesamt) ───────────────
    site_breakdown_json = json.dumps({'labels': [], 'views': [], 'klicks': [], 'colors': []})
    try:
        breakdown = list(
            WerbungStat.objects
            .filter(werbung_id__in=own_ids)
            .annotate(seite_norm=Lower('seite'))  # Groß/Kleinschreibung normieren
            .values('seite_norm')
            .annotate(total_v=Sum('impressionen'), total_k=Sum('klicks'))
            .order_by('seite_norm')
        )
        colors = [
            SITE_COLORS.get(s['seite_norm'], FALLBACK_COLORS[i % len(FALLBACK_COLORS)])
            for i, s in enumerate(breakdown)
        ]
        site_breakdown_json = json.dumps({
            'labels': [s['seite_norm'].capitalize() for s in breakdown],
            'views':  [s['total_v'] for s in breakdown],
            'klicks': [s['total_k'] for s in breakdown],
            'colors': colors,
        })
    except Exception as e:
        _log.error('site_breakdown error: %s', e)

    # ── Chart 2: Tagesverlauf – Views & Klicks der letzten 30 Tage ───────
    timeline_json = json.dumps({'labels': [], 'views': [], 'klicks': []})
    try:
        today = timezone.localdate()
        start_date = today - timedelta(days=29)
        day_labels = [(start_date + timedelta(days=i)).strftime('%d.%m.') for i in range(30)]

        timeline_qs = (
            WerbungStat.objects
            .filter(datum__gte=start_date, werbung_id__in=own_ids)
            .values('datum')
            .annotate(v=Sum('impressionen'), k=Sum('klicks'))
            .order_by('datum')
        )
        day_views, day_klicks = {}, {}
        for entry in timeline_qs:
            lbl = entry['datum'].strftime('%d.%m.')
            day_views[lbl]  = day_views.get(lbl, 0)  + entry['v']
            day_klicks[lbl] = day_klicks.get(lbl, 0) + entry['k']

        timeline_json = json.dumps({
            'labels': day_labels,
            'views':  [day_views.get(l, 0)  for l in day_labels],
            'klicks': [day_klicks.get(l, 0) for l in day_labels],
        })
    except Exception as e:
        _log.error('timeline error: %s', e)

    context = {
        'werbungen': werbungen,
        'aktiv_count': aktiv_count,
        'site_breakdown_json': site_breakdown_json,
        'timeline_json': timeline_json,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'shop1/admin/werbung_list.html', context)


@admin_required
def admin_werbung_create(request):
    """Neue Werbung anlegen (POST only). Bild per Upload oder URL."""
    if request.method == 'POST':
        titel = request.POST.get('titel', '').strip()
        link = request.POST.get('link', '').strip()
        beschreibung = request.POST.get('beschreibung', '').strip()
        bild = request.POST.get('bild', '').strip()
        budget_str = request.POST.get('budget', '0').replace(',', '.')
        try:
            budget = float(budget_str)
        except (ValueError, TypeError):
            budget = 0.0

        # Bild: Upload hat Vorrang vor manuell eingetragener URL
        if not bild and 'bild_file' in request.FILES:
            bild = _upload_werbung_bild(request.FILES['bild_file'])

        if not titel or not link:
            messages.error(request, 'Titel und Link sind Pflichtfelder.')
            return redirect('admin_werbung_list')

        try:
            Werbung.objects.create(
                titel=titel,
                link=link,
                beschreibung=beschreibung,
                bild=bild,
                budget=budget,
                aktiv=True,
            )
            messages.success(request, f'Werbung "{titel}" wurde erstellt.')
        except Exception as e:
            messages.error(request, f'Fehler beim Erstellen: {e}')
    return redirect('admin_werbung_list')


@admin_required
def admin_werbung_delete(request, werbung_id):
    """Werbung löschen (POST only)."""
    if request.method == 'POST':
        w = get_object_or_404(Werbung, id=werbung_id)
        titel = w.titel
        try:
            w.delete()
            messages.success(request, f'Werbung "{titel}" wurde gelöscht.')
        except Exception as e:
            messages.error(request, f'Fehler beim Löschen: {e}')
    return redirect('admin_werbung_list')


@admin_required
def admin_reset_werbung_stats(request):
    """Setzt Werbungs-Statistiken dieser Site auf 0 zurück (nur eigene Kampagnen)."""
    if request.method == 'POST':
        try:
            site_name = os.getenv('SITE_NAME', 'luviq')
            own_qs = Werbung.objects.filter(link__icontains=site_name)
            own_ids = list(own_qs.values_list('id', flat=True))
            own_qs.update(impressionen=0, klicks=0)
            WerbungStat.objects.filter(werbung_id__in=own_ids).delete()
            messages.success(request, 'Werbungs-Statistiken dieser Site wurden zurückgesetzt.')
        except Exception as e:
            messages.error(request, f'Fehler beim Zurücksetzen: {e}')
    return redirect('admin_werbung_list')


@admin_required
def admin_werbung_toggle(request, werbung_id):
    """Schaltet Aktiv-Status einer Werbung um."""
    if request.method == 'POST':
        w = get_object_or_404(Werbung, id=werbung_id)
        w.aktiv = not w.aktiv
        w.save(update_fields=['aktiv'])
        status = 'aktiviert' if w.aktiv else 'pausiert'
        messages.success(request, f'Werbung "{w.titel}" wurde {status}.')
    return redirect('admin_werbung_list')


@admin_required
def admin_werbung_edit(request, werbung_id):
    """Werbung-Felder inline bearbeiten (POST only)."""
    if request.method == 'POST':
        w = get_object_or_404(Werbung, id=werbung_id)
        w.titel = request.POST.get('titel', w.titel).strip() or w.titel
        w.link = request.POST.get('link', w.link).strip() or w.link
        w.beschreibung = request.POST.get('beschreibung', w.beschreibung)
        bild = request.POST.get('bild', '').strip()
        if not bild and 'bild_file' in request.FILES:
            bild = _upload_werbung_bild(request.FILES['bild_file'])
        if bild:
            w.bild = bild
        try:
            w.budget = float(request.POST.get('budget', w.budget))
        except (ValueError, TypeError):
            pass
        aktiv_val = request.POST.get('aktiv')
        w.aktiv = aktiv_val == '1'
        w.save()
        messages.success(request, f'Werbung "{w.titel}" gespeichert.')
    return redirect('admin_werbung_list')


def _geo_enrich_visitors(visitors):
    """Batch geo-enrich visitor log entries that have no country yet."""
    import urllib.request
    import json as _json

    PRIVATE = ('127.', '10.', '192.168.', '::1', '172.16.', '172.17.',
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

    to_enrich = [v for v in visitors
                 if not v.country and v.ip_address
                 and not any(str(v.ip_address).startswith(p) for p in PRIVATE)]
    if not to_enrich:
        return
    ips = [str(v.ip_address) for v in to_enrich[:10]]
    ip_to_obj = {str(v.ip_address): v for v in to_enrich[:10]}
    _log.debug('geo_enrich_visitors: querying %d IPs: %s', len(ips), ips)
    try:
        body = _json.dumps([{'query': ip} for ip in ips]).encode('utf-8')
        req = urllib.request.Request(
            'http://ip-api.com/batch?fields=query,status,country,countryCode,city',
            data=body, headers={'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            results = _json.loads(resp.read())
        _log.debug('geo_enrich_visitors: got %d results', len(results))
        for r in results:
            ip = r.get('query')
            v = ip_to_obj.get(ip)
            if v and r.get('status') == 'success':
                v.country = r.get('country', '')
                v.country_code = r.get('countryCode', '')
                v.city = r.get('city', '')
                VisitorLog.objects.filter(pk=v.pk).update(
                    country=v.country, country_code=v.country_code, city=v.city,
                )
            elif v:
                _log.warning('geo_enrich_visitors: ip-api fail ip=%s status=%s', ip, r.get('status'))
    except Exception as e:
        _log.error('geo_enrich_visitors: batch failed: %s', e)


@admin_required
def admin_stats(request):
    """Statistik-Seite mit Benutzerverwaltung und Bestellungen"""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    
    # --- CHART DATA: Besuche der letzten 30 Tage ---
    try:
        today = timezone.localdate()
        start_date = today - timedelta(days=29)
        
        # Lade existierende Besuche aus der Datenbank
        visits_qs = PageVisit.objects.filter(date__gte=start_date).order_by('date')
        visits_dict = {v.date: v.visits for v in visits_qs}
        
        labels = []
        data = []
        
        # Fülle Lücken für Tage ohne Besuche mit 0 auf
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            labels.append(current_date.strftime("%d.%m."))
            data.append(visits_dict.get(current_date, 0))
            
        chart_data_json = json.dumps({'labels': labels, 'data': data})
    except Exception as e:
        print(f"Error in chart calculation: {e}")
        chart_data_json = json.dumps({'labels': [], 'data': []})

    
    # Order-Statistiken
    orders = Order.objects.select_related('user').prefetch_related('items').all().order_by('-erstellt_am')
    orders_paid = orders.filter(status='paid')
    orders_pending = orders.filter(status='pending')
    orders_failed = orders.filter(status='failed')
    
    # Umsatz & Rabatte berechnen
    total_revenue = 0
    total_discounts = 0
    try:
        for order in orders_paid:
            rev = float(order.gesamt_betrag or 0)
            total_revenue += rev
            
            # Berechne Rabatt basierend auf Item-Summe vs Bezahltem Betrag
            items_sum = sum(float((item.produkt_preis or 0) * (item.menge or 1)) for item in order.items.all())
            if items_sum > rev:
                total_discounts += (items_sum - rev)
    except Exception as e:
        print(f"Error in revenue calculation: {e}")
    
    recent_visitors = []
    total_visitor_logs = 0
    try:
        site_name = os.getenv('SITE_NAME', 'luviq')
        # pystore zeigt alle Sites; andere Sites nur ihre eigenen Einträge
        if site_name == 'pystore':
            visitor_qs = VisitorLog.objects
        else:
            visitor_qs = VisitorLog.objects.filter(seite=site_name)
        visitors = list(visitor_qs.order_by('-timestamp')[:30])
        _log.debug('admin_stats: loaded %d visitor log entries (site=%s)', len(visitors), site_name)
        _geo_enrich_visitors(visitors)
        recent_visitors = visitors
        total_visitor_logs = visitor_qs.count()
    except Exception as e:
        _log.error('admin_stats: visitor log error: %s', e)

    context = {
        'users': users,
        'orders': orders,
        'orders_paid': orders_paid,
        'orders_pending': orders_pending,
        'orders_failed': orders_failed,
        'total_orders': orders.count(),
        'total_revenue': total_revenue,
        'total_discounts': total_discounts,
        'chart_data_json': chart_data_json,
        'recent_visitors': recent_visitors,
        'total_visitor_logs': total_visitor_logs,
    }
    return render(request, 'shop1/admin/stats.html', context)


@admin_required
def admin_reset_visits(request):
    """Löscht alle Seitenbesuche aus der Statistik"""
    if request.method == 'POST':
        PageVisit.objects.all().delete()
        messages.success(request, '✅ Seitenbesuche-Statistik wurde erfolgreich zurückgesetzt.')
    return redirect('admin_stats')


@admin_required
def admin_reset_orders(request):
    """Löscht alle Bestellungen aus der Statistik"""
    if request.method == 'POST':
        Order.objects.all().delete()
        messages.success(request, '✅ Alle Bestellungen wurden erfolgreich gelöscht.')
    return redirect('admin_stats')


@admin_required
def admin_user_create(request):
    """Admin - Neuen Benutzer anlegen"""
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'✅ Benutzer "{user.username}" erfolgreich erstellt!')
            return redirect('admin_stats')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'shop1/admin/user_create.html', {'form': form})


@admin_required
def admin_user_edit(request, user_id):
    """Admin - Benutzer bearbeiten"""
    edit_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=edit_user)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Benutzer "{edit_user.username}" erfolgreich aktualisiert!')
            return redirect('admin_stats')
    else:
        form = AdminUserEditForm(instance=edit_user)
    
    return render(request, 'shop1/admin/user_edit.html', {
        'edit_user': edit_user,
        'form': form,
    })


@admin_required
def admin_produkt_toggle(request, produkt_id):
    """Schaltet den Aktiv-Status eines Produkts um."""
    produkt = get_object_or_404(Produkt, id=produkt_id)
    produkt.aktiv = not produkt.aktiv
    produkt.save()
    status_str = "aktiviert" if produkt.aktiv else "deaktiviert"
    messages.success(request, f'✅ Produkt "{produkt.name}" wurde erfolgreich {status_str}!')
    return redirect('admin_produkte_list')


@admin_required
def admin_newsletter_reset(request, produkt_id):
    """Setzt den Newsletter-Status eines Produkts zurück."""
    produkt = get_object_or_404(Produkt, id=produkt_id)
    produkt.newsletter_gesendet = False
    produkt.save()
    messages.success(request, f'✅ Newsletter-Status für "{produkt.name}" wurde zurückgesetzt.')
    return redirect('admin_produkte_list')


@admin_required
def admin_resend_newsletter(request, produkt_id):
    """Ermöglicht das manuelle erneute Senden eines Newsletters für ein Produkt."""
    produkt = get_object_or_404(Produkt, id=produkt_id)
    from .models import Subscriber
    from .utils import send_newsletter_email
    
    subscribers = Subscriber.objects.all()
    if subscribers.exists():
        send_newsletter_email(produkt, subscribers)
        produkt.newsletter_gesendet = True
        produkt.save()
        messages.success(request, f'🚀 Newsletter für "{produkt.name}" wurde erfolgreich an alle Abonnenten gesendet!')
    else:
        messages.warning(request, 'Es gibt aktuell keine Newsletter-Abonnenten.')
        
    return redirect('admin_produkte_list')


@admin_required
def admin_user_delete(request, user_id):
    """Admin - Benutzer löschen"""
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Verhindern, dass man sich selbst löscht
    if user_to_delete == request.user:
        messages.error(request, '❌ Du kannst dich nicht selbst löschen!')
        return redirect('admin_stats')
        
    # Verhindern, dass der Haupt-Admin (Shopbesitzer) gelöscht wird
    admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
    if user_to_delete.username == admin_username:
        messages.error(request, '❌ Der Haupt-Admin Account kann nicht gelöscht werden!')
        return redirect('admin_stats')

    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'✅ Benutzer "{username}" erfolgreich gelöscht!')
        return redirect('admin_stats')
    
    return render(request, 'shop1/admin/user_delete.html', {'delete_user': user_to_delete})


@admin_required
def admin_user_cart(request, user_id):
    """Admin - Warenkorb eines Benutzers einsehen"""
    user_to_view = get_object_or_404(User, id=user_id)
    from .models import Cart, Produkt
    cart, created = Cart.objects.get_or_create(user=user_to_view)
    items = cart.items.all()
    
    # Ergänze die Items um die echten Produkt-Objekte aus der DB für die Bilder
    enriched_items = []
    for item in items:
        # Versuche das Produkt anhand des Namens zu finden
        db_produkt = Produkt.objects.filter(name=item.produkt_name).first()
        enriched_items.append({
            'item': item,
            'db_produkt': db_produkt
        })
    
    total = sum(item.produkt_preis * item.menge for item in items)
    
    context = {
        'view_user': user_to_view,
        'enriched_items': enriched_items,
        'total': total,
    }
    return render(request, 'shop1/admin/user_cart_detail.html', context)


@product_manager_required
def admin_produkt_upload(request):
    """Admin/Superuser - Neues Produkt hochladen"""
    if request.method == 'POST':
        form = ProduktForm(request.POST, request.FILES)
        if form.is_valid():
            produkt = form.save(commit=False)
            produkt.ersteller = request.user
            produkt.save()
            messages.success(request, f'✅ Produkt "{produkt.name}" erfolgreich erstellt!')
            
            # NEWSLETTER: Nur wenn Checkbox aktiviert ist
            if form.cleaned_data.get('send_newsletter'):
                from .models import Subscriber
                from .utils import send_newsletter_email
                subscribers = Subscriber.objects.all()
                if subscribers.exists():
                    send_newsletter_email(produkt, subscribers)
                    produkt.newsletter_gesendet = True
                    produkt.save()
                    messages.info(request, '📧 Newsletter-Update wurde an alle Abonnenten gesendet.')
            
            return redirect('admin_produkte_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProduktForm()
    
    context = {
        'form': form,
    }
    return render(request, 'shop1/admin/produkt_upload.html', context)


@product_manager_required
def admin_produkt_edit(request, produkt_id):
    """Admin/Superuser - Produkt bearbeiten"""
    produkt = get_object_or_404(Produkt, id=produkt_id)
    
    if request.method == 'POST':
        form = ProduktForm(request.POST, request.FILES, instance=produkt)
        if form.is_valid():
            produkt = form.save()
            messages.success(request, f'✅ Produkt "{produkt.name}" wurde aktualisiert!')
            
            # Optional: Erneut Newsletter schicken wenn Checkbox in Edit-Form (falls wir sie dort auch wollen)
            if form.cleaned_data.get('send_newsletter'):
                from .models import Subscriber
                from .utils import send_newsletter_email
                subscribers = Subscriber.objects.all()
                if subscribers.exists():
                    send_newsletter_email(produkt, subscribers)
                    produkt.newsletter_gesendet = True
                    produkt.save()
                    messages.info(request, '📧 Newsletter-Update wurde erneut gesendet.')
            
            return redirect('admin_produkte_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = ProduktForm(instance=produkt)
    
    context = {
        'form': form,
        'produkt': produkt,
    }
    return render(request, 'shop1/admin/produkt_edit.html', context)


@product_manager_required
def admin_produkt_delete(request, produkt_id):
    """Admin/Superuser - Produkt löschen"""
    produkt = get_object_or_404(Produkt, id=produkt_id)
    
    if request.method == 'POST':
        produkt_name = produkt.name
        produkt.delete()
        messages.success(request, f'✅ Produkt "{produkt_name}" erfolgreich gelöscht!')
        return redirect('admin_produkte_list')
    
    context = {
        'produkt': produkt,
    }
    return render(request, 'shop1/admin/produkt_delete.html', context)
@admin_required
def admin_orders_list(request):
    """Admin - Liste aller Bestellungen"""
    status_filter = request.GET.get('status')
    try:
        orders = Order.objects.select_related('user').prefetch_related('items').all().order_by('-erstellt_am')
        
        if status_filter:
            orders = orders.filter(status=status_filter)
    except Exception as e:
        print(f"Orders list error: {e}")
        orders = []
        
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'shop1/admin/orders_list.html', context)


@admin_required
def admin_order_detail(request, order_id):
    """Admin - Detailansicht einer Bestellung mit Status-Update"""
    try:
        order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id)
    except Exception as e:
        messages.error(request, f"Fehler beim Laden der Bestellung: {e}")
        return redirect('admin_orders_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            if new_status in dict(Order.STATUS_CHOICES):
                order.status = new_status
                order.save()
                
                # Wenn auf "Bezahlt" gesetzt wird -> Artikel deaktivieren
                if new_status == 'paid':
                    for item in order.items.all():
                        db_produkt = Produkt.objects.filter(name=item.produkt_name).first()
                        if db_produkt:
                            db_produkt.aktiv = False
                            db_produkt.save()
                
                messages.success(request, f'✅ Status für Bestellung #{order.id} wurde auf "{order.get_status_display()}" aktualisiert!')
            return redirect('admin_order_detail', order_id=order.id)
            
    # Produkte in der DB finden für Bilder
    items_with_products = []
    for item in order.items.all():
        db_produkt = Produkt.objects.filter(name=item.produkt_name).first()
        items_with_products.append({
            'item': item,
            'db_produkt': db_produkt
        })
        
    context = {
        'order': order,
        'items_with_products': items_with_products,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'shop1/admin/order_detail.html', context)


@admin_required
def admin_order_delete(request, order_id):
    """Admin - Bestellung löschen"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        order_id_display = order.id
        order.delete()
        messages.success(request, f'✅ Bestellung #{order_id_display} wurde dauerhaft gelöscht.')
        return redirect('admin_orders_list')
    
    return render(request, 'shop1/admin/order_delete.html', {'order': order})
