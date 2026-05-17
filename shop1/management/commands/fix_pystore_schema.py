import os
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Fuegt fehlende Spalten in pystore-DB hinzu (seite in shop1_visitorlog)'

    def handle(self, *args, **kwargs):
        if not os.getenv('PYSTORE_DATABASE_URL'):
            self.stdout.write('PYSTORE_DATABASE_URL nicht gesetzt – Schema-Fix uebersprungen.')
            return
        try:
            with connections['pystore'].cursor() as c:
                c.execute(
                    "ALTER TABLE shop1_visitorlog "
                    "ADD COLUMN IF NOT EXISTS seite varchar(100) DEFAULT '' NOT NULL"
                )
            self.stdout.write(self.style.SUCCESS('pystore: seite-Spalte in shop1_visitorlog OK'))
        except Exception as e:
            self.stderr.write(f'pystore Schema-Fix fehlgeschlagen: {e}')
