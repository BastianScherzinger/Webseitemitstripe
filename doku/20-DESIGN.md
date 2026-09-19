---
bereich: design
titel: Design und Gestaltungslinie
stand: 2026-09-19
status: teilweise
fortschritt: 77
zusammenfassung: 19.09.2026 gebaut: „Nachtausgabe" – luviq.css (Tokens, ein Akzent #C8763F), Cormorant/Schibsted/JetBrains selbst gehostet, Radius 0, keine Schatten/Glas/Animationen außer dem Laufband; alte Seiten über die Schicht .lv-alt. Bericht docs/design-2026-09-BERICHT.md.
offen: 7
quellen: CLAUDE.md, DOCUMENTATION.md, LOGBUCH.md, shop1/static/shop1/style.css, tailwind.config.js, templates/base.html
---

# Design — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Bereichswert **Barrierefreiheit** des Laufs vom 02.09.2026 (Regelstand `2026-09-02a`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße.*

## Gestaltungslinie seit 19.09.2026: „Nachtausgabe"

Gebaut nach `C:\Users\basti\Desktop\Webagentur Scherzinger\Design\luviq\FINALER-BAUPLAN.md`,
Bericht `docs/design-2026-09-BERICHT.md`. Ein Stylesheet für alle öffentlichen Seiten:
`shop1/static/shop1/luviq.css`.

| Token | Wert | Rolle |
|---|---|---|
| `--lv-grund` / `--lv-grund-2` | `#0A0A0A` / `#131211` | Seitengrund / abgesetzte Flächen |
| `--lv-text` / `--lv-leise` | `#F2EEE6` / `#9C968C` | Text 17,1:1 / Nebentext 6,8:1 |
| `--lv-linie` / `--lv-linie-2` | `rgba(242,238,230,.12)` / `.28` | Linien |
| `--lv-akzent` | `#C8763F` | **einziger** Akzent (Nummern, feine Linien, Hover) – austauschbar, weil Luisa künftig mit Textilfarben malt |
| `--lv-kachel` | `#E8E1D6` | Kachel hinter Freistellern (`mix-blend-mode: multiply`) |

