"""Rechtstexte, Datenschutz-Tatsachen und Mailvorlagen (Paket L2-B5, 02.10.2026).

Hält fest, was die Texte über den Code behaupten dürfen: Impressum nach § 5 DDG
mit klar benannter Anbieterin, Datenschutzerklärung mit Rechten, Beschwerderecht,
den tatsächlich gespeicherten und weitergegebenen Daten und festem Stand-Datum,
der Newsletter deutsch und im Look der übrigen Mails.
"""

import re
from unittest import mock

from django.test import override_settings

from ..models import Subscriber
from ._basis import LuviqTestCase, erzeuge_produkt


def _text(html):
    """Sichtbarer Text, Leerraum zusammengezogen."""
    html = re.sub(r'(?s)<(script|style).*?</\1>', ' ', html)
    return ' '.join(re.sub(r'<[^>]+>', ' ', html).split())


class ImpressumTest(LuviqTestCase):

    def test_anbieterin_ist_als_solche_ausgezeichnet(self):
        text = _text(self.hole('/impressum/').content.decode())
        self.assertIn('Anbieterin: Luisa Brehler', text)
        self.assertIn('Verantwortlich für den Inhalt: Luisa Brehler', text)
        self.assertIn('Grünberger Str. 16', text)

    def test_keine_aufgehobenen_normen_und_keine_os_plattform(self):
        html = self.hole('/impressum/').content.decode()
        self.assertIn('§ 5 DDG', html)
        for alt in ('TMG', 'MStV', 'RStV', 'ec.europa.eu/consumers/odr'):
            with self.subTest(alt=alt):
                self.assertNotIn(alt, html)

    def test_datenschutz_nennt_keine_aufgehobene_norm(self):
        html = self.hole('/datenschutz/').content.decode()
        for alt in ('TMG', 'TKG', 'RStV', 'Privacy Shield'):
            with self.subTest(alt=alt):
                self.assertNotIn(alt, html)


class DatenschutzTatsachenTest(LuviqTestCase):

    def setUp(self):
        self.text = _text(self.hole('/datenschutz/').content.decode())

    def test_rechte_nennen_widerspruch_und_beschwerde(self):
        for teil in ('Widerspruch', 'Art. 21 DSGVO', 'Aufsichtsbehörde',
                     'Hessische Beauftragte für Datenschutz', 'Einwilligung'):
            with self.subTest(teil=teil):
                self.assertIn(teil, self.text)

    def test_speicherung_und_weitergabe_der_anfragen_stehen_drin(self):
        for teil in ('speichern wir vor dem Versand in unserer Datenbank',
                     'Webagentur Scherzinger', 'Kopie',
                     'Eine feste Löschfrist gibt es'):
            with self.subTest(teil=teil):
                self.assertIn(teil, self.text)

    def test_datenbank_und_anmeldeprotokoll_sind_genannt(self):
        self.assertIn('Datenbank', self.text)
        self.assertIn('PostgreSQL', self.text)
        # django-axes speichert IP, Benutzername und Browserkennung in der Datenbank.
        self.assertIn('django-axes', self.text)
        self.assertNotIn('kurzzeitig im Arbeitsspeicher, etwa um wiederholte', self.text)

    def test_besucherzaehlung_ist_beschrieben(self):
        for teil in ('kein Cookie', 'keine IP-Adresse', 'Geräteklasse'):
            with self.subTest(teil=teil):
                self.assertIn(teil, self.text)

    def test_stand_ist_ein_festes_datum(self):
        html = self.hole('/datenschutz/').content.decode()
        self.assertRegex(html, r'Stand: \d{1,2}\. [A-Z][a-zä]+ 20\d\d')
        # Kein Vorlagen-Befehl, der die Seite bei jedem Abruf „aktuell“ datiert.
        quelle = open(
            __import__('os').path.join(
                __import__('os').path.dirname(__file__), '..', 'templates', 'shop1', 'legal',
                'datenschutz.html'), encoding='utf-8').read()
        self.assertNotIn('{% now', quelle)

    @override_settings(VERKAUF_AKTIV=False)
    def test_ohne_verkauf_gilt_paypal_nur_ab_eroeffnung(self):
        self.assertIn('Verarbeitung durch PayPal gilt erst ab Eröffnung des Shops', self.text)

    def test_formularhinweise_sagen_die_wahrheit(self):
        motiv = _text(self.hole('/motiv-anfragen/').content.decode())
        self.assertNotIn('nur für die Antwort', motiv)
        self.assertIn('Kopie an die Webagentur', motiv)
        kontakt = _text(self.hole('/kontakt/').content.decode())
        self.assertIn('Kopie erhält die Webagentur', kontakt)


