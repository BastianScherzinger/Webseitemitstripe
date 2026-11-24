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
from ..management.commands.pruefe_abwehr import (ANGEBOTE, ANGEBOTE_ABNAHME, KUNDINNEN_ABNAHME_1, KUNDINNEN_ABNAHME_2, CREATOR_ANGEBOTE, ECHTE_ANGEBOTE, KEINE_ANGEBOTE,
                                                 KUNDINNEN_REGRESSION, KUNDINNEN_ABNAHME_3, ANGEBOTE_ABNAHME_3)
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


@mock.patch.dict('os.environ', {'ANGEBOT_ERKENNUNG': 'an'})
@override_settings(**PROD)
class AngebotTest(_Basis):

    def _angebot(self, kuerzel, betreff, text, email='agentur@example.org'):
        luisa, absage = self._senden(name='Sam Agentur', email=email, betreff=betreff, nachricht=text)
        luisa.assert_not_called()
        # Kopie an die Webagentur zur Kontrolle der Einordnung – Luisa bekommt nichts.
        self.kopie_versand.assert_called_once()
        self.assertIn('[Angebot – ', self.kopie_versand.call_args[0][0])
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

    def test_alle_unbekannten_kundinnen_der_abnahme_sind_keine_angebote(self):
        for betreff, text in KUNDINNEN_ABNAHME_1 + KUNDINNEN_ABNAHME_2:
            self.assertFalse(angebote.ist_angebot('', betreff, text), (betreff, text[:60]))

    def test_alle_verkaufsschreiben_der_abnahme_werden_erkannt(self):
        for betreff, text in ANGEBOTE_ABNAHME:
            self.assertTrue(angebote.ist_angebot('', betreff, text), (betreff, text[:60]))

    def test_ein_beliebiges_free_ist_kein_tausch_und_berufsangaben_allein_kein_angebot(self):
        for satz in ("Hi! I'm a content creator and want to buy a coat. Do you offer free shipping? I love your videos.",
                     "I'm a web designer myself and love your work, could you make me a sweatshirt with my cat?",
                     "We create costumes for a theatre and would like to commission a coat for a music video."):
            self.assertFalse(angebote.ist_angebot('', 'Frage', satz), satz)
        # ausdrücklicher Tausch plus Ziel „für deine Marke“: Absage
        self.assertTrue(angebote.ist_angebot('', 'Collab', "I'm a UGC creator and can make a reel for your brand "
                                                           "in exchange for a free piece."))

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

    def test_die_absage_hat_einen_rueckweg_zu_luisa_und_in_jeder_sprache_den_hinweis(self):
        for kuerzel, (betreff, text) in angebote.ABSAGEN.items():
            self.assertIn('Luisa', text.replace('Луиза', 'Luisa').replace('Луїза', 'Luisa'), kuerzel)
            self.assertGreaterEqual(text.count(chr(10) * 2), 3, kuerzel)   # Gruß, Absatz, Rückweg, Schluss
        kuerzel, betreff, text = ANGEBOTE[1]
        with mock.patch.dict('os.environ', {'ADMIN_EMAIL': 'luisa@example.org'}):
            absage = self._angebot(kuerzel, betreff, text)
        self.assertEqual(absage.call_args.kwargs['reply_to'], 'luisa@example.org')

    def test_die_agentur_kopie_nennt_den_wirklichen_stand_im_betreff(self):
        kuerzel, betreff, text = ANGEBOTE[1]
        self._senden(name='Sam', email='noreply@firma.example', betreff=betreff, nachricht=text)
        self.assertIn('[Angebot – keine Absage: adresse]', self.kopie_versand.call_args[0][0])
        self.kopie_versand.reset_mock()
        cache.clear()
        self._senden(name='Sam', email='ok@example.org', betreff=betreff, nachricht=text)
        self.assertIn('[Angebot – abgesagt]', self.kopie_versand.call_args[0][0])

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


