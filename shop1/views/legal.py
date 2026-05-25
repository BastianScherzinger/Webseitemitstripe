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
        "Disallow: /verify/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    """Erzeugt eine dynamische sitemap.xml."""
    base_url = request.build_absolute_uri('/')[:-1]

    pages = [
        {'loc': '',                          'priority': '1.0', 'changefreq': 'daily'},
        {'loc': reverse('produkte'),         'priority': '0.9', 'changefreq': 'daily'},
        {'loc': reverse('gaestebuch'),       'priority': '0.8', 'changefreq': 'daily'},
        {'loc': reverse('kontakt'),          'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': reverse('ueber_uns'),        'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': reverse('impressum'),        'priority': '0.3', 'changefreq': 'yearly'},
        {'loc': reverse('datenschutz'),      'priority': '0.3', 'changefreq': 'yearly'},
        {'loc': reverse('agb'),              'priority': '0.3', 'changefreq': 'yearly'},
    ]

    for produkt in Produkt.objects.filter(aktiv=True):
        pages.append({
            'loc': reverse('produkt_detail', args=[produkt.id]),
            'priority': '0.8',
            'changefreq': 'weekly',
        })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        xml += '  <url>\n'
        xml += f'    <loc>{base_url}{page["loc"]}</loc>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml += '  </url>\n'
    xml += '</urlset>'

    return HttpResponse(xml, content_type="application/xml")


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
