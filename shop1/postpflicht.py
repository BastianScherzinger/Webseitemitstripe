"""Zustandsändernde Adressen nur per POST (Beim Kunden Nr. 10, EIG85).

Ein GET darf nichts verändern: Er ist von der CSRF-Prüfung ausgenommen, wird von
Vorab-Laden, Link-Prüfern und fremden Seiten (``<img src="…">``) ausgelöst. Wer
eine solche Adresse per GET aufruft – ein alter Lesezeichen-Link, ein
Vorab-Laden –, wird auf die Übersicht zurückgeschickt, ohne dass etwas passiert.
"""

from functools import wraps

from django.shortcuts import redirect


def nur_post(ziel):
    """Dekorator: andere Methoden als POST leiten auf ``ziel`` (Routenname) um.

    ``@login_required``/``@admin_required`` stehen **außen**, damit
    Nicht-Angemeldete weiter zuerst zur Anmeldung kommen.
    """
    def dekorator(view):
        @wraps(view)
        def umhuellung(request, *args, **kwargs):
            if request.method != 'POST':
                return redirect(ziel)
            return view(request, *args, **kwargs)
        return umhuellung
    return dekorator
