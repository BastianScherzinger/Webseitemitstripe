"""Texte und Werte der öffentlichen Seiten im Look „Nachtausgabe" (19.09.2026).

Eine Stelle für alles, was sonst in Vorlagen getippt würde: Markensatz, Lead,
Laufband, Drop, Teaser, die Auswahl der Motivanfrage, die fünf Schritte,
Luisas Satz. Quelle der Wortlaute: ``Design/luviq/MARKENWISSEN-luisa.md`` und
``FINALER-BAUPLAN.md`` in den Firmenunterlagen (Luisas Befragung vom
19.09.2026). Luisa darf jeden Satz in ihre Worte ändern – dann hier.

Kein Datum und kein Satz davon steht in einer Vorlage.
"""

import logging
import os
from datetime import datetime

from django.db import DatabaseError
from django.utils import timezone

_log = logging.getLogger('shop1')

#: Anbieterin laut Gewerbeanmeldung (GewA 1 vom 22.10.2026, Ordnungsamt der
#: Hansestadt Lübeck; Unterlagen ``Buero\luisa\arbeitsplatz\recht\gewerbe``):
#: Feld 3 Geschäftsbezeichnung „LUVIQ", Feld 4/5 Name, Feld 15 Betriebsstätte,
#: Feld 20 Beginn 01.11.2026 im Nebenerwerb. Impressum, Datenschutz, Kontakt,
#: Schema, llms.txt und die Mailfußzeile lesen **nur** von hier. Die
#: Telefonnummer aus Feld 15 steht bewusst nicht hier: ob sie öffentlich
#: werden soll, entscheidet Luisa (Frage F12); Pflicht ist sie nicht.
ANBIETERIN = {
    'name': 'Luisa Brehler',
    'geschaeft': 'Luviq',
    'strasse': 'Mühlenkamp 5',
    'plz': '23569',
    'ort': 'Lübeck',
    'region': 'Schleswig-Holstein',
    'land': 'DE',
    'land_name': 'Deutschland',
    'email': 'brehlerluisa@gmail.com',
    'gewerbe_beginn': '01.11.2026',
}

#: Wo Luviq angefangen hat: die ersten Stücke (Nº 001–005), die Domain
#: luviq-alsfeld.com und das Google-Profil stammen aus Alsfeld. Seit Oktober
#: 2026 malt Luisa in Lübeck (Gewerbeanmeldung) – Alsfeld bleibt Herkunft,
#: kein Sitz mehr.
HERKUNFT = {'ort': 'Alsfeld', 'region': 'Hessen', 'kreis': 'Vogelsbergkreis'}

#: Luisas Markensatz, von ihr gewählt am 19.09.2026. Gesprochen, nicht gesetzt.
MARKENSATZ = 'Sag mir, was du willst — ich mal’s dir.'

#: Erster Absatz nach der Überschrift. Nennt den Ort, weil Antwortmaschinen
#: den ersten Absatz zitieren (test_inhalt: Anbieter oder Ort im ersten Absatz).
LEAD = ('Ich bemale in Lübeck Second-Hand-Teile von Hand, mit Bleiche und Pinsel, meist '
        'in 2 bis 5 Tagen. Du sagst mir, was drauf soll, ich schick dir Vorschläge, und '
        'dann entsteht dein Stück. Jedes Motiv gibt es genau einmal.')

#: Erfahrungswert von Luisa, **nie als Zusage** schreiben („meistens").
DAUER = '2 bis 5 Tage'

#: Luisas Satz zum Anfang von Luviq – beiläufig, keine Gründungslegende.
ZITAT = 'Langeweile, schwere Zeit — und Bock, was zu bemalen.'
ZITAT_QUELLE = 'Luisa Brehler, wie Luviq angefangen hat'

#: Das frühere Profil ``luviq.universe`` gibt es nicht mehr (live geprüft
#: 02.10.2026, „Seite nicht verfügbar"); das aktive heißt ``luviq.archive``.
INSTAGRAM = 'https://www.instagram.com/luviq.archive/'
INSTAGRAM_NAME = 'luviq.archive'

#: TikTok „luviq" (@luviq.archive); die Bio verweist auf dasselbe
#: Instagram-Profil (live geprüft 02.10.2026).
TIKTOK = 'https://www.tiktok.com/@luviq.archive'

#: Google-Unternehmensprofil „Luviq", Grünberger Str. 16, 36304 Alsfeld,
#: Website luviq-alsfeld.com (Maps, live geprüft 02.10.2026; CID aus der
#: Profiladresse 0xc0e5d5a554eadc30).
GOOGLE_PROFIL = 'https://www.google.com/maps?cid=13899750731019902000'

#: Belegte Profiladressen für ``sameAs`` (Schema) und ``llms.txt``.
PROFILE = (INSTAGRAM, TIKTOK, GOOGLE_PROFIL)

