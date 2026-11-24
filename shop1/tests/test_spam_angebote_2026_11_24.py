"""Spam-Abwehr und Absage an Dienstleistungs-Angebote (24.11.2026).

Anlass: Von 37 gespeicherten Kontaktnachrichten (17.09. bis 24.11.2026) war keine einzige eine
Kundenanfrage – 13 Preisfrage-Bots („Robertstady“), 12 Tastaturgeklapper mit Wegwerf-Adressen oder der
eigenen Domain, 9 Verkaufsschreiben von Agenturen (SEO, Video, Webdesign), 3 Tests von Bastian.
Die Punktwertung gab all diesen Einsendungen 0 bis 2 Punkte.

Geprüft wird in beide Richtungen: Bots landen als ``spam`` gespeichert und ohne Mail; Kundinnen
(kurz, englisch, mit Instagram-Link, mit Frage nach einem Video vom Stück) kommen wie bisher an Luisa;
Angebote bekommen genau eine Absage in ihrer Sprache und gehen nicht an Luisa.
"""

import time
from io import StringIO
from unittest import mock

from django.core import signing
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings

from .. import angebote, spamschutz
from ..management.commands.pruefe_abwehr import (ANGEBOTE, CREATOR_ANGEBOTE, ECHTE_ANGEBOTE, KEINE_ANGEBOTE,
                                                 KUNDINNEN_REGRESSION)
from ..models import KontaktAnfrage
from ._basis import LuviqTestCase

_LUISA = 'shop1.views.shop.send_brevo_email'
_ABSAGE = 'shop1.utils.send_brevo_email'
PROD = dict(CANONICAL_HOST='www.luviq-luebeck.com')


def _formular(**felder):
    """POST-Daten wie ein Browser mit JavaScript, der das Formular vor 60 Sekunden bekam."""
    daten = {'name': 'Jana Weber', 'email': 'jana@example.com', 'betreff': 'Frage',
             'nachricht': 'Ist Nº 006 noch frei?',
             spamschutz.FELD_ZEIT: signing.dumps(int(time.time()) - 60, salt=spamschutz._SALZ)}
    daten.update(felder)
    return daten


class _Basis(LuviqTestCase):

    def _senden(self, **felder):
        with mock.patch(_LUISA) as luisa, mock.patch(_ABSAGE) as absage:
            antwort = self.sende('/kontakt/', _formular(**felder))
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        return luisa, absage


@override_settings(**PROD)
class BotsTest(_Basis):

    def _ist_spam(self, **felder):
        luisa, absage = self._senden(**felder)
        luisa.assert_not_called()
        absage.assert_not_called()
        self.kopie_versand.assert_not_called()
        a = KontaktAnfrage.objects.get()
        self.assertEqual(a.einstufung, 'spam')
        self.assertIsNone(a.absage_am)
        return a

    def test_preisfrage_bot_wird_gespeichert_aber_nicht_gemailt(self):
        a = self._ist_spam(name='Robertstady', email='ninadvhegmannjfc33@gmail.com',
                           betreff='Hi    write about your the price for reseller',
                           nachricht='Sveiki, aš norėjau sužinoti jūsų kainą.')
        self.assertIn('preis-bot', a.einstufung_gruende)

    def test_preisfrage_bot_ohne_luecken_aber_mit_reseller(self):
        self._ist_spam(name='Robertstady', betreff='Hi, i writing about your the price for reseller',
                       nachricht='Hola, quería saber tu precio..')

    def test_zahlenmuster_mit_wegwerfadresse(self):
        a = self._ist_spam(name='NARTYTRYUT2173457NEWETREWT', email='abbey46901@belettersmail.com',
                           betreff='TOTUTYJ2173457TIRTYRTTR', nachricht='MERTYHRTHYHT2173457MARTHHDF')
        self.assertIn('zahlenmuster', a.einstufung_gruende)
        self.assertIn('wegwerf-mail', a.einstufung_gruende)

    def test_tastaturgeklapper_mit_der_eigenen_domain_im_produktivbetrieb(self):
        # Produktiv ist luviq-luebeck.com eine eigene Domain; die Markenimitation greift dort nicht –
        # das Kauderwelsch muss allein tragen.
        a = self._ist_spam(name='Michaelprove', email='ingeiiv7braun@mail.com',
                           betreff='Mnfuhfiejfuwduqwdhuwdwuhdu huwfqwuhfbqwihqwife',
                           nachricht='Jfeuwgduwefhw fuhefyugewfhqwyfuewu uwqduiqwhfqefhwduhwfe uwhidwdfefue '
                                     'luviq-luebeck.com')
        self.assertIn('kauderwelsch', a.einstufung_gruende)
        self.assertNotIn('markenimitation', a.einstufung_gruende)

    def test_honigtopf_wird_auch_gespeichert(self):
        self._ist_spam(**{spamschutz.FELD_FALLE: 'https://x.example'})

    def test_gleiche_einsendungen_werden_eine_zeile_auch_wenn_der_cache_leer_ist(self):
        """Am 23.11.2026 kamen vier gleiche Einsendungen in 2 Sekunden durch, weil der Merker im Cache
        je Gunicorn-Prozess gilt. Die Datenbankprüfung fängt das ab."""
        felder = dict(name='Michaelprove', email='ingeiiv7braun@mail.com', betreff='Mnfuhfiejfuwduqwdhuwdwuhdu',
                      nachricht='Jfeuwgduwefhw fuhefyugewfhqwyfuewu uwqduiqwhfqefhwduhwfe luviq-luebeck.com')
        for _ in range(4):
            cache.clear()
            self._senden(**felder)
        self.assertEqual(KontaktAnfrage.objects.count(), 1)


