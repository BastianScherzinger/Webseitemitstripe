"""Interne Hilfsfunktionen und Decorators – kein direkter URL-Zugriff."""

import os

from django.core.cache import cache

from ..models import Cart, CartItem

#: Anfragen je IP-Adresse und Bereich im Zeitfenster (FO09). Grosszügig für
#: Menschen – das Kontaktformular schickt nach Erfolg auf ``/kontakt/danke/``,
#: ein zweiter Versuch ist die Ausnahme –, eng für eine Schleife.
ANFRAGE_GRENZE = 5
ANFRAGE_FENSTER = 15 * 60


def _client_ip(request):
    """Die Adresse des Absenders hinter dem Railway-Proxy.

    Der letzte Eintrag in ``X-Forwarded-For`` ist der, den der einzige Proxy
    vor Gunicorn (``DOCUMENTATION.md`` §1) selbst gesehen hat. Den ersten
    kann der Absender frei setzen und so jede Drosselung umgehen."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff.strip():
        return xff.split(',')[-1].strip()
    return request.META.get('REMOTE_ADDR', '')


def zu_viele_anfragen(request, bereich, grenze=ANFRAGE_GRENZE, fenster=ANFRAGE_FENSTER):
    """Zählt eine Anfrage je IP-Adresse und meldet ``True`` über der Grenze.

    Der Zähler liegt im ``LocMemCache`` und damit je Gunicorn-Prozess; bei
    zwei Workern (``start.sh``) kommt eine Adresse im ungünstigsten Fall auf
    die doppelte Zahl. Das genügt gegen eine Schleife und braucht keinen
    zusätzlichen Dienst."""
    schluessel = f'drossel:{bereich}:{_client_ip(request)}'
    # add() legt den Zähler nur an, wenn es ihn noch nicht gibt – das
    # Zeitfenster beginnt mit der ersten Anfrage und verlängert sich nicht.
    if cache.add(schluessel, 1, fenster):
        return False
    try:
        anzahl = cache.incr(schluessel)
    except ValueError:
        # Zwischen add() und incr() abgelaufen oder verdrängt.
        cache.add(schluessel, 1, fenster)
        return False
    return anzahl > grenze


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


# offen-ok: keine View, keine URL – Hilfsfunktion, die login() erst nach
# erfolgreicher Anmeldung mit dem bereits angemeldeten Benutzer aufruft.
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