#: Pflegehinweis (GPSR-Angabe im Online-Angebot), wortgleich aus Luisas
#: Antwort in ``FAQ_MOTIV`` unten – kein neuer Satz, keine neue Zusage.
PFLEGE = ('Auf links bei 30 °C waschen, nicht in den Trockner, keinen Weichspüler nehmen und nur '
          'von links bügeln.')

#: Häufige Fragen rund um die Motivanfrage (Bestellung nach Wunsch), wortgleich als
#: Text auf ``/motiv-anfragen/`` und – erst mit Verkauf – als ``FAQPage``. Nur, was
#: auf der Seite und in den Wissensbeiträgen schon belegt ist: kein Preis, keine
#: Zusage, keine Lieferzeit, kein Verkaufsversprechen.
FAQ_MOTIV = [
    ('Ist eine Motivanfrage schon eine Bestellung?',
     'Nein. Die Anfrage kostet nichts und verpflichtet zu nichts: Du zahlst dabei '
     'nichts und bekommst keine Zusage. Du beschreibst, was dir vorschwebt, und Luisa '
     'schickt dir Vorschläge.'),
    ('Was passiert nach meiner Anfrage?',
     'Luisa meldet sich bei dir, per Instagram oder E-Mail, je nachdem, was du angegeben '
     'hast. Sie schickt dir ein paar Vorschläge, und ihr entscheidet zusammen. Erst wenn das '
     'Motiv passt, entsteht das Stück.'),
    ('Wie lange dauert es von der Anfrage bis zum fertigen Stück?',
     f'Meistens {DAUER}, je nach Motiv. Das ist ein Erfahrungswert und keine feste Zusage.'),
    ('Bekomme ich dasselbe Motiv zweimal?',
     'Nein. Jedes Stück ist ein handbemaltes Einzelstück, und weil jedes Motiv frei von Hand '
     'gemalt wird, entsteht kein zweites genauso. Ein Strich mit der Bleiche lässt sich '
     'außerdem nicht zurücknehmen.'),
    ('Wie pflege ich ein handbemaltes Stück?',
     PFLEGE + ' So bleibt die Bemalung lange schön.'),
]

#: Antwortzeit auf Anfragen, von Bastian für Luisa am 02.10.2026 bestätigt.
#: Eine Erreichbarkeit, keine Öffnungszeit (kein Ladengeschäft, GE20).
ANTWORT = 'innerhalb von 2 Stunden'

# ── Drop ─────────────────────────────────────────────────────────────────────

#: Vorgabe für ``DROP_TERMIN``. Leer setzen (``DROP_TERMIN=``) heißt: kein
#: Termin, der Kasten sagt „Die nächste Ausgabe ist in Arbeit." ohne Uhr.
#: Seit 02.10.2026 leer: der nächste Drop kommt, ein fester Termin steht noch
#: nicht (Bastian). Mit Termin wieder setzen, z. B. '2026-11-01T18:00+01:00'.
DROP_TERMIN_VORGABE = ''

_WOCHENTAGE = ('Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag')


def drop_termin(jetzt=None):
    """Der nächste Drop als bewusster Zeitpunkt – oder ``None``.

    ``None`` bei leerer, unlesbarer oder abgelaufener Angabe: dann gibt es
    keinen Countdown, sondern nur „in Arbeit" (Bauplan § 5)."""
    roh = os.getenv('DROP_TERMIN', DROP_TERMIN_VORGABE).strip()
    if not roh:
        return None
    try:
        termin = datetime.fromisoformat(roh)
    except ValueError:
        return None
    if timezone.is_naive(termin):
        termin = timezone.make_aware(termin)
    if termin <= (jetzt or timezone.now()):
        return None
    return termin


def termin_text(termin):
    """„Donnerstag, 08.10., 18 Uhr" in Berliner Zeit."""
    ort = timezone.localtime(termin)
    uhr = f'{ort.hour} Uhr' if not ort.minute else f'{ort.hour}:{ort.minute:02d} Uhr'
    return f'{_WOCHENTAGE[ort.weekday()]}, {ort:%d.%m.}, {uhr}'


