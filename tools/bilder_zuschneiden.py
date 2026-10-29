"""Erzeugt alle Marken- und Hero-Bilder des Luviq-Umbaus (Paket P0) aus zwei Quelldateien.

Aufruf (aus dem Projektordner):
    ../WebseiteMAIN/.venv/Scripts/python.exe -X utf8 tools/bilder_zuschneiden.py

Jede Ausgabe entsteht aus einer Funktion mit festen Koordinaten; ein zweiter Lauf liefert
dieselben Dateien. Die Quellen werden nur gelesen. AVIF wird erzeugt, wenn Pillow es
kann (Pillow >= 11.3 hat den Encoder eingebaut); sonst entstehen nur WebP-Dateien.
"""
from pathlib import Path

from PIL import Image, ImageFilter, features

BUERO = Path(r"C:\Users\basti\Desktop\Webagentur Scherzinger\Buero\luisa\arbeitsplatz")
QUELLE_HERO = BUERO / "bilder" / "2026-10-29-chatgpt" / "engel-studio-2.png"
QUELLE_LOGO = BUERO / "grafik" / "logo-2026-10-29" / "luviq-neu-3.png"

WURZEL = Path(__file__).resolve().parent.parent
BILDER = WURZEL / "shop1" / "static" / "shop1" / "images"
ZIEL_LUVIQ = BILDER / "luviq"
ZIEL_MARKE = BILDER / "marke"

SCHWARZ = (10, 10, 10)  # #0A0A0A
AVIF = features.check("avif")
SCHARF = ImageFilter.UnsharpMask(radius=1, percent=60, threshold=0)


def verkleinern(bild, breite):
    hoehe = round(bild.height * breite / bild.width)
    return bild.resize((breite, hoehe), Image.LANCZOS).filter(SCHARF)


def webp_avif(bild, pfad_ohne_endung, qualitaet=82):
    bild.save(f"{pfad_ohne_endung}.webp", "WEBP", quality=qualitaet, method=6)
    if AVIF:
        bild.save(f"{pfad_ohne_endung}.avif", "AVIF", quality=60)


# ---------------------------------------------------------------- Hero und OG
def hero():
    quelle = Image.open(QUELLE_HERO).convert("RGB")
    hoch = quelle.crop((592, 0, 1412, 1024))  # 820 x 1024, 4:5, Buegel im Anschnitt oben
    for breite in (480, 640, 800):
        # 800 px: Qualitaet 74, damit die Datei unter 120 KB bleibt (Vorgabe Masterplan)
        webp_avif(verkleinern(hoch, breite), ZIEL_LUVIQ / f"hero-engel-45-{breite}", 74 if breite == 800 else 82)
    webp_avif(quelle.copy(), ZIEL_LUVIQ / "hero-engel-quer-1536")
    webp_avif(verkleinern(quelle, 1024), ZIEL_LUVIQ / "hero-engel-quer-1024")


def og_start():
    quelle = Image.open(QUELLE_HERO).convert("RGB")
    ausschnitt = quelle.crop((0, 109, 1536, 109 + 806))
    ausschnitt = ausschnitt.resize((1200, 630), Image.LANCZOS).filter(SCHARF)
    ausschnitt.save(ZIEL_LUVIQ / "og-start-1200x630.jpg", "JPEG", quality=85, optimize=True)


# ---------------------------------------------------------------- Logo
def logo_alpha(box, farbe):
    """Schneidet box aus dem Logo; Helligkeit wird Deckung, Farbe ein einziger Ton."""
    grau = Image.open(QUELLE_LOGO).convert("L").crop(box)
    boden = 10  # Hintergrundgrau (#0A0A0A) -> Deckung 0
    spitze = max(grau.getdata())
    alpha = grau.point(lambda v: 0 if v <= boden else min(255, round((v - boden) * 255 / (spitze - boden))))
    bild = Image.new("RGBA", grau.size, farbe + (0,))
    bild.putalpha(alpha)
    return bild


