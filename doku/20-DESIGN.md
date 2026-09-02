---
bereich: design
titel: Design und Gestaltungslinie
stand: 2026-09-02
status: vollständig
fortschritt: 90
zusammenfassung: Dunkelbraun-Gold-Linie mit Glas-Karten steht und ist durch die Designwache eingefroren; offen sind Google-Schriften von fremdem Server und englische Restbeschriftungen.
offen: 4
quellen: CLAUDE.md, DOCUMENTATION.md, LOGBUCH.md, shop1/static/shop1/style.css, tailwind.config.js, templates/base.html
---

# Design — Luviq Universe

## Gestaltungslinie

**„Dark Brown Edition"** (Kopfkommentar in `style.css`): ein durchgehend dunkler, warmer Grund,
Gold als einziger Akzent, Glasflächen mit Weichzeichner, grosse schwarze Versalien in der
Display-Schrift, dazu ein animierter „Nebel"-Hintergrund und auf dem Desktop ein Partikel-Hero
(Three.js, nur ≥ 640 px und nur ohne `prefers-reduced-motion`). Stimmung: Streetwear-Drop,
nicht Boutique. Die Startseite ist als Bühne gebaut (Hero mit Produktfoto als Hintergrund,
umschaltbarer Produkt-Showcase, Trust-Badges, Ticker — Commits `82f3077`, `67fb4fb`, 03.07.2026).

**Keine Neugestaltung geplant.** Die Verbesserungsläufe 3 und 4 haben ausdrücklich **kein
Element, keine Klasse, keine Kennung** verändert — jeder Schritt im Logbuch belegt das gegen die
Designwache. Wer am Aussehen etwas ändert, ändert bewusst die Referenz.

## Farben und Schriften

Tokens aus `style.css` (`:root`) und `tailwind.config.js` (`theme.extend.colors`), identische Werte:

| Rolle | Token (CSS) | Tailwind-Name | Wert |
|---|---|---|---|
| Grund | `--bg-base` | `space-black` | `#0d0907` |
| Grund 2 | `--bg-secondary` | `space-dark` | `#160d06` |
| Akzent Gold | `--accent-gold` (Alias `--accent-orange`) | `glow-orange` | `#c8965c` |
| Akzent warm | `--accent-warm` (Alias `--accent-amber`) | `glow-amber` | `#a0714a` |
| Text | `--text-main` | `soft-light` / `space-text` | `#f5ede4` |
| Glas | `--glass` | — | `rgba(20,12,6,0.72)`, Rand `rgba(200,150,92,0.15)` |
| Leuchten | `--glow-gold`, `--glow-gold-intense` | — | Gold-Schatten 20 px / 44 px |
| `theme-color` | — | — | `#0d0907` (`base.html`) |

Bauteile: `.glass` (Blur 20 px), `.glass-card` (Verlauf + mehrschichtiger Schatten),
`.energy-nebula` (fixer Hintergrund, 30-s-Animation), `.btn-glow`, `.text-glow`, `.scroll-reveal`
(mit Alpine `x-intersect`). Kontrastwerte sind **nicht dokumentiert** — nirgends gerechnet.

**Schriften:** `Inter` 400–700 für Fliesstext, `Outfit` 700/900 für Überschriften (`.heading-font`),
beide von **`fonts.googleapis.com`** (Preconnect + `media="print" onload` + `noscript`,
`base.html` Zeilen 172–175). Das ist der Rechtsbefund RE07 (13 von 13 Seiten, Messung
02.09.2026) und im Zweig **nicht** behoben. Fallback `sans-serif`.

## Seitenaufbau

**Rahmen (`templates/base.html`):** klebrige Glas-Navigation (`Home · Produkte · Gästebuch ·
Kontakt · Über uns · Login · Registrieren`, mobil per Alpine-Menü), Fusszeile mit zwei Linkgruppen
(`Produkte · Kontakt · Über uns · Liefergebiet` / `Datenschutz · Impressum · AGB`), zusätzlich eine
**mobile Bottom-Navigation** (`aria-label="Mobile Navigation"`). Kein Link auf `/wissen/` (Plan
des Laufs 4, bewusst verworfen). Keine Telefonnummer im Rahmen — es gibt keine belegte Nummer.

