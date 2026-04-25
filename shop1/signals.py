from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal: Erstelle automatisch ein UserProfile, wenn ein neuer User erstellt wird
    """
    if created:
        profile = UserProfile.objects.create(user=instance)
        # Verifikations-Email senden (aber nicht für Superuser)
        if not instance.is_superuser:
            send_verification_email(instance, profile)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal: Speichere das UserProfile, wenn der User gespeichert wird
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)


import threading
import requests
import json

def send_verification_email(user, profile):
    """
    Sendet eine Verifikations-Email an den neuen User asynchron.
    Nutzt vorrangig die Brevo API (stabil auf Railway), sonst SMTP.
    """
    if not user.email:
        return
    
    def _send():
        api_key = os.getenv('BREVO_API_KEY')
        verification_url = f"{settings.SITE_URL}/verify/{profile.verification_token}/"
        subject = "MeinShop – Bitte bestätige deine E-Mail-Adresse"
        sender_name = "MeinShop"
        sender_email = settings.DEFAULT_FROM_EMAIL
        
        # HTML Nachricht für besseres Aussehen
        html_content = f"""
        <html>
            <body>
                <h2>Hallo {user.first_name or user.username},</h2>
                <p>vielen Dank für deine Registrierung bei MeinShop!</p>
                <p>Bitte bestätige deine E-Mail-Adresse, indem du auf den folgenden Button klickst:</p>
                <a href="{verification_url}" style="background-color: #0d6efd; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">E-Mail bestätigen</a>
                <p>Oder kopiere diesen Link in deinen Browser:<br>{verification_url}</p>
                <p>Viele Grüße,<br>Dein MeinShop-Team</p>
            </body>
        </html>
        """
        
        if api_key:
            # --- WEG A: BREVO API (Beste Lösung für Railway) ---
            print(f"DEBUG: Versuche E-Mail via Brevo API zu senden...")
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key
            }
            payload = {
                "sender": {"name": sender_name, "email": sender_email},
                "to": [{"email": user.email, "name": user.username}],
                "subject": subject,
                "htmlContent": html_content
            }
            try:
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                if response.status_code < 300:
                    print(f"✅ E-Mail via API erfolgreich an {user.email} gesendet.")
                else:
                    print(f"❌ API Fehler: {response.text}")
            except Exception as e:
                print(f"❌ API Verbindungsfehler: {str(e)}")
        else:
            # --- WEG B: KLASSISCHES SMTP (Fallback) ---
            print(f"DEBUG: Versuche E-Mail via SMTP zu senden...")
            try:
                from django.core.mail import send_mail
                sent = send_mail(
                    subject,
                    f"Bitte bestätige deine E-Mail: {verification_url}",
                    sender_email,
                    [user.email],
                    fail_silently=False,
                )
                if sent:
                    print(f"✅ E-Mail via SMTP erfolgreich an {user.email} gesendet.")
            except Exception as e:
                print(f"❌ SMTP Fehler: {str(e)}")

    # Hintergrund-Thread starten
    threading.Thread(target=_send).start()
