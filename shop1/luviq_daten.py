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
#: Seit P5b (A/B-Sieger B) nicht mehr die H1 der Startseite, sondern die Überschrift
#: des Abschnitts „Motiv anfragen“ (``index.html``, ``#anfragen``).
MARKENSATZ = 'Sag mir, was du willst — ich mal’s dir.'

#: H1 der Startseite (P5b, Kundenpanel-Sieger B, 30.10.2026): nennt die Technik und das Unikat.
HERO_H1 = 'Mit Bleiche gemalt. Jedes Stück gibt es nur einmal.'

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

#: Pinterest-Unternehmenskonto (Website bestätigt) und ProvenExpert-Profil der Marke
#: (beide am 30.10.2026 abgerufen, 200). Die Adresse ``/luviq-luebeck/`` bei
#: ProvenExpert liefert 410, richtig ist ``/de-de/luviq/``.
PINTEREST = 'https://www.pinterest.com/luviqarchive/'
PROVENEXPERT = 'https://www.provenexpert.com/de-de/luviq/'

#: Luisas persönliche Profile (Facebook, LinkedIn): gehören an den Personenknoten,
#: nicht an die Marke (Analyse 30.10.2026, C5).
FACEBOOK_LUISA = 'https://www.facebook.com/profile.php?id=61595684296277'
LINKEDIN_LUISA = 'https://www.linkedin.com/in/luisa-brehler-89a050448'

#: Belegte Profiladressen für ``sameAs`` (Schema) und ``llms.txt``.
PROFILE = (INSTAGRAM, TIKTOK, GOOGLE_PROFIL, PINTEREST, PROVENEXPERT)

#: ``sameAs`` des Personenknotens Luisa Brehler.
PROFILE_PERSON = (FACEBOOK_LUISA, LINKEDIN_LUISA)

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

#: Das Stück im Hero-Foto (static/shop1/images/luviq/hero-engel-*, P3 29.10.2026):
#: das Engel-Shirt, Studioaufnahme des echten Motivs (KI-Aufnahme, deshalb im
#: Alt-Text nur das sichtbare Motiv, keine Angabe zu Preis oder Größe). Nummer
#: und Name kommen aus dem Archiv, damit die Bildunterschrift und die Karte
#: dasselbe Stück gleich nennen (EIG134): zuerst über die Archivnummer
#: ``nummer`` (``None`` = keine festgelegt), sonst über den ersten Namen, der
#: einen der ``suche``-Begriffe enthält. Ohne Treffer steht nur die
#: Beschreibung des Fotos da, kein erfundener Stückname und keine Nummer.
#: ``status`` steht rechts in der Bildunterschrift: „Unikat“, kein Preis, kein Datum.
HERO_STUECK = {'nummer': None, 'suche': ('engel',), 'name': 'Shirt mit Engel-Motiv',
               'alt': 'Studiobild (KI) aus dem echten Foto: Rückenansicht eines schwarzen T-Shirts auf einem Holzbügel vor dunkler Betonwand; darauf ein handgebleichtes Linienmotiv: ein Engel mit Flügeln hält eine Rose, rechts daneben ein kleiner Stern',
               'status': 'Unikat'}

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


# ── Startseite (Paket P3, 29.10.2026) ────────────────────────────────────────

def _lead():
    """Antwortsatz unter der H1 (höchstens 45 Wörter, Quelle SEO-Analyse C1; Lead B, P5b).

    Der letzte Satz setzt sich aus ``VERSAND`` und ``ABHOLUNG`` zusammen; ohne
    Übergabetext (``ABHOLUNG['text']`` leer) bleibt nur der Versand."""
    teile = ['Luisa Brehler aus Lübeck zieht die Farbe mit Bleiche aus dem Stoff – nichts ist '
             'aufgedruckt. Das Engel-Shirt ist das erste Stück']
    if VERSAND.get('gebiet'):
        letzter = f'Versand in {VERSAND["gebiet"]}'
        if ABHOLUNG.get('text'):
            letzter += f', Übergabe in {ABHOLUNG["ort"]} nach Absprache'
        teile.append(letzter)
    return '; '.join(teile) + '.'


#: Erster Absatz nach der Überschrift. Nennt den Ort, weil Antwortmaschinen
#: den ersten Absatz zitieren (test_inhalt: Anbieter oder Ort im ersten Absatz).
LEAD = _lead()


