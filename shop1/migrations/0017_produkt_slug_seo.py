from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    used = set()
    for p in Produkt.objects.all().order_by('id'):
        base = slugify(p.name) or f"produkt-{p.id}"
        slug = base
        n = 1
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        p.slug = slug
        p.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0016_visitorlog_site_column'),
    ]

    operations = [
        migrations.AddField(
            model_name='produkt',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='produkt',
            name='seo_titel',
            field=models.CharField(blank=True, max_length=60, help_text='SEO-Titel (max. 60 Zeichen). Leer = automatisch.'),
        ),
        migrations.AddField(
            model_name='produkt',
            name='seo_beschreibung',
            field=models.CharField(blank=True, max_length=160, help_text='Meta-Description (max. 160 Zeichen). Leer = aus Beschreibung.'),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
    ]
