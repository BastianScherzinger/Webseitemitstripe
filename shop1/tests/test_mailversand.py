"""Gestaltete Mails und die Kopie an die Webagentur (``shop1/mails.py``, 26.09.2026).

Die Kopie an die Webagentur ist eine eigene, zusätzliche Mail. Geprüft wird,
dass sie bei echten Anfragen hinausgeht, bei Spam nicht, dass ihr Scheitern
nichts anderes mitreißt, dass sie abschaltbar ist und keine Dublette erzeugt,
und dass die HTML-Teile Eingaben maskieren. ``_basis`` ersetzt den Versand der
Kopie in jedem Test (``self.kopie_versand``); die Mail an Luisa wird hier
zusätzlich ersetzt.
"""

import os
from unittest import mock

from .. import mails, spamschutz
from ..models import KontaktAnfrage, Motivanfrage
from ._basis import LuviqTestCase

_KONTAKT = 'shop1.views.shop.send_brevo_email'
_MOTIV = 'shop1.views.motiv.send_brevo_email'

KONTAKT = {
    'name': 'Jürgen Übermut',
    'email': 'juergen@example.invalid',
    'betreff': 'Frage zur Größe',
    'nachricht': 'Hallo,\nhat die Jacke Größe M?\nGrüße',
}
MOTIV = {
    'richtung': 'tier',
    'teil': 'hoodie',
    'platzierung': 'ruecken',
    'bedeutung': 'Ein Drache für meinen Bruder.',
    'instagram': '@erika.muster',
    'email': 'erika@example.invalid',
}


class KopieBeiAnfragenTest(LuviqTestCase):

    def test_kontaktanfrage_geht_als_kopie_an_bastian(self):
        with mock.patch(_KONTAKT) as luisa, mock.patch.dict(os.environ, {'ADMIN_EMAIL': 'luisa@example.invalid'}):
            antwort = self.sende('/kontakt/', KONTAKT)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(luisa.call_count, 1)
        self.assertEqual(self.kopie_versand.call_count, 1)
        args, kwargs = self.kopie_versand.call_args
        betreff, html, empfaenger = args[0], args[1], args[2]
        self.assertTrue(betreff.startswith('[Luviq] Neue Kontaktanfrage – Jürgen Übermut'))
        self.assertEqual(empfaenger, mails.BETREIBER_VORGABE)
        self.assertEqual(kwargs['reply_to'], KONTAKT['email'])
        self.assertIn('Kopie für die Webagentur Scherzinger', html)
        self.assertIn('https://www.luviq-alsfeld.com/', html)
        anfrage = KontaktAnfrage.objects.get()
        self.assertIn(f'/kontaktanfrage/{anfrage.pk}/change/', html)
        self.assertIn('Kopie für die Webagentur Scherzinger', kwargs['text_content'])

    def test_motivanfrage_geht_als_kopie_an_bastian(self):
        with mock.patch(_MOTIV) as luisa:
            self.sende('/motiv-anfragen/', MOTIV)
        self.assertEqual(luisa.call_count, 1)
        self.assertEqual(self.kopie_versand.call_count, 1)
        args, kwargs = self.kopie_versand.call_args
        self.assertTrue(args[0].startswith('[Luviq] Neue Motivanfrage – @erika.muster'))
        self.assertEqual(kwargs['reply_to'], MOTIV['email'])
        self.assertIn(f'/motivanfrage/{Motivanfrage.objects.get().pk}/change/', args[1])

    def test_registrierung_geht_als_kopie_ohne_passwort(self):
        daten = {'username': 'neukundin', 'email': 'neu@example.invalid', 'first_name': 'Neu',
                 'last_name': 'Kundin', 'password1': 'ein-sehr-langes-passwort-42',
                 'password2': 'ein-sehr-langes-passwort-42'}
        with mock.patch('shop1.signals.send_brevo_email'):
            self.sende('/register/', daten)
        self.assertEqual(self.kopie_versand.call_count, 1)
        args, kwargs = self.kopie_versand.call_args
        self.assertTrue(args[0].startswith('[Luviq] Neue Registrierung – neukundin'))
        self.assertNotIn('ein-sehr-langes-passwort-42', args[1] + kwargs['text_content'])
        self.assertNotIn('/verify/', args[1] + kwargs['text_content'])


