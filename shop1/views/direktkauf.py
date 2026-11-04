"""Direktkauf ohne Konto (31.10.2026): Name, E-Mail, Anschrift (oder Abholung) -> Bestellung.

Bastians Vorgabe: keine großen Anmeldesysteme, der Kauf läuft über E-Mail; Luisa schickt innerhalb von
1 bis 2 Werktagen die Rechnung (Lexware) mit einem persönlichen Revolut-Zahlungslink (Karte, Apple Pay,
Google Pay, Revolut Pay; Überweisung bleibt zweiter Weg). Seit 04.11.2026 ist das der Hauptweg. Der Code bildet das ab:

* Nur sichtbar und erreichbar, wenn ``verkauf_aktiv()`` **und** ``settings.DIREKTKAUF`` (die
  Routen stehen in ``verkauf.KAUFROUTEN``; Warenkorb, Login-Checkout und PayPal bleiben im Code
  und sind bei ``DIREKTKAUF`` ausgeblendet bzw. über ``verkauf.DIREKTKAUF_GESPERRT`` umgeleitet).
* Eine Bestellung (``Order``, ohne ``user``) mit Zahlart „Zahlungslink“ (``zahlungslink``, Vorkasse wie ``bank_transfer``) und Status „pending“:
  Das ist dieselbe Reservierung wie im Login-Checkout (``checkout.reserviert``). Das Unikat gilt
  damit sofort als reserviert; ein zweiter Käufer sieht „reserviert“. Storniert Luisa die
  Bestellung im Admin (Status „Abgebrochen“), ist das Stück wieder frei.
* Schutz: CSRF, Honigtopf + Zeitfalle (``spamschutz``), Ratenbegrenzung je IP, Sperre gegen
  Doppelklick (Cache), Sperrung der Zeile des Stücks in der Transaktion (kein Doppelverkauf).
* Mails: „Deine Bestellung ist reserviert“ an die Kundin (Zahlungslink und Rechnung kommen separat in 1 bis 2
  Werktagen, Gesamtpreis, AGB, Widerrufsbelehrung), Bestellung mit Checkliste an Luisa, Kopie an die Webagentur.
"""

import hashlib
import logging
from datetime import timedelta

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import DatabaseError, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.utils import timezone
from django.views.decorators.cache import never_cache

from .. import luviq_daten, mails, rabatt, spamschutz
from ..models import Order, OrderItem, Produkt
from ..utils import send_brevo_email
from ._helpers import zu_viele_anfragen
from .checkout import reserviert

_log = logging.getLogger('shop1')

#: Wörtlich der Knopf nach § 312j Abs. 3 BGB.
KNOPF = 'Zahlungspflichtig bestellen'
ABHOLUNG_ADRESSE = 'Abholung in Lübeck nach Absprache'
LAENGEN = {'name': 200, 'email': 254, 'strasse': 200, 'plz': 10, 'stadt': 100, 'telefon': 20, 'rabattcode': 40}
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


def serie_kontext(produkt):
    """Serienstück (Bastian 01.11.2026): Bearbeitungszeit in Werktagen, dann Versand. Die verbindliche
    Lieferfrist (AGB § 5, 5 Werktage ab dem Tag nach der Zahlung) schließt die Bearbeitung ein; fürs Schema
    gilt: Übergabe an den Versand nach ``bearbeitungstage``, Laufzeit = Frist minus Bearbeitung."""
    if not getattr(produkt, 'serie', False):
        return {'serie': False}
    tage = produkt.bearbeitungstage or 0
    kontext = {'serie': True, 'bearbeitung': tage}
    if tage:
        kontext.update({'versand_werktage_min': tage, 'versand_werktage_max': tage,
                        'versand_transit_max': max(luviq_daten.VERSAND['lieferfrist_werktage'] - tage, 1)})
    return kontext


def rabatt_kontext(produkt, werte=None, request=None, ergebnis=None):
    """Rabattcode fürs Formular: eingegebener Code, sonst der über ``/rabatt/<code>/`` gemerkte.

    Ohne E-Mail lässt sich „erste Bestellung“ noch nicht prüfen; der Abzug wird dann vorläufig gezeigt und beim
    Absenden endgültig geprüft (gilt er nicht, wird nicht bestellt, sondern der Preis ohne Code gezeigt)."""
    werte = werte or {}
    text = werte.get('rabattcode')
    if text is None and request is not None:
        text = request.session.get(rabatt.SITZUNG, '')
    if ergebnis is None:
        ergebnis = rabatt.pruefe(text or '', produkt.preis, werte.get('email', ''),
                                 werte.get('strasse', ''), werte.get('plz', ''))
    return {
        'rabattcode_wert': ergebnis.text,
        'rabatt': ergebnis if ergebnis.gilt else None,
        'rabatt_fehler': ergebnis.fehler,
        'gesamtpreis': ergebnis.gesamt if ergebnis.gilt else produkt.preis,
    }


