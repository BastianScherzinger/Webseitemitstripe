"""Zusagen der Datenmodule, auf die sich Views und Templates verlassen.

Zwei davon sind im Projekt bewusst so gebaut und würden bei einem
gutgemeinten Umbau als Erstes wegfallen: die Slug-Erzeugung in
``Produkt.save()`` und die Denormalisierung in ``CartItem``/``OrderItem``.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from ..models import Cart, CartItem, Order, OrderItem, Produkt, Subscriber
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt


class ProduktSlugTest(LuviqTestCase):
    """Der Slug ist die öffentliche Adresse eines Produkts."""

    def test_slug_entsteht_automatisch_aus_dem_namen(self):
        """Verhindert, dass ein im Admin angelegtes Produkt ohne Slug bleibt –
        seine Detailseite wäre dann nur über die alte ID-Adresse erreichbar."""
        produkt = erzeuge_produkt('Bemalte Jeansjacke XL')
        self.assertEqual(produkt.slug, 'bemalte-jeansjacke-xl')
        self.assertEqual(produkt.get_absolute_url(), '/produkt/bemalte-jeansjacke-xl/')

    def test_gleichnamige_produkte_bekommen_verschiedene_slugs(self):
        """Verhindert einen ``IntegrityError`` beim Anlegen des zweiten
        Produkts mit demselben Namen – ``slug`` ist ``unique``."""
        erstes = erzeuge_produkt('Custom Print Hoodie')
        zweites = erzeuge_produkt('Custom Print Hoodie')
        drittes = erzeuge_produkt('Custom Print Hoodie')
        self.assertEqual(erstes.slug, 'custom-print-hoodie')
        self.assertEqual(zweites.slug, 'custom-print-hoodie-1')
        self.assertEqual(drittes.slug, 'custom-print-hoodie-2')

    def test_slug_bleibt_beim_umbenennen_stehen(self):
        """Verhindert, dass eine Namenskorrektur im Admin die eingerichtete
        Produktadresse ändert und jeden bestehenden Link ins Leere schickt."""
        produkt = erzeuge_produkt('Bemalte Jacke')
        produkt.name = 'Bemalte Jacke – überarbeitet'
        produkt.save()
        self.assertEqual(produkt.slug, 'bemalte-jacke')

    def test_produkt_ohne_verwertbaren_namen_bekommt_trotzdem_einen_slug(self):
        """Verhindert einen leeren Slug – und damit die Adresse ``/produkt//``,
        die auf 404 läuft – bei Namen ganz ohne lateinische Buchstaben."""
        produkt = erzeuge_produkt('★★★')
        self.assertTrue(produkt.slug)
        self.assertEqual(self.hole(produkt.get_absolute_url()).status_code, 200)

    def test_zwei_produkte_koennen_sich_keinen_slug_teilen(self):
        """Verhindert, dass die Eindeutigkeit auf Datenbankebene verlorengeht;
        zwei Produkte auf einer Adresse hiesse, eines ist unerreichbar."""
        erzeuge_produkt('Erstes Teil', slug='festgelegt')
        with self.assertRaises(IntegrityError), transaction.atomic():
            erzeuge_produkt('Zweites Teil', slug='festgelegt')


class ProduktPflichtfelderTest(LuviqTestCase):
    """Keine leeren Pflichtfelder – sonst bricht die Anzeige."""

    def test_produkt_ohne_namen_wird_abgelehnt(self):
        """Verhindert einen namenlosen Eintrag in der Produktliste, der als
        leere Kachel ohne Beschriftung ausgeliefert würde."""
        with self.assertRaises(ValidationError):
            Produkt(name='', preis=Decimal('10.00')).full_clean()

    def test_produkt_ohne_preis_wird_abgelehnt(self):
        """Verhindert ein Produkt ohne Preis, das sich in den Warenkorb legen
        liesse und dort die Summenbildung mit einem Fehler abbrechen würde."""
        with self.assertRaises(ValidationError):
            Produkt(name='Ohne Preis').full_clean()

    def test_meta_angaben_bevorzugen_die_gepflegten_felder(self):
        """Verhindert, dass gepflegte SEO-Angaben von der automatischen
        Ersatzfassung überschrieben werden."""
        produkt = erzeuge_produkt(
            'Bemalte Jacke',
            seo_titel='Bemalte Jeansjacke aus Alsfeld kaufen',
            seo_beschreibung='Handbemaltes Einzelstück, versandfertig aus Alsfeld.',
        )
        self.assertEqual(produkt.meta_title, 'Bemalte Jeansjacke aus Alsfeld kaufen')
        self.assertEqual(
            produkt.meta_description,
            'Handbemaltes Einzelstück, versandfertig aus Alsfeld.',
        )

    def test_meta_angaben_haben_eine_ersatzfassung(self):
        """Verhindert einen leeren Titel oder eine leere Beschreibung bei
        Produkten, deren SEO-Felder nicht gepflegt sind."""
        produkt = erzeuge_produkt('Bemalte Jacke')
        self.assertIn('Bemalte Jacke', produkt.meta_title)
        self.assertTrue(produkt.meta_description.strip())

    def test_meta_beschreibung_bleibt_unter_der_anzeigegrenze(self):
        """Verhindert eine Beschreibung, die Google mitten im Satz abschneidet –
        die automatische Fassung hängt an eine lange Produktbeschreibung noch
        einen festen Nachsatz an."""
        produkt = erzeuge_produkt('Langtext', beschreibung='Wort ' * 200)
        self.assertLessEqual(len(produkt.meta_description), 230)


class DenormalisierungTest(LuviqTestCase):
    """``CartItem`` und ``OrderItem`` führen Name und Preis als eigene Felder.

    Das ist Absicht (siehe ``CLAUDE.md``): Bestellungen und Warenkörbe dürfen
    sich nicht rückwirkend ändern. Ein Umbau auf einen Fremdschlüssel würde
    genau diese Zusage brechen – die folgenden Tests schlagen dann an.
    """

    def setUp(self):
        self.benutzerin = erzeuge_benutzer('kundin')
        self.produkt = erzeuge_produkt('Bemalte Jacke', preis=Decimal('80.00'))

    def test_warenkorbposten_behaelt_seinen_preis_nach_einer_preisaenderung(self):
        """Verhindert, dass sich der Warenkorb einer Kundin still verteuert,
        während sie ihn offen hat."""
        korb = Cart.objects.create(user=self.benutzerin)
        posten = CartItem.objects.create(
            cart=korb, produkt_name=self.produkt.name,
            produkt_preis=self.produkt.preis, menge=2,
        )
        self.produkt.preis = Decimal('120.00')
        self.produkt.save()

        posten.refresh_from_db()
        self.assertEqual(posten.produkt_preis, Decimal('80.00'))
        self.assertEqual(posten.gesamt_preis, Decimal('160.00'))

    def test_bestellposten_ueberlebt_das_loeschen_des_produkts(self):
        """Verhindert, dass eine abgeschlossene Bestellung unlesbar wird, sobald
        die Betreiberin das verkaufte Einzelstück aus dem Shop nimmt – bei
        Einzelstücken ist das der Normalfall, nicht die Ausnahme."""
        bestellung = Order.objects.create(
            user=self.benutzerin, vorname='Erika', nachname='Musterfrau',
            email='erika@example.invalid', adresse='Grünberger Str. 16',
            stadt='Alsfeld', postleitzahl='36304', land='Deutschland',
            gesamt_betrag=Decimal('80.00'),
        )
        OrderItem.objects.create(
            order=bestellung, produkt_name=self.produkt.name,
            produkt_preis=self.produkt.preis, menge=1,
        )
        self.produkt.delete()

        posten = bestellung.items.get()
        self.assertEqual(posten.produkt_name, 'Bemalte Jacke')
        self.assertEqual(posten.produkt_preis, Decimal('80.00'))

    def test_warenkorb_summiert_menge_und_preis_seiner_posten(self):
        """Verhindert eine falsche Summe im Warenkorb – der Wert steht der
        Kundin direkt vor dem Bezahlen vor Augen."""
        korb = Cart.objects.create(user=self.benutzerin)
        CartItem.objects.create(cart=korb, produkt_name='A', produkt_preis=Decimal('10.00'), menge=3)
        CartItem.objects.create(cart=korb, produkt_name='B', produkt_preis=Decimal('5.50'), menge=2)
        self.assertEqual(korb.anzahl_items, 5)
        self.assertEqual(korb.gesamt_preis, Decimal('41.00'))

    def test_der_warenkorbzaehler_im_seitenkopf_zaehlt_mengen_mit_einer_abfrage(self):
        """Verhindert zweierlei am Zähler, der auf **jeder** Seite eines
        angemeldeten Nutzers mitläuft: dass er Zeilen statt Mengen zählt (zwei
        Posten mit 3 und 2 Stück müssen 5 ergeben, nicht 2) und dass er wieder
        auf mehrere Abfragen je Seitenaufruf anwächst – die Zählung war die
        teuerste ungecachte Abfrage im Kontextprozessor."""
        from django.test import RequestFactory

        from ..context_processors import shop_owner_check

        korb = Cart.objects.create(user=self.benutzerin)
        CartItem.objects.create(cart=korb, produkt_name='A', produkt_preis=Decimal('10.00'), menge=3)
        CartItem.objects.create(cart=korb, produkt_name='B', produkt_preis=Decimal('5.50'), menge=2)
        anfrage = RequestFactory().get('/shop-admin/')   # Pfad ohne Werbeabfrage
        anfrage.user = self.benutzerin
        with self.assertNumQueries(1):
            self.assertEqual(shop_owner_check(anfrage)['cart_count'], 5)

        # Ohne Warenkorb bleibt es bei 0 – kein None im Template.
        anfrage.user = erzeuge_benutzer('ohne-korb')
        self.assertEqual(shop_owner_check(anfrage)['cart_count'], 0)


class KennungenTest(LuviqTestCase):
    """Keine doppelten Kennungen dort, wo das Projekt Eindeutigkeit zusagt."""

    def test_eine_adresse_kann_sich_nur_einmal_anmelden(self):
        """Verhindert doppelte Newsletter-Zustellung an dieselbe Adresse."""
        Subscriber.objects.create(email='doppelt@example.invalid')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Subscriber.objects.create(email='doppelt@example.invalid')

    def test_eine_benutzerin_hat_hoechstens_einen_warenkorb(self):
        """Verhindert zwei parallele Warenkörbe pro Konto – die Kundin sähe je
        nach Einstiegspunkt einen anderen Inhalt."""
        benutzerin = erzeuge_benutzer('kundin')
        Cart.objects.create(user=benutzerin)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cart.objects.create(user=benutzerin)

    def test_eine_paypal_kennung_kann_nur_zu_einer_bestellung_gehoeren(self):
        """Verhindert, dass eine Zahlung zwei Bestellungen gutgeschrieben wird."""
        benutzerin = erzeuge_benutzer('kundin')
        felder = dict(
            user=benutzerin, vorname='Erika', nachname='Musterfrau',
            email='erika@example.invalid', adresse='Grünberger Str. 16',
            stadt='Alsfeld', postleitzahl='36304', land='Deutschland',
            gesamt_betrag=Decimal('80.00'), paypal_order_id='PAYPAL-1',
        )
        Order.objects.create(**felder)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(**felder)
