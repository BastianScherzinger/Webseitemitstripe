"""Warenkorb-Views: hinzufügen, entfernen, aktualisieren, anzeigen.

Ein Posten wird über seine eigene Kennung (``CartItem.pk``) angesprochen, nicht
über den Namen (EIG46, EIG76, EIG112): zwei Stücke mit gleichem Namen bleiben
zwei Posten, und ein „/" im Namen bricht keine Adresse. Alles, was den Korb
verändert, läuft per POST mit CSRF-Prüfung (EIG85).
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Produkt
from ..postpflicht import nur_post
from ._helpers import _get_or_create_cart


@login_required(login_url='login')
@nur_post('produkte')
def add_to_cart(request, produkt_id):
    """Fügt ein Produkt zum Warenkorb hinzu (nur POST)."""
    produkt = Produkt.objects.filter(id=produkt_id).first()

    # EIG47: ein abgeschaltetes oder vergebenes Stück lässt sich nicht legen.
    if produkt is None or not produkt.aktiv or produkt.vergeben:
        messages.error(request, 'Dieses Stück ist nicht mehr verfügbar.')
        return redirect('produkte')

    if produkt.lagerbestand < 1:
        messages.error(request, f'Entschuldigung, "{produkt.name}" ist leider ausverkauft.')
        return redirect('home')

    cart = _get_or_create_cart(request.user)
    # Posten über die Kennung des Stücks finden. Posten aus der Zeit vor der
    # Kennung (``produkt_ref`` leer) werden über den Namen übernommen und
    # bekommen sie dabei.
    item = cart.items.filter(produkt_ref=produkt.id).first()
    if item is None:
        item = cart.items.filter(produkt_ref__isnull=True, produkt_name=produkt.name).first()
        if item is not None:
            item.produkt_ref = produkt.id
            item.save(update_fields=['produkt_ref'])
    if item is None:
        cart.items.create(
            produkt_name=produkt.name,
            produkt_ref=produkt.id,
            produkt_preis=produkt.preis,
            produkt_bild=produkt.bild.url if produkt.bild else '',
            menge=1,
        )
        messages.success(request, f'"{produkt.name}" wurde zum Warenkorb hinzugefügt!')
    elif item.menge < produkt.lagerbestand:
        item.menge += 1
        item.save()
        messages.success(request, f'"{produkt.name}" wurde zum Warenkorb hinzugefügt!')
    else:
        messages.warning(request, f'Du hast bereits alle verfügbaren Einheiten ({produkt.lagerbestand}) im Warenkorb.')

    next_url = request.GET.get('next', None)
    if next_url == 'warenkorb':
        return redirect('warenkorb')
    return redirect('produkt_detail', produkt_id=produkt.id)


@login_required(login_url='login')
@nur_post('warenkorb')
def remove_from_cart(request, item_id):
    """Entfernt einen Posten aus dem Warenkorb (nur POST)."""
    cart = _get_or_create_cart(request.user)
    item = cart.items.filter(id=item_id).first()
    if item is not None:
        name = item.produkt_name
        item.delete()
        messages.success(request, f'"{name}" wurde aus dem Warenkorb entfernt.')
    return redirect('warenkorb')


@login_required(login_url='login')
@nur_post('warenkorb')
def update_cart(request, item_id):
    """Aktualisiert die Menge eines Postens im Warenkorb (nur POST)."""
    try:
        menge = int(request.POST.get('menge', 1))
    except (ValueError, TypeError):
        menge = 1

    if menge < 1:
        return remove_from_cart(request, item_id)

    cart = _get_or_create_cart(request.user)
    item = cart.items.filter(id=item_id).first()
    if item:
        db_produkt = item.produkt()
        if db_produkt is None or not db_produkt.aktiv or db_produkt.vergeben:
            # EIG96: Gibt es das Stück nicht mehr, wächst die Menge nicht –
            # entfernen kann die Kundin den Posten weiterhin.
            menge = min(menge, item.menge)
            messages.warning(request, f'"{item.produkt_name}" ist nicht mehr verfügbar. '
                                      f'Bitte nimm es aus dem Warenkorb.')
        elif menge > db_produkt.lagerbestand:
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
    for item in cart.items.order_by('id'):
        item_gesamt = float(item.produkt_preis) * item.menge
        warenkorb_items.append({
            'id': item.id,
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