class NewsletterMailTest(LuviqTestCase):

    def _mail(self):
        from ..utils import send_newsletter_email
        produkt = erzeuge_produkt('Bemalte Bomberjacke')
        with mock.patch('shop1.utils.send_brevo_email') as versand:
            send_newsletter_email(produkt, [Subscriber(email='leserin@example.invalid')])
        self.assertEqual(versand.call_count, 1)
        betreff, html, adresse = versand.call_args.args[:3]
        return produkt, betreff, html, adresse, versand.call_args.kwargs.get('text_content', '')

    def test_mail_ist_deutsch_und_im_aktuellen_look(self):
        produkt, betreff, html, adresse, text = self._mail()
        self.assertEqual(adresse, 'leserin@example.invalid')
        self.assertEqual(betreff, 'Neues Stück: Bemalte Bomberjacke')
        for alt in ('NEW DROP', 'New Drop', 'is online', '#ff6a00', 'border-radius: 40px',
                    'Cinematic', 'Fast-Fashion'):
            with self.subTest(alt=alt):
                self.assertNotIn(alt, html)
        self.assertIn('lang="de"', html)
        self.assertIn('#0A0A0A', html)  # Token der übrigen Mails (emails/basis.html)
        self.assertIn('ein neues Stück ist da', html)
        self.assertIn('Abmelden', html)
        self.assertIn('Impressum', html)
        self.assertIn('Abmelden', text)

    def test_link_fuehrt_auf_die_produktseite(self):
        produkt, _, html, _, text = self._mail()
        self.assertIn(produkt.get_absolute_url(), html)
        self.assertIn(produkt.get_absolute_url(), text)
        self.assertNotIn(f'/produkte/{produkt.id}/', html)

    @override_settings(VERKAUF_AKTIV=False)
    def test_ohne_verkauf_kein_preis_und_kein_kaufaufruf(self):
        _, _, html, _, text = self._mail()
        for alt in ('Jetzt sichern', '49,90', '49.90', '€', 'Warenkorb', 'bestellen'):
            with self.subTest(alt=alt):
                self.assertNotIn(alt, html)
                self.assertNotIn(alt, text)
        self.assertIn('Stück ansehen', html)

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_heisst_der_knopf_jetzt_sichern(self):
        _, _, html, _, _ = self._mail()
        self.assertIn('Jetzt sichern', html)


class AbsenderTest(LuviqTestCase):

    def test_ein_absendername_fuer_alle_mails(self):
        """EIG97: Brevo-Absender und Unterschriften nennen dieselbe Person und Marke."""
        import os
        import shop1.utils as utils
        quelle = open(utils.__file__, encoding='utf-8').read()
        self.assertIn('sender_name = "Luviq Universe"', quelle)
        self.assertNotIn('Luviq-Shop', quelle)
        basis = os.path.join(os.path.dirname(__file__), '..')
        for rel in ('views/checkout.py', 'templates/shop1/password_reset_email.html'):
            with self.subTest(datei=rel):
                text = open(os.path.join(basis, rel), encoding='utf-8').read()
                self.assertNotIn('Shop-Team', text)
                self.assertNotIn('Luviq-Shop', text)
                self.assertIn('Luisa Brehler', text)

    @override_settings(VERKAUF_AKTIV=True)
    def test_checkout_verlinkt_agb_und_datenschutz_am_abschluss(self):
        """EIG117: Rechtslinks direkt am zahlungspflichtigen Knopf (§ 312j Abs. 3 BGB)."""
        import os
        pfad = os.path.join(os.path.dirname(__file__), '..', 'templates', 'shop1', 'checkout.html')
        quelle = open(pfad, encoding='utf-8').read()
        knopf = quelle.index('Zahlungspflichtig bestellen')
        nach = quelle[knopf:]
        self.assertIn("{% url 'agb' %}", nach)
        self.assertIn("{% url 'datenschutz' %}", nach)
