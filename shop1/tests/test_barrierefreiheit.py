"""Bedienbarkeit ohne Maus und ohne Augenlicht.

Geprüft wird das ausgelieferte Dokument, nicht das Template – so fallen auch
Fehler auf, die erst durch eine Bedingung im Template entstehen.
"""

import re
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User

from ..models import Cart, CartItem, Comment, Order, Werbung
from ._basis import (ADMIN_SEITEN, INHALTSSEITEN, OEFFENTLICHE_SEITEN,
                     LuviqTestCase, erzeuge_benutzer, erzeuge_produkt)

STYLE_DATEI = Path(settings.BASE_DIR) / 'shop1' / 'static' / 'shop1' / 'style.css'
TAILWIND_DATEI = STYLE_DATEI.with_name('tailwind.css')

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
        self._nav_tiefe = 0       # > 0, solange wir in einem <nav> stehen
        self._label_tiefe = 0     # > 0, solange wir in einem <label> stehen

    def handle_starttag(self, tag, attrs):
        werte = dict(attrs)
        if tag == 'nav':
            self._nav_tiefe += 1
        if tag == 'img':
            werte['_in_nav'] = self._nav_tiefe > 0
            self.bilder.append(werte)
        elif tag in _FELDER:
            # Ein Feld *in* einem <label> ist implizit beschriftet – so stehen
            # die Zahlungsarten im Checkout und der Aktiv-Schalter der Werbung.
            werte['_in_label'] = self._label_tiefe > 0
            self.felder.append((tag, werte))
        elif tag == 'label':
            self._label_tiefe += 1
            if werte.get('for'):
                self.label_fuer.add(werte['for'])
        elif tag in ('a', 'button'):
            if self._element:
                self.bedienelemente.append(self._element)
            self._element = {'tag': tag, 'attrs': werte, 'text': ''}
        elif self._element and tag == 'img':
            self._element['text'] += werte.get('alt', '')

    def handle_endtag(self, tag):
        if tag == 'nav' and self._nav_tiefe:
            self._nav_tiefe -= 1
        if tag == 'label' and self._label_tiefe:
            self._label_tiefe -= 1
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


def _name_von(element):
    """Der Name, den ein Bildschirmleser für ein a/button ansagen würde.

    Ein Text nur aus Symbolen („👁️", „🗑️", „→") zählt nicht: Vorleseprogramme
    sagen dafür bestenfalls 'Auge' oder 'Papierkorb' an, nicht die Handlung.
    """
    werte = element['attrs']
    text = element['text'].strip()
    if not re.search(r'\w', text):
        text = ''
    return (text
            or werte.get('aria-label', '').strip()
            or werte.get('aria-labelledby', '').strip()
            or werte.get('title', '').strip())


def _ist_beschriftet(tag, werte, label_fuer):
    """Ob ein Feld einen zugänglichen Namen hat – oder keinen braucht."""
    if werte.get('type', 'text').lower() in _OHNE_BESCHRIFTUNG:
        return True
    return bool(
        werte.get('_in_label')
        or werte.get('aria-label', '').strip()
        or werte.get('aria-labelledby', '').strip()
        or (werte.get('id') and werte['id'] in label_fuer)
    )


# ── Spezifität von CSS-Selektoren ───────────────────────────────────────────
# Nur so viel, wie der Fokus-Test braucht: Kennungen, Klassen/Attribute/
# Pseudoklassen, Elemente. ``:is()``/``:not()``/``:has()`` zählen ihr
# stärkstes Argument, ``:where()`` zählt nichts – genau wie im Browser.

_ESCAPES = re.compile(r'\\.')
_KOMMENTARE = re.compile(r'/\*.*?\*/', re.S)
_FUNKTIONEN = re.compile(r':(is|not|has|matches|where)\(')


def _teile_oben(text):
    """Trennt an Kommas, die nicht in Klammern stehen."""
    teile, tiefe, start = [], 0, 0
    for stelle, zeichen in enumerate(text):
        if zeichen == '(':
            tiefe += 1
        elif zeichen == ')':
            tiefe -= 1
        elif zeichen == ',' and tiefe == 0:
            teile.append(text[start:stelle])
            start = stelle + 1
    teile.append(text[start:])
    return [teil.strip() for teil in teile if teil.strip()]


