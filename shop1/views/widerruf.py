"""Elektronische Widerrufsfunktion „Vertrag widerrufen“ (§ 356a BGB, seit 19.06.2026).

Wortlaut der Norm (gesetze-im-internet.de, abgerufen 30.10.2026):

* Abs. 1 – eine Funktion auf der Online-Benutzeroberfläche, gut lesbar mit
  „Vertrag widerrufen“ beschriftet, während der Widerrufsfrist **ständig
  verfügbar, hervorgehoben und leicht zugänglich** → Link im Fuß jeder Seite,
  auf der Bestellseite, im Profil und in jeder Bestellmail; **ohne Anmeldung**
  nutzbar (die Route steht nicht in ``verkauf.KAUFROUTEN``).
* Abs. 2 – Name, Angaben zur Identifizierung des Vertrags (oder des Teils),
  elektronisches Kommunikationsmittel für die Eingangsbestätigung → Felder
  ``name``, ``vertrag`` (+ freiwillig ``umfang``), ``email``.
* Abs. 3 – Bestätigungsfunktion „Widerruf bestätigen“ → der Absendeknopf.
* Abs. 4 – Eingangsbestätigung auf einem dauerhaften Datenträger, unverzüglich,
  mit Inhalt der Erklärung, Datum und Uhrzeit des Eingangs → E-Mail an die
  angegebene Adresse (und Anzeige auf der Bestätigungsseite).

Gleiche Schutzschichten wie Kontakt- und Motivformular: CSRF, Drosselung je
IP, Honigtopf und Zeitfalle (``spamschutz``), Mail-Obergrenze. Anders als
dort wird **jede** gültige Erklärung gespeichert, auch bei Spamverdacht:
ein Widerruf darf nicht still verloren gehen. Bei Spamverdacht geht keine
Mail hinaus (sonst wäre das Formular ein Werkzeug, um beliebigen Adressen
Mails zu schicken); Luisa sieht den Eintrag im Admin mit dem Vermerk.
"""

import hashlib
import logging
import os
import re

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache

from .. import mails, spamschutz
from ..models import Order, Widerruf
from ..utils import send_brevo_email
from ._helpers import zu_viele_anfragen

_log = logging.getLogger('shop1')

#: Obergrenzen = Spaltenlängen in ``Widerruf``; im Formular als ``maxlength``.
LAENGEN = {'name': 200, 'vertrag': 200, 'umfang': 1000, 'email': 254}

#: Gesetzliche Beschriftungen (§ 356a Abs. 1 Satz 2 und Abs. 3 Satz 2 BGB).
KNOPF_WIDERRUF = 'Vertrag widerrufen'
KNOPF_BESTAETIGEN = 'Widerruf bestätigen'

DOPPELT_FENSTER = 2 * 60
SITZUNG_SCHLUESSEL = 'widerruf_eingang'


def pruefe(daten):
    """``(werte, fehler)``: bereinigte Werte und ein Fehlertext oder ``None``."""
    werte = {feld: (daten.get(feld) or '').strip() for feld in LAENGEN}
    if not werte['name']:
        return werte, 'Bitte gib deinen Namen an.'
    if not werte['vertrag']:
        return werte, 'Bitte gib deine Bestellnummer an (oder Bestelldatum und Stück), damit der Widerruf zugeordnet werden kann.'
    if not werte['email']:
        return werte, 'Bitte gib deine E-Mail-Adresse an. Dorthin schicken wir die Eingangsbestätigung.'
    if any(len(werte[f].replace('\r\n', '\n')) > g for f, g in LAENGEN.items()):
        return werte, 'Eine Eingabe ist zu lang. Bitte kürze sie.'
    try:
        validate_email(werte['email'])
    except ValidationError:
        return werte, 'Bitte gib eine gültige E-Mail-Adresse an.'
    return werte, None


def passende_bestellung(vertrag, email):
    """Die Bestellung, deren Nummer im Feld steht **und** deren E-Mail passt – sonst ``None``.

    Beide Merkmale zusammen, damit niemand fremde Bestellungen zuordnet."""
    for nummer in re.findall(r'\d{1,9}', vertrag or ''):
        bestellung = Order.objects.filter(pk=int(nummer), email__iexact=email).first()
        if bestellung:
            return bestellung
    return None


def empfaenger_luisa():
    """Luisas Adresse für die Benachrichtigung (wie bei der Motivanfrage, nie die eingetippte)."""
    return settings.MOTIV_EMPFAENGER or os.getenv('ADMIN_EMAIL', '') or mails.KONTAKT_EMAIL


def eingang_text(widerruf):
    """``Datum, Uhrzeit`` des Eingangs in deutscher Zeit, z. B. ``01.11.2026, 14:03 Uhr``."""
    return timezone.localtime(widerruf.eingegangen_am).strftime('%d.%m.%Y, %H:%M Uhr')


