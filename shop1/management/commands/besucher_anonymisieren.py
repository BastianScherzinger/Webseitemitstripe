"""Entfernt IP-Adressen und Städte aus alten Besuchereinträgen (``start.sh``).

Seit der cookielosen Zählung (``PageVisitMiddleware``) speichert die Seite
keine IP-Adresse mehr. Einträge von davor tragen sie noch; dieser Befehl
leert sie für die eigene Seite (``SITE_NAME``). Einträge anderer Seiten in
der gemeinsamen pystore-Datenbank bleiben unberührt. Mehrfach ausführbar.
"""
import logging
import os

from django.core.management.base import BaseCommand

from shop1.models import VisitorLog

_log = logging.getLogger('shop1')


class Command(BaseCommand):
    """``python manage.py besucher_anonymisieren``; bricht den Start bei einem Fehler nicht ab."""
    help = 'Leert IP-Adresse und Stadt in alten VisitorLog-Einträgen der eigenen Seite'

    def handle(self, *args, **kwargs):
        seite = os.getenv('SITE_NAME') or 'luviq'
        try:
            anzahl = (VisitorLog.objects.filter(seite=seite)
                      .exclude(ip_address__isnull=True, city='')
                      .update(ip_address=None, city=''))
        except Exception as e:
            _log.error('besucher_anonymisieren: %s', e)
            self.stdout.write(f'Anonymisieren fehlgeschlagen: {e}')
            return
        self.stdout.write(f'{anzahl} Besuchereinträge ohne IP-Adresse und Stadt ({seite}).')
