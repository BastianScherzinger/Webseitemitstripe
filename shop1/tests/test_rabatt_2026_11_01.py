"""Rabattcodes (01.11.2026): Prüfung, erste Bestellung, Link, Formular, Bestellung, Mails, Seiten.

python manage.py test shop1.tests.test_rabatt_2026_11_01
"""

import time
from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

from django.core import signing
from django.core.management import call_command
from django.test import override_settings

from shop1 import luviq_daten, rabatt, spamschutz
from shop1.models import Order, Rabattcode
from shop1.views.direktkauf import mail_an_kundin, mail_an_luisa
from ._basis import LuviqTestCase, erzeuge_produkt

_MAIL = 'shop1.views.direktkauf.send_brevo_email'


def _formzeit():
    return signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ)


class SchluesselTest(LuviqTestCase):
    def test_email_schluessel_vereinheitlicht(self):
        self.assertEqual(rabatt.email_schluessel(' Anna.Muster+2@GoogleMail.com '), 'annamuster@gmail.com')
        self.assertEqual(rabatt.email_schluessel('a.b+x@web.de'), 'a.b@web.de')

    def test_anschrift_schluessel(self):
        self.assertEqual(rabatt.anschrift_schluessel('Mühlenstraße 5', '23552'),
                         rabatt.anschrift_schluessel('muehlenstr. 5'.replace('ue', 'ü'), '23 552'))
        self.assertEqual(rabatt.anschrift_schluessel('Abholung in Lübeck nach Absprache', ''), '')

    def test_betrag_rundet_kaufmaennisch(self):
        self.assertEqual(rabatt.betrag(Decimal('69.00'), 10), Decimal('6.90'))
        self.assertEqual(rabatt.betrag(Decimal('69.95'), 10), Decimal('7.00'))  # 6,995 → 7,00

    def test_code_wird_beim_speichern_vereinheitlicht(self):
        c = Rabattcode.objects.create(code=' hafen wind-10 ', prozent=10)
        self.assertEqual(c.code, 'HAFENWIND-10')


class RabattDirektkaufTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        # Klassendekorator greift vor dem DIREKTKAUF=False der Basisklasse – deshalb hier.
        self.enterContext(override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True))
        self.produkt = erzeuge_produkt(
            name='Engel-Shirt', preis=Decimal('69.00'), masse='Größe M', material='Baumwolle',
            lagerbestand=5, aktiv=True, vergeben=False, zustand='Neu, von Hand bemalt', serie=True,
            bearbeitungstage=3, slug=luviq_daten.ENGEL_STUECK['slug'])
        self.pfad = f'/bestellen/{self.produkt.slug}/'
        self.stueck = self.produkt.get_absolute_url()
        self.mail = self.enterContext(mock.patch(_MAIL))
        self.zehn = Rabattcode.objects.create(code='HAFENWIND-10', prozent=10, oeffentlich=True, zweck='Website')
        self.zwanzig = Rabattcode.objects.create(code='TRAVEWIND-7KQ4', prozent=20, max_einloesungen=2)

    def daten(self, **ab):
        d = {'name': 'Kim Muster', 'email': 'kim@example.org', 'strasse': 'Testweg 1', 'plz': '23552',
             'stadt': 'Lübeck', 'lieferart': 'versand', 'zustimmung': 'ja', 'formzeit': _formzeit(),
             'rabattcode': 'hafenwind-10'}
        d.update(ab)
        return d

    def test_bestellung_mit_code_speichert_reduzierten_betrag(self):
        antwort = self.sende(self.pfad, self.daten())
        self.assertRedirects(antwort, '/bestellen/danke/', fetch_redirect_response=False)
        o = Order.objects.get()
        self.assertEqual(o.gesamt_betrag, Decimal('62.10'))
        self.assertEqual(o.rabatt_betrag, Decimal('6.90'))
        self.assertEqual((o.rabatt_code, o.rabatt_code_text, o.rabatt_prozent), (self.zehn, 'HAFENWIND-10', 10))
        self.assertEqual(o.email_schluessel, 'kim@example.org')
        self.assertEqual(self.zehn.einloesungen(), 1)
        danke = self.hole('/bestellen/danke/')
        self.assertContains(danke, '62,10')
        self.assertContains(danke, 'HAFENWIND-10')

    def test_zweite_bestellung_bekommt_keinen_erstbestellrabatt(self):
        self.sende(self.pfad, self.daten())
        Order.objects.update(erstellt_am=Order.objects.get().erstellt_am - timedelta(hours=1))
        # Andere Schreibweise derselben Adresse, gleiche Anschrift
        antwort = self.sende(self.pfad, self.daten(email='KIM+neu@example.org', formzeit=_formzeit()))
        self.assertEqual(antwort.status_code, 400)
        self.assertContains(antwort, 'nur für die erste Bestellung', status_code=400)
        self.assertContains(antwort, 'Es wurde noch nichts bestellt', status_code=400)
        self.assertEqual(Order.objects.count(), 1)

    def test_gleiche_anschrift_neue_email_gilt_nicht_als_erste(self):
        self.sende(self.pfad, self.daten())
        antwort = self.sende(self.pfad, self.daten(email='andere@example.org', strasse='Testweg  1',
                                                   formzeit=_formzeit()))
        self.assertEqual(antwort.status_code, 400)
        self.assertEqual(Order.objects.count(), 1)

    def test_stornierte_bestellung_zaehlt_nicht(self):
        self.sende(self.pfad, self.daten())
        Order.objects.update(status='cancelled', erstellt_am=Order.objects.get().erstellt_am - timedelta(hours=1))
        from django.core.cache import cache
        cache.clear()  # Doppelklick-Sperre (120 s) gehört nicht zu diesem Fall
        self.sende(self.pfad, self.daten(formzeit=_formzeit()))
        self.assertEqual(Order.objects.filter(rabatt_code=self.zehn).count(), 2)

    def test_doppelklick_legt_keine_zweite_bestellung_an(self):
        self.sende(self.pfad, self.daten())
        from django.core.cache import cache
        cache.clear()  # anderer Gunicorn-Prozess: Cache-Sperre greift nicht
        antwort = self.sende(self.pfad, self.daten(formzeit=_formzeit()))
        self.assertRedirects(antwort, '/bestellen/danke/', fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 1)

    def test_unbekannter_code_bestellt_nicht(self):
        antwort = self.sende(self.pfad, self.daten(rabattcode='GIBTSNICHT'))
        self.assertEqual(antwort.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_ohne_code_voller_preis(self):
        self.sende(self.pfad, self.daten(rabattcode=''))
        o = Order.objects.get()
        self.assertEqual((o.gesamt_betrag, o.rabatt_betrag, o.rabatt_code), (Decimal('69.00'), 0, None))

    def test_hoechstzahl_und_ablauf(self):
        for i in range(2):
            self.sende(self.pfad, self.daten(email=f'p{i}@example.org', strasse=f'Weg {i}', rabattcode='TRAVEWIND-7KQ4',
                                             formzeit=_formzeit()))
        self.assertEqual(Order.objects.filter(rabatt_prozent=20).count(), 2)
        antwort = self.sende(self.pfad, self.daten(email='p9@example.org', strasse='Weg 9',
                                                   rabattcode='TRAVEWIND-7KQ4', formzeit=_formzeit()))
        self.assertContains(antwort, 'vollständig eingelöst', status_code=400)
        self.zehn.gueltig_bis = date.today() - timedelta(days=2)
        self.zehn.save()
        self.assertIn('gültig', rabatt.pruefe('HAFENWIND-10', Decimal('69')).fehler)

    def test_einloesen_zeigt_preis_ohne_zu_bestellen(self):
        antwort = self.sende(self.pfad, {'aktion': 'rabattcode', 'rabattcode': 'travewind-7kq4'})
        self.assertEqual(antwort.status_code, 200)
        self.assertContains(antwort, '55,20')
        self.assertContains(antwort, 'Zahlungspflichtig bestellen')
        self.assertEqual(Order.objects.count(), 0)

    def test_link_merkt_code_und_formular_traegt_ihn_ein(self):
        antwort = self.hole('/rabatt/hafenwind-10/')
        self.assertRedirects(antwort, self.stueck + '#bestellen', fetch_redirect_response=False)
        seite = self.hole(self.stueck)
        self.assertContains(seite, 'value="HAFENWIND-10"')
        self.assertContains(seite, '62,10')
        # Bestellung ohne Feldinhalt aus dem POST: das Feld schickt den Code mit
        self.sende(self.pfad, self.daten(rabattcode='HAFENWIND-10'))
        self.assertEqual(Order.objects.get().rabatt_prozent, 10)

    def test_link_mit_fremdem_ziel_bleibt_auf_der_seite(self):
        antwort = self.hole('/rabatt/HAFENWIND-10/?weiter=https://boese.example/')
        self.assertRedirects(antwort, self.stueck + '#bestellen', fetch_redirect_response=False)

    def test_startseite_hero_zeigt_code_und_knopf(self):
        seite = self.hole('/')
        self.assertContains(seite, '/rabatt/HAFENWIND-10/')
        self.assertContains(seite, 'HAFENWIND-10')
        self.assertNotContains(seite, 'TRAVEWIND')

    def test_ohne_oeffentlichen_code_hero_wie_vorher(self):
        self.zehn.oeffentlich = False
        self.zehn.save()
        seite = self.hole('/')
        self.assertNotContains(seite, '/rabatt/')
        self.assertContains(seite, 'data-ereignis="hero_bestellen"')

    def test_faq_llms_und_agb_nennen_den_oeffentlichen_code(self):
        self.assertContains(self.hole('/wissen/bestellen-und-bezahlen/'), 'Gibt es einen Rabattcode')
        self.assertContains(self.hole('/llms.txt'), 'HAFENWIND-10')
        self.assertNotContains(self.hole('/llms.txt'), 'TRAVEWIND')
        self.assertContains(self.hole('/agb/'), 'Rabattcodes')

    def test_mails_nennen_den_rabatt(self):
        self.sende(self.pfad, self.daten())
        o = Order.objects.get()
        self.mail.reset_mock()
        mail_an_kundin(o)
        text = self.mail.call_args.kwargs['text_content']
        self.assertIn('Rabatt 10 % (Code HAFENWIND-10): -6.90', text)
        self.assertIn('62.10', text)
        self.mail.reset_mock()
        mail_an_luisa(o)
        self.assertIn('Rechnung über diesen Betrag', self.mail.call_args.kwargs['text_content'])

    def test_zu_langer_nachname_ergibt_meldung_statt_fehler(self):
        antwort = self.sende(self.pfad, self.daten(name='Kim ' + 'x' * 120))
        self.assertContains(antwort, 'zu lang', status_code=400)


class RabattOhneVerkaufTest(LuviqTestCase):
    def test_ohne_verkauf_kein_code_und_link_leitet_um(self):
        self.enterContext(override_settings(VERKAUF_AKTIV=False, DIREKTKAUF=True))
        Rabattcode.objects.create(code='HAFENWIND-10', prozent=10, oeffentlich=True)
        self.assertNotContains(self.hole('/'), 'HAFENWIND-10')
        self.assertEqual(self.hole('/rabatt/HAFENWIND-10/').status_code, 302)


class BefehlTest(LuviqTestCase):
    def test_anlegen_mit_zufall_und_liste(self):
        call_command('rabattcode', 'anlegen', '--zufall', 'karte', '--prozent', '10', '--zweck', 'Karten', stdout=mock.Mock())
        c = Rabattcode.objects.get()
        self.assertRegex(c.code, r'^KARTE-[A-HJ-KM-NP-Z2-9]{4}$')
        self.assertTrue(c.nur_erstbestellung)
        call_command('rabattcode', 'aus', c.code, stdout=mock.Mock())
        c.refresh_from_db()
        self.assertFalse(c.aktiv)