def _vertrauen():
    """Die drei belegten Aussagen der Vertrauensleiste; leere Einträge fallen weg."""
    eintraege = []
    if VERSAND.get('gebiet'):
        eintraege.append(f'Versand in {VERSAND["gebiet"]}')
    eintraege.append(ABHOLUNG.get('text', ''))
    eintraege.append('Von Luisa in Lübeck von Hand gebleicht')
    return [e for e in eintraege if e]


#: Vertrauensleiste unter dem Hero. Nur Aussagen, die im Code oder in den AGB
#: stehen (Versand: ``VERSAND``, Übergabe: ``ABHOLUNG``, Technik: Bleiche).
VERTRAUEN = _vertrauen()

#: Die Wege der Startseite: (Überschrift, Satz, Routenname, Ankertext). Der Anker
#: beschreibt das Ziel (SEO-Analyse § 4.2). ``motiv_anfragen`` erscheint nur, wenn
#: die Motivanfrage läuft (Vorlage prüft ``motivanfrage_aktiv``).
WEGE = [
    ('Handbemalte Unikate',
     'Hochwertige Hoodies, Pullover und Shirts, gebraucht oder neu, jedes Motiv nur einmal.',
     'produkte', 'alle Stücke im Archiv'),
    ('Dein eigenes Teil',
     'Du beschreibst dein Motiv, bekommst Vorschläge, erst dann wird gemalt.',
     'motiv_anfragen', 'eigenes Motiv anfragen'),
]

#: Kurzfilme für den Abschnitt „Film“ der Startseite: (Datei unter
#: ``static/shop1/video/``, Poster unter ``static/shop1/images/luviq/``, Titel,
#: Untertitel). Leer ⇒ der Abschnitt wird nicht ausgegeben, kein Platzhalter.
FILME = []

#: Luviq-Shirts mit Logo: noch keine Daten, deshalb kein Abschnitt. Hook für später.
LINIE_SHIRTS = None

#: Abschnitt „So sieht es in echt aus“ direkt nach dem Hero (Bastian, 29.10.2026):
#: das Studiobild ist aus dem echten Stück entstanden, jedes Unikat sieht etwas
#: anders aus. ``ECHT_FOTOS`` nimmt später weitere echte Handyfotos auf:
#: (Dateiname ohne Breite und Endung unter ``static/shop1/images/luviq/``,
#: Breiten, Maße der größten Datei als (Breite, Höhe), Alt-Text, Bildunterschrift).
#: Die Dateien ``<name>-<breite>.webp`` erzeugt ``tools/bilder_zuschneiden.py``.
#: Leer ⇒ der Abschnitt entfällt.
ECHT_TITEL = 'So sieht es in echt aus'
ECHT_TEXT = ('So sieht das Shirt wirklich aus: Handyfoto vom echten Stück. Das Bild oben ist daraus '
             'als Studiobild erstellt (KI). Jedes Unikat ist von Hand gemalt und sieht deshalb '
             'ein bisschen anders aus.')
#: Kleine Bildunterschrift am Hero-Bild (P5b): sagt ehrlich, dass es ein KI-Studiobild ist.
HERO_BILDUNTERSCHRIFT = 'Studiobild (KI) aus dem echten Foto'
ECHT_FOTOS = [
    ('echt-engel-2', (480, 720, 960), (960, 1080),
     'Handyfoto des fertigen Engel-Shirts: schwarzes T-Shirt von hinten, darauf ein handgebleichter '
     'Engel mit Flügeln, der eine Rose hält, und rechts daneben ein kleiner Stern',
     'Handyfoto, ungeschönt'),
]


# ── Rahmen: Ankündigung, Navigation, Fuß, Leiste (Paket P2, 29.10.2026) ──────

def hinweis(verkauf_aktiv, shop_oeffnet=''):
    """Die Teile der Ankündigungszeile über dem Kopf (ersetzt das Laufband).

    Ohne Verkauf steht als erstes der abgestimmte Satz ``shop_oeffnet`` (siehe
    ``verkauf.oeffnungs_satz``, wörtlich, nicht umformulieren), mit Verkauf
    „Shop ist offen“. Versand und Übergabe kommen aus ``VERSAND`` und
    ``ABHOLUNG``; ein leerer ``ABHOLUNG['text']`` nimmt die Übergabe heraus."""
    teile = ['Shop ist offen' if verkauf_aktiv else shop_oeffnet]
    if VERSAND.get('gebiet'):
        teile.append(f'Versand in {VERSAND["gebiet"]}')
    if ABHOLUNG.get('text'):
        teile.append(f'Übergabe in {ABHOLUNG["ort"]} nach Absprache')
    return [t for t in teile if t]


