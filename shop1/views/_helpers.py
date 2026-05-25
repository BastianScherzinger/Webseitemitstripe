"""Interne Hilfsfunktionen und Decorators – kein direkter URL-Zugriff."""

import os
from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.conf import settings

from ..models import UserProfile, Cart, CartItem


def _setup_admin_user():
    """Synchronisiert den Admin-User aus der .env mit der Datenbank."""
    try:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@shop.de')
        admin_password = os.getenv('ADMIN_PASSWORD')

        if not admin_password:
            return

        user = User.objects.filter(username=admin_username).first()
        if user:
            changed = False
            if user.email != admin_email:
                user.email = admin_email
                changed = True
            if not user.check_password(admin_password):
                user.set_password(admin_password)
                changed = True
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                changed = True
            if changed:
                user.save()
        else:
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
            )

        if hasattr(user, 'profile'):
            if not user.profile.email_verified:
                user.profile.email_verified = True
                user.profile.save()
    except Exception:
        pass


def _is_admin(user):
    """Prüft ob Benutzer der Admin/Shopbesitzer ist."""
    if not user.is_authenticated:
        return False
    admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
    return user.username == admin_username or user.is_superuser


def admin_required(view_func):
    """Decorator – nur Admin kann zugreifen."""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not _is_admin(request.user):
            messages.error(request, 'Du hast keine Berechtigung für diese Seite.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapped


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
