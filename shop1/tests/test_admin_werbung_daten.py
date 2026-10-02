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


class StatistikBausteineTest(LuviqTestCase):
    """Die aus ``admin_stats`` und ``admin_werbung_list`` herausgelösten Schritte (P08)."""

    def test_umsatz_und_rabatt_nur_aus_bezahlten_bestellungen(self):
        from decimal import Decimal

        from .. import admin_views
        from ..models import Order, OrderItem
        from ._basis import erzeuge_benutzer

        kundin = erzeuge_benutzer('kundin')
        daten = dict(user=kundin, vorname='E', nachname='M', adresse='Weg 1', postleitzahl='36304',
                     stadt='Alsfeld', land='Deutschland', email='e@example.invalid')
        bezahlt = Order.objects.create(status='paid', gesamt_betrag=Decimal('45.00'), **daten)
        OrderItem.objects.create(order=bezahlt, produkt_name='A', produkt_preis=Decimal('30.00'), menge=2)
        offen = Order.objects.create(status='pending', gesamt_betrag=Decimal('99.00'), **daten)
        OrderItem.objects.create(order=offen, produkt_name='B', produkt_preis=Decimal('99.00'))

        umsatz, rabatt = admin_views._umsatz_und_rabatte(Order.objects.filter(status='paid'))
        self.assertEqual((umsatz, rabatt), (45.0, 15.0))
        self.assertEqual(admin_views._umsatz_und_rabatte(Order.objects.none()), (0, 0))

    def test_besuche_30_tage_fuellt_luecken_mit_null(self):
        from datetime import timedelta

        from django.utils import timezone

        from .. import admin_views
        from ..models import PageVisit

        PageVisit.objects.create(date=timezone.localdate() - timedelta(days=2), visits=7)
        werte = json.loads(admin_views._besuche_30_tage())
        self.assertEqual(len(werte['labels']), 30)
        self.assertEqual(werte['data'][-3], 7)
        self.assertEqual(sum(werte['data']), 7)

    def test_letzte_besucher_zaehlen_nur_die_eigene_site(self):
        from unittest import mock

        from .. import admin_views
        from ..models import VisitorLog

        VisitorLog.objects.using('pystore').create(seite='luviq', path='/')
        VisitorLog.objects.using('pystore').create(seite='luviq', path='/kontakt/')
        VisitorLog.objects.using('pystore').create(seite='anderswo', path='/')
        with mock.patch.dict('os.environ', {'SITE_NAME': 'luviq'}):
            liste, gesamt = admin_views._letzte_besucher()
        self.assertEqual((len(liste), gesamt), (2, 2))
        self.assertEqual(liste[0].path, '/kontakt/')    # neueste zuerst

    def test_ein_fehler_beim_lesen_gibt_leere_werte_und_eine_spur(self):
        from unittest import mock

        from .. import admin_views

        with mock.patch('shop1.admin_views.VisitorLog') as modell, \
                self.assertLogs('shop1', level='ERROR'):
            modell.objects.filter.side_effect = RuntimeError('weg')
            self.assertEqual(admin_views._letzte_besucher(), ([], 0))
        with mock.patch('shop1.admin_views.WerbungStat') as modell, \
                self.assertLogs('shop1', level='ERROR'):
            modell.objects.filter.side_effect = RuntimeError('weg')
            self.assertEqual(admin_views._plattform_reichweite([1])['labels'], [])
            self.assertEqual(admin_views._tagesverlauf([1])['views'], [])

    def test_die_statistikseite_rendert_mit_den_neuen_schritten(self):
        chefin = User.objects.create_superuser('chefin2', 'c2@example.invalid', 'ein-langes-testpasswort')
        self.client.force_login(chefin)
        for pfad in ('/shop-admin/stats/', '/shop-admin/werbung/'):
            with self.subTest(pfad=pfad):
                self.assertEqual(self.hole(pfad).status_code, 200)
