"""Rechtliche Seiten, SEO-Endpunkte und Newsletter."""

import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_page

from ..models import Produkt, Subscriber
# Das Register SEITEN_STAND (Routenname → Datum) liegt seit Schritt 16 in
# ``shop1/seiten_stand.py``, weil auch der Kontextprozessor es liest. Hier
# bleibt es unter demselben Namen erreichbar; die Sitemap unten nutzt es.
from ..seiten_stand import SEITEN_STAND  # noqa: F401 – Re-Export
# Freigabe der Wissensbeiträge (Auflage 3 des vierten Laufs): Sitemap und
# llms.txt nennen nur bestätigte Beiträge, siehe Docstring in views/wissen.py.
from .wissen import freigegebene_beitraege, uebersicht_indexierbar


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
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        f"# Kurzfassung fuer Antwortmaschinen: {request.build_absolute_uri('/llms.txt')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


#: Wissensseiten für den Abschnitt „Wissen" der llms.txt: Tripel aus
#: Routenname, Ankertext und einem Satz Beschreibung. Die Routennamen kommen
#: aus dem Register ``views/wissen.py``; der Ankertext beschreibt, was die
#: Seite beantwortet, statt sie nur zu benennen. Ausgegeben werden nur die
#: Zeilen, deren Beitrag freigegeben ist (``wissen_routen_fuer_llms``); ist
#: danach nichts übrig, erscheint der Abschnitt nicht – eine leere
#: Überschrift wäre für Antwortmaschinen ein Versprechen ohne Inhalt.
WISSEN_SEITEN = [
    ('wissen', 'Wissen: Uebersicht',
     'Einstieg in die Beitraege zu Pflege, Upcycling-Begriff und Groessenwahl; nennt, woher die Angaben stammen'),
    ('wissen_pflege', 'Wie pflege ich handbemalte Kleidung?',
     'Waschen auf links bei 30 Grad, Trocknen an der Luft, Buegeln nur von links, Lagern ohne Druck auf die Bemalung, Flecken'),
    ('wissen_upcycling', 'Was ist Upcycling-Mode - und was unterscheidet sie von Second Hand?',
     'Begriffsklaerung Upcycling, Second Hand und Vintage; warum ein Einzelstueck nicht nachbestellbar ist; Handbemalung von Druck unterscheiden'),
    ('wissen_groesse', 'Wie finde ich bei Einzelstuecken die richtige Groesse?',
     'Masse mit eigener Kleidung vergleichen statt Etikett, warum Vintage-Schnitte abweichen, vorab nachfragen, Widerruf'),
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
    basis = request.build_absolute_uri('/')[:-1]

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
    ]

    return HttpResponse("\n".join(zeilen) + "\n",
                        content_type="text/plain; charset=utf-8")


@cache_page(AUSGABE_CACHE_SEKUNDEN)
def sitemap_xml(request):
    """Erzeugt eine vollständige sitemap.xml mit lastmod und Bild-URLs."""
    base_url = request.build_absolute_uri('/')[:-1]

    # 'home' behält absichtlich den leeren Pfad: die Startseite steht seit
    # jeher ohne Schrägstrich am Ende in der Sitemap, und eine andere
    # Schreibweise wäre für Google eine neue Adresse.
    static_pages = [
        {'name': 'home',         'loc': '',                      'priority': '1.0', 'changefreq': 'daily'},
        {'name': 'produkte',     'loc': reverse('produkte'),     'priority': '0.9', 'changefreq': 'daily'},
        {'name': 'gaestebuch',   'loc': reverse('gaestebuch'),   'priority': '0.7', 'changefreq': 'weekly'},
        {'name': 'ueber_uns',    'loc': reverse('ueber_uns'),    'priority': '0.7', 'changefreq': 'monthly'},
        {'name': 'liefergebiet', 'loc': reverse('liefergebiet'), 'priority': '0.7', 'changefreq': 'monthly'},
        {'name': 'kontakt',      'loc': reverse('kontakt'),      'priority': '0.6', 'changefreq': 'monthly'},
        {'name': 'datenschutz',  'loc': reverse('datenschutz'),  'priority': '0.2', 'changefreq': 'yearly'},
        {'name': 'agb',          'loc': reverse('agb'),          'priority': '0.2', 'changefreq': 'yearly'},
    ]
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


def newsletter_subscribe(request):
    """Abonniert den Newsletter."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
        except Exception:
            email = request.POST.get('email', '').strip()

        if not email:
            return JsonResponse({'error': 'Bitte gib eine gültige Email an.'}, status=400)

        if Subscriber.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Du bist bereits im Orbit angemeldet!'}, status=200)

        Subscriber.objects.create(email=email)
        return JsonResponse({'message': 'Erfolgreich zum Newsletter angemeldet!'}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=405)
