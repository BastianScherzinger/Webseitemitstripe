"""Vergibt die Archivnummern der bestehenden Stücke (Umbau „Nachtausgabe", 19.09.2026).

Bisher kam „Nº 006" aus dem Primärschlüssel; dadurch trug ein Archivstück
dieselbe Nummer wie der angekündigte nächste Drop. Jetzt bekommen die aktiven
Stücke aufsteigend nach ``erstellt_am`` die Nummern 1, 2, 3 …; der nächste
Drop bekommt die nächste freie. Luisa kann die Reihenfolge im Admin ändern.
Inaktive Stücke bleiben leer und bekommen beim nächsten Speichern die nächste
freie Nummer. Rückwärts werden die Nummern wieder geleert.
"""

from django.db import migrations


def vergeben(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    stuecke = Produkt.objects.filter(aktiv=True, nummer__isnull=True).order_by('erstellt_am', 'pk')
    naechste = (Produkt.objects.exclude(nummer__isnull=True)
                .order_by('-nummer').values_list('nummer', flat=True).first() or 0) + 1
    for stueck in stuecke:
        Produkt.objects.filter(pk=stueck.pk).update(nummer=naechste)
        naechste += 1


def leeren(apps, schema_editor):
    apps.get_model('shop1', 'Produkt').objects.update(nummer=None)


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0023_nummer_material_motivanfrage'),
    ]

    operations = [
        migrations.RunPython(vergeben, leeren),
    ]
