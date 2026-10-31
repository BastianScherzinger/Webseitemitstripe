"""Direktkauf ohne Konto (31.10.2026): Name, E-Mail, Anschrift (oder Abholung) -> Bestellung.

Bastians Vorgabe: keine großen Anmeldesysteme, der Kauf läuft über E-Mail; Luisa schickt die
Rechnung mit den Zahlungsdaten, bis es Zahlungslinks gibt. Der Code bildet das ab:

* Nur sichtbar und erreichbar, wenn ``verkauf_aktiv()`` **und** ``settings.DIREKTKAUF`` (die
  Routen stehen in ``verkauf.KAUFROUTEN``; Warenkorb, Login-Checkout und PayPal bleiben im Code
  und sind bei ``DIREKTKAUF`` ausgeblendet bzw. über ``verkauf.DIREKTKAUF_GESPERRT`` umgeleitet).
* Eine Bestellung (``Order``, ohne ``user``) mit Zahlart „Überweisung“ und Status „pending“:
  Das ist dieselbe Reservierung wie im Login-Checkout (``checkout.reserviert``). Das Unikat gilt
  damit sofort als reserviert; ein zweiter Käufer sieht „reserviert“. Storniert Luisa die
  Bestellung im Admin (Status „Abgebrochen“), ist das Stück wieder frei.
* Schutz: CSRF, Honigtopf + Zeitfalle (``spamschutz``), Ratenbegrenzung je IP, Sperre gegen
  Doppelklick (Cache), Sperrung der Zeile des Stücks in der Transaktion (kein Doppelverkauf).
* Mails: Eingang an die Kundin (Gesamtpreis, „Rechnung mit Zahlungsdaten folgt“, AGB,
  Widerrufsbelehrung), Bestellung an Luisa, Kopie an die Webagentur.
"""

import hashlib
import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.views.decorators.cache import never_cache

from .. import luviq_daten, mails, spamschutz
from ..models import Order, OrderItem, Produkt
from ..utils import send_brevo_email
from ._helpers import zu_viele_anfragen
from .checkout import reserviert

_log = logging.getLogger('shop1')

#: Wörtlich der Knopf nach § 312j Abs. 3 BGB.
KNOPF = 'Zahlungspflichtig bestellen'
ABHOLUNG_ADRESSE = 'Abholung in Lübeck nach Absprache'
LAENGEN = {'name': 200, 'email': 254, 'strasse': 200, 'plz': 10, 'stadt': 100, 'telefon': 20}
SITZUNG = 'direktkauf_bestellung'
DOPPELT_FENSTER = 120


from ..verkauf import direktkauf_aktiv  # noqa: E402  (ein Schalter, eine Stelle)


def frei(produkt, ausser=None):
    """Wie viele Stücke noch bestellbar sind (Bestand minus Reservierungen)."""
    return max(0, produkt.lagerbestand - reserviert(produkt, ausser))


def zustand(produkt):
    """``'bestellbar'``, ``'reserviert'`` oder ``'nicht'`` (vergeben, inaktiv, ausverkauft)."""
    if not produkt.kaufbar:
        return 'nicht'
    return 'bestellbar' if frei(produkt) >= 1 else 'reserviert'


def formular_kontext(produkt, werte=None, fehler=None):
    return {
        'produkt': produkt, 'werte': werte or {}, 'fehler': fehler, 'laengen': LAENGEN, 'knopf': KNOPF,
        'formzeit': spamschutz.zeitstempel(), 'feld_falle': spamschutz.FELD_FALLE,
        'direktkauf_zustand': zustand(produkt), 'abholung_adresse': ABHOLUNG_ADRESSE,
    }


def _werte(post):
    w = {k: (post.get(k) or '').strip() for k in ('name', 'email', 'strasse', 'plz', 'stadt', 'telefon')}
    w['lieferart'] = 'abholung' if post.get('lieferart') == 'abholung' else 'versand'
    w['zustimmung'] = post.get('zustimmung') == 'ja'
    return w


def pruefe(w):
    """Fehlertext oder ``None``."""
    if not w['name'] or len(w['name'].split()) < 2:
        return 'Bitte gib deinen Vor- und Nachnamen an.'
    if not w['email']:
        return 'Bitte gib deine E-Mail-Adresse an, an sie schicken wir die Rechnung.'
    for feld, grenze in LAENGEN.items():
        if len(w[feld]) > grenze:
            return f'Eine Eingabe ist zu lang (höchstens {grenze} Zeichen). Bitte kürze sie.'
    try:
        validate_email(w['email'])
    except ValidationError:
        return 'Bitte gib eine gültige E-Mail-Adresse an.'
    if w['lieferart'] == 'versand' and not (w['strasse'] and w['plz'] and w['stadt']):
        return 'Bitte gib Straße mit Hausnummer, Postleitzahl und Ort an – oder wähle Abholung.'
    if not w['zustimmung']:
        return 'Bitte bestätige, dass du AGB, Widerrufsbelehrung und Datenschutzerklärung gelesen hast.'
    return None


