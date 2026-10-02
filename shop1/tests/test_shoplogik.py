"""Shop-Logik: Warenkorb, Bestellung, Zahlung, Konto, Newsletter, Zählung.

Gehört zu Paket L2-B6 („Luviq fertig“, 02.10.2026). Jeder Test hängt an einer
Kennung der Eigenen Punkte (``EIG…`` in ``doku/80-AUFGABEN.md``). Was nur bei
laufendem Verkauf erreichbar ist (Warenkorb, Checkout, PayPal), läuft mit
``@override_settings(VERKAUF_AKTIV=True)`` – ohne den Schalter leitet die
``VerkaufsschalterMiddleware`` jede Kaufroute um (``test_verkauf``).

Der Mailversand wird in jedem Test ersetzt; es geht nie eine Mail hinaus, und
PayPal wird nie angerufen (``requests`` im Modul ``checkout`` ist ersetzt).
"""

import importlib
import json
import os
import re
from datetime import timedelta
from decimal import Decimal
from io import StringIO
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import RequestFactory, override_settings
from django.utils import timezone

from .. import luviq_daten, newsletter
from ..models import (Cart, CartItem, Comment, Order, OrderItem, PageVisit, Produkt, Subscriber,
                      VisitorLog, Werbung)
from ..views._helpers import zu_viele_anfragen
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt
from .test_zahlung import LIEFERADRESSE, _PayPalAntwort, bezahlt

SCHNELLER_HASHER = override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
PASSWORT = 'ein-langes-testpasswort'
HANDY = ('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 '
         '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')

_MAIL = 'shop1.views.checkout.send_brevo_email'
_ANFRAGEN = 'shop1.views.checkout.requests'
_BANK = {'BANK_IBAN': 'DE00 0000 0000 0000 0000 00', 'BANK_INHABER': 'Luisa Brehler'}


def bestaetigte_kundin(name='kundin', rabatt=False):
    kundin = erzeuge_benutzer(name, PASSWORT)
    kundin.profile.email_verified = True
    kundin.profile.has_welcome_discount = rabatt
    kundin.profile.save()
    return kundin


# ═══ Warenkorb ═════════════════════════════════════════════════════════════

@SCHNELLER_HASHER
@override_settings(VERKAUF_AKTIV=True)
class WarenkorbKennungTest(LuviqTestCase):
    """EIG46, EIG112, EIG76, EIG47, EIG96, EIG85: der Posten hat eine eigene Kennung."""

    def setUp(self):
        self.kundin = bestaetigte_kundin()
        self.client.force_login(self.kundin)

    def posten(self):
        return CartItem.objects.filter(cart__user=self.kundin).order_by('id')

    def test_zwei_stuecke_mit_gleichem_namen_bleiben_zwei_posten(self):
        """EIG46/EIG112: der Warenkorb unterschied Stücke nur am Namen – wer zwei
        „Custom print hoodie“ anklickte, bekam einen Posten mit Menge 2 zum
        Preis des ersten."""
        erstes = erzeuge_produkt('Custom print hoodie', preis=Decimal('59.00'))
        zweites = erzeuge_produkt('Custom print hoodie', preis=Decimal('58.96'))
        self.sende(f'/warenkorb/add/{erstes.id}/')
        self.sende(f'/warenkorb/add/{zweites.id}/')

        posten = list(self.posten())
        self.assertEqual(len(posten), 2)
        self.assertEqual([(p.produkt_ref, p.produkt_preis, p.menge) for p in posten],
                         [(erstes.id, Decimal('59.00'), 1), (zweites.id, Decimal('58.96'), 1)])

    def test_ein_schraegstrich_im_namen_bricht_den_warenkorb_nicht(self):
        """EIG76: ``<str:produkt_name>`` passte nicht auf „/“, der Warenkorb
        antwortete mit 500 (``NoReverseMatch``). Die Adressen tragen jetzt die
        Kennung des Postens."""
        produkt = erzeuge_produkt('Hoodie 1/1', lagerbestand=3)
        self.sende(f'/warenkorb/add/{produkt.id}/')

        antwort = self.hole('/warenkorb/')
        self.assertEqual(antwort.status_code, 200)
        self.assertContains(antwort, 'Hoodie 1/1')
        posten = self.posten().get()
        antwort = self.sende(f'/warenkorb/update/{posten.id}/', {'menge': '2'})
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(self.posten().get().menge, 2)
        self.sende(f'/warenkorb/remove/{posten.id}/')
        self.assertEqual(self.posten().count(), 0)

    def test_ein_abgeschaltetes_oder_vergebenes_stueck_kommt_nicht_in_den_warenkorb(self):
        """EIG47/EIG115: ``add_to_cart`` prüfte nur den Bestand, nicht ``aktiv`` –
        ein nach dem Verkauf abgeschaltetes Stück blieb bestellbar. Ein
        Archivstück (``vergeben``) ist nie kaufbar, auch wenn es aktiv ist."""
        abgeschaltet = erzeuge_produkt('Abgeschaltete Jacke', aktiv=False)
        archiv = erzeuge_produkt('Archivstück', vergeben=True)
        frei = erzeuge_produkt('Freie Jacke')

        for produkt in (abgeschaltet, archiv):
            antwort = self.sende(f'/warenkorb/add/{produkt.id}/')
            self.assertEqual(antwort.status_code, 302)
        self.assertEqual(self.posten().count(), 0)

        self.sende(f'/warenkorb/add/{frei.id}/')
        self.assertEqual(self.posten().count(), 1)

    def test_ein_get_aufruf_veraendert_den_warenkorb_nicht(self):
        """EIG85: Hinzufügen und Entfernen liefen per GET – ein Bild-Tag auf einer
        fremden Seite genügte. Jetzt verändert ein GET nichts und führt zurück."""
        produkt = erzeuge_produkt('Bemalte Jacke', lagerbestand=3)
        self.hole(f'/warenkorb/add/{produkt.id}/')
        self.assertEqual(self.posten().count(), 0)

        self.sende(f'/warenkorb/add/{produkt.id}/')
        posten = self.posten().get()
        antwort = self.hole(f'/warenkorb/remove/{posten.id}/')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(self.posten().count(), 1)
        self.hole(f'/warenkorb/update/{posten.id}/?menge=3')
        self.assertEqual(self.posten().get().menge, 1)

    def test_ein_posten_aus_der_zeit_vor_der_kennung_wird_uebernommen(self):
        """Gegenprobe zur Migration: ein Posten ohne ``produkt_ref`` (Altbestand)
        wird beim erneuten Hinzufügen nicht verdoppelt, sondern bekommt die
        Kennung."""
        produkt = erzeuge_produkt('Bemalte Jacke', lagerbestand=3)
        korb = Cart.objects.create(user=self.kundin)
        CartItem.objects.create(cart=korb, produkt_name='Bemalte Jacke',
                                produkt_preis=produkt.preis, menge=1)

        self.sende(f'/warenkorb/add/{produkt.id}/')

        posten = self.posten().get()
        self.assertEqual((posten.menge, posten.produkt_ref), (2, produkt.id))

    def test_fehlt_das_stueck_waechst_die_menge_nicht(self):
        """EIG96: War ein Stück gelöscht oder umbenannt, übernahm ``update_cart``
        jede Menge ungeprüft – und der Checkout rechnete damit."""
        produkt = erzeuge_produkt('Bemalte Jacke', lagerbestand=3)
        self.sende(f'/warenkorb/add/{produkt.id}/')
        posten = self.posten().get()
        produkt.delete()

        self.sende(f'/warenkorb/update/{posten.id}/', {'menge': '50'})

        self.assertEqual(self.posten().get().menge, 1)

    def test_der_warenkorb_zeigt_formulare_mit_token_statt_links(self):
        """EIG85: das Entfernen ist ein ``<form method="post">`` mit CSRF-Token."""
        produkt = erzeuge_produkt('Bemalte Jacke', lagerbestand=3)
        self.sende(f'/warenkorb/add/{produkt.id}/')
        posten = self.posten().get()
        seite = self.hole('/warenkorb/').content.decode()
        self.assertNotIn(f'href="/warenkorb/remove/{posten.id}/"', seite)
        self.assertIn(f'action="/warenkorb/remove/{posten.id}/"', seite)
        self.assertIn('csrfmiddlewaretoken', seite)

    def test_die_produktseite_legt_per_formular_in_den_warenkorb(self):
        """EIG85: der Knopf „In den Warenkorb“ gehört zu einem POST-Formular;
        ein vergebenes Stück zeigt ihn gar nicht."""
        frei = erzeuge_produkt('Freie Jacke')
        archiv = erzeuge_produkt('Archivstück', vergeben=True)

        seite = self.hole(frei.get_absolute_url()).content.decode()
        self.assertIn('form="lv-in-den-warenkorb"', seite)
        self.assertIn(f'action="/warenkorb/add/{frei.id}/?next=warenkorb"', seite)
        self.assertNotIn(f'href="/warenkorb/add/{frei.id}/', seite)

        seite = self.hole(archiv.get_absolute_url()).content.decode()
        self.assertNotIn('In den Warenkorb', seite)
        self.assertIn('Bereits vergeben', seite)