@override_settings(**PROD)
class MenschenTest(_Basis):
    """Was eine Kundin schreibt, kommt an – einstufung ``anfrage``, Mail an Luisa, Kopie an die Agentur."""

    def _kommt_an(self, **felder):
        luisa, absage = self._senden(**felder)
        luisa.assert_called_once()
        absage.assert_not_called()
        self.assertEqual(KontaktAnfrage.objects.get().einstufung, 'anfrage')

    def test_kurze_frage(self):
        self._kommt_an()

    def test_englisch_mit_instagram_link(self):
        self._kommt_an(name='Maya Stone', email='maya@example.com', betreff='Engel shirt',
                       nachricht='Hi! I found you on instagram (https://instagram.com/maya.stone). Is the engel '
                                 'shirt still available in size M and do you ship to Austria?')

    def test_ohne_zeitstempel_wie_ohne_javascript(self):
        daten = _formular()
        del daten[spamschutz.FELD_ZEIT]
        with mock.patch(_LUISA) as luisa:
            self.sende('/kontakt/', daten)
        luisa.assert_called_once()

    def test_frage_nach_einem_video_vom_stueck(self):
        self._kommt_an(betreff='Video vom Hoodie?',
                       nachricht='Hallo Luisa, kannst du mir ein kurzes Video oder Foto vom Hoodie schicken, damit '
                                 'ich die Farbe in echt sehen kann?')

    def test_preisfrage_ohne_die_luecken_der_vorlage(self):
        self._kommt_an(betreff='Preis für das Engel-Shirt', nachricht='Ich schreibe wegen des Preises vom Shirt.')

    def test_keine_kundin_der_beispielliste_gilt_als_angebot(self):
        for betreff, text in KEINE_ANGEBOTE + KUNDINNEN_REGRESSION:
            self.assertFalse(angebote.ist_angebot('', betreff, text), betreff)

    def test_jede_kundin_der_regressionsliste_kommt_ueber_das_formular_an_luisa(self):
        for name, text in KUNDINNEN_REGRESSION:
            cache.clear()
            KontaktAnfrage.objects.all().delete()
            luisa, absage = self._senden(betreff=name, nachricht=text)
            luisa.assert_called_once()
            absage.assert_not_called()
            self.assertEqual(KontaktAnfrage.objects.get().einstufung, 'anfrage', name)


