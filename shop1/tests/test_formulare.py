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
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(versand.call_count, 1)
        self.assertContains(antwort, 'erfolgreich gesendet')

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
