import os
import threading
import requests
import json
from django.conf import settings
from django.core.mail import send_mail

def send_brevo_email(subject, html_content, recipient_email, recipient_name="", text_content=""):
    """
    Zentrale Funktion zum Versenden von Emails via Brevo API (asynchron).
    Bypass für Railway SMTP-Port-Sperren.
    """
    def _send():
        api_key = os.getenv('BREVO_API_KEY')
        sender_name = "Luviq-Shop"
        sender_email = settings.DEFAULT_FROM_EMAIL
        
        if api_key:
            # --- BREVO API ---
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key
            }
            # Brevo verlangt zwingend einen Namen im 'to' Feld, darf nicht leer sein
            final_recipient_name = recipient_name if recipient_name else "Nutzer"
            
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": recipient_email, "name": final_recipient_name}],
                "subject": subject,
                "htmlContent": html_content,
            }
            if text_content:
                payload["textContent"] = text_content
                
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                if response.status_code < 300:
                    print(f"✅ E-Mail via API erfolgreich an {recipient_email} gesendet.")
                else:
                    print(f"❌ API Fehler: {response.text}")
            except Exception as e:
                print(f"❌ API Verbindungsfehler: {str(e)}")
        else:
            # --- SMTP FALLBACK ---
            try:
                sent = send_mail(
                    subject,
                    text_content or "Bitte HTML-Ansicht aktivieren",
                    sender_email,
                    [recipient_email],
                    fail_silently=False,
                    html_message=html_content
                )
                if sent:
                    print(f"✅ E-Mail via SMTP erfolgreich an {recipient_email} gesendet.")
            except Exception as e:
                print(f"❌ SMTP Fehler: {str(e)}")

    # Im Hintergrund senden
    threading.Thread(target=_send).start()