@override_settings(**PROD)
class SchalterTest(_Basis):
    """``ANGEBOT_ERKENNUNG`` (Vorgabe aus, Abnahme 3): ohne den Schalter geht jede Nicht-Spam-Nachricht an Luisa."""

    def test_vorgabe_ist_aus(self):
        with mock.patch.dict('os.environ', clear=False) as env:
            env.pop('ANGEBOT_ERKENNUNG', None)
            self.assertFalse(angebote.erkennung_aktiv())
        for wert in ('an', 'AN', 'ein', '1'):
            with mock.patch.dict('os.environ', {'ANGEBOT_ERKENNUNG': wert}):
                self.assertTrue(angebote.erkennung_aktiv(), wert)
        with mock.patch.dict('os.environ', {'ANGEBOT_ERKENNUNG': 'aus'}):
            self.assertFalse(angebote.erkennung_aktiv())

    def test_aus_jede_der_46_kundinnen_erreicht_luisa(self):
        for k, name, email, betreff, text, _s in KUNDINNEN_ABNAHME_3:
            cache.clear()
            KontaktAnfrage.objects.all().delete()
            self.kopie_versand.reset_mock()
            daten = _formular(name=name, email=email, betreff=betreff, nachricht=text)
            del daten[spamschutz.FELD_ZEIT]      # auch ohne Zeitstempel
            with mock.patch(_LUISA) as luisa, mock.patch(_ABSAGE) as absage:
                antwort = self.sende('/kontakt/', daten)
            self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
            self.assertEqual(KontaktAnfrage.objects.get().einstufung, 'anfrage', k)
            luisa.assert_called_once()
            absage.assert_not_called()

    def test_aus_ein_mutmassliches_angebot_geht_an_luisa_mit_praefix_und_ohne_absage(self):
        for k, name, email, betreff, text, _s in ANGEBOTE_ABNAHME_3[:6]:
            cache.clear()
            KontaktAnfrage.objects.all().delete()
            self.kopie_versand.reset_mock()
            with mock.patch(_LUISA) as luisa, mock.patch(_ABSAGE) as absage:
                self.sende('/kontakt/', _formular(name=name, email=email, betreff=betreff, nachricht=text))
            luisa.assert_called_once()
            self.assertTrue(luisa.call_args[0][0].startswith('[evtl. Angebot] Kontaktformular: '), k)
            absage.assert_not_called()
            a = KontaktAnfrage.objects.get()
            self.assertEqual(a.einstufung, 'anfrage')
            self.assertIn('evtl-angebot', a.einstufung_gruende)
            self.kopie_versand.assert_called_once()    # Agentur-Kopie wie bisher

    def test_aus_eine_kundin_hat_kein_praefix(self):
        with mock.patch(_LUISA) as luisa, mock.patch(_ABSAGE):
            self.sende('/kontakt/', _formular(betreff='Gutscheine für Firmen?',
                                              nachricht='Bietet ihr Gutscheine für Firmen an? Marketing-Team.'))
        self.assertEqual(luisa.call_args[0][0], 'Kontaktformular: Gutscheine für Firmen?')

    @mock.patch.dict('os.environ', {'ANGEBOT_ERKENNUNG': 'an'})
    def test_an_bisheriges_verhalten_angebot_wird_abgesagt(self):
        k, name, email, betreff, text, _s = ANGEBOTE_ABNAHME_3[1]
        with mock.patch(_LUISA) as luisa, mock.patch(_ABSAGE) as absage:
            self.sende('/kontakt/', _formular(name=name, email=email, betreff=betreff, nachricht=text))
        luisa.assert_not_called()
        absage.assert_called_once()
        self.assertEqual(KontaktAnfrage.objects.get().einstufung, 'angebot')

    @mock.patch.dict('os.environ', {'ANGEBOT_ERKENNUNG': 'aus', 'ABSAGE_AKTIV': 'an'})
    def test_absage_aktiv_wirkt_nur_bei_erkennung_an(self):
        k, name, email, betreff, text, _s = ANGEBOTE_ABNAHME_3[1]
        with mock.patch(_LUISA) as luisa, mock.patch(_ABSAGE) as absage:
            self.sende('/kontakt/', _formular(name=name, email=email, betreff=betreff, nachricht=text))
        luisa.assert_called_once()
        absage.assert_not_called()

    def test_datenschutz_absatz_folgt_dem_schalter(self):
        with mock.patch.dict('os.environ', {'ANGEBOT_ERKENNUNG': 'aus'}):
            seite = self.client.get('/datenschutz/', secure=True).content.decode()
        self.assertIn('erkennbar automatisch erzeugt wurden (Spam)', seite)
        self.assertNotIn('Werbeangebote von Dienstleistern', seite)
        self.assertNotIn('automatische Absage', seite)
        with mock.patch.dict('os.environ', {'ANGEBOT_ERKENNUNG': 'an'}):
            seite = self.client.get('/datenschutz/', secure=True).content.decode()
        self.assertIn('Werbeangebote von Dienstleistern', seite)
        self.assertIn('automatische Absage', seite)


