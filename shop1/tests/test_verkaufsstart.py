"""Verkaufsstart nach der Gewerbeanmeldung (29.10.2026).

Das Gewerbe „LUVIQ" beginnt am 01.11.2026. Verkauft wird trotzdem erst, wenn
die Startliste grün ist (``shop1/startsperre.py``). Hier stehen:

* die Startsperre als Funktion (Datum, Generator-Texte, LUCID, Versandkosten,
  Widerrufsfunktion),
* der sichtbare Hinweis „Der Shop öffnet frühestens am 01.11.2026",
* die Ablagen für die Generator-Texte und die USt-IdNr. im Impressum,
* das Einwilligungs-Gerüst (aus = kein Banner, an = gleichwertiges Ablehnen,
  kein Fremdskript im HTML),
* die Fakten im Angebot mit Verkauf (gebraucht, § 19-Satz, GPSR-Angaben).
"""

from datetime import date
from decimal import Decimal
from pathlib import Path
import tempfile

from django.test import SimpleTestCase, override_settings

from .. import startsperre, verkauf
from ..context_processors import rechtstexte_vorhanden
from ._basis import LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

VOR_START = date(2026, 10, 29)
NACH_START = date(2026, 11, 2)
VOLL = {'LUCID_REGISTRIERNUMMER': 'DE1234567890123'}  # nur Testwert


def _ordner_mit(*namen):
    """Temporäre Generator-Ablage, in der die genannten Texte „eingefügt" sind."""
    ordner = Path(tempfile.mkdtemp())
    for name in ('impressum', 'datenschutz', 'agb', 'widerruf'):
        inhalt = '<p>Text aus dem Generator</p>' if name in namen else startsperre.PLATZHALTER
        (ordner / f'{name}.html').write_text(inhalt, encoding='utf-8')
    return ordner


class StartsperreTest(SimpleTestCase):

    def test_vor_dem_ersten_november_ist_der_verkauf_gesperrt(self):
        gruende = startsperre.sperrgruende(heute=VOR_START, umgebung={})
        self.assertTrue(any('01.11.2026' in g for g in gruende))

    def test_die_ablagen_im_code_sind_gefuellt(self):
        """Stand 30.10.: AGB, Widerrufsbelehrung und Datenschutz stehen in der Ablage; nach dem
        01.11. und mit LUCID-Nummer bleibt kein Sperrgrund – ohne Nummer bleibt der Shop zu."""
        for name in startsperre.PFLICHT_TEXTE:
            with self.subTest(text=name):
                self.assertFalse(startsperre.generator_text_fehlt(name))
        self.assertEqual(startsperre.sperrgruende(heute=NACH_START, umgebung=VOLL), [])
        ohne = startsperre.sperrgruende(heute=NACH_START, umgebung={})
        self.assertEqual(len(ohne), 1)
        self.assertIn('LUCID_REGISTRIERNUMMER', ohne[0])

    def test_jeder_pflichtpunkt_sperrt_fuer_sich(self):
        alle = _ordner_mit('agb', 'widerruf', 'datenschutz')
        gruende = startsperre.sperrgruende(heute=NACH_START, umgebung=VOLL, ordner=alle)
        # Runde 3: Versandkosten gebaut; 30.10.: Widerrufsfunktion gebaut – kein Code-Grund mehr.
        self.assertEqual(gruende, [])
        from unittest import mock
        with mock.patch.object(startsperre, 'WIDERRUFSFUNKTION_VORHANDEN', False):
            ohne_funktion = startsperre.sperrgruende(heute=NACH_START, umgebung=VOLL, ordner=alle)
        self.assertTrue(any('356a' in g for g in ohne_funktion))
        ohne_lucid = startsperre.sperrgruende(heute=NACH_START, umgebung={}, ordner=alle)
        self.assertTrue(any('LUCID' in g for g in ohne_lucid))
        ohne_agb = startsperre.sperrgruende(heute=NACH_START, umgebung=VOLL,
                                            ordner=_ordner_mit('widerruf', 'datenschutz'))
        self.assertTrue(any('agb.html' in g for g in ohne_agb))

    def test_alles_erfuellt_heisst_startbereit(self):
        alle = _ordner_mit('agb', 'widerruf', 'datenschutz')
        with self._code_fertig():
            self.assertEqual(
                startsperre.sperrgruende(heute=NACH_START, umgebung=VOLL, ordner=alle), [])

    def test_ein_leerer_text_zaehlt_nicht(self):
        ordner = _ordner_mit()
        (ordner / 'agb.html').write_text('   \n', encoding='utf-8')
        self.assertTrue(startsperre.generator_text_fehlt('agb', ordner))

    def test_die_einstellungen_halten_den_verkauf_im_testlauf_aus(self):
        from django.conf import settings
        self.assertFalse(settings.VERKAUF_AKTIV)
        self.assertTrue(settings.VERKAUF_SPERRGRUENDE)
        self.assertEqual(settings.VERKAUF_FRUEHESTENS, date(2026, 11, 1))

    @staticmethod
    def _code_fertig():
        from unittest import mock
        return mock.patch.multiple(startsperre, VERSANDKOSTEN_IM_BESTELLWEG=True,
                                   WIDERRUFSFUNKTION_VORHANDEN=True)


