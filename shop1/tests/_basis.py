"""Gemeinsame Grundlage aller Tests – Testclient, Testdaten, Seitenliste.

Kein Testmodul (Name beginnt nicht mit ``test``), wird nur importiert.
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Produkt


class LuviqTestCase(TestCase):
    """Basisklasse für alle Tests dieser App.

    Zwei Eigenheiten des Projekts machen sie nötig:

    1. ``SECURE_SSL_REDIRECT = not DEBUG`` (``mainweb/settings.py``) beantwortet
       im Betriebsmodus **jeden** HTTP-Abruf mit einer 301 auf ``https://``.
       Ein Testclient-Abruf ohne ``secure=True`` erreicht die View also nie und
       jeder Statuscode-Vergleich prüfte nur die Weiterleitung. Deshalb laufen
       alle Abrufe über :meth:`hole` und :meth:`sende`, die ``secure=True``
       setzen. Direkte ``self.client.get``-Aufrufe sind in dieser Suite falsch.
    2. ``WerbungRouter`` leitet ``VisitorLog`` in die Datenbank ``pystore``.
       ``PageVisitMiddleware`` schreibt dort bei **jedem** Seitenabruf. Ohne
       ``databases`` scheitert jeder Seitentest an einer gesperrten Verbindung.
    """

    databases = {'default', 'pystore'}

    def hole(self, pfad, **kwargs):
        """GET über HTTPS – siehe Klassendokumentation, Punkt 1."""
        return self.client.get(pfad, secure=True, **kwargs)

    def sende(self, pfad, daten=None, **kwargs):
        """POST über HTTPS – siehe Klassendokumentation, Punkt 1."""
        return self.client.post(pfad, daten or {}, secure=True, **kwargs)


def erzeuge_produkt(name='Testjacke', **felder):
    """Legt ein aktives Produkt mit Pflichtfeldern an."""
    felder.setdefault('preis', Decimal('49.90'))
    felder.setdefault('beschreibung', 'Handbemaltes Einzelstück aus Alsfeld.')
    felder.setdefault('aktiv', True)
    return Produkt.objects.create(name=name, **felder)


def erzeuge_benutzer(username='kundin', passwort='ein-langes-testpasswort', **felder):
    """Legt einen normalen, nicht privilegierten Benutzer an."""
    return User.objects.create_user(username=username, password=passwort, **felder)


#: Öffentliche HTML-Seiten – ohne Anmeldung erreichbar, müssen 200 liefern.
#: Bricht hier eine Adresse weg, ist die Seite für Besucher und Suchmaschinen
#: verschwunden; das ist der teuerste Schaden, den eine Änderung anrichten kann.
OEFFENTLICHE_SEITEN = [
    '/',
    '/produkte/',
    '/kontakt/',
    '/ueber_uns/',
    '/liefergebiet/',
    '/gaestebuch/',
    '/impressum/',
    '/datenschutz/',
    '/agb/',
    '/login/',
    '/register/',
    '/password-reset/',
    '/password-reset/done/',
    '/reset/done/',
]

#: Inhaltsseiten: die Teilmenge von OEFFENTLICHE_SEITEN, die in den Suchindex
#: gehört. Die Anmelde- und Passwortseiten stehen bewusst nicht darin – sie
#: sind in robots.txt gesperrt und tragen bauartbedingt keine Überschrift.
INHALTSSEITEN = [
    '/',
    '/produkte/',
    '/kontakt/',
    '/ueber_uns/',
    '/liefergebiet/',
    '/gaestebuch/',
    '/impressum/',
    '/datenschutz/',
    '/agb/',
]

#: Pflichtseiten nach deutschem Recht – ihr Ausfall ist ein Abmahnrisiko.
PFLICHTSEITEN = ['/impressum/', '/datenschutz/', '/agb/']

#: Seiten, die eine Anmeldung verlangen. Sie dürfen niemals Inhalt zeigen und
#: niemals mit einem Serverfehler antworten, sondern müssen umleiten.
GESCHUETZTE_SEITEN = [
    '/warenkorb/',
    '/checkout/',
    '/profil/',
    '/profil/change-password/',
    '/resend-verification/',
    '/delete-account/',
]

#: Admin-Panel-Adressen ohne Parameter. Zugriffsschutz wird hier geprüft,
#: weil er in ``admin_views.py`` liegt und leicht unbemerkt wegfällt.
ADMIN_SEITEN = [
    '/shop-admin/dashboard/',
    '/shop-admin/stats/',
    '/shop-admin/produkte/',
    '/shop-admin/orders/',
    '/shop-admin/werbung/',
]
