"""Signierte Links des Newsletters: Abmelden (EIG17).

Der Bestätigungslink (Double-Opt-in) liegt in ``views/legal.py``. Der
Abmeldelink steht in **jedem** Newsletter und führt auf eine Seite mit einem
POST-Knopf: Mailprogramme und Link-Prüfer rufen Links per GET ab, und ein
GET darf niemanden abmelden. Der Link braucht kein Konto und läuft nicht ab –
wer eine alte Mail öffnet, soll sich auch dann noch abmelden können.
"""

from django.conf import settings
from django.core import signing
from django.urls import reverse

ABMELDE_SALT = 'luviq-newsletter-abmelden'


def abmelde_token(email):
    return signing.dumps({'e': email}, salt=ABMELDE_SALT)


def abmelde_adresse(email):
    """Absolute Adresse der Abmeldeseite für diese Abonnentin."""
    return settings.SITE_URL.rstrip('/') + reverse('newsletter_abmelden') + '?t=' + abmelde_token(email)


def email_aus_token(token):
    """Die Adresse aus dem Token oder ``None`` bei ungültiger Signatur."""
    try:
        return signing.loads(token, salt=ABMELDE_SALT)['e']
    except (signing.BadSignature, KeyError, TypeError):
        return None
