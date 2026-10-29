"""Bilder eines Stücks (P4): Upload (Cloudinary) oder statische Datei aus dem Repo.

Statische Bilder werden als Text beschrieben, damit ein Stück ohne Upload und ohne Admin
angelegt werden kann (``luviq_engel_anlegen``)::

    shop1/images/luviq/hero-engel-45-{w}.webp@480,640,800#800x1000

``{w}`` steht für die Breite, nach ``@`` folgen die vorhandenen Breiten, nach ``#`` die Maße
der größten Datei. Daraus entstehen ``src`` (mittlere Breite), ``srcset`` und ``width/height``.
Hochgeladene Bilder laufen weiter über die Cloudinary-Filter aus ``custom_tags``.
"""
from dataclasses import dataclass

from django.templatetags.static import static


@dataclass(frozen=True)
class Bild:
    src: str        # Rückfalladresse (mittlere Breite)
    srcset: str
    breite: int
    hoehe: int
    alt: str
    original: str   # größte Fassung, für og:image und Sitemap
    karte_src: str = ''
    karte_srcset: str = ''


def statisches_bild(spec):
    """``(muster, breiten, (breite, hoehe))`` aus der Textform, sonst ``None``."""
    spec = (spec or '').strip()
    if '@' not in spec or '#' not in spec or '{w}' not in spec:
        return None
    muster, rest = spec.split('@', 1)
    breiten_text, masse = rest.split('#', 1)
    try:
        breiten = [int(b) for b in breiten_text.split(',') if b.strip()]
        breite, hoehe = (int(x) for x in masse.lower().split('x'))
    except ValueError:
        return None
    if not breiten:
        return None
    return muster, breiten, (breite, hoehe)


def bild_aus(upload, statisch, breite, hoehe, alt):
    """Ein ``Bild`` aus Upload oder statischer Beschreibung; ``None``, wenn keins da ist."""
    from .templatetags.custom_tags import cloud, cloud_srcset
    if upload:
        url = upload.url
        if breite and hoehe:
            faktor = min(1, 1200 / breite)
            b, h = round(breite * faktor), round(hoehe * faktor)
        else:
            b, h = 900, 1125
        return Bild(src=cloud(url, 'w_900,c_limit'), srcset=cloud_srcset(url, '600,900,1200'),
                    breite=b, hoehe=h, alt=alt, original=url,
                    karte_src=cloud(url, 'w_600,h_750,c_fill'),
                    karte_srcset=cloud_srcset(url, '300,450,600;c_fill;1.25'))
    teile = statisches_bild(statisch)
    if not teile:
        return None
    muster, breiten, (b, h) = teile
    adressen = {w: static(muster.replace('{w}', str(w))) for w in breiten}
    mitte = sorted(breiten)[len(breiten) // 2]
    srcset = ', '.join(f'{adressen[w]} {w}w' for w in sorted(breiten))
    return Bild(src=adressen[mitte], srcset=srcset, breite=b, hoehe=h, alt=alt,
                original=adressen[max(breiten)], karte_src=adressen[mitte], karte_srcset=srcset)
