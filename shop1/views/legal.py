"""Rechtliche Seiten, SEO-Endpunkte und Newsletter."""

import hashlib
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.core import signing
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_page

from .. import indexnow
from ..middleware import oeffentliche_basis
from ..models import Produkt, Subscriber
# Das Register SEITEN_STAND (Routenname → Datum) liegt seit Schritt 16 in
# ``shop1/seiten_stand.py``, weil auch der Kontextprozessor es liest. Hier
# bleibt es unter demselben Namen erreichbar; die Sitemap unten nutzt es.
from ..seiten_stand import SEITEN_STAND  # noqa: F401 – Re-Export
# Freigabe der Wissensbeiträge (Auflage 3 des vierten Laufs): Sitemap und
# llms.txt nennen nur bestätigte Beiträge, siehe Docstring in views/wissen.py.
from .wissen import freigegebene_beitraege, uebersicht_indexierbar
from ._helpers import zu_viele_anfragen
from .. import spamschutz
from ..verkauf import verkauf_aktiv

_log = logging.getLogger('shop1')


def impressum(request):
    return render(request, 'shop1/legal/impressum.html')


def datenschutz(request):
    return render(request, 'shop1/legal/datenschutz.html')


def agb(request):
    return render(request, 'shop1/legal/agb.html')


#: Crawler, die Inhalte für KI-Antworten einsammeln. Sie werden ausdrücklich
#: zugelassen: eine Seite, die sie aussperrt, kann in einer KI-Antwort nicht
#: zitiert werden. Die geschützten Bereiche gelten für sie genauso wie für
#: alle anderen — deshalb dieselben Disallow-Regeln.
ANTWORT_CRAWLER = [
    'GPTBot',            # OpenAI, Training und Abruf
    'OAI-SearchBot',     # OpenAI, ChatGPT-Suche
    'ChatGPT-User',      # OpenAI, Abruf im Auftrag einer Nutzerin
    'PerplexityBot',
    'Perplexity-User',
    'ClaudeBot',         # Anthropic
    'Claude-User',
    'Claude-SearchBot',
    'Google-Extended',   # Google Gemini / AI Overviews
    'Applebot-Extended',
    'CCBot',             # Common Crawl, Grundlage vieler Modelle
    'meta-externalagent',
    'Bytespider',
]


