"""Shop-Hauptseiten: Startseite, Produkte, Kontakt, Über uns."""

import hashlib
import logging
import os
import re

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError, transaction
from django.db.models import F
from django.utils import timezone
from django.views.decorators.cache import never_cache

from ..models import Produkt, Werbung, WerbungStat, KontaktAnfrage
from .. import luviq_daten, spamschutz
from ..utils import send_brevo_email
from ._helpers import zu_viele_anfragen

_log = logging.getLogger('shop1')


def betreiber_konten():
    """Benutzernamen der Betreiberin, deren Gästebuch-Beiträge die Startseite
    nicht als Stimmen anderer zeigt.

    ``ADMIN_USERNAME`` (wie im Kontextprozessor) plus ``BETREIBER_KONTEN``
    (Komma-Liste). Die Vorgabe ``luisabre`` ist das Konto, unter dem am
    18.09.2026 Beiträge auf der Live-Startseite standen und dessen Name zu
    Luisa Brehler passt (nicht bestätigt) – wer es anders weiss, setzt die
    Variable.
    """
    namen = {os.getenv('ADMIN_USERNAME', 'shopbesitzer')}
    namen.update(n.strip() for n in os.getenv('BETREIBER_KONTEN', 'luisabre').split(','))
    return sorted(n for n in namen if n)


