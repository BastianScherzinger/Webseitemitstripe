"""Kontakt- und Newsletterformular – die einzigen Wege, auf denen Fremde
Daten in dieses Projekt schreiben.

Der Mailversand wird in jedem Test ersetzt. ``send_brevo_email`` startet einen
Thread und ruft die Brevo-HTTP-Schnittstelle auf; ein Test, der das echte
Verhalten benutzt, wäre langsam, netzabhängig und würde tatsächlich Post
verschicken.
"""

import json
from unittest import mock

from django.test import Client

from ..models import Subscriber
from ..views._helpers import ANFRAGE_GRENZE
from ._basis import LuviqTestCase

_MAIL = 'shop1.views.shop.send_brevo_email'

GUELTIGE_ANFRAGE = {
    'name': 'Erika Musterfrau',
    'email': 'erika@example.invalid',
    'betreff': 'Frage zu einer Jacke',
    'nachricht': 'Gibt es die bemalte Jeansjacke auch in Größe M?',
}


class KontaktformularTest(LuviqTestCase):
    """Das Anfrageformular – wenn es bricht, kommt keine Anfrage mehr an."""

    def test_gueltige_anfrage_wird_genau_einmal_verschickt(self):
        """Verhindert den unauffälligsten aller Ausfälle: das Formular meldet
        Erfolg, verschickt aber nichts – oder verschickt doppelt."""
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        self.assertEqual(versand.call_count, 1)

    def test_nach_dem_absenden_steht_die_bestaetigung_auf_eigener_adresse(self):
        """Verhindert, dass die Bestätigung wieder als Meldung auf ``/kontakt/``
        erscheint (KV07): ohne eigene Adresse ist kein abgeschicktes Formular
        zählbar, und Neuladen schickte die Anfrage ein zweites Mal ab."""
        # Ohne follow=True: der Testclient folgte der Weiterleitung über HTTP
        # und prüfte dann nur die 301 von SECURE_SSL_REDIRECT (_basis, Punkt 1).
        with mock.patch(_MAIL) as versand:
            weiter = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertEqual(weiter.status_code, 302)
        antwort = self.hole(weiter['Location'])
        self.assertEqual(antwort.status_code, 200)
        self.assertTemplateUsed(antwort, 'shop1/kontakt_danke.html')
        self.assertContains(antwort, 'Deine Nachricht ist abgeschickt.')
        self.assertNotContains(antwort, 'erfolgreich gesendet')
        self.assertEqual(versand.call_count, 1)

    def test_scheitert_der_versand_bleibt_die_anfrage_auf_der_kontaktseite(self):
        """Gegenprobe: eine Anfrage, deren Versand schon beim Start scheitert,
        darf nicht auf die Bestätigung führen."""
        with mock.patch(_MAIL, side_effect=RuntimeError('kein Versand')):
            antwort = self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        self.assertEqual(antwort.status_code, 200)
        self.assertTemplateUsed(antwort, 'shop1/kontakt.html')
        self.assertContains(antwort, 'Problem beim Senden')

    def test_leeres_formular_verschickt_nichts_und_meldet_das(self):
        """Verhindert, dass ein leeres Formular als gültige Anfrage durchgeht –
        das Postfach der Betreiberin füllt sich sonst mit Leermeldungen."""
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', {})
        self.assertEqual(antwort.status_code, 200)
        versand.assert_not_called()
        self.assertContains(antwort, 'Bitte fülle alle Felder aus')

    def test_jedes_pflichtfeld_wird_einzeln_verlangt(self):
        """Verhindert, dass eine Anfrage ohne Absenderadresse oder ohne Text
        ankommt und niemand darauf antworten kann."""
        for feld in GUELTIGE_ANFRAGE:
            daten = dict(GUELTIGE_ANFRAGE, **{feld: ''})
            with self.subTest(feld=feld), mock.patch(_MAIL) as versand:
                antwort = self.sende('/kontakt/', daten)
                versand.assert_not_called()
                self.assertContains(antwort, 'Bitte fülle alle Felder aus')

    def test_reine_leerzeichen_gelten_nicht_als_ausgefuellt(self):
        """Verhindert den billigsten Spamtrick auf diesem Formular: alle Felder
        mit einem Leerzeichen füllen. Ohne Prüfung auf echten Inhalt zählt das
        als gültige Anfrage und erzeugt eine leere Mail."""
        daten = {feld: '   ' for feld in GUELTIGE_ANFRAGE}
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/kontakt/', daten)
        versand.assert_not_called()
        self.assertContains(antwort, 'Bitte fülle alle Felder aus')

    def test_ungueltige_absenderadresse_verschickt_nichts(self):
        """Verhindert Anfragen, auf die niemand antworten kann (FO06): das
        ``type="email"`` im Formular umgeht jeder Abruf ohne Browser."""
        for adresse in ('keine-adresse', 'a@b', 'erika@@example.invalid'):
            daten = dict(GUELTIGE_ANFRAGE, email=adresse)
            with self.subTest(adresse=adresse), mock.patch(_MAIL) as versand:
                antwort = self.sende('/kontakt/', daten)
                self.assertEqual(antwort.status_code, 200)
                versand.assert_not_called()
                self.assertContains(antwort, 'gültige E-Mail-Adresse')

    def test_ueberlange_eingaben_verschicken_nichts(self):
        """Verhindert, dass ein Skript ein Megabyte Text in die Mail an die
        Betreiberin schreibt (FO06) – jedes Feld hat eine Obergrenze."""
        from ..views.shop import KONTAKT_LAENGEN
        for feld, grenze in KONTAKT_LAENGEN.items():
            wert = 'x' * (grenze + 1)
            if feld == 'email':
                wert = 'x' * (grenze - len('@example.invalid') + 1) + '@example.invalid'
            daten = dict(GUELTIGE_ANFRAGE, **{feld: wert})
            with self.subTest(feld=feld), mock.patch(_MAIL) as versand:
                antwort = self.sende('/kontakt/', daten)
                versand.assert_not_called()
                self.assertContains(antwort, 'zu lang')

    def test_zeilenumbrueche_gelangen_nicht_in_die_betreffzeile(self):
        """Verhindert das Einschleusen von Kopfzeilen (Header Injection): ein
        Zeilenumbruch im Betreff könnte sonst zusätzliche Empfänger oder einen
        fremden Absender in die Mail schreiben."""
        daten = dict(
            GUELTIGE_ANFRAGE,
            betreff='Hallo\r\nBcc: fremder@example.invalid',
            name='Ich\nX-Spam: nein',
        )
        with mock.patch(_MAIL) as versand:
            self.sende('/kontakt/', daten)
        betreff = versand.call_args.args[0]
        self.assertNotIn('\n', betreff)
        self.assertNotIn('\r', betreff)

    def test_anfrage_ohne_csrf_token_wird_abgewiesen(self):
        """Verhindert, dass eine fremde Seite im Namen einer Besucherin
        Anfragen abschickt – der CSRF-Schutz muss an diesem Formular greifen."""
        streng = Client(enforce_csrf_checks=True)
        with mock.patch(_MAIL) as versand:
            antwort = streng.post('/kontakt/', GUELTIGE_ANFRAGE, secure=True)
        self.assertEqual(antwort.status_code, 403)
        versand.assert_not_called()