def robots_txt(request):
    """Erzeugt die robots.txt Datei für Suchmaschinen."""
    gesperrt = [
        "Disallow: /shop-admin/",
        "Disallow: /profil/",
        "Disallow: /warenkorb/",
        "Disallow: /checkout/",
        "Disallow: /payment/",
        "Disallow: /verify/",
        "Disallow: /login/",
        "Disallow: /logout/",
        "Disallow: /register/",
        "Disallow: /password-reset/",
        "Disallow: /reset/",
        "Disallow: /resend-verification/",
        "Disallow: /delete-account/",
    ]

    lines = ["User-agent: *"] + gesperrt + ["Allow: /", ""]

    for bot in ANTWORT_CRAWLER:
        lines.append(f"User-agent: {bot}")
        lines.extend(gesperrt)
        lines.append("Allow: /")
        lines.append("")

    lines += [
        f"Sitemap: {oeffentliche_basis(request)}/sitemap.xml",
        f"# Kurzfassung fuer Antwortmaschinen: {oeffentliche_basis(request)}/llms.txt",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def indexnow_schluessel(request):
    """Schlüsseldatei für IndexNow (``shop1/indexnow.py``); ohne Schlüssel 404."""
    wert = indexnow.schluessel()
    if not wert:
        raise Http404('IndexNow ist nicht eingerichtet.')
    return HttpResponse(wert, content_type='text/plain; charset=utf-8')


#: Wissensseiten für den Abschnitt „Wissen" der llms.txt: Tripel aus
#: Routenname, Ankertext und einem Satz Beschreibung. Die Routennamen kommen
#: aus dem Register ``views/wissen.py``; der Ankertext beschreibt, was die
#: Seite beantwortet, statt sie nur zu benennen. Ausgegeben werden nur die
#: Zeilen, deren Beitrag freigegeben ist (``wissen_routen_fuer_llms``); ist
#: danach nichts übrig, erscheint der Abschnitt nicht – eine leere
#: Überschrift wäre für Antwortmaschinen ein Versprechen ohne Inhalt.
WISSEN_SEITEN = [
    ('wissen', 'Wissen: Uebersicht',
     'Einstieg in die Beitraege zu Bestellablauf, Widerruf, Konto und Pflege handbemalter Einzelstuecke; nennt, woher die Angaben stammen'),
    ('wissen_pflege', 'Wie pflege ich handbemalte Kleidung?',
     'Waschen auf links bei 30 Grad, Trocknen an der Luft, Buegeln nur von links, Lagern ohne Druck auf die Bemalung, Flecken'),
    ('wissen_upcycling', 'Was ist Upcycling-Mode - und was unterscheidet sie von Second Hand?',
     'Begriffsklaerung Upcycling, Second Hand und Vintage; warum ein Einzelstueck nicht nachbestellbar ist; Handbemalung von Druck unterscheiden'),
    ('wissen_groesse', 'Wie finde ich bei Einzelstuecken die richtige Groesse?',
     'Masse mit eigener Kleidung vergleichen statt Etikett, warum Vintage-Schnitte abweichen, vorab nachfragen, Widerruf'),
    ('wissen_bestellen', 'Wie bestelle und bezahle ich bei Luviq Universe?',
     'Anmeldepflicht, Weg in den Warenkorb, Pflichtangaben, PayPal oder Vorab-Ueberweisung, Pruefung der Zahlung, Bestaetigung, Versand in 1-2 Werktagen'),
    ('wissen_widerruf', 'Widerruf und Ruecksendung: was gilt bei einem Einzelstueck?',
     'Vierzehn Tage Widerrufsrecht ab Erhalt, Anschrift der Anbieterin, kein Umtausch bei Unikaten, Unregelmaessigkeiten der Bemalung sind kein Mangel'),
    ('wissen_konto', 'Was speichert der Shop - und warum braucht der Kauf ein Konto?',
     'Warum der Warenkorb ein Konto verlangt, Angaben der Registrierung, Besuchsprotokoll, eingebundene Dienste, Zahlungsdaten, Kontoloeschung'),
]


def wissen_routen_fuer_llms():
    """Routennamen der Wissensseiten, die llms.txt nennen darf.

    Die Übersicht ``wissen`` nur, wenn sie indexierbar ist; jeder Beitrag nur,
    wenn er freigegeben ist. Gleiche Regel wie in der Sitemap – eine Seite mit
    ``noindex`` gehört in keine der beiden Dateien.
    """
    routen = set()
    if uebersicht_indexierbar():
        routen.add('wissen')
    routen.update(b['url_name'] for b in freigegebene_beitraege().values())
    return routen


#: Wie lange sitemap.xml und llms.txt aus dem Cache kommen. Beide Antworten
#: sind für jeden Abrufer gleich (kein Nutzerbezug, keine Session) und
#: hängen nur vom Produktbestand ab – ein neues oder geändertes Stück
#: erscheint darin spätestens nach dieser Frist. Der Schlüssel enthält
#: Schema und Host (``build_absolute_uri``), www und Railway-Adresse werden
#: also getrennt gehalten.
AUSGABE_CACHE_SEKUNDEN = 60 * 15


@cache_page(AUSGABE_CACHE_SEKUNDEN)
def llms_txt(request):
    """Kurzfassung der Seite für Antwortmaschinen (llmstxt.org).

    Enthält ausschliesslich Angaben, die auch auf der Seite selbst stehen:
    Anschrift und E-Mail aus dem Impressum, Instagram-Profil aus dem
    ``sameAs`` des Schemas (``base.html``), Zahlungsarten und Widerrufsfrist
    aus den AGB, Versandangaben von der Liefergebietsseite. Wo eine Angabe
    fehlt, steht sie hier nicht.

    Der Einleitungsabsatz (die ``>``-Zeilen) ist der Absatz, den eine
    Antwortmaschine zitiert. Er nennt deshalb Ort, Postleitzahl und die
    belegten Versandzeiten – keine Zahl darin, die nicht auch auf
    ``/liefergebiet/`` oder im Impressum steht.
    """
    basis = oeffentliche_basis(request)
    # Verkaufsschalter: ohne Verkauf keine Kauf-, Zahlungs-, Versand- oder
    # Steuerangaben, keine Preise und kein Verweis auf die AGB.
    if not verkauf_aktiv():
        return _llms_txt_ohne_verkauf(basis)

    zeilen = [
        "# Luviq Universe",
        "",
        "> Luviq Universe ist ein Online-Shop aus Alsfeld (36304) in Hessen, zwischen",
        "> Fulda und Giessen. Luisa Brehler bemalt handverlesene Second-Hand- und",
        "> Vintage-Kleidung von Hand; jedes Stueck ist ein Einzelstueck (1-of-1).",
        "> Versand deutschlandweit, in der Regel innerhalb von 1-2 Werktagen;",
        "> innerhalb Hessens ist ein Stueck meist nach 1-3 Werktagen zugestellt.",
        "> Einen Laden zum Reinschauen gibt es nicht, der Verkauf laeuft",
        "> ausschliesslich ueber diese Seite.",
        "",
        "## Eckdaten",
        "",
        "- Betreiberin: Luisa Brehler, Gruenberger Str. 16, 36304 Alsfeld, Deutschland",
        "- E-Mail: brehlerluisa@gmail.com",
        "- Instagram: https://www.instagram.com/luviq.universe/",
        "- Zahlungsarten: PayPal oder Vorab-Ueberweisung (AGB, Paragraph 4)",
        "- Preise sind Endpreise; nach Paragraph 19 UStG wird keine Umsatzsteuer",
        "  berechnet (Kleinunternehmerstatus)",
        "- Versand: in der Regel innerhalb von 1-2 Werktagen, innerhalb Hessens",
        "  meist nach 1-3 Werktagen zugestellt; Versand deutschlandweit",
        "",
        "## Seiten",
        "",
        f"- [Startseite]({basis}{reverse('home')}): Ueberblick, aktuelle Einzelstuecke",
        f"- [Alle Unikate]({basis}{reverse('produkte')}): jedes verfuegbare Einzelstueck",
        f"- [Ueber uns]({basis}{reverse('ueber_uns')}): Luisa Brehler und die Arbeitsweise",
        f"- [Motiv anfragen]({basis}{reverse('motiv_anfragen')}): eigenes Motiv beschreiben, Vorschlaege bekommen - kostenlos, keine Bestellung",
        f"- [Liefergebiet]({basis}{reverse('liefergebiet')}): Versandgebiet zwischen Fulda und Giessen, Fragen und Antworten",
        f"- [Kontakt]({basis}{reverse('kontakt')}): Anfrageformular",
        f"- [Gaestebuch]({basis}{reverse('gaestebuch')}): Rueckmeldungen von Kundinnen und Kunden",
        "",
        "## Einzelstuecke",
        "",
    ]

    produkte = Produkt.objects.filter(aktiv=True).order_by('-aktualisiert_am')[:50]
    if produkte:
        for produkt in produkte:
            beschreibung = ' '.join(produkt.beschreibung.split())[:160]
            zeilen.append(
                f"- [{produkt.name}]({basis}{produkt.get_absolute_url()}): "
                f"{produkt.preis} EUR"
                + (f" – {beschreibung}" if beschreibung else "")
            )
    else:
        zeilen.append("- Zurzeit ist kein Einzelstueck verfuegbar.")

    erlaubt = wissen_routen_fuer_llms()
    wissen_zeilen = [eintrag for eintrag in WISSEN_SEITEN if eintrag[0] in erlaubt]
    if wissen_zeilen:
        zeilen += ["", "## Wissen", ""]
        for routenname, ankertext, beschreibung in wissen_zeilen:
            zeilen.append(f"- [{ankertext}]({basis}{reverse(routenname)}): {beschreibung}")

    zeilen += [
        "",
        "## Haeufige Fragen",
        "",
        "### Was ist Luviq Universe?",
        "Ein nachhaltiger Second-Hand-Shop aus Alsfeld in Hessen. Gruenderin Luisa",
        "Brehler verwandelt handverlesene Vintage-Kleidung durch Handmalerei in",
        "1-of-1 Kunstwerke. Jedes Stueck ist ein Unikat.",
        "",
        "### Wo sitzt Luviq Universe?",
        "In Alsfeld (36304) im Vogelsbergkreis, Hessen - zwischen Fulda und",
        "Giessen. Einen Laden zum Reinschauen gibt es nicht, der Verkauf laeuft",
        "ausschliesslich ueber diese Seite.",
        "",
        "### Liefert Luviq nach Giessen, Fulda und in andere Staedte?",
        "Ja, versendet wird deutschlandweit. Innerhalb Hessens ist ein Unikat",
        "meist nach 1-3 Werktagen zugestellt.",
        "",
        "### Was verkauft Luviq Universe?",
        "Handbemalte Second-Hand- und Vintage-Kleidung, vor allem Jacken und",
        "Shirts. Jedes Stueck ist ein Einzelstueck und nur einmal zu haben.",
        "",
        "### Wie bestellt man?",
        f"Ueber diese Seite: Einzelstueck auf {basis}{reverse('produkte')} auswaehlen,",
        "in den Warenkorb legen und bestellen. Bezahlt wird per PayPal oder",
        "Vorab-Ueberweisung.",
        "",
        "### Warum gilt Luviq als nachhaltig?",
        "Statt neue Kleidung zu produzieren, wird vorhandene Vintage-Kleidung",
        "weiterverwendet und von Hand bemalt.",
        "",
        "## Rechtliches",
        "",
        f"- [Impressum]({basis}{reverse('impressum')})",
        f"- [Datenschutzerklaerung]({basis}{reverse('datenschutz')})",
        f"- [AGB und Widerrufsrecht]({basis}{reverse('agb')})",
        "",
        f"Sitemap: {basis}/sitemap.xml",
        # Der Feed (GE32) steht hier, weil llms.txt die Datei ist, die eine
        # Antwortmaschine zuerst liest: ueber ihn erfaehrt sie, was neu ist,
        # ohne die ganze Seite noch einmal abzulaufen.
        f"Feed: {basis}{reverse('wissen_feed')}",
    ]

    return HttpResponse("\n".join(zeilen) + "\n",
                        content_type="text/plain; charset=utf-8")


def _llms_txt_ohne_verkauf(basis):
    """llms.txt, solange ``VERKAUF_AKTIV`` aus ist: Marke im Aufbau.

    Nur Angaben, die bei ausgeschaltetem Verkauf auch auf der Seite stehen –
    keine Preise, keine Zahlungsarten, kein Versand, kein Paragraph 19 UStG,
    kein Verweis auf die AGB (sie gelten erst ab Eröffnung des Shops).
    """
    zeilen = [
        "# Luviq Universe",
        "",
        "> Luviq Universe ist eine Modemarke im Aufbau aus Alsfeld (36304) in Hessen,",
        "> zwischen Fulda und Giessen. Luisa Brehler bemalt handverlesene Second-Hand-",
        "> und Vintage-Kleidung von Hand; jedes Stueck ist ein Einzelstueck (1-of-1).",
        "> Die bisherigen Stuecke sind bereits vergeben und stehen im Archiv. Neue",
        "> Stuecke gibt es mit dem ersten Drop; wer davon erfahren will, traegt sich",
        "> auf der Startseite in die Warteliste ein.",
        "",
        "## Eckdaten",
        "",
        "- Verantwortlich: Luisa Brehler, Gruenberger Str. 16, 36304 Alsfeld, Deutschland",
        "- E-Mail: brehlerluisa@gmail.com",
        "- Instagram: https://www.instagram.com/luviq.universe/",
        "- Status: Marke im Aufbau, noch kein Verkauf",
        "",
        "## Seiten",
        "",
        f"- [Startseite]({basis}{reverse('home')}): Ueberblick, bisherige Stuecke, Warteliste",
        f"- [Archiv]({basis}{reverse('produkte')}): bisherige Einzelstuecke, bereits vergeben",
        f"- [Ueber uns]({basis}{reverse('ueber_uns')}): Luisa Brehler und die Arbeitsweise",
        f"- [Motiv anfragen]({basis}{reverse('motiv_anfragen')}): eigenes Motiv beschreiben, Vorschlaege bekommen - kostenlos, keine Bestellung",
        f"- [Herkunft]({basis}{reverse('liefergebiet')}): Alsfeld zwischen Fulda und Giessen",
        f"- [Kontakt]({basis}{reverse('kontakt')}): Anfrageformular",
        f"- [Gaestebuch]({basis}{reverse('gaestebuch')}): Beitraege aus der Community",
        "",
        "## Archiv: bisherige Einzelstuecke (bereits vergeben)",
        "",
    ]
    produkte = Produkt.objects.filter(aktiv=True).order_by('-aktualisiert_am')[:50]
    if produkte:
        for produkt in produkte:
            beschreibung = ' '.join(produkt.beschreibung.split())[:160]
            zeilen.append(
                f"- [{produkt.name}]({basis}{produkt.get_absolute_url()})"
                + (f": {beschreibung}" if beschreibung else "")
            )
    else:
        zeilen.append("- Zurzeit ist kein Einzelstueck eingestellt.")

    erlaubt = wissen_routen_fuer_llms()
    wissen_zeilen = [eintrag for eintrag in WISSEN_SEITEN if eintrag[0] in erlaubt]
    if wissen_zeilen:
        zeilen += ["", "## Wissen", ""]
        for routenname, ankertext, beschreibung in wissen_zeilen:
            zeilen.append(f"- [{ankertext}]({basis}{reverse(routenname)}): {beschreibung}")

    zeilen += [
        "",
        "## Haeufige Fragen",
        "",
        "### Was ist Luviq Universe?",
        "Eine Modemarke im Aufbau aus Alsfeld in Hessen. Gruenderin Luisa Brehler",
        "verwandelt handverlesene Vintage-Kleidung durch Handmalerei in 1-of-1",
        "Kunstwerke. Jedes Stueck ist ein Unikat.",
        "",
        "### Wo sitzt Luviq Universe?",
        "In Alsfeld (36304) im Vogelsbergkreis, Hessen - zwischen Fulda und",
        "Giessen. Einen Laden zum Reinschauen gibt es nicht.",
        "",
        "### Kann man bei Luviq Universe schon kaufen?",
        "Nein. Die bisherigen Stuecke sind bereits vergeben; neue gibt es mit dem",
        f"ersten Drop. Die Warteliste steht auf der Startseite {basis}{reverse('home')} -",
        "eine E-Mail-Adresse genuegt, die Anmeldung wird per Link bestaetigt.",
        "",
        "### Warum gilt Luviq als nachhaltig?",
        "Statt neue Kleidung zu produzieren, wird vorhandene Vintage-Kleidung",
        "weiterverwendet und von Hand bemalt.",
        "",
        "## Rechtliches",
        "",
        f"- [Impressum]({basis}{reverse('impressum')})",
        f"- [Datenschutzerklaerung]({basis}{reverse('datenschutz')})",
        "",
        f"Sitemap: {basis}/sitemap.xml",
        f"Feed: {basis}{reverse('wissen_feed')}",
    ]
    return HttpResponse("\n".join(zeilen) + "\n",
                        content_type="text/plain; charset=utf-8")


def _bild_xml(bild_url: str, titel: str) -> str:
    """Ein ``<image:image>``-Block, Adresse und Titel XML-sicher."""
    def esc(text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return ('    <image:image>\n'
            f'      <image:loc>{esc(bild_url)}</image:loc>\n'
            f'      <image:title>{esc(titel)}</image:title>\n'
            '    </image:image>\n')


def _seitenbilder(name: str, base_url: str) -> list[tuple[str, str]]:
    """Die Bilder, die eine statische Seite **wirklich zeigt** — Adresse und Alttext.

    Nur Startseite (Titelbild + die fünf Entstehungsschritte, beide aus
    ``luviq_daten``, derselben Quelle wie ``index.html``) und Produktübersicht
    (die aktiven Stücke). Seiten ohne Inhaltsbild bekommen bewusst keins: das
    Logo an jede Adresse zu hängen, hiesse Bilder anzumelden, die dort nicht stehen.
    """
    from django.templatetags.static import static
    from .. import luviq_daten

    def absolut(adresse):
        return adresse if adresse.startswith('http') else f"{base_url}{adresse}"

    if name == 'home':
        bilder = [(absolut(static('shop1/images/luviq/hero-panorama-1600.webp')),
                   luviq_daten.HERO_STUECK['alt'])]
        bilder += [(absolut(static(f'shop1/images/luviq/{bild}-720.webp')), alt)
                   for _titel, _text, bild, alt in luviq_daten.SCHRITTE]
        return bilder
    if name == 'produkte':
        return [(absolut(p.bild.url), f'{p.name} – Luviq Universe')
                for p in Produkt.objects.filter(aktiv=True).order_by('-aktualisiert_am')
                if p.bild]
    return []


@cache_page(AUSGABE_CACHE_SEKUNDEN)
def sitemap_xml(request):
    """Erzeugt eine vollständige sitemap.xml mit lastmod und Bild-URLs."""
    base_url = oeffentliche_basis(request)

    # 'home' behält absichtlich den leeren Pfad: die Startseite steht seit
    # jeher ohne Schrägstrich am Ende in der Sitemap, und eine andere
    # Schreibweise wäre für Google eine neue Adresse.
    static_pages = [
        {'name': 'home',         'loc': '',                      'priority': '1.0', 'changefreq': 'daily'},
        {'name': 'produkte',     'loc': reverse('produkte'),     'priority': '0.9', 'changefreq': 'daily'},
        {'name': 'gaestebuch',   'loc': reverse('gaestebuch'),   'priority': '0.7', 'changefreq': 'weekly'},
        {'name': 'ueber_uns',    'loc': reverse('ueber_uns'),    'priority': '0.7', 'changefreq': 'monthly'},
        {'name': 'motiv_anfragen', 'loc': reverse('motiv_anfragen'), 'priority': '0.8', 'changefreq': 'monthly'},
        {'name': 'liefergebiet', 'loc': reverse('liefergebiet'), 'priority': '0.7', 'changefreq': 'monthly'},
        {'name': 'kontakt',      'loc': reverse('kontakt'),      'priority': '0.6', 'changefreq': 'monthly'},
        {'name': 'datenschutz',  'loc': reverse('datenschutz'),  'priority': '0.2', 'changefreq': 'yearly'},
        {'name': 'agb',          'loc': reverse('agb'),          'priority': '0.2', 'changefreq': 'yearly'},
    ]
    # Verkaufsschalter: ohne Verkauf gelten die AGB noch nicht, die Seite
    # meldet noindex (agb.html) und gehört deshalb nicht in die Sitemap.
    if not verkauf_aktiv():
        static_pages = [p for p in static_pages if p['name'] != 'agb']
    # Wissensbereich: Redaktionsinhalt, lastmod aus demselben Register. Nur
    # freigegebene Beiträge (und die Übersicht, sobald einer freigegeben ist);
    # die übrigen liefern "noindex" und dürfen deshalb hier nicht stehen.
    if uebersicht_indexierbar():
        static_pages.append(
            {'name': 'wissen', 'loc': reverse('wissen'), 'priority': '0.6', 'changefreq': 'monthly'}
        )
    for beitrag in freigegebene_beitraege().values():
        static_pages.append({
            'name': beitrag['url_name'], 'loc': reverse(beitrag['url_name']),
            'priority': '0.6', 'changefreq': 'monthly',
        })
    # /impressum/ steht bewusst NICHT in dieser Liste: impressum.html setzt
    # meta robots auf "noindex, follow". Eine Adresse gleichzeitig zur
    # Aufnahme anzumelden und die Aufnahme zu verbieten, meldet die Search
    # Console als Fehler. Massgeblich ist die Angabe auf der Seite selbst.

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xml += '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'

    for page in static_pages:
        xml += '  <url>\n'
        xml += f'    <loc>{base_url}{page["loc"]}</loc>\n'
        xml += f'    <lastmod>{SEITEN_STAND[page["name"]]}</lastmod>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        for bild_url, titel in _seitenbilder(page['name'], base_url):
            xml += _bild_xml(bild_url, titel)
        xml += '  </url>\n'

    for produkt in Produkt.objects.filter(aktiv=True).order_by('-aktualisiert_am'):
        if produkt.slug:
            loc = reverse('produkt_detail_slug', args=[produkt.slug])
        else:
            loc = reverse('produkt_detail', args=[produkt.id])

        xml += '  <url>\n'
        xml += f'    <loc>{base_url}{loc}</loc>\n'
        xml += f'    <lastmod>{produkt.aktualisiert_am.strftime("%Y-%m-%d")}</lastmod>\n'
        xml += '    <changefreq>weekly</changefreq>\n'
        xml += '    <priority>0.8</priority>\n'

        if produkt.bild:
            bild_url = produkt.bild.url
            if not bild_url.startswith('http'):
                bild_url = f"{base_url}{bild_url}"
            escaped = bild_url.replace('&', '&amp;')
            name_esc = produkt.name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            xml += '    <image:image>\n'
            xml += f'      <image:loc>{escaped}</image:loc>\n'
            xml += f'      <image:title>{name_esc} – Luviq Universe</image:title>\n'
            xml += f'      <image:caption>Handbemaltes 1-of-1 Upcycling-Unikat: {name_esc}</image:caption>\n'
            xml += '    </image:image>\n'

        xml += '  </url>\n'

    xml += '</urlset>'
    return HttpResponse(xml, content_type='application/xml; charset=utf-8')


def produkt_uebersicht_redirect(request):
    """``/produkt/`` ohne Kennung dauerhaft auf die Produktübersicht leiten.

    Die Adresse ist der natürliche Tippfehler zu ``/produkte/`` und der
    Elternpfad jeder Produktseite ``/produkt/<slug>/``; sie lief bisher ins
    404 (Befund SU09). Eine 301 gibt Besuchern und Crawlern das Ziel, das
    sie meinen, ohne eine Seite zu ändern."""
    return HttpResponsePermanentRedirect(reverse('produkte'))


_NEWSLETTER_SALT = 'luviq-newsletter-optin'
_NEWSLETTER_GUELTIG = 7 * 24 * 3600


def _bestaetigung_senden(request, abo):
    """Bestaetigungslink an eine noch offene Adresse - hoechstens einmal am Tag.

    Die Mail enthaelt **keinen Text aus dem Formular**: Die Adresse hat niemand
    bestaetigt, und ein Bot soll hierueber nichts in fremde Postfaecher tragen.
    """
    schluessel = 'luviq-nl-' + hashlib.sha256(abo.email.lower().encode()).hexdigest()
    try:
        if not cache.add(schluessel, 1, 24 * 3600):
            return
    except Exception:
        # Ohne Cache keine Tagessperre: der Link geht trotzdem raus, der
        # Ausfall steht aber im Log statt still zu verschwinden.
        _log.exception('Newsletter: Tagessperre im Cache nicht pruefbar')
    from ..utils import send_brevo_email
    token = signing.dumps({'e': abo.email}, salt=_NEWSLETTER_SALT)
    link = settings.SITE_URL.rstrip('/') + reverse('newsletter_bestaetigen') + '?t=' + token
    from ..mails import rendern
    # Gestaltet seit 26.09.2026 (templates/emails/besucher.html) – weiter ohne
    # Text aus dem Formular.
    send_brevo_email(
        'Luviq – Bitte bestätige deine Newsletter-Anmeldung',
        rendern('besucher.html', titel='Bitte bestätige deine Anmeldung', kopf_label='Newsletter',
                preheader='Ein Klick, dann bekommst du Post, wenn es Neues von Luviq gibt.',
                absaetze=['für diese Adresse wurde der Luviq-Newsletter angemeldet. Bitte bestätige '
                          'das mit einem Klick:'],
                link=link, knopf='Anmeldung bestätigen',
                nachsatz='Warst du das nicht, ignoriere diese E-Mail einfach – ohne Bestätigung '
                         'schicken wir dir nichts.'),
        abo.email,
        text_content=f'Bitte bestätige deine Newsletter-Anmeldung: {link}\n\n'
                     'Warst du das nicht, ignoriere diese E-Mail einfach.',
    )


def newsletter_bestaetigen(request):
    """Schritt 2 des Double-Opt-in: der signierte Link aus der Mail."""
    try:
        daten = signing.loads(request.GET.get('t', ''), salt=_NEWSLETTER_SALT,
                              max_age=_NEWSLETTER_GUELTIG)
        abo = Subscriber.objects.get(email=daten['e'])
    except (signing.BadSignature, KeyError, TypeError, Subscriber.DoesNotExist):
        messages.error(request, 'Der Bestätigungslink ist ungültig oder abgelaufen.')
        return redirect('/')
    if not abo.bestaetigt:
        abo.bestaetigt = True
        abo.bestaetigt_am = timezone.now()
        abo.save(update_fields=['bestaetigt', 'bestaetigt_am'])
    messages.success(request, 'Danke! Deine Newsletter-Anmeldung ist bestätigt.')
    return redirect('/')


# offen-ok: der Abmeldelink steht in jeder Newsletter-Mail und richtet sich an
# Empfänger ohne Konto. Er trägt eine Signatur; gelöscht wird nur die Adresse
# aus dem Token, und nur per POST.
def newsletter_abmelden(request):
    """Newsletter abbestellen: GET zeigt die Seite, POST löscht die Adresse (EIG17)."""
    from ..newsletter import email_aus_token
    token = request.POST.get('t') or request.GET.get('t', '')
    email = email_aus_token(token)
    if email is None:
        messages.error(request, 'Der Abmeldelink ist ungültig. Schreib uns kurz über das Kontaktformular, '
                                'dann nehmen wir dich aus dem Verteiler.')
        return redirect('/')
    if request.method == 'POST':
        Subscriber.objects.filter(email=email).delete()
        messages.success(request, 'Du bist abgemeldet. Es kommt keine Newsletter-Post mehr an diese Adresse.')
        return redirect('/')
    return render(request, 'shop1/newsletter_abmelden.html', {'token': token})


# offen-ok: die Newsletter-Anmeldung steht auf der Startseite und richtet sich
# an Besucher ohne Konto. Geschrieben wird eine einzelne E-Mail-Adresse, und
# das unique-Feld verhindert Mehrfacheinträge derselben Adresse.
def newsletter_subscribe(request):
    """Abonniert den Newsletter.

    Zwei Wege in dieselbe Prüfung: das Skript der Startseite schickt JSON und liest die
    JSON-Antwort; ein Formular ohne JavaScript (EIG89, EIG129) schickt klassisch per POST
    und bekommt eine Weiterleitung auf die Warteliste mit einer Meldung. Erkannt wird der
    zweite Weg am ``Accept``-Kopf des Browsers (``text/html``) – Skriptaufrufe und Tests
    schicken ihn nicht."""
    if request.method == 'POST':
        klassisch = 'text/html' in request.headers.get('Accept', '')

        def antwort_fehler(text, status):
            if klassisch:
                messages.error(request, text)
                return redirect(reverse('home') + '#warteliste')
            return JsonResponse({'error': text}, status=status)

        # Drosselung je IP-Adresse (FO09): ohne sie füllt eine Schleife die
        # Abonnentenliste mit fremden Adressen.
        if zu_viele_anfragen(request, 'newsletter'):
            return antwort_fehler('Zu viele Anmeldungen in kurzer Zeit. '
                                  'Bitte versuche es später noch einmal.', 429)

        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            falle = {k: data.get(k, '') for k in (spamschutz.FELD_FALLE, spamschutz.FELD_FALLE_ALT,
                                                  spamschutz.FELD_ZEIT)}
        except (ValueError, AttributeError):
            # Kein JSON (ValueError, auch UnicodeDecodeError) oder JSON ohne
            # Objekt bzw. ohne Text unter "email" (AttributeError): dann kam
            # das Formular klassisch als POST-Felder.
            email = request.POST.get('email', '').strip()
            falle = {k: request.POST.get(k, '') for k in (spamschutz.FELD_FALLE, spamschutz.FELD_FALLE_ALT,
                                                          spamschutz.FELD_ZEIT)}

        # Serverseitige Prüfung (FO06): ``type="email"`` im Formular umgeht
        # jeder Abruf ohne Browser. 254 Zeichen ist die Länge des Modellfelds
        # (``EmailField``); ``validate_email`` selbst lässt bis zu 320 zu.
        try:
            if len(email) > 254:
                raise ValidationError('zu lang')
            validate_email(email)
        except ValidationError:
            return antwort_fehler('Bitte gib eine gültige Email an.', 400)

        # Der Antworttext ist für neue, offene und bestätigte Adressen – und für
        # verworfene Bots – derselbe: sonst verrät er, wer schon Abonnent ist.
        text_ok = ('Fast geschafft! Bitte bestätige deine Anmeldung '
                   'über den Link in der E-Mail, die wir dir geschickt haben.')

        # Bot-Spam still verwerfen (Honigtopf, Zeitfalle, Markennachahmung in der
        # Adresse): dieselbe Antwort, kein Eintrag, keine Mail.
        punkte, gruende = spamschutz.bewerte(dict(falle, email=email))
        if punkte >= spamschutz.SCHWELLE:
            _log.warning('Newsletter: Spam verworfen (%s: %s)', punkte, ','.join(gruende))
            if klassisch:
                messages.success(request, text_ok)
                return redirect(reverse('home') + '#warteliste')
            return JsonResponse({'message': text_ok}, status=200)

        # Double-Opt-in (17.09.2026). Die Antwort ist fuer neue, offene und
        # bestaetigte Adressen dieselbe - sonst verraet sie, wer schon Abonnent ist.
        abo, neu = Subscriber.objects.get_or_create(email=email)
        if not abo.bestaetigt and spamschutz.mail_budget_ok('newsletter', stunde=30, tag=150):
            _bestaetigung_senden(request, abo)
        if klassisch:
            messages.success(request, text_ok)
            return redirect(reverse('home') + '#warteliste')
        antwort = {'message': text_ok}
        if neu:
            # ``neu`` sagt dem Skript der Startseite, dass diese Anmeldung als
            # Abschluss zählt (FO08); eine Wiederholung zählt nicht.
            antwort['neu'] = True
        return JsonResponse(antwort, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=405)
