"""Rabattcodes anlegen und auflisten (01.11.2026). Codes stehen nur in der Datenbank, nie im Repository.

    python manage.py rabattcode liste
    python manage.py rabattcode anlegen TRAVEWIND-7KQ4 --prozent 20 --max 30 --bis 2027-06-30 --zweck "Freunde/Karten"
    python manage.py rabattcode anlegen --zufall KARTE --prozent 10 --zweck Karten     # erzeugt KARTE-XXXX
    python manage.py rabattcode anlegen HAFENWIND-10 --prozent 10 --oeffentlich --zweck Website
    python manage.py rabattcode aus TRAVEWIND-7KQ4

Ohne ``--alle`` gilt ein Code nur für die erste Bestellung.
"""

import secrets
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from shop1.models import Rabattcode
from shop1.rabatt import normalisiere_code

# Ohne 0/O und 1/I/L: Codes werden von Hand auf Karten geschrieben und abgetippt.
_ZEICHEN = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'


class Command(BaseCommand):
    help = 'Rabattcodes anlegen, auflisten, abschalten'

    def add_arguments(self, parser):
        parser.add_argument('aktion', choices=('liste', 'anlegen', 'aus', 'an'))
        parser.add_argument('code', nargs='?', default='')
        parser.add_argument('--zufall', default='', help='Präfix; hängt 4 zufällige Zeichen an')
        parser.add_argument('--prozent', type=int)
        parser.add_argument('--max', type=int, default=None)
        parser.add_argument('--bis', default='', help='JJJJ-MM-TT, einschließlich')
        parser.add_argument('--zweck', default='')
        parser.add_argument('--oeffentlich', action='store_true')
        parser.add_argument('--alle', action='store_true', help='nicht nur erste Bestellung')

    def handle(self, *args, **o):
        if o['aktion'] == 'liste':
            for c in Rabattcode.objects.order_by('erstellt_am'):
                self.stdout.write(
                    f"{c.code:<22} {c.prozent:>3} %  {'erst' if c.nur_erstbestellung else 'alle'}  "
                    f"{'öffentlich' if c.oeffentlich else 'intern    '}  {'aktiv' if c.aktiv else 'AUS  '}  "
                    f"bis {c.gueltig_bis or '-':<10}  eingelöst {c.einloesungen()}/{c.max_einloesungen or '∞'}  {c.zweck}")
            return
        if o['aktion'] in ('aus', 'an'):
            n = Rabattcode.objects.filter(code=normalisiere_code(o['code'])).update(aktiv=o['aktion'] == 'an')
            if not n:
                raise CommandError('Code nicht gefunden')
            self.stdout.write(f"{normalisiere_code(o['code'])}: {o['aktion']}")
            return
        code = normalisiere_code(o['code'])
        if o['zufall']:
            code = normalisiere_code(o['zufall']) + '-' + ''.join(secrets.choice(_ZEICHEN) for _ in range(4))
        if not code or not o['prozent'] or not 1 <= o['prozent'] <= 50:
            raise CommandError('Code und --prozent (1–50) angeben')
        if Rabattcode.objects.filter(code=code).exists():
            raise CommandError(f'{code} gibt es schon')
        c = Rabattcode.objects.create(
            code=code, prozent=o['prozent'], max_einloesungen=o['max'], zweck=o['zweck'],
            gueltig_bis=date.fromisoformat(o['bis']) if o['bis'] else None,
            oeffentlich=o['oeffentlich'], nur_erstbestellung=not o['alle'])
        self.stdout.write(self.style.SUCCESS(f'angelegt: {c.code} ({c.prozent} %)'))
