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


from .utils import send_brevo_email

def send_verification_email(user, profile):
    """
    Sendet eine Verifikations-Email an den neuen User via Brevo API.
    """
    if not user.email:
        return
    
    # Sicherstellen, dass SITE_URL keinen Schrägstrich am Ende hat
    base_url = settings.SITE_URL.rstrip('/')
    verification_url = f"{base_url}/verify/{profile.verification_token}/"
    subject = "MeinShop – Bitte bestätige deine E-Mail-Adresse"
    
    # HTML Nachricht
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
    
    send_brevo_email(subject, html_content, user.email, recipient_name=user.username, text_content=f"Bestätige deine E-Mail: {verification_url}")