def _spezifitaet(selektor):
    """Spezifität eines einzelnen Selektors als Tripel (ids, klassen, elemente)."""
    selektor = _ESCAPES.sub('x', selektor)   # ``\:`` ist ein gewöhnliches Zeichen
    ids = klassen = elemente = 0
    stelle = 0
    while stelle < len(selektor):
        rest = selektor[stelle:]
        funktion = _FUNKTIONEN.match(rest)
        if funktion:
            tiefe, ende = 1, stelle + funktion.end()
            while tiefe:
                tiefe += {'(': 1, ')': -1}.get(selektor[ende], 0)
                ende += 1
            if funktion.group(1) != 'where':
                innen = selektor[stelle + funktion.end():ende - 1]
                staerkstes = max(_spezifitaet(teil) for teil in _teile_oben(innen))
                ids, klassen, elemente = (ids + staerkstes[0],
                                          klassen + staerkstes[1],
                                          elemente + staerkstes[2])
            stelle = ende
            continue
        for muster, gewicht in ((r'#[\w-]+', 'id'),
                                (r'\.[\w-]+', 'klasse'),
                                (r'\[[^\]]*\]', 'klasse'),
                                (r'::[\w-]+', 'element'),
                                (r':[\w-]+(\([^)]*\))?', 'klasse'),
                                (r'[a-zA-Z][\w-]*', 'element')):
            treffer = re.match(muster, rest)
            if treffer:
                ids += gewicht == 'id'
                klassen += gewicht == 'klasse'
                elemente += gewicht == 'element'
                stelle += treffer.end()
                break
        else:
            stelle += 1    # Kombinator, Leerzeichen, ``*``
    return (ids, klassen, elemente)


def _schwaechste_spezifitaet(selektorliste):
    """Bei ``a, b, c { … }`` zählt für 'gewinnt immer' das schwächste Glied."""
    return min(_spezifitaet(teil) for teil in _teile_oben(selektorliste))


