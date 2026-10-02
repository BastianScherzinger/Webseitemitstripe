"""Werbe-Statistik im Admin-Panel: Diagrammdaten kommen als ``json_script``, nicht als ``|safe``.

Der Seitenname einer ``WerbungStat`` stammt von fremden Sites (das
``pystore``-Projekt schreibt ihn). Stünde das JSON roh in einem Skript, könnte
ein Name wie ``</script><script>…`` Code in das Panel der Betreiberin bringen
(Prüfung V02). ``json_script`` maskiert ``<``, ``>`` und ``&``.
"""

import json
import re
from datetime import date

from django.contrib.auth.models import User

from ..models import Werbung, WerbungStat
from ._basis import LuviqTestCase

BOESER_NAME = '</script><script>alert(1)</script>'


class WerbungDatenTest(LuviqTestCase):

    def setUp(self):
        chefin = User.objects.create_superuser('chefin', 'chefin@example.invalid', 'ein-langes-testpasswort')
        self.client.force_login(chefin)

    def daten(self, html, kennung):
        treffer = re.search(rf'<script id="{kennung}" type="application/json">(.*?)</script>', html, re.S)
        self.assertIsNotNone(treffer, f'{kennung} fehlt')
        return json.loads(treffer.group(1))

    def test_ohne_werbung_gibt_es_keine_datenbloecke_und_die_seite_antwortet(self):
        antwort = self.hole('/shop-admin/werbung/')
        self.assertEqual(antwort.status_code, 200)
        self.assertNotContains(antwort, 'werbung-timeline')

    def test_die_diagrammdaten_stehen_maskiert_in_zwei_json_bloecken(self):
        werbung = Werbung.objects.create(titel='Banner', link='https://www.luviq-alsfeld.com/')
        WerbungStat.objects.using('pystore').create(
            werbung=werbung, seite=BOESER_NAME, impressionen=5, klicks=2, datum=date.today())
        html = self.hole('/shop-admin/werbung/').content.decode()

        # Der Name kommt nie roh im Quelltext vor …
        self.assertNotIn(BOESER_NAME, html)
        self.assertNotIn('<script>alert(1)', html)
        # … und ist nach dem Lesen des JSON wieder derselbe Text.
        plattformen = self.daten(html, 'werbung-plattformen')
        self.assertEqual(plattformen['views'], [5])
        self.assertEqual(plattformen['klicks'], [2])
        self.assertEqual(plattformen['labels'], [BOESER_NAME.capitalize()])
        verlauf = self.daten(html, 'werbung-timeline')
        self.assertEqual(len(verlauf['labels']), 30)
        self.assertEqual((sum(verlauf['views']), sum(verlauf['klicks'])), (5, 2))

    def test_das_skript_liest_die_bloecke_und_kein_safe_steht_mehr_dort(self):
        quelle = open(self._vorlage(), encoding='utf-8').read()
        self.assertNotIn('|safe', quelle)
        self.assertIn("getElementById('werbung-timeline')", quelle)
        self.assertIn("getElementById('werbung-plattformen')", quelle)

    @staticmethod
    def _vorlage():
        from pathlib import Path
        return str(Path(__file__).resolve().parent.parent / 'templates' / 'shop1' / 'admin' / 'werbung_list.html')
