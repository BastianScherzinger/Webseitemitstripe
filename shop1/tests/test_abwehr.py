"""Missbrauchsschutz der Formulare und Formular-Reste (Paket L2-B3, 02.10.2026).

Geprüft werden die vier Bausteine, die die Agenturseite vorgemacht hat – nackte
Domain, fremde Domain mit dem eigenen Markennamen, Mail-Obergrenze, Prüfbefehl –
sowie die Newsletter-Formulare ohne JavaScript (EIG89, EIG129), der Rückruf nach dem
Mailversand (EIG10) und die kleinen Strukturkorrekturen (VL17, KV15, FO04).

Der Mailversand wird in jedem Test ersetzt (siehe ``test_formulare``).
"""

import re
import time
from io import StringIO
from unittest import mock

from django.core import signing
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from .. import spamschutz, utils
from ..models import KontaktAnfrage, Motivanfrage, Subscriber
from ._basis import OEFFENTLICHE_SEITEN, LuviqTestCase, erzeuge_benutzer, erzeuge_produkt

_KONTAKT = 'shop1.views.shop.send_brevo_email'
_MOTIV = 'shop1.views.motiv.send_brevo_email'
_NEWSLETTER = 'shop1.utils.send_brevo_email'

KONTAKT = {'name': 'Erika Musterfrau', 'email': 'erika@example.invalid',
           'betreff': 'Frage zu einer Jacke', 'nachricht': 'Gibt es die Jacke auch in M?'}
MOTIV = {'richtung': 'tier', 'teil': 'hoodie', 'platzierung': 'ruecken',
         'bedeutung': 'Ein Drache.', 'instagram': '@erika.muster', 'email': ''}


def _punkte(**felder):
    daten = {'name': 'Anna', 'email': 'anna@gmail.com', 'betreff': 'Frage', 'nachricht': 'Hallo Luisa'}
    daten.update(felder)
    daten.setdefault(spamschutz.FELD_ZEIT, signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ))
    return spamschutz.bewerte(daten)


class NackteDomainTest(LuviqTestCase):
    """Eine Adresse ohne ``http://`` zählte bis 02.10.2026 nichts."""

    def test_eine_nackte_domain_zaehlt_wie_ein_schwacher_link(self):
        punkte, gruende = _punkte(nachricht='Trag dich ein auf suchmaschine-eintrag.pro bitte')
        self.assertIn('nackte-domain', gruende)
        self.assertEqual(punkte, 1)

    def test_ein_link_mit_schema_zaehlt_nicht_zusaetzlich_als_nackte_domain(self):
        punkte, gruende = _punkte(nachricht='Schau auf https://beispiel.de/jacke')
        self.assertNotIn('nackte-domain', gruende)

    def test_eine_nackte_domain_allein_blockt_keinen_menschen(self):
        punkte, _ = _punkte(nachricht='So eine wie auf meinshop.de hätte ich gern')
        self.assertLess(punkte, spamschutz.SCHWELLE)


class MarkenimitationTest(LuviqTestCase):
    """Eine fremde Domain, die den Markennamen trägt, gibt es nur zum Täuschen."""

    def test_eine_nachahmer_domain_als_absender_blockt_allein(self):
        punkte, gruende = _punkte(email='domains@search-luviq-alsfeld.xyz')
        self.assertIn('markenimitation', gruende)
        self.assertGreaterEqual(punkte, spamschutz.SCHWELLE)

    def test_eine_nachahmer_domain_im_text_blockt_allein(self):
        punkte, gruende = _punkte(nachricht='Verlängern unter luviq-alsfeld-shop.pro')
        self.assertIn('markenimitation', gruende)
        self.assertGreaterEqual(punkte, spamschutz.SCHWELLE)

    def test_die_eigene_domain_und_ihre_unterdomains_sind_ausgenommen(self):
        for adresse in ('luisa@luviq-alsfeld.com', 'luisa@mail.luviq-alsfeld.com'):
            with self.subTest(adresse=adresse):
                _, gruende = _punkte(email=adresse, nachricht='Test von www.luviq-alsfeld.com')
                self.assertNotIn('markenimitation', gruende)

    def test_die_marke_ohne_domain_ist_kein_signal(self):
        _, gruende = _punkte(nachricht='Ich folge Luviq schon lange')
        self.assertNotIn('markenimitation', gruende)

    def test_weitere_eigene_domains_stehen_in_der_umgebung(self):
        with mock.patch.dict('os.environ', {'SPAM_EIGENE_DOMAINS': 'luviq.de, Luviq-Mode.com'}):
            self.assertIn('luviq.de', spamschutz.eigene_domains())
            _, gruende = _punkte(email='luisa@luviq-mode.com')
            self.assertNotIn('markenimitation', gruende)

    @override_settings(CANONICAL_HOST='www.luviq-neu.example')
    def test_der_kanonische_host_zaehlt_als_eigene_domain(self):
        self.assertIn('luviq-neu.example', spamschutz.eigene_domains())

    def test_die_markenimitation_verwirft_die_kontaktanfrage_still(self):
        with mock.patch(_KONTAKT) as versand:
            antwort = self.sende('/kontakt/', dict(KONTAKT, email='domains@search-luviq-alsfeld.xyz'))
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        versand.assert_not_called()
        self.assertEqual(KontaktAnfrage.objects.count(), 0)


