from django import template
import os

register = template.Library()


@register.filter
def mul(value, arg):
    """Multipliziert zwei Werte"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def is_admin(user):
    """Filter - prüft ob Benutzer Admin oder Superuser ist"""
    if not user.is_authenticated:
        return False
    # Sowohl Admins (is_staff) als auch Superuser (is_superuser) dürfen den Shop verwalten
    return user.is_staff or user.is_superuser


@register.filter
def cloud(url, spec=''):
    """Fügt Cloudinary-Transformationen in eine /image/upload/-URL ein.

    Reduziert Payload/LCP drastisch: liefert automatisch modernes Format
    (f_auto) und passende Qualität (q_auto) und skaliert das Bild auf die
    tatsächlich benötigte Größe herunter, statt das Original auszuliefern.

    Verwendung:  {{ produkt.bild.url|cloud:'w_600,c_limit' }}
                 {{ produkt.bild.url|cloud:'w_160,h_120,c_fill' }}

    Nicht-Cloudinary-URLs (z.B. lokales /media/ im Dev-Modus) werden
    unverändert zurückgegeben.
    """
    url = str(url or '')
    marker = '/image/upload/'
    if marker not in url:
        return url
    transform = 'f_auto,q_auto'
    if spec:
        transform += ',' + spec
    return url.replace(marker, marker + transform + '/', 1)
