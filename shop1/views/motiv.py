"""Motiv anfragen (``/motiv-anfragen/``) – Luisas Anfrage-System, Stufe 1.

Umbau „Nachtausgabe" (19.09.2026, Bauplan § 3). Das Formular bildet Luisas
Gespräch ab: Richtung, Teil, Platzierung, was es bedeuten soll, Kontakt über
Instagram oder Mail. **Kein Preis, keine Zahlung, keine Zusage** – eine
Anfrage, keine Bestellung; deshalb ohne Gewerbe zulässig.

Gleiche Schutzschichten wie das Kontaktformular: Drosselung je IP (FO09),
Feldprüfung auf dem Server, Spamschutz (Honeypot, Zeitfalle, Punkte),
Doppelt-Sperre (FO03). Erst speichern, dann mailen (MW18). Gemailt wird nur
an Luisa (``MOTIV_EMPFAENGER``, sonst ``ADMIN_EMAIL``) – **nie** an die
eingetippte Adresse (Lehre vom 17.09.2026); die Danke-Seite sagt, dass Luisa
sich meldet.
"""

import hashlib
import logging
import os
import re

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError, transaction
from django.shortcuts import redirect, render
from django.utils.html import escape, linebreaks
from django.views.decorators.cache import never_cache

from .. import luviq_daten, spamschutz
from ..models import Motivanfrage
from ..utils import send_brevo_email
from ._helpers import zu_viele_anfragen

_log = logging.getLogger('shop1')

#: Obergrenzen der Freitextfelder, im Formular als ``maxlength`` gespiegelt.
LAENGEN = {'bedeutung': 1500, 'instagram': 31, 'email': 254}

#: Instagram-Name: ohne Link-Prüfung, nur das Muster der Plattform.
INSTAGRAM_MUSTER = re.compile(r'^@?[A-Za-z0-9._]{1,30}$')

DOPPELT_FENSTER = 2 * 60


def _auswahl(liste):
    return {schluessel for schluessel, _ in liste}


def pruefe(daten):
    """``(werte, fehler)``: bereinigte Werte und ein Fehlertext oder ``None``."""
    werte = {
        'richtung': (daten.get('richtung') or '').strip(),
        'teil': (daten.get('teil') or '').strip(),
        'platzierung': (daten.get('platzierung') or '').strip(),
        'bedeutung': (daten.get('bedeutung') or '').strip(),
        'instagram': (daten.get('instagram') or '').strip(),
        'email': (daten.get('email') or '').strip(),
    }
    if werte['richtung'] not in _auswahl(luviq_daten.RICHTUNGEN):
        return werte, 'Bitte wähl eine Richtung aus.'
    if werte['teil'] not in _auswahl(luviq_daten.TEILE):
        return werte, 'Bitte sag mir, auf welches Teil es soll.'
    if werte['platzierung'] not in _auswahl(luviq_daten.PLATZIERUNGEN):
        return werte, 'Bitte sag mir, wo das Motiv hin soll.'
    # Zeilenumbrüche zählen wie im Browser (maxlength) als ein Zeichen.
    if any(len(werte[feld].replace('\r\n', '\n')) > grenze for feld, grenze in LAENGEN.items()):
        return werte, 'Eine Eingabe ist zu lang. Bitte kürze sie.'
    if not werte['instagram'] and not werte['email']:
        return werte, 'Bitte gib deinen Instagram-Namen oder deine E-Mail-Adresse an, damit ich dir antworten kann.'
    if werte['instagram']:
        if not INSTAGRAM_MUSTER.match(werte['instagram']):
            return werte, 'Der Instagram-Name darf nur Buchstaben, Zahlen, Punkt und Unterstrich enthalten.'
        werte['instagram'] = werte['instagram'].lstrip('@')
    if werte['email']:
        try:
            validate_email(werte['email'])
        except ValidationError:
            return werte, 'Bitte gib eine gültige E-Mail-Adresse an.'
    return werte, None


def _doppelt_schluessel(werte):
    inhalt = '\x00'.join(werte[k] for k in sorted(werte)).lower()
    return 'motiv-doppelt:' + hashlib.sha256(inhalt.encode()).hexdigest()