class OeffnungsSatzTest(SimpleTestCase):

    @override_settings(VERKAUF_AKTIV=False, VERKAUF_FRUEHESTENS=date(2026, 11, 1))
    def test_vor_dem_tag_nennt_der_satz_das_datum(self):
        self.assertEqual(verkauf.oeffnungs_satz(VOR_START),
                         'Der Shop öffnet frühestens am 01.11.2026.')

    @override_settings(VERKAUF_AKTIV=False, VERKAUF_FRUEHESTENS=date(2026, 11, 1))
    def test_nach_dem_tag_steht_kein_vergangenes_datum_da(self):
        satz = verkauf.oeffnungs_satz(NACH_START)
        self.assertNotIn('2026', satz)
        self.assertIn('noch nicht geöffnet', satz)

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_gibt_es_keinen_satz(self):
        self.assertEqual(verkauf.oeffnungs_satz(VOR_START), '')


@override_settings(VERKAUF_AKTIV=False, VERKAUF_FRUEHESTENS=date(2099, 11, 1))
class HinweisAufDenSeitenTest(LuviqTestCase):
    """Ohne Verkauf sagen Fuß, Impressum und AGB-Hinweis, ab wann frühestens."""

    SATZ = 'Der Shop öffnet frühestens am 01.11.2099.'

    def test_fuss_impressum_und_agb_nennen_den_tag(self):
        for pfad in ('/', '/impressum/', '/agb/'):
            with self.subTest(pfad=pfad):
                self.assertContains(self.hole(pfad), self.SATZ)

    def test_eine_abgefangene_kaufroute_nennt_den_tag(self):
        antwort = self.hole('/warenkorb/', follow=True)
        self.assertContains(antwort, self.SATZ)

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_steht_der_satz_nirgends(self):
        self.assertNotContains(self.hole('/'), 'Der Shop öffnet')


class ImpressumTest(LuviqTestCase):

    def test_ohne_ust_idnr_steht_wird_nachgereicht_da(self):
        """Ohne UST_IDNR sagt das Impressum ehrlich „wird nachgereicht“ (Leitung
        29.10.2026): keine Nummer, kein § 27a, vor allem keine Steuernummer."""
        antwort = self.hole('/impressum/')
        self.assertContains(antwort, 'Umsatzsteuer-Identifikationsnummer: wird nachgereicht.')
        self.assertNotContains(antwort, 'gemäß § 27a')
        self.assertNotContains(antwort, 'Steuernummer:')

    @override_settings(UST_IDNR='DE999999999')
    def test_gesetzte_ust_idnr_erscheint_mit_paragraph(self):
        antwort = self.hole('/impressum/')
        self.assertContains(antwort,
                            'Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz: DE999999999')
        self.assertNotContains(antwort, 'wird nachgereicht')

    def test_ladungsfaehige_anschrift_aus_luebeck_und_keine_alsfelder_strasse(self):
        html = self.hole('/impressum/').content.decode()
        self.assertIn('Mühlenkamp 5', html)
        self.assertIn('23569 Lübeck', html)
        for alt in ('Grünberger', '36304', '§ 5 TMG', 'ec.europa.eu/consumers/odr'):
            self.assertNotIn(alt, html)

    def test_die_ablagen_stand_30_10(self):
        """Seit 30.10.2026: AGB, Widerrufsbelehrung und Datenschutz gefüllt; das Impressum
        bleibt die bewährte Seite (keine eigene Ablage nötig)."""
        self.assertEqual(rechtstexte_vorhanden(),
                         {'impressum': False, 'datenschutz': True, 'agb': True, 'widerruf': True})


