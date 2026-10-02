"""Volltext der öffentlichen Seiten für ``/llms-full.txt`` (GE31, VL08).

``llms.txt`` ist die Kurzfassung; ``llms-full.txt`` liefert zusätzlich den
Text der Seiten selbst – ein Abruf statt zehn. Damit dort nichts steht, was die
Seite nicht auch sagt, wird der Text **nicht** noch einmal getippt: die Views
der Seiten werden aufgerufen und aus ihrem ``<main>`` wird der Text gelesen.
Was eine Seite ändert, ändert sich hier von selbst, ohne zweite Pflegestelle.

Aufgenommen werden nur Seiten, die auch in der Sitemap stehen dürfen (kein
``noindex``): Übersicht, Über-uns, Herkunft, Motivanfrage, die aktiven
Stücke und die freigegebenen Wissensbeiträge. Die Startseite zählt Werbe-
Impressionen mit und fehlt deshalb bewusst; ihr Kernsatz steht in
``llms.txt`` und im Abschnitt über Luisa.
"""

import logging
from html.parser import HTMLParser

_log = logging.getLogger('shop1')

#: Elemente, deren Inhalt nie Text der Seite ist.
_UEBERSPRINGEN = {'script', 'style', 'svg', 'noscript', 'template', 'iframe',
                  'form', 'button', 'select', 'textarea', 'input', 'nav'}
_UEBERSCHRIFTEN = {'h1': '####', 'h2': '####', 'h3': '#####', 'h4': '#####'}
_BLOCK = {'p', 'div', 'section', 'article', 'li', 'ul', 'ol', 'dl', 'dt', 'dd',
          'blockquote', 'figure', 'figcaption', 'header', 'footer', 'aside',
          'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
_LEER = {'br', 'img', 'input', 'meta', 'link', 'hr', 'source', 'wbr'}
#: Zeilenelemente, die in der Seite wie getrennte Stücke stehen („Nº 001“ neben
#: „vergeben“, Fettdruck neben dem Satz dahinter): dazwischen gehört ein Leerzeichen.
_ABSTAND = {'span', 'b', 'small', 'time', 'label'}


class _MainText(HTMLParser):
    """Liest den Text aus ``<main>`` als Zeilen; Überschriften und Listen
    behalten ihre Auszeichnung."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._in_main = 0
        self._skip = []          # Stapel der gerade übersprungenen Elemente
        self._stack = []         # alle offenen Elemente (nur Namen)
        self._zeilen = []
        self._aktuell = []
        self._prefix = ''

    # -- Hilfen ------------------------------------------------------------
    def _zeile_abschliessen(self):
        text = ' '.join(''.join(self._aktuell).split())
        if text:
            self._zeilen.append(f'{self._prefix}{text}')
        self._aktuell = []
        self._prefix = ''

    # -- HTMLParser --------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'main':
            self._in_main += 1
        if tag not in _LEER:
            self._stack.append(tag)
        if not self._in_main:
            return
        versteckt = a.get('aria-hidden') == 'true' or 'hidden' in a
        if tag in _UEBERSPRINGEN or versteckt:
            if tag not in _LEER:
                self._skip.append(len(self._stack))
            return
        if self._skip:
            return
        if tag in _ABSTAND:
            self._aktuell.append(' ')
        if tag in _BLOCK:
            self._zeile_abschliessen()
        if tag in _UEBERSCHRIFTEN:
            self._prefix = _UEBERSCHRIFTEN[tag] + ' '
        elif tag == 'li':
            self._prefix = '- '

    def handle_endtag(self, tag):
        if tag in _LEER:
            return
        if self._stack and tag in self._stack:
            while self._stack:
                oben = self._stack.pop()
                if self._skip and self._skip[-1] > len(self._stack):
                    self._skip.pop()
                if oben == tag:
                    break
        if tag == 'main' and self._in_main:
            self._zeile_abschliessen()
            self._in_main -= 1
            return
        if self._in_main and not self._skip and tag in _ABSTAND:
            self._aktuell.append(' ')
        if self._in_main and not self._skip and tag in _BLOCK:
            self._zeile_abschliessen()

    def handle_data(self, data):
        if self._in_main and not self._skip:
            self._aktuell.append(data)

    def zeilen(self):
        self._zeile_abschliessen()
        return list(self._zeilen)


def haupttext(html):
    """Text aus ``<main>`` einer HTML-Seite, eine Zeile je Absatz.

    Überschriften beginnen mit ``####``, Listenpunkte mit ``- ``. Formulare,
    Schaltflächen, Navigation, Skripte und ``aria-hidden``-Teile fehlen."""
    parser = _MainText()
    parser.feed(html)
    zeilen = parser.zeilen()
    sauber = []
    for zeile in zeilen:
        if sauber and zeile == sauber[-1]:
            continue
        sauber.append(zeile)
    return sauber


def seite_als_text(antwort):
    """``haupttext`` einer Antwort – leer, wenn sie kein 200 mit HTML ist."""
    if getattr(antwort, 'status_code', None) != 200:
        return []
    if 'text/html' not in antwort.get('Content-Type', ''):
        return []
    try:
        return haupttext(antwort.content.decode('utf-8'))
    except Exception:                      # pragma: no cover - nie die Datei kippen
        _log.exception('llms-full: Seitentext nicht lesbar')
        return []