class MailObergrenzeTest(LuviqTestCase):
    """Letzte Instanz: das Postfach läuft nicht über, die Anfrage geht nie verloren."""

    def test_nach_der_grenze_wird_keine_mail_mehr_freigegeben(self):
        ergebnisse = [spamschutz.mail_budget_ok('test', stunde=3, tag=100) for _ in range(5)]
        self.assertEqual(ergebnisse, [True, True, True, False, False])

    def test_auch_die_tagesgrenze_gilt(self):
        ergebnisse = [spamschutz.mail_budget_ok('test-tag', stunde=100, tag=2) for _ in range(4)]
        self.assertEqual(ergebnisse, [True, True, False, False])

    def test_die_formulare_haben_eigene_zaehler(self):
        spamschutz.mail_budget_ok('kontakt', stunde=1, tag=1)
        self.assertTrue(spamschutz.mail_budget_ok('motiv', stunde=1, tag=1))

    @override_settings(MAIL_OBERGRENZE_STUNDE=1)
    def test_ueber_der_grenze_steht_die_kontaktanfrage_gespeichert_ohne_mail(self):
        with mock.patch(_KONTAKT) as versand:
            self.sende('/kontakt/', KONTAKT)
            zweite = self.sende('/kontakt/', dict(KONTAKT, nachricht='Eine zweite, andere Frage'))
        self.assertRedirects(zweite, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(versand.call_count, 1)
        self.assertEqual(KontaktAnfrage.objects.count(), 2)
        self.assertEqual(self.kopie_versand.call_count, 1)
        self.assertFalse(KontaktAnfrage.objects.order_by('-id').first().mail_gestartet)

    @override_settings(MAIL_OBERGRENZE_STUNDE=1)
    def test_ueber_der_grenze_steht_die_motivanfrage_gespeichert_ohne_mail(self):
        with mock.patch(_MOTIV) as versand:
            self.sende('/motiv-anfragen/', MOTIV)
            zweite = self.sende('/motiv-anfragen/', dict(MOTIV, bedeutung='Etwas ganz anderes.'))
        self.assertRedirects(zweite, '/motiv-anfragen/danke/', fetch_redirect_response=False)
        self.assertEqual(versand.call_count, 1)
        self.assertEqual(Motivanfrage.objects.count(), 2)


class PruefbefehlTest(LuviqTestCase):

    def test_der_pruefbefehl_laeuft_gruen_und_nennt_beide_richtungen(self):
        ausgabe = StringIO()
        call_command('pruefe_abwehr', stdout=ausgabe)
        text = ausgabe.getvalue()
        self.assertIn('Bot:', text)
        self.assertIn('Mensch:', text)
        self.assertIn('Mail-Obergrenze', text)
        self.assertNotIn('FEHLER', text)

    def test_der_pruefbefehl_schlaegt_an_wenn_die_schwelle_zu_hoch_liegt(self):
        """Eine Abwehr, die nichts mehr blockt, muss der Befehl melden."""
        with mock.patch.object(spamschutz, 'SCHWELLE', 99):
            with self.assertRaises(CommandError):
                call_command('pruefe_abwehr', stdout=StringIO())

    def test_der_pruefbefehl_schlaegt_an_wenn_die_schwelle_zu_niedrig_liegt(self):
        """Und er meldet die Gegenrichtung: ein Mensch würde abgewiesen."""
        with mock.patch.object(spamschutz, 'SCHWELLE', 1):
            with self.assertRaises(CommandError) as fehler:
                call_command('pruefe_abwehr', stdout=StringIO())
        self.assertIn('Mensch', str(fehler.exception))


class NewsletterOhneSkriptTest(LuviqTestCase):
    """EIG89/EIG129: ohne JavaScript ging die Adresse per GET in die Adresszeile."""

    def test_beide_formulare_senden_per_post_an_die_anmeldung(self):
        html = self.hole('/').content.decode()
        formulare = re.findall(r'<form[^>]*data-newsletter[^>]*>', html)
        self.assertEqual(len(formulare), 2)
        for form in formulare:
            with self.subTest(form=form):
                self.assertIn('method="post"', form)
                self.assertIn('action="/newsletter/subscribe/"', form)

    def test_beide_formulare_tragen_csrf_falle_und_zeitstempel(self):
        html = self.hole('/').content.decode()
        self.assertEqual(html.count('name="csrfmiddlewaretoken"'), 2)
        self.assertEqual(html.count(f'name="{spamschutz.FELD_FALLE}"'), 2)
        self.assertEqual(html.count('<input type="hidden" name="formzeit"'), 2)

    def test_die_anmeldung_ohne_skript_leitet_mit_meldung_auf_die_warteliste(self):
        with mock.patch(_NEWSLETTER):
            antwort = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'},
                                 HTTP_ACCEPT='text/html,application/xhtml+xml')
        self.assertRedirects(antwort, '/#warteliste', fetch_redirect_response=False)
        self.assertEqual(Subscriber.objects.filter(email='neu@example.invalid').count(), 1)
        seite = self.hole('/').content.decode()
        self.assertIn('Fast geschafft', seite)

    def test_eine_ungueltige_adresse_ohne_skript_bekommt_eine_meldung_statt_json(self):
        antwort = self.sende('/newsletter/subscribe/', {'email': 'keine-adresse'},
                             HTTP_ACCEPT='text/html')
        self.assertRedirects(antwort, '/#warteliste', fetch_redirect_response=False)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_der_honigtopf_verwirft_still_mit_derselben_antwort(self):
        with mock.patch(_NEWSLETTER) as versand:
            antwort = self.sende('/newsletter/subscribe/',
                                 {'email': 'bot@example.invalid', spamschutz.FELD_FALLE: 'http://x.example'})
        self.assertEqual(antwort.status_code, 200)
        self.assertIn('Fast geschafft', antwort.json()['message'])
        self.assertNotIn('neu', antwort.json())
        self.assertEqual(Subscriber.objects.count(), 0)
        versand.assert_not_called()

    def test_die_falle_gilt_auch_im_json_pfad_des_skripts(self):
        antwort = self.client.post('/newsletter/subscribe/',
                                   '{"email": "bot@example.invalid", "website": "http://x.example"}',
                                   content_type='application/json', secure=True)
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_eine_nachahmer_adresse_wird_still_verworfen(self):
        antwort = self.sende('/newsletter/subscribe/', {'email': 'x@search-luviq-alsfeld.xyz'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_die_json_antwort_bleibt_fuer_das_skript_wie_vorher(self):
        antwort = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        self.assertEqual(antwort.status_code, 200)
        self.assertIs(antwort.json().get('neu'), True)

    def test_nach_der_obergrenze_geht_keine_bestaetigungsmail_mehr_hinaus(self):
        with mock.patch(_NEWSLETTER) as versand, \
                mock.patch.object(spamschutz, 'mail_budget_ok', return_value=False):
            antwort = self.sende('/newsletter/subscribe/', {'email': 'viele@example.invalid'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 1)
        versand.assert_not_called()

    def test_die_startseite_verspricht_keine_abmeldung_mit_einem_klick(self):
        """EIG121: eine Abmelde-Adresse gibt es nicht – der Text nennt den echten Weg."""
        html = self.hole('/').content.decode()
        self.assertNotIn('bmelden geht mit einem Klick', html)
        self.assertIn('abmelden: kurze Nachricht an brehlerluisa@gmail.com', html)


class MailRueckrufTest(LuviqTestCase):
    """EIG10: scheitert der Versand im Hintergrund, steht das an der Anfrage."""

    class _SofortThread:
        def __init__(self, target, **kwargs):
            self._target = target

        def start(self):
            self._target()

    def _senden(self, *, erfolg, **kwargs):
        with mock.patch.object(utils.threading, 'Thread', self._SofortThread), \
                mock.patch.object(utils, 'EmailMultiAlternatives') as mail, \
                self.settings(DEFAULT_FROM_EMAIL='x@example.invalid'), \
                mock.patch.dict('os.environ', {'BREVO_API_KEY': ''}):
            if erfolg:
                mail.return_value.send.return_value = 1
            else:
                mail.return_value.send.side_effect = OSError('SMTP down')
            utils.send_brevo_email('Betreff', '<p>x</p>', 'a@example.invalid', **kwargs)

    def test_der_rueckruf_bekommt_das_ergebnis(self):
        for erfolg in (True, False):
            with self.subTest(erfolg=erfolg):
                danach = mock.Mock()
                self._senden(erfolg=erfolg, danach=danach)
                danach.assert_called_once_with(erfolg)

    def test_ein_fehler_im_rueckruf_wirft_nicht(self):
        danach = mock.Mock(side_effect=RuntimeError('kaputt'))
        with self.assertLogs('shop1', level='ERROR'):
            self._senden(erfolg=True, danach=danach)

    def test_die_kontaktanfrage_gibt_den_rueckruf_mit(self):
        with mock.patch(_KONTAKT) as versand:
            self.sende('/kontakt/', KONTAKT)
        danach = versand.call_args.kwargs['danach']
        anfrage = KontaktAnfrage.objects.get()
        self.assertTrue(anfrage.mail_gestartet)
        danach(False)
        anfrage.refresh_from_db()
        self.assertFalse(anfrage.mail_gestartet)

    def test_die_motivanfrage_gibt_den_rueckruf_mit(self):
        with mock.patch(_MOTIV) as versand:
            self.sende('/motiv-anfragen/', MOTIV)
        danach = versand.call_args.kwargs['danach']
        danach(True)
        self.assertTrue(Motivanfrage.objects.get().mail_gestartet)
        danach(False)
        self.assertFalse(Motivanfrage.objects.get().mail_gestartet)


class FormularResteTest(LuviqTestCase):

    def test_die_registrierung_kennzeichnet_pflichtfelder_und_begrenzt_die_adresse(self):
        html = self.hole('/register/').content.decode()
        for label in ('Benutzername *', 'Email *', 'Vorname *', 'Nachname *'):
            with self.subTest(label=label):
                self.assertIn(label, html)
        self.assertIn('maxlength="254"', html)
        self.assertIn('autocomplete="new-password"', html)
        self.assertIn('Mit * markierte Felder sind Pflicht', html)

    def test_die_gaestebuch_formulare_sind_wie_der_server_auf_2000_zeichen_begrenzt(self):
        """``comment_add`` weist über 2000 Zeichen ab – das Formular sagt es vorher."""
        benutzer = erzeuge_benutzer()
        self.client.force_login(benutzer)
        for pfad in ('/kontakt/', '/gaestebuch/'):
            with self.subTest(pfad=pfad):
                html = self.hole(pfad).content.decode()
                self.assertRegex(html, r'<textarea[^>]*maxlength="2000"')

    def test_die_motivanfrage_kennzeichnet_die_drei_auswahlgruppen_als_pflicht(self):
        html = self.hole('/motiv-anfragen/').content.decode()
        legenden = re.findall(r'<legend>(.*?)</legend>', html, re.S)
        self.assertEqual(len(legenden), 3)
        for legende in legenden:
            with self.subTest(legende=legende):
                self.assertTrue(legende.rstrip().endswith('*'))
        self.assertIn('Mit * markierte Angaben sind Pflicht', html)

    def test_das_logo_auf_dem_gaestebuch_fuehrt_zur_startseite(self):
        html = self.hole('/gaestebuch/').content.decode()
        self.assertRegex(html, r'<a href="/" aria-label="Luviq Universe, zur Startseite"[^>]*>\s*<img[^>]*logo-luviq')


class UeberschriftenfolgeTest(LuviqTestCase):
    """VL17/BF15/IS14: keine Ebene wird übersprungen (h1 -> h3 war auf vier Seiten)."""

    def test_keine_oeffentliche_seite_ueberspringt_eine_ueberschriftenebene(self):
        erzeuge_produkt('Stueck')
        seiten = list(OEFFENTLICHE_SEITEN) + ['/impressum/', '/agb/', '/produkt/stueck/']
        for pfad in seiten:
            with self.subTest(pfad=pfad):
                antwort = self.hole(pfad)
                if antwort.status_code != 200:
                    continue
                ebenen = [int(e) for e in re.findall(r'<h([1-6])[\s>]', antwort.content.decode())]
                letzte = 0
                for ebene in ebenen:
                    if letzte:
                        self.assertLessEqual(ebene, letzte + 1, f'{pfad}: h{letzte} -> h{ebene}')
                    letzte = ebene

    def test_das_archiv_setzt_die_namen_der_karten_als_h2_die_startseite_als_h3(self):
        erzeuge_produkt('Stueck')
        archiv = self.hole('/produkte/').content.decode()
        self.assertRegex(archiv, r'<h2 class="lv-serif"><a href="/produkt/stueck/">')
        start = self.hole('/').content.decode()
        self.assertRegex(start, r'<h3 class="lv-serif"><a href="/produkt/stueck/">')