#: Die Wege im Kopf und im Handy-Menü: (Routenname, Beschriftung, Beschriftung mit
#: Verkauf, nur wenn die Motivanfrage aktiv ist). „Drop“ und „Entstehung“ gibt es
#: nicht mehr (Design-Analyse Befund #12).
NAVIGATION = [
    ('produkte', 'Stücke', 'Unikate', False),
    ('motiv_anfragen', 'Motiv anfragen', 'Motiv anfragen', True),
    ('wissen', 'Wissen', 'Wissen', False),
    ('ueber_uns', 'Luisa', 'Luisa', False),
    ('kontakt', 'Kontakt', 'Kontakt', False),
]

#: Der Fuß in zwei Linkgruppen (die dritte, „Rechtliches“, hängt an Schaltern und
#: steht in ``base.html``). Je Eintrag: (Routenname, Anker, Beschriftung, Beschriftung
#: mit Verkauf, nur wenn die Motivanfrage aktiv ist). Adressen ändern sich nicht:
#: ``liefergebiet`` heißt jetzt „Versand & Abholung“, bleibt aber ``/liefergebiet/``.
FUSS = [
    ('Stücke', [
        ('produkte', '', 'Archiv', 'Unikate', False),
        ('motiv_anfragen', '', 'Motiv anfragen', 'Motiv anfragen', True),
        ('home', '#warteliste', 'Warteliste', 'Warteliste', False),
    ]),
    ('Hilfe', [
        ('liefergebiet', '', 'Versand & Abholung', 'Versand & Abholung', False),
        ('wissen_groesse', '', 'Größe bei Einzelstücken', 'Größe bei Einzelstücken', False),
        ('wissen_pflege', '', 'Pflege', 'Pflege', False),
        ('wissen', '', 'Wissen', 'Wissen', False),
        ('kontakt', '', 'Kontakt', 'Kontakt', False),
        ('gaestebuch', '', 'Gästebuch', 'Gästebuch', False),
    ]),
]


def _wege(eintraege, verkauf_aktiv, motiv_aktiv, mit_anker):
    wege = []
    for e in eintraege:
        route, anker = (e[0], e[1]) if mit_anker else (e[0], '')
        rest = e[2:] if mit_anker else e[1:]
        name, name_verkauf, nur_motiv = rest
        if nur_motiv and not motiv_aktiv:
            continue
        wege.append({'route': route, 'anker': anker, 'name': name_verkauf if verkauf_aktiv else name})
    return wege


def navigation(verkauf_aktiv, motiv_aktiv):
    """Die Wege für Kopf und Handy-Menü, fertig beschriftet."""
    return _wege(NAVIGATION, verkauf_aktiv, motiv_aktiv, False)


def fuss(verkauf_aktiv, motiv_aktiv):
    """Die Linkgruppen des Fußes: Liste aus (Titel, Wege)."""
    return [(titel, _wege(eintraege, verkauf_aktiv, motiv_aktiv, True)) for titel, eintraege in FUSS]


def leiste(verkauf_aktiv, tag=None, heute=None):
    """Handy-Leiste: (Satz, Beschriftung des Knopfs, Routenname, Anker).

    Der Tag kommt aus ``settings.VERKAUF_FRUEHESTENS`` (``tag``), nie aus einer Vorlage;
    „frühestens“ bleibt dabei, wie im abgestimmten Satz ``verkauf.oeffnungs_satz``. Liegt der
    Tag hinter uns und der Verkauf ist noch aus, steht kein Datum mehr da."""
    if verkauf_aktiv:
        return ('Jedes Stück nur einmal', 'Stücke ansehen', 'produkte', '')
    heute = heute or timezone.localdate()
    if tag and heute < tag:
        satz = f'Shop öffnet frühestens am {tag.day}. {_MONATE[tag.month - 1]}'
    else:
        satz = 'Der Shop ist noch nicht geöffnet'
    return (satz, 'Vormerken', 'home', '#warteliste')


#: Routennamen, auf denen es keine Handy-Leiste gibt: Rechtsseiten, Konto, Kasse,
#: Motivanfrage (hat ihr eigenes Formular). Fehlerseiten (ohne Routenname) und das
#: Admin-Panel bekommen sie ebenfalls nie (``base.html``).
LEISTE_AUS = frozenset({
    'impressum', 'datenschutz', 'agb', 'motiv_anfragen', 'motiv_danke',
    'login', 'logout', 'register', 'profil', 'change_password', 'delete_account',
    'verify_email', 'verify_email_no_slash', 'resend_verification',
    'password_reset', 'password_reset_done', 'password_reset_confirm', 'password_reset_complete',
    'warenkorb', 'checkout', 'payment', 'payment_success', 'payment_cancel',
    'newsletter_abmelden', 'newsletter_bestaetigen', 'kontakt_danke', 'lockout',
})