def formular_kontext(produkt, werte=None, fehler=None, request=None, ergebnis=None):
    return {
        **serie_kontext(produkt),
        **rabatt_kontext(produkt, werte, request, ergebnis),
        'produkt': produkt, 'werte': werte or {}, 'fehler': fehler, 'laengen': LAENGEN, 'knopf': KNOPF,
        'formzeit': spamschutz.zeitstempel(), 'feld_falle': spamschutz.FELD_FALLE,
        'direktkauf_zustand': zustand(produkt), 'abholung_adresse': ABHOLUNG_ADRESSE,
    }


def _werte(post):
    w = {k: (post.get(k) or '').strip() for k in ('name', 'email', 'strasse', 'plz', 'stadt', 'telefon', 'rabattcode')}
    w['rabattcode'] = rabatt.normalisiere_code(w['rabattcode'])
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
    teile = w['name'].split()
    if len(' '.join(teile[:-1])) > 100 or len(teile[-1]) > 100:
        # Order.vorname/nachname fassen je 100 Zeichen (Bug-Prüfung 01.11.2026: sonst Speicherfehler).
        return 'Vor- oder Nachname ist zu lang (höchstens 100 Zeichen). Bitte kürze ihn.'
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


class RabattGiltNicht(Exception):
    """Der Code galt beim Absenden nicht (mehr) – es wird nicht bestellt, die Kundin sieht den Preis ohne Code."""

    def __init__(self, ergebnis):
        super().__init__(ergebnis.fehler)
        self.ergebnis = ergebnis


def _bestellung_anlegen(produkt_id, w):
    """Order samt Posten; ``None``, wenn das Stück inzwischen weg ist. Wirft ``RabattGiltNicht``."""
    with transaction.atomic():
        produkt = Produkt.objects.select_for_update().get(pk=produkt_id)
        # Doppelklick/zweiter Tab (Bug-Prüfung 01.11.2026): Die Cache-Sperre gilt nur je Gunicorn-Prozess. Gibt es
        # dieselbe Bestellung (E-Mail, Stück) schon aus den letzten Minuten, ist es dieselbe – keine zweite Order,
        # keine zweite Mail, und ein Rabattcode scheitert nicht an „schon bestellt“.
        doppelt = (Order.objects.filter(
            email_schluessel=rabatt.email_schluessel(w['email']), status='pending', items__produkt_ref=produkt.pk,
            erstellt_am__gte=timezone.now() - timedelta(seconds=DOPPELT_FENSTER)).order_by('-erstellt_am').first())
        if doppelt:
            doppelt.doppelt = True
            return doppelt
        if zustand(produkt) != 'bestellbar':
            return None
        teile = w['name'].split()
        abholung = w['lieferart'] == 'abholung'
        # Code in derselben Transaktion prüfen und seine Zeile sperren: zwei gleichzeitige Bestellungen können
        # weder die Höchstzahl noch „nur erste Bestellung“ gemeinsam unterlaufen.
        ergebnis = rabatt.pruefe(w.get('rabattcode', ''), produkt.preis, w['email'],
                                 '' if abholung else w['strasse'], '' if abholung else w['plz'], sperren=True)
        if ergebnis.text and not ergebnis.gilt:
            raise RabattGiltNicht(ergebnis)
        order = Order.objects.create(
            user=None, status='pending', payment_method='zahlungslink',
            vorname=' '.join(teile[:-1]), nachname=teile[-1], email=w['email'],
            adresse=ABHOLUNG_ADRESSE if abholung else w['strasse'],
            stadt='Lübeck' if abholung else w['stadt'],
            postleitzahl='' if abholung else w['plz'],
            land='Deutschland',
            telefon=w['telefon'], gesamt_betrag=ergebnis.gesamt if ergebnis.gilt else produkt.preis,
            rabatt_betrag=ergebnis.abzug if ergebnis.gilt else 0,
            rabatt_code=ergebnis.code if ergebnis.gilt else None,
            rabatt_code_text=ergebnis.text if ergebnis.gilt else '',
            rabatt_prozent=ergebnis.prozent if ergebnis.gilt else 0)
        OrderItem.objects.create(order=order, produkt_name=produkt.name, produkt_preis=produkt.preis,
                                 produkt_ref=produkt.pk, menge=1)
    return order


