"""Shop-Hauptseiten: Startseite, Produkte, Kontakt, Über uns."""

import os

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.db.models import F
from django.utils import timezone

from ..models import Produkt, Werbung, WerbungStat
from ..utils import send_brevo_email


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
        pass

    return render(request, 'shop1/index.html', {
        'titel': 'Luviq-Shop',
        'anzahl': 42,
        'produkte_galerie': produkte_galerie,
    })


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
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        betreff = request.POST.get('betreff', '')
        nachricht = request.POST.get('nachricht', '')

        if name and email and betreff and nachricht:
            safe_betreff = betreff.replace('\r', '').replace('\n', ' ')
            safe_name = name.replace('\r', '').replace('\n', ' ')
            safe_email = email.replace('\r', '').replace('\n', ' ')
            subject = f"Kontaktformular: {safe_betreff}"
            message = f"Neue Nachricht von {safe_name} ({safe_email}):\n\n{nachricht}"
            recipient = os.getenv('ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            try:
                send_brevo_email(subject, message, recipient, recipient_name="Shop Admin", text_content=message)
                messages.success(request, 'Deine Nachricht wurde erfolgreich gesendet! Wir melden uns in Kürze.')
            except Exception:
                messages.error(request, 'Entschuldigung, es gab ein Problem beim Senden deiner Nachricht.')
        else:
            messages.error(request, 'Bitte fülle alle Felder aus.')

    return render(request, 'shop1/kontakt.html')


def ueber_uns(request):
    return render(request, 'shop1/ueber_uns.html')


def produkte(request):
    """Zeigt alle aktiven Produkte aus der Datenbank."""
    produkte_liste = Produkt.objects.filter(aktiv=True).order_by('-erstellt_am')
    return render(request, 'shop1/produkte.html', {'produkte_liste': produkte_liste})


def produkt_detail(request, produkt_id):
    """Zeigt die Detailseite eines einzelnen Produkts."""
    produkt = get_object_or_404(Produkt, id=produkt_id, aktiv=True)
    return render(request, 'shop1/produkt_detail.html', {'produkt': produkt})
