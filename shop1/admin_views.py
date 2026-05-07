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
    """Prüft ob Benutzer 'Admin' Rechte hat (Statistiken & alles)"""
    return user.is_authenticated and user.is_staff


def is_superuser(user):
    """Prüft ob Benutzer 'Mitarbeiter' Rechte hat (Nur Produktverwaltung)"""
    return user.is_authenticated and user.is_superuser


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
        if not (is_admin(request.user) or is_superuser(request.user)):
            messages.error(request, 'Du hast keine Berechtigung für die Produktverwaltung.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapped


@product_manager_required
def admin_dashboard(request):
    """Admin/Superuser Dashboard - Übersicht"""
    produkte_count = Produkt.objects.count()
    aktive_count = Produkt.objects.filter(aktiv=True).count()
    user_count = User.objects.count()
    
    # Order-Statistiken
    orders_count = Order.objects.count()
    orders_paid = Order.objects.filter(status='paid').count()
    orders_pending = Order.objects.filter(status='pending').count()
    orders_failed = Order.objects.filter(status='failed').count()
    
    context = {
        'produkte_count': produkte_count,
        'aktive_count': aktive_count,
        'user_count': user_count,
        'orders_count': orders_count,
        'orders_paid': orders_paid,
        'orders_pending': orders_pending,
        'orders_failed': orders_failed,
        'is_admin': is_admin(request.user),
        'is_superuser': is_superuser(request.user),
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


from django.utils import timezone
from datetime import timedelta
import json
from .models import PageVisit

@admin_required
def admin_stats(request):
    """Statistik-Seite mit Benutzerverwaltung und Bestellungen"""
    users = User.objects.all().order_by('-date_joined')
    
    # --- CHART DATA: Besuche der letzten 30 Tage ---
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

    
    # Order-Statistiken
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-erstellt_am')
    orders_paid = orders.filter(status='paid')
    orders_pending = orders.filter(status='pending')
    orders_failed = orders.filter(status='failed')
    
    # Umsatz & Rabatte berechnen
    total_revenue = 0
    total_discounts = 0
    for order in orders_paid:
        total_revenue += float(order.gesamt_betrag)
        items_sum = sum(float(item.produkt_preis * item.menge) for item in order.items.all())
        total_discounts += (items_sum - float(order.gesamt_betrag))
    
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
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_to_edit)
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
