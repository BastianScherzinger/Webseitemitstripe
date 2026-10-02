"""Prüfbefehl für die Spam-Abwehr der Formulare – in beide Richtungen.

Eine Abwehr lässt sich in eine Richtung leicht verschärfen: Schwelle runter, und kein Bot
kommt mehr durch. Die Kosten stehen auf der anderen Seite und fallen nie auf, weil eine
abgewiesene echte Anfrage niemandem fehlt – sie kommt einfach nicht an. Deshalb prüft
dieser Befehl beide Richtungen mit denselben Zahlen aus ``shop1/spamschutz.py``:

* **Bot-Fälle** müssen die Schwelle erreichen (Honigtopf, Gewinnspiel mit Link, fremde
  Domain mit dem Markennamen, Linkliste in fremder Schrift).
* **Mensch-Fälle** müssen durchkommen – auch die unbequemen: ohne JavaScript (kein
  Zeitstempel), mit der eigenen Seite im Text, mit einem Instagram-Link, in
  Großbuchstaben, aus einem Tab von gestern, mit der eigenen Domain dieser Seite.
* Die **Mail-Obergrenze** lässt genau so viele Mails durch, wie eingestellt ist, und
  keine mehr.

Der Lauf schreibt nichts: kein Formular wird abgeschickt, keine Mail verschickt, nichts
gespeichert; die Zähler der Obergrenze laufen unter einem eigenen Namen.

    python manage.py pruefe_abwehr

Rückgabe: Fehler (Exitcode 1), wenn ein Mensch geblockt oder ein Bot durchgelassen würde.
"""

import time

from django.core.management.base import BaseCommand, CommandError

from shop1 import spamschutz

_MENSCH_TEXT = 'Hallo Luisa, ich hätte gern eine Jacke mit einem Drachen auf dem Rücken. Geht das bis Dezember?'


def _daten(jetzt, *, name='Anna Müller', email='anna@gmail.com', betreff='Frage zu einem Motiv',
           nachricht=_MENSCH_TEXT, alter=60, zeit=True, **zusatz):
    """POST-Daten eines Formulars, das vor ``alter`` Sekunden angezeigt wurde."""
    daten = {'name': name, 'email': email, 'betreff': betreff, 'nachricht': nachricht}
    if zeit:
        from django.core import signing
        daten[spamschutz.FELD_ZEIT] = signing.dumps(int(jetzt - alter), salt=spamschutz._SALZ)
    daten.update(zusatz)
    return daten


