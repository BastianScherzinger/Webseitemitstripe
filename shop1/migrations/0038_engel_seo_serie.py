"""Engel-Shirt: Meta-Beschreibung ohne „Unikat“ (Rechtscheck 07.11.2026, W1, § 5 UWG).

Das Engel-Shirt ist eine Serie: derselbe Engel wird für jede Bestellung neu von Hand gemalt.
Ersetzt wird ``seo_beschreibung`` nur, wenn sie noch eine der beiden bekannten Fassungen mit
„Unikat“ trägt; Luisas eigener Text bleibt unangetastet.
"""
from django.db import migrations

SLUG = 'engel-shirt-handgebleicht'
ALT = (
    'Unikat Nº 006: T-Shirt mit Engel, Rose und Stern, von Hand mit Bleiche gemalt. '
    '100 % Baumwolle, Größe M. Luviq, Lübeck.',
    'Engel-Shirt Nº 006: Second-Hand-T-Shirt mit Engel, Rose und Stern, von Hand mit Bleiche gemalt. '
    '100 % Baumwolle, Größe M. Unikat von Luviq aus Lübeck.',
)
NEU = ('Engel-Shirt Nº 006: Second-Hand-T-Shirt mit Engel, Rose und Stern, von Hand mit Bleiche gemalt. '
       '100 % Baumwolle, Größe M. Jedes Shirt neu gemalt.')


def umstellen(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    for p in Produkt.objects.filter(slug=SLUG):
        if (p.seo_beschreibung or '').strip() in ALT:
            Produkt.objects.filter(pk=p.pk).update(seo_beschreibung=NEU)


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0037_archivstuecke_deutsch'),
    ]

    operations = [
        migrations.RunPython(umstellen, migrations.RunPython.noop),
    ]