**Schriften, selbst gehostet** (`shop1/static/shop1/fonts/`, OFL daneben, zugeschnitten mit
`tools/schriften_zuschneiden.py`): Cormorant Garamond kursiv 500 (Überschriften, Markensatz,
Zitat) · Schibsted Grotesk 400–700 (Text; 700 gesperrt für „LUVIQ") · JetBrains Mono 400–500
(Nummern, Daten, Uhr). Ersatzschriften mit gerechneten Metriken, Preload nur Cormorant +
Schibsted. Kein Google Fonts mehr (RE07 erledigt).

**Form:** Radius 0, keine Schatten, keine Verläufe, kein Glas, kein Glühen. Einzige Bewegung:
das Laufband (steht bei `prefers-reduced-motion`). Desktop 1:1 zur Vorlage über
`--u: min(1vw, 14.4px)`, unter 1024 px feste Werte aus dem Handy-Rahmen.

**Zwei Seitenarten** (`{% block seitenart %}` in `base.html`): `lv-seite` für neu gebaute
Seiten (Start, Motiv anfragen, Archiv, Stück, Luisa – laden nur `luviq.css`, kein Tailwind, kein
Alpine) und `lv-alt` (Vorgabe) für Seiten mit altem Markup (Konto, Kasse, Gästebuch, Wissen,
Rechtstexte): dort übersetzt eine Schicht in `luviq.css` Glas, Rundungen, Glühen und Knöpfe in
die neue Linie. Das Admin-Panel (`lv-admin`) bleibt, wie es ist.

**Designwache:** `shop1/tests/aufbau_referenz.json` am 19.09.2026 für alle 25 Seiten bewusst
neu erfasst (LOGBUCH).

## Frühere Gestaltungslinie (bis 18.09.2026, nur Geschichte)

**„Dark Brown Edition"** (Kopfkommentar in `style.css`): ein durchgehend dunkler, warmer Grund,
Gold als einziger Akzent, Glasflächen mit Weichzeichner, grosse schwarze Versalien in der
Display-Schrift, dazu ein animierter „Nebel"-Hintergrund und auf dem Desktop ein Partikel-Hero
(Three.js, nur ≥ 640 px und nur ohne `prefers-reduced-motion`). Stimmung: Streetwear-Drop,
nicht Boutique. Die Startseite ist als Bühne gebaut (Hero mit Produktfoto als Hintergrund,
umschaltbarer Produkt-Showcase, Trust-Badges, Ticker — Commits `82f3077`, `67fb4fb`, 03.07.2026).

**Neugestaltung beschlossen (18.09.2026), noch nicht gebaut.** Bastian hat nach drei Runden
Entwürfen **B3 „Nachtausgabe“ mit Hero H4 „Panorama“** gewählt: Schwarz, Cormorant Garamond kursiv,
Schibsted Grotesk gesperrt, ein Foto über die ganze Breite ohne Text darauf, das Archiv mit Nummern.
Entscheidung, Design-Vorgabe (Farben, Schriften, Aufbau) und Bauplan stehen **außerhalb dieses Repos** in
`C:\Users\basti\Desktop\Webagentur Scherzinger\Design\luviq\ENTSCHEIDUNG-UND-BAUPLAN.md`, die Entwürfe
daneben in `entwuerfe\`. **Bis zum Bau** gilt die Linie unten weiter, und die Verbesserungsläufe verändern
kein Element, keine Klasse und keine Kennung. Der Umbau selbst schreibt die Designwache-Referenz bewusst neu.

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
(mit Alpine `x-intersect`). Kontrastwerte sind **nicht vollständig dokumentiert**. Bekannt seit
`BF29` (Messung 16.09.2026, axe-core: `color-contrast` auf allen vier geprüften Seiten, am
17.09.2026 in Paket 219 benannt): zu schwach sind im Rahmen `templates/base.html` die Fusslinks
(`text-white/40`, Zeilen 449–460), die Copyright-Zeile (`text-white/30`, Zeile 465) und der Knopf
„Registrieren" — Weiss auf `glow-orange` `#c8965c` (Zeile 374), rechnerisch rund 2,6:1. Nicht
behoben: jede Lösung ändert eine Farbe dieser Linie und wartet auf die Betreiberin.

**Schriften:** `Inter` 400–700 für Fliesstext, `Outfit` 700/900 für Überschriften (`.heading-font`),
beide von **`fonts.googleapis.com`** (Preconnect + `media="print"` mit `data-schrift-nachladen`
seit SI09 + `noscript`, `base.html` Zeilen 212–215). Das ist der Rechtsbefund RE07 (13 von 13
Seiten, Messung 02.09.2026) und weiter **nicht** behoben: am 12.09.2026 (Paket 183) erneut
angefasst und als nicht möglich beendet — im Projekt ist keine einzige `*.woff2`-Datei
versioniert, und der Lauf hatte keinen Netzzugang, um die Schnitte zu holen. Die Umstellung
bleibt damit offen ([80-AUFGABEN.md](80-AUFGABEN.md) → Offen Nr. 3). Fallback `sans-serif`.

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

**Die Karte zeigt seit dem 18.09.2026 zuerst einen Platzhalter** (`RE17`, `d58a96c`, Zweig
`sofort/2026-09-18-re15-und-2-weitere`, nicht gemergt): über dem Kartenrahmen auf `/` und
`/gaestebuch/` liegt ein Knopf über die volle Fläche — dunkler Grund (`rgba(18,13,10,0.96)`),
darauf „Karte laden" in goldenen Versalien (`#c8965c`, `0.625rem`, weite Laufweite) und darunter
der Hinweis „Beim Laden werden Daten an Google Maps übertragen." in gedämpftem Weiss. Erst der
Klick holt die Karte von Google und entfernt den Knopf. **Aufbau und Referenz bleiben unberührt:**
der Knopf entsteht im Skript am Körperende von `base.html`, nicht in der Vorlage, das
ausgelieferte HTML enthält weiter nur den Rahmen (`aufbau_referenz.json` nicht angefasst). Seine
Gestaltung steht als Inline-Stil im Skript und greift deshalb auf keine Klasse der Linie zurück —
**im Browser hat das niemand angesehen**, und ohne JavaScript bleibt der Rahmen leer.

**Produkte (`/produkte/`, „The Drop"):** Produktkarten mit Bild, Name, „Handbemaltes 1-of-1 Unikat",
„Endpreis" (Zweig; auf main „Vintage Custom Art" / „Investition"). Ein einziger Fliesstextabsatz
in Versalien (`uppercase tracking-[0.4em]`), mit IS19 und zuletzt mit IS18 (11.09.2026, `2591fde`,
Zweig `sofort/2026-09-11-is18`, nicht gemergt) auf den Umfang einer Kategorieseite erweitert —
nur Text, Klassen und Aufbau unverändert. Bei diesem Umfang ist der Absatz in dieser Satzart lang
zu lesen und schiebt das Produktraster nach unten (Nebenbefund in `LOGBUCH.md`, Paket 165; siehe „Offen").

**Die Produktkarte liegt seit dem 12.09.2026 als eigener Baustein** (`VL21`, `5f517de`, Zweig
`sofort/2026-09-12-vl21-und-2-weitere`, nicht gemergt): `shop1/templates/shop1/teile/angebot.html`
für `/produkte/`, `teile/angebot_galerie.html` für den Startseiten-Abschnitt — zwei Dateien, weil
die beiden Karten sich in Ecken, Bildhöhe, `srcset`, Abzeichen und Aufbau des Textteils
unterscheiden. **Am Aussehen ändert das nichts:** das gerenderte HTML ist wörtlich dasselbe wie
vorher, `test_aufbau` bleibt ohne Änderung der Referenz grün, keine neue Klasse, kein
Tailwind-Neubau. Wer künftig am Aussehen einer Produktkarte etwas ändern will, ändert diese
Bausteine — und damit bewusst die Designwache-Referenz.

**Produktdetail:** Galerie, Preis, Warenkorb-Knopf, „Spezifikationen"-Absatz (Zweig: statischer
Zusatz zu 1-of-1, Zahlung, Versand), `Product`/`Offer`/`Brand` + `BreadcrumbList` im JSON-LD.

**Kontakt, Über uns, Liefergebiet, Gästebuch, Wissen (Zweig):** Glas-Karten auf dem Nebel-Grund,
`h1` mit Kicker in Versalien, Formulare mit `.form-input`. Impressum/Datenschutz/AGB als
Textseiten mit Emoji-Ikonen (📍 📧 ⚖️ 🌍).

**Danke-Seite (`/kontakt/danke/`, `2d78a55`, seit dem Merge `c522ff9` auf `main`):** neue Seite nach dem Aufbau von `payment_success.html` — Nebel, Glaskarte,
Symbolkreis mit einem Häkchen als Inline-SVG statt Emoji, Versalien-Überschrift „Danke für deine
Nachricht", zwei Knöpfe (Zur Startseite, Unikate ansehen). Laut `LOGBUCH.md` (Paket 171) nur
Klassen, die in der gebauten `tailwind.css` schon stehen. Keine bestehende Seite verändert;
`aufbau_referenz.json` gezielt um die neue Seite ergänzt (nur Zeilen hinzu, keine entfernt).

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
| **Meldungen werden angesagt** (`BF24`): jede Meldungskarte im Rahmen trägt `role="alert"` bei Fehlern und `role="status"` sonst; das Formular auf `/kontakt/` trägt `aria-live="polite"`. Nur Attribute — Karte, Farben, Klassen und Aufbau unverändert, `aufbau_referenz.json` nicht angefasst | Formularfehler erreichen auch, wer sie nicht sieht (WCAG 3.3.1); zwei Tests in `test_barrierefreiheit` (`FehleransageTest`), im Bildschirmleser ungeprüft | `a8190b8` (Zweig `sofort/2026-09-17-pj05-und-2-weitere`, 17.09.2026, seit `f489e76` auf `main`) |
| **Die Fehlermeldung des Kontaktformulars steht im Formular** (`BF24`, Nachbesserung): `<div id="kontakt-fehler" role="alert">` als erstes Kind des `<form>`, mit den vorhandenen Klassen (`glass rounded-2xl p-4 border-l-4 border-red-500 …`); die vier Pflichtfelder verweisen mit `aria-describedby` darauf. **Der Block wird nur im Fehlerfall gerendert** (`{% if fehler %}`) — ein dauerhaft leerer Meldungsbereich wäre ein Element und eine Kennung mehr im sichtbaren Aufbau, und den friert die Designwache ein. Das Aussehen der Seite im Normalfall ist unverändert, `aufbau_referenz.json` nicht angefasst. **Kein Tailwind-Neubau nötig:** `rounded-2xl`, `p-4`, `border-l-4`, `border-red-500`, `text-white/90`, `text-sm` und `font-medium` stehen schon im gebauten `shop1/static/shop1/tailwind.css`, `.glass` in `style.css` (geprüft 17.09.2026) | Im Meldungsbereich ganz oben stand die Meldung ausserhalb des Formulars und gehörte zu keinem Feld; jetzt wird sie mit dem Feld vorgelesen. Drei Tests in `test_barrierefreiheit` (`FehleransageTest`): Wortlaut samt `id` und `role`, Lage innerhalb des `<form>`, `aria-describedby` an jedem Pflichtfeld. Im Bildschirmleser ungeprüft | `8014429` (Zweig `sofort/2026-09-17-bf24-und-2-weitere`, 17.09.2026, seit dem Merge `911c26a` auf `main`) |
| **Der Datenschutzhinweis im Kontaktformular steht als reiner Fliesstext** (`KV05`): kein `<p>`, kein `<a>`, keine eigene Klasse — der Text hängt direkt im `<div>` unter dem Nachrichtenfeld, die Adresse der Datenschutzerklärung ist ausgeschrieben statt verlinkt. Ein Absatz mit Verweis wären zwei Elemente mehr im sichtbaren Aufbau, und den friert die Designwache ein; verlinkt bleibt die Erklärung in der Fusszeile jeder Seite. **Folge fürs Aussehen:** ohne eigene Klasse erbt der Hinweis Schriftgrösse und Farbe des Formularrahmens statt der kleinen, gedämpften Schrift der übrigen Formulartexte — **im Browser nicht angesehen**. Eine Klasse nachzutragen wäre eine Änderung am eingefrorenen Aufbau und braucht eine bewusste Entscheidung. Das Fallenfeld des Spamschutzes (`KV06`) bleibt unsichtbar: `aria-hidden` und `style` sind Attribute, die die Designwache nicht erfasst | Art. 13 DSGVO verlangt den Hinweis dort, wo die Daten eingegeben werden; ein Test in `test_formulare` hält ihn zwischen `<form>` und `</form>` fest. `aufbau_referenz.json` nicht angefasst, `test_aufbau` unverändert | `b736994`, `06503a7` (Zweig `sofort/2026-09-17-kv05-und-2-weitere`, 17.09.2026, nicht gemergt) |
| **Der Kartenplatzhalter wird im Skript gebaut, nicht in der Vorlage** (`RE17`): die Vorlage liefert den Rahmen ohne `src`, das Skript in `base.html` legt den Knopf darüber und setzt `src` erst im Klick. Ein Platzhalter in der Vorlage wäre ein Element und eine Klasse mehr im sichtbaren Aufbau — den friert die Designwache ein. **Folge fürs Aussehen:** der Knopf trägt Inline-Stile statt Klassen der Linie, und ohne JavaScript bleibt der Rahmen leer; beides ist im Browser nicht angesehen | Vor dem Klick geht keine Anfrage an `maps.google.com`, also auch keine IP-Adresse (`RE17`, `RE15`); drei Tests in `test_einstellungen` (`EinbettungErstNachKlickTest`), `aufbau_referenz.json` nicht angefasst | `d58a96c` (Zweig `sofort/2026-09-18-re15-und-2-weitere`, 18.09.2026, nicht gemergt) |
| **Der Bestellknopf heisst „Zahlungspflichtig bestellen"** (`RE21`) statt „Continue to Payment →" — nur der Text von `checkout.html:114`, keine Klasse, keine Kennung, kein Element | § 312j Abs. 3 BGB verlangt die eindeutige Beschriftung, und die AGB nannten sie längst (`legal/agb.html:42`); die Seite widersprach sich selbst. Auf `/payment/` beschriftet PayPals SDK seinen Knopf selbst | `329dbc4` (derselbe Zweig, 18.09.2026, nicht gemergt) |
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
| Kontrast im Seitenrahmen: Fusslinks (`text-white/40`), Copyright-Zeile (`text-white/30`), „Registrieren" weiss auf Gold. Am 17.09.2026 (Paket 219) als nicht möglich beendet, keine Zeile geändert — braucht eine Farbentscheidung der Betreiberin ([80-AUFGABEN.md](80-AUFGABEN.md), „Beim Kunden" Nr. 18), danach Tailwind neu bauen | Messung 16.09.2026: 4 von 4 Seiten mit `color-contrast` | BF29 |
| `prefers-reduced-motion` auch für die CSS-Animationen (`nebula-evolve`, `rotate`, Ticker) — im ausgelieferten Stilblatt nicht gefunden; nur der Three.js-Pfad prüft es | BF19 | BF19 |
| Darstellung des Datenschutzhinweises auf `/kontakt/` im Browser ansehen (Paket 243, `KV05`): Er trägt keine eigene Klasse und erbt Schriftgrösse und Farbe des Formularrahmens. Passt das nicht zum Rest des Formulars, ist eine Klasse eine Änderung am eingefrorenen Aufbau und braucht eine bewusste Entscheidung samt Nachziehen von `aufbau_referenz.json` | im Zweig gebaut, nie angesehen | KV05 |
| Den Kartenplatzhalter auf `/` und `/gaestebuch/` im Browser ansehen (Paket 248, `RE17`): dunkler Kasten mit „Karte laden" über der ganzen Kartenfläche, Gestaltung aus Inline-Stilen statt aus Klassen der Linie. Passt er nicht zu den Glas-Karten daneben, ist eine Klasse eine Änderung am eingefrorenen Aufbau und braucht eine bewusste Entscheidung samt Nachziehen von `aufbau_referenz.json`. Dabei auch ohne JavaScript ansehen — dann bleibt der Rahmen leer | im Zweig gebaut, nie angesehen | RE17 |
| Englische Restbeschriftungen ohne Aussage („Get in Touch", „Zentrale/Channels", „Legal Notice", „Art is not a luxury…", „JOIN THE") — Geschmacksfrage der Betreiberin, nicht der Messung; „Continue to Payment →" ist mit `RE21` (18.09.2026) durch „Zahlungspflichtig bestellen" ersetzt | — | — |
| Menüknopf und Icon-Knöpfe ohne Namen (13 Seiten × 1); 5 namenlose Links auf `/produkte/` | BF12, BF11 | BF12, VL18 |
| Satzart des Einleitungsabsatzes auf `/produkte/`: Versalien mit weiter Laufweite bei einem Absatz im Umfang einer Kategorieseite (seit IS18, `2591fde`). Eine andere Satzart ist eine Änderung am Aussehen — eigenes Paket, Freigabe, Designwache-Referenz bewusst nachziehen | Nebenbefund `LOGBUCH.md`, Paket 165 (keine Messung) | — |
