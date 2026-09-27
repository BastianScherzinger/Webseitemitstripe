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

Die drei später hinzugekommenen Beiträge – Bestellen und Bezahlen, Widerruf
und Rücksendung, Konto und Daten – stehen dagegen von Anfang an auf
``freigegeben``: Sie geben ausschliesslich wieder, was an anderer Stelle
dieser Seite belegt ist (AGB, Datenschutzerklärung, Impressum, Liefergebiet
und das Verhalten von Warenkorb, Bestellvorgang und Anmeldung im Code). Sie
brauchen deshalb keine Bestätigung der Betreiberin. Wo die Seite eine Frage
nicht regelt – wer das Rückporto trägt, wie schnell zurückgezahlt wird –,
sagt der Beitrag das ausdrücklich, statt eine Zahl zu nennen, die nirgends
steht.
"""

from datetime import date, datetime, time

from django.contrib.syndication.views import Feed
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from ..verkauf import verkauf_aktiv

#: Slug → Beitrag. ``url_name`` ist der Routenname, ``template`` die Vorlage,
#: ``titel`` die sichtbare Überschrift (zugleich ``h1`` der Seite), ``kurz``
#: der Satz, mit dem die Übersicht den Beitrag ankündigt, ``freigegeben`` die
#: Bestätigung der Betreiberin (siehe Modul-Docstring).
#:
#: ``veroeffentlicht`` ist der Tag, an dem der Beitrag entstanden ist – das
#: ``datePublished`` seines ``Article``-Knotens (GE15). Belegt durch
#: ``git log --diff-filter=A --date=short -- <Template>``, also den Commit,
#: der die Vorlage angelegt hat; nicht zu verwechseln mit dem Stand der
#: letzten inhaltlichen Änderung, den ``seiten_stand.py`` führt und der als
#: ``dateModified`` erscheint. Zwei Angaben, zwei Register, beide von Hand –
#: ein Datei- oder Build-Datum würde bei jedem Deploy hochspringen und eine
#: Änderung vorgaukeln, die es nicht gab.
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
        'veroeffentlicht': '2026-09-01',
    },
    'upcycling-mode-second-hand-vintage': {
        'url_name': 'wissen_upcycling',
        'template': 'shop1/wissen/upcycling.html',
        'titel': 'Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand?',
        'kurz': 'Begriffsklärung Upcycling, Second Hand und Vintage, warum ein Einzelstück '
                'nicht nachbestellbar ist und woran man Handbemalung von Druck unterscheidet.',
        # Offen: keine strittige Zahl, aber die Auflage nennt alle drei Beiträge.
        'freigegeben': False,
        'veroeffentlicht': '2026-09-01',
    },
    'groesse-bei-einzelstuecken': {
        'url_name': 'wissen_groesse',
        'template': 'shop1/wissen/groesse.html',
        'titel': 'Wie finde ich bei Einzelstücken die richtige Größe?',
        'kurz': 'Maße mit der eigenen Kleidung vergleichen statt aufs Etikett zu vertrauen, '
                'warum Vintage-Schnitte abweichen und wie man vor dem Kauf nachfragt.',
        # Offen: „fünf Zentimeter Unterschied in der Brustweite sind eine ganze Grösse".
        'freigegeben': False,
        'veroeffentlicht': '2026-09-01',
    },
    # Ab hier: Beiträge, die ausschliesslich aus dem Projekt belegte Angaben
    # wiedergeben (AGB, Datenschutzerklärung, Impressum, Liefergebiet und der
    # Code von Warenkorb, Bestellvorgang und Anmeldung). Sie brauchen keine
    # Bestätigung der Betreiberin, weil sie keine Sachangabe treffen, die nicht
    # schon an anderer Stelle dieser Seite steht – deshalb ``freigegeben``.
    # Wo die Seite etwas nicht regelt (Kosten der Rücksendung, Frist der
    # Rückzahlung), sagt der Beitrag genau das, statt eine Zahl zu erfinden.
    'bestellen-und-bezahlen': {
        'url_name': 'wissen_bestellen',
        'template': 'shop1/wissen/bestellen.html',
        'titel': 'Wie bestelle und bezahle ich bei Luviq Universe?',
        'kurz': 'Konto, Warenkorb, Pflichtangaben im Bestellvorgang, PayPal oder '
                'Vorab-Überweisung, Prüfung der Zahlung, Bestätigung und Versand.',
        'freigegeben': True,
        # Beschreibt den Kaufweg: ohne Verkauf (VERKAUF_AKTIV aus) noindex
        # und nicht in Sitemap, llms.txt und Feed, siehe _sichtbar().
        'nur_mit_verkauf': True,
        'veroeffentlicht': '2026-09-07',
    },
    'widerruf-und-ruecksendung': {
        'url_name': 'wissen_widerruf',
        'template': 'shop1/wissen/widerruf.html',
        'titel': 'Widerruf und Rücksendung: was gilt bei einem Einzelstück?',
        'kurz': 'Vierzehn Tage Widerrufsrecht nach § 5 der AGB, Anschrift für die '
                'Rücksendung, Unregelmäßigkeiten der Bemalung und echte Mängel.',
        'freigegeben': True,
        # Beschreibt den Kaufweg: ohne Verkauf (VERKAUF_AKTIV aus) noindex
        # und nicht in Sitemap, llms.txt und Feed, siehe _sichtbar().
        'nur_mit_verkauf': True,
        'veroeffentlicht': '2026-09-07',
    },
    'konto-und-daten': {
        'url_name': 'wissen_konto',
        'template': 'shop1/wissen/konto.html',
        'titel': 'Was speichert der Shop – und warum braucht der Kauf ein Konto?',
        'kurz': 'Anmeldepflicht im Warenkorb, Angaben bei der Registrierung, '
                'Besuchsprotokoll, eingebundene Dienste und wie ein Konto gelöscht wird.',
        'freigegeben': True,
        # Beschreibt den Kaufweg: ohne Verkauf (VERKAUF_AKTIV aus) noindex
        # und nicht in Sitemap, llms.txt und Feed, siehe _sichtbar().
        'nur_mit_verkauf': True,
        'veroeffentlicht': '2026-09-07',
    },
}


def _sichtbar(beitrag):
    """Freigegeben – und, wenn der Beitrag den Kaufweg beschreibt
    (``nur_mit_verkauf``), nur bei eingeschaltetem Verkauf.

    Solange kein Gewerbe angemeldet ist, stehen Bestell-, Widerrufs- und
    Kontobeitrag nicht in Sitemap, llms.txt, Feed und Übersicht, und ihre
    Adresse leitet mit 302 auf ``/wissen/`` (``nur_mit_verkauf_ausgeblendet``,
    seit 18.09.2026 abends; vorher erreichbar mit Hinweis und ``noindex``).
    """
    return bool(beitrag.get('freigegeben')) and (
        verkauf_aktiv() or not beitrag.get('nur_mit_verkauf'))


def freigegebene_beitraege():
    """Slug → Beitrag, nur die von der Betreiberin bestätigten Beiträge.

    Das ist die Menge, die Sitemap (``views/legal.py``) und llms.txt nennen
    und die ohne ``noindex`` ausgeliefert wird. Beiträge zum Kaufweg zählen
    nur bei eingeschaltetem Verkauf dazu (``_sichtbar``).
    """
    return {slug: b for slug, b in WISSEN_BEITRAEGE.items() if _sichtbar(b)}


def uebersicht_indexierbar():
    """True, sobald mindestens ein Beitrag freigegeben ist (siehe Docstring)."""
    return bool(freigegebene_beitraege())


def nur_mit_verkauf_ausgeblendet(beitrag):
    """True, wenn der Beitrag den Kaufweg beschreibt und der Verkauf aus ist.

    Solche Beiträge (Bestellen, Widerruf, Konto) stehen dann nicht in der
    Übersicht, und ihre Adresse leitet mit 302 auf ``/wissen/`` – ein Text
    über Warenkorb, PayPal und Versand passt nicht zu einer Seite, die nichts
    verkauft. 302 statt 301: die Adresse kommt mit ``VERKAUF_AKTIV=1`` zurück.
    """
    return bool(beitrag.get('nur_mit_verkauf')) and not verkauf_aktiv()


def wissen(request):
    """Übersicht des Wissensbereichs mit allen angemeldeten Beiträgen –
    ohne Verkauf ohne die Beiträge zum Kaufweg (``nur_mit_verkauf``)."""
    beitraege = [{'slug': slug, **beitrag, 'freigegeben': _sichtbar(beitrag)}
                 for slug, beitrag in WISSEN_BEITRAEGE.items()
                 if not nur_mit_verkauf_ausgeblendet(beitrag)]
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
    if nur_mit_verkauf_ausgeblendet(beitrag):
        return redirect('wissen')
    # ``freigegeben`` im Kontext ist die wirksame Freigabe (samt
    # Verkaufsschalter); die Vorlagen setzen danach ``noindex``.
    beitrag = {**beitrag, 'freigegeben': _sichtbar(beitrag)}
    return render(request, beitrag['template'], {'beitrag': beitrag, 'slug': slug})


class WissenFeed(Feed):
    """RSS-Feed des Wissensbereichs unter ``/feed/`` (GE32).

    **Wozu.** Ein Feed ist die einzige Adresse, an der ein Aggregator oder eine
    Antwortmaschine fragen kann, *was neu ist*, ohne die ganze Seite abzulaufen.
    Der Shop hat mit dem Wissensbereich Redaktionsinhalte, die dazu passen –
    die Produktseiten nicht: ein Einzelstück ist nach dem Verkauf weg, und ein
    Feed, aus dem Einträge wieder verschwinden, ist für einen Leser kaputt.

    **Was drinsteht.** Dieselbe Menge wie in Sitemap und llms.txt: nur die von
    der Betreiberin freigegebenen Beiträge (``freigegebene_beitraege()``). Ein
    Beitrag mit ``noindex`` gehört in keine der drei Aufstellungen – sonst
    meldet die Seite eine Adresse an, deren Aufnahme sie selbst verbietet.

    **Die Angaben stammen aus dem Register oben**, nicht aus einer Datei- oder
    Bauzeit: ``titel`` als Überschrift, ``kurz`` als Beschreibung,
    ``veroeffentlicht`` als ``pubDate``. Ein Datum aus dem Dateisystem spränge
    bei jedem Deploy hoch und meldete eine Änderung, die es nicht gab.
    """

    title = 'Luviq Universe – Wissen'
    language = 'de'

    def description(self):
        """Ohne Verkauf ohne Bestellablauf, Widerruf und Konto – diese
        Beiträge stehen dann nicht im Feed (``freigegebene_beitraege``)."""
        if verkauf_aktiv():
            return ('Beiträge zu Bestellablauf, Widerruf, Konto und zur Pflege '
                    'handbemalter Einzelstücke aus dem Wissensbereich von Luviq Universe.')
        return ('Beiträge zu Pflege, Upcycling und Größen handbemalter Einzelstücke '
                'aus dem Wissensbereich von Luviq Universe.')

    def link(self):
        return reverse('wissen')

    def items(self):
        """Die freigegebenen Beiträge, der neueste zuerst."""
        beitraege = [{'slug': slug, **b} for slug, b in freigegebene_beitraege().items()]
        return sorted(beitraege, key=lambda b: b['veroeffentlicht'], reverse=True)

    def item_title(self, item):
        return item['titel']

    def item_description(self, item):
        return item['kurz']

    def item_link(self, item):
        return reverse(item['url_name'])

    def item_pubdate(self, item):
        """``veroeffentlicht`` als Zeitstempel in der Zeitzone der Seite.

        ``USE_TZ=True``: ein naives ``datetime`` ergäbe hier eine Warnung und
        einen ``pubDate`` ohne Zonenangabe, den jeder Leser anders auslegt.
        """
        tag = date.fromisoformat(item['veroeffentlicht'])
        return timezone.make_aware(datetime.combine(tag, time.min))