def marken_farbe():
    """Beige-Ton der hellsten Pixel (Mittel der obersten 2 % nach Helligkeit)."""
    bild = Image.open(QUELLE_LOGO).convert("RGB").crop((230, 430, 1070, 790))
    pixel = sorted(bild.getdata(), key=lambda p: sum(p))
    oberste = pixel[-max(1, len(pixel) // 50):]
    return tuple(round(sum(p[i] for p in oberste) / len(oberste)) for i in range(3))


def wortmarke(farbe):
    voll = logo_alpha((230, 430, 1070, 790), farbe)  # 840 x 360
    for breite in (840, 420, 210):
        bild = voll if breite == 840 else voll.resize((breite, round(360 * breite / 840)), Image.LANCZOS)
        bild.save(ZIEL_MARKE / f"luviq-wortmarke-{breite}.png", optimize=True)
        bild.save(ZIEL_MARKE / f"luviq-wortmarke-{breite}.webp", "WEBP", lossless=True, method=6)
    return voll


def stern_alpha(farbe):
    mitte_x, mitte_y, halb = 627, 737, 108
    stern = logo_alpha((mitte_x - halb, mitte_y - halb, mitte_x + halb, mitte_y + halb), farbe)
    return stern.resize((256, 256), Image.LANCZOS)


def stern_auf_schwarz(kante, anteil=0.72):
    """Stern mittig auf #0A0A0A, Sternhoehe = anteil * kante."""
    stern = stern_alpha(MARKE_FARBE)
    inhalt = round(kante * anteil)
    stern = stern.resize((inhalt, inhalt), Image.LANCZOS)
    flaeche = Image.new("RGBA", (kante, kante), SCHWARZ + (255,))
    versatz = (kante - inhalt) // 2
    flaeche.alpha_composite(stern, (versatz, versatz))
    return flaeche.convert("RGB")


def icons():
    stern_alpha(MARKE_FARBE).save(ZIEL_MARKE / "luviq-stern-256.png", optimize=True)
    stern_auf_schwarz(180, 0.78).save(BILDER / "apple-touch-icon.png", optimize=True)
    stern_auf_schwarz(192, 0.78).save(BILDER / "icon-192.png", optimize=True)
    stern_auf_schwarz(512, 0.78).save(BILDER / "icon-512.png", optimize=True)
    # Favicon: kleine Groessen brauchen mehr Fuellung
    gross = stern_auf_schwarz(256, 0.92)
    gross.save(BILDER / "flavicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])


def og_logo(wortmarke_bild):
    flaeche = Image.new("RGB", (1200, 630), SCHWARZ)
    breite = 720
    wm = wortmarke_bild.resize((breite, round(360 * breite / 840)), Image.LANCZOS)
    flaeche.paste(wm, ((1200 - breite) // 2, (630 - wm.height) // 2), wm)
    flaeche.save(BILDER / "og-logo-1200x630.jpg", "JPEG", quality=88, optimize=True)

    quadrat = Image.new("RGB", (512, 512), SCHWARZ)
    wm2 = wortmarke_bild.resize((440, round(360 * 440 / 840)), Image.LANCZOS)
    quadrat.paste(wm2, ((512 - 440) // 2, (512 - wm2.height) // 2), wm2)
    quadrat.save(BILDER / "logo-luviq-512.png", optimize=True)


if __name__ == "__main__":
    ZIEL_LUVIQ.mkdir(parents=True, exist_ok=True)
    ZIEL_MARKE.mkdir(parents=True, exist_ok=True)
    MARKE_FARBE = marken_farbe()
    print("Markenfarbe gemessen: #%02X%02X%02X" % MARKE_FARBE, "| AVIF:", AVIF)
    hero()
    og_start()
    wm = wortmarke(MARKE_FARBE)
    icons()
    og_logo(wm)
    print("fertig")
