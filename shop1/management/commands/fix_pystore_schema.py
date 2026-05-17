import os
from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Fuegt fehlende Spalten in pystore-DB hinzu (site in shop1_visitorlog)'

    def handle(self, *args, **kwargs):
        if not os.getenv('PYSTORE_DATABASE_URL'):
            self.stdout.write('PYSTORE_DATABASE_URL nicht gesetzt – Schema-Fix uebersprungen.')
            return
        try:
            with connections['pystore'].cursor() as c:
                c.execute(
                    "ALTER TABLE shop1_visitorlog "
                    "ADD COLUMN IF NOT EXISTS site varchar(100) DEFAULT '' NOT NULL"
                )
                # Backfill: copy seite -> site for entries written by older luviq code
                try:
                    c.execute(
                        "UPDATE shop1_visitorlog SET site = seite "
                        "WHERE site = '' AND seite IS NOT NULL AND seite != ''"
                    )
                except Exception:
                    pass
            self.stdout.write(self.style.SUCCESS('pystore: site-Spalte in shop1_visitorlog OK'))
        except Exception as e:
            self.stderr.write(f'pystore Schema-Fix fehlgeschlagen: {e}')
