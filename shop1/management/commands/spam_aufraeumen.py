"""Löscht gespeicherten Spamverdacht und alte Dienstleistungs-Angebote aus den Kontaktnachrichten.

Seit 24.11.2026 wird nichts mehr still verworfen: jede Einsendung steht in ``KontaktAnfrage``, auch Bot-Spam
(``einstufung='spam'``) und Verkaufsschreiben (``einstufung='angebot'``). Das gibt Luisa die Möglichkeit,
einen Fehlgriff im Django-Admin zu finden, soll aber keine Adressen ewig sammeln.

**Wie bei ``besucher_aufraeumen`` legt die Betreiberin die Fristen fest.** Ohne Angabe löscht der Befehl nichts
und nennt nur den Vorschlag (30 Tage Spam, 90 Tage Angebote – letztere müssen mindestens so lange stehen wie
die Pause je Adresse, ``ABSAGE_PAUSE_TAGE``, Vorgabe 30). Fristen: ``--spam-tage`` / ``--angebot-tage`` oder
die Umgebungsvariablen ``SPAM_AUFBEWAHRUNG_TAGE`` / ``ANGEBOT_AUFBEWAHRUNG_TAGE``. ``--trocken`` zählt nur.
Echte Anfragen (``einstufung='anfrage'``) fasst der Befehl nie an.
"""
import os
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from shop1.models import KontaktAnfrage

VORSCHLAG = {'spam': 30, 'angebot': 90}


def _frist(optionen, name, umgebung):
    wert = optionen[name]
    if wert is None:
        roh = os.getenv(umgebung, '').strip()
        if roh:
            if not roh.isdigit():
                raise CommandError(f'{umgebung} ist keine Zahl: {roh!r}')
            wert = int(roh)
    return wert


class Command(BaseCommand):
    """``python manage.py spam_aufraeumen --spam-tage 30 --angebot-tage 90``; ohne Fristen passiert nichts."""
    help = 'Löscht Spamverdacht und Dienstleistungs-Angebote der Kontaktnachrichten nach einer Frist'

    def add_arguments(self, parser):
        parser.add_argument('--spam-tage', type=int, default=None)
        parser.add_argument('--angebot-tage', type=int, default=None)
        parser.add_argument('--trocken', action='store_true', help='nur zählen, nichts löschen')

    def handle(self, *args, **optionen):
        fristen = {
            'spam': _frist(optionen, 'spam_tage', 'SPAM_AUFBEWAHRUNG_TAGE'),
            'angebot': _frist(optionen, 'angebot_tage', 'ANGEBOT_AUFBEWAHRUNG_TAGE'),
        }
        if all(v is None for v in fristen.values()):
            self.stdout.write('Keine Frist festgelegt – es wird nichts gelöscht. Vorschlag: '
                              f'{VORSCHLAG["spam"]} Tage Spam, {VORSCHLAG["angebot"]} Tage Angebote.')
            return
        for art, tage in fristen.items():
            if tage is None:
                continue
            alt = KontaktAnfrage.objects.filter(einstufung=art, erstellt_am__lt=timezone.now() - timedelta(days=tage))
            n = alt.count()
            if optionen['trocken']:
                self.stdout.write(f'{art}: {n} Einträge älter als {tage} Tage (trocken, nichts gelöscht).')
            else:
                alt.delete()
                self.stdout.write(f'{art}: {n} Einträge älter als {tage} Tage gelöscht.')