def _felder(widerruf):
    return [
        ('Name', widerruf.name),
        ('Bestellnummer / Vertrag', widerruf.vertrag),
        ('Widerrufene Stücke', widerruf.umfang or 'die ganze Bestellung'),
        ('E-Mail für die Bestätigung', widerruf.email, 'mail'),
        ('Eingegangen am', eingang_text(widerruf)),
        ('Zugeordnete Bestellung', f'#{widerruf.bestellung_id}' if widerruf.bestellung_id else 'keine – bitte von Hand prüfen'),
    ]


def bestaetigung_mail(widerruf):
    """``(betreff, html, text)`` der Eingangsbestätigung an die Verbraucherin (§ 356a Abs. 4 BGB)."""
    eingang = eingang_text(widerruf)
    umfang = widerruf.umfang or 'die ganze Bestellung'
    betreff = mails.einzeilig(f'Eingangsbestätigung deines Widerrufs ({widerruf.vertrag})')[:150]
    html = mails.rendern(
        'widerruf_eingang.html', titel='Dein Widerruf ist eingegangen',
        preheader=f'Eingegangen am {eingang}', w=widerruf, eingang=eingang, umfang=umfang,
        anbieterin=mails.ANBIETERIN)
    a = mails.ANBIETERIN
    text = (
        'Eingangsbestätigung deines Widerrufs\n\n'
        f'Deine Widerrufserklärung ist am {eingang} bei uns eingegangen.\n\n'
        'Inhalt deiner Erklärung:\n'
        f'Name: {widerruf.name}\n'
        f'Bestellnummer / Vertrag: {widerruf.vertrag}\n'
        f'Widerrufene Stücke: {umfang}\n'
        f'E-Mail für diese Bestätigung: {widerruf.email}\n'
        f'Eingegangen am: {eingang}\n\n'
        'Wie es weitergeht: Bitte schicke die Ware spätestens 14 Tage nach deinem Widerruf an '
        f'{a["name"]}, {a["strasse"]}, {a["plz"]} {a["ort"]} zurück. Die unmittelbaren Kosten der '
        'Rücksendung trägst du. Den Kaufpreis einschließlich der Lieferkosten zahlen wir spätestens '
        '14 Tage nach Eingang deines Widerrufs mit demselben Zahlungsmittel zurück; wir können die '
        'Rückzahlung verweigern, bis die Ware zurück ist oder du die Rücksendung nachgewiesen hast.\n\n'
        f'Viele Grüße\nLuisa\n\n{mails.MARKE} · {mails.IMPRESSUM_ZEILE} · {mails.KONTAKT_EMAIL}'
    )
    return betreff, html, text


def _mails_verschicken(widerruf):
    """Eingangsbestätigung an die Verbraucherin, Benachrichtigung an Luisa, Kopie an die Betreuung."""
    betreff, html, text = bestaetigung_mail(widerruf)
    gestartet = False
    try:
        send_brevo_email(betreff, html, widerruf.email, recipient_name=widerruf.name,
                         text_content=text, reply_to=mails.KONTAKT_EMAIL,
                         danach=_vermerk(widerruf.pk))
        gestartet = True
    except Exception:
        _log.exception('Widerruf: Eingangsbestätigung nicht gestartet')
    if gestartet:
        Widerruf.objects.filter(pk=widerruf.pk).update(bestaetigung_gestartet=True)

    felder = _felder(widerruf)
    luisa_text = 'Neuer Widerruf über „Vertrag widerrufen“\n\n' + '\n'.join(f'{e[0]}: {e[1]}' for e in felder)
    luisa_text += ('\n\nDie Kundin hat automatisch eine Eingangsbestätigung bekommen. Rückzahlung spätestens '
                   '14 Tage nach Eingang; alle Widerrufe stehen im Admin unter „Widerrufe“.')
    l_betreff, l_html, l_text = mails.anfrage_an_luisa(
        art='Widerruf', betreff=f'Widerruf: {widerruf.vertrag} – {widerruf.name}', felder=felder,
        text=luisa_text, antwort_an=widerruf.email, objekt=widerruf,
        hinweis='Rückzahlung spätestens 14 Tage nach Eingang (Widerrufsbelehrung). Die Kundin hat die Eingangsbestätigung automatisch bekommen.')
    try:
        send_brevo_email(l_betreff, l_html, empfaenger_luisa(), recipient_name='Luisa',
                         text_content=l_text, reply_to=widerruf.email)
    except Exception:
        _log.exception('Widerruf: Mail an Luisa nicht gestartet')
    mails.betreiber_kopie(art='Widerruf', name=widerruf.name, felder=felder, antwort_an=widerruf.email,
                          objekt=widerruf, admin_mail=True, kunden_mail='Eingangsbestätigung (Pflicht, § 356a BGB)',
                          schon=[empfaenger_luisa()])
    return gestartet


