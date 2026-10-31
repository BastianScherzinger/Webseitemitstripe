"""Gepflegter Stand der statischen Seiten.

Ein einziges Register speist zwei Stellen, damit sie nicht auseinanderlaufen:
das ``<lastmod>`` der Sitemap (``views/legal.py``) und das ``dateModified``
des ``WebPage``-Knotens im JSON-LD jeder Seite (``base.html``, gefüllt über
``context_processors.py``).

Das Register wird **von Hand** nachgezogen, wenn sich der Inhalt einer Seite
ändert. Absichtlich kein Datei-Änderungsdatum und kein Build-Zeitpunkt:
beide springen bei jedem Deploy hoch und würden Suchmaschinen eine Änderung
vorgaukeln, die es nicht gab – dann verlieren sie das Vertrauen in die
Angabe. Die Daten unten sind belegt durch
``git log -1 --date=short -- <Template>`` am 2026-09-01.

Kein Datenbankzugriff, kein Import aus ``models`` oder ``views``: dieses
Modul wird bei jedem Request aus dem Kontextprozessor gelesen.
"""

#: Routenname → Datum der letzten inhaltlichen Änderung (ISO 8601).
SEITEN_STAND = {
    # 31.10.2026: Direktkauf ohne Konto – Texte zu Bestellung, Zahlung, Vormerken und Verlinkung
    # (home, produkte, ueber_uns, liefergebiet, kontakt, motiv_anfragen, wissen*, agb, datenschutz).
    # 23.10.2026: Sitz Lübeck laut Gewerbeanmeldung, Alsfeld als Herkunft – Titel,
    # Beschreibungen und Texte aller Seiten; deshalb tragen alle dieses Datum.
    'home':         '2026-10-31',
    'produkte':     '2026-10-31',
    'gaestebuch':   '2026-10-31',
    'ueber_uns':    '2026-10-31',
    'liefergebiet': '2026-10-31',
    'kontakt':      '2026-10-31',
    'impressum':    '2026-10-30',  # VSBG-Satz (Rechts-Runde 30.10.)
    'datenschutz':  '2026-10-31',  # vollständige Erklärung (Rechts-Runde 30.10.)
    'agb':          '2026-10-31',  # AGB §§ 1–14 + Widerrufsbelehrung (Rechts-Runde 30.10.)
    # IS19 (27.09.2026): Erklärsätze der Stationen, Dauer, Bestätigungshinweis.
    # 02.10.2026 (L1-B1): Titel, Beschreibung, Vorschaubild und Twitter-Angaben neu
    # (IS03/06/07/09/10/11/13/36/39, EIG137) — home, produkte, gaestebuch, ueber_uns,
    # liefergebiet, kontakt, datenschutz und motiv_anfragen tragen deshalb dieses Datum.
    'motiv_anfragen': '2026-10-31',
    # Wissensbereich (Welle 6, Schritte 26–29): Routennamen aus views/wissen.py.
    'wissen':           '2026-10-31',
    'wissen_pflege':    '2026-10-30',
    'wissen_upcycling': '2026-10-31',
    'wissen_groesse':   '2026-10-30',
    'wissen_motiv':     '2026-10-23',  # Entwurf, noindex
    # Ratgeber (30.10.2026, C8), seit Runde 3 veröffentlicht; ISO 8601 mit Uhrzeit und Zone:
    'wissen_bleach':      '2026-10-30T14:15:00+01:00',  # veröffentlicht, Runde 3
    'wissen_bleichfleck': '2026-10-30T14:15:00+01:00',  # veröffentlicht, Runde 3
    # Belegte Beiträge ohne Freigabevorbehalt (SU04, 2026-09-07).
    # Quellenverweise im Fliesstext (GE43, 2026-09-17).
    'wissen_bestellen': '2026-10-31',
    'wissen_widerruf':  '2026-10-30',
    'wissen_konto':     '2026-10-31',
}

#: Routenname → Bezeichnung der Seite, wörtlich so, wie sie in der Navigation
#: und im Fusszeilen-Menü von ``base.html`` sichtbar ist. Der ``WebPage``-
#: Knoten trägt sie als ``name``; ein Schema, das eine Seite anders nennt als
#: die Seite selbst, ist schlimmer als keines. Die Wissensseiten stehen in
#: keinem Menü; ihr Name ist der Text ihrer ``h1`` (die Übersicht: die
#: Bereichsbezeichnung „Wissen", die dort als Kicker über der ``h1`` steht).
SEITEN_NAME = {
    'home':         'Startseite',
    'produkte':     'Archiv',
    'gaestebuch':   'Gästebuch',
    'ueber_uns':    'Luisa',
    'liefergebiet': 'Versand & Abholung',
    'kontakt':      'Kontakt',
    'impressum':    'Impressum',
    'datenschutz':  'Datenschutz',
    'agb':          'AGB',
    'motiv_anfragen': 'Motiv anfragen',
    'wissen':           'Wissen',
    'wissen_pflege':    'Wie pflege ich handbemalte Kleidung?',
    'wissen_upcycling': 'Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand?',
    'wissen_groesse':   'Wie finde ich bei Einzelstücken die richtige Größe?',
    'wissen_motiv':     'Wie entsteht aus meiner Idee ein handbemaltes Stück?',
    'wissen_bleach':      'Was ist Bleach Painting?',
    'wissen_bleichfleck': 'Bleichfleck übermalen: geht das?',
    'wissen_bestellen': 'Wie bestelle und bezahle ich bei Luviq Universe?',
    'wissen_widerruf':  'Widerruf und Rücksendung: was gilt bei einem Einzelstück?',
    'wissen_konto':     'Was speichert der Shop – und brauche ich ein Konto?',
}


#: Abweichende Namen, solange ``VERKAUF_AKTIV`` aus ist (shop1/verkauf.py).
#: Seit P1/P2 (29.10.2026) heißt die Seite mit und ohne Verkauf „Versand & Abholung“; der
#: Mechanismus bleibt für künftige Fälle.
SEITEN_NAME_OHNE_VERKAUF = {}


def seite_fuer(url_name):
    """Registereintrag der Route als ``{'name': …, 'stand': …}`` oder ``None``.

    ``None`` ist der sichere Rückfall für alles, was nicht im Register steht
    (Produktseiten, Konto-Seiten, Admin-Panel, 404): ``base.html`` lässt
    ``name`` und ``dateModified`` dann weg, statt etwas zu erfinden.
    """
    if url_name not in SEITEN_STAND:
        return None
    name = SEITEN_NAME[url_name]
    # Verkaufsschalter: ohne Verkauf kann eine Seite sichtbar anders heißen; der
    # WebPage-Name folgt (derzeit kein Eintrag).
    from django.conf import settings
    if not getattr(settings, 'VERKAUF_AKTIV', False):
        name = SEITEN_NAME_OHNE_VERKAUF.get(url_name, name)
    stand = SEITEN_STAND[url_name]
    return {'name': name, 'stand': stand, 'stand_anzeige': stand_anzeige(stand)}


_MONATE = ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
           'August', 'September', 'Oktober', 'November', 'Dezember')


def stand_anzeige(iso):
    """``'2026-10-02'`` → ``'2. Oktober 2026'`` – das sichtbare Datum (GE47).

    Eigene Monatsliste statt ``|date``: unabhängig von der aktiven Sprache,
    und dieselbe Zeichenkette wie im ``dateModified`` bleibt die Quelle."""
    jahr, monat, tag = (int(t) for t in iso[:10].split('-'))
    return f'{tag}. {_MONATE[monat - 1]} {jahr}'