class KontaktDankeTest(LuviqTestCase):
    """Die Bestätigungsseite ``/kontakt/danke/`` (KV07)."""

    def test_die_seite_ist_direkt_abrufbar_und_zeigt_nichts_aus_einer_anfrage(self):
        """Verhindert, dass die Adresse nur im Ablauf funktioniert: ein
        Messwerkzeug oder ein Werbekonto ruft sie direkt auf. Sie darf dabei
        keine Daten einer früheren Anfrage zeigen."""
        with mock.patch(_MAIL):
            self.sende('/kontakt/', GUELTIGE_ANFRAGE)
        fremd = Client()
        antwort = fremd.get('/kontakt/danke/', secure=True)
        self.assertEqual(antwort.status_code, 200)
        for wert in GUELTIGE_ANFRAGE.values():
            self.assertNotContains(antwort, wert)

    def test_die_seite_steht_nicht_im_suchindex(self):
        """Verhindert, dass eine Bestätigung ohne eigenen Inhalt in der
        Trefferliste landet: ``noindex, follow``, weder in der Sitemap noch in
        llms.txt."""
        inhalt = self.hole('/kontakt/danke/').content.decode()
        self.assertIn('<meta name="robots" content="noindex, follow">', inhalt)
        self.assertNotIn('/kontakt/danke/', self.hole('/sitemap.xml').content.decode())
        self.assertNotIn('/kontakt/danke/', self.hole('/llms.txt').content.decode())

    def test_die_seite_wird_nicht_zwischengespeichert(self):
        """Verhindert, dass ein Zwischenspeicher die Bestätigung ausliefert,
        ohne dass der Aufruf den Server erreicht – er fehlte dann im
        Besuchsprotokoll, an dem sich ein Abschluss ablesen lässt."""
        antwort = self.hole('/kontakt/danke/')
        self.assertIn('no-store', antwort['Cache-Control'])

    def test_die_seite_nennt_keine_andere_adresse_als_die_kontaktseite(self):
        """Verhindert erfundene Kontaktwege auf der Bestätigung: die E-Mail-
        Adresse muss dieselbe sein, die ``/kontakt/`` nennt."""
        danke = self.hole('/kontakt/danke/').content.decode()
        kontakt = self.hole('/kontakt/').content.decode()
        self.assertIn('mailto:brehlerluisa@gmail.com', danke)
        self.assertIn('mailto:brehlerluisa@gmail.com', kontakt)
        self.assertNotIn('tel:', danke)


