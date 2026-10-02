"""Trägt nach, was die Felder aus 0025 für Bestandsdaten brauchen (EIG115, EIG08).

* Die Stücke Nº 001–005 sind vergeben (Archiv): ``Produkt.vergeben`` = ``True``.
  Damit macht ein späteres ``VERKAUF_AKTIV=1`` sie nicht wieder kaufbar. Stücke
  ab Nº 006 bleiben unberührt.
* Warenkorb- und Bestellposten bekommen ``produkt_ref``, **wenn** ihr Name genau
  einem Produkt gehört. Bei doppelten oder nicht mehr vorhandenen Namen bleibt
  das Feld leer – raten wäre hier gefährlicher als leer lassen.

Rückwärts: keine Wirkung (die Felder verschwinden mit 0025).
"""

from django.db import migrations


def nachtragen(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    CartItem = apps.get_model('shop1', 'CartItem')
    OrderItem = apps.get_model('shop1', 'OrderItem')

    Produkt.objects.filter(nummer__gte=1, nummer__lte=5).update(vergeben=True)

    eindeutig = {}
    gesehen = set()
    for pk, name in Produkt.objects.values_list('pk', 'name'):
        if name in gesehen:
            eindeutig.pop(name, None)
        else:
            eindeutig[name] = pk
            gesehen.add(name)
    for modell in (CartItem, OrderItem):
        for name, pk in eindeutig.items():
            modell.objects.filter(produkt_name=name, produkt_ref__isnull=True).update(produkt_ref=pk)


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0025_bestellungen_erhalten_stueckkennung_archiv'),
    ]

    operations = [
        migrations.RunPython(nachtragen, migrations.RunPython.noop),
    ]
