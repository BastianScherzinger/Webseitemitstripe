"""Mailversand über die Brevo-API und der Newsletter-Text: ``send_brevo_email`` (asynchron),
``send_newsletter_email`` (an die übergebenen Abonnenten; die Auswahl der bestätigten trifft der Aufrufer)."""

import os
import logging
import threading
import requests
import json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

_log = logging.getLogger('shop1')


def send_brevo_email(subject, html_content, recipient_email, recipient_name="", text_content="",
                     reply_to="", danach=None):
    """
    Zentrale Funktion zum Versenden von Emails via Brevo API (asynchron).
    Bypass für Railway SMTP-Port-Sperren.

    ``reply_to`` (MW21): die Adresse, an die „Antworten“ im Postfach geht.
    Ohne sie ginge die Antwort auf eine Kontaktanfrage an die eigene
    Versandadresse statt an den Anfragenden. Beide Wege setzen sie.

    ``danach`` (EIG10): ein Aufruf ``danach(ok)`` am Ende des Hintergrund-Threads, ``ok``
    ist ``True``, wenn Brevo bzw. der SMTP-Server die Mail angenommen hat. Damit kann
    der Aufrufer ein Scheitern festhalten, das sonst nur im Protokoll stünde. Das
    Ergebnis erreicht den Besucher nicht mehr — die Antwortseite ist da längst
    ausgeliefert —, aber die gespeicherte Anfrage (Panel) trägt es.
    """
    def _send():
        ok = False
        try:
            ok = _senden()
        finally:
            if danach is not None:
                try:
                    danach(ok)
                except Exception:
                    _log.exception("Nachbearbeitung nach dem Mailversand fehlgeschlagen")
                finally:
                    # Der Thread hat eine eigene Datenbankverbindung geöffnet; im
                    # Hauptthread (Tests, die den Thread ersetzen) bleibt sie offen.
                    if threading.current_thread() is not threading.main_thread():
                        from django.db import connections
                        connections.close_all()

    def _senden():
        api_key = os.getenv('BREVO_API_KEY')
        sender_name = "Luviq Universe"
        sender_email = settings.DEFAULT_FROM_EMAIL

        if api_key:
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key
            }
            final_recipient_name = recipient_name if recipient_name else "Nutzer"
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": recipient_email, "name": final_recipient_name}],
                "subject": subject,
                "htmlContent": html_content,
            }
            if text_content:
                payload["textContent"] = text_content
            if reply_to:
                payload["replyTo"] = {"email": reply_to}
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                if response.status_code < 300:
                    _log.info("E-Mail via Brevo API gesendet an %s", recipient_email)
                    return True
                _log.error("Brevo API Fehler (%s): %s", response.status_code, response.text)
            except Exception as e:
                _log.error("Brevo API Verbindungsfehler: %s", e)
            return False
        else:
            try:
                # EmailMultiAlternatives statt send_mail: nur so lässt sich
                # die Antwortadresse (reply_to) mitgeben.
                mail = EmailMultiAlternatives(
                    subject,
                    text_content or "Bitte HTML-Ansicht aktivieren",
                    sender_email,
                    [recipient_email],
                    reply_to=[reply_to] if reply_to else None,
                )
                mail.attach_alternative(html_content, "text/html")
                sent = mail.send(fail_silently=False)
                if sent:
                    _log.info("E-Mail via SMTP gesendet an %s", recipient_email)
                return bool(sent)
            except Exception as e:
                _log.error("SMTP Fehler: %s", e)
            return False

    # Im Hintergrund senden
    threading.Thread(target=_send).start()


def send_newsletter_email(produkt, subscribers):
    """Sendet das Newsletter-Update zu einem neuen Stück an die Abonnenten.

    Deutsch und im Look der übrigen Mails (``emails/newsletter.html``, EIG130);
    Text- und HTML-Teil. Ohne Verkauf kein Kaufaufruf in der Mail."""
    from .mails import KONTAKT_EMAIL, rendern
    from .verkauf import verkauf_aktiv
    subject = f"Neues Stück: {produkt.name}"
    site_url = settings.SITE_URL.rstrip('/')
    # Zieladresse aus der URLconf holen statt sie von Hand zusammenzusetzen.
    # Vorher stand hier f"{site_url}/produkte/{produkt.id}/" – diese Route gibt
    # es nicht (richtig waere "produkt/<int>/", siehe shop1/urls.py). Jeder
    # verschickte Newsletter fuehrte damit auf eine 404-Seite.
    produkt_url = f"{site_url}{produkt.get_absolute_url()}"
    knopf = 'Jetzt sichern' if verkauf_aktiv() else 'Stück ansehen'
    # Wenn das Bild auf einem externen Speicher (Cloudinary) liegt, ist die URL bereits absolut
    if produkt.bild and (produkt.bild.url.startswith('http://') or produkt.bild.url.startswith('https://')):
        image_url = produkt.bild.url
    elif produkt.bild:
        image_url = f"{site_url}{produkt.bild.url}"
    else:
        image_url = ""

    from .newsletter import abmelde_adresse
    for sub in subscribers:
        # Abmeldelink in jeder Mail (EIG17), je Adresse signiert; im Text und im HTML.
        abmelde_url = abmelde_adresse(sub.email)
        html_content = rendern(
            'newsletter.html',
            titel=subject,
            preheader=f'Ein neues handbemaltes Stück bei Luviq Universe: {produkt.name}',
            produkt_name=produkt.name,
            bild_url=image_url,
            link=produkt_url,
            knopf=knopf,
            abmelde_url=abmelde_url,
        )
        text_content = (
            'Hallo,\n\n'
            f'ein neues Stück ist da: „{produkt.name}“. Handbemalt, ein Einzelstück.\n\n'
            f'{knopf}: {produkt_url}\n\n'
            'Viele Grüße\nLuisa\n\n'
            'Du bekommst diese Mail, weil du dich für den Newsletter angemeldet und die Anmeldung '
            f'bestätigt hast. Abmelden über diesen Link: {abmelde_url} - oder schreib mir kurz an {KONTAKT_EMAIL}.'
        )
        send_brevo_email(subject, html_content, sub.email, text_content=text_content)
