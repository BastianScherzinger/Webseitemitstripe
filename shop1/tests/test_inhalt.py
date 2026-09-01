"""Inhalt: stimmt, was auf der Seite steht – und stimmt es überall gleich?

Widersprüchliche Angaben zu Anschrift, E-Mail oder Zahlungsarten sind für die
lokale Auffindbarkeit einer der schädlichsten Zustände überhaupt: Google
gleicht diese Angaben quer über Seite, Schema und Verzeichnisse ab.
"""

import re
from html.parser import HTMLParser

from ._basis import INHALTSSEITEN, OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_produkt
from .test_geo import sichtbarer_text

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

        Die drei Rechtstexte sind ausgenommen: sie beginnen mit einer knappen
        Bereichsbezeichnung über dem vorgeschriebenen Aufbau, und diese Zeile
        aufzublähen wäre eine Änderung am Erscheinungsbild ohne Nutzen."""
        rechtstexte = {'/impressum/', '/datenschutz/', '/agb/'}
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
