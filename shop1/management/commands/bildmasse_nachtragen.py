"""Trägt die Bildmaße (``bild_breite``/``bild_hoehe``) für Produkte nach, die sie noch nicht haben.

    python manage.py bildmasse_nachtragen

Läuft bei jedem Start (``start.sh``, nicht blockierend) und tut nichts, wenn
alle Maße da sind. Ein Produkt ohne lesbares Bild bleibt ohne Maße; die Stückseite
lässt ``width``/``height`` dann weg (PF25). Wirft nie: ein Fehler steht in der Ausgabe.
"""

import logging

from django.core.files.images import get_image_dimensions
from django.core.management.base import BaseCommand
from django.db.models import Q

from shop1.models import Produkt

_log = logging.getLogger(__name__)


class Command(BaseCommand):
    """Liest die Maße der Produktbilder und speichert sie (``bild_breite``/``bild_hoehe``)."""

    help = 'Trägt fehlende Bildmaße der Produkte nach.'

    def handle(self, *args, **options):
        offen = Produkt.objects.exclude(bild='').exclude(bild__isnull=True).filter(
            Q(bild_breite__isnull=True) | Q(bild_hoehe__isnull=True))
        nachgetragen = 0
        for produkt in offen:
            try:
                with produkt.bild.open('rb') as datei:
                    breite, hoehe = get_image_dimensions(datei)
            except Exception as fehler:  # ein Bild darf den Start nicht stoppen
                _log.warning('Bildmaße von Produkt %s nicht lesbar: %s', produkt.pk, fehler)
                self.stderr.write(f'{produkt.pk} {produkt.name}: Maße nicht lesbar ({fehler})')
                continue
            if not (breite and hoehe):
                self.stderr.write(f'{produkt.pk} {produkt.name}: kein lesbares Bild')
                continue
            Produkt.objects.filter(pk=produkt.pk).update(bild_breite=breite, bild_hoehe=hoehe)
            nachgetragen += 1
            self.stdout.write(f'{produkt.pk} {produkt.name}: {breite} x {hoehe}')
        self.stdout.write(f'Bildmaße nachgetragen: {nachgetragen}')
