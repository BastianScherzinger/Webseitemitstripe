"""Der HTML-Teil der Newsletter-Mail (``emails/newsletter.html`` über ``shop1/utils.py::send_newsletter_email``).

Der Test zum Link steht in ``test_seo``; hier geht es um das, was beim
Umbau der langen Funktion nicht verloren gehen darf: Name maskiert, Bild nur
wenn vorhanden, Knopf je nach Verkaufsschalter, jede Abonnentin eine Mail.
"""

from unittest import mock

from django.test import override_settings

from ..models import Subscriber
from ..utils import send_newsletter_email
from ._basis import LuviqTestCase, erzeuge_produkt


class NewsletterHtmlTest(LuviqTestCase):

    def _html(self, produkt):
        with mock.patch('shop1.utils.send_brevo_email') as versand:
            send_newsletter_email(produkt, [Subscriber(email='a@example.invalid')])
        return versand.call_args.args[1]

    def test_der_name_steht_maskiert_im_html_und_im_alternativtext(self):
        html = self._html(erzeuge_produkt('Jacke <b>"Fuchs"</b> & Co'))
        self.assertNotIn('<b>', html)
        self.assertIn('Jacke &lt;b&gt;', html)

    def test_ohne_bild_gibt_es_keine_bildzeile(self):
        self.assertNotIn('<img', self._html(erzeuge_produkt('Jacke')))

    def test_link_und_knopf_stehen_drin(self):
        with override_settings(SITE_URL='https://www.luviq-alsfeld.com'):
            produkt = erzeuge_produkt('Jacke')
            html = self._html(produkt)
        self.assertIn('href="https://www.luviq-alsfeld.com' + produkt.get_absolute_url(), html)
        self.assertIn('Stück ansehen', html)
        self.assertNotIn('{', html)       # keine liegengebliebene Platzhalter-Klammer
        self.assertNotIn('€', html)

    def test_jede_abonnentin_bekommt_genau_eine_mail_mit_demselben_text(self):
        produkt = erzeuge_produkt('Bemalte Jacke')
        abos = [Subscriber(email='a@example.invalid'), Subscriber(email='b@example.invalid')]
        with mock.patch('shop1.utils.send_brevo_email') as versand:
            send_newsletter_email(produkt, abos)
        self.assertEqual([a.args[2] for a in versand.call_args_list], ['a@example.invalid', 'b@example.invalid'])
        self.assertEqual(len({a.args[1] for a in versand.call_args_list}), 1)
        self.assertIn('Bemalte Jacke', versand.call_args.args[0])

    def test_ohne_abonnenten_geht_nichts_raus(self):
        with mock.patch('shop1.utils.send_brevo_email') as versand:
            send_newsletter_email(erzeuge_produkt('Jacke'), [])
        versand.assert_not_called()

    @override_settings(VERKAUF_AKTIV=False)
    def test_der_knopf_nennt_ohne_verkauf_keinen_kauf(self):
        with mock.patch('shop1.utils.send_brevo_email') as versand:
            send_newsletter_email(erzeuge_produkt('Jacke'), [Subscriber(email='a@example.invalid')])
        self.assertIn('Stück ansehen', versand.call_args.args[1])
        self.assertNotIn('sichern', versand.call_args.args[1])

    @override_settings(VERKAUF_AKTIV=True)
    def test_mit_verkauf_steht_der_kaufaufruf_im_knopf(self):
        with mock.patch('shop1.utils.send_brevo_email') as versand:
            send_newsletter_email(erzeuge_produkt('Jacke'), [Subscriber(email='a@example.invalid')])
        self.assertIn('Jetzt sichern', versand.call_args.args[1])
