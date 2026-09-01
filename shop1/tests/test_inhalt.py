"""Inhalt: stimmt, was auf der Seite steht – und stimmt es überall gleich?

Widersprüchliche Angaben zu Anschrift, E-Mail oder Zahlungsarten sind für die
lokale Auffindbarkeit einer der schädlichsten Zustände überhaupt: Google
gleicht diese Angaben quer über Seite, Schema und Verzeichnisse ab.

Der zweite Teil dieses Moduls misst den **Umfang** des Inhalts. Bis Welle 5
waren alle Wortzahlen des Laufs Schätzungen aus den Vorlagen
(``01-BEFUND.md`` Abschnitt 7); :func:`inhaltstext` und :func:`wortzahl`
messen am ausgelieferten HTML, und ``MINDESTWOERTER`` hält den erreichten
Stand fest, damit er nicht still wieder abschmilzt.
"""

import re
from html.parser import HTMLParser

from ._basis import INHALTSSEITEN, OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_produkt
from .test_geo import sichtbarer_text


class _Inhaltsleser(HTMLParser):
    """Zieht den sichtbaren Text aus dem ``<main>`` eines Dokuments.

    Navigation, Fusszeile und Cookie-Hinweis stehen in ``base.html`` ausserhalb
    von ``<main>`` und wären auf jeder Seite dieselben ~80 Wörter – wer sie
    mitzählt, misst nicht den Inhalt der Seite, sondern das Gerüst.
    """

    _STUMM = ('script', 'style', 'noscript', 'template')

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._im_main = False
        self._stumm = 0
        self.stuecke = []

    def handle_starttag(self, tag, attrs):
        if tag == 'main':
            self._im_main = True
        elif tag in self._STUMM:
            self._stumm += 1

    def handle_endtag(self, tag):
        if tag == 'main':
            self._im_main = False
        elif tag in self._STUMM and self._stumm:
            self._stumm -= 1

    def handle_data(self, daten):
        if self._im_main and not self._stumm:
            self.stuecke.append(daten)


def inhaltstext(html):
    """Sichtbarer Text des Inhaltsbereichs, Leerraum auf ein Zeichen gekürzt."""
    leser = _Inhaltsleser()
    leser.feed(html)
    return ' '.join(' '.join(leser.stuecke).split())


def wortzahl(text):
    """Zählt Wörter: durch Leerraum getrennte Stücke mit mindestens einem
    Buchstaben oder einer Ziffer. Trennstriche, Punkte und Sterne
    („·", „—", „★★★★★") zählen nicht; „1-2" und „§" zählen als ein Wort."""
    return len([stueck for stueck in text.split() if re.search(r'\w', stueck)])


#: Produkt, das die Umfangstests anlegen. Name und Beschreibung sind fest,
#: weil beide in die Wortzahl der Produktseite und der Übersichten eingehen.
UMFANG_PRODUKT = 'Bemalte Bomberjacke'
UMFANG_PRODUKT_SEITE = '/produkt/bemalte-bomberjacke/'

#: Mindestwortzahl je Seite im Inhaltsbereich – **kein** Ziel, sondern der
#: nach Welle 5 (2026-09-01) tatsächlich gemessene Stand, jeweils um einige
#: Wörter unterschritten, damit eine Umformulierung nicht anschlägt, ein
#: gestrichener Absatz aber schon. Gemessen mit genau einem Produkt im
#: Bestand, ohne Kommentare, ohne Anmeldung: ``/`` 399, ``/produkte/`` 111,
#: ``/kontakt/`` 135, ``/ueber_uns/`` 362, ``/liefergebiet/`` 247,
#: ``/gaestebuch/`` 99, ``/impressum/`` 75, ``/datenschutz/`` 371,
#: ``/agb/`` 177, Produktseite 103. Die Zielgrössen des Prüfstands (700 für
#: die Startseite, 600 für ``/produkte/``) sind damit ausdrücklich **nicht**
#: erreicht; wer sie erreicht, zieht die Schwellen nach.
MINDESTWOERTER = {
    '/': 390,
    '/produkte/': 105,
    '/kontakt/': 130,
    '/ueber_uns/': 350,
    '/liefergebiet/': 240,
    '/gaestebuch/': 95,
    '/impressum/': 70,
    '/datenschutz/': 360,
    '/agb/': 170,
    UMFANG_PRODUKT_SEITE: 95,
}

#: Seiten, deren erstes Drittel noch keine Zahl nennt. ``/liefergebiet/``
#: nennt seine Lieferzeiten erst in der FAQ am Seitenende (Befund 4.14); die
#: Vorlage gehörte nicht zu den Dateien, die Welle 5 ändern durfte. Wer den
#: ersten Absatz dort um die Versandangabe ergänzt, streicht die Ausnahme.
OHNE_ZAHL_IM_ERSTEN_DRITTEL = {'/liefergebiet/'}

