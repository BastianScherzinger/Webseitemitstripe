"""Texte und Werte der öffentlichen Seiten im Look „Nachtausgabe" (19.09.2026).

Eine Stelle für alles, was sonst in Vorlagen getippt würde: Markensatz, Lead,
Laufband, Drop, Teaser, die Auswahl der Motivanfrage, die fünf Schritte,
Luisas Satz. Quelle der Wortlaute: ``Design/luviq/MARKENWISSEN-luisa.md`` und
``FINALER-BAUPLAN.md`` in den Firmenunterlagen (Luisas Befragung vom
19.09.2026). Luisa darf jeden Satz in ihre Worte ändern – dann hier.

Kein Datum und kein Satz davon steht in einer Vorlage.
"""

import os
from datetime import datetime

from django.utils import timezone

#: Luisas Markensatz, von ihr gewählt am 19.09.2026. Gesprochen, nicht gesetzt.
MARKENSATZ = 'Sag mir, was du willst — ich mal’s dir.'

#: Erster Absatz nach der Überschrift. Nennt den Ort, weil Antwortmaschinen
#: den ersten Absatz zitieren (test_inhalt: Anbieter oder Ort im ersten Absatz).
LEAD = ('Ich bemale in Alsfeld Second-Hand-Teile von Hand, mit Bleiche und Pinsel. '
        'Du sagst mir, was drauf soll, ich schick dir Vorschläge, und dann entsteht '
        'dein Stück. Jedes Motiv gibt es genau einmal.')

#: Erfahrungswert von Luisa, **nie als Zusage** schreiben („meistens").
DAUER = '2 bis 5 Tage'

#: Luisas Satz zum Anfang von Luviq – beiläufig, keine Gründungslegende.
ZITAT = 'Langeweile, schwere Zeit — und Bock, was zu bemalen.'
ZITAT_QUELLE = 'Luisa Brehler, wie Luviq angefangen hat'

INSTAGRAM = 'https://www.instagram.com/luviq.universe/'
INSTAGRAM_NAME = 'luviq.universe'

# ── Drop ─────────────────────────────────────────────────────────────────────

#: Vorgabe für ``DROP_TERMIN``. Leer setzen (``DROP_TERMIN=``) heißt: kein
#: Termin, der Kasten sagt „Die nächste Ausgabe ist in Arbeit." ohne Uhr.
DROP_TERMIN_VORGABE = '2026-10-08T18:00+02:00'

_WOCHENTAGE = ('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag')


def drop_termin(jetzt=None):
    """Der nächste Drop als bewusster Zeitpunkt – oder ``None``.

    ``None`` bei leerer, unlesbarer oder abgelaufener Angabe: dann gibt es
    keinen Countdown, sondern nur „in Arbeit" (Bauplan § 5)."""
    roh = os.getenv('DROP_TERMIN', DROP_TERMIN_VORGABE).strip()
    if not roh:
        return None
    try:
        termin = datetime.fromisoformat(roh)
    except ValueError:
        return None
    if timezone.is_naive(termin):
        termin = timezone.make_aware(termin)
    if termin <= (jetzt or timezone.now()):
        return None
    return termin


def termin_text(termin):
    """„Donnerstag, 08.10., 18 Uhr" in Berliner Zeit."""
    ort = timezone.localtime(termin)
    uhr = f'{ort.hour} Uhr' if not ort.minute else f'{ort.hour}:{ort.minute:02d} Uhr'
    return f'{_WOCHENTAGE[ort.weekday()]}, {ort:%d.%m.}, {uhr}'


def drop_nummer():
    """Nummer der nächsten Ausgabe, dreistellig: ``DROP_NUMMER`` oder die
    nächste freie Archivnummer. So bekommt der Drop nie eine Nummer, die im
    Archiv schon vergeben ist."""
    fest = os.getenv('DROP_NUMMER', '').strip()
    if fest.isdigit():
        return f'{int(fest):03d}'
    from django.db.models import Max
    from .models import Produkt
    try:
        hoechste = Produkt.objects.aggregate(m=Max('nummer'))['m'] or 0
    except Exception:
        hoechste = 0
    return f'{hoechste + 1:03d}'


#: Kopfzeile des Hero: „LUVIQ · Ausgabe 01 | Oktober 2026 | Alsfeld".
AUSGABE = '01'
_MONATE = ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
           'September', 'Oktober', 'November', 'Dezember')

#: Das Stück im Panorama-Foto (static/shop1/images/luviq/hero-*). Die Nummer
#: kommt aus dem Archiv (erster Name, der einen der ``suche``-Begriffe
#: enthält), damit sie mit der Karte übereinstimmt; ohne Treffer steht nur der
#: Name da. Live heißt die Spinnennetz-Jeans „Custom Pants" (Stand 19.09.2026).
HERO_STUECK = {'name': 'Spinnennetz-Jeans', 'suche': ('spinnen', 'pants'),
               'alt': 'Handbemalte Jeans mit Spinnennetz-Motiv, draußen im Gras fotografiert'}

