"""Durchstarten (15.11.2026): Wisch-Band mit echtem Status, Anfrage-Fassung von llms.txt, Schema, Datenschutz 8a.

Prüft:
- das Wisch-Band auf Start und /produkte/: offenes Stück zuerst, „Vergeben“ nur bei echten Daten (Archiv-Flag oder
  Bestand 0 nach Bestellung), nie „Verkauft“, nie „nur 1×“ bei einem Serienstück, „Unikat · 1×“ nur bei genau
  einem Stück auf Lager;
- der Startfilm „Verkaufsstart“ steht nicht mehr auf der Startseite;
- ``/llms.txt`` im Anfrage-Shop: keine Warteliste, kein „noch nicht“, dafür der Anfrageweg;
- das Organization-Schema im Anfrage-Shop ohne „Derzeit findet kein Verkauf statt“;
- FAQ der Stückseite im Anfrage-Shop (sichtbar und als FAQPage, ohne Zahlungsart);
- der Datenschutz-Abschnitt 8a gegen die Felder des Formulars.
"""
import json
import re
from decimal import Decimal

from django.test import override_settings

from .. import luviq_daten
from ..models import Produkt
from ._basis import LuviqTestCase, erzeuge_produkt

STATISCH = 'shop1/images/luviq/hero-engel-45-{w}.webp@480,640,800#800x999'


def _ld(html):
    roh = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    return [json.loads(r) for r in roh]


class BandTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        einstellungen = self.settings(VERKAUF_AKTIV=False, DIREKTKAUF=True, ANFRAGESHOP=True)
        einstellungen.enable()
        self.addCleanup(einstellungen.disable)
        self.engel = erzeuge_produkt('Engel-Shirt', preis=Decimal('69.00'), lagerbestand=1, serie=True,
                                     bearbeitungstage=3, bild_statisch=STATISCH, nummer=6)
        self.archiv = erzeuge_produkt('Custom Hoodie', vergeben=True, lagerbestand=1, bild_statisch=STATISCH, nummer=1)
        self.einzeln = erzeuge_produkt('Einzelstück Jacke', lagerbestand=1, bild_statisch=STATISCH, nummer=7)
        self.leer = erzeuge_produkt('Ausverkaufte Weste', lagerbestand=0, bild_statisch=STATISCH, nummer=8)

    def test_status_kommt_aus_den_daten(self):
        self.assertEqual(self.engel.status_wort, luviq_daten.OFFEN_WORT)
        self.assertEqual(self.engel.status_klasse, 'offen')
        self.assertEqual(self.archiv.status_wort, 'Vergeben')
        self.assertEqual(self.leer.status_wort, 'Vergeben')   # Bestand 0 nach Bestellung: „Vergeben“, nie „Verkauft“
        self.assertNotIn('Verkauft', {luviq_daten.VERKAUFT_WORT, luviq_daten.VERGEBEN_WORT})

    def test_hinweis_ist_ehrlich(self):
        self.assertIn('Serie', self.engel.band_hinweis)
        self.assertNotIn('1×', self.engel.band_hinweis)          # Serienstück ist nie „nur 1×“
        self.assertEqual(self.einzeln.band_hinweis, 'Unikat · 1×')  # genau ein Stück auf Lager, kein Serienstück
        self.einzeln.lagerbestand = 3
        self.assertEqual(self.einzeln.band_hinweis, 'Unikat')
        self.assertTrue(self.archiv.band_hinweis.startswith('Archiv'))

    def test_band_auf_der_startseite_offene_zuerst(self):
        html = self.hole('/').content.decode()
        self.assertIn('class="lv-reihe"', html)
        self.assertIn('role="region"', html)
        kopf = html.split('class="lv-reihe"', 1)[1]
        self.assertLess(kopf.index('Engel-Shirt'), kopf.index('Custom Hoodie'))
        self.assertLess(kopf.index('Einzelstück Jacke'), kopf.index('Custom Hoodie'))
        self.assertLess(kopf.index('Custom Hoodie'), kopf.index('Ausverkaufte Weste') + 10_000)
        # Genau die Stücke mit Archiv-Flag bzw. Bestand 0 tragen „Vergeben“, die offenen „Offen“.
        self.assertEqual(html.count('lv-reihestatus vergeben'), 2)
        self.assertEqual(html.count('lv-reihestatus offen'), 2)
        self.assertNotIn('Verkauft', html)
        self.assertNotIn('Jetzt im Shop', html)

    def test_offene_karte_hat_preis_und_anfrageknopf_vergebene_nicht(self):
        html = self.hole('/').content.decode()
        offen = re.search(r'<li class="lv-reihekarte ist-offen">.*?</li>', html, re.S).group(0)
        self.assertIn('69,00 €', offen)
        self.assertIn('Stück anfragen', offen)
        vergeben = re.search(r'<li class="lv-reihekarte ist-vergeben">.*?</li>', html, re.S).group(0)
        self.assertNotIn('Stück anfragen', vergeben)
        self.assertNotIn(' €', vergeben)

    def test_kein_vergeben_ohne_daten(self):
        Produkt.objects.filter(pk__in=[self.archiv.pk, self.leer.pk]).delete()
        html = self.hole('/').content.decode()
        self.assertNotIn('lv-reihestatus vergeben', html)
        self.assertNotIn('Vergeben', html.split('id="stuecke"', 1)[1].split('</section>', 1)[0])

    def test_produkte_nutzt_dasselbe_band(self):
        html = self.hole('/produkte/').content.decode()
        self.assertIn('class="lv-reihe"', html)
        self.assertEqual(html.count('lv-reihestatus vergeben'), 2)
        self.assertIn('lv-kopf-eins', html)
        self.assertEqual(len(re.findall(r'<h1\b', html)), 1)

    def test_startfilm_verkaufsstart_ist_weg(self):
        html = self.hole('/').content.decode()
        self.assertIsNone(luviq_daten.STARTFILM)
        self.assertNotIn('id="startfilm"', html)
        self.assertNotIn('Verkaufsstart', html)
        self.assertNotIn('Shop offen', html)
        self.assertNotIn('3 Monate später', html)

    def test_archiv_abschnitt_unten_ist_im_band_aufgegangen(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('id="archiv"', html)
        self.assertNotIn('Seitlich wischen</p>', html)


class LlmsAnfrageTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        einstellungen = self.settings(VERKAUF_AKTIV=True, DIREKTKAUF=True, ANFRAGESHOP=True)
        einstellungen.enable()
        self.addCleanup(einstellungen.disable)
        self.engel = erzeuge_produkt('Engel-Shirt', preis=Decimal('69.00'), lagerbestand=1, serie=True,
                                     bearbeitungstage=3, bild_statisch=STATISCH, nummer=6,
                                     slug=luviq_daten.ENGEL_STUECK['slug'])
        erzeuge_produkt('Custom Hoodie', vergeben=True, bild_statisch=STATISCH, nummer=1)

    def test_llms_txt_sagt_anfrage_statt_noch_nicht(self):
        text = self.hole('/llms.txt').content.decode()
        for alt in ('Warteliste', 'Noch nicht', 'noch kein Verkauf', 'Marke im Aufbau', 'Verkaufsstart',
                    'Jetzt bestellen', 'Warenkorb'):
            with self.subTest(alt=alt):
                self.assertNotIn(alt, text)
        self.assertIn('auf Anfrage', text)
        self.assertIn('keine Bestellung', text)
        self.assertIn('Engel-Shirt', text)
        self.assertIn('69.00 EUR', text)
        self.assertIn('Archiv (vergeben', text)
        self.assertIn('Lübeck', text)

    def test_llms_txt_nennt_keine_lieferfrist_in_tagen_und_keine_gmail(self):
        text = self.hole('/llms.txt').content.decode()
        self.assertNotIn('5 Werktagen', text)
        self.assertNotIn('gmail', text.lower())

    def test_llms_full_txt_beginnt_mit_der_anfrage_fassung(self):
        text = self.hole('/llms-full.txt').content.decode()
        self.assertNotIn('Warteliste', text.split('## Volltext der Seiten')[0])
        self.assertIn('auf Anfrage', text.split('## Volltext der Seiten')[0])

    def test_organization_schema_ohne_kein_verkauf(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('Derzeit findet kein Verkauf statt', html)
        org = [k for k in sum((k if isinstance(k, list) else [k] for k in _ld(html)), [])
               if isinstance(k, dict)]
        beschreibungen = ' '.join(str(k.get('description', '')) for k in org)
        graph = [n for k in org for n in k.get('@graph', [])]
        beschreibungen += ' '.join(str(n.get('description', '')) for n in graph)
        self.assertIn('Stücke werden auf Anfrage vergeben', beschreibungen)

    def test_stueckseite_hat_faq_ohne_zahlungsart(self):
        antwort = self.hole(self.engel.get_absolute_url())
        html = antwort.content.decode()
        faq = [k for k in _ld(html) if isinstance(k, dict) and k.get('@type') == 'FAQPage']
        self.assertEqual(len(faq), 1)
        fragen = [e['name'] for e in faq[0]['mainEntity']]
        self.assertIn('Wie bekomme ich das Engel-Shirt?', fragen)
        # Alles, was im Schema steht, steht auch sichtbar auf der Seite.
        for frage in fragen:
            self.assertIn(frage, html)
        text = json.dumps(faq[0], ensure_ascii=False)
        for weg in ('Zahlungslink', 'Revolut', 'Überweisung', 'ohne Konto', 'Rechnung'):
            self.assertNotIn(weg, text)
        self.assertIn('69 €', text)

    def test_stueckseite_ohne_offer_im_anfrage_shop(self):
        html = self.hole(self.engel.get_absolute_url()).content.decode()
        self.assertNotIn('"@type": "Offer"', html)
        self.assertNotIn('aggregateRating', html)


class RechtstextTest(LuviqTestCase):
    def test_datenschutz_8a_nennt_die_felder_des_formulars(self):
        html = self.hole('/datenschutz/').content.decode()
        self.assertIn('id="ds-8a"', html)
        abschnitt = html.split('id="ds-8a"', 1)[1].split('id="ds-9"', 1)[0]
        for feld in ('Namen', 'E-Mail-Adresse', 'Stückzahl', 'Größe', 'Nachricht', 'Bearbeitungsstatus',
                     'keine Bestellung', 'Art. 6 Abs. 1 lit. b DSGVO'):
            with self.subTest(feld=feld):
                self.assertIn(feld, abschnitt)
        self.assertNotIn('gmail', abschnitt.lower())
        self.assertIn('Stand: 24. November 2026', html)  # Spam/Angebote-Absatz 24.11.

    def test_formularfelder_sind_die_in_8a_genannten(self):
        formular = open('shop1/templates/shop1/teile/stueckanfrage_formular.html', encoding='utf-8').read()
        for name in ('name', 'email', 'anzahl', 'groesse', 'nachricht'):
            self.assertIn(f'name="{name}"', formular)

    @override_settings(ANFRAGESHOP=True, VERKAUF_AKTIV=True)
    def test_hinweis_zu_alten_abschnitten_nur_im_anfrage_shop(self):
        html = self.hole('/datenschutz/').content.decode()
        self.assertIn('bis zum 14.11.2026 möglich waren', html)

    def test_liefergebiet_sagt_versand_im_preis(self):
        with self.settings(ANFRAGESHOP=True, VERKAUF_AKTIV=True):
            html = self.hole('/liefergebiet/').content.decode()
        self.assertNotIn('Versandkosten klärt', html)
        self.assertIn('im Preis enthalten', html)