#: Belegt im Impressum (impressum.html) und im seitenweiten JSON-LD.
ANSCHRIFT = ['Grünberger Str. 16', '36304', 'Alsfeld']
EMAIL = 'brehlerluisa@gmail.com'

#: Muster, die im sichtbaren Text auf Platzhalter oder Blindtext hindeuten.
#: Geprüft wird bewusst nur der sichtbare Text: ``forms.py`` benutzt
#: „z.B. Musterstraße 123" als Beispiel in einem Eingabefeld – das ist eine
#: Ausfüllhilfe und keine Behauptung über das Unternehmen.
PLATZHALTER = [
    'Musterstraße 123<', 'Mustermann', 'Musterfrau',
    '12345 Berlin', '+49 (0) 30 123456', 'info@luviq.universe',
    'lorem ipsum', 'Lorem ipsum', 'TODO', 'FIXME',
]

#: Adressen, die in keinem ``href`` mehr auftauchen dürfen.
FALSCHE_ZIELE = ['luviq.de', 'info@luviq.universe', 'tel:+4930123456',
                 'example.com']


class _ErsterAbsatz(HTMLParser):
    """Findet den ersten Absatz nach der ``h1``."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._nach_h1 = False
        self._sammelt = False
        self.text = None

    def handle_starttag(self, tag, attrs):
        if tag == 'p' and self._nach_h1 and self.text is None:
            self._sammelt = True
            self.text = ''

    def handle_endtag(self, tag):
        if tag == 'h1':
            self._nach_h1 = True
        elif tag == 'p' and self._sammelt:
            self._sammelt = False

    def handle_data(self, daten):
        if self._sammelt:
            self.text += daten


def erster_absatz(html):
    leser = _ErsterAbsatz()
    leser.feed(html)
    return ' '.join((leser.text or '').split())


class PlatzhalterTest(LuviqTestCase):
    """Nichts Erfundenes und nichts Halbfertiges im Auslieferzustand."""

    def setUp(self):
        erzeuge_produkt('Bemalte Bomberjacke')

    def test_keine_seite_zeigt_platzhalterdaten(self):
        """Verhindert den Zustand, den dieser Lauf vorgefunden hat: die
        Kontaktseite nannte live eine Musteranschrift in Berlin, eine erfundene
        Telefonnummer und eine E-Mail-Adresse, die es nicht gibt – während
        Impressum und Schema Alsfeld nannten."""
        for pfad in OEFFENTLICHE_SEITEN:
            inhalt = self.hole(pfad).content.decode()
            for muster in PLATZHALTER:
                with self.subTest(pfad=pfad, muster=muster):
                    self.assertNotIn(muster, inhalt, f'{pfad} enthält "{muster}"')

    def test_kein_verweis_zeigt_auf_eine_erfundene_adresse(self):
        """Verhindert Verweise, die ins Leere gehen: das Impressum nannte
        ``www.luviq.de`` als Website, die Kontaktseite eine erfundene
        Telefonnummer und die Adresse ``info@luviq.universe``."""
        for pfad in OEFFENTLICHE_SEITEN:
            ziele = re.findall(r'href="([^"]*)"', self.hole(pfad).content.decode())
            for ziel in ziele:
                for falsch in FALSCHE_ZIELE:
                    with self.subTest(pfad=pfad, ziel=ziel[:50]):
                        self.assertNotIn(falsch, ziel)

    def test_auch_die_kurzfassung_zeigt_keine_platzhalterdaten(self):
        """Gegenprobe für llms.txt – Antwortmaschinen zitieren daraus wörtlich."""
        inhalt = self.hole('/llms.txt').content.decode()
        for muster in PLATZHALTER + FALSCHE_ZIELE:
            with self.subTest(muster=muster):
                self.assertNotIn(muster, inhalt)


class AngabenTest(LuviqTestCase):
    """Anschrift, E-Mail und Zahlungsarten – überall dieselben."""

    def test_die_kontaktseite_nennt_dieselbe_anschrift_wie_das_impressum(self):
        """Verhindert zwei Anschriften auf einer Seite. Google gleicht Name,
        Anschrift und Telefonnummer über alle Quellen ab; weichen sie
        voneinander ab, sinkt die lokale Auffindbarkeit."""
        kontakt = sichtbarer_text(self.hole('/kontakt/').content.decode())
        impressum = sichtbarer_text(self.hole('/impressum/').content.decode())
        for teil in ANSCHRIFT:
            with self.subTest(teil=teil):
                self.assertIn(teil, kontakt)
                self.assertIn(teil, impressum)

    def test_die_kontaktseite_nennt_dieselbe_adresse_wie_das_impressum(self):
        """Verhindert eine zweite, nicht erreichbare E-Mail-Adresse."""
        for pfad in ('/kontakt/', '/impressum/', '/datenschutz/'):
            with self.subTest(pfad=pfad):
                self.assertIn(EMAIL, self.hole(pfad).content.decode())

    def test_die_zahlungsarten_stimmen_ueberall_ueberein(self):
        """Verhindert den Zustand, den dieser Lauf vorgefunden hat: die
        Kontaktseite versprach 'PayPal, Kreditkarte und Krypto-Transfers',
        die AGB nennen PayPal und Vorab-Überweisung. Krypto wird im Code
        nirgends verarbeitet."""
        kontakt = sichtbarer_text(self.hole('/kontakt/').content.decode())
        self.assertIn('PayPal oder Vorab-Überweisung', kontakt)
        for unbelegt in ('Kreditkarte', 'Krypto'):
            with self.subTest(begriff=unbelegt):
                self.assertNotIn(unbelegt, kontakt)

    def test_die_lieferzeit_stimmt_auf_beiden_seiten_ueberein(self):
        """Verhindert zwei verschiedene Lieferversprechen. Vorher sagte die
        Kontaktseite '2-3 Werktage', die Liefergebietsseite '1-2 Werktage
        Versand, 1-3 Werktage Zustellung'."""
        for pfad in ('/kontakt/', '/liefergebiet/'):
            with self.subTest(pfad=pfad):
                text = sichtbarer_text(self.hole(pfad).content.decode())
                self.assertIn('1-2 Werktagen versendet', text)
                self.assertIn('1-3 Werktagen', text)


