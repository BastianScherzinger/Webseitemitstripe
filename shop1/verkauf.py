"""Verkaufsschalter: ein Hebel für „Marke im Aufbau" und „Shop offen".

Solange kein Gewerbe angemeldet ist, darf die Seite keinen gewerblichen
Verkauf anbieten (§ 14 GewO, irreführende Angaben nach UWG, Pflichten im
Fernabsatz). Der Shop bleibt deshalb vollständig im Code – Warenkorb,
Bestellvorgang, PayPal, Überweisung, Willkommensrabatt, AGB –, wird aber mit
``settings.VERKAUF_AKTIV`` abgeschaltet statt entfernt. Nach der
Gewerbeanmeldung bringt ``VERKAUF_AKTIV=1`` in Railway alles zurück, ohne
neuen Code (Checkliste in ``doku/80-AUFGABEN.md``).

Drei Bausteine lesen den Schalter:

* ``verkauf_aktiv()`` – für Python-Code (Views, Sitemap, llms.txt, Mails).
* ``verkauf_kontext`` – Kontextprozessor, macht ``verkauf_aktiv`` in jeder
  Vorlage verfügbar. Vorlagen blenden damit Preise, Warenkorb und Kauf-,
  Zahlungs- und Versandsätze aus, **ohne** ein Element hinzuzufügen oder
  wegzunehmen, wo es geht – die Designwache (``test_aufbau``) erfasst Tags
  und Klassen, keinen Fliesstext.
* ``VerkaufsschalterMiddleware`` – fängt die Routen des Kaufwegs ab, bevor
  ihre View läuft, und leitet freundlich um. Nie ein Fehler 500, und die
  Views selbst bleiben unverändert.

Der Schalter wird bei jeder Anfrage aus ``settings`` gelesen (nicht beim
Import), damit ``override_settings(VERKAUF_AKTIV=True)`` in den Tests wirkt.
"""

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

#: Hinweis, den eine abgefangene Kaufroute als Meldung mitgibt.
HINWEIS = ('Der Shop öffnet mit dem ersten Drop – trag dich in die '
           'Warteliste ein, dann erfährst du es zuerst.')

#: Routennamen des Kaufwegs. Admin-Panel (/shop-admin/…), Konto und Profil
#: samt Bestellübersicht bleiben erreichbar.
KAUFROUTEN = frozenset({
    'warenkorb', 'add_to_cart', 'remove_from_cart', 'update_cart',
    'checkout', 'payment', 'payment_success', 'payment_cancel',
})

#: Routen, die per ``fetch`` aufgerufen werden und JSON erwarten. Eine
#: Weiterleitung auf eine HTML-Seite wäre für das aufrufende Skript ein
#: unlesbarer Fehler; sie bekommen eine JSON-Antwort mit Status 409.
KAUFROUTEN_JSON = frozenset({'paypal_capture'})

#: Ziel für „Auf die Warteliste": die vorhandene Newsletter-Anmeldung mit
#: Double-Opt-in auf der Startseite (Formular ``#newsletter-form``).
WARTELISTE_ANKER = '#newsletter-form'


def verkauf_aktiv():
    """True, wenn der Shop verkauft (``settings.VERKAUF_AKTIV``)."""
    return bool(getattr(settings, 'VERKAUF_AKTIV', False))


def verkauf_kontext(request):
    """Kontextprozessor: ``verkauf_aktiv`` für jede Vorlage."""
    return {'verkauf_aktiv': verkauf_aktiv()}


class VerkaufsschalterMiddleware:
    """Leitet die Kaufrouten um, solange ``VERKAUF_AKTIV`` aus ist.

    ``process_view`` läuft nach der Adressauflösung und vor der View – der
    Routenname steht fest, die View wird gar nicht erst aufgerufen. Steht
    hinter ``MessageMiddleware``, damit die Meldung ankommt.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if verkauf_aktiv():
            return None
        treffer = getattr(request, 'resolver_match', None)
        name = treffer.url_name if treffer else None
        if name in KAUFROUTEN_JSON:
            return JsonResponse({'error': HINWEIS, 'verkauf_aktiv': False}, status=409)
        if name in KAUFROUTEN:
            messages.info(request, HINWEIS)
            return redirect(reverse('home') + WARTELISTE_ANKER)
        return None
