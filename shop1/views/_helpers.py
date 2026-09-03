"""Interne Hilfsfunktionen und Decorators – kein direkter URL-Zugriff."""

import os

from ..models import Cart, CartItem


def _is_admin(user):
    """Prüft ob Benutzer der Admin/Shopbesitzer ist."""
    if not user.is_authenticated:
        return False
    admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
    return user.username == admin_username or user.is_superuser


def _get_or_create_cart(user):
    """Holt oder erstellt den Warenkorb für einen User."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def _sync_session_to_db(request, user):
    """Synct Session-Warenkorb in die Datenbank beim Login."""
    session_cart = request.session.get('warenkorb', {})
    if not session_cart:
        return

    cart = _get_or_create_cart(user)
    for key, item in session_cart.items():
        existing = cart.items.filter(produkt_name=item['name']).first()
        if existing:
            existing.menge += item.get('menge', 1)
            existing.save()
        else:
            CartItem.objects.create(
                cart=cart,
                produkt_name=item['name'],
                produkt_preis=item['preis'],
                produkt_bild=item.get('bild', ''),
                menge=item.get('menge', 1),
            )

    request.session['warenkorb'] = {}
    request.session.modified = True
