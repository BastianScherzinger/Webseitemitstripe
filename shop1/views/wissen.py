"""Wissensbereich: Übersicht ``/wissen/`` und die Beiträge ``/wissen/<slug>/``.

Die Beiträge sind Redaktionsinhalt. Sie liegen als statische Templates unter
``shop1/templates/shop1/wissen/`` – keine Datenbank, keine Migration, kein
Admin-Formular. Das Register ``WISSEN_BEITRAEGE`` ist die einzige Stelle, an
der ein Beitrag angemeldet wird:

* ``urls.py`` baut daraus je Beitrag eine Route mit festem Pfad und **eigenem
  Routennamen**. Der eigene Name ist nötig, weil Sitemap (``lastmod``), der
  ``WebPage``-Knoten (``seiten_stand.py``) und ``llms.txt`` Seiten über den
  Routennamen ansprechen – eine gemeinsame Route ``wissen/<slug>/`` hätte für
  drei Seiten nur einen Namen und damit nur ein Änderungsdatum.
* Die Übersicht listet die Einträge in dieser Reihenfolge.

Ein neuer Beitrag heisst: Template anlegen, hier eintragen, dann in
``seiten_stand.py`` (Stand und Name), ``views/legal.py`` (Sitemap und
``WISSEN_SEITEN`` der llms.txt) und ``tests/_basis.py`` nachziehen.
"""

from django.http import Http404
from django.shortcuts import render

#: Slug → Beitrag. ``url_name`` ist der Routenname, ``template`` die Vorlage,
#: ``titel`` die sichtbare Überschrift (zugleich ``h1`` der Seite), ``kurz``
#: der Satz, mit dem die Übersicht den Beitrag ankündigt.
WISSEN_BEITRAEGE = {}


def wissen(request):
    """Übersicht des Wissensbereichs mit allen angemeldeten Beiträgen."""
    beitraege = [{'slug': slug, **beitrag} for slug, beitrag in WISSEN_BEITRAEGE.items()]
    return render(request, 'shop1/wissen/uebersicht.html', {'beitraege': beitraege})


def wissen_beitrag(request, slug):
    """Ein einzelner Beitrag. ``slug`` kommt als festes Argument aus der Route.

    Der 404-Fall kann über die erzeugten Routen nicht eintreten; er bleibt als
    Schutz, falls die View einmal an eine freie ``<slug>``-Route gehängt wird.
    """
    beitrag = WISSEN_BEITRAEGE.get(slug)
    if beitrag is None:
        raise Http404(f'Kein Wissensbeitrag mit der Kennung "{slug}"')
    return render(request, beitrag['template'], {'beitrag': beitrag, 'slug': slug})
