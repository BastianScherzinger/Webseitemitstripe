"""Gestaltete Mails und die Kopie an die Webagentur (26.09.2026).

Drei Arten von Mails laufen hier zusammen, alle über ``utils.send_brevo_email``
(Brevo-API, sonst SMTP; Text- **und** HTML-Teil):

* **Mail an Luisa** zu einer Anfrage (Kontaktformular, Motivanfrage) –
  :func:`anfrage_an_luisa` liefert Betreff, HTML und Text; verschickt wird sie
  wie bisher in der View.
* **Kopie an die Webagentur** (:func:`betreiber_kopie`): eine **eigene,
  zusätzliche** Mail je echter Anfrage an ``BETREIBER_KOPIE_AN`` (Vorgabe
  Bastian Scherzinger, kommagetrennt, leer oder ``aus`` = abgeschaltet). Sie
  wirft nie: scheitert sie, bleiben Anfrage, Speichern und die Mail an Luisa
  unberührt. Spam und Doppelklicks erreichen sie nicht – die Views rufen sie
  erst nach allen Schutzschichten.
* **Mails an Besucher** ohne Formulartext (Konto bestätigen, Newsletter
  bestätigen) – nur die Gestaltung ist neu. Eine automatische Bestätigung
  einer Anfrage an die eingetippte Adresse gibt es bewusst **nicht** (Lehre
  vom 17.09.2026, Danke-Seite der Motivanfrage).

Solange ``VERKAUF_AKTIV`` aus ist, stehen in keiner dieser Mails Preise,
Kleinunternehmer-Sätze oder Bestell-Wörter. Vorlagen: ``templates/emails/``.
Vorschau: ``python tools/mailvorschau.py <zielordner>``.
"""

import logging
import os

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.html import escape

from .utils import send_brevo_email

_log = logging.getLogger('shop1')

SEITENNAME = 'Luviq'
MARKE = 'Luviq Universe'
BETREIBER_VORGABE = 'bastian.scherzinger05@gmail.com'
KONTAKT_EMAIL = 'brehlerluisa@gmail.com'
INSTAGRAM_NAME = 'luviq.universe'
INSTAGRAM_URL = 'https://www.instagram.com/luviq.universe/'
IMPRESSUM_ZEILE = 'Luisa Brehler · Grünberger Str. 16 · 36304 Alsfeld'


def live_url():
    """Absolute Adresse der Live-Seite ohne Schrägstrich am Ende.

    ``CANONICAL_HOST`` ist die gepflegte Hauptadresse; ``SITE_URL`` zeigt in
    der Vorgabe noch auf die Railway-Adresse und taugt deshalb nicht für Links
    in Mails an die Betreuung."""
    host = getattr(settings, 'CANONICAL_HOST', '') or 'www.luviq-alsfeld.com'
    return f'https://{host}'


def _grundkontext(**kontext):
    basis = {
        'marke': MARKE,
        'live_url': live_url(),
        'domain': live_url().replace('https://', ''),
        'kontakt_email': KONTAKT_EMAIL,
        'instagram_name': INSTAGRAM_NAME,
        'instagram_url': INSTAGRAM_URL,
        'impressum_zeile': IMPRESSUM_ZEILE,
        'impressum_url': live_url() + _pfad('impressum'),
    }
    basis.update(kontext)
    return basis


def _pfad(name, *args):
    try:
        return reverse(name, args=args)
    except NoReverseMatch:
        return '/'


def admin_link(objekt):
    """Absolute Adresse des Eintrags im Django-Admin (geheimer Pfad ``ADMIN_URL``)."""
    if objekt is None or getattr(objekt, 'pk', None) is None:
        return ''
    meta = objekt._meta
    try:
        pfad = reverse(f'admin:{meta.app_label}_{meta.model_name}_change', args=[objekt.pk])
    except NoReverseMatch:
        return ''
    return live_url() + pfad


def rendern(vorlage, **kontext):
    """HTML einer Mailvorlage; Eingaben escapet Django selbst (autoescape)."""
    return render_to_string(f'emails/{vorlage}', _grundkontext(**kontext))


def zeitpunkt():
    return timezone.localtime(timezone.now()).strftime('%d.%m.%Y, %H:%M Uhr')


def einzeilig(wert):
    """Kein Zeilenumbruch in einer Kopfzeile (Header Injection)."""
    return ' '.join(str(wert or '').split())


# ─── Empfänger der Kopie ────────────────────────────────────────────────────

def betreiber_empfaenger(schon=()):
    """Adressen aus ``BETREIBER_KOPIE_AN`` ohne die, die schon regulär eine Mail
    bekommen (Groß-/Kleinschreibung egal). Leer oder ``aus`` = keine Kopie."""
    roh = os.getenv('BETREIBER_KOPIE_AN')
    if roh is None:
        roh = BETREIBER_VORGABE
    if roh.strip().lower() in ('', 'aus', 'off', 'false', '0'):
        return []
    bekannt = {str(a).strip().lower() for a in schon if a}
    ergebnis = []
    for adresse in roh.split(','):
        adresse = adresse.strip()
        if adresse and adresse.lower() not in bekannt:
            bekannt.add(adresse.lower())
            ergebnis.append(adresse)
    return ergebnis


