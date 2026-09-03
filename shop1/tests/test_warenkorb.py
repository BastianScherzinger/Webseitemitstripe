"""Der Warenkorb über seine Views – ``views/cart.py`` und der Sitzungsabgleich
``_sync_session_to_db`` in ``views/_helpers.py``.

``test_daten`` prüft die Denormalisierung von ``CartItem`` am Modell; hier
geht es um den Weg, den eine Kundin tatsächlich nimmt: hinzufügen, entfernen,
anmelden, ansehen. Jede Behauptung wird über die Adresse geprüft, die auch
das Template aufruft.
"""

from decimal import Decimal
from urllib.parse import quote

from django.test import Client

from ..models import Cart, CartItem, Produkt
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

PASSWORT = 'ein-langes-testpasswort'


class WarenkorbTest(LuviqTestCase):
    """Eine angemeldete Kundin und ein Produkt mit drei Einheiten."""

    def setUp(self):
        self.kundin = erzeuge_benutzer('kundin', PASSWORT)
        self.produkt = erzeuge_produkt('Bemalte Jacke', preis=Decimal('80.00'), lagerbestand=3)
        self.client.force_login(self.kundin)

    def hinzufuegen(self, produkt):
        return self.hole(f'/warenkorb/add/{produkt.id}/')

    def entfernen(self, name):
        return self.hole(f'/warenkorb/remove/{quote(name)}/')

    def posten(self):
        return CartItem.objects.filter(cart__user=self.kundin)

    def summe(self):
        antwort = self.hole('/warenkorb/')
        self.assertEqual(antwort.status_code, 200)
        return antwort.context['gesamt']

    def test_hinzufuegen_kopiert_preis_und_namen_statt_auf_das_produkt_zu_verweisen(self):
        """Verhindert, dass ein Umbau von ``CartItem`` auf einen Fremdschlüssel
        die Zusage bricht, dass ein Warenkorb nur das enthält, was die Kundin
        hineingelegt hat – Name und Preis stehen als eigene Werte im Posten,
        und es gibt kein Feld, das auf ``Produkt`` zeigt."""
        self.hinzufuegen(self.produkt)

        posten = self.posten().get()
        self.assertEqual(posten.produkt_name, 'Bemalte Jacke')
        self.assertEqual(posten.produkt_preis, Decimal('80.00'))
        self.assertEqual(posten.menge, 1)
        verweise = [
            feld.name for feld in CartItem._meta.get_fields()
            if feld.is_relation and feld.related_model is Produkt
        ]
        self.assertEqual(verweise, [], 'CartItem verweist auf Produkt – die Kopie wäre hinfällig')

    def test_eine_spaetere_preisaenderung_wirkt_nicht_rueckwirkend(self):
        """Verhindert, dass sich ein offener Warenkorb still verteuert, wenn
        die Betreiberin den Preis im Admin anhebt – die Kundin sähe beim
        Bezahlen eine andere Summe als beim Hineinlegen."""
        self.hinzufuegen(self.produkt)
        Produkt.objects.filter(pk=self.produkt.pk).update(preis=Decimal('120.00'))

        self.assertEqual(self.posten().get().produkt_preis, Decimal('80.00'))
        self.assertEqual(self.summe(), 80.0)

    def test_ein_geloeschtes_produkt_bricht_den_warenkorb_nicht(self):
        """Verhindert einen Serverfehler auf der Warenkorbseite, sobald ein
        Einzelstück aus dem Shop genommen wird, das noch in einem Warenkorb
        liegt – bei Einzelstücken der Normalfall, nicht die Ausnahme."""
        self.hinzufuegen(self.produkt)
        self.produkt.delete()

        antwort = self.hole('/warenkorb/')
        self.assertEqual(antwort.status_code, 200)
        self.assertContains(antwort, 'Bemalte Jacke')
        self.assertEqual(antwort.context['gesamt'], 80.0)

    def test_zweimal_hinzufuegen_erhoeht_die_menge_statt_einen_zweiten_posten_anzulegen(self):
        """Verhindert doppelte Zeilen für dasselbe Produkt – der Warenkorb
        zeigte es zweimal, und Entfernen träfe nur eine der beiden."""
        self.hinzufuegen(self.produkt)
        self.hinzufuegen(self.produkt)

        self.assertEqual(self.posten().count(), 1)
        self.assertEqual(self.posten().get().menge, 2)
        self.assertEqual(self.summe(), 160.0)

    def test_die_menge_bleibt_beim_lagerbestand_stehen_und_ausverkauftes_kommt_nicht_hinein(self):
        """Verhindert, dass mehr Einheiten in den Warenkorb wandern, als es
        gibt – bei einem Einzelstück hiesse das, zwei Kundinnen bezahlen
        dasselbe Teil."""
        for _ in range(5):
            self.hinzufuegen(self.produkt)
        self.assertEqual(self.posten().get().menge, 3)

        ausverkauft = erzeuge_produkt('Vergriffene Tasche', lagerbestand=0)
        antwort = self.hinzufuegen(ausverkauft)
        self.assertEqual(antwort.status_code, 302)
        self.assertFalse(self.posten().filter(produkt_name='Vergriffene Tasche').exists())

    def test_entfernen_nimmt_nur_diesen_posten_heraus_und_stimmt_die_summe(self):
        """Verhindert, dass nach dem Entfernen eines Postens die alte Summe
        stehen bleibt oder der falsche Posten verschwindet – der Betrag
        steht der Kundin direkt vor dem Bezahlen vor Augen."""
        tasche = erzeuge_produkt('Bemalte Tasche', preis=Decimal('25.50'))
        self.hinzufuegen(self.produkt)
        self.hinzufuegen(tasche)
        self.assertEqual(self.summe(), 105.5)

        antwort = self.entfernen('Bemalte Jacke')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(list(self.posten().values_list('produkt_name', flat=True)), ['Bemalte Tasche'])
        self.assertEqual(self.summe(), 25.5)

    def test_der_sitzungswarenkorb_wandert_beim_anmelden_in_die_datenbank_ohne_zu_verdoppeln(self):
        """Verhindert zwei Fehler beim Anmelden: dass der vor der Anmeldung
        gefüllte Sitzungswarenkorb verloren geht, und dass ein Posten, den
        es in der Datenbank schon gibt, als zweite Zeile angelegt statt in
        der Menge zusammengeführt wird. Eine zweite Anmeldung darf nichts
        mehr hinzufügen – die Sitzung muss nach dem Abgleich leer sein."""
        self.client.logout()
        korb = Cart.objects.create(user=self.kundin)
        CartItem.objects.create(cart=korb, produkt_name='Bemalte Jacke', produkt_preis=Decimal('80.00'), menge=1)

        sitzung = self.client.session
        sitzung['warenkorb'] = {
            '1': {'name': 'Bemalte Jacke', 'preis': '80.00', 'menge': 1, 'bild': ''},
            '2': {'name': 'Bemalte Tasche', 'preis': '25.50', 'menge': 2},
        }
        sitzung.save()

        antwort = self.sende('/login/', {'username': 'kundin', 'password': PASSWORT})
        self.assertEqual(antwort.status_code, 302)

        self.assertEqual(self.posten().count(), 2)
        self.assertEqual(self.posten().get(produkt_name='Bemalte Jacke').menge, 2)
        tasche = self.posten().get(produkt_name='Bemalte Tasche')
        self.assertEqual((tasche.menge, tasche.produkt_preis), (2, Decimal('25.50')))
        self.assertEqual(self.client.session.get('warenkorb'), {})

        self.client.logout()
        self.sende('/login/', {'username': 'kundin', 'password': PASSWORT})
        self.assertEqual(self.posten().count(), 2)
        self.assertEqual(self.posten().get(produkt_name='Bemalte Jacke').menge, 2)

    def test_fremde_warenkoerbe_sind_weder_sichtbar_noch_veraenderbar(self):
        """Verhindert, dass eine Kundin den Warenkorb einer anderen sieht oder
        per Entfernen-Adresse leert – der Warenkorb hängt am angemeldeten
        Konto, nicht an einer Kennung in der Adresse."""
        self.hinzufuegen(self.produkt)

        # Eigener Browser für die Nachbarin – sonst trüge die noch nicht
        # angezeigte Erfolgsmeldung der Kundin im Cookie den Produktnamen mit.
        nachbarin = erzeuge_benutzer('nachbarin')
        browser = Client()
        browser.force_login(nachbarin)
        antwort = browser.get('/warenkorb/', secure=True)
        self.assertEqual(antwort.status_code, 200)
        self.assertNotContains(antwort, 'Bemalte Jacke')
        self.assertEqual(antwort.context['gesamt'], 0)

        browser.get(f'/warenkorb/remove/{quote("Bemalte Jacke")}/', secure=True)
        self.assertEqual(self.posten().count(), 1)
        self.assertEqual(CartItem.objects.filter(cart__user=nachbarin).count(), 0)