# ═══ Bestellung ════════════════════════════════════════════════════════════

@SCHNELLER_HASHER
@override_settings(VERKAUF_AKTIV=True, PAYPAL_CLIENT_ID='test-client-id')
@mock.patch.dict(os.environ, {'PAYPAL_SECRET': 'test-secret', 'PAYPAL_MODE': 'sandbox'})
class BestellungTest(LuviqTestCase):
    """EIG47, EIG56, EIG75, EIG112, EIG114, EIG23, EIG16, EIG88, EIG15, EIG66, EIG08, EIG65."""

    def setUp(self):
        self.kundin = bestaetigte_kundin()
        self.client.force_login(self.kundin)

    def legen(self, produkt, menge=1):
        korb, _ = Cart.objects.get_or_create(user=self.kundin)
        CartItem.objects.create(cart=korb, produkt_name=produkt.name, produkt_ref=produkt.id,
                                produkt_preis=produkt.preis, menge=menge)

    def bestellen(self, **ueberschreiben):
        with mock.patch(_MAIL):
            return self.sende('/checkout/', {**LIEFERADRESSE, **ueberschreiben})

    # ── Prüfungen vor der Bestellung ─────────────────────────────────────

    def test_eine_unbestaetigte_adresse_darf_nicht_bestellen(self):
        """EIG56: die Bestätigungsmail der Registrierung war folgenlos – ein Konto
        mit einer fremden, nie bestätigten Adresse konnte bestellen. Die
        Bestellung geht an eine frei wählbare Adresse; ohne bestätigte Adresse
        des Kontos kommt man nicht zum Formular."""
        self.kundin.profile.email_verified = False
        self.kundin.profile.save()
        self.legen(erzeuge_produkt('Bemalte Jacke'))

        antwort = self.hole('/checkout/')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/profil/')
        antwort = self.bestellen()
        self.assertEqual(antwort['Location'], '/profil/')
        self.assertEqual(Order.objects.count(), 0)

    def test_ein_inzwischen_abgeschaltetes_stueck_blockiert_die_bestellung(self):
        """EIG47: ``checkout()`` prüfte weder ``aktiv`` noch den Bestand noch
        einmal. Ein Stück, das inzwischen verkauft oder abgeschaltet ist,
        führt zurück in den Warenkorb – ohne Bestellung."""
        produkt = erzeuge_produkt('Bemalte Jacke')
        self.legen(produkt)
        Produkt.objects.filter(pk=produkt.pk).update(aktiv=False)

        for aufruf in (self.hole('/checkout/'), self.bestellen()):
            self.assertEqual(aufruf.status_code, 302)
            self.assertEqual(aufruf['Location'], '/warenkorb/')
        self.assertEqual(Order.objects.count(), 0)

    def test_ein_vergebenes_archivstueck_laesst_sich_nicht_bestellen(self):
        """EIG115: der Verkaufsstart (``VERKAUF_AKTIV=1``) darf aktive Archivstücke
        nicht wieder kaufbar machen – ``vergeben`` sperrt sie auch dann, wenn
        sie aktiv sind und Bestand haben."""
        archiv = erzeuge_produkt('Archivstück')
        self.legen(archiv)
        Produkt.objects.filter(pk=archiv.pk).update(vergeben=True)

        antwort = self.bestellen()

        self.assertEqual(antwort['Location'], '/warenkorb/')
        self.assertEqual(Order.objects.count(), 0)

    def test_zu_lange_eingaben_werden_abgefangen_statt_mit_einem_datenbankfehler_zu_enden(self):
        """EIG75: ``telefon`` (20) und ``postleitzahl`` (10) gingen ungeprüft in
        ``Order``; PostgreSQL warf einen ``DataError``, SQLite – und damit die
        Tests – nie. Jetzt prüft der View die Längen der Spalten selbst."""
        self.legen(erzeuge_produkt('Bemalte Jacke'))
        for feld, wert in (('telefon', '1' * 21), ('postleitzahl', '3' * 11), ('vorname', 'A' * 101),
                           ('adresse', 'S' * 256), ('email', 'a' * 250 + '@example.invalid')):
            with self.subTest(feld=feld):
                antwort = self.bestellen(**{feld: wert})
                self.assertEqual(antwort['Location'], '/checkout/')
                self.assertEqual(Order.objects.count(), 0)

        antwort = self.bestellen(email='keine-adresse')
        self.assertEqual(antwort['Location'], '/checkout/')
        antwort = self.bestellen(payment_method='pickup')
        self.assertEqual(antwort['Location'], '/checkout/')
        self.assertEqual(Order.objects.count(), 0)

    def test_das_formular_begrenzt_die_felder_wie_die_spalten(self):
        """EIG75: ``maxlength`` im Formular entspricht der Spaltenlänge."""
        self.legen(erzeuge_produkt('Bemalte Jacke'))
        seite = self.hole('/checkout/').content.decode()
        for feld, grenze in (('telefon', 20), ('postleitzahl', 10), ('adresse', 255)):
            eingabe = re.search(rf'<input\b[^>]*\bname="{feld}"[^>]*>', seite)
            self.assertIsNotNone(eingabe, feld)
            self.assertRegex(eingabe.group(0), rf'\bmaxlength="{grenze}"')

    # ── Überweisung ──────────────────────────────────────────────────────

    def test_ohne_iban_gibt_es_keine_ueberweisung(self):
        """EIG114: ohne ``BANK_IBAN`` stand ein leeres Feld in der Bankdaten-Mail,
        und die Erfolgsseite meldete trotzdem „erfolgreich“. Jetzt wird die
        Zahlart gar nicht angenommen."""
        self.legen(erzeuge_produkt('Bemalte Jacke'))
        with mock.patch.dict(os.environ, {'BANK_IBAN': ''}):
            antwort = self.bestellen(payment_method='bank_transfer')
            seite = self.hole('/checkout/').content.decode()
        self.assertEqual(antwort['Location'], '/checkout/')
        self.assertEqual(Order.objects.count(), 0)
        self.assertNotIn('value="bank_transfer"', seite)

    def test_eine_ueberweisung_zeigt_die_bankdaten_auf_der_seite_und_leert_den_korb(self):
        """EIG114/EIG23: die Bankdaten stehen auch auf der Erfolgsseite (die Mail
        läuft asynchron und meldet Fehler nicht zurück); die Bestellung ist
        angelegt, der Warenkorb hat seine Aufgabe erfüllt."""
        produkt = erzeuge_produkt('Bemalte Jacke', preis=Decimal('80.00'))
        self.legen(produkt)
        with mock.patch.dict(os.environ, _BANK):
            antwort = self.bestellen(payment_method='bank_transfer')
            bestellung = Order.objects.get()
            seite = self.hole(antwort['Location'])

        self.assertEqual(antwort['Location'], f'/payment/success/{bestellung.id}/')
        self.assertEqual((bestellung.status, bestellung.payment_method), ('pending', 'bank_transfer'))
        self.assertContains(seite, 'DE00 0000 0000 0000 0000 00')
        self.assertContains(seite, f'Mission #{bestellung.id}')
        self.assertEqual(CartItem.objects.filter(cart__user=self.kundin).count(), 0)

    def test_das_setzen_auf_bezahlt_im_panel_bestaetigt_die_ueberweisung_und_schaltet_das_richtige_stueck_ab(self):
        """EIG66/EIG08/EIG15: die Bankdaten-Mail verspricht eine Bestätigung nach
        Zahlungseingang – gesendet wurde sie nie. Außerdem fand das Panel das
        Stück über den Namen: bei zwei gleichnamigen schaltete es das falsche
        ab. Und der Willkommensrabatt blieb nach einer Überweisung bestehen."""
        self.kundin.profile.has_welcome_discount = True
        self.kundin.profile.save()
        gekauft = erzeuge_produkt('Custom print hoodie', preis=Decimal('59.00'))
        anderes = erzeuge_produkt('Custom print hoodie', preis=Decimal('58.96'))
        self.legen(gekauft)
        with mock.patch.dict(os.environ, _BANK):
            self.bestellen(payment_method='bank_transfer')
        bestellung = Order.objects.get()
        self.assertEqual(bestellung.rabatt_betrag, Decimal('5.90'))
        self.assertEqual(bestellung.items.get().produkt_ref, gekauft.id)

        besitzerin = User.objects.create_superuser('shopbesitzer', 'shop@example.invalid', PASSWORT)
        self.client.force_login(besitzerin)
        with mock.patch(_MAIL) as mail:
            self.sende(f'/shop-admin/orders/{bestellung.id}/', {'action': 'update_status', 'status': 'paid'})

        bestellung.refresh_from_db()
        self.assertEqual(bestellung.status, 'paid')
        gekauft.refresh_from_db()
        anderes.refresh_from_db()
        self.assertEqual((gekauft.aktiv, gekauft.lagerbestand), (False, 0))
        self.assertEqual((anderes.aktiv, anderes.lagerbestand), (True, 1))
        self.kundin.profile.refresh_from_db()
        self.assertFalse(self.kundin.profile.has_welcome_discount)
        mail.assert_called_once()
        self.assertEqual(mail.call_args.args[2], LIEFERADRESSE['email'])
        self.assertIn('Bestellbestätigung', mail.call_args.args[0])

        # Ein zweites „bezahlt“ bucht nichts noch einmal ab und mailt nicht noch einmal.
        with mock.patch(_MAIL) as mail:
            self.sende(f'/shop-admin/orders/{bestellung.id}/', {'action': 'update_status', 'status': 'shipped'})
            self.sende(f'/shop-admin/orders/{bestellung.id}/', {'action': 'update_status', 'status': 'paid'})
        mail.assert_not_called()

    # ── Rabatt und Bestätigung ───────────────────────────────────────────

    def test_der_rabatt_steht_in_der_bestellung_und_in_der_bestaetigung(self):
        """EIG16/EIG88: ``Order`` hatte kein Rabattfeld, der Wert lebte nur in der
        Sitzung – die Mail listete Einzelpreise, deren Summe nicht zum Gesamtbetrag
        passte. Jetzt steht der Rabatt in der Bestellung und in der Mail."""
        from ..views.checkout import send_order_confirmation_email

        self.kundin.profile.has_welcome_discount = True
        self.kundin.profile.save()
        self.legen(erzeuge_produkt('Bemalte Jacke', preis=Decimal('80.00')))
        self.bestellen()
        bestellung = Order.objects.get()
        self.assertEqual((bestellung.gesamt_betrag, bestellung.rabatt_betrag),
                         (Decimal('72.00'), Decimal('8.00')))
        self.assertNotIn('order_rabatt', self.client.session)

        with mock.patch(_MAIL) as mail:
            send_order_confirmation_email(bestellung)
        html, text = mail.call_args.args[1], mail.call_args.kwargs['text_content']
        for inhalt in (html, text):
            self.assertIn('Zwischensumme: 80.00 €', inhalt)
            self.assertIn('Willkommensrabatt: -8.00 €', inhalt)
            self.assertIn('72.00 €', inhalt)

    def test_die_mails_geben_eingetippten_text_nicht_als_html_aus(self):
        """EIG65: Vorname, Adresse und Produktname standen unmaskiert im HTML der
        Mail, deren Empfänger frei wählbar ist – ein Konto konnte so Links in
        Mails vom Absender des Shops an Dritte schicken."""
        from ..views.checkout import send_bank_details_email, send_order_confirmation_email

        bestellung = Order.objects.create(
            user=self.kundin, vorname='<a href="https://boese.example/">Klick</a>', nachname='<b>N</b>',
            email='x@example.invalid', adresse='<img src=x onerror=alert(1)>', stadt='<i>S</i>',
            postleitzahl='1', land='<u>L</u>', gesamt_betrag=Decimal('10.00'))
        OrderItem.objects.create(order=bestellung, produkt_name='<script>x</script>',
                                 produkt_preis=Decimal('10.00'), menge=1)

        for versand in (send_order_confirmation_email, send_bank_details_email):
            with mock.patch(_MAIL) as mail, mock.patch.dict(os.environ, _BANK):
                versand(bestellung)
            html = mail.call_args.args[1]
            for roh in ('<a href="https://boese', '<script>x', '<img src=x', '<b>N</b>'):
                self.assertNotIn(roh, html, versand.__name__)
            self.assertIn('&lt;a href=', html, versand.__name__)

    # ── Erfolgsseite ─────────────────────────────────────────────────────

    def test_die_erfolgsseite_einer_offenen_paypal_bestellung_loescht_den_korb_nicht(self):
        """EIG54/EIG113: ``payment_success`` lud die Bestellung ohne Statusprüfung,
        leerte den Warenkorb und meldete eine verarbeitete Zahlung – auch nach
        einem Abbruch bei PayPal."""
        self.legen(erzeuge_produkt('Bemalte Jacke'))
        self.bestellen()
        bestellung = Order.objects.get()

        antwort = self.hole(f'/payment/success/{bestellung.id}/')

        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], f'/payment/{bestellung.id}/')
        self.assertEqual(CartItem.objects.filter(cart__user=self.kundin).count(), 1)

    def test_eine_erfolgsseite_aendert_nichts_auch_nicht_fuer_bezahlte_bestellungen(self):
        """EIG113: Die Erfolgsseite zeigt nur an. Den Warenkorb leert der Weg,
        der die Bestellung als bezahlt bucht (``paypal_capture``)."""
        produkt = erzeuge_produkt('Bemalte Jacke')
        self.legen(produkt)
        self.bestellen()
        bestellung = Order.objects.get()
        Order.objects.filter(pk=bestellung.pk).update(status='paid')

        antwort = self.hole(f'/payment/success/{bestellung.id}/')

        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(CartItem.objects.filter(cart__user=self.kundin).count(), 1)


