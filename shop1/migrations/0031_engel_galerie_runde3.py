"""Runde 3 (30.10.2026): Engel-Shirt bekommt die Vorderseiten-Fotos in der Galerie.

Das Stück legt ``luviq_engel_anlegen`` nur einmal an und überschreibt danach nichts. Damit die
Live-Datenbank die neuen echten Fotos trotzdem bekommt, trägt diese Migration sie **einmal**
nach – nur für das Stück mit dem Slug ``engel-shirt-handgebleicht`` und nur Bilder, deren
``bild_statisch`` noch nicht da ist (löscht Luisa später eins im Admin, kommt es nicht wieder,
weil eine Migration nur einmal läuft). Die Beschreibung wird nur ersetzt, wenn sie noch wörtlich
den alten Text mit „Foto folgt“ trägt. Werte bewusst hier fest (eine Migration darf sich nicht
ändern, wenn ``luviq_daten`` sich ändert). Auf einer frischen Datenbank gibt es das Stück vor
dem Befehl noch nicht: dann tut sie nichts, der Befehl legt alles aus ``ENGEL_STUECK`` an.
"""
from django.db import migrations
from django.utils import timezone

SLUG = 'engel-shirt-handgebleicht'
ALT_TEXT = ('Ein T-Shirt aus 100 % Baumwolle in Größe M. Auf dem Rücken steht ein Engel mit '
            'Rose und einem Stern, von Hand gemalt – viel Handarbeit, genau einmal. '
            'Vorne ein kleines Luviq-Zeichen auf Herzhöhe – Foto folgt.')
NEU_TEXT = ALT_TEXT.replace(' – Foto folgt.', '.')
RUECKEN = 'shop1/images/stuecke/engel-echt-45-{w}.webp@600,900,960#960x1200'
NEUE_BILDER = [
    {'position': 3, 'ist_ki': False, 'unterschrift': 'Echtes Foto: vorne, Luviq-Zeichen',
     'bild_statisch': 'shop1/images/stuecke/engel-vorne-echt-45-{w}.webp@600,900,960#960x1200',
     'breite': 960, 'hoehe': 1200,
     'alt': ('Echtes Foto der Vorderseite des Engel-Shirts, nah: das Luviq-Zeichen in Bleich-Beige '
             'auf schwarzem Stoff, ein Schriftzug mit Stern und zwei Pfeilen')},
    {'position': 4, 'ist_ki': False, 'unterschrift': 'Echtes Foto: auf Luisas Arbeitstisch',
     'bild_statisch': 'shop1/images/stuecke/engel-arbeitsplatz-45-{w}.webp@600,900,960#960x1200',
     'breite': 960, 'hoehe': 1200,
     'alt': ('Echtes Foto: das Engel-Shirt mit der Vorderseite nach oben auf Luisas Arbeitstisch, '
             'daneben Pinsel, Stifte, Gummihandschuhe und ein Glas mit Bleiche')},
]


def vorwaerts(apps, schema_editor):
    Produkt = apps.get_model('shop1', 'Produkt')
    ProduktBild = apps.get_model('shop1', 'ProduktBild')
    produkt = Produkt.objects.filter(slug=SLUG).first()
    if not produkt:
        return
    geaendert = False
    vorhanden = set(ProduktBild.objects.filter(produkt=produkt).values_list('bild_statisch', flat=True))
    for daten in NEUE_BILDER:
        if daten['bild_statisch'] not in vorhanden:
            ProduktBild.objects.create(produkt=produkt, **daten)
            geaendert = True
    if ProduktBild.objects.filter(produkt=produkt, bild_statisch=RUECKEN, unterschrift='').update(
            unterschrift='Echtes Foto: Rücken'):
        geaendert = True
    if produkt.beschreibung == ALT_TEXT:
        produkt.beschreibung = NEU_TEXT
        geaendert = True
    if geaendert:
        # lastmod der Sitemap und dateModified folgen aktualisiert_am (auto_now greift bei
        # .update() nicht, deshalb ausdrücklich).
        Produkt.objects.filter(pk=produkt.pk).update(beschreibung=produkt.beschreibung,
                                                     aktualisiert_am=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0030_zusatzbild_ki_und_unterschrift'),
    ]

    operations = [
        migrations.RunPython(vorwaerts, migrations.RunPython.noop),
    ]