def drop_nummer():
    """Nummer der nächsten Ausgabe, dreistellig: ``DROP_NUMMER``, sonst die
    Nummer des vorab angelegten Drop-Stücks, sonst die nächste freie.

    Lädt Luisa das Drop-Stück vor dem Termin hoch, bekommt es beim ersten
    Speichern die nächste freie Archivnummer (``Produkt.save``). Der Countdown
    muss diese Nummer nennen und darf nicht auf die übernächste springen
    (EIG123): Drop-Stück = das Stück mit der kleinsten Nummer über dem
    Archiv (``Produkt.vergeben``). Ohne so ein Stück gilt höchste Nummer + 1 –
    der Drop bekommt nie eine Nummer, die im Archiv schon vergeben ist."""
    fest = os.getenv('DROP_NUMMER', '').strip()
    if fest.isdigit():
        return f'{int(fest):03d}'
    from django.db.models import Max
    from .models import Produkt
    try:
        archiv = Produkt.objects.filter(vergeben=True).aggregate(m=Max('nummer'))['m'] or 0
        vorab = (Produkt.objects.filter(vergeben=False, nummer__gt=archiv)
                 .order_by('nummer').values_list('nummer', flat=True).first())
        if vorab:
            return f'{vorab:03d}'
        hoechste = Produkt.objects.aggregate(m=Max('nummer'))['m'] or 0
    except DatabaseError:
        # Die Seite muss auch ohne lesbare Tabelle rendern (frische Datenbank,
        # Migration läuft): dann beginnt die Zählung bei Nº 001.
        _log.warning('drop_nummer: Archivnummern nicht lesbar, Nº 001 angenommen', exc_info=True)
        hoechste = 0
    return f'{hoechste + 1:03d}'


#: Kopfzeile des Hero: „LUVIQ Universe | Oktober 2026 | Lübeck". Eine eigene
#: „Ausgabe 01" gibt es nicht mehr (EIG126): die Seite nennt sonst Nº 006 als
#: nächste Ausgabe, und zwei Zählungen widersprachen sich.
_MONATE = ('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August',
           'September', 'Oktober', 'November', 'Dezember')

#: Das Stück im Panorama-Foto (static/shop1/images/luviq/hero-*). Nummer und
#: Name kommen aus dem Archiv, damit die Bildunterschrift und die Karte
#: dasselbe Stück gleich nennen (EIG134): zuerst über die Archivnummer
#: ``nummer`` (übersteht eine Umbenennung), sonst über den ersten Namen, der
#: einen der ``suche``-Begriffe enthält. Ohne Treffer steht nur die
#: Beschreibung des Fotos da, kein erfundener Stückname und keine Nummer.
HERO_STUECK = {'nummer': 2, 'name': 'Hoodie mit Dornen-Augen-Motiv', 'suche': ('dornen',),
               'alt': 'Rückenansicht eines dunklen Hoodies mit handgebleichtem Rankenmotiv aus Dornen und Augen, draußen vor Herbstbäumen fotografiert'}

#: Teaser vor dem Drop: (Datum, Titel, Bildadresse, Alternativtext). Leer ⇒
#: der Abschnitt „Nº …, in Teilen" entfällt ganz – keine leeren Kacheln.
TEASER = []


def laufband(nummer, termin):
    """Die drei Teile des Laufbands; mit Termin nennt der mittlere die Ausgabe."""
    teile = ['Motiv anfragen, ohne Kosten']
    if termin:
        teile.append(f'Nº {nummer} erscheint {termin_text(termin)}')
    else:
        teile.append('Die nächste Ausgabe ist in Arbeit')
    teile.append('Handbemalt in Lübeck')
    return teile


def drop_kontext(jetzt=None):
    """Alles, was Laufband und Drop-Kasten brauchen – für den Kontextprozessor."""
    jetzt = jetzt or timezone.now()
    termin = drop_termin(jetzt)
    nummer = drop_nummer()
    monat = timezone.localtime(termin or jetzt)
    rest = {}
    if termin:
        sekunden = int((termin - jetzt).total_seconds())
        rest = {'d': f'{sekunden // 86400:02d}', 'h': f'{sekunden % 86400 // 3600:02d}',
                'm': f'{sekunden % 3600 // 60:02d}', 's': f'{sekunden % 60:02d}'}
    return {
        'monat': f'{_MONATE[monat.month - 1]} {monat.year}',
        'rest': rest,
        'nummer': nummer,
        'termin': termin,
        'termin_iso': timezone.localtime(termin).isoformat() if termin else '',
        'termin_text': termin_text(termin) if termin else '',
        'laufband': laufband(nummer, termin),
        'teaser': TEASER,
    }


# ── Motivanfrage ─────────────────────────────────────────────────────────────

#: Luisas erste Frage ist immer „in welche Richtung?" (Markenwissen § 5).
RICHTUNGEN = [
    ('tier', 'Tier'),
    ('symbol', 'Symbol oder Zeichen'),
    ('pflanze', 'Pflanze oder Ranke'),
    ('himmel', 'Mond und Sterne'),
    ('abstrakt', 'Abstrakt'),
    ('offen', 'Weiß ich noch nicht'),
]

TEILE = [
    ('hoodie', 'Hoodie'),
    ('sweatshirt', 'Sweatshirt'),
    ('jeans', 'Jeans'),
    ('shirt', 'Shirt'),
    ('eigenes', 'Hab ich selbst'),
]

