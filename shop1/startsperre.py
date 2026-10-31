"""Startsperre des Verkaufs: was erfüllt sein muss, bevor ``VERKAUF_AKTIV`` wirkt.

Anlass (29.10.2026): Luisa Brehler hat das Gewerbe „LUVIQ" zum 01.11.2026
angemeldet. Verkaufen darf der Shop trotzdem erst, wenn auch die Pflichten
rund um den Versandhandel stehen (``Buero\\luisa\\planung\\START-LISTE-LUISA.md``
§ 5/§ 8). Damit ein zu früh gesetztes ``VERKAUF_AKTIV=1`` in Railway nicht
versehentlich einen Shop mit unfertigen Rechtstexten öffnet, prüft
``settings.py`` beim Start diese Liste: Steht auch nur ein Grund darauf,
bleibt der Verkauf aus, und ``pruefe_seite`` nennt den Grund im Log.

Bewusst ohne Django-Import: ``settings.py`` lädt dieses Modul, bevor Django
eingerichtet ist. Die Tests übersteuern ``settings.VERKAUF_AKTIV`` direkt und
prüfen die Sperre hier als Funktion.
"""

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

#: Frühester Verkaufstag: Beginn des Gewerbes laut Anmeldung (22.10.2026).
#: Über ``VERKAUF_FRUEHESTENS`` (ISO-Datum) verschiebbar, nie früher als nötig.
VERKAUF_FRUEHESTENS_VORGABE = '2026-11-01'

#: Ablage der Rechtstexte. Bis 29.10.2026 sollten sie aus einem Generator kommen
#: (Agenturregel 3); seit 30.10.2026 schreibt die Agentur sie selbst, belegt jede
#: Aussage gegen Code und Gesetz und lässt sie unabhängig gegenprüfen (Bericht:
#: Analysen\luviq-2026-10-30-recht\BERICHT.md). Eine leere Ablage trägt den Platzhalter.
GENERATOR_ORDNER = Path(__file__).resolve().parent / 'templates' / 'shop1' / 'legal' / 'generator'

#: Kennwort in einer noch leeren Ablage. Wer den Generator-Text einfügt,
#: ersetzt den ganzen Dateiinhalt – damit verschwindet auch dieses Wort.
PLATZHALTER = 'GENERATOR-TEXT-FEHLT'

#: Rechtstexte, ohne die nicht verkauft wird. Impressum und Datenschutz sind
#: auch ohne Verkauf online und werden ersetzt, sobald Luisa freigibt; für den
#: Verkauf ist der Datenschutztext mit Shop, Zahlung und Versand Pflicht.
PFLICHT_TEXTE = {
    'agb': 'AGB',
    'widerruf': 'Widerrufsbelehrung mit Muster-Widerrufsformular',
    'datenschutz': 'Datenschutzerklärung mit Shop, Zahlung und Versand',
}

#: Was der Code selbst noch nicht kann. Wer es baut, setzt den Wert auf True
#: (mit Test) – dann fällt der Grund aus der Liste.
#: Versandkosten: Bestellweg und Preisangabe kennen keine Versandkosten; ein
#: Betrag (oder „versandkostenfrei") ist Luisas Entscheidung (PAngV § 6).
VERSANDKOSTEN_IM_BESTELLWEG = True  # Runde 3 (30.10.2026): Versand im Preis enthalten (luviq_daten.VERSAND['kosten'] = 0), Preisangabe „inkl. Versand“
#: Elektronische Widerrufsfunktion („Vertrag widerrufen", § 356a BGB, seit
#: 19.06.2026 für Online-Verträge mit Verbrauchern).
WIDERRUFSFUNKTION_VORHANDEN = True  # 30.10.2026: /vertrag-widerrufen/ (views/widerruf.py, Modell Widerruf, Mails, Tests test_widerruf)


def heute_berlin(jetzt=None):
    """Heutiges Datum in Berlin (Ortszeit), unabhängig von der Serverzeit.

    ``settings.py`` lädt dieses Modul, bevor Django ``TIME_ZONE`` setzt; auf Railway
    (UTC) wäre um 00:00 MEZ noch der Vortag und der Verkauf bliebe bis 01:00 gesperrt.
    ``jetzt`` (mit Zeitzone) ist für Tests. Fehlt die Zeitzonen-Datenbank, gilt MEZ (UTC+1)."""
    jetzt = jetzt or datetime.now(timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        zone = ZoneInfo('Europe/Berlin')
    except Exception:
        zone = timezone(timedelta(hours=1))
    return jetzt.astimezone(zone).date()


def fruehester_tag():
    roh = os.getenv('VERKAUF_FRUEHESTENS', VERKAUF_FRUEHESTENS_VORGABE).strip()
    try:
        return date.fromisoformat(roh)
    except ValueError:
        return date.fromisoformat(VERKAUF_FRUEHESTENS_VORGABE)


def generator_text_fehlt(name, ordner=None):
    """True, wenn die Ablage ``<name>.html`` fehlt, leer ist oder den Platzhalter trägt."""
    datei = (ordner or GENERATOR_ORDNER) / f'{name}.html'
    try:
        inhalt = datei.read_text(encoding='utf-8')
    except OSError:
        return True
    return PLATZHALTER in inhalt or not inhalt.strip()


def sperrgruende(heute=None, umgebung=None, ordner=None):
    """Alle Gründe, aus denen der Verkauf noch nicht öffnen darf (leer = startbereit)."""
    heute = heute or heute_berlin()
    umgebung = os.environ if umgebung is None else umgebung
    gruende = []
    tag = fruehester_tag()
    if heute < tag:
        gruende.append(f'Verkauf erst ab {tag:%d.%m.%Y} (Beginn des Gewerbes).')
    for name, was in PFLICHT_TEXTE.items():
        if generator_text_fehlt(name, ordner):
            gruende.append(f'{was} fehlt (shop1/templates/shop1/legal/generator/{name}.html).')
    if not umgebung.get('LUCID_REGISTRIERNUMMER', '').strip():
        gruende.append('Verpackungsregister: LUCID_REGISTRIERNUMMER ist nicht gesetzt '
                       '(Registrierung und Systemvertrag vor dem ersten Paket).')
    if not VERSANDKOSTEN_IM_BESTELLWEG:
        gruende.append('Versandkosten sind im Bestellweg und bei den Preisen noch nicht eingebaut.')
    if not WIDERRUFSFUNKTION_VORHANDEN:
        gruende.append('Elektronische Widerrufsfunktion („Vertrag widerrufen", § 356a BGB) fehlt.')
    return gruende
