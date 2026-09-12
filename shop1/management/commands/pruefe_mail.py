"""Prüfbefehl für den Mailweg.

Der dritte eigene Prüfbefehl neben ``pruefe_seite`` (Umgebung und
ausgelieferte Seite) und ``pruefe_links`` (Verweise). Er sieht sich das an,
was beide übergehen und was kein Test der Suite sehen kann: ob eine Mail
diesen Rechner überhaupt verlassen würde.

Das ist hier keine akademische Frage, weil dieses Projekt **zwei** Mailwege
benutzt und ein Ausfall auf beiden still ist:

* **Brevo-HTTP-API** (``shop1/utils.py::send_brevo_email``) – Bestätigung der
  Registrierung, Bestellbestätigung, Zahlungseingang, Kontaktanfrage an die
  Betreiberin, Newsletter. Der Versand läuft in einem eigenen Thread und
  protokolliert einen Fehlschlag nur ins Log; die Bestellung gilt trotzdem
  als aufgegeben. Ein falscher Schlüssel fällt deshalb niemandem auf.
* **SMTP über das Brevo-Relay** (Djangos ``send_mail``) – der Rückfall
  derselben Funktion, wenn kein ``BREVO_API_KEY`` gesetzt ist, und der
  einzige Weg für die Passwort-Vergessen-Mail, die Django selbst verschickt.
  Railway blockt ausgehende SMTP-Ports; genau deswegen gibt es den ersten
  Weg. Ein stiller SMTP-Weg heisst: niemand kann sein Passwort zurücksetzen.

Der Befehl zeigt die Einstellungen beider Wege, versucht die Anmeldung
(API-Schlüssel gegen ``/v3/account``, SMTP mit ``EHLO``/``STARTTLS``/Login)
und verschickt auf Wunsch eine Testmail – **synchron**, damit man sieht, was
passiert, statt es im Thread zu verlieren.

    python manage.py pruefe_mail                      # Einstellungen + Anmeldung
    python manage.py pruefe_mail --ohne-verbindung    # nur Einstellungen, kein Netz
    python manage.py pruefe_mail --streng             # Warnungen zählen wie Fehler
    python manage.py pruefe_mail --an du@example.com  # zusätzlich eine Testmail

Kein Geheimnis erscheint in der Ausgabe: von Schlüsseln und Passwörtern
meldet der Befehl nur, ob sie gesetzt sind und wie lang sie sind. Die
Ausgabe darf in einem Container-Log landen.
"""

import json
import os
import smtplib

import requests
from django.conf import settings
from django.core.mail import get_connection
from django.core.management.base import BaseCommand

#: Auskunft über das eigene Brevo-Konto. Ein reiner Lesezugriff – er
#: verschickt nichts und verbraucht kein Mailkontingent, beantwortet aber
#: genau die Frage, die zählt: nimmt Brevo diesen Schlüssel an?
BREVO_KONTO = 'https://api.brevo.com/v3/account'

#: Versandadresse derselben API (``shop1/utils.py`` benutzt sie).
BREVO_VERSAND = 'https://api.brevo.com/v3/smtp/email'

#: Absender, den ``settings.py`` ohne gesetzte Umgebungsvariable einsetzt.
#: Brevo verschickt nur von einer verifizierten Domain – dieser Wert ist
#: keine.
STANDARD_ABSENDER = 'noreply@luviq-shop.de'

#: Sekunden, die eine Anmeldung höchstens dauern darf. Kurz genug, dass der
#: Befehl auch mit geblocktem Port zügig zurückkommt.
ZEITGRENZE = 15


def maskiert(wert):
    """„gesetzt (38 Zeichen)“ oder „nicht gesetzt“ – nie der Wert selbst."""
    if not wert:
        return 'nicht gesetzt'
    return f'gesetzt ({len(wert)} Zeichen)'


