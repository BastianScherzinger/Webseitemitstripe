"""Anfrage-Shop (15.11.2026, Nachbesserung): keine Sätze „kein Verkauf / Warteliste / ersten Drop“ in Wissen, llms-full
und Motiv-Seite, in beiden Schalterständen (VERKAUF_AKTIV an und aus), dazu die Handy-Knöpfe der Stückseite."""
import re
from decimal import Decimal

from ._basis import LuviqTestCase, erzeuge_produkt

STATISCH = 'shop1/images/luviq/hero-engel-45-{w}.webp@480,640,800#800x999'
SEITEN = ['/wissen/groesse-bei-einzelstuecken/', '/wissen/pflege-handbemalte-kleidung/',
          '/wissen/upcycling-mode-second-hand-vintage/', '/motiv-anfragen/', '/llms-full.txt']
VERBOTEN = ['findet kein Verkauf', 'ersten Drop', 'Warteliste', 'verkauft derzeit nichts', 'Noch nicht.',
            'Ist ein Stück verkauft', 'Marke im Aufbau']


def _text(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html))


class AnfrageTexteTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.engel = erzeuge_produkt('Engel-Shirt', preis=Decimal('69.00'), lagerbestand=1, serie=True,
                                     bearbeitungstage=3, bild_statisch=STATISCH, nummer=6)

    def test_keine_widerspruechlichen_saetze(self):
        for verkauf in (False, True):
            with self.settings(ANFRAGESHOP=True, VERKAUF_AKTIV=verkauf, DIREKTKAUF=True):
                for pfad in SEITEN:
                    text = _text(self.hole(pfad).content.decode())
                    for wort in VERBOTEN:
                        self.assertNotIn(wort, text, f'{pfad} (VERKAUF_AKTIV={verkauf}): {wort}')

    def test_stueckseite_hat_knopf_unter_dem_preis_und_leiste(self):
        with self.settings(ANFRAGESHOP=True, VERKAUF_AKTIV=False, DIREKTKAUF=True):
            html = self.hole(f'/produkt/{self.engel.slug}/').content.decode()
        self.assertIn('data-anfrage-knopf', html)
        # 26.11.2026: im Anfrage-Shop steht kein Preis mehr im Knopf (Bastians Regel seit 20.11.)
        self.assertIn('>Stück anfragen</a>', html)
        self.assertNotIn('Stück anfragen ·', html)
        self.assertIn('data-kaufleiste', html)

    def test_danke_knopf_und_leiste_auf_produkte(self):
        with self.settings(ANFRAGESHOP=True, VERKAUF_AKTIV=False, DIREKTKAUF=True):
            produkte = self.hole('/produkte/').content.decode()
        self.assertIn('ohne-leiste', produkte)