# ── P4: Stücke-Seiten ────────────────────────────────────────────────────────

#: Schriftzug über dem Bild eines Stücks, das nicht mehr zu haben ist (Karte und Stückseite).
#: Die fünf Archivstücke Nº 001–005 sind „vergeben“, aber nie über den Shop verkauft worden
#: (Migration 0022: keine Rechnungen) – für sie steht „Vergeben“, nie „Verkauft“, sonst wäre es
#: eine falsche Tatsachenbehauptung. „Verkauft“ steht nur bei einem Stück, das nicht als Archiv
#: gekennzeichnet ist und nach einer Bestellung Bestand 0 hat (``Produkt.band_wort``).
VERGEBEN_WORT = 'Vergeben'
#: Band der fünf ersten Stücke Nº 001–005: Bastian 30.10.2026 – „wie Referenzen, nicht offiziell
#: verkauft, als Beispiele drin, kommen später raus“; sie wurden verschenkt, deshalb „Vergeben“.
REFERENZ_WORT = 'Vergeben'
REFERENZ_NUMMERN = range(1, 6)
VERKAUFT_WORT = 'Verkauft'

#: Die Technik in einem Satz, auf Stückseite und Luisa-Seite gleich (Bastian 29.10.2026).
BLEICHE_SATZ = ('Mit Bleiche gemalt: Die Farbe wird aus dem Stoff gezogen, nichts ist aufgedruckt. '
                'Deshalb steht das Motiv in Bleich-Beige auf dem schwarzen Stoff.')

#: Statische Bilder, die KI-Studiobilder aus einem echten Foto sind (Präfixe). Ihr Alt-Text,
#: der Sitemap-Bildtitel und die Bildunterschrift nennen das ehrlich (Analyse 30.10.2026, C7).
KI_BILD_PRAEFIXE = ('shop1/images/luviq/hero-engel',)

#: Erstes offizielles Stück Nº 006, angelegt von ``manage.py luviq_engel_anlegen`` (aus
#: ``start.sh``). Quelle: Bastian am 29.10.2026, 23:45. Nicht belegt und deshalb nicht
#: eingetragen: Maße in cm, Marke des Shirts, Pflegeversprechen. Preis 69 € wird erst
#: mit dem Verkauf gezeigt (``verkauf_aktiv``), vorher steht nur „Unikat“.
ENGEL_STUECK = {
    'slug': 'engel-shirt-handgebleicht',
    'name': 'Engel-Shirt, mit Bleiche gemalt',
    'preis': '69.00',
    'masse': 'Größe M',
    'material': '100 % Baumwolle',
    'technik': 'Mit Bleiche von Hand gemalt',
    'zustand': 'Neu',  # Bastian 30.10.2026: „eigentlich komplett neu“
    'seo_titel': 'Engel-Shirt mit Bleiche gemalt – Luviq Lübeck',
    'seo_beschreibung': ('Unikat Nº 006: T-Shirt mit Engel, Rose und Stern, von Hand mit Bleiche '
                         'gemalt. 100 % Baumwolle, Größe M. Luviq, Lübeck.'),
    'beschreibung': ('Ein T-Shirt aus 100 % Baumwolle in Größe M. Auf dem Rücken steht ein Engel mit '
                     'Rose und einem Stern, von Hand gemalt – viel Handarbeit, genau einmal. '
                     'Vorne ein kleines Luviq-Zeichen auf Herzhöhe – Foto folgt.'),
    # Statische Bilder (siehe produktbilder.py): Studiobild mit Stern (Hero-Zuschnitt 4:5) zuerst,
    # dann das echte Foto. Vorderseiten-Fotos später als weitere „Zusatzbilder“ im Admin eintragen.
    'bild_statisch': 'shop1/images/luviq/hero-engel-45-{w}.webp@480,640,800#800x999',
    'zusatzbilder': [
        {'bild_statisch': 'shop1/images/stuecke/engel-echt-45-{w}.webp@600,900,960#960x1200',
         'breite': 960, 'hoehe': 1200,
         'alt': ('Echtes Foto des fertigen Engel-Shirts von hinten: schwarzes T-Shirt, darauf in '
                 'Bleich-Beige ein Engel mit Flügeln, Rose und Stern')},
    ],
}