# ═══ PayPal ════════════════════════════════════════════════════════════════

@SCHNELLER_HASHER
@override_settings(VERKAUF_AKTIV=True, PAYPAL_CLIENT_ID='test-client-id')
@mock.patch.dict(os.environ, {'PAYPAL_SECRET': 'test-secret', 'PAYPAL_MODE': 'sandbox'})
class PayPalServerseitigTest(LuviqTestCase):
    """EIG63: Anlegen und Einziehen der Zahlung macht der Server."""

    def setUp(self):
        self.kundin = bestaetigte_kundin()
        self.client.force_login(self.kundin)
        self.produkt = erzeuge_produkt('Bemalte Jacke', preis=Decimal('80.00'))
        self.bestellung = Order.objects.create(
            user=self.kundin, gesamt_betrag=Decimal('72.00'), rabatt_betrag=Decimal('8.00'),
            **{k: v for k, v in LIEFERADRESSE.items() if k != 'payment_method'})
        OrderItem.objects.create(order=self.bestellung, produkt_name='Bemalte Jacke',
                                 produkt_ref=self.produkt.id, produkt_preis=Decimal('80.00'), menge=1)

    def post(self, adresse, daten=None):
        return self.client.post(adresse, data=json.dumps(daten or {}), content_type='application/json',
                                secure=True)

    def test_der_betrag_der_paypal_bestellung_kommt_vom_server(self):
        """Vorher legte das Skript die PayPal-Bestellung im Browser an; der
        Betrag stammte aus dem Seitentext. Jetzt schickt der Server den Betrag
        der Bestellung aus der Datenbank."""
        with mock.patch(_ANFRAGEN) as anfragen:
            anfragen.post.side_effect = [_PayPalAntwort(200, {'access_token': 't'}),
                                         _PayPalAntwort(201, {'id': 'PAYPAL-NEU'})]
            antwort = self.post(f'/paypal/create/{self.bestellung.id}/')

        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json(), {'id': 'PAYPAL-NEU'})
        anlegen = anfragen.post.call_args_list[1]
        self.assertTrue(anlegen.args[0].endswith('/v2/checkout/orders'))
        einheit = anlegen.kwargs['json']['purchase_units'][0]
        self.assertEqual(einheit['amount'], {'currency_code': 'EUR', 'value': '72.00'})
        self.assertEqual(anlegen.kwargs['json']['intent'], 'CAPTURE')

    def test_anlegen_nur_fuer_die_eigene_offene_bestellung_und_nur_per_post(self):
        with mock.patch(_ANFRAGEN) as anfragen:
            self.assertEqual(self.hole(f'/paypal/create/{self.bestellung.id}/').status_code, 405)
            Order.objects.filter(pk=self.bestellung.pk).update(status='paid')
            self.assertEqual(self.post(f'/paypal/create/{self.bestellung.id}/').status_code, 400)
            Order.objects.filter(pk=self.bestellung.pk).update(status='pending')
            self.client.force_login(erzeuge_benutzer('nachbarin', PASSWORT))
            self.assertEqual(self.post(f'/paypal/create/{self.bestellung.id}/').status_code, 404)
        anfragen.post.assert_not_called()

    def test_anlegen_ohne_paypal_zugang_bucht_nichts_und_meldet_es(self):
        with mock.patch.dict(os.environ, {'PAYPAL_SECRET': ''}):
            antwort = self.post(f'/paypal/create/{self.bestellung.id}/')
        self.assertEqual(antwort.status_code, 502)
        self.assertIn('nichts abgebucht', antwort.json()['error'])

    def test_der_server_zieht_ein_bevor_er_prueft_und_bucht(self):
        """Vorher buchte der Browser ab (``actions.order.capture()``) und fragte
        den Server erst danach – scheiterte dessen Prüfung, war das Geld weg.
        Jetzt: Einzug auf dem Server, dann Prüfung, dann Buchung."""
        aufrufe = []

        def antwort_post(adresse, **kwargs):
            aufrufe.append(('post', adresse))
            if adresse.endswith('/oauth2/token'):
                return _PayPalAntwort(200, {'access_token': 't'})
            return _PayPalAntwort(201, {'status': 'COMPLETED'})

        def antwort_get(adresse, **kwargs):
            aufrufe.append(('get', adresse))
            return bezahlt('72.00')

        with mock.patch(_ANFRAGEN) as anfragen, mock.patch(_MAIL):
            anfragen.post.side_effect = antwort_post
            anfragen.get.side_effect = antwort_get
            antwort = self.post(f'/paypal/capture/{self.bestellung.id}/', {'paypal_order_id': 'PAYPAL-1'})

        self.assertEqual(antwort.status_code, 200, antwort.content)
        reihenfolge = [(art, adresse.rsplit('/', 1)[-1]) for art, adresse in aufrufe if 'oauth2' not in adresse]
        self.assertEqual(reihenfolge, [('post', 'capture'), ('get', 'PAYPAL-1')])
        self.bestellung.refresh_from_db()
        self.assertEqual((self.bestellung.status, self.bestellung.paypal_order_id), ('paid', 'PAYPAL-1'))
        self.produkt.refresh_from_db()
        self.assertEqual((self.produkt.aktiv, self.produkt.lagerbestand), (False, 0))

    def test_zwei_gleichzeitige_abschluesse_buchen_nur_einmal_ab(self):
        """Doppelklick oder zweiter Tab: beide Aufrufe haben die Bestellung noch als
        „offen" geladen. Der zweite sieht in der Datenbank den bezahlten Zustand,
        bucht weder Bestand noch Rabatt ein zweites Mal und meldet ``False`` –
        dann verschickt ``paypal_capture`` auch keine zweite Bestätigung."""
        from ..views.checkout import bestellung_abschliessen
        self.produkt.lagerbestand = 3
        self.produkt.save()
        OrderItem.objects.filter(order=self.bestellung).update(menge=2)
        erster = Order.objects.get(pk=self.bestellung.pk)
        zweiter = Order.objects.get(pk=self.bestellung.pk)

        self.assertTrue(bestellung_abschliessen(erster))
        self.assertFalse(bestellung_abschliessen(zweiter))

        self.produkt.refresh_from_db()
        self.assertEqual(self.produkt.lagerbestand, 1, 'zwei Stück einmal abgebucht, nicht viermal')
        self.assertEqual(Order.objects.get(pk=self.bestellung.pk).status, 'paid')

    def test_ein_abgelehnter_einzug_laesst_die_bestellung_offen(self):
        with mock.patch(_ANFRAGEN) as anfragen, mock.patch(_MAIL):
            def antwort_post(adresse, **kwargs):
                if adresse.endswith('/oauth2/token'):
                    return _PayPalAntwort(200, {'access_token': 't'})
                return _PayPalAntwort(422, {'name': 'INSTRUMENT_DECLINED'})
            anfragen.post.side_effect = antwort_post
            anfragen.get.return_value = _PayPalAntwort(200, {'status': 'APPROVED', 'purchase_units': []})
            antwort = self.post(f'/paypal/capture/{self.bestellung.id}/', {'paypal_order_id': 'PAYPAL-1'})

        self.assertEqual(antwort.status_code, 400)
        self.assertIn(f'#{self.bestellung.id}', antwort.json()['error'])
        self.bestellung.refresh_from_db()
        self.assertEqual(self.bestellung.status, 'pending')

    def test_eine_bezahlte_bestellung_leert_den_korb_der_kaeuferin(self):
        """EIG113: der Korb wird beim Buchen geleert, nicht beim Anzeigen."""
        korb = Cart.objects.create(user=self.kundin)
        CartItem.objects.create(cart=korb, produkt_name='Bemalte Jacke', produkt_ref=self.produkt.id,
                                produkt_preis=Decimal('80.00'), menge=1)
        with mock.patch(_ANFRAGEN) as anfragen, mock.patch(_MAIL):
            anfragen.post.return_value = _PayPalAntwort(200, {'access_token': 't'})
            anfragen.get.return_value = bezahlt('72.00')
            self.post(f'/paypal/capture/{self.bestellung.id}/', {'paypal_order_id': 'PAYPAL-1'})
        self.assertEqual(korb.items.count(), 0)


