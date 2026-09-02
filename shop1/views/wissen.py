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
``seiten_stand.py`` (Stand und Name), ``views/legal.py`` (``WISSEN_SEITEN``
der llms.txt) und ``tests/_basis.py`` nachziehen. Die Sitemap liest dieses
Register selbst.

**Freigabe.** Jeder Beitrag trägt ``freigegeben``. Solange es ``False`` ist,
wird die Seite ausgeliefert (sie ist erreichbar, verlinkt und wird von der
Testsuite in Aufbau, Text und Barrierefreiheit geprüft), aber sie meldet
``noindex`` und steht weder in der Sitemap noch in der llms.txt. Grund
(Gegenprüfung des vierten Laufs, Auflage 3): die Beiträge nennen Sachangaben,
die im Projekt nicht belegt sind – Waschtemperatur, Trockner-, Weichspüler-
und Bügelregel auf der Pflegeseite, die Faustregel „fünf Zentimeter sind eine
ganze Grösse" auf der Grössenseite. Auf der eigenen Shopseite liest man eine
Pflegeanleitung als Anweisung der Verkäuferin. Erst wenn die Betreiberin die
Angaben bestätigt hat, wird ``freigegeben`` auf ``True`` gesetzt; Sitemap,
llms.txt und robots-Angabe folgen dann von selbst, ebenso die Tests
(``test_seo.WissensfreigabeTest``). Die Übersicht ``/wissen/`` folgt den
Beiträgen: sie ist indexierbar, sobald mindestens ein Beitrag freigegeben ist
– eine Übersicht, die nur auf ``noindex``-Seiten zeigt, wäre für
Suchmaschinen eine leere Seite, und ihr Kurztext wiederholt die Pflegeangaben.
"""

from django.http import Http404
from django.shortcuts import render

#: Slug → Beitrag. ``url_name`` ist der Routenname, ``template`` die Vorlage,
#: ``titel`` die sichtbare Überschrift (zugleich ``h1`` der Seite), ``kurz``
#: der Satz, mit dem die Übersicht den Beitrag ankündigt, ``freigegeben`` die
#: Bestätigung der Betreiberin (siehe Modul-Docstring).
WISSEN_BEITRAEGE = {
    'pflege-handbemalte-kleidung': {
        'url_name': 'wissen_pflege',
        'template': 'shop1/wissen/pflege.html',
        'titel': 'Wie pflege ich handbemalte Kleidung?',
        'kurz': 'Waschen auf links bei 30 °C, Trocknen an der Luft, Bügeln nur von links, '
                'Lagern ohne Druck auf die Bemalung – und was für ein einzelnes Stück '
                'von Luviq Universe gilt.',
        # Offen: 30 °C, kein Trockner, kein Weichspüler, Bügeln nur von links.
        'freigegeben': False,
    },
    'upcycling-mode-second-hand-vintage': {
        'url_name': 'wissen_upcycling',
        'template': 'shop1/wissen/upcycling.html',
        'titel': 'Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand?',
        'kurz': 'Begriffsklärung Upcycling, Second Hand und Vintage, warum ein Einzelstück '
                'nicht nachbestellbar ist und woran man Handbemalung von Druck unterscheidet.',
        # Offen: keine strittige Zahl, aber die Auflage nennt alle drei Beiträge.
        'freigegeben': False,
    },
    'groesse-bei-einzelstuecken': {
        'url_name': 'wissen_groesse',
        'template': 'shop1/wissen/groesse.html',
        'titel': 'Wie finde ich bei Einzelstücken die richtige Größe?',
        'kurz': 'Maße mit der eigenen Kleidung vergleichen statt aufs Etikett zu vertrauen, '
                'warum Vintage-Schnitte abweichen und wie man vor dem Kauf nachfragt.',
        # Offen: „fünf Zentimeter Unterschied in der Brustweite sind eine ganze Grösse".
        'freigegeben': False,
    },
}


def freigegebene_beitraege():
    """Slug → Beitrag, nur die von der Betreiberin bestätigten Beiträge.

    Das ist die Menge, die Sitemap (``views/legal.py``) und llms.txt nennen
    und die ohne ``noindex`` ausgeliefert wird.
    """
    return {slug: b for slug, b in WISSEN_BEITRAEGE.items() if b.get('freigegeben')}


def uebersicht_indexierbar():
    """True, sobald mindestens ein Beitrag freigegeben ist (siehe Docstring)."""
    return bool(freigegebene_beitraege())


def wissen(request):
    """Übersicht des Wissensbereichs mit allen angemeldeten Beiträgen."""
    beitraege = [{'slug': slug, **beitrag} for slug, beitrag in WISSEN_BEITRAEGE.items()]
    return render(request, 'shop1/wissen/uebersicht.html', {
        'beitraege': beitraege,
        'indexierbar': uebersicht_indexierbar(),
    })


def wissen_beitrag(request, slug):
    """Ein einzelner Beitrag. ``slug`` kommt als festes Argument aus der Route.

    Der 404-Fall kann über die erzeugten Routen nicht eintreten; er bleibt als
    Schutz, falls die View einmal an eine freie ``<slug>``-Route gehängt wird.
    """
    beitrag = WISSEN_BEITRAEGE.get(slug)
    if beitrag is None:
        raise Http404(f'Kein Wissensbeitrag mit der Kennung "{slug}"')
    return render(request, beitrag['template'], {'beitrag': beitrag, 'slug': slug})