# ─── Mail an Luisa ──────────────────────────────────────────────────────────

def anfrage_an_luisa(*, art, betreff, felder, text, antwort_an='', langtext_titel='',
                     langtext='', objekt=None, hinweis=''):
    """Betreff, HTML und Text der Mail an Luisa.

    ``felder``: Liste ``(Bezeichnung, Wert[, Typ])`` mit Typ ``mail``, ``tel``,
    ``insta`` oder leer. ``text`` ist der bisherige Textteil und bleibt es.

    Scheitert die Gestaltung, geht die Mail mit dem Text als HTML hinaus –
    eine Vorlage darf nie eine Anfrage kosten."""
    try:
        html = _anfrage_html(art, betreff, felder, antwort_an, langtext_titel, langtext, objekt, hinweis)
    except Exception:
        _log.exception('Mail an Luisa: Gestaltung gescheitert, Textfassung geht hinaus')
        html = '<pre style="white-space:pre-wrap">' + escape(text) + '</pre>'
    return einzeilig(betreff), html, text


def _anfrage_html(art, betreff, felder, antwort_an, langtext_titel, langtext, objekt, hinweis):
    return rendern(
        'anfrage_admin.html',
        art=art,
        titel=f'Neue {art}',
        preheader=f'Neue {art} über {live_url().replace("https://", "")}',
        felder=_felder(felder),
        langtext_titel=langtext_titel,
        langtext=langtext,
        antwort_an=antwort_an,
        antwort_betreff=f'Re: {betreff}',
        admin_url=admin_link(objekt),
        zeitpunkt=zeitpunkt(),
        hinweis=hinweis,
    )


def _felder(felder):
    ergebnis = []
    for eintrag in felder:
        bezeichnung, wert = eintrag[0], eintrag[1]
        typ = eintrag[2] if len(eintrag) > 2 else ''
        ergebnis.append({'bezeichnung': bezeichnung, 'wert': wert if wert not in (None, '') else '–',
                         'typ': typ if wert else ''})
    return ergebnis


# ─── Kopie an die Webagentur ────────────────────────────────────────────────

def betreiber_kopie(*, art, name, felder, antwort_an='', langtext_titel='', langtext='',
                    objekt=None, gespeichert=True, admin_mail=None, kunden_mail='keine (bewusst)',
                    herkunft='', schon=()):
    """Eigene Kopie jeder echten Anfrage an die Webagentur. Wirft nie.

    ``admin_mail``: ``True``/``False`` – ob die Mail an Luisa angestoßen wurde
    (``None`` = nicht bekannt). Gibt die Zahl der angestoßenen Kopien zurück."""
    try:
        empfaenger = betreiber_empfaenger(schon)
        if not empfaenger:
            return 0
        betreff = einzeilig(f'[{SEITENNAME}] Neue {art} – {name or "ohne Namen"}')
        status = [
            ('Gespeichert', 'ja' if gespeichert else 'NEIN – nur in dieser Mail'),
            ('Mail an Luisa', {True: 'angestoßen', False: 'fehlgeschlagen', None: '–'}[admin_mail]),
            ('Bestätigung an Absender', kunden_mail),
        ]
        admin_url = admin_link(objekt) if gespeichert else ''
        text = _kopie_text(art, felder, langtext_titel, langtext, status, admin_url, herkunft)
        html = rendern(
            'betreiber_kopie.html',
            art=art,
            titel=f'Neue {art}',
            preheader=f'{MARKE}: neue {art} von {name or "ohne Namen"}',
            felder=_felder(felder),
            langtext_titel=langtext_titel,
            langtext=langtext,
            status=status,
            admin_url=admin_url,
            herkunft=herkunft,
            antwort_an=antwort_an,
            zeitpunkt=zeitpunkt(),
        )
    except Exception:
        _log.exception('Kopie an die Webagentur: nicht aufgebaut (%s)', art)
        return 0
    gestartet = 0
    for adresse in empfaenger:
        try:
            send_brevo_email(betreff, html, adresse, recipient_name='Webagentur Scherzinger',
                             text_content=text, reply_to=antwort_an or '')
            gestartet += 1
        except Exception:
            _log.exception('Kopie an die Webagentur: Versand nicht gestartet (%s)', art)
    return gestartet


def _kopie_text(art, felder, langtext_titel, langtext, status, admin_url, herkunft):
    zeilen = [f'{MARKE} ({live_url()}) – neue {art}', f'Zeitpunkt: {zeitpunkt()}', '']
    zeilen += [f'{e[0]}: {e[1] or "–"}' for e in felder]
    if langtext_titel:
        zeilen += ['', f'{langtext_titel}:', langtext or '–']
    if herkunft:
        zeilen += ['', f'Herkunft: {herkunft}']
    zeilen += [''] + [f'{k}: {v}' for k, v in status]
    if admin_url:
        zeilen += ['', f'Im Admin: {admin_url}']
    zeilen += ['', '–', 'Kopie für die Webagentur Scherzinger – Betreuung dieser Website']
    return '\n'.join(zeilen)