# ═══ Konto, Anmeldung ══════════════════════════════════════════════════════

@SCHNELLER_HASHER
class KontoTest(LuviqTestCase):
    """EIG45, EIG70."""

    def test_nach_dem_loeschen_des_kontos_bleibt_die_bestellung_erhalten(self):
        """EIG45: ``Order.user`` war CASCADE – mit dem Konto verschwanden bezahlte
        Bestellungen samt Posten, obwohl Belege aufbewahrt werden müssen
        (§ 257 HGB, § 147 AO). Jetzt SET_NULL: die Bestellung bleibt, nur die
        Verknüpfung zum Konto entfällt."""
        kundin = bestaetigte_kundin()
        bestellung = Order.objects.create(
            user=kundin, status='paid', gesamt_betrag=Decimal('80.00'),
            **{k: v for k, v in LIEFERADRESSE.items() if k != 'payment_method'})
        OrderItem.objects.create(order=bestellung, produkt_name='Bemalte Jacke',
                                 produkt_preis=Decimal('80.00'), menge=1)
        self.client.force_login(kundin)

        antwort = self.sende('/delete-account/')

        self.assertEqual(antwort.status_code, 302)
        self.assertFalse(User.objects.filter(username='kundin').exists())
        bestellung.refresh_from_db()
        self.assertIsNone(bestellung.user)
        self.assertEqual((bestellung.vorname, bestellung.gesamt_betrag), ('Erika', Decimal('80.00')))
        self.assertEqual(bestellung.items.count(), 1)
        self.assertIn('Konto gelöscht', str(bestellung))

    def test_die_anmeldung_fuehrt_zum_gewuenschten_ziel_aber_nie_auf_fremde_seiten(self):
        """EIG70: ``next`` wurde nirgends gelesen, jede Anmeldung endete auf der
        Startseite. Jetzt kommt die Kundin zum Stück zurück; fremde Ziele
        (offene Weiterleitung) fallen auf die Startseite."""
        erzeuge_benutzer('kundin', PASSWORT)
        daten = {'username': 'kundin', 'password': PASSWORT}

        antwort = self.sende('/login/?next=/produkt/bemalte-jacke/', daten)
        self.assertEqual(antwort['Location'], '/produkt/bemalte-jacke/')
        self.client.logout()

        for fremd in ('https://boese.example/', '//boese.example/', 'javascript:alert(1)'):
            with self.subTest(ziel=fremd):
                antwort = self.sende('/login/', {**daten, 'next': fremd})
                self.assertEqual(antwort['Location'], '/')
                self.client.logout()

    def test_der_gesperrte_warenkorb_leitet_nach_der_anmeldung_zurueck(self):
        """EIG70: ``@login_required`` hängt ``?next=`` an; die Anmeldung nimmt es auf."""
        erzeuge_benutzer('kundin', PASSWORT)
        with override_settings(VERKAUF_AKTIV=True):
            antwort = self.hole('/warenkorb/')
            self.assertEqual(antwort.status_code, 302)
            self.assertIn('next=/warenkorb/', antwort['Location'])
            antwort = self.sende(antwort['Location'], {'username': 'kundin', 'password': PASSWORT})
        self.assertEqual(antwort['Location'], '/warenkorb/')


