"""Der Zahlungspfad – ``views/checkout.py`` von der Bestellung bis zur
serverseitigen PayPal-Prüfung ``_verify_paypal_order``.

Der PayPal-Aufruf wird ersetzt (``requests`` im Modul ``checkout``), geprüft
wird die **Entscheidung** der Anwendung: Was tut sie mit dem, was PayPal
antwortet? Der wichtigste Test dieser Datei ist der erste – ein zu niedrig
bezahlter Betrag darf eine Bestellung nicht als bezahlt markieren.

Der Mailversand wird ebenfalls ersetzt: ``send_brevo_email`` startet einen
Thread mit einem HTTP-Aufruf.
"""

import json
import os
from decimal import Decimal
from unittest import mock

from django.test import override_settings

from ..models import Cart, CartItem, Order, Produkt
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

_ANFRAGEN = 'shop1.views.checkout.requests'
_MAIL = 'shop1.views.checkout.send_brevo_email'

LIEFERADRESSE = {
    'vorname': 'Erika',
    'nachname': 'Musterfrau',
    'email': 'erika@example.invalid',
    'adresse': 'Grünberger Str. 16',
    'stadt': 'Alsfeld',
    'postleitzahl': '36304',
    'land': 'Deutschland',
    'payment_method': 'paypal',
}


class _PayPalAntwort:
    """Nachbildung einer ``requests``-Antwort – nur, was ``checkout`` liest."""

    def __init__(self, status_code, daten):
        self.status_code = status_code
        self._daten = daten

    def json(self):
        return self._daten

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f'HTTP {self.status_code}')


def bezahlt(betrag, waehrung='EUR', status='COMPLETED', http_status=200):
    """Eine PayPal-Order-Antwort mit genau einer erfassten Zahlung."""
    return _PayPalAntwort(http_status, {
        'status': status,
        'purchase_units': [{
            'payments': {'captures': [{'amount': {'value': betrag, 'currency_code': waehrung}}]},
        }],
    })


