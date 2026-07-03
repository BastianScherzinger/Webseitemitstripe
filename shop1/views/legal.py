"""Rechtliche Seiten, SEO-Endpunkte und Newsletter."""

import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.urls import reverse

from ..models import Produkt, Subscriber


def impressum(request):
    return render(request, 'shop1/legal/impressum.html')


def datenschutz(request):
    return render(request, 'shop1/legal/datenschutz.html')


def agb(request):
    return render(request, 'shop1/legal/agb.html')


def robots_txt(request):
    """Erzeugt die robots.txt Datei für Suchmaschinen."""
    lines = [
        "User-agent: *",
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
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    """Erzeugt eine vollständige sitemap.xml mit lastmod und Bild-URLs."""
    base_url = request.build_absolute_uri('/')[:-1]

    static_pages = [
        {'loc': '',                          'priority': '1.0', 'changefreq': 'daily'},
        {'loc': reverse('produkte'),         'priority': '0.9', 'changefreq': 'daily'},
        {'loc': reverse('gaestebuch'),       'priority': '0.7', 'changefreq': 'weekly'},
        {'loc': reverse('ueber_uns'),        'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': reverse('liefergebiet'),     'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': reverse('kontakt'),          'priority': '0.6', 'changefreq': 'monthly'},
        {'loc': reverse('impressum'),        'priority': '0.2', 'changefreq': 'yearly'},
        {'loc': reverse('datenschutz'),      'priority': '0.2', 'changefreq': 'yearly'},
        {'loc': reverse('agb'),              'priority': '0.2', 'changefreq': 'yearly'},
    ]

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
    xml += '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'

    for page in static_pages:
        xml += '  <url>\n'
        xml += f'    <loc>{base_url}{page["loc"]}</loc>\n'
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
