"""Shop-Hauptseiten: Startseite, Produkte, Kontakt, Über uns."""

import logging
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.db.models import F
from django.utils import timezone
from django.views.decorators.cache import never_cache

from ..models import Produkt, Werbung, WerbungStat, Comment
from ..utils import send_brevo_email

_log = logging.getLogger('shop1')


# offen-ok: die Startseite ist die öffentlichste Seite überhaupt. Geschrieben
# wird nur der eigene Zähler der Werbeeinblendungen (WerbungStat), nichts, was
# aus der Anfrage stammt.
def startseite(request):
    produkte_galerie = Produkt.objects.filter(aktiv=True).order_by('-erstellt_am')[:8]

    # Impressionen für aktive Werbung zählen (nur auf der Startseite)
    try:
        site_name = os.getenv('SITE_NAME', 'luviq')
        today = timezone.now().date()
        for w in Werbung.objects.filter(aktiv=True):
            if w.ist_aktiv:
                Werbung.objects.filter(id=w.id).update(impressionen=F('impressionen') + 1)
                stat, _ = WerbungStat.objects.get_or_create(werbung=w, seite=site_name, datum=today)
                WerbungStat.objects.filter(id=stat.id).update(impressionen=F('impressionen') + 1)
    except Exception:
        _log.exception('Werbe-Impressionen auf der Startseite konnten nicht gezählt werden')

    recent_comments = (
        Comment.objects.filter(parent=None)
        .select_related('user')
        .prefetch_related('likes')
        .order_by('-erstellt_am')[:4]
    )

    return render(request, 'shop1/index.html', {
        'titel': 'Luviq-Shop',
        'produkte_galerie': produkte_galerie,
        'recent_comments': recent_comments,
    })


# offen-ok: der Klick auf eine Anzeige kommt von einem Besucher ohne Konto.
# Geschrieben wird nur der eigene Klickzähler (WerbungStat); die Kennung wird
# gegen eine aktive Werbung geprüft und das Ziel muss http/https sein.
def werbung_klick(request, werbung_id):
    """Zählt einen Klick auf eine Werbung (atomisch) und leitet zur Ziel-URL weiter."""
    try:
        site_name = os.getenv('SITE_NAME', 'luviq')
        today = timezone.now().date()
        w = Werbung.objects.get(id=werbung_id, aktiv=True)
        if not w.link.startswith(('http://', 'https://')):
            return redirect('home')
        Werbung.objects.filter(id=werbung_id).update(klicks=F('klicks') + 1)
        stat, _ = WerbungStat.objects.get_or_create(werbung=w, seite=site_name, datum=today)
        WerbungStat.objects.filter(id=stat.id).update(klicks=F('klicks') + 1)
        return redirect(w.link)
    except Werbung.DoesNotExist:
        return redirect('home')


def kontakte(request, produkt_id):
    return redirect('kontakt')


def kontakt(request):
    if request.method == 'POST':
        # .strip(): ohne das zaehlt ein Feld, in dem nur ein Leerzeichen steht,
        # als ausgefuellt – der billigste Weg, das Formular mit Leermeldungen
        # zu fluten.
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        betreff = request.POST.get('betreff', '').strip()
        nachricht = request.POST.get('nachricht', '').strip()

        if name and email and betreff and nachricht:
            safe_betreff = betreff.replace('\r', '').replace('\n', ' ')
            safe_name = name.replace('\r', '').replace('\n', ' ')
            safe_email = email.replace('\r', '').replace('\n', ' ')
            subject = f"Kontaktformular: {safe_betreff}"
            message = f"Neue Nachricht von {safe_name} ({safe_email}):\n\n{nachricht}"
            recipient = os.getenv('ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            try:
                send_brevo_email(subject, message, recipient, recipient_name="Shop Admin", text_content=message)
            except Exception:
                messages.error(request, 'Entschuldigung, es gab ein Problem beim Senden deiner Nachricht.')
            else:
                # Weiterleitung auf eine eigene Adresse statt einer Meldung auf
                # derselben Seite (KV07): nur so ist ein abgeschicktes Formular
                # als Seitenaufruf zählbar, und ein Neuladen schickt es nicht
                # ein zweites Mal ab.
                return redirect('kontakt_danke')
        else:
            messages.error(request, 'Bitte fülle alle Felder aus.')

    return render(request, 'shop1/kontakt.html')


@never_cache
def kontakt_danke(request):
    """Bestätigung nach dem Absenden des Kontaktformulars (``/kontakt/danke/``).

    Die Seite zeigt nichts aus der Anfrage und ist deshalb auch direkt
    abrufbar. ``noindex`` und weder in Sitemap noch in llms.txt – sie ist ein
    Ziel nach dem Absenden, keine Seite, die jemand sucht. ``never_cache``,
    damit jede Bestätigung den Server erreicht und im Besuchsprotokoll
    (``PageVisitMiddleware``) als Aufruf dieser Adresse steht.
    """
    return render(request, 'shop1/kontakt_danke.html')


def ueber_uns(request):
    return render(request, 'shop1/ueber_uns.html')


def liefergebiet(request):
    """SEO/GEO-Landingpage: Herkunft Alsfeld + Liefergebiet zwischen Fulda und Gießen."""
    orte = [
        'Fulda', 'Herbstein', 'Lauterbach', 'Grebenau', 'Ulrichstein',
        'Alsfeld', 'Romrod', 'Antrifttal', 'Kirtorf', 'Homberg (Efze)',
        'Neustadt (Hessen)', 'Schwalmstadt', 'Mücke', 'Grünberg', 'Laubach', 'Gießen',
    ]
    return render(request, 'shop1/liefergebiet.html', {'orte': orte})


def produkte(request):
    """Zeigt alle aktiven Produkte aus der Datenbank."""
    produkte_liste = Produkt.objects.filter(aktiv=True).order_by('-erstellt_am')
    return render(request, 'shop1/produkte.html', {'produkte_liste': produkte_liste})


def produkt_detail_slug(request, slug):
    """Zeigt die Detailseite eines Produkts über seinen SEO-Slug."""
    produkt = get_object_or_404(Produkt, slug=slug, aktiv=True)
    return render(request, 'shop1/produkt_detail.html', {'produkt': produkt})


def produkt_detail_redirect(request, produkt_id):
    """Redirect numerische ID → Slug-URL; generiert Slug falls noch keiner existiert."""
    produkt = get_object_or_404(Produkt, id=produkt_id, aktiv=True)
    if not produkt.slug:
        produkt.save()
    return redirect(produkt.get_absolute_url(), permanent=True)
