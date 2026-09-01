"""Rechtliche Seiten, SEO-Endpunkte und Newsletter."""

import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponsePermanentRedirect, JsonResponse
from django.urls import reverse

from ..models import Produkt, Subscriber


#: Stand der statischen Seiten: Routenname → Datum der letzten inhaltlichen
#: Änderung (ISO 8601). Speist das ``<lastmod>`` der Sitemap.
#:
#: Das Register wird **von Hand** nachgezogen, wenn sich der Inhalt einer
#: Seite ändert. Absichtlich kein Datei-Änderungsdatum und kein Build-
#: Zeitpunkt: beide springen bei jedem Deploy hoch und würden Suchmaschinen
#: eine Änderung vorgaukeln, die es nicht gab – dann verlieren sie das
#: Vertrauen in die Angabe. Die Daten unten sind belegt durch
#: ``git log -1 --date=short -- <Template>`` am 2026-09-01.
SEITEN_STAND = {
    'home':         '2026-09-01',
    'produkte':     '2026-09-01',
    'gaestebuch':   '2026-09-01',
    'ueber_uns':    '2026-09-01',
    'liefergebiet': '2026-09-01',
    'kontakt':      '2026-09-01',
    'impressum':    '2026-09-01',
    'datenschutz':  '2026-09-01',
    'agb':          '2026-09-01',
}


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


def llms_txt(request):
    """Kurzfassung der Seite für Antwortmaschinen (llmstxt.org).

    Enthält ausschliesslich Angaben, die auch auf der Seite selbst stehen:
    Anschrift und E-Mail aus dem Impressum, Zahlungsarten und Widerrufsfrist
    aus den AGB, Versandangaben von der Liefergebietsseite. Wo eine Angabe
    fehlt, steht sie hier nicht.
    """
    basis = request.build_absolute_uri('/')[:-1]

    zeilen = [
        "# Luviq Universe",
        "",
        "> Luviq Universe ist ein Online-Shop aus Alsfeld in Hessen. Luisa Brehler",
        "> bemalt handverlesene Second-Hand- und Vintage-Kleidung von Hand; jedes",
        "> Stueck ist ein Einzelstueck (1-of-1) und wird deutschlandweit versendet.",
        "> Einen Laden zum Reinschauen gibt es nicht, der Verkauf laeuft",
        "> ausschliesslich ueber diese Seite.",
        "",
        "## Eckdaten",
        "",
        "- Betreiberin: Luisa Brehler, Gruenberger Str. 16, 36304 Alsfeld, Deutschland",
        "- E-Mail: brehlerluisa@gmail.com",
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
