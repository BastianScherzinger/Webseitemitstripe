"""Archivstücke Nº 001–005 bekommen deutsche Namen und Beschreibungen (Bastian, 04.11.2026).

Die Stücke hießen „Custom print hoodie“, „Custom Pants“ usw. Die Adressen (Slugs) bleiben unverändert,
damit keine Links brechen. Geändert wird nur, wo noch der alte Text steht: Was Luisa im Admin
schon selbst geändert hat, bleibt.
"""

from django.db import migrations

# Slug -> (alter Name, neuer Name, alte Beschreibung, neue Beschreibung)
STUECKE = {
    'custom-print-hoodie': (
        'Custom print hoodie', 'Pullover mit Kreismotiv',
        'Custom hoodie mit print',
        'Dunkler Pullover mit großem Kreismotiv auf der Vorderseite, von Hand mit Bleiche gemalt. '
        'Ein Einzelstück aus dem Archiv, bereits vergeben.'),
    'custom-print-jacke': (
        'Custom print jacke', 'Jacke mit Rankenmotiv',
        'Jacke mit backprint',
        'Dunkle Jacke mit einer Ranke über den Rücken, von Hand mit Bleiche gemalt. '
        'Ein Einzelstück aus dem Archiv, bereits vergeben.'),
    'custom-print-hoodie-1': (
        'Custom print hoodie', 'Hoodie mit Sternmotiv',
        'Hoodie mit backprint',
        'Schwarzer Hoodie mit Stern und symmetrischem Motiv auf dem Rücken, von Hand mit Bleiche gemalt. '
        'Ein Einzelstück aus dem Archiv, bereits vergeben.'),
    'custom-hoodie-mit-print': (
        'Custom hoodie mit print', 'Hoodie mit Rückenmotiv',
        'Hoodie mit backprint',
        'Schwarzer Hoodie mit schmalem Motiv auf dem Rücken, von Hand mit Bleiche gemalt. '
        'Ein Einzelstück aus dem Archiv, bereits vergeben.'),
    'custom-pants': (
        'Custom Pants', 'Hose mit Spinnenmotiv',
        'Pants with custom print',
        'Dunkle Hose mit Spinnen und Netzen auf beiden Beinen, von Hand mit Bleiche gemalt. '
        'Ein Einzelstück aus dem Archiv, bereits vergeben.'),
}


def vorwaerts(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    for slug, (alt_name, neu_name, alt_text, neu_text) in STUECKE.items():
        Produkt.objects.filter(slug=slug, name__iexact=alt_name).update(name=neu_name)
        Produkt.objects.filter(slug=slug, beschreibung__iexact=alt_text).update(beschreibung=neu_text)


def rueckwaerts(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    for slug, (alt_name, neu_name, alt_text, neu_text) in STUECKE.items():
        Produkt.objects.filter(slug=slug, name=neu_name).update(name=alt_name)
        Produkt.objects.filter(slug=slug, beschreibung=neu_text).update(beschreibung=alt_text)


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0036_zahlungslink'),
    ]

    operations = [
        migrations.RunPython(vorwaerts, rueckwaerts),
    ]
