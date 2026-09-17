"""Spamschutz für das Kontaktformular (17.09.2026).

Anlass: Das Formular schickte jede Einsendung ungeprüft als Mail an die Betreiberin —
am 16.09.2026 kam so „THE LAMBORGHINI AVENTADOR SWEEPSTAKES CLOSES SOON“ von
„RobertBoobe“ mit einem telegra.ph-Link an. Das ist Bot-Spam, kein Kunde.

Punkteverfahren, ab ``SCHWELLE`` wird **still verworfen**: der Absender sieht dieselbe
Bestätigungsseite wie ein echter Kunde, es geht keine Mail hinaus. Ein Bot, der eine
Fehlermeldung sieht, probiert die nächste Variante.

Kein einzelnes schwaches Signal blockt allein. Ein fehlender Zeitstempel (+2) trifft
auch einen Menschen ohne JavaScript oder mit sehr altem Tab — deshalb reicht er nicht.
"""

import re
import time

from django.core import signing

SCHWELLE = 5
MINDESTZEIT = 3                 # Sekunden zwischen Anzeigen und Absenden
HOECHSTALTER = 24 * 3600
FELD_FALLE = 'webseite'         # unsichtbar; ein Mensch füllt es nie aus
FELD_ZEIT = 'formzeit'
_SALZ = 'shop1.spamschutz'

_LINK = re.compile(r'https?://|www\.|telegra\.ph|t\.me/|bit\.ly', re.I)
_WOERTER = re.compile(
    r'sweepstake|lamborghini|aventador|you are a snap away|claim your|winner|'
    r'jackpot|casino|crypto|bitcoin|forex|viagra|seo servic|backlinks?\b|'
    r'gewinnspiel|gewonnen|перевод|руб\.', re.I)
_ZUSAMMEN = re.compile(r'^[A-Z][a-z]+[A-Z][a-z]+$')          # „RobertBoobe“
_FREMDSCHRIFT = re.compile('[Ѐ-ӿ一-鿿぀-ヿ]')


def zeitstempel():
    """Signierter Ausgabezeitpunkt für das versteckte Feld."""
    return signing.dumps(int(time.time()), salt=_SALZ)


def bewerte(daten, jetzt=None):
    """(punkte, gruende) für die POST-Daten."""
    jetzt = time.time() if jetzt is None else jetzt
    punkte, gruende = 0, []

    def treffer(wert, grund):
        nonlocal punkte
        punkte += wert
        gruende.append(grund)

    if (daten.get(FELD_FALLE) or '').strip():
        treffer(10, 'falle')

    roh = daten.get(FELD_ZEIT) or ''
    if not roh:
        treffer(2, 'ohne-zeit')
    else:
        try:
            ausgegeben = int(signing.loads(roh, salt=_SALZ, max_age=HOECHSTALTER))
        except (signing.BadSignature, ValueError, TypeError):
            treffer(4, 'zeit-gefaelscht')
        else:
            if jetzt - ausgegeben < MINDESTZEIT:
                treffer(3, 'zu-schnell')

    name = daten.get('name') or ''
    betreff = daten.get('betreff') or ''
    nachricht = daten.get('nachricht') or ''
    alles = ' '.join((name, betreff, nachricht))

    if _LINK.search(name) or _LINK.search(betreff):
        treffer(5, 'link-im-kopf')
    links = len(_LINK.findall(nachricht))
    if links >= 2:
        treffer(3, 'links')
    elif links:
        treffer(2, 'link')
    if _WOERTER.search(alles):
        treffer(4, 'spamwort')
    if _ZUSAMMEN.match(name.strip()):
        treffer(2, 'name-zusammen')
    if _FREMDSCHRIFT.search(alles) and _LINK.search(alles):
        treffer(3, 'fremdschrift-link')
    return punkte, gruende


def ist_spam(daten, jetzt=None):
    return bewerte(daten, jetzt)[0] >= SCHWELLE
