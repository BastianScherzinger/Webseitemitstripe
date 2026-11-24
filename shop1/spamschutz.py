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

Seit 24.11.2026 (Analyse der Railway-Logs und aller 37 gespeicherten Kontaktnachrichten, Büro-Bericht
2026-11-24_LUVIQ-SPAM): von 37 Nachrichten war keine einzige eine Kundenanfrage; die Abwehr ließ 0 Punkte
durch, weil kein Merkmal der drei Bot-Arten gesucht wurde. Neu:

* **Preisfrage-Bot** („Hi, i write about your price“ + ein Satz in einer Zufallssprache) — +5;
* **Kauderwelsch** („Jfeuwgduwefhw fuhefyugewfhqwyfuewu …“) — Wörter ohne gebräuchliche Buchstabenpaare;
* **Zahlenmuster** („NARTYTRYUT2173457NEWETREWT“, dieselbe Zahl in Name, Betreff und Text) — +5;
* **Wegwerf-Adresse** (``belettersmail.com``, ``mailinator.com`` …) — +3;
* Verdachtsfälle werden **gespeichert** (``KontaktAnfrage.einstufung = 'spam'``), nur ohne Mail.

Dienstleistungs-Angebote (SEO, Video, Webdesign …) sind kein Bot-Spam: sie erkennt ``angebote.py``.
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
_EIGENE_VORGABE = ('luviq-alsfeld.com', 'luviq-luebeck.com')

_ZUSAMMEN = re.compile(r'^[A-Z][a-z]+[A-Z][a-z]+$')          # „RobertBoobe“
_FREMDSCHRIFT = re.compile('[Ѐ-ӿ一-鿿぀-ヿ]')


# ── Seit 24.11.2026: die drei Arten, die bis dahin mit 0 Punkten durchkamen ──

#: „Hi, i write about your price for reseller“ – Vorlagenbetreff mit Doppelleerzeichen, dazu ein Satz
#: in einer Zufallssprache („Sveiki, aš norėjau sužinoti jūsų kainą.“).
_PREISFRAGE = re.compile(r'\b(?:writ\w*|wrote)\s+(?:about|to ask)\b.{0,40}\bpric', re.I)
#: Die Vorlage lässt beim Füllen Wörter weg und hinterlässt zwei oder mehr Leerzeichen in Folge.
_LUECKEN = re.compile(r'\S\s{2,}\S')
#: Name/Betreff/Text wie „NARTYTRYUT2173457NEWETREWT“.
_ZAHLENMUSTER = re.compile(r'[A-Za-z]{4,}(\d{5,})[A-Za-z]{3,}')

#: Wegwerf- und Testadressen (Teilzeichenfolgen der Domain).
_WEGWERF = ('belettersmail.', 'notlettersmail.', 'mailinator.', 'guerrillamail', 'sharklasers.',
            '10minutemail', 'tempmail', 'temp-mail', 'trashmail', 'yopmail.', 'getnada.', 'dispostable.',
            'maildrop.cc', 'throwawaymail', 'fakeinbox.', 'moakt.', 'mohmal.', 'emailondeck.', 'mintemail.',
            'spambox.', 'tmpmail.', 'mailnesia.', 'burnermail.', 'inboxkitten.', 'lettersmail.')

