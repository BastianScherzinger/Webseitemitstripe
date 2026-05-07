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


def send_newsletter_email(produkt, subscribers):
    """Sendet ein wunderschönes Newsletter-Update an alle Abonnenten."""
    subject = f"✨ NEW DROP: {produkt.name} is online!"
    site_url = settings.SITE_URL.rstrip('/')
    # Wenn das Bild auf einem externen Speicher (Cloudinary) liegt, ist die URL bereits absolut
    if produkt.bild and (produkt.bild.url.startswith('http://') or produkt.bild.url.startswith('https://')):
        image_url = produkt.bild.url
    elif produkt.bild:
        image_url = f"{site_url}{produkt.bild.url}"
    else:
        image_url = ""
    
    for sub in subscribers:
        html_content = f"""
        <html>
            <body style="margin: 0; padding: 0; background-color: #050816; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #ffffff;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #050816; padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.1); border-radius: 40px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                                <!-- Header Image -->
                                {"<tr><td><img src='" + image_url + "' width='600' style='width: 100%; height: auto; display: block;' alt='" + produkt.name + "'></td></tr>" if image_url else ""}
                                
                                <!-- Content -->
                                <tr>
                                    <td style="padding: 40px; text-align: center;">
                                        <h1 style="color: #ff6a00; font-size: 32px; font-weight: 900; text-transform: uppercase; letter-spacing: 4px; margin: 0 0 20px 0; text-shadow: 0 0 20px rgba(255,106,0,0.3);">New Drop</h1>
                                        <h2 style="font-size: 24px; font-weight: 300; margin: 0 0 30px 0; color: #f4f7fb;">"{produkt.name}"</h2>
                                        
                                        <div style="height: 1px; width: 60px; background-color: #ff6a00; margin: 0 auto 30px auto;"></div>
                                        
                                        <p style="font-size: 16px; line-height: 1.6; color: rgba(255,255,255,0.6); margin-bottom: 40px; font-weight: 300;">
                                            Ein neues handbemaltes Unikat aus dem Luviq-Orbit ist soeben gelandet. 
                                            Jedes Teil ist ein 1-of-1 Statement gegen die Fast-Fashion Industrie.
                                        </p>
                                        
                                        <a href="{site_url}/produkte/{produkt.id}/" style="display: inline-block; background-color: #ff6a00; color: #ffffff; padding: 18px 40px; text-decoration: none; border-radius: 15px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px; font-size: 14px; box-shadow: 0 10px 30px rgba(255,106,0,0.3);">
                                            Jetzt Sichern
                                        </a>
                                    </td>
                                </tr>
                                
                                <!-- Footer -->
                                <tr>
                                    <td style="padding: 30px; background-color: rgba(255,255,255,0.03); text-align: center; border-top: 1px solid rgba(255,255,255,0.05);">
                                        <p style="font-size: 10px; color: rgba(255,255,255,0.2); text-transform: uppercase; letter-spacing: 2px; margin: 0;">
                                            © {settings.SITE_URL.replace('https://', '').replace('http://', '')} // Luviq Cinematic Branding
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        send_brevo_email(subject, html_content, sub.email)
