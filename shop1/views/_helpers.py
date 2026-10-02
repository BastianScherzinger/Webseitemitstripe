"""Interne Hilfsfunktionen und Decorators – kein direkter URL-Zugriff."""

import os

from django.core.cache import cache

from ..clientip import client_ip
from ..models import Cart, CartItem

#: Anfragen je IP-Adresse und Bereich im Zeitfenster (FO09). Grosszügig für
#: Menschen – das Kontaktformular schickt nach Erfolg auf ``/kontakt/danke/``,
#: ein zweiter Versuch ist die Ausnahme –, eng für eine Schleife.
ANFRAGE_GRENZE = 5
ANFRAGE_FENSTER = 15 * 60


_client_ip = client_ip  # Name bleibt für bestehende Aufrufer; Logik in shop1/clientip.py


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


# Heute ohne Wirkung (EIG92, 02.10.2026): ``request.session['warenkorb']``
# schreibt keine View mehr – der Warenkorb liegt in ``Cart``/``CartItem``. Die
# Übernahme bleibt als Haken für einen späteren Gast-Warenkorb und ist
# getestet (``test_warenkorb``); ``login()`` ruft sie auf, sie tut dann nichts.
# offen-ok: keine View, keine URL – Hilfsfunktion, die login() erst nach der Anmeldung aufruft
def _sync_session_to_db(request, user):
    """Übernimmt einen Sitzungs-Warenkorb ins Konto (heute leer, siehe oben)."""
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


def mail_ergebnis_vermerken(modell, pk):
    """Rückruf für ``send_brevo_email(danach=…)`` (EIG10): scheitert der Versand im
    Hintergrund, steht an der gespeicherten Anfrage wieder „Mail nicht angestoßen“ —
    sichtbar im Panel statt nur im Protokoll. Gibt ``None`` zurück, wenn die Anfrage
    nicht gespeichert werden konnte (nichts zu vermerken)."""
    if pk is None:
        return None

    def danach(ok):
        if not ok:
            modell.objects.filter(pk=pk).update(mail_gestartet=False)
    return danach