# offen-ok: die Startseite ist die öffentlichste Seite überhaupt. Geschrieben
# wird nur der eigene Zähler der Werbeeinblendungen (WerbungStat), nichts, was
# aus der Anfrage stammt.
def startseite(request):
    """Startseite im Look „Nachtausgabe" (19.09.2026, Bauplan § 2).

    Das Archiv steht nach Nummer sortiert (Nº 001 zuerst). Das Gästebuch-Band
    mit den letzten Beiträgen ist entfallen (Bauplan § 2); ``betreiber_konten``
    bleibt stehen für den Fall, dass es zurückkommt – dann gilt wieder: keine
    Beiträge der Betreiberin als Stimmen anderer (UWG Anh. Nr. 23b/23c)."""
    produkte_galerie = Produkt.objects.filter(aktiv=True).order_by('nummer', 'erstellt_am')[:10]

    # Impressionen für aktive Werbung zählen (nur auf der Startseite). Die
    # Startseite zeigt seit dem Umbau keine Werbung mehr; die Zählung bleibt,
    # weil das pystore-Projekt sie liest.
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

    hero = dict(luviq_daten.HERO_STUECK)
    treffer = None
    for begriff in hero['suche']:
        treffer = (Produkt.objects.filter(aktiv=True, name__icontains=begriff)
                   .order_by('nummer').first())
        if treffer:
            break
    hero['nummer'] = treffer.archiv_nummer if treffer else ''

    return render(request, 'shop1/index.html', {
        'titel': 'Luviq-Shop',
        'produkte_galerie': produkte_galerie,
        'hero': hero,
        'lead': luviq_daten.LEAD,
        'markensatz': luviq_daten.MARKENSATZ,
        'richtungen': luviq_daten.RICHTUNGEN,
        'ablauf': luviq_daten.ANFRAGE_ABLAUF,
        'schritte': luviq_daten.SCHRITTE,
        'dauer': luviq_daten.DAUER,
        'zitat': luviq_daten.ZITAT,
        'zitat_quelle': luviq_daten.ZITAT_QUELLE,
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


#: Obergrenzen der Kontaktfelder (FO06). Die E-Mail-Grenze folgt RFC 5321
#: wie Djangos ``EmailField``; die übrigen lassen jeder echten Anfrage Platz.
KONTAKT_LAENGEN = {'name': 100, 'email': 254, 'betreff': 150, 'nachricht': 5000}


def kontakt_fehler(name, email, betreff, nachricht):
    """Prüft die Kontaktfelder serverseitig; gibt die Fehlermeldung oder ``None`` zurück.

    Die ``required``-Angaben im Formular sind nur Komfort – ein einziger
    Abruf ohne Browser umgeht sie (FO06)."""
    werte = {'name': name, 'email': email, 'betreff': betreff, 'nachricht': nachricht}
    if not all(werte.values()):
        return 'Bitte fülle alle Felder aus.'
    # Zeilenumbrüche zählen wie im Browser (``maxlength``, FO07) als ein
    # Zeichen – abgeschickt wird jeder als ``\r\n``.
    if any(len(werte[feld].replace('\r\n', '\n')) > grenze
           for feld, grenze in KONTAKT_LAENGEN.items()):
        return 'Eine Eingabe ist zu lang. Bitte kürze sie.'
    try:
        validate_email(email)
    except ValidationError:
        return 'Bitte gib eine gültige E-Mail-Adresse an.'
    return None


#: Zeitfenster, in dem eine wortgleiche Anfrage als Doppelklick gilt (FO03).
DOPPELT_FENSTER = 2 * 60


def _doppelt_schluessel(email, betreff, nachricht):
    inhalt = '\x00'.join((email.lower(), betreff, nachricht))
    return 'kontakt-doppelt:' + hashlib.sha256(inhalt.encode()).hexdigest()


def doppelt_abgeschickt(email, betreff, nachricht):
    """``True``, wenn dieselbe Anfrage gerade schon angenommen wurde (FO03).

    Zusammengeführt wird nur, was in Absender, Betreff und Text wortgleich ist
    – ein Doppelklick oder ein wiederholtes Absenden ohne Skript. Eine zweite
    Anfrage mit anderem Text geht normal hinaus. Wie die Drosselung liegt der
    Merker im ``LocMemCache`` und damit je Gunicorn-Prozess."""
    return not cache.add(_doppelt_schluessel(email, betreff, nachricht), 1, DOPPELT_FENSTER)


# offen-ok: das Kontaktformular richtet sich an Besucher ohne Konto. Geschrieben
# wird nur eine KontaktAnfrage (MW18), und erst nach Drosselung je IP,
# Feldprüfung (kontakt_fehler), Spamschutz und Doppelsperre.
def kontakt(request):
    # ``fehler``: der Text, den das Formular selbst ansagt (BF24). Er geht seit
    # dem 17.09.2026 nicht mehr über ``messages`` an den Meldungsbereich der
    # Seite, sondern in den Block ``role="alert"`` innerhalb des Formulars –
    # dort, wo die Pflichtfelder ihn über ``aria-describedby`` erwarten.
    fehler = None
    if request.method == 'POST':
        # .strip(): ohne das zaehlt ein Feld, in dem nur ein Leerzeichen steht,
        # als ausgefuellt – der billigste Weg, das Formular mit Leermeldungen
        # zu fluten.
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        betreff = request.POST.get('betreff', '').strip()
        nachricht = request.POST.get('nachricht', '').strip()

        # Drosselung je IP-Adresse (FO09) vor jeder Prüfung: auch eine
        # Schleife ungültiger Anfragen kostet Rechenzeit.
        if zu_viele_anfragen(request, 'kontakt'):
            return render(request, 'shop1/kontakt.html', {
                'fehler': 'Du hast gerade mehrere Nachrichten geschickt. '
                          'Bitte versuche es in einer Viertelstunde noch einmal.',
            }, status=429)

        fehler = kontakt_fehler(name, email, betreff, nachricht)
        if fehler is None:
            # Bot-Spam still verwerfen: dieselbe Bestätigung, keine Mail
            # (shop1/spamschutz.py, Anlass 16.09.2026).
            punkte, gruende = spamschutz.bewerte(request.POST)
            if punkte >= spamschutz.SCHWELLE:
                _log.warning('Kontaktformular: Spam verworfen (%s: %s)',
                             punkte, ','.join(gruende))
                return redirect('kontakt_danke')
            # Doppeltes Absenden (FO03): dieselbe Bestätigung, aber nur eine Mail.
            if doppelt_abgeschickt(email, betreff, nachricht):
                _log.info('Kontaktformular: doppelt abgeschickte Anfrage zusammengeführt')
                return redirect('kontakt_danke')
            safe_betreff = betreff.replace('\r', '').replace('\n', ' ')
            safe_name = name.replace('\r', '').replace('\n', ' ')
            safe_email = email.replace('\r', '').replace('\n', ' ')
            subject = f"Kontaktformular: {safe_betreff}"
            message = f"Neue Nachricht von {safe_name} ({safe_email}):\n\n{nachricht}"
            recipient = os.getenv('ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            # Erst speichern, dann mailen (MW18): scheitert der Versand, steht
            # die Anfrage trotzdem in der Verwaltung (Kontaktanfragen).
            try:
                with transaction.atomic():
                    anfrage = KontaktAnfrage.objects.create(
                        name=name, email=email, betreff=betreff, nachricht=nachricht)
            except DatabaseError:
                _log.exception('Kontaktformular: Anfrage nicht gespeichert')
                anfrage = None
            try:
                # reply_to (MW21): „Antworten“ im Postfach der Betreiberin geht
                # an den Anfragenden, nicht an die eigene Versandadresse.
                send_brevo_email(subject, message, recipient, recipient_name="Shop Admin", text_content=message,
                                 reply_to=safe_email)
            except Exception:
                _log.exception('Kontaktformular: Mailversand nicht gestartet')
                gestartet = False
            else:
                gestartet = True
                if anfrage is not None:
                    try:
                        KontaktAnfrage.objects.filter(pk=anfrage.pk).update(mail_gestartet=True)
                    except DatabaseError:
                        _log.exception('Kontaktformular: Versandvermerk nicht gespeichert')
            if gestartet or anfrage is not None:
                # Weiterleitung auf eine eigene Adresse statt einer Meldung auf
                # derselben Seite (KV07): nur so ist ein abgeschicktes Formular
                # als Seitenaufruf zählbar, und ein Neuladen schickt es nicht
                # ein zweites Mal ab.
                return redirect('kontakt_danke')
            # Weder gespeichert noch versandt: nicht angenommen, ein erneuter
            # Versuch darf nicht als Doppel gelten.
            cache.delete(_doppelt_schluessel(email, betreff, nachricht))
            fehler = 'Entschuldigung, es gab ein Problem beim Senden deiner Nachricht.'

    return render(request, 'shop1/kontakt.html', {
        'formzeit': spamschutz.zeitstempel(),
        'feld_falle': spamschutz.FELD_FALLE,
        'fehler': fehler,
    })


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
    """„Luisa" (``/ueber_uns/``): ihr Satz, ihr Anfang, ihre fünf Schritte –
    alles aus ``luviq_daten`` (Markenwissen vom 19.09.2026)."""
    return render(request, 'shop1/ueber_uns.html', {
        'zitat': luviq_daten.ZITAT,
        'zitat_quelle': luviq_daten.ZITAT_QUELLE,
        'schritte': luviq_daten.SCHRITTE,
        'dauer': luviq_daten.DAUER,
    })


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
    produkte_liste = Produkt.objects.filter(aktiv=True).order_by('nummer', 'erstellt_am')
    return render(request, 'shop1/produkte.html', {'produkte_liste': produkte_liste})


#: Slug-Endung eines früheren Verkaufsvermerks („custom-pants-sold"), auch mit
#: Kollisionszähler. Migration 0022 hat solche Slugs neu gebildet; dieselbe
#: Regel steht dort.
SLUG_VERMERK = re.compile(r'-(?:sold(?:-out)?|ausverkauft|verkauft)(?:-\d+)?$')


def alter_verkaufsslug(slug):
    """Das aktive Produkt, das früher unter ``slug`` mit Verkaufsvermerk stand,
    oder ``None``.

    Migration 0022 hat „(Sold)" aus dem Namen und ``-sold`` aus dem Slug
    genommen (die Stücke wurden nie verkauft). Die alte Adresse ist verlinkt
    und indexiert; statt eines Registers alter Slugs genügt die Regel: ohne
    Vermerk, mit oder ohne Kollisionszähler, das älteste passende Stück.
    """
    if not SLUG_VERMERK.search(slug or ''):
        return None
    basis = SLUG_VERMERK.sub('', slug)
    if not basis:
        return None
    return (Produkt.objects
            .filter(aktiv=True, slug__regex=rf'^{re.escape(basis)}(-[0-9]+)?$')
            .order_by('pk').first())


def produkt_detail_slug(request, slug):
    """Zeigt die Detailseite eines Produkts über seinen SEO-Slug.

    Eine alte Adresse mit Verkaufsvermerk (``/produkt/custom-pants-sold/``)
    leitet per 301 auf die heutige um (``alter_verkaufsslug``)."""
    produkt = Produkt.objects.filter(slug=slug, aktiv=True).first()
    if produkt is None:
        neu = alter_verkaufsslug(slug)
        if neu is not None and neu.slug != slug:
            return redirect(neu.get_absolute_url(), permanent=True)
        produkt = get_object_or_404(Produkt, slug=slug, aktiv=True)
    return render(request, 'shop1/produkt_detail.html', {'produkt': produkt})


def produkt_detail_redirect(request, produkt_id):
    """Redirect numerische ID → Slug-URL; generiert Slug falls noch keiner existiert."""
    produkt = get_object_or_404(Produkt, id=produkt_id, aktiv=True)
    if not produkt.slug:
        produkt.save()
    return redirect(produkt.get_absolute_url(), permanent=True)