@override_settings(**PROD)
class Abnahme3Test(_Basis):

    def test_46_kundinnen_unter_der_schwelle_auch_ohne_zeitstempel_und_kein_angebot(self):
        for k, name, email, betreff, text, _s in KUNDINNEN_ABNAHME_3:
            punkte, gruende = spamschutz.bewerte(dict(name=name, email=email, betreff=betreff, nachricht=text))
            self.assertLess(punkte, spamschutz.SCHWELLE, (k, gruende))
            self.assertFalse(angebote.ist_angebot(name, betreff, text), k)

    def test_18_angebote_werden_erkannt(self):
        for k, name, email, betreff, text, _s in ANGEBOTE_ABNAHME_3:
            self.assertTrue(angebote.ist_angebot(name, betreff, text), k)

    def test_ein_einziger_verkaufssatz_reicht_nicht(self):
        self.assertFalse(angebote.ist_angebot('', 'Video', 'Hi, we produce videos for your brand. Nice shop!'))

    def test_kundenwoerter_in_allen_sprachen_sperren(self):
        for wort in ('Gutschein', 'voucher', 'gift card', 'carte cadeau', "bon d'achat", 'tarjeta regalo',
                     'buono regalo', 'cadeaubon', 'bon podarunkowy', 'hediye çeki', 'Newsletter', 'заказ',
                     'купить', 'худи', 'скидка', 'kaufen', 'bestellen'):
            text = (f'{wort}: Hi, we help brands with video marketing, let me know if you are interested, '
                    f'we offer a free audit and our clients love it.')
            self.assertFalse(angebote.ist_angebot('', 'Video', text), wort)

    def test_eigene_domain_und_kundenlinks_sind_keine_links(self):
        def punkte(**felder):
            d = dict(name='Ben', email='ben@gmail.com', betreff='Frage', nachricht='Hallo, eine Frage.')
            d.update(felder)
            return spamschutz.bewerte(d)
        self.assertLess(punkte(betreff='Frage zu www.luviq-alsfeld.com/stuecke')[0], spamschutz.SCHWELLE)
        self.assertNotIn('link-im-kopf', punkte(betreff='Frage zu https://www.luviq-luebeck.com/')[1])
        for url in ('https://www.instagram.com/p/C8xYz12/', 'https://www.tiktok.com/@luviq', 'https://pin.it/abc',
                    'https://de.pinterest.com/pin/123/', 'https://luviq-shop.example/x'):
            p, g = punkte(nachricht=f'Gewinnspiel, mein Kommentar: {url} Wo ist mein Gewinn?')
            self.assertLess(p, spamschutz.SCHWELLE, (url, g))
        self.assertEqual(spamschutz.bewerte(dict(name='x', email='a@b.de', betreff='Hi',
                                                 nachricht='Sieh https://www.fremd.example/a'))[1],
                         ['ohne-zeit', 'link'])

    def test_gewinnspiel_nur_mit_fremdem_link_ist_spam(self):
        d = dict(name='Anna', email='a@gmx.de', betreff='Gewinnspiel',
                 nachricht='Ich habe gewonnen, bitte hier klicken: https://fremd.example/x')
        punkte, gruende = spamschutz.bewerte(d)
        self.assertIn('spamwort', gruende)
        self.assertGreaterEqual(punkte, spamschutz.SCHWELLE)
        d['nachricht'] = 'Ich habe gewonnen, wie bekomme ich meinen Gewinn?'
        self.assertLess(spamschutz.bewerte(d)[0], spamschutz.SCHWELLE)

    def test_kyrillisch_allein_ist_kein_fremdschrift_link(self):
        p, g = spamschutz.bewerte(dict(name='Алексей', email='a@mail.ru', betreff='Вопрос',
                                       nachricht='Здравствуйте, хочу заказать худи, пишу в Instagram https://www.instagram.com/luviq'))
        self.assertNotIn('fremdschrift-link', g)
        self.assertLess(p, spamschutz.SCHWELLE)


class SpracheTest(LuviqTestCase):

    def test_rueckfall_ist_englisch(self):
        self.assertEqual(angebote.sprache(''), 'en')
        self.assertEqual(angebote.sprache('qwertz'), 'en')
        self.assertEqual(angebote.sprache('你好 我们提供视频服务'), 'en')

    def test_unsicher_heisst_englisch_nicht_polnisch(self):
        for t in ("Hi, I noticed your website could use a redesign. I'm a web developer and could build you a faster site.",
                  "Hello, I'm a web designer myself and I just love what you do. Could you make me a z do na sweatshirt?",
                  "Hi, do you do custom designs? I would like it in time for a gift, thanks"):
            self.assertEqual(angebote.sprache(t), 'en', t)
        self.assertEqual(angebote.sprache('Dzień dobry, oferujemy pozycjonowanie stron i reklamy Google dla sklepów'), 'pl')

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