# ═══ Archiv und Drop ═══════════════════════════════════════════════════════

class ArchivUndDropTest(LuviqTestCase):
    """EIG115, EIG123."""

    def test_die_migration_markiert_nur_die_stuecke_001_bis_005_als_vergeben(self):
        """EIG115: Daten­migration ``0026``. Nº 001–005 sind vergeben; ein Stück ab
        Nº 006 (etwa das vorab angelegte Drop-Stück) bleibt kaufbar."""
        from django.apps import apps
        migration = importlib.import_module('shop1.migrations.0026_archivstuecke_und_stueckkennung_nachtragen')
        archiv = [erzeuge_produkt(f'Archiv {n}', nummer=n) for n in range(1, 6)]
        drop = erzeuge_produkt('Neues Stück', nummer=6)
        zwei_gleiche = [erzeuge_produkt('Doppelt'), erzeuge_produkt('Doppelt')]
        einzeln = erzeuge_produkt('Einzigartig')
        korb = Cart.objects.create(user=erzeuge_benutzer('k'))
        eindeutig = CartItem.objects.create(cart=korb, produkt_name='Einzigartig', produkt_preis=Decimal('1'))
        mehrdeutig = CartItem.objects.create(cart=korb, produkt_name='Doppelt', produkt_preis=Decimal('1'))

        migration.nachtragen(apps, None)

        self.assertEqual([Produkt.objects.get(pk=p.pk).vergeben for p in archiv], [True] * 5)
        self.assertFalse(Produkt.objects.get(pk=drop.pk).vergeben)
        eindeutig.refresh_from_db()
        mehrdeutig.refresh_from_db()
        self.assertEqual(eindeutig.produkt_ref, einzeln.id)
        self.assertIsNone(mehrdeutig.produkt_ref, 'bei doppeltem Namen wird nicht geraten')
        self.assertTrue(all(p.pk for p in zwei_gleiche))

    def test_die_nummer_im_countdown_bleibt_beim_vorab_angelegten_stueck(self):
        """EIG123: ein vor dem Termin hochgeladenes Drop-Stück bekommt die nächste
        freie Nummer (006); der Countdown nannte danach „Nº 007“."""
        for n in range(1, 6):
            erzeuge_produkt(f'Archiv {n}', nummer=n, vergeben=True)
        self.assertEqual(luviq_daten.drop_nummer(), '006')

        erzeuge_produkt('Drop-Stück', aktiv=False)   # bekommt beim Speichern die Nummer 6

        self.assertEqual(luviq_daten.drop_nummer(), '006')
        with mock.patch.dict(os.environ, {'DROP_NUMMER': '9'}):
            self.assertEqual(luviq_daten.drop_nummer(), '009')