**Startseite (`index.html`, acht Abschnitte):** Hero (`#hero-section`, 100 svh, GSAP-Einflug der
Wortmarke, Antwortabsatz `#hero-sub`) → drei Feature-Karten (`Hand-Painted · Eco-Conscious ·
Curated Style`) → Herkunft und Versandgebiet → Markenblock → Trust-/Ticker-Leiste → Community
(`#community`, Gästebuch-Auszug + Google-Karte aus `_reviews_map.html`) → „Aktuelle Drops"
(Produktkarten, `ItemList`) → Newsletter („JOIN THE …").

**Produkte (`/produkte/`, „The Drop"):** Produktkarten mit Bild, Name, „Handbemaltes 1-of-1 Unikat",
„Endpreis" (Zweig; auf main „Vintage Custom Art" / „Investition"). Ein einziger Fliesstextabsatz
in Versalien (`tracking-[0.4em]`), im Zweig auf rund 100 Wörter erweitert.

**Produktdetail:** Galerie, Preis, Warenkorb-Knopf, „Spezifikationen"-Absatz (Zweig: statischer
Zusatz zu 1-of-1, Zahlung, Versand), `Product`/`Offer`/`Brand` + `BreadcrumbList` im JSON-LD.

**Kontakt, Über uns, Liefergebiet, Gästebuch, Wissen (Zweig):** Glas-Karten auf dem Nebel-Grund,
`h1` mit Kicker in Versalien, Formulare mit `.form-input`. Impressum/Datenschutz/AGB als
Textseiten mit Emoji-Ikonen (📍 📧 ⚖️ 🌍).

**Bilder:** Logo `logo-luviq` (Zweig: WebP 96/192 + `flavicon.ico`), Hero `hero-dragon`
(Zweig: WebP 640/1024/1536 mit `srcset`/`sizes`/Preload), Porträt `ich` (Zweig: WebP 450/900);
Produktbilder von Cloudinary (JPEG/PNG, ohne `srcset` — PF15/PF16). Bildsumme Startseite im Zweig
498,6 KB → 175,3 KB (Logbuch Schritt 32).

## Entscheidungen

| Entscheidung | Warum | Beleg |
|---|---|---|
| **Designwache** `test_aufbau` friert den sichtbaren Aufbau jeder öffentlichen Seite ein (Tag-Reihenfolge, `id`/`class`, Überschriften, Elementzahlen); `<head>`, `alt`, `aria-*`, `src`, `srcset` bewusst ausgenommen | Verbesserungsläufe dürfen Text, Meta und Schema ändern, nicht das Aussehen; blockiert seit Auflage 4 (`47769d4`) auch bei null verglichenen Seiten | `CLAUDE.md`, `shop1/tests/_aufbau.py` |
| Neuer Inhalt wächst in **vorhandenen** Absätzen; keine neuen Elemente | Regel 1 der Läufe; `/produkte/` hatte ausser `h1` und Karten nur einen Absatz | Logbuch Schritte 21–24 |
| Kein Link auf `/wissen/` in Navigation oder Fusszeile | verworfen (Plan Lauf 4, Zeile 7); Wissensseiten sind über die Übersicht und untereinander verlinkt | Logbuch Schritt 26 |
| Three.js nur Desktop, ohne reduzierte Bewegung, nachgeladen; `setPixelRatio ≤ 1,5`, `antialias: false` | LCP/TBT mobil | `DOCUMENTATION.md` §8, `index.html` |
| Fokusring per `body :is(...)` (Spezifität 0,2,1), damit er `.form-input:focus` und `focus:outline-none` schlägt | Tastaturfokus war unsichtbar | Schritt 9 (`508d0ec`); Sichtprüfung im Browser durch die Betreiberin steht aus (Auflage 2) |
| Karussell: benannte Schaltflächengruppe mit `aria-pressed` statt halbem ARIA-Tabmuster | Barrierefreiheit | Schritt 7 (`5eb59b9`) |
| Platzhalter-Kontaktdaten auf `/kontakt/` („Musterstraße 123, Berlin", „+49 (0) 30 123456", `info@luviq.universe`) durch belegte Angaben ersetzt, **Telefon entfernt statt erfunden** | keine belegte Nummer im Projekt | Zweig `kontakt.html`; live (main) stehen die Platzhalter noch |
| „5.0 ★★★★★" im Bewertungskasten nicht angefasst | Quelle der Zahl nicht belegt | Logbuch Schritt 23 |

**Was am Aussehen nicht angefasst wird:** Farbtokens, Glas-Bauteile, Nebel-Hintergrund, der
GSAP-Hero, die Abschnittsreihenfolge der Startseite, die Emoji-Ikonen der Rechtsseiten — alles
in `aufbau_referenz.json` festgeschrieben. Änderungen an Warenkorb-, Checkout- und
Zahlungsvorlagen (`warenkorb.html`, `checkout.html`, `payment.html`, `payment_success.html`)
zusätzlich nur mit Sandbox-Test ([10-TECHNIK.md](10-TECHNIK.md) → Fallen).

## Offen

| Punkt | Beleg (Messung 02.09.2026) | Regel |
|---|---|---|
| Inter und Outfit als WOFF2 selbst hosten, `@font-face` mit `font-display: swap` | 13 von 13 Seiten laden von `fonts.googleapis.com` | RE07, VL16 |
| Sprungmarke „Zum Inhalt" als erstes Element im `body` | 13 von 13 ohne | BF08, VL17 |
| `prefers-reduced-motion` auch für die CSS-Animationen (`nebula-evolve`, `rotate`, Ticker) — im ausgelieferten Stilblatt nicht gefunden; nur der Three.js-Pfad prüft es | BF19 | BF19 |
| Englische Restbeschriftungen ohne Aussage („Get in Touch", „Zentrale/Channels", „Legal Notice", „Art is not a luxury…", „JOIN THE") — Geschmacksfrage der Betreiberin, nicht der Messung | — | — |
| Menüknopf und Icon-Knöpfe ohne Namen (13 Seiten × 1); 5 namenlose Links auf `/produkte/` | BF12, BF11 | BF12, VL18 |
