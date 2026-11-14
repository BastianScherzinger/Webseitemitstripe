"""Stückanfrage (``/anfragen/<slug>/``) – der einfache Shop mit Anfragen (Bastian 14.11.2026).

Statt Warenkorb, Konto und „Zahlungspflichtig bestellen“ schickt ein Besucher eine Anfrage zu einem Stück:
Größe, Stückzahl, Name, E-Mail, Nachricht. **Keine Bestellung, kein Vertrag, keine Zahlung, keine
Reservierung** – Luisa antwortet persönlich; bezahlt wird später (Mollie) auf einem Weg, der noch nicht
gebaut ist. Das Muster stammt von Rümpelwerk (Anfrage statt Online-Kauf) und von ``views/motiv.py``.

Gleiche Schutzschichten wie das Motivformular: Drosselung je IP, Feldprüfung auf dem Server, Spamschutz
(Honeypot, Zeitfalle, Punkte), Doppelsperre. Erst speichern, dann mailen. Gemailt wird nur an Luisa
(``MOTIV_EMPFAENGER``, sonst ``ADMIN_EMAIL``) und als Kopie an die Webagentur – **nie** an die eingetippte
Adresse (Lehre vom 17.09.2026); die Danke-Seite sagt, dass Luisa sich meldet.

Nur bei ``verkauf.anfrageshop_aktiv()``; sonst leitet die Adresse auf die Stückseite.
"""

import hashlib
import logging
import re

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache

from .. import mails, spamschutz
from ..models import Produkt, Stueckanfrage
from ..utils import send_brevo_email
from ..verkauf import anfrageshop_aktiv
from ._helpers import mail_ergebnis_vermerken, zu_viele_anfragen
from .motiv import empfaenger

_log = logging.getLogger('shop1')

LAENGEN = {'name': 200, 'email': 254, 'groesse': 40, 'nachricht': 1500}
MAX_ANZAHL = 5
DOPPELT_FENSTER = 2 * 60
KNOPF = 'Anfrage senden'


def _werte(post):
    w = {k: (post.get(k) or '').strip() for k in ('name', 'email', 'groesse', 'nachricht')}
    w['anzahl'] = (post.get('anzahl') or '1').strip()
    w['zustimmung'] = post.get('zustimmung') == 'ja'
    return w


def pruefe(w):
    """``(anzahl, fehler)``: bereinigte Stückzahl und ein Fehlertext oder ``None``."""
    if not w['name']:
        return 1, 'Bitte gib deinen Namen an.'
    if not w['email']:
        return 1, 'Bitte gib deine E-Mail-Adresse an, damit ich dir antworten kann.'
    # Zeilenumbrüche zählen wie im Browser (maxlength) als ein Zeichen.
    if any(len(str(w[feld]).replace('\r\n', '\n')) > grenze for feld, grenze in LAENGEN.items()):
        return 1, 'Eine Eingabe ist zu lang. Bitte kürze sie.'
    try:
        validate_email(w['email'])
    except ValidationError:
        return 1, 'Bitte gib eine gültige E-Mail-Adresse an.'
    if not re.fullmatch(r'[0-9]{1,2}', w['anzahl']) or not 1 <= int(w['anzahl']) <= MAX_ANZAHL:
        return 1, f'Bitte wähl eine Stückzahl von 1 bis {MAX_ANZAHL}.'
    if not w['zustimmung']:
        return int(w['anzahl']), 'Bitte bestätige, dass du die Datenschutzerklärung gelesen hast.'
    return int(w['anzahl']), None


def formular_kontext(produkt, werte=None, fehler=None):
    """Alles, was das Formular (``teile/stueckanfrage_formular.html``) braucht."""
    return {
        'produkt': produkt, 'werte': werte or {}, 'fehler': fehler, 'laengen': LAENGEN,
        'anfrage_knopf': KNOPF, 'anzahlen': range(1, MAX_ANZAHL + 1),
        'formzeit': spamschutz.zeitstempel(), 'feld_falle': spamschutz.FELD_FALLE,
    }


def _felder(a):
    stueck = f'Nº {a.produkt_nummer} · {a.produkt_name}' if a.produkt_nummer else a.produkt_name
    return [
        ('Stück', stueck),
        ('Stückzahl', str(a.anzahl)),
        ('Größe', a.groesse or '–'),
        ('Name', a.name),
        ('E-Mail', a.email, 'mail'),
    ]


def _mail(a):
    betreff = f'Stückanfrage: {a.produkt_name}'
    text = 'Neue Stückanfrage über www.luviq-luebeck.com\n\n'
    text += '\n'.join(f'{z[0]}: {z[1]}' for z in _felder(a))
    text += '\n\nNachricht:\n' + (a.nachricht or '–')
    text += '\n\nKeine Bestellung: nichts ist bezahlt oder reserviert. Antworte der Person direkt per E-Mail.'
    text += '\nAlle Anfragen stehen im Django-Admin unter „Stückanfragen“.'
    return mails.anfrage_an_luisa(
        art='Stückanfrage', betreff=betreff, felder=_felder(a), text=text, antwort_an=a.email,
        langtext_titel='Nachricht', langtext=a.nachricht, objekt=a if a.pk else None,
        hinweis='Keine Bestellung: nichts ist bezahlt oder reserviert. Antworte der Person direkt per E-Mail.')