class DatenschutzTest(LuviqTestCase):
    """Die Datenschutzerklärung muss nennen, was die Seite tatsächlich lädt."""

    def test_jeder_eingebundene_drittanbieter_ist_genannt(self):
        """Verhindert eine Datenschutzerklärung, die vier Abschnitte lang ist
        und keinen der Dienste nennt, an die beim Aufruf Daten fliessen.
        Besonders ip-api.com: dorthin geht die Besucher-IP im Klartext."""
        text = sichtbarer_text(self.hole('/datenschutz/').content.decode())
        for dienst in ('Cloudinary', 'jsDelivr', 'Google Fonts',
                       'Google Maps', 'ip-api.com', 'Brevo', 'PayPal', 'Railway'):
            with self.subTest(dienst=dienst):
                self.assertIn(dienst, text)

    def test_es_wird_kein_dienst_genannt_der_nicht_eingebunden_ist(self):
        """Gegenprobe: die Erklärung nannte 'Railway / Supabase' als Hoster.
        Supabase kommt im gesamten Projekt nicht vor."""
        text = sichtbarer_text(self.hole('/datenschutz/').content.decode())
        self.assertNotIn('Supabase', text)

    def test_das_besuchsprotokoll_ist_beschrieben(self):
        """Verhindert, dass die Seite bei jedem Aufruf IP-Adresse, Pfad und
        Browserkennung speichert, ohne dass es irgendwo steht."""
        text = sichtbarer_text(self.hole('/datenschutz/').content.decode())
        for begriff in ('IP-Adresse', 'DSGVO'):
            with self.subTest(begriff=begriff):
                self.assertIn(begriff, text)


class AntwortZuerstTest(LuviqTestCase):
    """Der erste Absatz jeder Seite soll für sich zitierbar sein."""

    def setUp(self):
        erzeuge_produkt('Bemalte Bomberjacke')

    def test_jede_inhaltsseite_beginnt_mit_einer_sachlichen_antwort(self):
        """Verhindert Werbezeilen als Einstieg. Antwortmaschinen zitieren den
        ersten Absatz; 'Wir antworten schneller als das Licht.' beantwortet
        keine Frage und nennt weder Anbieter noch Ort.

        Seit Welle 5 gilt das auch für das Impressum: seine Unterzeile nennt
        Anbieterin, Ort und Inhalt der Seite. AGB und Datenschutzerklärung
        bleiben ausgenommen – an Rechtstexten wird nicht formuliert (Plan,
        Schritt 24), und ihre Unterzeile ist eine Bereichsbezeichnung über
        dem vorgeschriebenen Aufbau."""
        rechtstexte = {'/datenschutz/', '/agb/'}
        for pfad in [p for p in INHALTSSEITEN if p not in rechtstexte]:
            with self.subTest(pfad=pfad):
                absatz = erster_absatz(self.hole(pfad).content.decode())
                self.assertGreaterEqual(
                    len(absatz), 90,
                    f'{pfad}: erster Absatz nur {len(absatz)} Zeichen: "{absatz}"',
                )
                self.assertTrue(
                    re.search(r'Luviq|Alsfeld|Luisa Brehler', absatz),
                    f'{pfad}: erster Absatz nennt weder Anbieter noch Ort: "{absatz}"',
                )


