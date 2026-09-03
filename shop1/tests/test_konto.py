"""Konto: Registrierung, E-Mail-Verifizierung, Passwortwechsel, Kontolöschung
und die Anmeldesperre von ``django-axes`` – ``views/auth.py``, ``forms.py``,
``signals.py`` und die Axes-Einstellungen in ``mainweb/settings.py``.

Der Mailversand wird ersetzt: ``send_verification_email`` (``signals.py``)
ruft ``send_brevo_email`` auf, das einen Thread mit HTTP-Aufruf startet.
"""

import uuid
from unittest import mock

from axes.utils import reset as axes_zuruecksetzen
from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings

from ..models import UserProfile
from ._basis import LuviqTestCase, erzeuge_benutzer

_MAIL = 'shop1.signals.send_brevo_email'
#: Die Anmeldetests hashen rund dreissig Passwörter; mit dem Betriebs-Hasher
#: (PBKDF2, absichtlich langsam) kostet das je Lauf über eine Minute. Der
#: schnelle Hasher ändert nichts an dem, was geprüft wird.
SCHNELLER_HASHER = override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
PASSWORT = 'ein-langes-testpasswort'
NEUES_PASSWORT = 'noch-ein-langes-testpasswort'

REGISTRIERUNG = {
    'username': 'neu',
    'email': 'neu@example.invalid',
    'first_name': 'Erika',
    'last_name': 'Musterfrau',
    'password1': 'Sehr-sicheres-Passwort-2026',
    'password2': 'Sehr-sicheres-Passwort-2026',
}


class RegistrierungTest(LuviqTestCase):
    """Der Weg von der Registrierung bis zur bestätigten Adresse."""

    def test_registrierung_legt_nutzer_und_profil_an_und_verschickt_genau_eine_mail(self):
        """Verhindert drei stille Ausfälle: das Konto entsteht ohne Profil (die
        Profilseite bräche), es entsteht schon bestätigt, oder die
        Bestätigungsmail geht nicht – oder doppelt – raus. Der Link in der
        Mail muss zum Token des angelegten Profils führen."""
        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/register/', REGISTRIERUNG)

        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/login/')
        konto = User.objects.get(username='neu')
        self.assertEqual((konto.email, konto.first_name), ('neu@example.invalid', 'Erika'))
        self.assertFalse(konto.profile.email_verified)

        self.assertEqual(versand.call_count, 1)
        betreff, inhalt, empfaenger = versand.call_args.args[:3]
        self.assertEqual(empfaenger, 'neu@example.invalid')
        self.assertIn('bestätige', betreff.lower())
        self.assertIn(f'/verify/{konto.profile.verification_token}/', inhalt)

    def test_ein_gueltiger_verifizierungslink_bestaetigt_und_ein_zweiter_aufruf_schadet_nicht(self):
        """Verhindert, dass der Link aus der Mail ins Leere führt – oder dass
        ein zweiter Klick (Mailprogramme rufen Links vorab auf) die
        Bestätigung wieder zurücknimmt oder den Token verbrennt."""
        konto = erzeuge_benutzer('kundin')
        token = konto.profile.verification_token

        antwort = self.hole(f'/verify/{token}/')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/login/')
        konto.profile.refresh_from_db()
        self.assertTrue(konto.profile.email_verified)

        antwort = self.hole(f'/verify/{token}/')
        self.assertEqual(antwort['Location'], '/login/')
        konto.profile.refresh_from_db()
        self.assertTrue(konto.profile.email_verified)
        self.assertEqual(konto.profile.verification_token, token)

    def test_ein_gefaelschter_token_verifiziert_nicht(self):
        """Verhindert, dass ein erratener oder kaputter Token irgendein Konto
        bestätigt oder die Seite mit 500 abbricht."""
        konto = erzeuge_benutzer('kundin')

        for falsch in (uuid.uuid4(), 'kein-uuid', '0' * 36):
            with self.subTest(token=falsch):
                antwort = self.hole(f'/verify/{falsch}/')
                self.assertEqual(antwort.status_code, 302)
                self.assertEqual(antwort['Location'], '/')
                konto.profile.refresh_from_db()
                self.assertFalse(konto.profile.email_verified)
        self.assertFalse(UserProfile.objects.filter(email_verified=True).exists())

    def test_ein_vergebener_benutzername_legt_kein_zweites_konto_an(self):
        """Verhindert, dass eine zweite Registrierung mit demselben Namen mit
        einem Serverfehler endet oder eine Mail verschickt."""
        erzeuge_benutzer('neu')

        with mock.patch(_MAIL) as versand:
            antwort = self.sende('/register/', REGISTRIERUNG)

        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(User.objects.filter(username='neu').count(), 1)
        versand.assert_not_called()

    def test_eine_vorhandene_email_legt_heute_ein_zweites_konto_an(self):
        """Hält den **heutigen** Zustand fest, damit er nicht vergessen wird:
        ``CustomUserCreationForm`` (``forms.py``) prüft die Adresse nicht auf
        Eindeutigkeit, ``User.email`` ist es auch in der Datenbank nicht.
        Eine zweite Registrierung mit derselben Adresse legt deshalb ein
        zweites Konto an und verschickt eine zweite Bestätigungsmail; die
        Passwort-Zurücksetzen-Mail ginge später für beide Konten an ein
        Postfach. Der Plan (Welle 9, Schritt 43) erwartete die Ablehnung –
        sie gibt es nicht. Bekommt das Formular eine ``clean_email``-Prüfung,
        wird dieser Test rot und ist dann bewusst umzudrehen (Status 200,
        kein zweites Konto, keine Mail)."""
        with mock.patch(_MAIL) as versand:
            erzeuge_benutzer('erste', email='neu@example.invalid')
            versand.reset_mock()
            antwort = self.sende('/register/', dict(REGISTRIERUNG, username='zweite'))

        self.assertEqual(antwort.status_code, 302)
        self.assertTrue(User.objects.filter(username='zweite').exists())
        self.assertEqual(User.objects.filter(email='neu@example.invalid').count(), 2)
        self.assertEqual(versand.call_count, 1)


