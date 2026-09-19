"""Schneidet die Webfonts auf das zu, was die Seite benutzt, und rechnet die
Werte der metrisch angepassten Ersatzschriften.

    python tools/schriften_zuschneiden.py

Braucht fontTools und brotli (`pip install fonttools brotli`, System-Python).

Schriftsystem seit dem Umbau „Nachtausgabe" (19.09.2026,
`Design/luviq/FINALER-BAUPLAN.md` § 1 in den Firmenunterlagen):

  · Cormorant Garamond kursiv 500 – Überschriften, Markensatz, Zitat
  · Schibsted Grotesk 400–700     – Text; 700 gesperrt für die Wortmarke
  · JetBrains Mono 400–500        – Nummern, Daten, Uhr, Kopfzeilen

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

AUFTRAG = {
    "cormorant-garamond-latin-wght-italic.woff2": {"wght": 500},
    "cormorant-garamond-latin-ext-wght-italic.woff2": {"wght": 500},
    "schibsted-grotesk-latin-wght-normal.woff2": {"wght": (400, 700)},
    "schibsted-grotesk-latin-ext-wght-normal.woff2": {"wght": (400, 700)},
    "jetbrains-mono-latin-wght-normal.woff2": {"wght": (400, 500)},
    "jetbrains-mono-latin-ext-wght-normal.woff2": {"wght": (400, 500)},
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


def main() -> int:
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
    for lizenz in QUELLE.glob("OFL-*.txt"):
        shutil.copy2(lizenz, ZIEL / lizenz.name)
    _ersatzwerte()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