def _spam(post, w):
    punkte, gruende = spamschutz.bewerte({
        spamschutz.FELD_FALLE: post.get(spamschutz.FELD_FALLE, ''),
        spamschutz.FELD_FALLE_ALT: post.get(spamschutz.FELD_FALLE_ALT, ''),
        spamschutz.FELD_ZEIT: post.get(spamschutz.FELD_ZEIT, ''),
        'name': w['name'], 'email': w['email'], 'betreff': '', 'nachricht': w['strasse'],
    })
    if punkte >= spamschutz.SCHWELLE:
        _log.warning('Direktkauf: Spamverdacht (%s: %s) – verworfen', punkte, ','.join(gruende))
        return True
    return False


def _bestellung_anlegen(produkt_id, w):
    """Order samt Posten; ``None``, wenn das Stück inzwischen weg ist."""
    with transaction.atomic():
        produkt = Produkt.objects.select_for_update().get(pk=produkt_id)
        if zustand(produkt) != 'bestellbar':
            return None
        teile = w['name'].split()
        abholung = w['lieferart'] == 'abholung'
        order = Order.objects.create(
            user=None, status='pending', payment_method='bank_transfer',
            vorname=' '.join(teile[:-1]), nachname=teile[-1], email=w['email'],
            adresse=ABHOLUNG_ADRESSE if abholung else w['strasse'],
            stadt='Lübeck' if abholung else w['stadt'],
            postleitzahl='' if abholung else w['plz'],
            land='Deutschland',
            telefon=w['telefon'], gesamt_betrag=produkt.preis)
        OrderItem.objects.create(order=order, produkt_name=produkt.name, produkt_preis=produkt.preis,
                                 produkt_ref=produkt.pk, menge=1)
    return order


def _doppelt_schluessel(produkt, w):
    roh = '\x00'.join((str(produkt.pk), w['email'].lower(), w['name'].lower(), w['strasse'].lower()))
    return 'direktkauf-doppelt:' + hashlib.sha256(roh.encode()).hexdigest()


# ─── Mails ──────────────────────────────────────────────────────────────────

def mail_an_kundin(order):
    """Eingang der Bestellung, Gesamtpreis, Hinweis auf die Rechnung, Vertragsunterlagen."""
    posten = list(order.items.all())
    gesamt = f'{float(order.gesamt_betrag):.2f} €'
    abholung = order.adresse == ABHOLUNG_ADRESSE
    wo = ('Abholung in Lübeck nach Absprache' if abholung else
          f'{order.vorname} {order.nachname}, {order.adresse}, {order.postleitzahl} {order.stadt}')
    satz = ('Wir haben deine Bestellung erhalten und das Stück für dich reserviert. Schau bitte auch im Spam-Ordner nach, falls die Rechnung nicht ankommt. Die Rechnung mit den '
            'Zahlungsdaten folgt per E-Mail an diese Adresse. Der Kaufvertrag kommt zustande, wenn Luisa '
            'Brehler deine Bestellung mit dieser Rechnung annimmt (AGB § 2). Bitte überweise innerhalb von '
            f'{luviq_daten.RESERVIERUNG_TAGE} Tagen nach Rechnungsdatum; so lange halten wir das Stück für dich zurück.')
    unterlagen_html, unterlagen_text = mails.vertragsunterlagen(order)
    zeilen_text = '\n'.join(f'- {p.menge}x {p.produkt_name}: {float(p.produkt_preis) * p.menge:.2f} €' for p in posten)
    zeilen_html = ''.join(f'<li>{p.menge}x {escape(p.produkt_name)}: {float(p.produkt_preis) * p.menge:.2f} €</li>'
                          for p in posten)
    text = (f'Eingang deiner Bestellung #{order.id}\n\nHallo {order.vorname},\n\n{satz}\n\n{zeilen_text}\n'
            f'Gesamt: {gesamt} (inkl. Versand innerhalb Deutschlands, gemäß § 19 UStG ohne Umsatzsteuer)\n'
            f'Lieferung: {wo}\n\nViele Grüße\nLuisa Brehler\n\n---\n{unterlagen_text}')
    html = (f'<html><body><h2>Hallo {escape(order.vorname)},</h2><p>{escape(satz)}</p><ul>{zeilen_html}</ul>'
            f'<p><strong>Gesamt: {gesamt}</strong> (inkl. Versand innerhalb Deutschlands, gemäß § 19 UStG ohne '
            f'Umsatzsteuer)</p><p>Lieferung: {escape(wo)}</p><p>Viele Grüße,<br>Luisa Brehler</p>'
            f'{unterlagen_html}</body></html>')
    send_brevo_email(f'Eingang deiner Bestellung #{order.id} bei Luviq', html, order.email,
                     recipient_name=f'{order.vorname} {order.nachname}', text_content=text,
                     reply_to=mails.KONTAKT_EMAIL)


