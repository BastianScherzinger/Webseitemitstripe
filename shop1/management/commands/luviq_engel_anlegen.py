"""Legt das Engel-Shirt Nº 006 an, wenn es noch nicht da ist (P4).

Läuft bei jedem Start über ``start.sh`` und ist idempotent: Erkennung allein über den Slug
``engel-shirt-handgebleicht``. Gibt es ein Stück mit diesem Slug (auch inaktiv), passiert
nichts – Luisas Änderungen im Admin werden nie überschrieben. Die Bilder liegen als statische
Dateien im Repo (``Produkt.bild_statisch``), es braucht also weder Upload noch Cloudinary.

Wichtig: Das Stück nicht löschen, sondern im Admin auf „aktiv“ aus stellen – ein gelöschtes
Stück legt der nächste Start neu an.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from shop1 import luviq_daten
from shop1.models import Produkt, ProduktBild


class Command(BaseCommand):
    help = 'Legt das Engel-Shirt Nº 006 an, falls es fehlt (idempotent, überschreibt nichts).'

    def handle(self, *args, **optionen):
        d = luviq_daten.ENGEL_STUECK
        with transaction.atomic():
            if Produkt.objects.filter(slug=d['slug']).exists():
                self.stdout.write('Engel-Shirt ist schon vorhanden, nichts geändert.')
                return
            frei = 6 if not Produkt.objects.filter(nummer=6).exists() else None  # sonst nächste freie
            produkt = Produkt.objects.create(
                name=d['name'], slug=d['slug'], preis=Decimal(d['preis']), nummer=frei,
                beschreibung=d['beschreibung'], seo_titel=d['seo_titel'],
                seo_beschreibung=d['seo_beschreibung'], masse=d['masse'], material=d['material'],
                technik=d['technik'], zustand=d['zustand'], bild_statisch=d['bild_statisch'],
                aktiv=True, vergeben=False, lagerbestand=1,
                # Kein Newsletter-Versand durch das Anlegen: der läuft nur über das Panel.
                newsletter_gesendet=True)
            for nr, extra in enumerate(d['zusatzbilder'], start=1):
                ProduktBild.objects.create(produkt=produkt, position=nr, **extra)
        self.stdout.write(f'Engel-Shirt Nº {produkt.archiv_nummer} angelegt.')