@override_settings(**PROD)
class AngebotTest(_Basis):

    def _angebot(self, kuerzel, betreff, text, email='agentur@example.org'):
        luisa, absage = self._senden(name='Sam Agentur', email=email, betreff=betreff, nachricht=text)
        luisa.assert_not_called()
        # Kopie an die Webagentur zur Kontrolle der Einordnung – Luisa bekommt nichts.
        self.kopie_versand.assert_called_once()
        self.assertIn('[Angebot – automatisch abgesagt]', self.kopie_versand.call_args[0][0])
        self.kopie_versand.reset_mock()
        return absage

    def test_jede_sprache_bekommt_genau_eine_absage_in_ihrer_sprache(self):
        for i, (kuerzel, betreff, text) in enumerate(ANGEBOTE):
            cache.clear()
            absage = self._angebot(kuerzel, betreff, text, email=f'sender{i}@example.org')
            absage.assert_called_once()
            args, kwargs = absage.call_args
            erwartet_betreff, erwarteter_text = angebote.ABSAGEN[kuerzel]
            self.assertEqual(args[0], erwartet_betreff, kuerzel)
            self.assertEqual(args[2], f'sender{i}@example.org')
            self.assertEqual(kwargs['text_content'], erwarteter_text)
            self.assertTrue(kwargs['auto_antwort'])
            a = KontaktAnfrage.objects.get(email=f'sender{i}@example.org')
            self.assertEqual((a.einstufung, a.absage_sprache), ('angebot', kuerzel))
            self.assertIsNotNone(a.absage_am)

    def test_die_absage_enthaelt_weder_link_noch_text_des_absenders(self):
        for kuerzel, (betreff, text) in angebote.ABSAGEN.items():
            self.assertNotIn('http', text.lower(), kuerzel)
            self.assertNotIn('www.', text.lower(), kuerzel)
            self.assertNotIn('@', text, kuerzel)
            self.assertTrue(text.rstrip().endswith('Luviq'), kuerzel)
            self.assertNotIn('<a ', angebote.absage_html(text))

    def test_die_echten_verkaufsschreiben_und_der_creator_gegen_gratisstueck_werden_erkannt(self):
        for name, betreff, text in ECHTE_ANGEBOTE + CREATOR_ANGEBOTE:
            self.assertTrue(angebote.ist_angebot('', betreff, text), name)

    def test_kundenwoerter_allein_oder_zusammen_loesen_nie_ein_angebot_aus(self):
        for satz in ('Hi, send me a quote and your pricing, a proposal and your portfolio please, for the team.',
                     'Habt ihr eine Preisliste? Wir können 20 abnehmen, unser Team freut sich über ein Angebot.',
                     'I noticed your shop and came across your page, I make videos as a hobby, love your marketing.'):
            self.assertFalse(angebote.ist_angebot('', 'Frage', satz), satz)

    def test_alle_elf_sprachen_haben_eine_absage(self):
        self.assertEqual(set(angebote.ABSAGEN), {'de', 'en', 'fr', 'es', 'it', 'nl', 'pt', 'pl', 'tr', 'ru', 'uk'})

    def test_hoechstens_eine_absage_je_adresse_in_30_tagen(self):
        kuerzel, betreff, text = ANGEBOTE[1]
        erste = self._angebot(kuerzel, betreff, text)
        erste.assert_called_once()
        cache.clear()
        zweite = self._angebot(kuerzel, betreff + ' (nochmal)', text)
        zweite.assert_not_called()
        self.assertEqual(KontaktAnfrage.objects.filter(absage_am__isnull=False).count(), 1)
        self.assertEqual(KontaktAnfrage.objects.count(), 2)   # beide gespeichert, nur eine Absage

    def test_nach_der_pause_geht_wieder_eine_absage_raus(self):
        kuerzel, betreff, text = ANGEBOTE[1]
        self._angebot(kuerzel, betreff, text)
        from datetime import timedelta
        from django.utils import timezone
        KontaktAnfrage.objects.update(absage_am=timezone.now() - timedelta(days=31))
        cache.clear()
        self._angebot(kuerzel, betreff + ' (neu)', text).assert_called_once()

    @mock.patch.dict('os.environ', {'ABSAGE_TAGESGRENZE': '2'})
    def test_tagesgrenze(self):
        zahl = 0
        for i in range(4):
            cache.clear()
            kuerzel, betreff, text = ANGEBOTE[1]
            absage = self._angebot(kuerzel, betreff, text, email=f'tag{i}@example.org')
            zahl += absage.call_count
        self.assertEqual(zahl, 2)

    @mock.patch.dict('os.environ', {'ABSAGE_AKTIV': 'aus'})
    def test_schalter_aus_stuft_nur_ein(self):
        kuerzel, betreff, text = ANGEBOTE[1]
        self._angebot(kuerzel, betreff, text).assert_not_called()
        self.assertEqual(KontaktAnfrage.objects.get().einstufung, 'angebot')

    def test_keine_absage_ohne_zeitstempel_an_wegwerfadresse_oder_noreply(self):
        kuerzel, betreff, text = ANGEBOTE[1]
        for email in ('x@mailinator.com', 'noreply@firma.example', 'no-reply@firma.example',
                      'info@luviq-luebeck.com'):
            cache.clear()
            self._angebot(kuerzel, betreff, text, email=email).assert_not_called()
        # ohne Zeitstempel: kein Browser mit Formular, also kein Absender, dem man antwortet
        cache.clear()
        daten = _formular(name='Sam', email='agentur@example.org', betreff=betreff, nachricht=text)
        del daten[spamschutz.FELD_ZEIT]
        with mock.patch(_LUISA) as luisa, mock.patch(_ABSAGE) as absage:
            self.sende('/kontakt/', daten)
        luisa.assert_not_called()
        absage.assert_not_called()

    def test_keine_absage_bei_linkflut_im_angebot(self):
        kuerzel, betreff, text = ANGEBOTE[1]
        absage = self._angebot(kuerzel, betreff, text + ' https://a.example https://b.example https://c.example')
        absage.assert_not_called()

    def test_ein_versandfehler_wirft_nie(self):
        kuerzel, betreff, text = ANGEBOTE[1]
        with mock.patch(_LUISA), mock.patch(_ABSAGE, side_effect=RuntimeError('SMTP weg')):
            antwort = self.sende('/kontakt/', _formular(name='Sam', email='agentur@example.org',
                                                        betreff=betreff, nachricht=text))
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(KontaktAnfrage.objects.get().einstufung, 'angebot')


