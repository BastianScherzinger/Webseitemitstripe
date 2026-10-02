"""Zieht das Critical CSS je Seitentyp aus `shop1/static/shop1/luviq.css`.

    python tools/kritisches_css.py            # schreibt shop1/templates/shop1/stile/kritisch-<seitentyp>.html
    python tools/kritisches_css.py --pruefen  # Exit 1, wenn eine Datei veraltet ist

Critical CSS heißt: das, was im ersten Bildschirm einer Seite gebraucht wird —
Schriften, Tokens, Grundstil, Kopf, Laufband, Fuß (auf kurzen Seiten steht er im
ersten Bildschirm) und je Seitentyp der Teil, der dort oben steht (`PROFILE`).
`shop1/templates/shop1/teile/stil_kritisch.html` setzt die passende Datei inline
in den `<head>`; `luviq.css` selbst lädt danach ohne Blockierung nach.

Die Dateien sind Vorlagen, damit die Schriftadressen über `{% static %}` die
ausgelieferten, gehashten Namen bekommen (in `luviq.css` stehen sie relativ). Sie
werden nie von Hand gepflegt: ändert sich `luviq.css`, läuft dieses Skript neu —
ein Test (`test_ladezeit.KritischesCssTest`) hält beides gegeneinander.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "shop1" / "static" / "shop1" / "luviq.css"
ZIEL_ORDNER = WURZEL / "shop1" / "templates" / "shop1" / "stile"

#: Klassen, die auf jeder neu gebauten Seite oben stehen: Kopf, Laufband, Knöpfe,
#: Meldungen, Abschnittsrahmen und die feste Leiste am Handy. Den Fuß trägt nur die
#: kurze Danke-Seite (Seitentyp „danke“): auf langen steht er weit unterhalb des ersten
#: Bildschirms, und jedes Kilobyte Critical CSS geht bei jedem Abruf mit (PF20).
BASIS = {
    "lv-seite", "lv-kopf", "lv-leiste", "lv-band",
    "lv-serif", "lv-nr", "lv-klein", "lv-versteckt", "lv-sprung", "lv-knopf", "lv-link",
    "lv-wm", "lv-nav", "lv-nav-anfrage", "lv-kopf-rechts", "lv-ig", "lv-konto", "lv-menue",
    "lv-menue-klein", "lv-meldungen", "lv-meldung", "lv-brotkrume", "lv-abschnitt",
    "lv-abschnittskopf", "lv-ohne-linie",
}

#: Je Seitentyp, was zusätzlich im ersten Bildschirm steht.
PROFILE = {
    # Startseite: Hero H4, Drop-Kasten mit Uhr und Eintragsfeld; darunter der Abschnitt
    # „Motiv anfragen“ (auf hohen Tablets noch im ersten Bildschirm).
    "start": {"lv-hero", "lv-mast", "lv-pano", "lv-unterbild", "lv-satz", "lv-lead",
              "lv-dropkasten", "lv-dl", "lv-uhr", "lv-feldzeile", "lv-antwort", "lv-anfragen",
              "lv-ablauf", "lv-anfragekasten", "lv-frage", "lv-chips", "lv-chip"},
    # Archiv: Raster aus Karten.
    "archiv": {"lv-raster", "lv-karte", "lv-karte-kopf", "lv-material", "lv-preis", "lv-leer"},
    # Stückseite: Bild, Nummer, Datenliste, Knöpfe.
    "stueck": {"lv-stueck", "lv-stueck-bild", "lv-stueck-nummer", "lv-stueck-text",
               "lv-stueck-preis", "lv-status", "lv-daten", "lv-stueck-knoepfe"},
    # Luisa (Über uns): Fließtext, Zitat, Ablauf.
    "luisa": {"lv-luisa", "lv-luisa-text", "lv-ablauf", "lv-prosa"},
    # Motiv anfragen: Formular mit Auswahl und Stationen.
    "anfrage": {"lv-anfrageseite", "lv-satz", "lv-lead", "lv-stationen", "lv-formular", "lv-feld",
                "lv-feld2", "lv-wahl", "lv-wahlen", "lv-fehler", "lv-falle"},
    # Danke-Seite: so kurz, dass der Fuß schon im ersten Bildschirm steht.
    "danke": {"lv-danke", "lv-fuss", "lv-fuss-wm", "lv-recht"},
}

_KLASSE = re.compile(r"\.(lv-[a-z0-9-]+)")


def _einheiten(text: str) -> list[str]:
    """Zerlegt CSS-Text in Regeln und At-Blöcke der obersten Ebene (ohne Kommentare)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    einheiten, tiefe, start = [], 0, 0
    zeichenkette = ""
    for i, zeichen in enumerate(text):
        if zeichenkette:
            if zeichen == zeichenkette:
                zeichenkette = ""
            continue
        if zeichen in "\"'":
            zeichenkette = zeichen
        elif zeichen == "{":
            tiefe += 1
        elif zeichen == "}":
            tiefe -= 1
            if tiefe == 0:
                einheiten.append(text[start:i + 1].strip())
                start = i + 1
    rest = text[start:].strip()
    if rest:
        einheiten.append(rest)
    return [e for e in einheiten if e]