class NewsletterTest(LuviqTestCase):
    """Die Newsletter-Anmeldung schreibt ohne Anmeldung in die Datenbank."""

    def test_anmeldung_legt_genau_einen_eintrag_an(self):
        """Verhindert, dass die Anmeldung Erfolg meldet, ohne zu speichern."""
        antwort = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.filter(email='neu@example.invalid').count(), 1)

    def test_anmeldung_ohne_adresse_wird_abgewiesen(self):
        """Verhindert leere Datensätze in der Abonnentenliste, an die später
        kein Newsletter zugestellt werden kann."""
        antwort = self.sende('/newsletter/subscribe/', {'email': '   '})
        self.assertEqual(antwort.status_code, 400)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_anmeldung_mit_ungueltiger_adresse_wird_abgewiesen(self):
        """Verhindert Datensätze, an die kein Newsletter zugestellt werden
        kann (FO06) – auch als JSON, wie das Skript der Startseite schickt."""
        for adresse in ('keine-adresse', 'a@b', 'x' * 250 + '@example.invalid'):
            with self.subTest(adresse=adresse):
                antwort = self.client.post(
                    '/newsletter/subscribe/', json.dumps({'email': adresse}),
                    content_type='application/json', secure=True)
                self.assertEqual(antwort.status_code, 400)
        self.assertEqual(Subscriber.objects.count(), 0)

    def test_zweite_anmeldung_erzeugt_keinen_zweiten_eintrag(self):
        """Verhindert doppelte Zustellung an dieselbe Adresse und – weil das
        Feld ``unique`` ist – einen Serverfehler beim zweiten Absenden."""
        Subscriber.objects.create(email='schon.da@example.invalid')
        antwort = self.sende('/newsletter/subscribe/', {'email': 'schon.da@example.invalid'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_nur_eine_neue_anmeldung_meldet_einen_abschluss(self):
        """Verhindert doppelt gezählte Anmeldungen (FO08): das Skript der
        Startseite löst sein Ereignis nur bei ``neu`` aus, eine Wiederholung
        derselben Adresse darf das nicht melden."""
        erste = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        zweite = self.sende('/newsletter/subscribe/', {'email': 'neu@example.invalid'})
        self.assertIs(erste.json().get('neu'), True)
        self.assertNotIn('neu', zweite.json())

    def test_die_startseite_zaehlt_die_anmeldung_ohne_personendaten(self):
        """Verhindert, dass die Anmeldung wieder unzählbar auf der Seite
        endet (FO08) – und dass das Ereignis die Adresse mitschickt."""
        inhalt = self.hole('/').content.decode()
        self.assertIn("window.dataLayer.push({ event: 'generate_lead', lead_quelle: 'newsletter' })",
                      inhalt)
        self.assertIn('response.ok && data.neu', inhalt)
        push = inhalt.split('window.dataLayer.push(', 1)[1].split(')', 1)[0]
        self.assertNotIn('email', push)

    def test_anmeldung_per_get_ist_nicht_moeglich(self):
        """Verhindert, dass ein vorab geladener Link oder ein Bild in einer Mail
        fremde Adressen in die Abonnentenliste schreibt."""
        antwort = self.hole('/newsletter/subscribe/')
        self.assertEqual(antwort.status_code, 405)
        self.assertEqual(Subscriber.objects.count(), 0)


class DrosselungTest(LuviqTestCase):
    """Obergrenze je IP-Adresse für beide Anfragewege (FO09)."""

    def _kontakt(self, **meta):
        return self.sende('/kontakt/', GUELTIGE_ANFRAGE, **meta)

    def test_ueber_der_grenze_wird_keine_nachricht_mehr_verschickt(self):
        """Verhindert, dass eine Schleife das Postfach der Betreiberin füllt:
        nach fünf Anfragen einer Adresse antwortet das Formular mit 429."""
        with mock.patch(_MAIL) as versand:
            for _ in range(ANFRAGE_GRENZE):
                self.assertEqual(self._kontakt().status_code, 302)
            antwort = self._kontakt()
        self.assertContains(antwort, 'mehrere Nachrichten', status_code=429)
        self.assertEqual(versand.call_count, ANFRAGE_GRENZE)

    def test_eine_andere_adresse_ist_nicht_betroffen(self):
        """Gegenprobe: die Grenze gilt je Absender, nicht für alle Besucher."""
        with mock.patch(_MAIL) as versand:
            for _ in range(ANFRAGE_GRENZE + 1):
                self._kontakt(REMOTE_ADDR='198.51.100.1')
            antwort = self._kontakt(REMOTE_ADDR='198.51.100.2')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(versand.call_count, ANFRAGE_GRENZE + 1)

    def test_ein_selbst_gesetzter_weiterleitungskopf_umgeht_die_grenze_nicht(self):
        """Verhindert den einfachsten Umweg: der Absender setzt den ersten
        Eintrag von ``X-Forwarded-For`` bei jeder Anfrage neu. Gezählt wird
        der Eintrag, den der Proxy anhängt."""
        with mock.patch(_MAIL):
            for nummer in range(ANFRAGE_GRENZE):
                self._kontakt(HTTP_X_FORWARDED_FOR=f'10.0.0.{nummer}, 203.0.113.7')
            antwort = self._kontakt(HTTP_X_FORWARDED_FOR='10.0.0.99, 203.0.113.7')
        self.assertEqual(antwort.status_code, 429)

    def test_der_newsletter_nimmt_ueber_der_grenze_keine_adresse_mehr_an(self):
        """Verhindert, dass ein Skript die Abonnentenliste mit fremden
        Adressen füllt."""
        for nummer in range(ANFRAGE_GRENZE):
            antwort = self.sende('/newsletter/subscribe/', {'email': f'n{nummer}@example.invalid'})
            self.assertEqual(antwort.status_code, 200)
        antwort = self.sende('/newsletter/subscribe/', {'email': 'zuviel@example.invalid'})
        self.assertEqual(antwort.status_code, 429)
        self.assertIn('error', antwort.json())
        self.assertEqual(Subscriber.objects.count(), ANFRAGE_GRENZE)


class KontaktSpamschutzTest(LuviqTestCase):
    """Bot-Spam wird still verworfen (Anlass: Lamborghini-„Gewinnspiel“, 16.09.2026)."""

    LAMBORGHINI = {
        'name': 'RobertBoobe',
        'email': 'cosmas133@live.com',
        'betreff': 'THE LAMBORGHINI AVENTADOR SWEEPSTAKES CLOSES SOON',
        'nachricht': 'You are a snap away from an Lamborghini Aventador '
                     'https://telegra.ph/Win-a-new-Lamborghini-Aventador-today-Message-ID-24459-09-14',
    }

    def test_die_lamborghini_mail_wird_nicht_verschickt(self):
        with mock.patch(_MAIL) as versand, self.assertLogs('shop1', level='WARNING'):
            antwort = self.sende('/kontakt/', self.LAMBORGHINI)
        self.assertRedirects(antwort, '/kontakt/danke/', fetch_redirect_response=False)
        versand.assert_not_called()

    def test_die_falle_verwirft_auch_eine_harmlose_nachricht(self):
        with mock.patch(_MAIL) as versand:
            self.sende('/kontakt/', dict(GUELTIGE_ANFRAGE, webseite='https://x.example'))
        versand.assert_not_called()

    def test_ein_mensch_mit_einem_link_kommt_durch(self):
        """Eine Kundin darf auf ein Bild verweisen — ein Link allein blockt nicht."""
        from .. import spamschutz
        daten = dict(GUELTIGE_ANFRAGE,
                     nachricht='So eine Jacke wie hier: https://instagram.com/p/abc',
                     formzeit=spamschutz.zeitstempel())
        import time
        punkte, gruende = spamschutz.bewerte(daten, jetzt=time.time() + 60)
        self.assertLess(punkte, spamschutz.SCHWELLE, gruende)

    def test_das_formular_traegt_zeitstempel_und_falle(self):
        inhalt = self.hole('/kontakt/').content.decode()
        self.assertIn('name="formzeit"', inhalt)
        self.assertIn('name="webseite"', inhalt)
        self.assertIn('tabindex="-1"', inhalt)