#: Teaser vor dem Drop: (Datum, Titel, Bildadresse, Alternativtext). Leer ⇒
#: der Abschnitt „Nº …, in Teilen" entfällt ganz – keine leeren Kacheln.
TEASER = []


def laufband(nummer, termin):
    teile = ['Motiv anfragen, ohne Kosten']
    if termin:
        teile.append(f'Nº {nummer} erscheint {termin_text(termin)}')
    else:
        teile.append('Die nächste Ausgabe ist in Arbeit')
    teile.append('Handbemalt in Alsfeld')
    return teile


def drop_kontext(jetzt=None):
    """Alles, was Laufband und Drop-Kasten brauchen – für den Kontextprozessor."""
    jetzt = jetzt or timezone.now()
    termin = drop_termin(jetzt)
    nummer = drop_nummer()
    monat = timezone.localtime(termin or jetzt)
    rest = {}
    if termin:
        sekunden = int((termin - jetzt).total_seconds())
        rest = {'d': f'{sekunden // 86400:02d}', 'h': f'{sekunden % 86400 // 3600:02d}',
                'm': f'{sekunden % 3600 // 60:02d}', 's': f'{sekunden % 60:02d}'}
    return {
        'ausgabe': AUSGABE,
        'monat': f'{_MONATE[monat.month - 1]} {monat.year}',
        'rest': rest,
        'nummer': nummer,
        'termin': termin,
        'termin_iso': timezone.localtime(termin).isoformat() if termin else '',
        'termin_text': termin_text(termin) if termin else '',
        'laufband': laufband(nummer, termin),
        'teaser': TEASER,
    }


# ── Motivanfrage ─────────────────────────────────────────────────────────────

#: Luisas erste Frage ist immer „in welche Richtung?" (Markenwissen § 5).
RICHTUNGEN = [
    ('tier', 'Tier'),
    ('symbol', 'Symbol oder Zeichen'),
    ('pflanze', 'Pflanze oder Ranke'),
    ('himmel', 'Mond und Sterne'),
    ('abstrakt', 'Abstrakt'),
    ('offen', 'Weiß ich noch nicht'),
]

TEILE = [
    ('hoodie', 'Hoodie'),
    ('sweatshirt', 'Sweatshirt'),
    ('jeans', 'Jeans'),
    ('shirt', 'Shirt'),
    ('eigenes', 'Hab ich selbst'),
]

PLATZIERUNGEN = [
    ('ruecken', 'Groß auf dem Rücken'),
    ('vorne', 'Kleiner vorne'),
    ('offen', 'Weiß ich noch nicht'),
]

#: Die drei Zeilen des Abschnitts „Du hast eine Idee?" auf der Startseite.
ANFRAGE_ABLAUF = [
    ('Du beschreibst dein Motiv', 'Richtung, Teil und was es dir bedeutet.'),
    ('Ich schick dir Vorschläge', 'Per Instagram oder Mail, persönlich von mir.'),
    ('Wir entscheiden zusammen', 'Erst wenn es passt, fange ich an.'),
]

#: Die vier Stationen auf der Seite /motiv-anfragen/.
ANFRAGE_STATIONEN = ['Anfrage', 'Vorschläge', 'Entscheidung', 'Malen']

# ── Entstehung ───────────────────────────────────────────────────────────────

#: Luisas fünf echte Schritte (Markenwissen § 7). Bild: Dateiname unter
#: shop1/static/shop1/images/luviq/ – bis ihr Arbeitsfoto da ist, die
#: vorhandenen Stückfotos.
SCHRITTE = [
    ('Design finden', 'Wir klären die Richtung, ich schick dir ein paar Vorschläge, '
                      'und wir entscheiden zusammen.', 'eclipse-crew', 'Sweatshirt mit gebleichtem Eclipse-Motiv'),
    ('Skizze', 'Das Motiv entsteht erst auf Papier, mit Bleistift.',
     'augen-mit-fluegeln', 'Pullover mit Augen und Flügeln auf dem Rücken'),
    ('Vorzeichnen', 'Dann zeichne ich es direkt auf dein Teil vor.',
     'spinnennetz-jeans-hoch', 'Jeans mit Spinnennetz-Motiv am Bein'),
    ('Bleiche', 'Mit dem Pinsel zieht die Bleiche die Farbe aus dem Stoff. '
                'Ein Strich lässt sich nicht zurücknehmen.', 'dornenaugen-hoodie',
     'Hoodie mit gebleichtem Dornen-Motiv auf dem Rücken'),
    ('Waschen und los', 'Waschen, fotografieren, einpacken und ab zu dir.',
     'drache', 'Hoodie mit Drachen-Motiv auf dem Rücken'),
]
