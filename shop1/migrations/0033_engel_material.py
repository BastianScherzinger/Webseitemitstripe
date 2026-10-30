"""Gegenprüfung M3 (30.10.2026): Faserzusammensetzung beim Engel-Shirt Nº 006.

Neue Textilien brauchen die Faserangabe vor dem Kauf (VO (EU) Nr. 1007/2011 Art. 16);
seit diesem Stand ist ein neues Stück ohne ``material`` nicht kaufbar
(``Produkt.pflichtangaben_fehlen``). Das Engel-Shirt ist öffentlich als „100 % Baumwolle“
beschrieben (``luviq_daten.ENGEL_STUECK``). Die Migration trägt den Wert nur nach, wenn das
Feld leer ist – ein Wert, den Luisa im Admin gesetzt hat, bleibt.
"""
from django.db import migrations

SLUG = 'engel-shirt-handgebleicht'
MATERIAL = '100 % Baumwolle'


def nachtragen(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    for produkt in Produkt.objects.filter(slug=SLUG):
        if not (produkt.material or '').strip():
            Produkt.objects.filter(pk=produkt.pk).update(material=MATERIAL)


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0032_widerruf'),
    ]

    operations = [
        migrations.RunPython(nachtragen, migrations.RunPython.noop),
    ]