class KeineKopieTest(LuviqTestCase):

    def test_spam_im_kontaktformular_loest_keine_kopie_aus(self):
        with mock.patch(_KONTAKT) as luisa, self.assertLogs('shop1', level='WARNING'):
            self.sende('/kontakt/', dict(KONTAKT, **{spamschutz.FELD_FALLE: 'https://x.example'}))
        luisa.assert_not_called()
        self.kopie_versand.assert_not_called()

    def test_spam_in_der_motivanfrage_loest_keine_kopie_aus(self):
        with mock.patch(_MOTIV) as luisa, self.assertLogs('shop1', level='WARNING'):
            self.sende('/motiv-anfragen/', dict(MOTIV, **{spamschutz.FELD_FALLE: 'https://x.example'}))
        luisa.assert_not_called()
        self.kopie_versand.assert_not_called()

    def test_doppelklick_loest_nur_eine_kopie_aus(self):
        with mock.patch(_KONTAKT):
            self.sende('/kontakt/', KONTAKT)
            self.sende('/kontakt/', KONTAKT)
        self.assertEqual(self.kopie_versand.call_count, 1)

    def test_abschaltbar_ueber_leeren_wert(self):
        for wert in ('', 'aus'):
            with self.subTest(wert=wert), mock.patch(_KONTAKT) as luisa, \
                    mock.patch.dict(os.environ, {'BETREIBER_KOPIE_AN': wert}):
                self.kopie_versand.reset_mock()
                self.sende('/kontakt/', dict(KONTAKT, betreff=f'Test {wert!r}'))
                self.assertEqual(luisa.call_count, 1)
                self.kopie_versand.assert_not_called()

    def test_keine_dublette_wenn_bastian_schon_empfaenger_ist(self):
        with mock.patch(_KONTAKT) as luisa, \
                mock.patch.dict(os.environ, {'ADMIN_EMAIL': 'Bastian.Scherzinger05@Gmail.com'}):
            self.sende('/kontakt/', KONTAKT)
        self.assertEqual(luisa.call_count, 1)
        self.kopie_versand.assert_not_called()

    def test_mehrere_empfaenger_kommagetrennt(self):
        with mock.patch.dict(os.environ, {'BETREIBER_KOPIE_AN': 'a@example.invalid, B@example.invalid,a@example.invalid'}):
            self.assertEqual(mails.betreiber_empfaenger(schon=['b@example.invalid']), ['a@example.invalid'])


class KopieFehlerTest(LuviqTestCase):

    def test_scheiternde_kopie_bricht_weder_anfrage_noch_mail_an_luisa(self):
        self.kopie_versand.side_effect = RuntimeError('Brevo weg')
        with mock.patch(_KONTAKT) as luisa, self.assertLogs('shop1', level='ERROR'):
            antwort = self.sende('/kontakt/', KONTAKT)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(luisa.call_count, 1)
        self.assertTrue(KontaktAnfrage.objects.get().mail_gestartet)

    def test_scheiternde_kopie_bricht_die_motivanfrage_nicht(self):
        self.kopie_versand.side_effect = RuntimeError('Brevo weg')
        with mock.patch(_MOTIV) as luisa, self.assertLogs('shop1', level='ERROR'):
            antwort = self.sende('/motiv-anfragen/', MOTIV)
        self.assertRedirects(antwort, '/motiv-anfragen/danke/', fetch_redirect_response=False)
        self.assertEqual(luisa.call_count, 1)
        self.assertTrue(Motivanfrage.objects.get().mail_gestartet)

    def test_kaputte_vorlage_der_kopie_kostet_nichts(self):
        with mock.patch('shop1.mails.rendern', side_effect=RuntimeError('Vorlage')), \
                mock.patch(_KONTAKT) as luisa, self.assertLogs('shop1', level='ERROR'):
            antwort = self.sende('/kontakt/', KONTAKT)
        self.assertEqual(antwort.status_code, 302)
        # Mail an Luisa geht mit der Textfassung als HTML hinaus.
        self.assertEqual(luisa.call_count, 1)
        self.assertIn('<pre', luisa.call_args.args[1])
        self.kopie_versand.assert_not_called()


class HtmlTeilTest(LuviqTestCase):

    BOESE = dict(KONTAKT, name='<script>alert(1)</script>',
                 nachricht='<script>alert(2)</script>\n<b>fett</b>')

    def test_mail_an_luisa_hat_html_und_text_und_maskiert(self):
        with mock.patch(_KONTAKT) as luisa:
            self.sende('/kontakt/', self.BOESE)
        args, kwargs = luisa.call_args
        html, text = args[1], kwargs['text_content']
        self.assertIn('<!doctype html>', html)
        self.assertIn('lang="de"', html)
        self.assertIn('color-scheme', html)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;alert(2)&lt;/script&gt;<br>', html)
        self.assertIn('mailto:juergen@example.invalid', html)
        # Textteil wie bisher.
        self.assertIn('<script>alert(2)</script>', text)
        self.assertTrue(text.startswith('Neue Nachricht von'))
        self.assertEqual(args[0], 'Kontaktformular: Frage zur Größe')

    def test_kopie_maskiert_eingaben(self):
        with mock.patch(_KONTAKT):
            self.sende('/kontakt/', self.BOESE)
        html = self.kopie_versand.call_args.args[1]
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)

    def test_mail_an_luisa_zur_motivanfrage_maskiert(self):
        with mock.patch(_MOTIV) as luisa:
            self.sende('/motiv-anfragen/', dict(MOTIV, bedeutung='<script>x</script>'))
        html = luisa.call_args.args[1]
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;x&lt;/script&gt;', html)

    def test_besuchermails_ohne_preis_und_bestellwort(self):
        html = mails.rendern('besucher.html', titel='Bitte bestätige deine Anmeldung', kopf_label='Newsletter',
                             preheader='x', absaetze=['Absatz'], link='https://www.luviq-alsfeld.com/x',
                             knopf='Anmeldung bestätigen', nachsatz='')
        for wort in ('€', 'Bestellung', 'Kleinunternehmer', 'verkauft'):
            self.assertNotIn(wort, html)
        self.assertIn('Impressum', html)
