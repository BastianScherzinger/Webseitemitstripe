"""Warenkorb-Views: hinzufügen, entfernen, aktualisieren, anzeigen."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Produkt
from ._helpers import _get_or_create_cart


@login_required(login_url='login')
def add_to_cart(request, produkt_id):
    """Fügt ein Produkt zum Warenkorb hinzu."""
    produkt = get_object_or_404(Produkt, id=produkt_id)

    if produkt.lagerbestand < 1:
        messages.error(request, f'Entschuldigung, "{produkt.name}" ist leider ausverkauft.')
        return redirect('home')

    cart = _get_or_create_cart(request.user)
    item, created = cart.items.get_or_create(
        produkt_name=produkt.name,
        defaults={
            'produkt_preis': produkt.preis,
            'produkt_bild': produkt.bild.url if produkt.bild else '',
            'menge': 1,
        },
    )
    if not created:
        if item.menge < produkt.lagerbestand:
            item.menge += 1
            item.save()
            messages.success(request, f'"{produkt.name}" wurde zum Warenkorb hinzugefügt!')
        else:
            messages.warning(request, f'Du hast bereits alle verfügbaren Einheiten ({produkt.lagerbestand}) im Warenkorb.')
    else:
        messages.success(request, f'"{produkt.name}" wurde zum Warenkorb hinzugefügt!')

    next_url = request.GET.get('next', None)
    if next_url == 'warenkorb':
        return redirect('warenkorb')
    return redirect('produkt_detail', produkt_id=produkt.id)


@login_required(login_url='login')
def remove_from_cart(request, produkt_name):
    """Entfernt ein Produkt aus dem Warenkorb."""
    cart = _get_or_create_cart(request.user)
    cart.items.filter(produkt_name=produkt_name).delete()
    messages.success(request, f'"{produkt_name}" wurde aus dem Warenkorb entfernt.')
    return redirect('warenkorb')


@login_required(login_url='login')
def update_cart(request, produkt_name):
    """Aktualisiert die Menge eines Produkts im Warenkorb."""
    try:
        menge = int(request.POST.get('menge', 1))
    except (ValueError, TypeError):
        menge = 1

    if menge < 1:
        return remove_from_cart(request, produkt_name)

    cart = _get_or_create_cart(request.user)
    item = cart.items.filter(produkt_name=produkt_name).first()
    if item:
        db_produkt = Produkt.objects.filter(name=produkt_name).first()
        if db_produkt and menge > db_produkt.lagerbestand:
            menge = db_produkt.lagerbestand
            messages.warning(request, f'Nur {menge} Einheiten verfügbar. Menge wurde angepasst.')
        item.menge = menge
        item.save()

    return redirect('warenkorb')


@login_required(login_url='login')
def warenkorb(request):
    """Warenkorb-Seite."""
    warenkorb_items = []
    gesamt = 0

    cart = _get_or_create_cart(request.user)
    for item in cart.items.all():
        item_gesamt = float(item.produkt_preis) * item.menge
        warenkorb_items.append({
            'name': item.produkt_name,
            'preis': float(item.produkt_preis),
            'bild': item.produkt_bild,
            'menge': item.menge,
            'gesamt': item_gesamt,
        })
        gesamt += item_gesamt

    return render(request, 'shop1/warenkorb.html', {
        'warenkorb_items': warenkorb_items,
        'gesamt': gesamt,
    })