def faelle(jetzt=None):
    """``[(Bezeichnung, daten, soll_geblockt)]`` – die Fälle dieses Befehls."""
    jetzt = time.time() if jetzt is None else jetzt
    return [
        # ── Bots: müssen die Schwelle erreichen ──
        ('Bot: Gewinnspiel mit telegra.ph-Link (Vorfall 16.09.2026)',
         _daten(jetzt, name='RobertBoobe', betreff='THE LAMBORGHINI AVENTADOR SWEEPSTAKES CLOSES SOON',
                nachricht='You are a snap away from an Lamborghini Aventador https://telegra.ph/Win-today',
                alter=1), True),
        ('Bot: Honigtopf ausgefüllt, sonst harmlos',
         _daten(jetzt, **{spamschutz.FELD_FALLE: 'https://x.example'}), True),
        ('Bot: Honigtopf unter dem alten Namen „webseite“',
         _daten(jetzt, **{spamschutz.FELD_FALLE_ALT: 'https://x.example'}), True),
        ('Bot: fremde Domain mit dem Markennamen als Absender',
         _daten(jetzt, email='domains@search-luviq-alsfeld.xyz'), True),
        ('Bot: fremde Domain mit dem Markennamen im Text, nackt geschrieben',
         _daten(jetzt, nachricht='Ihr Eintrag läuft ab, verlängern unter luviq-alsfeld-shop.pro bitte.'), True),
        ('Bot: Linkliste in kyrillischer Schrift',
         _daten(jetzt, name='Иван', nachricht='Перевод руб. http://a.example http://b.example http://c.example',
                alter=1), True),
        # ── Menschen: müssen durchkommen ──
        ('Mensch: normale Anfrage', _daten(jetzt), False),
        ('Mensch: ohne JavaScript, also ohne Zeitstempel', _daten(jetzt, zeit=False), False),
        ('Mensch: nennt die eigene Seite ohne http (nackte Domain)',
         _daten(jetzt, nachricht='So etwas wie auf meinshop.de hätte ich gern, nur mit einem Drachen.'), False),
        ('Mensch: verweist auf ein Instagram-Bild',
         _daten(jetzt, nachricht='So eine Jacke wie hier: https://instagram.com/p/abc – geht das?'), False),
        ('Mensch: schreibt von der eigenen Domain dieser Seite',
         _daten(jetzt, email='luisa@luviq-alsfeld.com', nachricht='Test von www.luviq-alsfeld.com aus.'), False),
        ('Mensch: schreibt die Marke ohne Domain',
         _daten(jetzt, nachricht='Ich folge Luviq schon lange und möchte ein eigenes Stück.'), False),
        ('Mensch: in Großbuchstaben getippt',
         _daten(jetzt, nachricht='HALLO, ICH BRAUCHE DIE JACKE BIS ZUM ERSTEN ADVENT, GEHT DAS?'), False),
        ('Mensch: Tab von gestern (25 Stunden alt) bei einer normalen Anfrage',
         _daten(jetzt, alter=25 * 3600), False),
        ('Mensch: sehr schnell (2 Sekunden, Browser-Autofill)', _daten(jetzt, alter=2), False),
    ]


class Command(BaseCommand):
    help = 'Prüft die Spam-Abwehr der Formulare in beide Richtungen (Bots geblockt, Menschen nicht).'

    def handle(self, *args, **optionen):
        jetzt = time.time()
        fehler = []
        self.stdout.write(f'Schwelle: {spamschutz.SCHWELLE} Punkte\n')
        for bezeichnung, daten, soll_geblockt in faelle(jetzt):
            punkte, gruende = spamschutz.bewerte(daten, jetzt)
            geblockt = punkte >= spamschutz.SCHWELLE
            ok = geblockt == soll_geblockt
            marke = 'OK    ' if ok else 'FEHLER'
            self.stdout.write(f'  {marke} {punkte:>2} Punkte  {bezeichnung}'
                              + (f'  [{", ".join(gruende)}]' if gruende else ''))
            if not ok:
                fehler.append(bezeichnung + (' – ein Mensch würde abgewiesen' if geblockt
                                             else ' – ein Bot käme durch'))

        # Mail-Obergrenze: genau ``stunde`` Mails durch, die nächste nicht.
        art = f'pruefung-{int(jetzt)}'
        stunde = 3
        durch = sum(1 for _ in range(stunde + 2)
                    if spamschutz.mail_budget_ok(art, stunde=stunde, tag=100))
        ok = durch == stunde
        self.stdout.write(f'  {"OK    " if ok else "FEHLER"}    Mail-Obergrenze: {durch} von {stunde + 2} '
                          f'Versuchen durchgelassen (Soll {stunde})')
        if not ok:
            fehler.append(f'Mail-Obergrenze lässt {durch} statt {stunde} Mails durch')

        self.stdout.write(
            f'\nEingestellt: höchstens {spamschutz.MAIL_OBERGRENZE_STUNDE} Mails je Stunde und '
            f'{spamschutz.MAIL_OBERGRENZE_TAG} je Tag und Formular (je Gunicorn-Prozess).')
        self.stdout.write('Eigene Domains (nie als Nachahmer gewertet): '
                          + ', '.join(sorted(spamschutz.eigene_domains())))
        if fehler:
            raise CommandError('Spam-Abwehr fehlerhaft:\n  - ' + '\n  - '.join(fehler))
        self.stdout.write(self.style.SUCCESS('\nSpam-Abwehr in beide Richtungen in Ordnung.'))
