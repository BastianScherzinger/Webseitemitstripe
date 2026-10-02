"""Löscht alte Besuchereinträge der eigenen Seite nach einer Frist (EIG51).

Das Besuchsprotokoll (``VisitorLog``) hatte weder Frist noch Löschroutine; die
Datenschutzerklärung nennt keine Speicherdauer. Seit der cookielosen Zählung
steht keine IP-Adresse mehr darin (nur Pfad, Zeitpunkt, Geräteklasse), aber auch
das sollte nicht ewig bleiben.

**Die Frist legt die Betreiberin fest** (Luisa Brehler, mit Bastian) – der Befehl
rät sie nicht. Ohne Angabe löscht er nichts und nennt nur den Vorschlag
(90 Tage). Die Frist kommt aus ``--tage`` oder aus der Umgebungsvariablen
``BESUCHER_AUFBEWAHRUNG_TAGE``; ``--trocken`` zeigt nur, wie viele Einträge
betroffen wären. Einträge anderer Seiten in der gemeinsamen pystore-Datenbank
bleiben unberührt. Die Tageszähler (``PageVisit``) enthalten keine
personenbezogenen Daten und bleiben.
"""
import logging
import os
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from shop1.models import VisitorLog

_log = logging.getLogger('shop1')

VORSCHLAG_TAGE = 90


class Command(BaseCommand):
    """``python manage.py besucher_aufraeumen --tage 90``; ohne Frist passiert nichts."""
    help = 'Löscht VisitorLog-Einträge der eigenen Seite, die älter als die Frist sind'

    def add_arguments(self, parser):
        parser.add_argument('--tage', type=int, default=None,
                            help='Frist in Tagen (sonst BESUCHER_AUFBEWAHRUNG_TAGE; ohne beides wird nichts gelöscht)')
        parser.add_argument('--trocken', action='store_true',
                            help='nur zählen, nichts löschen')

    def handle(self, *args, **optionen):
        tage = optionen['tage']
        if tage is None:
            roh = os.getenv('BESUCHER_AUFBEWAHRUNG_TAGE', '').strip()
            if roh:
                if not roh.isdigit():
                    raise CommandError(f'BESUCHER_AUFBEWAHRUNG_TAGE ist keine Zahl: {roh!r}')
                tage = int(roh)
        if tage is None:
            self.stdout.write(
                f'Keine Frist festgelegt – es wird nichts gelöscht. Vorschlag: {VORSCHLAG_TAGE} Tage '
                f'(--tage {VORSCHLAG_TAGE} oder BESUCHER_AUFBEWAHRUNG_TAGE={VORSCHLAG_TAGE}). '
                f'Entscheiden müssen Luisa Brehler und Bastian.')
            return
        if tage < 1:
            raise CommandError('Die Frist muss mindestens 1 Tag betragen.')

        seite = os.getenv('SITE_NAME') or 'luviq'
        grenze = timezone.now() - timedelta(days=tage)
        alte = VisitorLog.objects.filter(seite=seite, timestamp__lt=grenze)
        if optionen['trocken']:
            self.stdout.write(f'{alte.count()} Besuchereinträge von {seite} wären älter als {tage} Tage (trocken, nichts gelöscht).')
            return
        anzahl, _ = alte.delete()
        _log.info('besucher_aufraeumen: %s Einträge von %s älter als %s Tage gelöscht', anzahl, seite, tage)
        self.stdout.write(f'{anzahl} Besuchereinträge von {seite} älter als {tage} Tage gelöscht.')