@override_settings(PAYPAL_CLIENT_ID='test-client-id')
@mock.patch.dict(os.environ, {'PAYPAL_SECRET': 'test-secret', 'PAYPAL_MODE': 'sandbox'})
class ZahlungspfadTest(LuviqTestCase):
    """Eine Kundin, ein Einzelstück für 80 €, kein Willkommensrabatt.

    Der Rabatt (``UserProfile.has_welcome_discount``, Vorgabe ``True``) wird
    hier abgeschaltet, damit der Bestellbetrag dem Produktpreis entspricht
    und die Betragstests ohne Nebenrechnung lesbar bleiben; ein eigener Test
    prüft ihn.
    """

    def setUp(self):
        self.kundin = erzeuge_benutzer('kundin')
        self.kundin.profile.has_welcome_discount = False
        self.kundin.profile.save()
        self.produkt = erzeuge_produkt('Bemalte Jacke', preis=Decimal('80.00'), lagerbestand=1)
        self.client.force_login(self.kundin)

    # ── Helfer ────────────────────────────────────────────────────────────

    def in_den_warenkorb(self, produkt, menge=1):
        korb, _ = Cart.objects.get_or_create(user=self.kundin)
        CartItem.objects.create(
            cart=korb, produkt_name=produkt.name, produkt_preis=produkt.preis, menge=menge,
        )

    def bestellung_anlegen(self):
        """Bestellt den Warenkorb per ``/checkout/`` und gibt die Bestellung zurück."""
        antwort = self.sende('/checkout/', LIEFERADRESSE)
        self.assertEqual(antwort.status_code, 302)
        bestellung = Order.objects.get(user=self.kundin, status='pending')
        self.assertEqual(antwort['Location'], f'/payment/{bestellung.id}/')
        return bestellung

    def zahlung_melden(self, bestellung, paypal_kennung='PAYPAL-1', paypal_antwort=None):
        """Meldet eine PayPal-Zahlung wie das Skript auf der Bezahlseite und
        gibt (HTTP-Antwort, Nachbildung von ``requests``) zurück."""
        with mock.patch(_ANFRAGEN) as anfragen, mock.patch(_MAIL):
            anfragen.post.return_value = _PayPalAntwort(200, {'access_token': 'test-token'})
            anfragen.get.return_value = paypal_antwort or bezahlt('80.00')
            antwort = self.client.post(
                f'/paypal/capture/{bestellung.id}/',
                data=json.dumps({'paypal_order_id': paypal_kennung}),
                content_type='application/json',
                secure=True,
            )
        bestellung.refresh_from_db()
        return antwort, anfragen

    def assertUnbezahlt(self, antwort, bestellung):
        self.assertEqual(antwort.status_code, 400, antwort.content)
        self.assertEqual(bestellung.status, 'pending')
        self.assertIsNone(bestellung.paypal_order_id)
        self.produkt.refresh_from_db()
        self.assertEqual((self.produkt.lagerbestand, self.produkt.aktiv), (1, True))

    # ── Tests ─────────────────────────────────────────────────────────────

    def test_ein_zu_niedrig_bezahlter_betrag_wird_abgelehnt(self):
        """Verhindert den teuersten Fehler des Shops: eine Kundin bezahlt bei
        PayPal 1 € und meldet die Zahlung für eine 80-€-Bestellung – ohne
        den Betragsvergleich gälte sie als bezahlt, das Einzelstück würde
        verschickt. Die Kennung ist dabei echt und der PayPal-Status
        ``COMPLETED``; nur der Betrag stimmt nicht."""
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()
        self.assertEqual(bestellung.gesamt_betrag, Decimal('80.00'))

        antwort, _ = self.zahlung_melden(bestellung, paypal_antwort=bezahlt('1.00'))

        self.assertUnbezahlt(antwort, bestellung)
        self.assertIn('nicht verifiziert', antwort.json()['error'])

    def test_eine_zahlung_in_fremder_waehrung_wird_abgelehnt(self):
        """Verhindert, dass 80 in einer schwächeren Währung als 80 € gelten –
        nur Zahlungen in EUR zählen zum bezahlten Betrag."""
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()

        antwort, _ = self.zahlung_melden(bestellung, paypal_antwort=bezahlt('80.00', waehrung='USD'))

        self.assertUnbezahlt(antwort, bestellung)

    def test_eine_unbekannte_paypal_kennung_wird_abgelehnt(self):
        """Verhindert, dass eine ausgedachte Kennung genügt: PayPal kennt sie
        nicht (404), und die Bestellung bleibt unbezahlt."""
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()

        antwort, anfragen = self.zahlung_melden(
            bestellung, paypal_kennung='GIBT-ES-NICHT',
            paypal_antwort=_PayPalAntwort(404, {'name': 'RESOURCE_NOT_FOUND'}),
        )

        self.assertUnbezahlt(antwort, bestellung)
        abgefragt = anfragen.get.call_args.args[0]
        self.assertTrue(abgefragt.endswith('/v2/checkout/orders/GIBT-ES-NICHT'), abgefragt)
        self.assertIn('api-m.sandbox.paypal.com', abgefragt)

    def test_eine_nicht_abgeschlossene_zahlung_wird_abgelehnt(self):
        """Verhindert, dass eine bei PayPal nur angelegte, aber nie
        eingezogene Zahlung (Status ``CREATED``) als bezahlt zählt."""
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()

        antwort, _ = self.zahlung_melden(bestellung, paypal_antwort=bezahlt('80.00', status='CREATED'))

        self.assertUnbezahlt(antwort, bestellung)

    def test_checkout_legt_genau_eine_bestellung_an_und_kopiert_name_und_preis(self):
        """Verhindert doppelte Bestellungen aus einem Checkout und einen Umbau,
        bei dem ``OrderItem`` auf das Produkt verweist statt Name und Preis
        zu kopieren – eine Bestellung muss lesbar bleiben, auch wenn das
        Produkt später umbenannt, umgepreist oder gelöscht wird."""
        tasche = erzeuge_produkt('Bemalte Tasche', preis=Decimal('25.50'), lagerbestand=2)
        self.in_den_warenkorb(self.produkt)
        self.in_den_warenkorb(tasche, menge=2)

        bestellung = self.bestellung_anlegen()

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(bestellung.gesamt_betrag, Decimal('131.00'))
        posten = {p.produkt_name: (p.produkt_preis, p.menge) for p in bestellung.items.all()}
        self.assertEqual(posten, {
            'Bemalte Jacke': (Decimal('80.00'), 1),
            'Bemalte Tasche': (Decimal('25.50'), 2),
        })

        Produkt.objects.filter(pk=tasche.pk).update(preis=Decimal('99.00'), name='Umbenannt')
        self.produkt.delete()
        posten = {p.produkt_name: p.produkt_preis for p in bestellung.items.all()}
        self.assertEqual(posten, {'Bemalte Jacke': Decimal('80.00'), 'Bemalte Tasche': Decimal('25.50')})

    def test_eine_passende_zahlung_markiert_die_bestellung_und_bucht_den_bestand_ab(self):
        """Gegenprobe zu den Ablehnungen: ein zu scharfer Vergleich würde
        jede echte Zahlung abweisen. Stimmen Betrag, Währung und Status,
        wird die Bestellung bezahlt, das Einzelstück abgebucht und der
        Warenkorb nach der Erfolgsseite geleert."""
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()

        antwort, _ = self.zahlung_melden(bestellung, paypal_antwort=bezahlt('80.00'))

        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json(), {'status': 'success', 'redirect': f'/payment/success/{bestellung.id}/'})
        self.assertEqual((bestellung.status, bestellung.paypal_order_id), ('paid', 'PAYPAL-1'))
        self.produkt.refresh_from_db()
        self.assertEqual((self.produkt.lagerbestand, self.produkt.aktiv), (0, False))

        self.assertEqual(self.hole(f'/payment/success/{bestellung.id}/').status_code, 200)
        self.assertEqual(CartItem.objects.filter(cart__user=self.kundin).count(), 0)
        self.assertEqual(Order.objects.count(), 1)

    def test_dieselbe_paypal_kennung_erzeugt_keine_zweite_bezahlte_bestellung(self):
        """Verhindert, dass eine einmal bezahlte PayPal-Transaktion ein
        zweites Mal gutgeschrieben wird: weder für dieselbe Bestellung (der
        zweite Aufruf fragt PayPal nicht einmal mehr) noch für eine andere."""
        self.in_den_warenkorb(self.produkt)
        erste = self.bestellung_anlegen()
        antwort, _ = self.zahlung_melden(erste)
        self.assertEqual(antwort.status_code, 200)

        antwort, anfragen = self.zahlung_melden(erste)
        self.assertEqual(antwort.status_code, 200)
        anfragen.get.assert_not_called()
        self.assertEqual(Order.objects.filter(status='paid').count(), 1)

        tasche = erzeuge_produkt('Bemalte Tasche', preis=Decimal('80.00'))
        self.in_den_warenkorb(tasche)
        zweite = self.bestellung_anlegen()
        antwort, _ = self.zahlung_melden(zweite)   # wieder PAYPAL-1
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('bereits verwendet', antwort.json()['error'])
        self.assertEqual(zweite.status, 'pending')
        self.assertEqual(Order.objects.filter(status='paid').count(), 1)
        self.assertEqual(Order.objects.count(), 2)

    def test_ein_fehlgeschlagener_mailversand_laesst_die_bestellung_bestehen_und_steht_im_protokoll(self):
        """Verhindert, dass eine bezahlte Bestellung verloren geht, nur weil
        die Bestätigungsmail nicht rausgeht – und dass der Ausfall still
        bleibt: er muss im Protokoll ``shop1`` stehen (Schritt 3)."""
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()

        with mock.patch(_ANFRAGEN) as anfragen, \
             mock.patch(_MAIL, side_effect=RuntimeError('Brevo nicht erreichbar')), \
             self.assertLogs('shop1', level='ERROR') as protokoll:
            anfragen.post.return_value = _PayPalAntwort(200, {'access_token': 'test-token'})
            anfragen.get.return_value = bezahlt('80.00')
            antwort = self.client.post(
                f'/paypal/capture/{bestellung.id}/',
                data=json.dumps({'paypal_order_id': 'PAYPAL-1'}),
                content_type='application/json',
                secure=True,
            )

        self.assertEqual(antwort.status_code, 200, antwort.content)
        bestellung.refresh_from_db()
        self.assertEqual(bestellung.status, 'paid')
        eintraege = '\n'.join(protokoll.output)
        self.assertIn('Bestellbestätigung', eintraege)
        self.assertIn(str(bestellung.id), eintraege)
        self.assertIn('Brevo nicht erreichbar', eintraege)

    def test_eine_fremde_bestellung_laesst_sich_nicht_bezahlt_melden(self):
        """Verhindert, dass eine Kundin die Bestellung einer anderen als
        bezahlt markiert – die Bestellung gehört zum angemeldeten Konto."""
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()

        self.client.force_login(erzeuge_benutzer('nachbarin'))
        antwort, anfragen = self.zahlung_melden(bestellung)

        self.assertEqual(antwort.status_code, 404)
        anfragen.get.assert_not_called()
        self.assertEqual(bestellung.status, 'pending')

    def test_der_willkommensrabatt_senkt_den_betrag_einmal_und_erlischt_nach_der_zahlung(self):
        """Verhindert, dass der Willkommensrabatt bei jeder Bestellung neu
        greift: der Bestellbetrag ist um zehn Prozent niedriger, PayPal
        muss genau diesen Betrag ausweisen, danach ist der Rabatt weg."""
        self.kundin.profile.has_welcome_discount = True
        self.kundin.profile.save()
        self.in_den_warenkorb(self.produkt)
        bestellung = self.bestellung_anlegen()
        self.assertEqual(bestellung.gesamt_betrag, Decimal('72.00'))

        antwort, _ = self.zahlung_melden(bestellung, paypal_antwort=bezahlt('72.00'))

        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.kundin.profile.refresh_from_db()
        self.assertFalse(self.kundin.profile.has_welcome_discount)

    def test_checkout_und_zahlungsmeldung_verlangen_eine_anmeldung(self):
        """Verhindert, dass ein vergessener ``@login_required`` den Bestell-
        oder Zahlungsweg ohne Konto öffnet."""
        self.in_den_warenkorb(self.produkt)
        self.client.logout()

        antwort = self.hole('/checkout/')
        self.assertEqual(antwort.status_code, 302)
        self.assertIn('/login/', antwort['Location'])

        antwort = self.sende('/checkout/', LIEFERADRESSE)
        self.assertEqual(antwort.status_code, 302)
        self.assertIn('/login/', antwort['Location'])
        self.assertEqual(Order.objects.count(), 0)

        antwort = self.client.post(
            '/paypal/capture/1/', data=json.dumps({'paypal_order_id': 'PAYPAL-1'}),
            content_type='application/json', secure=True,
        )
        self.assertEqual(antwort.status_code, 302)
        self.assertIn('/login/', antwort['Location'])