def _auswahlen(kopf: str) -> list[str]:
    teile, tiefe, aktuell = [], 0, ""
    for zeichen in kopf:
        if zeichen in "([":
            tiefe += 1
        elif zeichen in ")]":
            tiefe -= 1
        if zeichen == "," and tiefe == 0:
            teile.append(aktuell.strip())
            aktuell = ""
        else:
            aktuell += zeichen
    teile.append(aktuell.strip())
    return [t for t in teile if t]


def _kritisch_regel(regel: str, erlaubt: set[str]) -> bool:
    """Eine Regel gehört dazu, wenn mindestens eine ihrer Auswahlen nur erlaubte
    `lv-`-Klassen nennt (Auswahlen ohne `lv-`-Klasse wie `html`, `:root`, `.lv a` zählen
    immer). `.lv-alt` und `.lv-admin` sind nie erlaubt: diese Seiten bekommen kein
    Critical CSS."""
    kopf = regel.split("{", 1)[0]
    for auswahl in _auswahlen(kopf):
        klassen = set(_KLASSE.findall(auswahl))
        if klassen <= erlaubt:
            return True
    return False


def _verdichten(text: str) -> str:
    """Zeilenumbrüche und überflüssige Leerzeichen weg — außerhalb von Zeichenketten
    (`"Cormorant Garamond"`, `content:"·"`), dort bleibt alles stehen. Die Leerzeichen
    um `+` und `-` in `calc()` bleiben ebenfalls (sie sind Pflicht)."""
    text = re.sub(r"\s*\n\s*", " ", text).strip()
    teile = re.split(r'("[^"]*")', text)
    for n in range(0, len(teile), 2):
        stueck = re.sub(r"\s*([{};,>~])\s*", r"\1", teile[n])
        stueck = re.sub(r":\s+", ":", stueck)
        teile[n] = stueck.replace(";}", "}")
    return "".join(teile)


def kritisch(css: str, profil: str) -> str:
    """Das Critical CSS eines Seitentyps zu einem `luviq.css`-Text."""
    erlaubt = BASIS | PROFILE[profil]
    behalten: list[str] = []
    for einheit in _einheiten(css):
        kopf = einheit.split("{", 1)[0].strip()
        if kopf.startswith("@keyframes"):
            behalten.append(einheit)  # unten gefiltert, wenn nichts darauf verweist
        elif kopf.startswith("@media"):
            innen = einheit[einheit.index("{") + 1:einheit.rindex("}")]
            regeln = [r for r in _einheiten(innen) if _kritisch_regel(r, erlaubt)]
            if regeln:
                behalten.append(kopf + "{" + "".join(regeln) + "}")
        elif kopf.startswith("@font-face"):
            # Der Zusatzteil der Textschrift (latin-ext) kommt erst mit luviq.css: er lädt
            # nur, wenn ein Zeichen daraus auf der Seite steht, und spart so Bytes je Abruf.
            if "latin-ext" not in einheit:
                behalten.append(einheit)
        elif _kritisch_regel(einheit, erlaubt):
            behalten.append(einheit)
    gesamt = "\n".join(_verdichten(e) for e in behalten)
    ergebnis = []
    for zeile in gesamt.split("\n"):
        if zeile.startswith("@keyframes"):
            name = zeile.split("{", 1)[0].split()[1]
            rest = gesamt.replace(zeile, "")
            if not re.search(r"animation[^;}]*\b" + re.escape(name) + r"\b", rest):
                continue
        ergebnis.append(zeile)
    return "\n".join(ergebnis) + "\n"


def vorlage(css: str, profil: str) -> str:
    """Der Inhalt der Vorlagendatei: Critical CSS, Schriftadressen über `{% static %}`."""
    text = kritisch(css, profil)
    for verboten in ("{{", "{%", "{#"):
        if verboten in text:
            raise ValueError(f"CSS enthält {verboten!r} — das wäre Vorlagensyntax")
    text = re.sub(r'url\("fonts/([^"]+)"\)',
                  lambda m: 'url("{% static \'shop1/fonts/' + m.group(1) + '\' %}")', text)
    kopf = ("{% load static %}{% comment %}Critical CSS „" + profil + "“, erzeugt mit "
            "tools/kritisches_css.py aus luviq.css — nicht von Hand ändern.{% endcomment %}")
    return kopf + text


def ziel(profil: str) -> Path:
    return ZIEL_ORDNER / f"kritisch-{profil}.html"


def main() -> int:
    """Schreibt (oder mit ``--pruefen`` vergleicht) die Critical-CSS-Vorlagen aller Seitentypen."""
    css = QUELLE.read_text(encoding="utf-8")
    veraltet = False
    for profil in PROFILE:
        neu = vorlage(css, profil)
        datei = ziel(profil)
        if "--pruefen" in sys.argv:
            if not datei.exists() or datei.read_text(encoding="utf-8") != neu:
                print(f"{datei.name} ist veraltet — python tools/kritisches_css.py")
                veraltet = True
            continue
        ZIEL_ORDNER.mkdir(parents=True, exist_ok=True)
        datei.write_text(neu, encoding="utf-8", newline="\n")
        print(f"{datei.relative_to(WURZEL)}: {len(neu.encode('utf-8')) / 1024:.1f} KB "
              f"(Quelle {QUELLE.stat().st_size / 1024:.1f} KB)")
    return 1 if veraltet else 0


if __name__ == "__main__":
    raise SystemExit(main())