class SpracheTest(LuviqTestCase):

    def test_rueckfall_ist_englisch(self):
        self.assertEqual(angebote.sprache(''), 'en')
        self.assertEqual(angebote.sprache('qwertz'), 'en')
        self.assertEqual(angebote.sprache('你好 我们提供视频服务'), 'en')

    def test_ukrainisch_und_russisch_werden_getrennt(self):
        self.assertEqual(angebote.sprache('Ми пропонуємо відео та рекламу'), 'uk')
        self.assertEqual(angebote.sprache('Мы предлагаем видео и рекламу'), 'ru')


class PruefbefehlNeuTest(LuviqTestCase):

    def test_der_befehl_nennt_die_neuen_faelle_und_laeuft_gruen(self):
        ausgabe = StringIO()
        call_command('pruefe_abwehr', stdout=ausgabe)
        text = ausgabe.getvalue()
        self.assertIn('Preisfrage-Vorlage', text)
        self.assertIn('Angebot (uk)', text)
        self.assertIn('Mensch: „Video vom Hoodie?“', text)
        self.assertNotIn('FEHLER', text)


class AufraeumenTest(LuviqTestCase):
    """``spam_aufraeumen``: nur mit Frist, nur Spam und Angebote, nie echte Anfragen."""

    def _zeilen(self):
        from datetime import timedelta
        from django.utils import timezone
        alt = timezone.now() - timedelta(days=100)
        for art in ('anfrage', 'angebot', 'spam'):
            for _ in range(2):
                a = KontaktAnfrage.objects.create(name='x', email='x@example.org', betreff=art, nachricht='n',
                                                  einstufung=art)
                KontaktAnfrage.objects.filter(pk=a.pk).update(erstellt_am=alt)
        KontaktAnfrage.objects.create(name='neu', email='n@example.org', betreff='neu', nachricht='n',
                                      einstufung='spam')

    def test_ohne_frist_wird_nichts_geloescht(self):
        self._zeilen()
        ausgabe = StringIO()
        call_command('spam_aufraeumen', stdout=ausgabe)
        self.assertIn('Keine Frist', ausgabe.getvalue())
        self.assertEqual(KontaktAnfrage.objects.count(), 7)

    def test_mit_frist_nur_alter_spam_und_alte_angebote(self):
        self._zeilen()
        call_command('spam_aufraeumen', '--spam-tage', '30', '--angebot-tage', '90', stdout=StringIO())
        self.assertEqual(KontaktAnfrage.objects.filter(einstufung='anfrage').count(), 2)
        self.assertEqual(KontaktAnfrage.objects.filter(einstufung='angebot').count(), 0)
        self.assertEqual(list(KontaktAnfrage.objects.filter(einstufung='spam').values_list('name', flat=True)), ['neu'])

    def test_trocken_loescht_nichts(self):
        self._zeilen()
        call_command('spam_aufraeumen', '--spam-tage', '30', '--trocken', stdout=StringIO())
        self.assertEqual(KontaktAnfrage.objects.count(), 7)