def _doppelt_schluessel(produkt, w):
    roh = '\x00'.join((str(produkt.pk), w['email'].lower(), w['name'].lower(), w['strasse'].lower()))
    return 'direktkauf-doppelt:' + hashlib.sha256(roh.encode()).hexdigest()


# ─── Mails ──────────────────────────────────────────────────────────────────

def _euro(betrag):
    """69.0 -> „69,00 €“."""
    return f'{float(betrag):.2f}'.replace('.', ',') + ' €'


def kundin_schritte(serie, tage):
    """Die drei Schritte „So geht es weiter“ der Mail an die Kundin (Zahlungslink als Hauptweg, 04.11.2026).

    Alle Werte kommen aus ``luviq_daten``. Nur ein Serienstück wird erst nach der Zahlung gemalt; ein Einzelstück
    liegt fertig bereit und ist reserviert."""
    z = luviq_daten.ZAHLUNG
    frist = luviq_daten.VERSAND['lieferfrist_werktage']
    reserviert = luviq_daten.RESERVIERUNG_TAGE
    if serie:
        danach = (f'Sobald deine Zahlung da ist, malt Luisa dein Shirt von Hand für dich (Bearbeitung ca. {tage or 3} '
                  f'Werktage), danach geht es in den Versand. Geliefert wird innerhalb von {frist} Werktagen '
                  f'{luviq_daten.FRIST_BEGINN} (AGB § 5).')
    else:
        danach = ('Sobald deine Zahlung da ist, machen wir dein Stück versandfertig und schicken es los. Geliefert wird '
                  f'innerhalb von {frist} Werktagen {luviq_daten.FRIST_BEGINN} (AGB § 5).')
    return [
        ('Zahlungslink und Rechnung',
         f'Beides kommt separat innerhalb von {luviq_daten.RECHNUNG_FRIST} per E-Mail an diese Adresse. Schau bitte '
         'auch im Spam-Ordner nach.'),
        ('Bezahlen',
         f'Mit dem persönlichen Zahlungslink zahlst du auf der sicheren Bezahlseite von {z["anbieter"]}: '
         f'{z["wege"]}. Alternativ kannst du auf die IBAN aus der Rechnung überweisen. Bitte zahle innerhalb von '
         f'{reserviert} Tagen nach Rechnungsdatum.'),
        ('Danach wird dein Stück fertig gemacht', danach),
    ]


