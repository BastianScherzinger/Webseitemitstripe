"""EU-Gewährleistungshinweis auf der echten Bestellseite (Rechtscheck 07.11.2026, Befund K1).

Art. 246a § 1 Abs. 1 Satz 1 Nr. 11 EGBGB, DVO (EU) 2025/1960 Anhang I: harmonisierte Mitteilung in
hervorgehobener Weise, hier unmittelbar vor dem Bestellknopf von Kaufseite und Stückseite.

Prüfbefehl: python manage.py test shop1.tests.test_eu_gewaehrleistung_2026_11_07
"""

from decimal import Decimal

from django.test import override_settings

from ._basis import LuviqTestCase, erzeuge_produkt

_VOLLTEXT = ('Mindestens zwei Jahre gesetzliche Gewährleistung der Vertragsmäßigkeit für Waren, die in der '
             'Europäischen Union verkauft werden. Für gebrauchte Waren kann ein kürzerer Zeitraum gelten, jedoch '
             'nicht weniger als ein Jahr. Verkäufer haften für jede Vertragswidrigkeit, die bei Lieferung bestand '
             'und innerhalb der Gewährleistungsfrist erkennbar wird, und müssen kostenlose Nachbesserung oder '
             'Ersatzlieferung, in bestimmten Fällen Preisminderung oder Erstattung anbieten. Problem so bald wie '
             'möglich dem Verkäufer melden und einen Kaufnachweis vorlegen. Mehr: europa.eu/youreurope/garantien')


@override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
class EuGewaehrleistungBestellseiteTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.enter = self.settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
        self.enter.enable()
        self.addCleanup(self.enter.disable)
        self.shirt = erzeuge_produkt(
            name='Engel-Shirt', preis=Decimal('69.00'), masse='Größe M', material='100 % Baumwolle',
            lagerbestand=1, aktiv=True, vergeben=False, zustand='Gebraucht, von Hand mit Bleiche gemalt',
            serie=True, bearbeitungstage=3)

    def test_hinweis_steht_direkt_vor_dem_bestellknopf(self):
        for pfad in (f'/bestellen/{self.shirt.slug}/', f'/produkt/{self.shirt.slug}/'):
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                form = html.split('id="bestellen"', 1)[1].split('</form>', 1)[0]
                self.assertEqual(form.count('class="lv-gewaehr"'), 1)
                self.assertEqual(form.count('type="submit" class="lv-knopf">'), 1)
                self.assertLess(form.index('class="lv-gewaehr"'), form.index('type="submit" class="lv-knopf">'))
                nach_hinweis = form.split('class="lv-gewaehr"', 1)[1].split('type="submit" class="lv-knopf">', 1)[0]
                self.assertLess(len(nach_hinweis), 1200, 'Hinweis muss unmittelbar vor dem Knopf stehen')

    def test_text_vollstaendig_und_bild_unveraendert(self):
        html = self.hole(f'/bestellen/{self.shirt.slug}/').content.decode()
        self.assertIn(_VOLLTEXT, html)
        self.assertIn('Für alle Stücke gilt die gesetzliche Gewährleistung von zwei Jahren, auch für gebrauchte Stücke.', html)
        self.assertIn('eu-gewaehrleistung-hinweis-de', html)
        self.assertIn('width="1654" height="2339" loading="eager"', html)

    def test_alter_checkout_nutzt_dieselbe_quelle(self):
        from django.template.loader import get_template
        quelle = get_template('shop1/checkout.html').template.source
        self.assertIn("shop1/teile/eu_gewaehrleistung.html", quelle)
        self.assertNotIn('<img class="lv-gewaehr"', quelle)