# ═══ Newsletter ════════════════════════════════════════════════════════════

class NewsletterAbmeldenTest(LuviqTestCase):
    """EIG17: Abmeldeweg."""

    def setUp(self):
        self.abo = Subscriber.objects.create(email='abo@example.invalid', bestaetigt=True)

    def test_ein_aufruf_zeigt_nur_die_seite_erst_der_klick_meldet_ab(self):
        token = newsletter.abmelde_token(self.abo.email)

        antwort = self.hole(f'/newsletter/abmelden/?t={token}')
        self.assertEqual(antwort.status_code, 200)
        self.assertContains(antwort, 'Jetzt abbestellen')
        self.assertIn('noindex', antwort.content.decode())
        self.assertTrue(Subscriber.objects.filter(pk=self.abo.pk).exists())

        antwort = self.sende('/newsletter/abmelden/', {'t': token})
        self.assertEqual(antwort.status_code, 302)
        self.assertFalse(Subscriber.objects.filter(pk=self.abo.pk).exists())

    def test_ein_ungueltiger_link_meldet_niemanden_ab(self):
        for t in ('', 'unsinn', newsletter.abmelde_token('andere@example.invalid') + 'x'):
            with self.subTest(token=t[:12]):
                self.assertEqual(self.hole(f'/newsletter/abmelden/?t={t}').status_code, 302)
                self.assertEqual(self.sende('/newsletter/abmelden/', {'t': t}).status_code, 302)
        self.assertTrue(Subscriber.objects.filter(pk=self.abo.pk).exists())

    def test_ein_bestaetigungstoken_taugt_nicht_zum_abmelden(self):
        """Gegenprobe: die beiden Links tragen eigene Salze und lassen sich nicht
        gegeneinander tauschen."""
        from django.core import signing
        fremd = signing.dumps({'e': self.abo.email}, salt='luviq-newsletter-optin')
        self.sende('/newsletter/abmelden/', {'t': fremd})
        self.assertTrue(Subscriber.objects.filter(pk=self.abo.pk).exists())

    def test_jeder_newsletter_traegt_den_abmeldelink_und_maskiert_den_namen(self):
        """EIG17: ``send_newsletter_email`` schickte ohne Abmeldelink. EIG65: der
        Produktname stand unmaskiert im HTML."""
        from ..utils import send_newsletter_email
        produkt = erzeuge_produkt('<b>Fett</b> Jacke')

        with mock.patch('shop1.utils.send_brevo_email') as mail:
            send_newsletter_email(produkt, [self.abo])

        html = mail.call_args.args[1]
        self.assertIn('/newsletter/abmelden/?t=', html)
        self.assertIn('Hier abmelden', html)
        self.assertNotIn('<b>Fett</b>', html)
        self.assertIn('/newsletter/abmelden/?t=', mail.call_args.kwargs['text_content'])
        token = html.split('/newsletter/abmelden/?t=')[1].split('"')[0].replace('&amp;', '&')
        self.assertEqual(newsletter.email_aus_token(token), self.abo.email)