class Command(BaseCommand):
    help = ('Prüft den Mailweg: Einstellungen beider Wege (Brevo-API und '
            'SMTP-Relay), die Anmeldung an beiden und auf Wunsch eine '
            'Testmail.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--streng', action='store_true',
            help='Warnungen ebenfalls als Fehler werten (Exitcode 1).',
        )
        parser.add_argument(
            '--ohne-verbindung', action='store_true', dest='ohne_verbindung',
            help='Nur die Einstellungen prüfen, keine Verbindung nach aussen.',
        )
        parser.add_argument(
            '--an', metavar='ADRESSE', default='',
            help='Zusätzlich eine Testmail an diese Adresse schicken '
                 '(über den Weg, den der Shop selbst benutzt).',
        )

    def handle(self, *args, **optionen):
        self.fehler = []
        self.warnungen = []

        self._zeige_einstellungen()
        self._pruefe_einstellungen()
        if not optionen['ohne_verbindung']:
            self._pruefe_brevo_anmeldung()
            self._pruefe_smtp_anmeldung()
        else:
            self.stdout.write(
                'Anmeldung übersprungen (--ohne-verbindung).'
            )
        if optionen['an']:
            self._sende_testmail(optionen['an'])

        for text in self.warnungen:
            self.stdout.write(self.style.WARNING(f'WARNUNG  {text}'))
        for text in self.fehler:
            self.stdout.write(self.style.ERROR(f'FEHLER   {text}'))

        if not self.fehler and not self.warnungen:
            self.stdout.write(self.style.SUCCESS('Alles in Ordnung.'))
        else:
            self.stdout.write(
                f'\n{len(self.fehler)} Fehler, {len(self.warnungen)} Warnungen.'
            )

        if self.fehler or (optionen['streng'] and self.warnungen):
            raise SystemExit(1)

    # ── Einstellungen ──────────────────────────────────────────────────

    def _zeige_einstellungen(self):
        """Was gilt gerade? Ohne diese Liste rät man beim Lesen des Logs."""
        backend = settings.EMAIL_BACKEND.rsplit('.', 1)[-1]
        zeilen = [
            f'Backend                {backend}',
            f'DEFAULT_FROM_EMAIL     {settings.DEFAULT_FROM_EMAIL}',
            f'ADMIN_EMAIL            {os.getenv("ADMIN_EMAIL") or "nicht gesetzt"}',
            f'SITE_URL               {settings.SITE_URL}',
            f'BREVO_API_KEY          {maskiert(os.getenv("BREVO_API_KEY"))}',
        ]
        if self._nutzt_smtp():
            zeilen += [
                f'EMAIL_HOST             {settings.EMAIL_HOST}:{settings.EMAIL_PORT}',
                f'Verschlüsselung        '
                f'{"SSL" if settings.EMAIL_USE_SSL else "STARTTLS" if settings.EMAIL_USE_TLS else "keine"}',
                f'EMAIL_HOST_USER        {settings.EMAIL_HOST_USER or "nicht gesetzt"}',
                f'EMAIL_HOST_PASSWORD    {maskiert(settings.EMAIL_HOST_PASSWORD)}',
            ]
        self.stdout.write('\n'.join(zeilen) + '\n')

    @staticmethod
    def _nutzt_smtp():
        return settings.EMAIL_BACKEND.endswith('smtp.EmailBackend')

    def _pruefe_einstellungen(self):
        api_schluessel = os.getenv('BREVO_API_KEY')

        if not self._nutzt_smtp():
            ziel = ('die Konsole' if 'console' in settings.EMAIL_BACKEND
                    else settings.EMAIL_BACKEND.rsplit('.', 1)[-1])
            meldung = (
                f'Das Mail-Backend schreibt nach {ziel} – über SMTP verlässt '
                f'keine Mail diesen Rechner. Betroffen ist vor allem die '
                f'Passwort-vergessen-Mail, die Django selbst verschickt.'
            )
            # Im Entwicklungsmodus ist genau das gewollt (settings.py), im
            # Betrieb wäre es ein Ausfall.
            (self.warnungen if settings.DEBUG else self.fehler).append(meldung)
        else:
            if not settings.EMAIL_HOST_USER:
                self.fehler.append(
                    'EMAIL_HOST_USER ist leer – das Brevo-Relay weist jede '
                    'Anmeldung ohne Benutzer ab, die Passwort-vergessen-Mail '
                    'geht dann nicht hinaus.'
                )
            if not settings.EMAIL_HOST_PASSWORD:
                self.fehler.append(
                    'EMAIL_HOST_PASSWORD ist leer – dasselbe: keine Anmeldung, '
                    'keine Mail über SMTP.'
                )
            if settings.EMAIL_USE_TLS and settings.EMAIL_USE_SSL:
                self.fehler.append(
                    'EMAIL_USE_TLS und EMAIL_USE_SSL sind beide an; Django '
                    'kann so keine Verbindung aufbauen.'
                )
            elif not (settings.EMAIL_USE_TLS or settings.EMAIL_USE_SSL):
                self.warnungen.append(
                    f'Weder STARTTLS noch SSL auf Port {settings.EMAIL_PORT} – '
                    f'Anmeldedaten gingen im Klartext über die Leitung.'
                )

        if not api_schluessel:
            self.warnungen.append(
                'BREVO_API_KEY ist nicht gesetzt – Bestell-, Kontakt- und '
                'Bestätigungsmails fallen auf SMTP zurück, dessen Ports '
                'Railway blockt (genau dafür gibt es den API-Weg).'
            )

        if settings.DEFAULT_FROM_EMAIL == STANDARD_ABSENDER:
            self.warnungen.append(
                f'DEFAULT_FROM_EMAIL steht auf dem Vorgabewert '
                f'„{STANDARD_ABSENDER}“. Brevo verschickt nur von einer im '
                f'Konto verifizierten Absenderadresse; ist diese es nicht, '
                f'lehnt die API jede Mail ab.'
            )
        if not os.getenv('ADMIN_EMAIL'):
            self.warnungen.append(
                'ADMIN_EMAIL ist nicht gesetzt – Kontaktanfragen gehen an '
                'DEFAULT_FROM_EMAIL, also an den Absender selbst.'
            )

    # ── Anmeldung ──────────────────────────────────────────────────────

    def _pruefe_brevo_anmeldung(self):
        """Fragt die Kontoauskunft ab. Ein gültiger Schlüssel antwortet mit
        200, ein falscher oder abgelaufener mit 401 – das ist der Unterschied
        zwischen „Mails gehen raus“ und „Mails verschwinden im Thread“."""
        schluessel = os.getenv('BREVO_API_KEY')
        if not schluessel:
            return  # schon als Warnung gemeldet
        kopf = {'accept': 'application/json', 'api-key': schluessel}
        try:
            antwort = requests.get(BREVO_KONTO, headers=kopf, timeout=ZEITGRENZE)
        except requests.RequestException as ausnahme:
            self.fehler.append(
                f'Brevo-API nicht erreichbar ({type(ausnahme).__name__}): '
                f'{ausnahme}'
            )
            return
        if antwort.status_code == 401:
            self.fehler.append(
                'Brevo lehnt den BREVO_API_KEY ab (401). Alle Bestell-, '
                'Kontakt- und Bestätigungsmails scheitern still.'
            )
            return
        if antwort.status_code >= 300:
            self.fehler.append(
                f'Brevo-Kontoauskunft antwortet mit {antwort.status_code}: '
                f'{antwort.text[:200]}'
            )
            return
        try:
            konto = antwort.json()
        except ValueError:
            konto = {}
        self.stdout.write(self.style.SUCCESS(
            f'Brevo-API: Schlüssel gültig, Konto '
            f'{konto.get("email", "(ohne Adresse)")}.'
        ))

    def _pruefe_smtp_anmeldung(self):
        """Baut die Verbindung genau so auf, wie Django sie für die
        Passwort-vergessen-Mail aufbauen würde, und meldet sich an."""
        if not self._nutzt_smtp():
            return  # schon gemeldet
        verbindung = get_connection(timeout=ZEITGRENZE, fail_silently=False)
        try:
            verbindung.open()
        except smtplib.SMTPAuthenticationError as ausnahme:
            self.fehler.append(
                f'Das Brevo-Relay weist die SMTP-Anmeldung zurück: {ausnahme}. '
                f'Benutzer und Passwort stammen aus EMAIL_HOST_USER und '
                f'EMAIL_HOST_PASSWORD.'
            )
            return
        except Exception as ausnahme:
            self.fehler.append(
                f'Keine SMTP-Verbindung zu {settings.EMAIL_HOST}:'
                f'{settings.EMAIL_PORT} ({type(ausnahme).__name__}): '
                f'{ausnahme}. Auf Railway sind ausgehende SMTP-Ports '
                f'gesperrt – dort ist das der Normalfall und der Grund für '
                f'den API-Weg.'
            )
            return
        try:
            self.stdout.write(self.style.SUCCESS(
                f'SMTP: angemeldet an {settings.EMAIL_HOST}:'
                f'{settings.EMAIL_PORT}.'
            ))
        finally:
            verbindung.close()

    # ── Testmail ───────────────────────────────────────────────────────

    def _sende_testmail(self, adresse):
        """Eine echte Mail über den Weg, den der Shop selbst nimmt: API,
        wenn ein Schlüssel gesetzt ist, sonst SMTP – dieselbe Weiche wie in
        ``shop1/utils.py``. Anders als dort läuft sie hier synchron und ohne
        ``fail_silently``, sonst prüfte der Befehl nichts."""
        betreff = 'Luviq: Prüfmail von pruefe_mail'
        text = (
            'Diese Mail stammt aus "python manage.py pruefe_mail". '
            'Kommt sie an, funktioniert der geprüfte Mailweg.'
        )
        html = f'<p>{text}</p>'
        schluessel = os.getenv('BREVO_API_KEY')

        if schluessel:
            nutzlast = {
                'sender': {'name': 'Luviq-Shop',
                           'email': settings.DEFAULT_FROM_EMAIL},
                'to': [{'email': adresse}],
                'subject': betreff,
                'htmlContent': html,
                'textContent': text,
            }
            kopf = {'accept': 'application/json',
                    'content-type': 'application/json',
                    'api-key': schluessel}
            try:
                antwort = requests.post(BREVO_VERSAND, headers=kopf,
                                        data=json.dumps(nutzlast),
                                        timeout=ZEITGRENZE)
            except requests.RequestException as ausnahme:
                self.fehler.append(f'Testmail über die API gescheitert: {ausnahme}')
                return
            if antwort.status_code >= 300:
                self.fehler.append(
                    f'Brevo nimmt die Testmail nicht an ({antwort.status_code}): '
                    f'{antwort.text[:200]}'
                )
                return
            self.stdout.write(self.style.SUCCESS(
                f'Testmail über die Brevo-API an {adresse} übergeben.'
            ))
            return

        from django.core.mail import EmailMultiAlternatives

        nachricht = EmailMultiAlternatives(
            betreff, text, settings.DEFAULT_FROM_EMAIL, [adresse])
        nachricht.attach_alternative(html, 'text/html')
        try:
            nachricht.send(fail_silently=False)
        except Exception as ausnahme:
            self.fehler.append(
                f'Testmail über SMTP gescheitert ({type(ausnahme).__name__}): '
                f'{ausnahme}'
            )
            return
        self.stdout.write(self.style.SUCCESS(
            f'Testmail über {settings.EMAIL_BACKEND.rsplit(".", 1)[-1]} an '
            f'{adresse} übergeben.'
        ))