@SCHNELLER_HASHER
class PasswortUndKontoTest(LuviqTestCase):
    """Passwortwechsel und Kontolöschung einer angemeldeten Kundin."""

    def setUp(self):
        self.kundin = erzeuge_benutzer('kundin', PASSWORT)
        self.client.force_login(self.kundin)

    def test_der_passwortwechsel_verlangt_das_alte_passwort(self):
        """Verhindert, dass jemand an einem offen gelassenen Browser das
        Passwort tauscht, ohne das alte zu kennen – und dass der Wechsel mit
        richtigem alten Passwort die Kundin abmeldet."""
        antwort = self.sende('/profil/change-password/', {
            'old_password': 'falsch', 'new_password1': NEUES_PASSWORT, 'new_password2': NEUES_PASSWORT,
        })
        self.assertEqual(antwort.status_code, 200)
        self.kundin.refresh_from_db()
        self.assertTrue(self.kundin.check_password(PASSWORT))

        antwort = self.sende('/profil/change-password/', {
            'old_password': PASSWORT, 'new_password1': NEUES_PASSWORT, 'new_password2': NEUES_PASSWORT,
        })
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/profil/')
        self.kundin.refresh_from_db()
        self.assertTrue(self.kundin.check_password(NEUES_PASSWORT))
        self.assertEqual(self.hole('/profil/').status_code, 200)

    def test_die_kontoloeschung_entfernt_das_konto_und_meldet_ab(self):
        """Verhindert, dass nach dem Löschen eine angemeldete Sitzung ohne
        Konto weiterläuft – und dass ein blosser Seitenaufruf (GET, etwa
        durch einen vorab geladenen Link) schon löscht."""
        antwort = self.hole('/delete-account/')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/profil/')
        self.assertTrue(User.objects.filter(username='kundin').exists())

        antwort = self.sende('/delete-account/')
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/')
        self.assertFalse(User.objects.filter(username='kundin').exists())
        self.assertFalse(UserProfile.objects.filter(user__username='kundin').exists())

        antwort = self.hole('/profil/')
        self.assertEqual(antwort.status_code, 302)
        self.assertIn('/login/', antwort['Location'])

    def test_das_konto_der_shopbesitzerin_laesst_sich_nicht_loeschen(self):
        """Verhindert, dass die Betreiberin sich mit einem Klick selbst aus
        dem Shop entfernt – mit ihr fielen Admin-Panel und Bestellzugriff."""
        besitzerin = User.objects.create_superuser('shopbesitzer', 'shop@example.invalid', PASSWORT)
        self.client.force_login(besitzerin)

        antwort = self.sende('/delete-account/')
        self.assertEqual(antwort['Location'], '/profil/')
        self.assertTrue(User.objects.filter(username='shopbesitzer').exists())