class UmfangTest(LuviqTestCase):
    """Gemessener Textumfang statt geschätzter – und kein Rückfall."""

    def setUp(self):
        erzeuge_produkt(UMFANG_PRODUKT)

    def test_die_messfunktion_zaehlt_nur_den_inhaltsbereich(self):
        """Gegenprobe an bekanntem Inhalt, bevor die Schwellen gelten.
        Verhindert, dass die Messung Navigation, Fusszeile oder Skripttext
        mitzählt und damit jede Seite um dieselben Gerüstwörter zu gross
        erscheint – dann würde ein gestrichener Absatz nicht mehr auffallen."""
        html = (
            '<html><head><title>Titel Titel</title>'
            '<script>var a = "kein Inhalt";</script></head><body>'
            '<nav>Home Produkte Kontakt</nav>'
            '<main><h1>Vier Wörter im Titel</h1>'
            '<p>Versand in 1-2 Werktagen · <strong>Alsfeld</strong> — ★★★★★</p>'
            '<script>document.write("auch kein Inhalt")</script>'
            '<style>.x { color: red }</style>'
            '</main><footer>Impressum Datenschutz AGB</footer></body></html>'
        )
        text = inhaltstext(html)
        self.assertEqual(
            text, 'Vier Wörter im Titel Versand in 1-2 Werktagen · Alsfeld — ★★★★★',
        )
        # 4 Wörter Überschrift + „Versand", „in", „1-2", „Werktagen", „Alsfeld";
        # „·", „—" und die Sterne sind keine Wörter.
        self.assertEqual(wortzahl(text), 9)
        self.assertEqual(wortzahl(''), 0)

    def test_keine_seite_faellt_unter_ihren_erreichten_umfang(self):
        """Verhindert den Rückfall: ein Absatz, der beim nächsten Umbau
        „aufgeräumt" wird, nimmt der Seite still ein Drittel ihres Inhalts.
        Vor Welle 5 hatte ``/produkte/`` 41 und jede Produktseite 23 Wörter
        – die Schwellen halten den seither erreichten Stand fest, nicht ein
        Ziel (siehe ``MINDESTWOERTER``)."""
        for pfad, mindestens in MINDESTWOERTER.items():
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                self.assertEqual(antwort.status_code, 200)
                woerter = wortzahl(inhaltstext(antwort.content.decode()))
                self.assertGreaterEqual(
                    woerter, mindestens,
                    f'{pfad} hat im Inhaltsbereich nur noch {woerter} Wörter '
                    f'(Stand nach Welle 5: mindestens {mindestens})',
                )

    def test_jede_inhaltsseite_ist_in_der_schwellenliste(self):
        """Verhindert, dass eine neue Inhaltsseite ungemessen bleibt: wer
        ``INHALTSSEITEN`` erweitert, muss ihren Stand auch festhalten."""
        for pfad in INHALTSSEITEN:
            with self.subTest(pfad=pfad):
                self.assertIn(pfad, MINDESTWOERTER)

    def test_jede_inhaltsseite_nennt_im_ersten_drittel_eine_zahl(self):
        """Verhindert den Zustand aus Befund 4.14: ``/`` und ``/ueber_uns/``
        nannten keine einzige Zahl, und wo Zahlen standen, standen sie am
        Seitenende in einer FAQ. Antwortmaschinen zitieren den Anfang; eine
        Angabe wie „1-2 Werktage" oder „36304 Alsfeld" macht ihn zitierfähig.
        Die Produktseite zählt mit – ihr statischer Teil nennt die Versanddauer."""
        seiten = [p for p in INHALTSSEITEN if p not in OHNE_ZAHL_IM_ERSTEN_DRITTEL]
        for pfad in seiten + [UMFANG_PRODUKT_SEITE]:
            with self.subTest(pfad=pfad):
                woerter = inhaltstext(self.hole(pfad).content.decode()).split()
                drittel = ' '.join(woerter[: max(1, len(woerter) // 3)])
                self.assertTrue(
                    re.search(r'\d', drittel),
                    f'{pfad}: im ersten Drittel des Inhalts steht keine Zahl: '
                    f'"{drittel[:200]}…"',
                )