# Kauderwelsch: Tastaturgeklapper („Jfeuwgduwefhw fuhefyugewfhqwyfuewu“). Gelernt wird an einem kleinen
# Text in den Sprachen, in denen Kundschaft schreibt; ein Wort fällt auf, wenn die Hälfte seiner
# Buchstabenpaare in keinem davon vorkommt. Geprüft werden nur Wörter ab 8 Buchstaben aus reinen
# ASCII-Buchstaben (Wörter mit Umlaut, Akzent oder anderer Schrift zählen nie), und erst ab zwei
# auffälligen Wörtern, die zusammen mindestens die Hälfte aller langen Wörter ausmachen.
_LERNTEXT = """
Hallo Luisa, ich hätte gern eine Jacke mit einem Drachen auf dem Rücken. Geht das bis Dezember? Ist Nummer 006 noch frei?
Ich möchte gern das Engel Shirt in Größe M bestellen und wüsste gern wie lange der Versand nach Österreich dauert.
Könnten Sie mir bitte ein Foto oder ein kurzes Video von dem Stück schicken, damit ich die Farben besser sehen kann?
Vielen Dank für Ihre Antwort und freundliche Grüße aus Hamburg. Das Material, die Verarbeitung und die Passform interessieren mich sehr.
Entschuldigung, beschriftet, Schnittmuster, Strickjacke, Geschenkverpackung, Nachhaltigkeit, Unikate, handgemacht, Rücksendung,
Zahlungsmöglichkeiten, Bestellnummer, Lieferzeit, Wochenende, Weihnachtsgeschenk, Kleidergröße, Schulterbreite, Zusammenarbeit,
Kooperation, Anfrage, Werbung, Influencer, Fotoshooting, Marketing, Videoproduktion, Reißverschluss, Kapuzenpullover, Übergangsjacke.
Hello, I would like to ask whether the jacket is still available and if you ship internationally. Thank you very much for your help,
best regards. The shirt looks great, could you send me more pictures please? I follow you on Instagram and love the handmade bleached designs.
Optimization, professional, information, development, communication, understand, something, business, together, wonderful, beautiful,
interested, available, delivery, question, customers, strategy, advertising, collaboration, photography, wholesale, shipping, packaging.
Bonjour, je voudrais savoir si la veste est encore disponible et quel est le délai de livraison. Merci beaucoup pour votre réponse.
Hola, quería saber si la chaqueta todavía está disponible y cuánto cuesta el envío. Muchas gracias por su respuesta y un saludo.
Ciao, vorrei sapere se la giacca è ancora disponibile e quanto costa la spedizione, grazie mille e buona giornata.
Hallo, ik wil graag weten of het shirt nog beschikbaar is en hoe lang de verzending duurt, alvast bedankt voor uw antwoord.
Olá, gostaria de saber se o casaco ainda está disponível e quanto custa o envio, muito obrigado pela resposta e cumprimentos.
Dzień dobry, chciałbym zapytać czy kurtka jest jeszcze dostępna oraz ile kosztuje wysyłka, dziękuję bardzo za odpowiedź.
Merhaba, ceketin hala satışta olup olmadığını ve kargo ücretini öğrenmek istiyorum, cevabınız için çok teşekkür ederim.
"""


def _paare(wort):
    return [wort[i:i + 2] for i in range(len(wort) - 1)]


def _gelernte_paare():
    zaehler = {}
    for w in re.findall(r'[a-zäöüßéèàáíóúñçêôâîûœąęłńśźżğşı]+', _LERNTEXT.lower()):
        for p in _paare(w):
            zaehler[p] = zaehler.get(p, 0) + 1
    return frozenset(p for p, n in zaehler.items() if n >= 2)


_PAARE = _gelernte_paare()


def kauderwelsch(text, mindestens=3):
    """``True`` bei Tastaturgeklapper: mindestens ``mindestens`` lange ASCII-Wörter, deren Buchstabenpaare
    zu mehr als der Hälfte in keiner Kundensprache vorkommen, und diese Wörter sind die Hälfte oder mehr
    aller langen Wörter. Ein Wort neben einem Umlaut oder Akzent zählt nicht (kein Teilwort von „ücretsiz“)."""
    lange = re.findall(r'(?<![^\W_])[A-Za-z]{8,}(?![^\W_])', text or '')
    lange = [w for w in lange if len(set(w.lower())) > 3]   # „xxxxxxxxx“ ist Füllung, kein Geklapper
    if len(lange) < mindestens:
        return False
    auffaellig = [w for w in lange
                  if sum(1 for p in _paare(w.lower()) if p not in _PAARE) / (len(w) - 1) > 0.55]
    return len(auffaellig) >= mindestens and len(auffaellig) * 2 >= len(lange)


def wegwerf_adresse(email):
    """``True``, wenn die Domain der Adresse ein Wegwerfdienst ist."""
    if '@' not in (email or ''):
        return False
    domain = email.rsplit('@', 1)[1].strip().lower()
    return any(m in domain for m in _WEGWERF)


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

    # Seit 24.11.2026 – siehe Kopf der Datei.
    if _PREISFRAGE.search(betreff) and len(nachricht) <= 120:
        # Mit den Lücken der Vorlage ist es der Bot; ohne sie könnte ein Mensch nach dem Preis fragen.
        if _LUECKEN.search(betreff) or re.search(r'\bfor resell', betreff, re.I):
            treffer(5, 'preis-bot')
        else:
            treffer(2, 'preis-bot-schwach')
    zahlen = [m.group(1) for m in _ZAHLENMUSTER.finditer(alles)]
    if zahlen and (len(zahlen) >= 2 or _ZAHLENMUSTER.search(name)):
        treffer(5, 'zahlenmuster')
    if kauderwelsch(betreff + ' ' + nachricht):
        treffer(4 + (2 if kauderwelsch(betreff, 2) else 0), 'kauderwelsch')
    elif kauderwelsch(betreff, 2) and kauderwelsch(name, 1):
        treffer(5, 'kauderwelsch')
    if wegwerf_adresse(daten.get('email') or ''):
        treffer(3, 'wegwerf-mail')
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