def empfaenger():
    return settings.MOTIV_EMPFAENGER or os.getenv('ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)


def _mail(anfrage):
    """Betreff und Text der Mail an Luisa. Nutzertext wird maskiert."""
    betreff = f'Motivanfrage: {anfrage.get_richtung_display()} auf {anfrage.get_teil_display()}'
    zeilen = [
        ('Richtung', anfrage.get_richtung_display()),
        ('Teil', anfrage.get_teil_display()),
        ('Wo', anfrage.get_platzierung_display()),
        ('Instagram', f'@{anfrage.instagram}' if anfrage.instagram else '–'),
        ('E-Mail', anfrage.email or '–'),
    ]
    text = 'Neue Motivanfrage über luviq-alsfeld.com\n\n'
    text += '\n'.join(f'{k}: {v}' for k, v in zeilen)
    text += '\n\nWas es bedeuten soll:\n' + (anfrage.bedeutung or '–')
    text += '\n\nAlle Anfragen stehen im Admin-Panel unter „Motivanfragen".'
    html = ('<p>Neue Motivanfrage über luviq-alsfeld.com</p><table>'
            + ''.join(f'<tr><td><b>{escape(k)}</b></td><td>{escape(v)}</td></tr>' for k, v in zeilen)
            + '</table><p><b>Was es bedeuten soll:</b></p>'
            + (linebreaks(escape(anfrage.bedeutung)) if anfrage.bedeutung else '<p>–</p>')
            + '<p>Alle Anfragen stehen im Admin-Panel unter „Motivanfragen".</p>')
    return betreff, html, text


def _seite(request, werte=None, fehler=None, status=200):
    werte = werte or {}
    vorbelegt = request.GET.get('richtung', '')
    if not werte.get('richtung') and vorbelegt in _auswahl(luviq_daten.RICHTUNGEN):
        werte['richtung'] = vorbelegt
    return render(request, 'shop1/motiv_anfragen.html', {
        'werte': werte,
        'fehler': fehler,
        'formzeit': spamschutz.zeitstempel(),
        'feld_falle': spamschutz.FELD_FALLE,
        'richtungen': luviq_daten.RICHTUNGEN,
        'teile': luviq_daten.TEILE,
        'platzierungen': luviq_daten.PLATZIERUNGEN,
        'stationen': luviq_daten.ANFRAGE_STATIONEN,
        'laengen': LAENGEN,
    }, status=status)


# offen-ok: die Anfrage richtet sich an Besucher ohne Konto. Geschrieben wird
# nur eine Motivanfrage, und erst nach Drosselung je IP, Feldprüfung,
# Spamschutz und Doppelsperre.
def motiv_anfragen(request):
    if not settings.MOTIVANFRAGE_AKTIV:
        return render(request, 'shop1/motiv_anfragen.html', {'geschlossen': True})
    if request.method != 'POST':
        return _seite(request)

    if zu_viele_anfragen(request, 'motiv'):
        return _seite(request, fehler='Du hast gerade mehrere Anfragen geschickt. '
                                      'Bitte versuch es in einer Viertelstunde noch einmal.', status=429)

    werte, fehler = pruefe(request.POST)
    if fehler:
        return _seite(request, werte, fehler)

    # Bot-Spam still verwerfen: dieselbe Danke-Seite, keine Mail, kein Eintrag.
    punkte, gruende = spamschutz.bewerte({
        spamschutz.FELD_FALLE: request.POST.get(spamschutz.FELD_FALLE, ''),
        spamschutz.FELD_ZEIT: request.POST.get(spamschutz.FELD_ZEIT, ''),
        'name': werte['instagram'],
        'betreff': '',
        'nachricht': werte['bedeutung'],
    })
    if punkte >= spamschutz.SCHWELLE:
        _log.warning('Motivanfrage: Spam verworfen (%s: %s)', punkte, ','.join(gruende))
        return redirect('motiv_danke')
    if not cache.add(_doppelt_schluessel(werte), 1, DOPPELT_FENSTER):
        _log.info('Motivanfrage: doppelt abgeschickte Anfrage zusammengeführt')
        return redirect('motiv_danke')

    try:
        with transaction.atomic():
            anfrage = Motivanfrage.objects.create(**werte)
    except DatabaseError:
        _log.exception('Motivanfrage: nicht gespeichert')
        anfrage = Motivanfrage(**werte)
        gespeichert = False
    else:
        gespeichert = True

    betreff, html, text = _mail(anfrage)
    try:
        send_brevo_email(betreff, html, empfaenger(), recipient_name='Luisa', text_content=text,
                         reply_to=anfrage.email)
    except Exception:
        _log.exception('Motivanfrage: Mailversand nicht gestartet')
        gestartet = False
    else:
        gestartet = True
        if gespeichert:
            try:
                Motivanfrage.objects.filter(pk=anfrage.pk).update(mail_gestartet=True)
            except DatabaseError:
                _log.exception('Motivanfrage: Versandvermerk nicht gespeichert')

    if gestartet or gespeichert:
        return redirect('motiv_danke')
    cache.delete(_doppelt_schluessel(werte))
    return _seite(request, werte, 'Entschuldige, beim Senden ist etwas schiefgegangen. '
                                  'Versuch es bitte gleich noch einmal oder schreib mir auf Instagram.', status=500)


@never_cache
def motiv_danke(request):
    """Bestätigung nach dem Absenden. Zeigt nichts aus der Anfrage, ``noindex``."""
    return render(request, 'shop1/motiv_danke.html')