PLATZIERUNGEN = [
    ('ruecken', 'Groß auf dem Rücken'),
    ('vorne', 'Kleiner vorne'),
    ('offen', 'Weiß ich noch nicht'),
]

#: Die drei Zeilen des Abschnitts „Du hast eine Idee?" auf der Startseite.
ANFRAGE_ABLAUF = [
    ('Du beschreibst dein Motiv', 'Richtung, Teil und was es dir bedeutet.'),
    ('Ich schick dir Vorschläge', 'Per Instagram oder Mail, persönlich von mir.'),
    ('Wir entscheiden zusammen', 'Erst wenn es passt, fange ich an.'),
]

#: Die vier Stationen auf der Seite /motiv-anfragen/, mit Erklärsatz je
#: Station (IS19, 2026-09-27) – dieselben Fakten wie ANFRAGE_ABLAUF und
#: SCHRITTE, nur auf vier Stationen statt drei bzw. fünf verteilt.
ANFRAGE_STATIONEN = [
    ('Anfrage', 'Du beschreibst dein Motiv: Richtung, Teil und was es dir bedeutet.'),
    ('Vorschläge', 'Ich schick dir Vorschläge, per Instagram oder Mail, persönlich von mir.'),
    ('Entscheidung', 'Wir entscheiden zusammen. Erst wenn es passt, fange ich an.'),
    ('Malen', 'Ich zeichne dein Motiv vor, trage die Bleiche mit dem Pinsel auf, wasche und fotografiere dein fertiges Stück.'),
]

# ── Entstehung ───────────────────────────────────────────────────────────────

#: Luisas fünf echte Schritte (Markenwissen § 7). Bild: Dateiname unter
#: shop1/static/shop1/images/luviq/ – bis ihr Arbeitsfoto da ist, die
#: vorhandenen Stückfotos.
SCHRITTE = [
    ('Design finden', 'Wir klären die Richtung, ich schick dir ein paar Vorschläge, '
                      'und wir entscheiden zusammen.', 'eclipse-crew', 'Sweatshirt mit gebleichtem Eclipse-Motiv'),
    ('Skizze', 'Das Motiv entsteht erst auf Papier, mit Bleistift.',
     'augen-mit-fluegeln', 'Pullover mit Augen und Flügeln auf dem Rücken'),
    ('Vorzeichnen', 'Dann zeichne ich es direkt auf dein Teil vor.',
     'spinnennetz-jeans-hoch', 'Jeans mit Spinnennetz-Motiv am Bein'),
    ('Bleiche', 'Mit dem Pinsel zieht die Bleiche die Farbe aus dem Stoff. '
                'Ein Strich lässt sich nicht zurücknehmen.', 'dornenaugen-hoodie',
     'Hoodie mit gebleichtem Dornen-Motiv auf dem Rücken'),
    ('Waschen und los', 'Waschen, fotografieren, einpacken und ab zu dir.',
     'drache', 'Hoodie mit Drachen-Motiv auf dem Rücken'),
]


# ── Versand, Übergabe, Herkunft (Paket P1, 29.10.2026) ───────────────────────

#: Versand. ``werktage`` steht so in den AGB (``legal/agb.html``, § 4: „Nach
#: Zahlungseingang wird in der Regel innerhalb von 1-2 Werktagen versendet“) und
#: wird nur mit Verkauf gezeigt. Versandkosten und ein Versanddienstleister stehen
#: weder in den AGB noch im Code, deshalb gibt es hier keinen Wert dafür und keine
#: Seite nennt einen. ``ausland=False``: Versand nur innerhalb Deutschlands.
VERSAND = {'gebiet': 'ganz Deutschland', 'ausland': False, 'werktage': '1-2'}

#: Persönliche Übergabe in Lübeck. Bewusst ohne Uhrzeiten und ohne Treffpunkt:
#: Luisa hat beides noch nicht festgelegt (SEO-Analyse, „Offene Angaben“). Ein
#: leerer ``text`` nimmt jede Erwähnung der Übergabe von den Seiten.
ABHOLUNG = {'ort': 'Lübeck', 'text': 'Persönliche Übergabe in Lübeck nach Absprache.'}

#: Herkunft in einem Satz. Belegt durch ``HERKUNFT`` und die Archivnummern
#: Nº 001 bis 005 (Alsfeld); Gewerbe und Sitz Lübeck laut ``ANBIETERIN``.
HERKUNFT_SATZ = ('Angefangen hat Luviq in Alsfeld im Vogelsbergkreis, mit den ersten fünf '
                 'Stücken Nº 001 bis 005. Seit Herbst 2026 entsteht jedes Stück in Lübeck.')