def mail_an_kundin(order):
    """Mail an die Kundin: Bestellung ist reserviert, Zahlungslink und Rechnung kommen separat (1 bis 2 Werktage),
    wie bezahlt wird, was danach passiert, Bestellübersicht, Vertragsunterlagen."""
    posten = list(order.items.all())
    gesamt = _euro(order.gesamt_betrag)
    abholung = order.adresse == ABHOLUNG_ADRESSE
    wo = ('Abholung in Lübeck nach Absprache' if abholung else
          f'{order.vorname} {order.nachname}, {order.adresse}, {order.postleitzahl} {order.stadt}')
    p0 = posten[0].produkt() if posten else None
    serie = bool(p0 and p0.serie)
    tage = (p0.bearbeitungstage if p0 else 0) or 0
    if serie:
        kopf = ('deine Bestellung ist reserviert, und dein Shirt wird jetzt für dich gemacht: Luisa malt es von Hand, '
                'sobald deine Zahlung eingegangen ist. Kein Shirt gleicht einem anderen.')
    else:
        kopf = ('deine Bestellung ist reserviert, und dein Stück wird jetzt für dich zurückgehalten und nach deiner '
                'Zahlung für den Versand vorbereitet.')
    schritte = kundin_schritte(serie, tage)
    vertrag = ('Der Kaufvertrag kommt zustande, wenn Luisa Brehler deine Bestellung mit der Rechnung annimmt (AGB § 2). '
               'AGB, Widerrufsbelehrung und Muster-Widerrufsformular findest du unten in dieser Mail.')
    unterlagen_html, unterlagen_text = mails.vertragsunterlagen(order)
    zeilen = [f'{p.menge}x {p.produkt_name}: {_euro(float(p.produkt_preis) * p.menge)}' for p in posten]
    rz = rabatt_zeile(order)
    if rz:
        zeilen.append(rz)
    betreff = f'Deine Bestellung #{order.id} ist reserviert – Luviq'
    preis_hinweis = '(inkl. Versand innerhalb Deutschlands, gemäß § 19 UStG ohne Umsatzsteuer)'
    text = (f'Deine Bestellung #{order.id} ist reserviert\n\nHallo {order.vorname},\n\n{kopf[0].upper() + kopf[1:]}\n\n'
            'So geht es weiter:\n' +
            '\n'.join(f'{i}. {t}: {b}' for i, (t, b) in enumerate(schritte, 1)) +
            '\n\nDeine Bestellung:\n' + '\n'.join(f'- {z}' for z in zeilen) +
            f'\nGesamt: {gesamt} {preis_hinweis}\nLieferung: {wo}\n\n{vertrag}\n\n'
            f'Fragen? Antworte einfach auf diese Mail oder schreib an {mails.KONTAKT_EMAIL}.\n\n'
            f'Viele Grüße\nLuisa Brehler\n\n---\n{unterlagen_text}')
    try:
        html = mails.rendern(
            'bestellung_kundin.html', titel=betreff,
            preheader=f'Reserviert. Zahlungslink und Rechnung folgen in {luviq_daten.RECHNUNG_FRIST}.',
            vorname=order.vorname, bestellnummer=order.id, kopf=kopf, schritte=schritte, zeilen=zeilen,
            gesamt=gesamt, preis_hinweis=preis_hinweis, wo=wo, vertrag=vertrag, unterlagen_html=unterlagen_html)
    except Exception:
        _log.exception('Mail an die Kundin: Gestaltung gescheitert, einfache Fassung geht hinaus')
        html = ('<html><body><h2>Hallo ' + escape(order.vorname) + ',</h2><pre style="white-space:pre-wrap">'
                + escape(text) + '</pre></body></html>')
    send_brevo_email(betreff, html, order.email, recipient_name=f'{order.vorname} {order.nachname}',
                     text_content=text, reply_to=mails.KONTAKT_EMAIL)


def rabatt_zeile(order):
    """„Rabatt 10 % (Code ABC): -6.90 €“ oder leer."""
    if not order.rabatt_betrag:
        return ''
    code = f' (Code {order.rabatt_code_text})' if order.rabatt_code_text else ''
    return f'Rabatt {order.rabatt_prozent} %{code}: -{float(order.rabatt_betrag):.2f} €'


def luisa_checkliste(order):
    """Die drei Schritte für Luisa (Mail „Neue Bestellung“): Zahlungslink, Rechnung, nach Zahlung auf „bezahlt“."""
    betrag = _euro(order.gesamt_betrag)
    return [
        f'In Revolut Pro einen Zahlungslink über genau {betrag} erstellen. Beschreibung: „Luviq Bestellung Nr. {order.id}“; '
        '„Mehrmals bezahlen“ ausgeschaltet.',
        f'Rechnung in Lexware mit dem Link und der IBAN an {order.email} schicken, innerhalb von '
        f'{luviq_daten.RECHNUNG_FRIST}. Den Link kannst du zur Übersicht auch in der Bestellung im Shop-Admin eintragen '
        '(der Shop verschickt damit nichts).',
        'Nach dem Zahlungseingang die Bestellung im Shop-Admin auf „bezahlt“ setzen, dann das Shirt malen.',
    ]


