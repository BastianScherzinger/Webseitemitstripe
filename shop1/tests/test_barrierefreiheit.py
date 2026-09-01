"""Bedienbarkeit ohne Maus und ohne Augenlicht.

Geprüft wird das ausgelieferte Dokument, nicht das Template – so fallen auch
Fehler auf, die erst durch eine Bedingung im Template entstehen.
"""

from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings

from ._basis import OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_produkt

STYLE_DATEI = Path(settings.BASE_DIR) / 'shop1' / 'static' / 'shop1' / 'style.css'

_FELDER = {'input', 'textarea', 'select'}

#: Eingabearten, die keine eigene Beschriftung brauchen.
_OHNE_BESCHRIFTUNG = {'hidden', 'submit', 'button', 'reset', 'image'}


class _Erheber(HTMLParser):
    """Sammelt Bilder, Bedienelemente und Beschriftungen einer Seite."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bilder = []
        self.felder = []
        self.label_fuer = set()
        self._element = None      # offenes a/button samt gesammeltem Text
        self.bedienelemente = []

    def handle_starttag(self, tag, attrs):
        werte = dict(attrs)
        if tag == 'img':
            self.bilder.append(werte)
        elif tag in _FELDER:
            self.felder.append((tag, werte))
        elif tag == 'label' and werte.get('for'):
            self.label_fuer.add(werte['for'])
        elif tag in ('a', 'button'):
            if self._element:
                self.bedienelemente.append(self._element)
            self._element = {'tag': tag, 'attrs': werte, 'text': ''}
        elif self._element and tag == 'img':
            self._element['text'] += werte.get('alt', '')

    def handle_endtag(self, tag):
        if self._element and tag == self._element['tag']:
            self.bedienelemente.append(self._element)
            self._element = None

    def handle_data(self, daten):
        if self._element:
            self._element['text'] += daten

    def close(self):
        super().close()
        if self._element:
            self.bedienelemente.append(self._element)
            self._element = None


def _erhebe(html):
    erheber = _Erheber()
    erheber.feed(html)
    erheber.close()
    return erheber


class AlternativtexteTest(LuviqTestCase):
    """Jedes Bild sagt, was darauf zu sehen ist – oder gilt als Schmuck."""

    def setUp(self):
        erzeuge_produkt('Bemalte Bomberjacke')

    def test_jedes_bild_hat_ein_alt_attribut(self):
        """Verhindert, dass ein Bildschirmleser die Bildadresse vorliest.
        Fehlt ``alt`` ganz, liest er den Dateinamen; ``alt=""`` sagt dagegen
        ausdrücklich 'nur Schmuck' und wird übersprungen."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                for bild in _erhebe(self.hole(pfad).content.decode()).bilder:
                    self.assertIn(
                        'alt', bild,
                        f'{pfad}: <img src="{bild.get("src", "?")}"> ohne alt',
                    )

    def test_kein_alternativtext_ist_ein_dateiname(self):
        """Verhindert den häufigsten Ersatztext überhaupt: den Dateinamen.
        'logo-luviq.jpeg' beschreibt nichts."""
        for pfad in OEFFENTLICHE_SEITEN:
            with self.subTest(pfad=pfad):
                for bild in _erhebe(self.hole(pfad).content.decode()).bilder:
                    text = bild.get('alt', '').strip().lower()
                    self.assertFalse(
                        text.endswith(('.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif')),
                        f'{pfad}: alt="{bild.get("alt")}" ist ein Dateiname',
                    )


class BedienelementeTest(LuviqTestCase):
    """Jede Schaltfläche und jeder Link hat einen sprechbaren Namen."""

    def setUp(self):
        erzeuge_produkt('Bemalte Bomberjacke')

    def test_jedes_bedienelement_hat_einen_namen(self):
        """Verhindert Schaltflächen, die ein Bildschirmleser nur als 'Schalter'
        ansagt. Betrifft alle Elemente, die nur ein Symbol enthalten – Menü,
        Warenkorb, Löschen, Aktualisieren."""
        for pfad in OEFFENTLICHE_SEITEN:
            antwort = self.hole(pfad).content.decode()
            for element in _erhebe(antwort).bedienelemente:
                werte = element['attrs']
                name = (element['text'].strip()
                        or werte.get('aria-label', '').strip()
                        or werte.get('aria-labelledby', '').strip()
                        or werte.get('title', '').strip())
                if werte.get('aria-hidden') == 'true':
                    continue
                with self.subTest(pfad=pfad, element=element['tag'],
                                  klasse=werte.get('class', '')[:40]):
                    self.assertTrue(
                        name,
                        f'{pfad}: <{element["tag"]}> ohne erkennbaren Namen '
                        f'(class="{werte.get("class", "")[:60]}")',
                    )

    def test_jedes_eingabefeld_ist_beschriftet(self):
        """Verhindert Felder, bei denen nur ein Platzhaltertext steht: der
        verschwindet beim Tippen und wird von Bildschirmlesern nicht
        zuverlässig als Beschriftung gewertet."""
        for pfad in OEFFENTLICHE_SEITEN:
            erhebung = _erhebe(self.hole(pfad).content.decode())
            for tag, werte in erhebung.felder:
                if werte.get('type', 'text').lower() in _OHNE_BESCHRIFTUNG:
                    continue
                beschriftet = (
                    werte.get('aria-label', '').strip()
                    or werte.get('aria-labelledby', '').strip()
                    or (werte.get('id') and werte['id'] in erhebung.label_fuer)
                )
                with self.subTest(pfad=pfad, feld=werte.get('name', tag)):
                    self.assertTrue(
                        beschriftet,
                        f'{pfad}: <{tag} name="{werte.get("name", "")}"> ohne '
                        f'Beschriftung (weder aria-label noch <label for>)',
                    )


class DarstellungTest(LuviqTestCase):
    """Zwei Regeln, die nur im Stylesheet stehen können."""

    def test_bewegungsreduzierung_wird_beachtet(self):
        """Verhindert, dass die Seite trotz der Systemeinstellung 'Bewegung
        reduzieren' weiter animiert – für Menschen mit vestibulären Störungen
        löst das Übelkeit und Schwindel aus."""
        css = STYLE_DATEI.read_text(encoding='utf-8')
        self.assertIn('prefers-reduced-motion: reduce', css)
        self.assertIn('animation-duration: 0.01ms !important', css)

    def test_der_tastaturfokus_ist_sichtbar(self):
        """Verhindert, dass beim Bedienen mit der Tabulatortaste unsichtbar
        bleibt, wo man gerade steht – ohne Maus ist die Seite dann unbenutzbar."""
        css = STYLE_DATEI.read_text(encoding='utf-8')
        self.assertIn(':focus-visible', css)
        self.assertIn('outline: 3px solid', css)
