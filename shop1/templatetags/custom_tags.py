"""Eigene Vorlagenfilter: ``mul``, ``is_admin`` und ``cloud`` (Cloudinary-Transformationen)."""
import re
from urllib.parse import urlsplit, urlunsplit

from django import template

register = template.Library()

#: Endungen, die ``cloud`` durch ``.webp`` ersetzt; bereits moderne bleiben.
_ALTFORMAT = re.compile(r'\.(jpe?g|png|gif|bmp|tiff?|heic|heif)$', re.IGNORECASE)
_MODERN = re.compile(r'\.(webp|avif)$', re.IGNORECASE)


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

    Endung ``.webp`` (PF15): mit ``f_auto`` ist sie nur der Rückfall für
    Browser ohne AVIF/WebP-Aushandlung – WebP statt JPEG/PNG, ohne <picture>.
    """
    url = str(url or '')
    marker = '/image/upload/'
    if marker not in url:
        return url
    transform = 'f_auto,q_auto'
    if spec:
        transform += ',' + spec
    teile = urlsplit(url.replace(marker, marker + transform + '/', 1))
    if not _MODERN.search(teile.path):
        pfad = _ALTFORMAT.sub('', teile.path) + '.webp'
        teile = teile._replace(path=pfad)
    return urlunsplit(teile)


@register.filter
def cloud_vorschau(url):
    """Vorschaubild für geteilte Links (``og:image``): 1200 × 630, JPEG.

    Cloudinary füllt das Querformat mit ``c_pad,b_auto`` auf, statt ein
    hochkantes Foto zu beschneiden (IS39: ein Hochformat wie 1107 × 2400 ist als
    Vorschau zu schmal). JPEG statt WebP, weil die Vorschau-Abrufer von
    WhatsApp, LinkedIn und Facebook dieses Format am sichersten lesen.
    Nicht-Cloudinary-URLs (lokales ``/media/``) bleiben unverändert.
    """
    url = str(url or '')
    marker = '/image/upload/'
    if marker not in url:
        return url
    teile = urlsplit(url.replace(marker, marker + 'f_jpg,q_auto,w_1200,h_630,c_pad,b_auto/', 1))
    pfad = re.sub(r'\.[A-Za-z0-9]{2,5}$', '', teile.path) + '.jpg'
    return urlunsplit(teile._replace(path=pfad))
