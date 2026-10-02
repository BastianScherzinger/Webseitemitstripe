"""Spamschutz für das Kontaktformular (17.09.2026).

Anlass: Das Formular schickte jede Einsendung ungeprüft als Mail an die Betreiberin —
am 16.09.2026 kam so „THE LAMBORGHINI AVENTADOR SWEEPSTAKES CLOSES SOON“ von
„RobertBoobe“ mit einem telegra.ph-Link an. Das ist Bot-Spam, kein Kunde.

Punkteverfahren, ab ``SCHWELLE`` wird **still verworfen**: der Absender sieht dieselbe
Bestätigungsseite wie ein echter Kunde, es geht keine Mail hinaus. Ein Bot, der eine
Fehlermeldung sieht, probiert die nächste Variante.

Kein einzelnes schwaches Signal blockt allein. Ein fehlender Zeitstempel (+2) trifft
auch einen Menschen ohne JavaScript oder mit sehr altem Tab — deshalb reicht er nicht.

Seit 02.10.2026 (Bausteine der Agenturseite, ``doku/80-AUFGABEN.md`` „Missbrauchsschutz“):

* **nackte Domain** — „suchmaschine-eintrag.pro“ ohne ``http://`` zählt wie ein Link (+1);
* **fremde Domain mit eigenem Markennamen** — ``info@search-luviq-alsfeld.xyz`` gibt es nur,
  um wie diese Seite auszusehen (+5, allein über der Schwelle). Die eigenen Domains sind
  ausgenommen (``eigene_domains``);
* **Mail-Obergrenze je Tag** — :func:`mail_budget_ok`: was darüber liegt, steht trotzdem
  gespeichert im Panel, nur die Benachrichtigungsmail entfällt;
* **Prüfbefehl** — ``python manage.py pruefe_abwehr`` rechnet Bot- und Menschenfälle durch.
"""

import os
import re
import time
import logging

from django.conf import settings
from django.core import signing
from django.core.cache import cache

_log = logging.getLogger('shop1')

SCHWELLE = 5
MINDESTZEIT = 3                 # Sekunden zwischen Anzeigen und Absenden
HOECHSTALTER = 24 * 3600
FELD_FALLE = 'website'          # unsichtbar; ein Mensch füllt es nie aus
FELD_FALLE_ALT = 'webseite'     # Name bis 02.10.2026: Formulare, die noch im Browser offen sind
FELD_ZEIT = 'formzeit'
_SALZ = 'shop1.spamschutz'

_LINK = re.compile(r'https?://|www\.|telegra\.ph|t\.me/|bit\.ly', re.I)
_WOERTER = re.compile(
    r'sweepstake|lamborghini|aventador|you are a snap away|claim your|winner|'
    r'jackpot|casino|crypto|bitcoin|forex|viagra|seo servic|backlinks?\b|'
    r'gewinnspiel|gewonnen|перевод|руб\.', re.I)
# Adresse ohne ``http://`` und ohne ``www.``: „suchmaschine-eintrag.pro“. Das Muster oben
# sucht ein Schema; wer keins schreibt, kam bis 02.10.2026 mit 0 Punkten durch.
_NACKTE_DOMAIN = re.compile(
    r'\b[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?'
    r'\.(?:de|com|net|org|eu|at|ch|info|biz|shop|online|site|pro|xyz|top|'
    r'icu|club|live|click|link|buzz|cyou|rest|monster|quest|io|dev|app|me|tv)\b', re.I)

#: Der Markenkern, nach dem eine Nachahmer-Domain sucht. ``luviq`` steckt in keinem
#: gebräuchlichen Wort; deshalb genügen fünf Zeichen (die Agenturseite verlangt sechs).
MARKENKERN = 'luviq'
_EIGENE_VORGABE = ('luviq-alsfeld.com',)

_ZUSAMMEN = re.compile(r'^[A-Z][a-z]+[A-Z][a-z]+$')          # „RobertBoobe“
_FREMDSCHRIFT = re.compile('[Ѐ-ӿ一-鿿぀-ヿ]')


