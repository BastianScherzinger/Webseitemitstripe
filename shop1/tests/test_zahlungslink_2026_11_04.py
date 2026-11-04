"""Revolut-Zahlungslink als Hauptweg des Direktkaufs (04.11.2026, Auftrag Bastian).

Geprüft wird: die Zahlart der Bestellung, die drei Mails (Kundin, Luisa, Kopie an die Webagentur), der
Block „So bezahlst du“ auf Kaufseite, Stückseite und Danke-Seite, die einheitliche Lieferfrist-Formulierung,
AGB, Datenschutz (Revolut), llms.txt und Schema, dazu der Ablauf „bezahlt“ im Panel.

Prüfbefehl: python manage.py test shop1.tests.test_zahlungslink_2026_11_04
"""

import os
import re
import time
from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.core import signing
from django.test import Client, override_settings

from shop1 import luviq_daten, spamschutz
from shop1.models import Order
from ._basis import LuviqTestCase, erzeuge_produkt

_MAIL = 'shop1.views.direktkauf.send_brevo_email'
_ALT = re.compile(r'Überweisungsauftrag|nach deiner Überweisung|ab deiner Überweisung|Rechnung mit den Zahlungsdaten|'
                  r'im Voraus per Überweisung|PayPal|Klarna|inkl\.? MwSt|inklusive MwSt|Pay by bank', re.I)


def _formzeit_alt():
    return signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ)