def _doppelt_schluessel(produkt, w):
    inhalt = '\x00'.join([str(produkt.pk)] + [str(w[k]) for k in sorted(w)]).lower()
    return 'stueckanfrage-doppelt:' + hashlib.sha256(inhalt.encode()).hexdigest()


def _speichern(produkt, w, anzahl):
    """``(anfrage, gespeichert)`` – scheitert die Datenbank, trägt die Mail die Anfrage trotzdem."""
    werte = dict(produkt=produkt, produkt_name=produkt.name, produkt_nummer=str(produkt.archiv_nummer),
                 anzahl=anzahl, groesse=w['groesse'], name=w['name'], email=w['email'], nachricht=w['nachricht'])
    try:
        with transaction.atomic():
            return Stueckanfrage.objects.create(**werte), True
    except DatabaseError:
        _log.exception('Stückanfrage: nicht gespeichert')
        werte['produkt'] = None
        return Stueckanfrage(**werte), False


def _mail_an_luisa(a, gespeichert):
    """Startet die Mail an Luisa; ``True``, wenn der Versand gestartet ist."""
    betreff, html, text = _mail(a)
    try:
        send_brevo_email(betreff, html, empfaenger(), recipient_name='Luisa', text_content=text,
                         reply_to=a.email,
                         danach=mail_ergebnis_vermerken(Stueckanfrage, a.pk if gespeichert else None))
    except Exception:
        _log.exception('Stückanfrage: Mailversand nicht gestartet')
        return False
    if gespeichert:
        try:
            Stueckanfrage.objects.filter(pk=a.pk).update(mail_gestartet=True)
        except DatabaseError:
            _log.exception('Stückanfrage: Versandvermerk nicht gespeichert')
    return True


def _ist_spam(post, w):
    """Honigtopf, Zeitfalle und Inhalt bewerten; ``True`` heißt still verwerfen."""
    punkte, gruende = spamschutz.bewerte({
        spamschutz.FELD_FALLE: post.get(spamschutz.FELD_FALLE, ''),
        spamschutz.FELD_ZEIT: post.get(spamschutz.FELD_ZEIT, ''),
        'name': w['name'], 'email': w['email'], 'betreff': '', 'nachricht': w['nachricht'],
        spamschutz.FELD_FALLE_ALT: post.get(spamschutz.FELD_FALLE_ALT, ''),
    })
    if punkte >= spamschutz.SCHWELLE:
        _log.warning('Stückanfrage: Spam verworfen (%s: %s)', punkte, ','.join(gruende))
        return True
    return False


# offen-ok: die Anfrage richtet sich an Besucher ohne Konto. Geschrieben wird nur eine Stückanfrage, und
# erst nach Drosselung je IP, Feldprüfung, Spamschutz und Doppelsperre.
def stueck_anfragen(request, slug):
    """Formular „Stück anfragen“: prüfen, speichern, mailen (nur an Luisa). GET leitet auf die Stückseite."""
    produkt = get_object_or_404(Produkt, slug=slug, aktiv=True)
    if request.method != 'POST' or not anfrageshop_aktiv() or produkt.vergeben:
        return redirect(produkt.get_absolute_url())

    def seite(werte=None, fehler=None, status=200):
        return render(request, 'shop1/stueck_anfrage_fehler.html', formular_kontext(produkt, werte, fehler),
                      status=status)

    w = _werte(request.POST)
    if zu_viele_anfragen(request, 'stueckanfrage'):
        return seite(w, 'Du hast gerade mehrere Anfragen geschickt. '
                        'Bitte versuch es in einer Viertelstunde noch einmal.', 429)
    anzahl, fehler = pruefe(w)
    if fehler:
        return seite(w, fehler)
    # Bot-Spam still verwerfen: dieselbe Danke-Seite, keine Mail, kein Eintrag.
    if _ist_spam(request.POST, w):
        return redirect('stueck_anfrage_danke')
    if not cache.add(_doppelt_schluessel(produkt, w), 1, DOPPELT_FENSTER):
        _log.info('Stückanfrage: doppelt abgeschickte Anfrage zusammengeführt')
        return redirect('stueck_anfrage_danke')

    a, gespeichert = _speichern(produkt, w, anzahl)
    mail_erlaubt = spamschutz.mail_budget_ok('stueckanfrage')
    gestartet = mail_erlaubt and _mail_an_luisa(a, gespeichert)
    # Eigene Kopie an die Webagentur – wirft nie, ändert nichts an Speichern oder der Mail an Luisa.
    if mail_erlaubt:
        mails.betreiber_kopie(
            art='Stückanfrage', name=a.name, felder=_felder(a), antwort_an=a.email,
            langtext_titel='Nachricht', langtext=a.nachricht, objekt=a, gespeichert=gespeichert,
            admin_mail=gestartet, schon=[empfaenger()])
    if gestartet or gespeichert:
        return redirect('stueck_anfrage_danke')
    cache.delete(_doppelt_schluessel(produkt, w))
    return seite(w, 'Entschuldige, beim Senden ist etwas schiefgegangen. Versuch es bitte gleich noch einmal '
                    'oder schreib mir über das Kontaktformular.', 500)


@never_cache
def stueck_anfrage_danke(request):
    """Bestätigung nach dem Absenden. Zeigt nichts aus der Anfrage, ``noindex``."""
    return render(request, 'shop1/stueck_anfrage_danke.html')
