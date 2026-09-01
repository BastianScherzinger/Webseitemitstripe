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
    'home':         '2026-09-01',
    'produkte':     '2026-09-01',
    'gaestebuch':   '2026-09-01',
    'ueber_uns':    '2026-09-01',
    'liefergebiet': '2026-09-01',
    'kontakt':      '2026-09-01',
    'impressum':    '2026-09-01',
    'datenschutz':  '2026-09-01',
    'agb':          '2026-09-01',
}

#: Routenname → Bezeichnung der Seite, wörtlich so, wie sie in der Navigation
#: und im Fusszeilen-Menü von ``base.html`` sichtbar ist. Der ``WebPage``-
#: Knoten trägt sie als ``name``; ein Schema, das eine Seite anders nennt als
#: die Seite selbst, ist schlimmer als keines.
SEITEN_NAME = {
    'home':         'Home',
    'produkte':     'Produkte',
    'gaestebuch':   'Gästebuch',
    'ueber_uns':    'Über uns',
    'liefergebiet': 'Liefergebiet',
    'kontakt':      'Kontakt',
    'impressum':    'Impressum',
    'datenschutz':  'Datenschutz',
    'agb':          'AGB',
}


def seite_fuer(url_name):
    """Registereintrag der Route als ``{'name': …, 'stand': …}`` oder ``None``.

    ``None`` ist der sichere Rückfall für alles, was nicht im Register steht
    (Produktseiten, Konto-Seiten, Admin-Panel, 404): ``base.html`` lässt
    ``name`` und ``dateModified`` dann weg, statt etwas zu erfinden.
    """
    if url_name not in SEITEN_STAND:
        return None
    return {'name': SEITEN_NAME[url_name], 'stand': SEITEN_STAND[url_name]}
