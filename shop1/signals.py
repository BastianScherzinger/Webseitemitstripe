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

def send_verification_email(user, profile):
    """
    Sendet eine Verifikations-Email an den neuen User asynchron in einem Thread.
    """
    if not user.email:
        return
    
    def _send():
        verification_url = f"{settings.SITE_URL}/verify/{profile.verification_token}/"
        subject = "MeinShop – Bitte bestätige deine E-Mail-Adresse"
        message = (
            f"Hallo {user.first_name or user.username},\n\n"
            f"vielen Dank für deine Registrierung bei MeinShop!\n\n"
            f"Bitte bestätige deine E-Mail-Adresse, indem du auf den folgenden Link klickst:\n\n"
            f"{verification_url}\n\n"
            f"Falls du dich nicht registriert hast, ignoriere diese E-Mail einfach.\n\n"
            f"Viele Grüße,\n"
            f"Dein MeinShop-Team"
        )
        try:
            sent = send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False, # Wir fangen es selbst ab um zu loggen
            )
            if sent:
                print(f"✅ E-Mail erfolgreich an {user.email} gesendet.")
        except Exception as e:
            print(f"❌ E-Mail Fehler an {user.email}: {str(e)}")

    # Starte den E-Mail-Versand in einem Hintergrund-Thread
    thread = threading.Thread(target=_send)
    thread.start()