def _vermerk(pk):
    def danach(ok):
        if not ok:
            Widerruf.objects.filter(pk=pk).update(bestaetigung_gestartet=False)
    return danach


def _ist_spam(post, werte):
    punkte, gruende = spamschutz.bewerte({
        spamschutz.FELD_FALLE: post.get(spamschutz.FELD_FALLE, ''),
        spamschutz.FELD_FALLE_ALT: post.get(spamschutz.FELD_FALLE_ALT, ''),
        spamschutz.FELD_ZEIT: post.get(spamschutz.FELD_ZEIT, ''),
        'name': werte['name'],
        'email': werte['email'],
        'betreff': werte['vertrag'],
        'nachricht': werte['umfang'],
    })
    if punkte >= spamschutz.SCHWELLE:
        _log.warning('Widerruf: Spamverdacht (%s: %s) – gespeichert, keine Mail', punkte, ','.join(gruende))
        return True
    return False


def _doppelt_schluessel(werte):
    inhalt = '\x00'.join(werte[k] for k in sorted(werte)).lower()
    return 'widerruf-doppelt:' + hashlib.sha256(inhalt.encode()).hexdigest()


def _vorbelegung(request):
    """Angemeldet: Name, E-Mail und die letzte Bestellung vorbelegen (alles änderbar)."""
    user = request.user
    if not user.is_authenticated:
        return {}, []
    bestellungen = list(Order.objects.filter(user=user).order_by('-erstellt_am')[:5])
    werte = {'name': f'{user.first_name} {user.last_name}'.strip(), 'email': user.email or ''}
    if bestellungen:
        werte['vertrag'] = f'#{bestellungen[0].pk}'
    return werte, bestellungen


def _seite(request, werte=None, fehler=None, status=200):
    vorbelegt, bestellungen = _vorbelegung(request)
    if werte is None:
        werte = vorbelegt
    return render(request, 'shop1/widerruf.html', {
        'werte': werte, 'fehler': fehler, 'bestellungen': bestellungen,
        'formzeit': spamschutz.zeitstempel(), 'feld_falle': spamschutz.FELD_FALLE,
        'laengen': LAENGEN, 'knopf_bestaetigen': KNOPF_BESTAETIGEN,
    }, status=status)


# offen-ok: Pflichtfunktion nach § 356a BGB, muss ohne Anmeldung gehen. Geschrieben
# wird ein Widerruf erst nach Drosselung je IP, Feldprüfung und Doppelsperre.
@never_cache
def vertrag_widerrufen(request):
    """„Vertrag widerrufen“: Formular anzeigen, Erklärung speichern, Eingang bestätigen."""
    if request.method != 'POST':
        return _seite(request)
    if zu_viele_anfragen(request, 'widerruf'):
        return _seite(request, dict(request.POST.items()), 'Du hast gerade mehrere Widerrufe geschickt. Bitte versuch es '
                      f'in einer Viertelstunde noch einmal oder schreib an {mails.KONTAKT_EMAIL}.', status=429)
    werte, fehler = pruefe(request.POST)
    if fehler:
        return _seite(request, werte, fehler)

    if not cache.add(_doppelt_schluessel(werte), 1, DOPPELT_FENSTER):
        letzter = request.session.get(SITZUNG_SCHLUESSEL)
        if letzter:
            return redirect('widerruf_eingang')

    spam = _ist_spam(request.POST, werte)
    try:
        widerruf = Widerruf.objects.create(
            bestellung=passende_bestellung(werte['vertrag'], werte['email']),
            spamverdacht=spam, **werte)
    except DatabaseError:
        _log.exception('Widerruf: nicht gespeichert')
        cache.delete(_doppelt_schluessel(werte))
        return _seite(request, werte, 'Der Widerruf konnte gerade nicht gespeichert werden. Bitte versuch es gleich '
                      f'noch einmal oder schick ihn per E-Mail an {mails.KONTAKT_EMAIL}.', status=500)

    if not spam and spamschutz.mail_budget_ok('widerruf'):
        _mails_verschicken(widerruf)
    request.session[SITZUNG_SCHLUESSEL] = widerruf.pk
    return redirect('widerruf_eingang')


@never_cache
def widerruf_eingang(request):
    """Bestätigungsseite: zeigt den eigenen, gerade abgeschickten Widerruf mit Eingangszeit."""
    pk = request.session.get(SITZUNG_SCHLUESSEL)
    widerruf = Widerruf.objects.filter(pk=pk).first() if pk else None
    if widerruf is None:
        return redirect('vertrag_widerrufen')
    return render(request, 'shop1/widerruf_eingang.html', {
        'w': widerruf, 'eingang': eingang_text(widerruf), 'umfang': widerruf.umfang or 'die ganze Bestellung',
    })
