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
        # Pflegeangaben (30 °C, kein Trockner, kein Weichspüler, Bügeln nur von
        # links) am 02.10.2026 freigegeben (Bastian für Luisa Brehler, EIG12).
        'kurz': 'Waschen auf links bei 30 °C, kein Trockner, kein Weichspüler, Bügeln '
                'nur von links – so bleibt die Bemalung lange schön.',
        'freigegeben': True,
        'veroeffentlicht': '2026-09-01',
    },
    'upcycling-mode-second-hand-vintage': {
        'url_name': 'wissen_upcycling',
        'template': 'shop1/wissen/upcycling.html',
        'titel': 'Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand?',
        'kurz': 'Begriffsklärung Upcycling, Second Hand und Vintage, warum ein Einzelstück '
                'nicht nachbestellbar ist und woran man Handbemalung von Druck unterscheidet.',
        # Freigegeben am 02.10.2026 (Bastian für Luisa Brehler).
        'freigegeben': True,
        'veroeffentlicht': '2026-09-01',
    },
    'groesse-bei-einzelstuecken': {
        'url_name': 'wissen_groesse',
        'template': 'shop1/wissen/groesse.html',
        'titel': 'Wie finde ich bei Einzelstücken die richtige Größe?',
        'kurz': 'Maße mit der eigenen Kleidung vergleichen statt aufs Etikett zu vertrauen, '
                'warum Vintage-Schnitte abweichen und wie man vor dem Kauf nachfragt.',
        # Faustregel „fünf Zentimeter Brustweite = eine Grösse" freigegeben am
        # 02.10.2026 (Bastian für Luisa Brehler).
        'freigegeben': True,
        'veroeffentlicht': '2026-09-01',
    },
    # ENTWURF (23.10.2026): Ablauf von der Motivanfrage bis zum Stück. Nur aus
    # Belegtem (luviq_daten.FAQ_MOTIV/SCHRITTE/DAUER, Markenwissen); Luisa gibt frei.
    # Solange ``freigegeben`` False ist: erreichbar, noindex, nicht in Sitemap,
    # llms.txt, Feed und Übersicht, und kein anderer Beitrag verlinkt darauf.
    'so-entsteht-dein-motiv': {
        'url_name': 'wissen_motiv',
        'template': 'shop1/wissen/motiv.html',
        'titel': 'Wie entsteht aus meiner Idee ein handbemaltes Stück?',
        'kurz': 'Von der Richtung über die Vorschläge bis zur Bleiche mit dem Pinsel: '
                'was nach einer Motivanfrage in welcher Reihenfolge passiert.',
        'freigegeben': False,
        'veroeffentlicht': '2026-10-23',
    },
    # Zwei Ratgeber zur Technik (Analyse C8, Entwurf 30.10.2026 vormittags). Veröffentlicht
    # 30.10.2026 (Runde 3, Bastians Auftrag): auf Wahrheit geprüft – Sicherheitsangaben zu Bleiche
    # gegen Herstellerangaben (Clorox zu Wasserstoffperoxid), Gesundheitsbehörden (NJ Department of
    # Health, Hazard Alert „Mixing Cleaners“) und Fachhandel (Dharma Trading, Natriumthiosulfat)
    # abgeglichen; zu Luisas Arbeitsweise nur, was die Seite schon sagt (SCHRITTE, DAUER, PFLEGE).
    # ``bild``: ein echtes Foto zum Beitrag (sichtbar oben, Article.image, Bild-Sitemap).
    'bleach-painting': {
        'url_name': 'wissen_bleach',
        'template': 'shop1/wissen/bleach.html',
        'titel': 'Was ist Bleach Painting?',
        'kurz': 'Malen mit Bleiche auf dunklem Stoff: wie die Technik funktioniert, wie sie sich von Druck unterscheidet, welche Stoffe passen und welche Sicherheitsregeln allgemein gelten.',
        'freigegeben': True,
        'bild': {
            'muster': 'shop1/images/stuecke/engel-arbeitsplatz-45-{w}.webp',
            'breiten': (600, 900, 960), 'masse': (960, 1200),
            'alt': ('Echtes Foto: das Engel-Shirt mit dem Luviq-Zeichen auf Luisas Arbeitstisch, daneben '
                    'Pinsel, Stifte, Gummihandschuhe und ein Glas mit Bleiche'),
            'unterschrift': 'Echtes Foto: Luisas Arbeitstisch mit dem Engel-Shirt',
        },
        'veroeffentlicht': '2026-10-30T11:45:00+01:00',
    },
    'bleichfleck-uebermalen': {
        'url_name': 'wissen_bleichfleck',
        'template': 'shop1/wissen/bleichfleck.html',
        'titel': 'Bleichfleck übermalen: geht das?',
        'kurz': 'Warum ein Bleichfleck bleibt, welche Wege es gibt – Fleck ausmalen, nachfärben oder zum Motiv machen – und worauf man vorher achten sollte.',
        'freigegeben': True,
        'veroeffentlicht': '2026-10-30T11:45:00+01:00',
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
        'kurz_direktkauf': 'Bestellung ohne Konto direkt beim Stück, Pflichtangaben, Reservierung, '
                           'Rechnung per E-Mail, Vorkasse per Überweisung und Versand.',
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
        'kurz': 'Vierzehn Tage Widerrufsrecht, Online-Widerruf über „Vertrag widerrufen“, '
                'Rücksendekosten, Unregelmäßigkeiten der Bemalung und echte Mängel.',
        'freigegeben': True,
        # Beschreibt den Kaufweg: ohne Verkauf (VERKAUF_AKTIV aus) noindex
        # und nicht in Sitemap, llms.txt und Feed, siehe _sichtbar().
        'nur_mit_verkauf': True,
        'veroeffentlicht': '2026-09-07',
    },
    'konto-und-daten': {
        'url_name': 'wissen_konto',
        'template': 'shop1/wissen/konto.html',
        'titel': 'Was speichert der Shop – und brauche ich ein Konto?',
        'kurz': 'Anmeldepflicht im Warenkorb, Angaben bei der Registrierung, '
                'Besuchsprotokoll, eingebundene Dienste und wie ein Konto gelöscht wird.',
        'kurz_direktkauf': 'Kein Konto für den Kauf nötig, gespeicherte Bestelldaten, '
                           'Besuchsprotokoll, eingebundene Dienste und wie Daten gelöscht werden.',
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


def _aktuell(beitrag):
    """Der Beitrag mit dem Kurztext, der zum Kaufweg passt: mit Direktkauf ohne Konto
    (``verkauf.direktkauf_aktiv``) steht ``kurz_direktkauf`` statt ``kurz``."""
    from ..verkauf import direktkauf_aktiv
    if beitrag.get('kurz_direktkauf') and direktkauf_aktiv():
        return {**beitrag, 'kurz': beitrag['kurz_direktkauf']}
    return beitrag


def freigegebene_beitraege():
    """Slug → Beitrag, nur die von der Betreiberin bestätigten Beiträge.

    Das ist die Menge, die Sitemap (``views/legal.py``) und llms.txt nennen
    und die ohne ``noindex`` ausgeliefert wird. Beiträge zum Kaufweg zählen
    nur bei eingeschaltetem Verkauf dazu (``_sichtbar``).
    """
    return {slug: _aktuell(b) for slug, b in WISSEN_BEITRAEGE.items() if _sichtbar(b)}


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


def weiterlesen(slug, anzahl=2):
    """Die nächsten freigegebenen Beiträge nach ``slug`` für den Fuß eines Beitrags.

    Reihenfolge des Registers, rundherum (nach dem letzten kommt der erste), ohne
    den Beitrag selbst und ohne Entwürfe oder ausgeblendete Kaufweg-Beiträge:
    ein Link, den die Seite selbst nicht indexieren lässt, wäre ein Versprechen
    ohne Seite dahinter. So bekommt jeder Beitrag Textlinks zu den anderen
    (Suchbegriff als Ankertext = der Titel), statt dass nur die Übersicht sie
    kennt."""
    sichtbar = [(s, b) for s, b in WISSEN_BEITRAEGE.items() if _sichtbar(b)]
    namen = [s for s, _ in sichtbar]
    start = namen.index(slug) + 1 if slug in namen else 0
    reihe = sichtbar[start:] + sichtbar[:start]
    return [{'slug': s, **_aktuell(b)} for s, b in reihe if s != slug][:anzahl]


def wissen(request):
    """Übersicht des Wissensbereichs mit den freigegebenen Beiträgen – ohne
    Verkauf ohne die Beiträge zum Kaufweg (``nur_mit_verkauf``), und Entwürfe
    (``freigegeben=False``) stehen nie in der Liste, bis Luisa sie freigibt."""
    beitraege = [{'slug': slug, **_aktuell(beitrag), 'freigegeben': _sichtbar(beitrag)}
                 for slug, beitrag in WISSEN_BEITRAEGE.items()
                 if _sichtbar(beitrag)]
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
    beitrag = {**_aktuell(beitrag), 'freigegeben': _sichtbar(beitrag)}
    kontext = {
        'beitrag': beitrag, 'slug': slug, 'weiter': weiterlesen(slug),
        'beitragsbild': beitragsbild(beitrag), 'engel_url': engel_url()}
    from ..verkauf import direktkauf_aktiv
    if slug == 'bestellen-und-bezahlen' and direktkauf_aktiv():
        from .. import wissen_direktkauf
        kontext['faq_direkt'] = wissen_direktkauf.bestellen_faq()
    return render(request, beitrag['template'], kontext)


def beitragsbild(beitrag):
    """Das Foto eines Beitrags (``beitrag['bild']``) als ``produktbilder.Bild`` oder ``None``."""
    from .. import produktbilder
    bild = beitrag.get('bild')
    if not bild:
        return None
    breite, hoehe = bild['masse']
    spec = f"{bild['muster']}@{','.join(str(b) for b in bild['breiten'])}#{breite}x{hoehe}"
    gefunden = produktbilder.bild_aus(None, spec, breite, hoehe, bild['alt'])
    if gefunden and bild.get('unterschrift'):
        from dataclasses import replace
        gefunden = replace(gefunden, unterschrift=bild['unterschrift'])
    return gefunden


def engel_url():
    """Adresse der Stückseite des Engel-Shirts, wenn es aktiv ist – sonst leer (kein toter Link)."""
    from .. import luviq_daten
    from ..models import Produkt
    produkt = Produkt.objects.filter(slug=luviq_daten.ENGEL_STUECK['slug'], aktiv=True).first()
    return produkt.get_absolute_url() if produkt else ''


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
        """Nennt nur Beiträge, die der Feed auch führt (EIG128): vorher stand hier
        „Pflege, Upcycling und Größen“, obwohl genau diese drei Beiträge nicht
        freigegeben sind und der Feed leer war. Die Titel kommen aus dem Register
        (``freigegebene_beitraege``), nicht aus einer zweiten Abschrift; ohne
        freigegebenen Beitrag sagt die Beschreibung das ehrlich."""
        titel = [b['titel'] for b in freigegebene_beitraege().values()]
        if not titel:
            return ('Wissensbereich von Luviq Universe: zurzeit sind keine '
                    'Beiträge veröffentlicht.')
        return ('Beiträge aus dem Wissensbereich von Luviq Universe: '
                + '; '.join(titel) + '.')

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
        roh = item['veroeffentlicht']
        if 'T' in roh:  # ISO 8601 mit Uhrzeit und Zone (neue Beiträge)
            return datetime.fromisoformat(roh)
        tag = date.fromisoformat(roh)
        return timezone.make_aware(datetime.combine(tag, time.min))
