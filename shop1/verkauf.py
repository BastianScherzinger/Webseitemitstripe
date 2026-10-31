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

from .startsperre import heute_berlin



def oeffnungs_satz(heute=None):
    """„Der Shop öffnet frühestens am 01.11.2026." – solange der Tag kommt.

    Danach (Schalter weiter aus, weil die Startliste noch nicht grün ist) nur
    „Der Shop ist noch nicht geöffnet.", damit nie ein vergangenes Datum als
    Ankündigung stehen bleibt. Mit Verkauf: leer."""
    from datetime import date
    if verkauf_aktiv():
        return ''
    tag = getattr(settings, 'VERKAUF_FRUEHESTENS', None)
    if tag and (heute or heute_berlin()) < tag:
        return f'Der Shop öffnet frühestens am {tag:%d.%m.%Y}.'
    return 'Der Shop ist noch nicht geöffnet.'


def verkauf_ab(heute=None):
    """„01.11.“ – der Tag aus ``VERKAUF_FRUEHESTENS`` für „Preis ab …“, solange er noch kommt.

    Leer, wenn der Verkauf läuft, kein Tag gesetzt ist oder der Tag vorbei ist (dann steht
    auf den Karten nur „Preis folgt“)."""
    from datetime import date
    if verkauf_aktiv():
        return ''
    tag = getattr(settings, 'VERKAUF_FRUEHESTENS', None)
    if tag and (heute or heute_berlin()) <= tag:
        return f'{tag:%d.%m.}'
    return ''


def hinweis():
    """Meldung einer abgefangenen Kaufroute, mit Öffnungsdatum."""
    return f'{oeffnungs_satz()} Trag dich in die Warteliste ein, dann erfährst du es zuerst.'

#: Routennamen des Kaufwegs. Admin-Panel (/shop-admin/…), Konto und Profil
#: samt Bestellübersicht bleiben erreichbar.
KAUFROUTEN = frozenset({
    'warenkorb', 'add_to_cart', 'remove_from_cart', 'update_cart',
    'checkout', 'payment', 'payment_success', 'payment_cancel',
    # Direktkauf ohne Konto (31.10.2026)
    'direktkauf', 'direktkauf_danke',
})

#: Der Login-Weg (Warenkorb, Kasse, PayPal) ist bei ``settings.DIREKTKAUF`` ausgeblendet:
#: Der Code bleibt, die Routen leiten auf die Startseite. Zurück mit ``DIREKTKAUF = False``.
DIREKTKAUF_GESPERRT = frozenset({
    'warenkorb', 'add_to_cart', 'remove_from_cart', 'update_cart',
    'checkout', 'payment', 'payment_success', 'payment_cancel',
})
DIREKTKAUF_GESPERRT_JSON = frozenset({'paypal_create', 'paypal_capture'})

#: Routen, die per ``fetch`` aufgerufen werden und JSON erwarten. Eine
#: Weiterleitung auf eine HTML-Seite wäre für das aufrufende Skript ein
#: unlesbarer Fehler; sie bekommen eine JSON-Antwort mit Status 409.
KAUFROUTEN_JSON = frozenset({'paypal_create', 'paypal_capture'})

#: Ziel für „Auf die Warteliste": die vorhandene Newsletter-Anmeldung mit
#: Double-Opt-in auf der Startseite (Formular ``#newsletter-form``).
WARTELISTE_ANKER = '#newsletter-form'


def verkauf_aktiv():
    """True, wenn der Shop verkauft (``settings.VERKAUF_AKTIV``)."""
    return bool(getattr(settings, 'VERKAUF_AKTIV', False))


def verkauf_kontext(request):
    """Kontextprozessor: ``verkauf_aktiv`` für jede Vorlage."""
    return {'verkauf_aktiv': verkauf_aktiv(), 'shop_oeffnet': oeffnungs_satz(),
            'verkauf_ab': verkauf_ab(), 'direktkauf_aktiv': direktkauf_aktiv()}


def direktkauf_aktiv():
    """True, wenn verkauft wird **und** der Direktkauf ohne Konto den Login-Weg ersetzt."""
    return verkauf_aktiv() and bool(getattr(settings, 'DIREKTKAUF', False))


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
            if direktkauf_aktiv():
                treffer = getattr(request, 'resolver_match', None)
                name = treffer.url_name if treffer else None
                if name in DIREKTKAUF_GESPERRT_JSON:
                    return JsonResponse({'error': 'Bestellt wird direkt auf der Stückseite.'}, status=409)
                if name in DIREKTKAUF_GESPERRT:
                    return redirect(reverse('produkte'))
            return None
        treffer = getattr(request, 'resolver_match', None)
        name = treffer.url_name if treffer else None
        if name in KAUFROUTEN_JSON:
            return JsonResponse({'error': hinweis(), 'verkauf_aktiv': False}, status=409)
        if name in KAUFROUTEN:
            messages.info(request, hinweis())
            return redirect(reverse('home') + WARTELISTE_ANKER)
        return None