@override_settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
class ZahlungslinkTest(LuviqTestCase):
    def setUp(self):
        super().setUp()
        self.enter = self.settings(VERKAUF_AKTIV=True, DIREKTKAUF=True)
        self.enter.enable()
        self.addCleanup(self.enter.disable)
        self.mail = self.enterContext(mock.patch(_MAIL))
        self.enterContext(mock.patch.dict(os.environ, {'BETREIBER_KOPIE_AN': 'bastian.scherzinger05@gmail.com'}))
        self.shirt = erzeuge_produkt(
            name='Engel-Shirt', preis=Decimal('69.00'), masse='Größe M', material='100 % Baumwolle',
            lagerbestand=1, aktiv=True, vergeben=False, zustand='Gebraucht, von Hand mit Bleiche gemalt',
            serie=True, bearbeitungstage=3)
        self.einzel = erzeuge_produkt(
            name='Drachen-Hoodie', preis=Decimal('89.00'), masse='Größe L', material='Baumwolle',
            lagerbestand=1, aktiv=True, vergeben=False, zustand='Gebraucht, von Hand bemalt')

    def daten(self, **abweichungen):
        daten = {'name': 'Kim Muster', 'email': 'kundin@example.org', 'strasse': 'Testweg 1', 'plz': '23552',
                 'stadt': 'Lübeck', 'lieferart': 'versand', 'zustimmung': 'ja', 'formzeit': _formzeit_alt()}
        daten.update(abweichungen)
        return daten

    def bestelle(self, produkt):
        antwort = self.sende(f'/bestellen/{produkt.slug}/', self.daten())
        self.assertRedirects(antwort, '/bestellen/danke/', fetch_redirect_response=False)
        return Order.objects.latest('pk')

    def mail_an(self, adresse):
        for aufruf in self.mail.call_args_list:
            if aufruf.args[2] == adresse:
                return aufruf
        self.fail(f'keine Mail an {adresse}: {[a.args[2] for a in self.mail.call_args_list]}')

    # ── Datenmodell ──────────────────────────────────────────────────────────────────────

    def test_direktkauf_legt_die_zahlart_zahlungslink_an(self):
        bestellung = self.bestelle(self.shirt)
        self.assertEqual(bestellung.payment_method, 'zahlungslink')
        self.assertEqual(bestellung.get_payment_method_display(), 'Zahlungslink (Karte, Apple Pay, Google Pay)')
        self.assertEqual(bestellung.zahlungslink, '')

    def test_einzelstueck_ist_mit_dem_zahlungslink_reserviert_und_stornieren_gibt_frei(self):
        bestellung = self.bestelle(self.einzel)
        self.assertContains(self.hole(f'/produkt/{self.einzel.slug}/'), 'Reserviert')
        self.client = Client()
        self.mail.reset_mock()
        antwort = self.sende(f'/bestellen/{self.einzel.slug}/', self.daten(email='zweite@example.org'))
        self.assertEqual(antwort.status_code, 409)
        self.assertEqual(Order.objects.count(), 1)
        bestellung.status = 'cancelled'
        bestellung.save()
        self.assertNotContains(self.hole(f'/produkt/{self.einzel.slug}/'), 'Dieses Stück wurde soeben reserviert')

    # ── Mails ────────────────────────────────────────────────────────────────────────────

    def test_drei_mails_kundin_luisa_und_kopie_an_bastian_mit_richtigem_antworten_an(self):
        bestellung = self.bestelle(self.shirt)
        empfaenger = [a.args[2] for a in self.mail.call_args_list]
        self.assertCountEqual(empfaenger, ['kundin@example.org', 'brehlerluisa@gmail.com'])
        self.assertEqual(self.mail_an('kundin@example.org').kwargs['reply_to'], 'brehlerluisa@gmail.com')
        self.assertEqual(self.mail_an('brehlerluisa@gmail.com').kwargs['reply_to'], 'kundin@example.org')
        self.kopie_versand.assert_called_once()
        kopie = self.kopie_versand.call_args
        self.assertEqual(kopie.args[2], 'bastian.scherzinger05@gmail.com')
        self.assertEqual(kopie.kwargs['reply_to'], 'kundin@example.org')
        self.assertIn(f'#{bestellung.id}', kopie.args[3] if len(kopie.args) > 3 else kopie.kwargs.get('text_content', ''))

    def test_kopie_geht_auch_hinaus_wenn_die_mail_an_luisa_scheitert(self):
        def kaputt(betreff, html, adresse, *a, **kw):
            if adresse == 'brehlerluisa@gmail.com':
                raise RuntimeError('Brevo weg')
        self.mail.side_effect = kaputt
        self.bestelle(self.shirt)
        self.kopie_versand.assert_called_once()
        self.assertEqual(Order.objects.count(), 1)

    def test_mail_an_die_kundin_sagt_reserviert_zahlungslink_separat_und_dass_gemalt_wird(self):
        bestellung = self.bestelle(self.shirt)
        aufruf = self.mail_an('kundin@example.org')
        betreff, html, text = aufruf.args[0], aufruf.args[1], aufruf.kwargs['text_content']
        self.assertEqual(betreff, f'Deine Bestellung #{bestellung.id} ist reserviert – Luviq')
        for teil in (text, html):
            for satz in ('reserviert', f'innerhalb von {luviq_daten.RECHNUNG_FRIST}', 'separat', 'Zahlungslink',
                         'Rechnung', 'Spam-Ordner', 'Revolut', 'Apple Pay', 'Google Pay', 'Revolut Pay', 'Überweisung',
                         'von Hand', 'ca. 3 Werktage', '69,00 €', 'AGB § 2', 'ab dem Tag nach deiner Zahlung',
                         'Muster-Widerrufsformular'):
                self.assertIn(satz, teil, f'fehlt in der Mail: {satz}')
        self.assertIn('wird jetzt für dich gemacht', text)
        self.assertNotRegex(text, _ALT)
        self.assertNotIn('style=""', html)
        # Gestaltet über die Mail-Basis (Kopf mit Wortmarke, Fuß mit Impressum).
        self.assertIn('Impressum', html)
        self.assertIn('Zahlungsart: Vorkasse per Zahlungslink von Revolut', html)

    def test_mail_an_die_kundin_bei_einzelstueck_ohne_malen_versprechen(self):
        self.bestelle(self.einzel)
        text = self.mail_an('kundin@example.org').kwargs['text_content']
        self.assertIn('reserviert', text)
        self.assertNotIn('malt Luisa dein Shirt', text)
        self.assertIn('versandfertig', text)

    def test_mail_an_luisa_hat_die_checkliste_mit_betrag_nummer_und_adresse(self):
        bestellung = self.bestelle(self.shirt)
        aufruf = self.mail_an('brehlerluisa@gmail.com')
        text, html = aufruf.kwargs['text_content'], aufruf.args[1]
        for teil in (text, html):
            for satz in ('In Revolut Pro einen Zahlungslink über genau 69,00 € erstellen',
                         f'Luviq Bestellung Nr. {bestellung.id}', 'Mehrmals bezahlen', 'Lexware', 'kundin@example.org',
                         f'innerhalb von {luviq_daten.RECHNUNG_FRIST}', 'auf „bezahlt“ setzen', 'Nächster Schritt'):
                self.assertIn(satz, teil, f'fehlt in der Mail an Luisa: {satz}')
        self.assertIn('Zahlungslink (Karte, Apple Pay, Google Pay)', text)
        self.assertNotIn('Rechnung mit Zahlungsdaten an die Kundin schicken', text)

    def test_nach_bezahlt_im_panel_geht_die_zahlungsbestaetigung_ohne_ueberweisungswort_raus(self):
        bestellung = self.bestelle(self.einzel)
        besitzerin = User.objects.create_superuser('shopbesitzer', 'shop@example.invalid', 'ein-langes-testpasswort')
        self.client.force_login(besitzerin)
        with mock.patch('shop1.views.checkout.send_brevo_email') as bestaetigung:
            self.sende(f'/shop-admin/orders/{bestellung.id}/', {'action': 'update_status', 'status': 'paid'})
        bestellung.refresh_from_db()
        self.assertEqual(bestellung.status, 'paid')
        bestaetigung.assert_called_once()
        self.assertEqual(bestaetigung.call_args.args[2], 'kundin@example.org')
        self.assertIn('Deine Zahlung ist eingegangen', bestaetigung.call_args.args[1])
        self.assertNotIn('Deine Überweisung ist eingegangen', bestaetigung.call_args.args[1])
        self.einzel.refresh_from_db()
        self.assertFalse(self.einzel.kaufbar)

    def test_zahlungslink_laesst_sich_im_panel_ablegen_und_verschickt_nichts(self):
        bestellung = self.bestelle(self.shirt)
        self.mail.reset_mock()
        besitzerin = User.objects.create_superuser('shopbesitzer', 'shop@example.invalid', 'ein-langes-testpasswort')
        self.client.force_login(besitzerin)
        seite = self.hole(f'/shop-admin/orders/{bestellung.id}/')
        self.assertContains(seite, 'Revolut-Zahlungslink')
        self.assertContains(seite, 'Zahlungslink (Karte, Apple Pay, Google Pay)')
        self.sende(f'/shop-admin/orders/{bestellung.id}/', {'action': 'zahlungslink', 'zahlungslink': 'https://revolut.me/pay/abc'})
        bestellung.refresh_from_db()
        self.assertEqual(bestellung.zahlungslink, 'https://revolut.me/pay/abc')
        self.sende(f'/shop-admin/orders/{bestellung.id}/', {'action': 'zahlungslink', 'zahlungslink': 'kein link'})
        bestellung.refresh_from_db()
        self.assertEqual(bestellung.zahlungslink, 'https://revolut.me/pay/abc')
        self.mail.assert_not_called()

    # ── Seiten ───────────────────────────────────────────────────────────────────────────

    def test_kaufseite_und_stueckseite_zeigen_so_bezahlst_du(self):
        for pfad in (f'/bestellen/{self.shirt.slug}/', f'/produkt/{self.shirt.slug}/'):
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                for satz in ('So bezahlst du', 'Zahlungslink per E-Mail', 'innerhalb von 1 bis 2 Werktagen',
                             'Karte (Visa, Mastercard), Apple Pay, Google Pay oder Revolut Pay', 'Überweisung',
                             'Erst nach der Zahlung', 'Zahlungspflichtig bestellen', 'ohne Umsatzsteuer nach § 19 UStG'):
                    self.assertContains(antwort, satz)
                html = antwort.content.decode()
                self.assertNotRegex(html, r'Überweisungsauftrag|nach deiner Überweisung|Rechnung mit den Zahlungsdaten')
                self.assertNotIn('style="', html.split('<body', 1)[1].split('<form', 1)[1].split('</form>', 1)[0])

    def test_stueckseite_nennt_die_frist_ab_dem_tag_nach_der_zahlung(self):
        antwort = self.hole(f'/produkt/{self.shirt.slug}/')
        self.assertContains(antwort, 'ab dem Tag nach deiner Zahlung')
        self.assertNotContains(antwort, 'ab deiner Überweisung')

    def test_danke_seite_sagt_reserviert_und_zahlungslink(self):
        self.bestelle(self.shirt)
        antwort = self.hole('/bestellen/danke/')
        for satz in ('Deine Bestellung ist reserviert', 'Zahlungslink und Rechnung kommen separat innerhalb von 1 bis 2 Werktagen',
                     'kundin@example.org', 'für dich gemacht', 'ab dem Tag nach deiner Zahlung'):
            self.assertContains(antwort, satz)
        self.assertNotRegex(antwort.content.decode(), _ALT)

    def test_keine_oeffentliche_seite_widerspricht_dem_zahlungslink(self):
        pfade = ['/kontakt/', '/versand/', '/agb/', '/datenschutz/', '/ueber-uns/', '/produkte/', '/wissen/',
                 '/wissen/bestellen-und-bezahlen/', '/wissen/widerruf-und-ruecksendung/', '/llms.txt']
        gesehen = 0
        for pfad in pfade:
            antwort = self.hole(pfad)
            if antwort.status_code != 200:
                continue
            gesehen += 1
            text = re.sub(r'<[^>]+>', ' ', antwort.content.decode())
            with self.subTest(pfad=pfad):
                self.assertNotRegex(text, r'Überweisungsauftrag an das überweisende|nach deiner Überweisung|ab deiner Überweisung|'
                                          r'Rechnung mit den Zahlungsdaten|im Voraus per Überweisung nach|per PayPal oder Vorab')
        self.assertGreaterEqual(gesehen, 6)

    def test_agb_paragraphen_zahlung_und_lieferung(self):
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', self.hole('/agb/').content.decode()))
        for satz in ('persönlichen Zahlungslink von Revolut (Revolut Bank UAB, Litauen)',
                     'Karte (Visa, Mastercard), Apple Pay, Google Pay oder Revolut Pay',
                     'Alternativ kannst du den Betrag auf die Bankverbindung überweisen',
                     'Die Rechnung mit dem Zahlungslink schicken wir dir innerhalb von 1 bis 2 Werktagen per E-Mail',
                     'Die Frist beginnt am Tag nach deiner Zahlung (bei Überweisung gilt als Zahlung',
                     'Zahlungspflichtig bestellen'):
            self.assertIn(satz, text)
        self.assertNotIn('Weitere Zahlungsarten, etwa ein Zahlungslink, bieten wir derzeit nicht an', text)

    def test_datenschutz_nennt_revolut_mit_rechtsgrundlage(self):
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', self.hole('/datenschutz/').content.decode()))
        for satz in ('Zahlung mit Revolut-Zahlungslink', 'Revolut Bank UAB', 'Litauen', 'Art. 6 Abs. 1 lit. b DSGVO',
                     'Datenschutzhinweise von Revolut', 'Kreditkartendaten sehen und speichern wir nicht'):
            self.assertIn(satz, text)
        self.assertNotIn('Einen Zahlungsdienstleister binden wir derzeit nicht ein', text)

    def test_llms_txt_und_schema_nennen_den_zahlungslink(self):
        llms = re.sub(r'\s+', ' ', self.hole('/llms.txt').content.decode())
        self.assertIn('Zahlungsarten: Vorkasse über Revolut-Zahlungslink', llms)
        self.assertIn('Rechnung und Zahlungslink kommen innerhalb von 1 bis 2 Werktagen per E-Mail', llms)
        startseite = self.hole('/').content.decode()
        self.assertRegex(startseite, r'"paymentAccepted": "Zahlungslink \(Karte, Apple Pay, Google Pay oder Revolut Pay\), Banküberweisung"')

    def test_bestell_wissen_beitrag_beschreibt_den_zahlungslink(self):
        text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', self.hole('/wissen/bestellen-und-bezahlen/').content.decode()))
        for satz in ('persönlichen Zahlungslink von Revolut', 'innerhalb von 1 bis 2 Werktagen per E-Mail',
                     'ab dem Tag nach deiner Zahlung', 'Die Zahlungsdaten gibst du nur auf der Bezahlseite von Revolut ein'):
            self.assertIn(satz, text)

    def test_zahlart_im_django_admin_und_choices_bleiben_vollstaendig(self):
        werte = [wert for wert, _ in Order.PAYMENT_METHODS]
        self.assertEqual(werte, ['paypal', 'bank_transfer', 'zahlungslink', 'pickup'])
        from shop1.views.checkout import VORKASSE_ARTEN, ZAHLARTEN
        self.assertEqual(ZAHLARTEN, ('paypal', 'bank_transfer'))
        self.assertEqual(VORKASSE_ARTEN, ('bank_transfer', 'zahlungslink'))