class EinwilligungTest(LuviqTestCase):

    def test_ohne_dienst_kein_banner_und_kein_skript(self):
        html = self.hole('/').content.decode()
        self.assertNotIn('lv-einwilligung', html)
        self.assertNotIn('einwilligung.js', html)
        self.assertNotIn('Cookie-Einstellungen', html)

    @override_settings(EINWILLIGUNG_DIENST='Testzähler',
                       EINWILLIGUNG_SKRIPT='https://zaehler.example.org/z.js')
    def test_mit_dienst_gleichwertiges_ablehnen_und_kein_vorab_laden(self):
        html = self.hole('/').content.decode()
        self.assertIn('id="lv-einwilligung"', html)
        ablehnen = '<button type="button" class="lv-einwilligung-knopf" data-einwilligung="nein">Ablehnen</button>'
        akzeptieren = '<button type="button" class="lv-einwilligung-knopf" data-einwilligung="ja">Akzeptieren</button>'
        self.assertIn(ablehnen, html)
        self.assertIn(akzeptieren, html)
        # Das Fremdskript steht nur als Adresse im Attribut, nie als <script src>.
        self.assertNotIn('<script src="https://zaehler.example.org', html)
        self.assertNotIn('src="https://zaehler.example.org', html)
        self.assertIn('data-skript="https://zaehler.example.org/z.js"', html)
        self.assertIn('Cookie-Einstellungen', html)


    @override_settings(EINWILLIGUNG_DIENST='Google Analytics',
                       EINWILLIGUNG_SKRIPT='https://www.googletagmanager.com/gtag/js?id=G-TEST1234',
                       GA_MESSUNG_ID='G-TEST1234')
    def test_google_analytics_nur_nach_einwilligung_und_in_der_datenschutzerklaerung(self):
        """Bastian 30.10.2026: GA4 für Luviq – gtag nie im HTML, nur als Adresse; die
        Datenschutzerklärung nennt den Dienst, sobald er eingestellt ist."""
        html = self.hole('/').content.decode()
        self.assertIn('data-ga="G-TEST1234"', html)
        self.assertNotIn('src="https://www.googletagmanager.com', html)
        self.assertNotIn("gtag('config'", html)
        self.assertIn('Google Analytics', self.hole('/datenschutz/').content.decode())

    def test_ohne_mess_id_kein_analytics_absatz(self):
        self.assertNotIn('id="ds-analytics"', self.hole('/datenschutz/').content.decode())

class AngebotMitVerkaufTest(LuviqTestCase):
    """Mit Verkauf: gebraucht, § 19-Satz statt „Endpreis", Herstellerangaben (GPSR)."""

    def setUp(self):
        self.produkt = erzeuge_produkt('Startstueck', preis=Decimal('60.00'), lagerbestand=1)

    def test_gebraucht_steht_immer_am_stueck(self):
        self.assertContains(self.hole(self.produkt.get_absolute_url()), 'Gebraucht (Second Hand)')

    @override_settings(VERKAUF_AKTIV=True)
    def test_preisangabe_und_herstellerangaben(self):
        html = self.hole(self.produkt.get_absolute_url()).content.decode()
        self.assertIn('Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.', html)
        # Runde 3: Versand im Preis enthalten, die Angabe steht am Preis (vorher „zuzüglich Versandkosten“).
        self.assertIn('inkl. Versand innerhalb Deutschlands', html)
        self.assertNotIn('Zuzüglich', html)
        self.assertNotIn('inkl. MwSt', html)
        self.assertIn('Herstellerin: Luisa Brehler', html)
        self.assertIn('Mühlenkamp 5, 23569 Lübeck', html)
        self.assertIn('Kennnummer Nº', html)
        self.assertIn('Pflege: Auf links bei 30 °C waschen', html)

    @override_settings(VERKAUF_AKTIV=False)
    def test_ohne_verkauf_keine_herstellerzeile(self):
        self.assertNotContains(self.hole(self.produkt.get_absolute_url()), 'Herstellerin:')

    @override_settings(VERKAUF_AKTIV=True)
    def test_kasse_zeigt_stueck_und_paragraph_19_vor_dem_bestellknopf(self):
        from ..models import Cart, CartItem
        kundin = erzeuge_benutzer('startkundin')
        kundin.profile.email_verified = True  # Bestellen verlangt sie (EIG56)
        kundin.profile.save()
        self.client.force_login(kundin)
        korb, _ = Cart.objects.get_or_create(user=kundin)
        CartItem.objects.create(cart=korb, produkt_name=self.produkt.name,
                                produkt_preis=self.produkt.preis, menge=1)
        antwort = self.hole('/checkout/')
        self.assertEqual(antwort.status_code, 200)
        html = antwort.content.decode()
        self.assertIn('Startstueck · Gebraucht (Second Hand), von Hand bemalt, 1-of-1', html)
        self.assertIn('Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.', html)
        self.assertIn('Zahlungspflichtig bestellen', html)
        self.assertNotIn('Verschlüsselung (Zahlungsart)', html)


class KeineAllgemeinenUmweltaussagenTest(LuviqTestCase):
    """UWG Anhang Nr. 4a (seit 27.09.2026): kein pauschales „nachhaltig" als Werbeaussage."""

    def test_weder_ohne_noch_mit_verkauf(self):
        erzeuge_produkt('Umweltstueck', preis=Decimal('40.00'))
        for an in (False, True):
            with self.subTest(verkauf=an), override_settings(VERKAUF_AKTIV=an):
                for pfad in ('/', '/produkte/', '/gaestebuch/', '/llms.txt'):
                    text = self.hole(pfad).content.decode().lower()
                    for wort in ('nachhaltige ', 'nachhaltig und', 'als nachhaltig gilt', 'nachhaltigem'):
                        self.assertNotIn(wort, text, f'{pfad}: {wort}')
