"""Rabattcodes (Auftrag Bastian 01.11.2026).

Ein Code zieht einen Prozentsatz vom Warenwert ab. Codes für die erste Bestellung gelten nur, wenn es unter
der E-Mail-Adresse **und** der Lieferanschrift noch keine Bestellung gibt (stornierte und fehlgeschlagene
zählen nicht). Die E-Mail wird dafür vereinheitlicht: Kleinbuchstaben, ohne „+Zusatz“, bei Gmail ohne Punkte –
sonst bekäme ``anna+2@gmail.com`` den Rabatt ein zweites Mal.

Wege zum Code:

* Eingabe im Bestellformular (Feld „Rabattcode“, Knopf „Einlösen“ zeigt den neuen Gesamtpreis vor dem Absenden).
* Link ``/rabatt/<CODE>/`` (Hero-Knopf, QR-Code auf Karten): merkt den Code in der Sitzung und trägt ihn im
  Formular ein. Das Sitzungs-Cookie entsteht erst durch diesen Klick (technisch notwendig, § 25 Abs. 2 Nr. 2 TDDDG).

Der Betrag steht danach fest in der Bestellung (``Order.gesamt_betrag`` = Warenwert − ``rabatt_betrag``). Jeder
Zahlungsweg – heute Rechnung, später Mollie – nimmt genau diesen Betrag; ein eigener Rabatt beim Zahlungsanbieter
ist nicht nötig und wäre doppelt.
"""

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Q
from django.utils import timezone

#: Status, die beim Zählen (erste Bestellung, Einlösungen) nicht mitzählen.
ZAEHLT_NICHT = ('cancelled', 'failed')
#: Sitzungsschlüssel des über einen Link gemerkten Codes.
SITZUNG = 'rabattcode'

_GMAIL = {'gmail.com', 'googlemail.com'}


def normalisiere_code(text):
    """Großbuchstaben, ohne Leerzeichen; erlaubt nur A–Z, 0–9 und Bindestrich."""
    return re.sub(r'[^A-Z0-9-]', '', (text or '').upper())[:40]


def email_schluessel(email):
    email = (email or '').strip().lower()
    if '@' not in email:
        return email
    lokal, domain = email.rsplit('@', 1)
    lokal = lokal.split('+', 1)[0]
    if domain in _GMAIL:
        lokal, domain = lokal.replace('.', ''), 'gmail.com'
    return f'{lokal}@{domain}'


def anschrift_schluessel(strasse, plz):
    """``musterstr12|23552``; leer ohne Straße oder bei Abholung."""
    strasse = (strasse or '').strip().lower()
    if not strasse or strasse.startswith('abholung'):
        return ''
    strasse = strasse.replace('ß', 'ss').replace('strasse', 'str').replace('str.', 'str')
    strasse = re.sub(r'[^a-z0-9äöü]', '', strasse)
    return f"{strasse}|{re.sub(r'[^0-9]', '', plz or '')}"[:220]


def betrag(warenwert, prozent):
    """Abzug in Euro, kaufmännisch auf Cent gerundet."""
    return (Decimal(warenwert) * Decimal(prozent) / Decimal(100)).quantize(Decimal('0.01'), ROUND_HALF_UP)


def schon_bestellt(email='', strasse='', plz=''):
    """True, wenn es unter dieser E-Mail oder Anschrift schon eine zählende Bestellung gibt."""
    from .models import Order
    bedingung = Q()
    if email_schluessel(email):
        bedingung |= Q(email_schluessel=email_schluessel(email))
    if anschrift_schluessel(strasse, plz):
        bedingung |= Q(anschrift_schluessel=anschrift_schluessel(strasse, plz))
    if not bedingung:
        return False
    return Order.objects.exclude(status__in=ZAEHLT_NICHT).filter(bedingung).exists()


@dataclass
class Ergebnis:
    code: object = None          # Rabattcode oder None
    text: str = ''               # eingegebener Code (vereinheitlicht)
    fehler: str = ''             # Meldung für die Kundin, leer = gilt
    prozent: int = 0
    abzug: Decimal = Decimal('0')
    warenwert: Decimal = Decimal('0')

    @property
    def gilt(self):
        return self.code is not None and not self.fehler

    @property
    def gesamt(self):
        return self.warenwert - self.abzug


def pruefe(text, warenwert, email='', strasse='', plz='', sperren=False):
    """Prüft einen Code für einen Warenwert. Mit ``sperren=True`` (nur in einer Transaktion) wird die Zeile des
    Codes gesperrt, damit zwei gleichzeitige Bestellungen Höchstzahl und „erste Bestellung“ nicht beide umgehen."""
    from .models import Rabattcode
    text = normalisiere_code(text)
    ergebnis = Ergebnis(text=text, warenwert=Decimal(warenwert))
    if not text:
        return ergebnis
    abfrage = Rabattcode.objects.select_for_update() if sperren else Rabattcode.objects
    code = abfrage.filter(code=text).first()
    if not code or not code.aktiv:
        ergebnis.fehler = 'Diesen Rabattcode kennen wir nicht. Bitte prüf die Schreibweise.'
        return ergebnis
    if code.gueltig_bis and timezone.localdate() > code.gueltig_bis:
        ergebnis.fehler = f'Der Rabattcode {text} war bis {code.gueltig_bis:%d.%m.%Y} gültig.'
        return ergebnis
    if code.max_einloesungen is not None and code.einloesungen() >= code.max_einloesungen:
        ergebnis.fehler = f'Der Rabattcode {text} ist schon vollständig eingelöst.'
        return ergebnis
    if code.nur_erstbestellung and schon_bestellt(email, strasse, plz):
        ergebnis.fehler = (f'Der Rabattcode {text} gilt nur für die erste Bestellung. Du kannst ohne Code '
                           f'zum regulären Preis bestellen.')
        return ergebnis
    ergebnis.code, ergebnis.prozent = code, code.prozent
    ergebnis.abzug = betrag(warenwert, code.prozent)
    return ergebnis


def gueltiger_code(text):
    """Der Rabattcode zu ``text``, wenn er aktiv, nicht abgelaufen und nicht ausgeschöpft ist (ohne E-Mail-Prüfung)."""
    from .models import Rabattcode
    code = Rabattcode.objects.filter(code=normalisiere_code(text), aktiv=True).first()
    if not code:
        return None
    if code.gueltig_bis and timezone.localdate() > code.gueltig_bis:
        return None
    if code.max_einloesungen is not None and code.einloesungen() >= code.max_einloesungen:
        return None
    return code


def oeffentlicher_code():
    """Der neueste aktive Code, der auf der Website beworben wird – oder ``None`` (dann zeigt die Seite nichts)."""
    from .models import Rabattcode
    for code in Rabattcode.objects.filter(aktiv=True, oeffentlich=True).order_by('-erstellt_am'):
        if gueltiger_code(code.code):
            return code
    return None


def kontext(request):
    """Kontextprozessor: ``willkommenscode`` (öffentlicher Code) in jeder Vorlage, nur wenn verkauft wird."""
    from .verkauf import verkauf_aktiv
    if not verkauf_aktiv():
        return {'willkommenscode': None}
    from django.core.cache import cache
    try:
        code = cache.get('rabatt:oeffentlich', 'leer')
        if code == 'leer':
            code = oeffentlicher_code()
            cache.set('rabatt:oeffentlich', code, 60)
        return {'willkommenscode': code}
    except Exception:  # Datenbank nicht bereit (Start, Migration): Seite ohne Code statt Fehler 500
        return {'willkommenscode': None}