def eigene_domains():
    """Die Domains dieser Seite (ohne ``www.``): Vorgabe, ``CANONICAL_HOST`` und die
    kommagetrennte Umgebungsvariable ``SPAM_EIGENE_DOMAINS`` (falls Luisa eine
    zweite Domain bekommt, trägt Bastian sie dort ein)."""
    roh = list(_EIGENE_VORGABE)
    roh.append(getattr(settings, 'CANONICAL_HOST', '') or '')
    roh += (os.getenv('SPAM_EIGENE_DOMAINS') or '').split(',')
    ergebnis = set()
    for eintrag in roh:
        eintrag = eintrag.strip().lower().split(':')[0]
        if eintrag.startswith('www.'):
            eintrag = eintrag[4:]
        if eintrag:
            ergebnis.add(eintrag)
    return ergebnis


def markenimitation(email, text):
    """``True``, wenn eine FREMDE Domain den eigenen Markennamen trägt.

    Geprüft werden die Domain der E-Mail-Adresse und jede nackte Domain im Text.
    Die eigenen Domains und ihre Unterdomains sind ausgenommen, sonst blockte die Abwehr
    die eigene Testmail. Punkte zählen als Bindestrich: ``luviq.alsfeld.xyz`` fällt
    genauso auf wie ``search-luviq-alsfeld.com``."""
    eigene = eigene_domains()
    kandidaten = []
    if '@' in (email or ''):
        kandidaten.append(email.rsplit('@', 1)[1].strip().lower())
    kandidaten += [d.lower() for d in _NACKTE_DOMAIN.findall(text or '')]
    for domain in kandidaten:
        if any(domain == e or domain.endswith('.' + e) for e in eigene):
            continue
        if MARKENKERN in domain.replace('.', '-'):
            return True
    return False


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

    if (daten.get(FELD_FALLE) or '').strip() or (daten.get(FELD_FALLE_ALT) or '').strip():
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
    if not links and _NACKTE_DOMAIN.search(alles):
        treffer(1, 'nackte-domain')
    if markenimitation(daten.get('email') or '', alles):
        treffer(5, 'markenimitation')
    if _WOERTER.search(alles):
        treffer(4, 'spamwort')
    if _ZUSAMMEN.match(name.strip()):
        treffer(2, 'name-zusammen')
    if _FREMDSCHRIFT.search(alles) and _LINK.search(alles):
        treffer(3, 'fremdschrift-link')
    return punkte, gruende


def ist_spam(daten, jetzt=None):
    return bewerte(daten, jetzt)[0] >= SCHWELLE


# ── Notbremse für das Postfach ──────────────────────────────────────────────

#: Höchstzahl der Benachrichtigungsmails je Stunde und je Tag über alle Absender.
#: Letzte Instanz: umgeht jemand künftig jedes einzelne Signal, läuft das Postfach nicht
#: voll. Der Zähler liegt im ``LocMemCache`` und gilt je Gunicorn-Prozess (Vorgabe 2).
MAIL_OBERGRENZE_STUNDE = 10
MAIL_OBERGRENZE_TAG = 40


def mail_budget_ok(art='anfrage', stunde=None, tag=None):
    """``False``, sobald die Obergrenze an Benachrichtigungen erreicht ist.

    Was darüber liegt, steht trotzdem gespeichert (Panel „Kontaktanfragen“ bzw.
    „Motivanfragen“) — es geht die Mail verloren, nicht die Anfrage. Bewusst **keine**
    Warnmail beim Erreichen der Grenze: das wäre derselbe Spam mit anderem Betreff; das
    Erreichen steht im Protokoll."""
    if stunde is None:
        stunde = getattr(settings, 'MAIL_OBERGRENZE_STUNDE', MAIL_OBERGRENZE_STUNDE)
    if tag is None:
        tag = getattr(settings, 'MAIL_OBERGRENZE_TAG', MAIL_OBERGRENZE_TAG)
    jetzt = int(time.time())
    schluessel_h = f'mailbudget:{art}:h:{jetzt // 3600}'
    schluessel_d = f'mailbudget:{art}:d:{jetzt // 86400}'
    pro_stunde = cache.get(schluessel_h, 0)
    pro_tag = cache.get(schluessel_d, 0)
    if pro_stunde >= stunde:
        _log.warning('Mail-Obergrenze (%s): %d Mails in dieser Stunde, weitere Anfragen '
                     'werden nur noch gespeichert', art, pro_stunde)
        return False
    if pro_tag >= tag:
        _log.warning('Mail-Obergrenze (%s): Tagesgrenze %d erreicht', art, tag)
        return False
    cache.set(schluessel_h, pro_stunde + 1, 3600)
    cache.set(schluessel_d, pro_tag + 1, 86400)
    return True