def mail_an_luisa(order):
    """Alle Daten der Bestellung an Luisa (Antworten geht an die Kundin) plus Kopie an die Webagentur."""
    p = order.items.first()
    felder = [
        ('Bestellung', f'#{order.id}'),
        ('Stück', p.produkt_name if p else '–'),
        ('Gesamtpreis', f'{_euro(order.gesamt_betrag)} (inkl. Versand)'
                        + (f' – {rabatt_zeile(order)}, Rechnung über diesen Betrag' if order.rabatt_betrag else '')),
        ('Zahlart', order.get_payment_method_display()),
        ('Name', f'{order.vorname} {order.nachname}'),
        ('E-Mail', order.email, 'mail'),
        ('Lieferung', order.adresse if order.adresse == ABHOLUNG_ADRESSE else
         f'{order.adresse}, {order.postleitzahl} {order.stadt}'),
        ('Telefon', order.telefon, 'tel'),
    ]
    produkt = p.produkt() if p else None
    serie = bool(produkt and produkt.serie)
    tage = (produkt.bearbeitungstage if serie else 0) or 3
    checkliste = luisa_checkliste(order)
    betreff = f'[Luviq] Neue Bestellung #{order.id} – {p.produkt_name if p else ""}'
    text = ('\n'.join(f'{f[0]}: {f[1] or "–"}' for f in felder) + '\n\nNächster Schritt:\n' +
            '\n'.join(f'({i}) {t}' for i, t in enumerate(checkliste, 1)))
    hinweis = (f'Serienstück: Das Shirt wird nach dem Zahlungseingang neu gemalt (ca. {tage} Werktage); '
               'ein Stück ist nicht vergeben, weitere Bestellungen sind möglich.' if serie else
               'Das Stück ist reserviert, bis die Zahlung da ist oder du die Bestellung im Shop-Admin auf '
               '„Abgebrochen“ setzt.')
    betreff, html, text = mails.anfrage_an_luisa(
        art='Bestellung', betreff=betreff, felder=felder, text=text, antwort_an=order.email, objekt=order,
        hinweis=hinweis, checkliste_titel='Nächster Schritt', checkliste=checkliste)
    try:
        send_brevo_email(betreff, html, mails.KONTAKT_EMAIL, recipient_name='Luisa Brehler',
                         text_content=text, reply_to=order.email)
    finally:
        # Die Kopie an die Webagentur geht auch dann hinaus, wenn die Mail an Luisa nicht gestartet werden konnte.
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
        return render(request, 'shop1/direktkauf.html', formular_kontext(produkt, request=request))
    if request.POST.get('aktion') == 'rabattcode':
        # „Einlösen“: nur den Code prüfen und den neuen Gesamtpreis zeigen, nichts bestellen.
        w = _werte(request.POST)
        if zu_viele_anfragen(request, 'rabattcode', grenze=20):
            return render(request, 'shop1/direktkauf.html', formular_kontext(
                produkt, {**w, 'rabattcode': ''}, 'Zu viele Versuche mit Rabattcodes. Bitte versuch es in einer '
                'Viertelstunde noch einmal.'), status=429)
        kontext = formular_kontext(produkt, w)
        if kontext['rabatt']:
            request.session[rabatt.SITZUNG] = w['rabattcode']
        return render(request, 'shop1/direktkauf.html', kontext)
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
    except RabattGiltNicht as fall:
        cache.delete(_doppelt_schluessel(produkt, w))
        request.session.pop(rabatt.SITZUNG, None)
        return render(request, 'shop1/direktkauf.html', formular_kontext(
            produkt, {**w, 'rabattcode': ''}, f'{fall.ergebnis.fehler} Es wurde noch nichts bestellt.'), status=400)
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
    request.session.pop(rabatt.SITZUNG, None)
    if getattr(order, 'doppelt', False):
        return redirect('direktkauf_danke')
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


@never_cache
def rabatt_einloesen(request, code):
    """``/rabatt/<CODE>/`` (Hero-Knopf, QR-Code auf Karten): merkt einen gültigen Code in der Sitzung und führt
    zum Bestellformular. Ob es die erste Bestellung ist, prüft erst das Absenden (dann kennen wir die E-Mail)."""
    from django.contrib import messages
    from django.urls import reverse
    from django.utils.http import url_has_allowed_host_and_scheme

    gefunden = rabatt.gueltiger_code(code)
    if gefunden:
        request.session[rabatt.SITZUNG] = gefunden.code
        bedingung = ' auf deine erste Bestellung' if gefunden.nur_erstbestellung else ''
        messages.success(request, f'Rabattcode {gefunden.code} ist eingetragen: {gefunden.prozent} %{bedingung}. '
                                  'Du siehst den Preis im Bestellformular.')
    else:
        messages.info(request, 'Dieser Rabattcode gilt leider nicht (mehr). Bestellen kannst du trotzdem.')
    weiter = request.GET.get('weiter', '')
    if weiter and url_has_allowed_host_and_scheme(weiter, allowed_hosts={request.get_host()},
                                                  require_https=request.is_secure()):
        return redirect(weiter)
    engel = Produkt.objects.filter(aktiv=True, slug=luviq_daten.ENGEL_STUECK['slug']).first()
    if engel and engel.kaufbar:
        return redirect(engel.get_absolute_url() + '#bestellen')
    return redirect(reverse('produkte'))
