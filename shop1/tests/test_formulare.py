"""Kontakt- und Newsletterformular – die einzigen Wege, auf denen Fremde
Daten in dieses Projekt schreiben.

Der Mailversand wird in jedem Test ersetzt. ``send_brevo_email`` startet einen
Thread und ruft die Brevo-HTTP-Schnittstelle auf; ein Test, der das echte
Verhalten benutzt, wäre langsam, netzabhängig und würde tatsächlich Post
verschicken.
"""

from unittest import mock

from django.test import Client

from ..models import Subscriber
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

    def test_zweite_anmeldung_erzeugt_keinen_zweiten_eintrag(self):
        """Verhindert doppelte Zustellung an dieselbe Adresse und – weil das
        Feld ``unique`` ist – einen Serverfehler beim zweiten Absenden."""
        Subscriber.objects.create(email='schon.da@example.invalid')
        antwort = self.sende('/newsletter/subscribe/', {'email': 'schon.da@example.invalid'})
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(Subscriber.objects.count(), 1)

    def test_anmeldung_per_get_ist_nicht_moeglich(self):
        """Verhindert, dass ein vorab geladener Link oder ein Bild in einer Mail
        fremde Adressen in die Abonnentenliste schreibt."""
        antwort = self.hole('/newsletter/subscribe/')
        self.assertEqual(antwort.status_code, 405)
        self.assertEqual(Subscriber.objects.count(), 0)