# ═══ Zählung ═══════════════════════════════════════════════════════════════

class ZaehlungTest(LuviqTestCase):
    """EIG58, EIG105, EIG26, EIG51, EIG86."""

    def hole(self, pfad, **kwargs):
        kwargs.setdefault('HTTP_USER_AGENT', HANDY)
        return super().hole(pfad, **kwargs)

    def test_werbe_impressionen_zaehlen_keine_crawler(self):
        """EIG58: ``startseite()`` zählte jeden Aufruf – auch GPTBot, Googlebot und
        Prüfwerkzeuge."""
        werbung = Werbung.objects.create(titel='Probe', link='https://example.invalid/', budget=10)

        for bot in ('Mozilla/5.0 (compatible; Googlebot/2.1)', 'GPTBot/1.0', 'python-requests/2.32', ''):
            self.hole('/', HTTP_USER_AGENT=bot)
        werbung.refresh_from_db()
        self.assertEqual(werbung.impressionen, 0)

        self.hole('/')
        werbung.refresh_from_db()
        self.assertEqual(werbung.impressionen, 1)

    def test_die_besucherzaehlung_nimmt_die_adresse_des_proxys_nicht_die_frei_gesetzte(self):
        """EIG105: ``_get_ip`` nahm den **ersten** Eintrag von ``X-Forwarded-For`` –
        den kann der Absender frei setzen, ein Besucher zählte so beliebig oft.
        Gilt der letzte Eintrag (Adresse, die der Proxy sah), bleibt es einer."""
        self.hole('/', HTTP_X_FORWARDED_FOR='1.1.1.1, 9.9.9.9')
        self.hole('/', HTTP_X_FORWARDED_FOR='2.2.2.2, 9.9.9.9')
        self.assertEqual(PageVisit.objects.get().visits, 1)

        self.hole('/', HTTP_X_FORWARDED_FOR='1.1.1.1, 8.8.8.8')
        self.assertEqual(PageVisit.objects.get().visits, 2)

    def test_die_drosselung_verlaengert_ihr_zeitfenster_nicht(self):
        """EIG26: Kein Zeitfenster ist eins, wenn jeder Treffer die Ablaufzeit
        erneuert. ``zu_viele_anfragen`` legt den Zähler mit ``add`` an und zählt
        mit ``incr`` – beides lässt das Ende des Fensters, wo es ist."""
        import time as zeit
        anfrage = RequestFactory().get('/', REMOTE_ADDR='203.0.113.9')
        uhr = {'jetzt': 1_000_000.0}
        with mock.patch.object(zeit, 'time', side_effect=lambda: uhr['jetzt']):
            cache.clear()
            ergebnisse = []
            for wann in (0, 6, 7, 11):    # Fenster 10 s, Grenze 2
                uhr['jetzt'] = 1_000_000.0 + wann
                ergebnisse.append(zu_viele_anfragen(anfrage, 'zeitfenster', grenze=2, fenster=10))
        # 1., 2. Treffer erlaubt, 3. über der Grenze; nach Ablauf (t=10) beginnt
        # ein neues Fenster – würde jeder Treffer verlängern, wäre t=11 noch gesperrt.
        self.assertEqual(ergebnisse, [False, False, True, False])

    def test_der_befehl_loescht_ohne_frist_nichts_und_mit_frist_nur_alte_eintraege(self):
        """EIG51: das Besuchsprotokoll hatte weder Frist noch Löschroutine. Der Befehl
        braucht eine **ausdrückliche** Frist (Luisa und Bastian entscheiden;
        90 Tage sind nur der Vorschlag) und rührt Einträge anderer Seiten in der
        gemeinsamen pystore-Datenbank nicht an."""
        alt = timezone.now() - timedelta(days=100)
        eigener_alt = VisitorLog.objects.create(path='/alt/', seite='luviq')
        fremder_alt = VisitorLog.objects.create(path='/alt/', seite='pystore')
        jung = VisitorLog.objects.create(path='/jung/', seite='luviq')
        VisitorLog.objects.filter(pk__in=[eigener_alt.pk, fremder_alt.pk]).update(timestamp=alt)

        ausgabe = StringIO()
        with mock.patch.dict(os.environ, {'BESUCHER_AUFBEWAHRUNG_TAGE': '', 'SITE_NAME': 'luviq'}):
            call_command('besucher_aufraeumen', stdout=ausgabe)
            self.assertEqual(VisitorLog.objects.count(), 3)
            self.assertIn('90', ausgabe.getvalue())

            call_command('besucher_aufraeumen', '--tage', '90', '--trocken', stdout=StringIO())
            self.assertEqual(VisitorLog.objects.count(), 3)

            call_command('besucher_aufraeumen', '--tage', '90', stdout=StringIO())
        self.assertEqual(set(VisitorLog.objects.values_list('pk', flat=True)), {fremder_alt.pk, jung.pk})

    def test_ein_besuch_legt_keine_sitzung_und_kein_cookie_an(self):
        """EIG86: das 14-Tage-Sitzungs-Cookie allein für die Reichweitenmessung gibt
        es seit der cookielosen Zählung (18.09.2026) nicht mehr – hier als
        Gegenprobe über mehrere Seiten."""
        for pfad in ('/', '/produkte/', '/kontakt/'):
            antwort = self.hole(pfad)
            self.assertNotIn('sessionid', antwort.cookies, pfad)
