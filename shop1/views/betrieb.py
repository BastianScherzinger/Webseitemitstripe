"""Betrieb und Sicherheit: Gesundheitsadresse und security.txt.

Beide Antworten sind kurz, ohne Vorlage und ohne Zwischenspeicher.
"""

from django.conf import settings
from django.db import DatabaseError, connection
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe

from ..mails import KONTAKT_EMAIL
from ..middleware import oeffentliche_basis


@require_safe
@never_cache
def gesundheit(request):
    """``/health/`` (BT11): 200 ``ok``, wenn Server und Datenbank antworten.

    Eine einzige Abfrage ``SELECT 1`` auf der Shop-Datenbank; die Werbe-
    Datenbank ``pystore`` bleibt außen vor, ihr Ausfall legt die Seite nicht
    lahm (``VisitorLog`` wird dort nur geschrieben). Fällt die Abfrage aus,
    antwortet die Adresse mit 503 – ein Überwachungsdienst schlägt dann an.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except DatabaseError:
        return HttpResponse('Datenbank nicht erreichbar', status=503,
                            content_type='text/plain; charset=utf-8')
    return HttpResponse('ok', content_type='text/plain; charset=utf-8')


def security_txt_text(request):
    """Der Text der ``security.txt`` nach RFC 9116.

    ``Expires`` ist ein fester Wert aus ``settings.SECURITY_TXT_EXPIRES`` und
    wird nicht je Abruf neu berechnet – eine Datei, die nie ablaufen kann,
    verfehlt den Zweck des Feldes (EIG60). ``pruefe_seite`` warnt, wenn der
    Wert in weniger als 60 Tagen abläuft.
    """
    basis = oeffentliche_basis(request)
    return '\n'.join([
        f'Contact: mailto:{KONTAKT_EMAIL}',
        f'Expires: {settings.SECURITY_TXT_EXPIRES}',
        'Preferred-Languages: de, en',
        f'Canonical: {basis}/.well-known/security.txt',
        '',
    ])


@require_safe
def security_txt(request):
    """``/.well-known/security.txt`` (SI25): wohin eine Schwachstelle gemeldet wird."""
    return HttpResponse(security_txt_text(request), content_type='text/plain; charset=utf-8')