@SCHNELLER_HASHER
class AnmeldesperreTest(LuviqTestCase):
    """``django-axes`` nach ``settings.py``: Sperre je Benutzername **und**
    Adresse, nicht je Adresse allein.

    Der Sperrzustand liegt in der Datenbank (``AccessAttempt``) und im
    Cache; beides wird vor und nach jedem Test geleert, damit kein Test den
    nächsten aussperrt.
    """

    def setUp(self):
        axes_zuruecksetzen()
        self.kundin = erzeuge_benutzer('kundin', PASSWORT)
        self.nachbarin = erzeuge_benutzer('nachbarin', PASSWORT)

    def tearDown(self):
        axes_zuruecksetzen()

    def anmelden(self, benutzername, passwort):
        return self.sende('/login/', {'username': benutzername, 'password': passwort})

    def test_fehlversuche_sperren_nur_die_kombination_aus_benutzername_und_adresse(self):
        """Verhindert zwei gegensätzliche Fehler. Erstens: nach der
        eingestellten Zahl von Fehlversuchen kommt derselbe Benutzername von
        derselben Adresse **auch mit richtigem Passwort** nicht mehr hinein.
        Zweitens: eine andere Kundin von derselben Adresse (Haushalt, Büro,
        Mobilfunk-NAT) kann sich weiter anmelden – sonst könnte jeder mit
        zehn falschen Passwörtern fremde Konten aussperren."""
        grenze = settings.AXES_FAILURE_LIMIT
        self.assertLessEqual(grenze, 10)

        for versuch in range(1, grenze):
            antwort = self.anmelden('kundin', 'falsch')
            self.assertEqual(antwort.status_code, 200, f'Versuch {versuch} schon gesperrt')
            self.assertContains(antwort, 'Ungültige Anmeldedaten')

        # Der letzte Fehlversuch löst die Sperre aus; ab hier hilft auch das
        # richtige Passwort nicht mehr. Axes antwortet mit dem eingestellten
        # Sperrstatus (Vorgabe 429 „Too Many Requests") und der Sperrseite.
        self.anmelden('kundin', 'falsch')
        antwort = self.anmelden('kundin', PASSWORT)
        self.assertEqual(antwort.status_code, getattr(settings, 'AXES_HTTP_RESPONSE_CODE', 429))
        self.assertTemplateUsed(antwort, settings.AXES_LOCKOUT_TEMPLATE)
        self.assertNotIn('_auth_user_id', self.client.session)

        antwort = self.anmelden('nachbarin', PASSWORT)
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], '/')
        self.assertEqual(int(self.client.session['_auth_user_id']), self.nachbarin.id)

    def test_ein_einzelner_fehlversuch_sperrt_nicht_und_eine_gelungene_anmeldung_setzt_zurueck(self):
        """Gegenprobe: eine zu scharfe Sperre würde nach dem ersten Tippfehler
        aussperren. Nach einer gelungenen Anmeldung beginnt die Zählung neu
        (``AXES_RESET_ON_SUCCESS``), sonst summierten sich Tippfehler über
        Monate zur Sperre."""
        self.assertEqual(self.anmelden('kundin', 'falsch').status_code, 200)
        antwort = self.anmelden('kundin', PASSWORT)
        self.assertEqual(antwort.status_code, 302)
        self.client.logout()

        for _ in range(settings.AXES_FAILURE_LIMIT - 1):
            self.assertEqual(self.anmelden('kundin', 'falsch').status_code, 200)
        self.assertEqual(self.anmelden('kundin', PASSWORT).status_code, 302)
