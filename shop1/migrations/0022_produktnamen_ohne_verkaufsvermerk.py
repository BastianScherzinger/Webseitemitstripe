"""Entfernt Verkaufsvermerke aus den gespeicherten Produktangaben.

Anlass (18.09.2026): Ein Stück hiess öffentlich „Custom Pants (Sold)" mit dem
Slug ``custom-pants-sold``, vier Beschreibungen endeten auf „-ausverkauft".
Beides behauptet einen Verkauf, den es nie gab – die Stücke wurden nie
verkauft, es gibt keine Rechnungen. Die Angaben stehen in der
Produktionsdatenbank; statt sie dort von Hand zu ändern, bereinigt diese
Migration sie beim nächsten Deploy (``start.sh`` führt ``migrate`` aus).

Was sie tut, je Produkt:

* ``name`` und ``seo_titel``: ein **angehängter** Vermerk „(Sold)", „[Sold]",
  „Sold", „Sold out", „Verkauft", „Ausverkauft" (beliebige Schreibweise, auch
  mit Bindestrich oder Mittelpunkt davor) fällt weg.
* ``beschreibung`` und ``seo_beschreibung``: derselbe Vermerk am Ende fällt weg
  („Hoodie mit backprint -ausverkauft" → „Hoodie mit backprint").
* ``slug``: endet er auf ``-sold``, ``-sold-out``, ``-verkauft`` oder
  ``-ausverkauft`` (auch mit Kollisionszähler ``-1``), wird er aus dem
  bereinigten Namen neu gebildet. Die alte Adresse leitet
  ``produkt_detail_slug`` per 301 auf die neue um (``views/shop.py``,
  ``alter_verkaufsslug``) – dafür braucht es kein Register alter Slugs.

Geändert wird nur ein **Anhang**: ein Vermerk mitten im Text bleibt stehen,
weil er dort etwas anderes heissen kann. Ergäbe das Entfernen einen leeren
Namen, bleibt der Name, wie er ist. Bestellungen und Warenkörbe führen den
Namen als eigene Kopie (``produkt_name``) und bleiben unberührt.

Rückwärts: nichts – der alte Vermerk war falsch und wird nicht wiederhergestellt.
Die Migration löscht keine Zeile und kein Feld.
"""

import re

from django.db import migrations
from django.utils.text import slugify

#: Ein angehängter Verkaufsvermerk samt Trennzeichen davor.
VERMERK = re.compile(
    r'[\s\-–—·|,:]*[\(\[]?\s*\b(?:sold(?:\s*out)?|ausverkauft|verkauft)\s*[\)\]]?[\s.!]*$',
    re.IGNORECASE,
)

#: Slug-Endung eines Verkaufsvermerks, auch mit Kollisionszähler.
SLUG_VERMERK = re.compile(r'-(?:sold(?:-out)?|ausverkauft|verkauft)(?:-\d+)?$')


def ohne_vermerk(text):
    """``text`` ohne angehängten Vermerk; leer bleibt leer, und ein Text, der
    nur aus dem Vermerk besteht, bleibt unverändert."""
    if not text:
        return text
    bereinigt = VERMERK.sub('', text).rstrip()
    return bereinigt if bereinigt else text


def bereinigen(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    for produkt in Produkt.objects.all().order_by('pk'):
        felder = {}
        for feld in ('name', 'seo_titel', 'beschreibung', 'seo_beschreibung'):
            alt = getattr(produkt, feld)
            neu = ohne_vermerk(alt)
            if neu != alt:
                felder[feld] = neu
        if produkt.slug and SLUG_VERMERK.search(produkt.slug):
            name = felder.get('name', produkt.name)
            basis = slugify(name) or SLUG_VERMERK.sub('', produkt.slug) or f'produkt-{produkt.pk}'
            basis = SLUG_VERMERK.sub('', basis) or f'produkt-{produkt.pk}'
            slug, n = basis, 1
            while Produkt.objects.filter(slug=slug).exclude(pk=produkt.pk).exists():
                slug = f'{basis}-{n}'
                n += 1
            felder['slug'] = slug
        if felder:
            # update() statt save(): kein auto_now, keine Signale (IndexNow).
            Produkt.objects.filter(pk=produkt.pk).update(**felder)


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0021_tagesbesucher'),
    ]

    operations = [
        migrations.RunPython(bereinigen, migrations.RunPython.noop),
    ]
