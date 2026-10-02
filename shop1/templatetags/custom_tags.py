"""Eigene Vorlagenfilter: ``mul``, ``is_admin``, ``cloud`` (Cloudinary-Transformationen),
``cloud_srcset`` (Breitenliste dazu)."""
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
def cloud_srcset(url, spec):
    """Baut ein ``srcset`` aus mehreren Cloudinary-Breiten (PF16/PF24).

    ``spec`` ist ``"breiten;beschnitt;verhaeltnis"``, die letzten beiden optional:

        {{ bild.url|cloud_srcset:'300,450,600;c_fill;1.25' }}   # Karte 4:5, beschnitten
        {{ bild.url|cloud_srcset:'600,900,1200' }}              # ganzes Bild, c_limit

    Jede Breite wird eine eigene ``cloud``-Adresse (``w_<breite>`` plus bei einem
    Verhältnis ``h_<breite*verhältnis>``) mit Beschreibung ``<breite>w``.
    Keine Cloudinary-Adresse (lokales ``/media/`` im Entwicklungsmodus, es gibt nur
    das eine Original): ein einziger Eintrag mit der größten Breite — gültig, nur
    ohne Auswahl.
    """
    url = str(url or '')
    teile = [t.strip() for t in str(spec).split(';')]
    breiten = [int(b) for b in teile[0].split(',') if b.strip().isdigit()]
    if not breiten:
        return ''
    beschnitt = teile[1] if len(teile) > 1 and teile[1] else 'c_limit'
    verhaeltnis = float(teile[2]) if len(teile) > 2 and teile[2] else None
    if '/image/upload/' not in url:
        return f'{url} {max(breiten)}w'
    eintraege = []
    for breite in breiten:
        angabe = f'w_{breite}'
        if verhaeltnis:
            angabe += f',h_{round(breite * verhaeltnis)}'
        eintraege.append(f'{cloud(url, angabe + "," + beschnitt)} {breite}w')
    return ', '.join(eintraege)
