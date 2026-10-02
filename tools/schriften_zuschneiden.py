"""Schneidet die Webfonts auf das zu, was die Seite benutzt, und rechnet die
Werte der metrisch angepassten Ersatzschriften.

    python tools/schriften_zuschneiden.py

Braucht fontTools und brotli (`pip install fonttools brotli`, System-Python).

Schriftsystem seit dem Umbau „Nachtausgabe" (19.09.2026,
`Design/luviq/FINALER-BAUPLAN.md` § 1 in den Firmenunterlagen):

  · Cormorant Garamond kursiv 500 – Überschriften, Markensatz, Zitat
  · Schibsted Grotesk 400–700     – Text; 700 gesperrt für die Wortmarke
  · JetBrains Mono 400–500        – Nummern, Daten, Uhr, Kopfzeilen

Höchstens vier Schriftdateien (Messpunkte PF27/VL16): Cormorant und JetBrains
Mono liegen je in EINER Datei, die den Umfang von „latin" und „latin-ext"
zusammen trägt; nur Schibsted Grotesk bleibt in zwei Dateien (die große
Textschrift: ihr Zusatzteil wird nur geladen, wenn ein Zeichen daraus auf der
Seite steht). Cormorant entsteht durch Zusammenführen der beiden Quellen,
JetBrains Mono durch Zuschnitt der vollständigen Variablenschrift
(`_quellen/schriften/jetbrains-mono-gesamt-wght-normal.ttf`, Google Fonts,
OFL) auf dieselben Unicode-Bereiche — fontTools kann zwei variable Schriften
nicht zusammenführen.

Quellen (Fontsource, variable Schriften, OFL) liegen unverändert unter
`_quellen/schriften/`; das Skript überschreibt `shop1/static/shop1/fonts/`.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WURZEL = Path(__file__).resolve().parent.parent
QUELLE = WURZEL / "_quellen" / "schriften"
ZIEL = WURZEL / "shop1" / "static" / "shop1" / "fonts"

#: Unicode-Bereiche „latin" und „latin-ext" (wie in luviq.css `unicode-range`).
LATIN = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
         "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
LATIN_EXT = ("U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,"
             "U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,"
             "U+2113,U+2C60-2C7F,U+A720-A7FF")

#: Cormorant: zwei Quellen → eine zusammengeführte Datei.
ZUSAMMEN = {
    "cormorant-garamond-italic.woff2": (
        ("cormorant-garamond-latin-wght-italic.woff2",
         "cormorant-garamond-latin-ext-wght-italic.woff2"), {"wght": 500}),
}

#: JetBrains Mono: eine vollständige Quelle → auf LATIN + LATIN_EXT zugeschnitten.
ZUGESCHNITTEN = {
    "jetbrains-mono-normal.woff2": ("jetbrains-mono-gesamt-wght-normal.ttf", {"wght": (400, 500)}),
}

AUFTRAG = {
    "schibsted-grotesk-latin-wght-normal.woff2": {"wght": (400, 700)},
    "schibsted-grotesk-latin-ext-wght-normal.woff2": {"wght": (400, 700)},
}

ERSATZ = {
    "Cormorant Ersatz": ("cormorant-garamond-latin-wght-italic.woff2", {"wght": 500},
                         r"C:\Windows\Fonts\georgiai.ttf",
                         "Sag mir, was du willst — ich mal’s dir. Wie ein Stück entsteht"),
    "Schibsted Ersatz": ("schibsted-grotesk-latin-wght-normal.woff2", {"wght": 400},
                         r"C:\Windows\Fonts\arial.ttf",
                         "Ich bemale Second-Hand-Teile von Hand, mit Bleiche und Pinsel. Größe"),
    "JetBrains Ersatz": ("jetbrains-mono-latin-wght-normal.woff2", {"wght": 400},
                         r"C:\Windows\Fonts\consola.ttf",
                         "Nº 006 · 08.10. 18:00 TAGE STD MIN SEK"),
}


def _breite(font, text: str) -> float:
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    return sum(hmtx[cmap[ord(z)]][0] for z in text if ord(z) in cmap) / font["head"].unitsPerEm


def _ersatzwerte() -> None:
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    print("\nErsatzschriften (in luviq.css eintragen):")
    for name, (datei, ort, system, muster) in ERSATZ.items():
        web = instancer.instantiateVariableFont(TTFont(QUELLE / datei), ort)
        faktor = _breite(web, muster) / _breite(TTFont(system), muster)
        upm = web["head"].unitsPerEm
        hhea = web["hhea"]
        print(f"  {name}: size-adjust {faktor * 100:.2f}%; "
              f"ascent-override {hhea.ascent / upm / faktor * 100:.2f}%; "
              f"descent-override {abs(hhea.descent) / upm / faktor * 100:.2f}%; "
              f"line-gap-override {hhea.lineGap / upm / faktor * 100:.2f}%")


def _zusammenfuehren() -> None:
    """Cormorant: „latin" und „latin-ext" als eine Datei (statische Instanz, Weite 500)."""
    import tempfile

    from fontTools.merge import Merger
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    for ziel_name, (quellen, grenzen) in ZUSAMMEN.items():
        with tempfile.TemporaryDirectory() as ordner:
            teile = []
            for n, name in enumerate(quellen):
                schrift = instancer.instantiateVariableFont(TTFont(QUELLE / name), grenzen)
                schrift.flavor = None
                pfad = Path(ordner) / f"teil{n}.ttf"
                schrift.save(pfad)
                teile.append(str(pfad))
            gesamt = Merger().merge(teile)
        gesamt.flavor = "woff2"
        ziel = ZIEL / ziel_name
        gesamt.save(ziel)
        print(f"{ziel_name:48} {len(quellen)} Quellen → {ziel.stat().st_size / 1024:6.1f} KB")


def _zuschneiden() -> None:
    """JetBrains Mono: vollständige Quelle auf LATIN + LATIN_EXT zuschneiden."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    for ziel_name, (quelle_name, grenzen) in ZUGESCHNITTEN.items():
        # Erst zuschneiden, dann die Weite eingrenzen: umgekehrt scheitert der
        # Zuschnitt an der gvar-Tabelle der teilweise eingegrenzten Schrift.
        schrift = TTFont(QUELLE / quelle_name)
        optionen = subset.Options()
        optionen.layout_features = ["*"]
        optionen.notdef_outline = True
        optionen.name_IDs = ["*"]
        werkzeug = subset.Subsetter(optionen)
        werkzeug.populate(unicodes=subset.parse_unicodes(LATIN + "," + LATIN_EXT))
        werkzeug.subset(schrift)
        schrift = instancer.instantiateVariableFont(schrift, grenzen)
        schrift.flavor = "woff2"
        ziel = ZIEL / ziel_name
        schrift.save(ziel)
        print(f"{ziel_name:48} {(QUELLE / quelle_name).stat().st_size / 1024:6.1f} KB → "
              f"{ziel.stat().st_size / 1024:6.1f} KB")


def main() -> int:
    """Erzeugt alle Schriftdateien und gibt die Werte der Ersatzschriften aus."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    ZIEL.mkdir(parents=True, exist_ok=True)
    for name, grenzen in AUFTRAG.items():
        quelle = QUELLE / name
        klein = instancer.instantiateVariableFont(TTFont(quelle), grenzen)
        klein.flavor = "woff2"
        ziel = ZIEL / name.replace("-wght", "")
        klein.save(ziel)
        print(f"{name:48} {quelle.stat().st_size / 1024:6.1f} KB → {ziel.stat().st_size / 1024:6.1f} KB")
    _zusammenfuehren()
    _zuschneiden()
    for lizenz in QUELLE.glob("OFL-*.txt"):
        shutil.copy2(lizenz, ZIEL / lizenz.name)
    _ersatzwerte()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
