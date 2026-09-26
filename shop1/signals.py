"""Signale: am Benutzerkonto Profil anlegen und die Bestätigungsmail verschicken,
am Produkt die geänderte Adresse per IndexNow melden.

Eingebunden in ``apps.py`` (``ready``); die Mail geht über die Brevo-API
(``utils.send_brevo_email``), nicht über SMTP.
"""

import logging

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse
from . import indexnow
from .models import Produkt, UserProfile

_log = logging.getLogger('shop1')


@receiver(post_save, sender=Produkt)
@receiver(post_delete, sender=Produkt)
def produkt_an_indexnow(sender, instance, raw=False, **kwargs):
    """Neues, geändertes, verkauftes oder gelöschtes Stück melden – erst nach
    dem Abschluss der Transaktion, und nicht beim ``loaddata`` in ``start.sh``."""
    if raw or not instance.slug:
        return
    pfade = [instance.get_absolute_url(), reverse('produkte')]
    transaction.on_commit(lambda: indexnow.melden(pfade))


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
def save_profile(sender, instance, created, **kwargs):
    """
    Signal: Speichere das UserProfile, wenn der User aktualisiert wird (nicht bei Create).
    create_profile() übernimmt den Create-Fall separat.
    """
    if not created:
        try:
            instance.profile.save()
        except UserProfile.DoesNotExist:
            _log.exception('Benutzer %s hat kein UserProfile, Speichern übersprungen', instance.pk)


from .utils import send_brevo_email

def send_verification_email(user, profile):
    """
    Sendet eine Verifikations-Email an den neuen User via Brevo API.

    Ohne Benutzername oder Vorname (17.09.2026): Beides tippt der Anmeldende
    selbst, und die Mail geht an eine Adresse, die noch niemand bestaetigt hat.
    Ein Bot koennte sonst Betrugstext in fremde Postfaecher tragen - der Name
    stand hier zudem unmaskiert im HTML.
    """
    if not user.email:
        return
    
    # Sicherstellen, dass SITE_URL keinen Schrägstrich am Ende hat
    base_url = settings.SITE_URL.rstrip('/')
    verification_url = f"{base_url}/verify/{profile.verification_token}/"
    subject = "Luviq Universe – Bitte bestätige deine E-Mail-Adresse"

    # Gestaltet seit 26.09.2026 (templates/emails/besucher.html) – weiter ohne
    # Namen und ohne eingetippten Text.
    from .mails import rendern
    html_content = rendern(
        'besucher.html', titel='Bitte bestätige deine E-Mail-Adresse', kopf_label='Konto',
        preheader='Ein Klick, dann ist dein Konto bei Luviq Universe bestätigt.',
        absaetze=['danke, dass du dich bei Luviq Universe registriert hast. Bitte bestätige '
                  'deine E-Mail-Adresse mit einem Klick:'],
        link=verification_url, knopf='E-Mail bestätigen',
        nachsatz='Hast du dich nicht registriert? Dann ignoriere diese E-Mail einfach.')

    send_brevo_email(subject, html_content, user.email, recipient_name="", text_content=f"Bestätige deine E-Mail: {verification_url}")
