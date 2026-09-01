"""Fingerabdruck des sichtbaren Seitenaufbaus.

Erfasst wird nur, was geschützt ist: die Reihenfolge der Elemente im
``<body>``, ihre Kennungen und CSS-Klassen, die Überschriftentexte und die
Anzahl von Bildern, Formularen, Links, Eingabefeldern und Schaltflächen.

Bewusst **nicht** erfasst und damit änderbar: alles im ``<head>`` (Titel,
Meta-Angaben, canonical, JSON-LD), Attribute wie ``alt``, ``aria-*``,
``title``, ``rel``, ``loading``, ``srcset``, ``fetchpriority``, ``decoding``,
``href`` und ``src`` sowie jeder Fliesstext ausserhalb von Überschriften.

Kein Testmodul (Name beginnt nicht mit ``test``), wird nur importiert.
"""

from html.parser import HTMLParser

#: Elemente, deren Inhalt nicht zum sichtbaren Aufbau gehört.
_STUMM = {'script', 'style'}

#: Elemente ohne schliessendes Tag – sie dürfen die Verschachtelung nicht stören.
_LEER = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
         'link', 'meta', 'param', 'source', 'track', 'wbr'}

_UEBERSCHRIFTEN = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}

#: Elemente, deren Anzahl Regel 1 wörtlich schützt.
_GEZAEHLT = ('img', 'form', 'a', 'input', 'button', 'select', 'textarea',
             'iframe', 'video', 'picture', 'source')


class _Sammler(HTMLParser):
    """Liest den ``<body>`` und sammelt die geschützten Merkmale."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.im_body = False
        self._stumm_tiefe = 0
        self._ueberschrift = None
        self.tags = []
        self.kennungen = []
        self.klassen = []
        self.ueberschriften = []
        self.anzahl = {name: 0 for name in _GEZAEHLT}

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.im_body = True
            return
        if not self.im_body:
            return
        if tag in _STUMM:
            self._stumm_tiefe += 1
            return
        if self._stumm_tiefe:
            return

        self.tags.append(tag)
        if tag in self.anzahl:
            self.anzahl[tag] += 1

        werte = dict(attrs)
        if werte.get('id'):
            self.kennungen.append(werte['id'])
        if werte.get('class'):
            self.klassen.append(' '.join(werte['class'].split()))
        if tag in _UEBERSCHRIFTEN:
            self._ueberschrift = [tag, '']

    def handle_endtag(self, tag):
        if tag == 'body':
            self.im_body = False
            return
        if tag in _STUMM and self._stumm_tiefe:
            self._stumm_tiefe -= 1
            return
        if self._ueberschrift and tag == self._ueberschrift[0]:
            ebene, text = self._ueberschrift
            self.ueberschriften.append(f'{ebene}: {" ".join(text.split())}')
            self._ueberschrift = None

    def handle_data(self, daten):
        if self._ueberschrift and not self._stumm_tiefe:
            self._ueberschrift[1] += daten


def fingerabdruck(html):
    """Gibt den Fingerabdruck eines ausgelieferten Dokuments zurück."""
    sammler = _Sammler()
    sammler.feed(html)
    return {
        'tags': sammler.tags,
        'kennungen': sammler.kennungen,
        'klassen': sammler.klassen,
        'ueberschriften': sammler.ueberschriften,
        'anzahl': sammler.anzahl,
    }


def unterschiede(referenz, aktuell):
    """Beschreibt die Abweichungen zweier Fingerabdrücke in Klartext."""
    meldungen = []
    for name in ('tags', 'kennungen', 'klassen', 'ueberschriften'):
        alt, neu = referenz.get(name, []), aktuell.get(name, [])
        if alt == neu:
            continue
        if len(alt) != len(neu):
            meldungen.append(f'{name}: {len(alt)} vorher, {len(neu)} jetzt')
        for stelle, (a, n) in enumerate(zip(alt, neu)):
            if a != n:
                meldungen.append(f'{name}[{stelle}]: "{a}" -> "{n}"')
                break
    for element, zahl in referenz.get('anzahl', {}).items():
        jetzt = aktuell.get('anzahl', {}).get(element, 0)
        if zahl != jetzt:
            meldungen.append(f'Anzahl <{element}>: {zahl} vorher, {jetzt} jetzt')
    return meldungen