def mail_an_luisa(order):
    """Alle Daten der Bestellung an Luisa (Antworten geht an die Kundin) plus Kopie an die Webagentur."""
    p = order.items.first()
    felder = [
        ('Bestellung', f'#{order.id}'),
        ('Stück', p.produkt_name if p else '–'),
        ('Gesamtpreis', f'{float(order.gesamt_betrag):.2f} € (inkl. Versand)'),
        ('Name', f'{order.vorname} {order.nachname}'),
        ('E-Mail', order.email, 'mail'),
        ('Lieferung', order.adresse if order.adresse == ABHOLUNG_ADRESSE else
         f'{order.adresse}, {order.postleitzahl} {order.stadt}'),
        ('Telefon', order.telefon, 'tel'),
    ]
    betreff = f'[Luviq] Neue Bestellung #{order.id} – {p.produkt_name if p else ""}'
    text = '\n'.join(f'{f[0]}: {f[1] or "–"}' for f in felder) + \
        '\n\nNächster Schritt: Rechnung mit Zahlungsdaten an die Kundin schicken (Antworten genügt).'
    betreff, html, text = mails.anfrage_an_luisa(
        art='Bestellung', betreff=betreff, felder=felder, text=text, antwort_an=order.email, objekt=order,
        hinweis='Nächster Schritt: Rechnung mit Zahlungsdaten an die Kundin schicken. Das Stück ist reserviert.')
    send_brevo_email(betreff, html, mails.KONTAKT_EMAIL, recipient_name='Luisa Brehler',
                     text_content=text, reply_to=order.email)
    mails.betreiber_kopie(art='Bestellung', name=f'{order.vorname} {order.nachname}', felder=felder,
                          antwort_an=order.email, objekt=order, admin_mail=True,
                          kunden_mail='Eingangsmail angestoßen', schon=(mails.KONTAKT_EMAIL,))


# ─── Views ──────────────────────────────────────────────────────────────────

# offen-ok: Kauf ohne Konto ist gewollt (Bastian 31.10.2026). Geschrieben wird erst nach Verkaufs-
# schalter (Middleware), CSRF, Drosselung je IP, Honigtopf/Zeitfalle, Feldprüfung und Doppelsperre.
@never_cache
def direktkauf(request, slug):
    produkt = get_object_or_404(Produkt, slug=slug, aktiv=True)
    if not direktkauf_aktiv():
        raise Http404
    if request.method != 'POST':
        return render(request, 'shop1/direktkauf.html', formular_kontext(produkt))
    if zu_viele_anfragen(request, 'direktkauf', grenze=8):
        return render(request, 'shop1/direktkauf.html', formular_kontext(
            produkt, dict(request.POST.items()),
            'Gerade kamen mehrere Bestellungen von dieser Verbindung. Bitte versuch es in einer Viertelstunde '
            f'noch einmal oder schreib an {mails.KONTAKT_EMAIL}.'), status=429)
    w = _werte(request.POST)
    fehler = pruefe(w)
    if fehler:
        return render(request, 'shop1/direktkauf.html', formular_kontext(produkt, w, fehler), status=400)
    if _spam(request.POST, w):
        # Still verwerfen wie bei den anderen Formularen: keine Bestellung, keine Mail.
        return redirect('direktkauf_danke')
    if not cache.add(_doppelt_schluessel(produkt, w), 1, DOPPELT_FENSTER):
        if request.session.get(SITZUNG):
            return redirect('direktkauf_danke')
    try:
        order = _bestellung_anlegen(produkt.pk, w)
    except DatabaseError:
        _log.exception('Direktkauf: Bestellung nicht gespeichert')
        cache.delete(_doppelt_schluessel(produkt, w))
        return render(request, 'shop1/direktkauf.html', formular_kontext(
            produkt, w, 'Die Bestellung konnte gerade nicht gespeichert werden. Bitte versuch es gleich noch '
                        f'einmal oder schreib an {mails.KONTAKT_EMAIL}.'), status=500)
    if order is None:
        cache.delete(_doppelt_schluessel(produkt, w))
        return render(request, 'shop1/direktkauf.html', formular_kontext(produkt, w), status=409)
    request.session[SITZUNG] = order.pk
    for versand in (mail_an_kundin, mail_an_luisa):
        try:
            versand(order)
        except Exception:
            _log.exception('Direktkauf: Mail nicht gestartet (%s, Bestellung %s)', versand.__name__, order.pk)
    return redirect('direktkauf_danke')


@never_cache
def direktkauf_danke(request):
    """Danke-Seite: zeigt die eigene, gerade abgeschickte Bestellung (aus der Sitzung)."""
    pk = request.session.get(SITZUNG)
    order = Order.objects.filter(pk=pk).prefetch_related('items').first() if pk else None
    return render(request, 'shop1/direktkauf_danke.html', {
        'order': order, 'abholung': bool(order and order.adresse == ABHOLUNG_ADRESSE),
    })