def _regeln_mit(css, deklaration):
    """Alle Selektorlisten, deren Block ``deklaration`` enthält."""
    css = _KOMMENTARE.sub('', css)
    return [
        selektor.strip()
        for selektor, block in re.findall(r'([^{}]+)\{([^{}]*)\}', css)
        if re.search(deklaration, block)
    ]


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

    #: Alternativtexte, die nur den Zweck der Datei nennen, nicht ihren Inhalt.
    _NUR_ZWECK = re.compile(
        r'^(luviq(\s+universe)?[\s:–-]*)?(logo|icon|bild|grafik|image|symbol|brand|marke)'
        r'([\s:–-]*(von\s+)?luviq(\s+universe)?)?[.!]?$',
        re.IGNORECASE,
    )

    def test_der_logo_alternativtext_beschreibt_das_bild(self):
        """Verhindert 'Luviq Universe Logo' als Ersatztext des Logos in der
        Navigation. Das nennt den Dateizweck, nicht das Bild – wer es nicht
        sieht, erfährt nicht, dass dort der Schriftzug mit dem Leitspruch
        steht. Weil das Logo in ``base.html`` liegt, trifft der Fehler jede
        Seite."""
        for pfad in INHALTSSEITEN:
            logos = [
                bild for bild in _erhebe(self.hole(pfad).content.decode()).bilder
                if bild['_in_nav'] and 'logo' in bild.get('src', '').lower()
            ]
            with self.subTest(pfad=pfad):
                self.assertTrue(logos, f'{pfad}: kein Logo in der Navigation gefunden')
                for logo in logos:
                    text = logo.get('alt', '').strip()
                    self.assertTrue(text, f'{pfad}: Logo in der Navigation ohne Alternativtext')
                    self.assertIsNone(
                        self._NUR_ZWECK.match(text),
                        f'{pfad}: alt="{text}" nennt nur den Dateizweck, nicht den Inhalt',
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
                with self.subTest(pfad=pfad, feld=werte.get('name', tag)):
                    self.assertTrue(
                        _ist_beschriftet(tag, werte, erhebung.label_fuer),
                        f'{pfad}: <{tag} name="{werte.get("name", "")}"> ohne '
                        f'Beschriftung (weder aria-label noch <label for>)',
                    )


class AngemeldeteBedienungTest(LuviqTestCase):
    """Was erst nach der Anmeldung erscheint, muss genauso bedienbar sein.

    Der Test darüber ruft die Seiten anonym ab und sieht darum weder das
    Kommentarfeld der Startseite noch das Antwortfeld im Gästebuch noch die
    Adressfelder im Checkout – genau die Felder, die lange ohne Namen waren.
    """

    def setUp(self):
        erzeuge_produkt('Bemalte Bomberjacke')
        self.kundin = erzeuge_benutzer('kundin')
        Comment.objects.create(user=self.kundin, text='Mein Unikat ist angekommen.')
        korb = Cart.objects.create(user=self.kundin)
        CartItem.objects.create(cart=korb, produkt_name='Bemalte Bomberjacke',
                                produkt_preis=Decimal('49.90'), menge=1)
        self.client.force_login(self.kundin)

    def test_jedes_eingabefeld_ist_auch_angemeldet_beschriftet(self):
        """Verhindert, dass ein Kommentar-, Antwort- oder Adressfeld nur mit
        einem Platzhalter erscheint. Solche Felder sieht nur, wer angemeldet
        ist – und ein Test ohne Anmeldung würde sie nie zu Gesicht bekommen.
        Gegenprobe: ein ``aria-label`` aus ``kontakt.html`` entfernen, der
        Test muss rot werden."""
        for pfad in INHALTSSEITEN + ['/checkout/']:
            antwort = self.hole(pfad)
            self.assertEqual(antwort.status_code, 200, f'{pfad} nicht erreichbar')
            erhebung = _erhebe(antwort.content.decode())
            self.assertTrue(erhebung.felder or pfad not in ('/', '/kontakt/', '/gaestebuch/', '/checkout/'),
                            f'{pfad}: kein einziges Formularfeld gefunden – der Test läuft ins Leere')
            for tag, werte in erhebung.felder:
                with self.subTest(pfad=pfad, feld=werte.get('name', tag)):
                    self.assertTrue(
                        _ist_beschriftet(tag, werte, erhebung.label_fuer),
                        f'{pfad}: <{tag} name="{werte.get("name", "")}"> ohne '
                        f'zugänglichen Namen (weder aria-label noch <label for>)',
                    )


class AdminPanelBedienungTest(LuviqTestCase):
    """Das Admin-Panel bedient die Betreiberin täglich – auch dort darf keine
    Schaltfläche namenlos sein und kein Feld ohne Beschriftung stehen."""

    def setUp(self):
        self.produkt = erzeuge_produkt('Bemalte Bomberjacke')
        self.besitzerin = User.objects.create_superuser(
            'shopbesitzer', 'shop@example.invalid', 'ein-langes-testpasswort'
        )
        Order.objects.create(
            user=self.besitzerin, vorname='Erika', nachname='Musterfrau',
            email='erika@example.invalid', adresse='Grünberger Str. 16',
            stadt='Alsfeld', postleitzahl='36304', land='Deutschland',
            gesamt_betrag=Decimal('49.90'),
        )
        Werbung.objects.create(
            titel='Testkampagne', link='https://www.luviq-alsfeld.com/',
            bild='https://example.invalid/werbung.jpg', budget=Decimal('20.00'),
        )
        self.client.force_login(self.besitzerin)
        self.seiten = ADMIN_SEITEN + [
            '/shop-admin/users/create/',
            f'/shop-admin/users/{self.besitzerin.id}/edit/',
        ]

    def test_jedes_bedienelement_im_admin_panel_hat_einen_namen(self):
        """Verhindert die Symbol-Links „👁️" und „🗑️" in Bestell- und
        Statistikliste, die ein Bildschirmleser nur als 'Link' ansagt – wer
        nicht sieht, weiss dann nicht, ob er gerade eine Bestellung öffnet
        oder löscht."""
        for pfad in self.seiten:
            antwort = self.hole(pfad)
            self.assertEqual(antwort.status_code, 200, f'{pfad} nicht erreichbar')
            erhebung = _erhebe(antwort.content.decode())
            self.assertTrue(erhebung.bedienelemente, f'{pfad}: keine Bedienelemente gefunden')
            for element in erhebung.bedienelemente:
                werte = element['attrs']
                if werte.get('aria-hidden') == 'true':
                    continue
                with self.subTest(pfad=pfad, element=element['tag'],
                                  klasse=werte.get('class', '')[:40]):
                    self.assertTrue(
                        _name_von(element),
                        f'{pfad}: <{element["tag"]}> ohne erkennbaren Namen '
                        f'(class="{werte.get("class", "")[:60]}")',
                    )

    def test_jedes_eingabefeld_im_admin_panel_ist_beschriftet(self):
        """Verhindert die Filter-, Sammelaktions- und Kampagnenfelder, die nur
        über ihre Nachbarschaft zu erraten waren. Die Django-Formulare für
        Benutzer bekommen ihre Beschriftung über ``<label for>`` auf die von
        Django vergebene Kennung, alle anderen Felder über ``aria-label``."""
        for pfad in self.seiten:
            antwort = self.hole(pfad)
            self.assertEqual(antwort.status_code, 200, f'{pfad} nicht erreichbar')
            erhebung = _erhebe(antwort.content.decode())
            for tag, werte in erhebung.felder:
                with self.subTest(pfad=pfad, feld=werte.get('name', tag)):
                    self.assertTrue(
                        _ist_beschriftet(tag, werte, erhebung.label_fuer),
                        f'{pfad}: <{tag} name="{werte.get("name", "")}"> ohne '
                        f'zugänglichen Namen',
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

    def test_die_fokusregel_setzt_sich_gegen_outline_none_durch(self):
        """Verhindert einen Fokusring, der zwar im Stylesheet steht, aber nie
        zu sehen ist: ``.form-input:focus`` in ``style.css`` und die
        Tailwind-Klasse ``focus:outline-none`` löschen den Outline mit der
        Spezifität 0,2,0. Ein Fokus-Selektor wie ``input:focus-visible``
        (0,1,1) verliert dagegen, egal wie spät er geladen wird. Die Regel muss
        deshalb auf jedem ihrer Selektoren stärker sein als beide Gegner –
        sonst dreht der nächste Tailwind-Build die Sichtbarkeit still zurück."""
        style = STYLE_DATEI.read_text(encoding='utf-8')
        fokusregeln = [
            selektor for selektor in _regeln_mit(style, r'outline:\s*3px solid')
            if ':focus-visible' in selektor
        ]
        self.assertTrue(fokusregeln, 'Keine :focus-visible-Regel mit 3px-Outline in style.css')
        fokus = min(_schwaechste_spezifitaet(selektor) for selektor in fokusregeln)

        gegner = {
            '.form-input:focus (style.css)': [
                s for s in _regeln_mit(style, r'outline:\s*none') if '.form-input:focus' in s
            ],
        }
        if TAILWIND_DATEI.exists():
            tailwind = TAILWIND_DATEI.read_text(encoding='utf-8')
            gegner['focus:outline-none (tailwind.css)'] = [
                s for s in _regeln_mit(tailwind, r'outline:\s*2px solid transparent')
                if 'outline-none:focus' in s
            ]
        # Beide Gegner haben heute 0,2,0. Sollte einer verschwinden, bleibt die
        # Latte trotzdem liegen – sonst reicht irgendwann wieder 0,1,1.
        latte = (0, 2, 0)
        for name, selektoren in gegner.items():
            for selektor in selektoren:
                latte = max(latte, _spezifitaet(selektor))
                with self.subTest(gegner=name, selektor=selektor):
                    self.assertGreater(
                        fokus, _spezifitaet(selektor),
                        f'Die Fokusregel ({fokus}) verliert gegen {selektor} '
                        f'({_spezifitaet(selektor)}) – der Ring bleibt unsichtbar',
                    )
        self.assertGreater(
            fokus, latte,
            f'Die Fokusregel hat Spezifität {fokus}, muss aber über {latte} liegen',
        )
