---
bereich: performance
titel: Performance und Core Web Vitals
stand: 2026-10-02
status: teilweise
fortschritt: 99
zusammenfassung: Stand 02.10.2026 (lokal, nicht gepusht): Produktbilder in mehreren Größen mit srcset, LCP-Bild mit fetchpriority und Vorladen, Bildmaße (Migration 0027), vier Schriftdateien, Critical CSS, Alpine.js entfernt. Stand 01.10.2026: PageSpeed mobil 95–99, Desktop 100, Serverzeit 1,6 ms, CLS 0,00–0,05 (Messblock vom 01.10.2026); WebP, GZip, Cache, gthread und die Cloudinary-.webp-Endung sind in main und live. Offen sind Bildgrößen und -attribute, sechs statt vier Schriftdateien und die Fremdskripte (Alpine, Chart.js).
offen: 3
pagespeed_mobil: 98
pagespeed_desktop: 100
antwortzeit_ms: 2
quellen: DOCUMENTATION.md, LOGBUCH.md, start.sh
antwortzeit_quelle: PageSpeed server-response-time
---

# Performance — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Tempo-Wert des **letzten** Laufs (PageSpeed mobil doppelt, Desktop einfach gewichtet), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße. Die Zahl selbst steht im erzeugten Block unter „Messwerte“, nicht in diesem Satz.*
Gemessen wird die **Live-Seite**, also der Stand `main` — seit dem 01.10.2026 ist das derselbe Stand wie der lokale Ordner (alle Arbeitszweige gemergt, `main` = `36c0741`). Was früher unter „im Zweig, noch nicht live“ stand (Verbesserungslauf 4, Paket 267), ist seit den Merges live und unten unter „Umgesetzt“ geführt.

Gemessen wird die **Live-Seite**, also der Stand `main`. Der Verbesserungslauf 4 (Zweig) ist
**nicht** enthalten — seine Tempomassnahmen sind unten unter „Umgesetzt (im Zweig)" aufgeführt
und live noch nicht wirksam.

## Messwerte

<!-- tempo:anfang -->
**Messung vom 02.10.2026** (Webagentur Scherzinger Overview, Regelstand 2026-10-02d). Bereich „Performance & Core Web Vitals“: **100,0 von 100**, Reifegrad „Referenz“.

### Lighthouse je Seite

| Seite | Gerät | Leistung | LCP | CLS | TBT | Serverzeit |
|---|---|---:|---:|---:|---:|---:|
| `/` | mobile | **93** | 3,15 s | 0,000 | 0 ms | 4 ms |
| `/` | desktop | **100** | 0,65 s | 0,043 | 0 ms | 4 ms |
| `/datenschutz/` | mobile | **100** | 1,35 s | 0,000 | 0 ms | 2 ms |
| `/datenschutz/` | desktop | **100** | 0,32 s | 0,001 | 0 ms | 1 ms |
| `/impressum/` | mobile | **98** | 1,96 s | 0,000 | 0 ms | 2 ms |
| `/impressum/` | desktop | **100** | 0,32 s | 0,001 | 0 ms | 1 ms |
| `/kontakt/` | mobile | **100** | 1,65 s | 0,000 | 0 ms | 2 ms |
| `/kontakt/` | desktop | **100** | 0,38 s | 0,001 | 0 ms | 2 ms |
| `/produkte/` | mobile | **99** | 2,04 s | 0,000 | 0 ms | 3 ms |
| `/produkte/` | desktop | **100** | 0,48 s | 0,051 | 0 ms | 2 ms |

10 Abrufe, davon 0 wiederholt und **0 endgültig ohne Ergebnis**. Ein Abruf ohne Ergebnis steht oben als „nicht gemessen“ — bei CLS und TBT wäre eine Null der Bestwert und damit ein Lob für etwas, das niemand gemessen hat.

**Serverzeit (`server-response-time` aus PageSpeed): 2,3 ms** im Mittel. Das ist die Zahl, an der `PF09` und `PF10` hängen. Die Sekundenwerte, die der eigene Prüfstand je Seite notiert, sind Wanduhrzeiten bei sechs gleichzeitigen Abrufen samt Kaltstart — sie messen den Prüfstand, nicht den Server.

### Tempo-Regeln, die offen sind

Keine. Alle messbaren Tempo-Regeln sind bestanden.

### Die grössten Bremsen laut Lighthouse

Keine Einsparchance über 150 ms.
<!-- tempo:ende -->

**Was hier erzeugt wird und was von Hand kommt.** Jede gemessene Zahl steht im Block
darüber; geschrieben hat ihn das Werkzeug („Messung nachziehen"). Von Hand steht hier nur,
was keine Messung hergibt. Bis zum 04.09.2026 stand an dieser Stelle eine PageSpeed-Tabelle
aus `2026-09-02a` — richtig beim Schreiben, zwei Katalogstände später falsch (CLAUDE.md §14).

**Die drei Deutungen, die keine Messung ersetzt:**
- **Die Startseite ist die langsamste geprüfte Seite** (mobil 95, LCP 2,87 s; alle übrigen mobil 99, LCP um 2,1 s — Messung 01.10.2026). Nach dem Umbau vom 19.09.2026 entscheidet das Panoramafoto den LCP; `/produkte/` ist kein Ausreißer mehr (mobil 99).
- **`/produkte/` ist der Ausreisser** — die Produktbilder kommen von Cloudinary ohne
  `srcset`, ohne modernes Format und ohne Preload auf dieser Seite. Das ist die eine Stelle,
  an der der LCP der Seite entschieden wird.
- **CLS ist überall null**, Best Practices durchgehend 100. Feldwerte (CrUX) gibt es nicht:
  `PF06` (INP), `PF07` (LCP) und `PF08` (CLS) sind **nicht messbar** — zu wenig Verkehr.
- Der **SEO-Wert auf `/impressum/`** liegt tief, weil die Seite `noindex` trägt. Kein Befund.

**Die „mittlere Antwortzeit über 14 Seiten" war kein offener Punkt, sondern eine Eigenschaft
der Messung.** Der eigene Prüfstand ruft die Seiten gleichzeitig ab und misst die Wanduhr,
Kaltstart inbegriffen; PageSpeed meldete für dieselben Adressen im selben Lauf einstellige
Millisekunden Serverzeit. `PF09` bis `PF12` nehmen seit `2026-09-04a` die PageSpeed-Zahl und
sind bestanden; seit `2026-09-05a` schreibt das Werkzeug auch `antwortzeit_ms` im Kopf aus
derselben Quelle. **Was im Code trotzdem bleibt und unabhängig davon zu tun ist:** die
Besuchs-Middleware schreibt `PageVisit` und `VisitorLog` **synchron im Request** (zwei
Datenbanken), und Gunicorn läuft mit 2 Workern × 4 Threads (`start.sh`, Vorgabe).
Datenbanken), und auf `main` läuft Gunicorn mit nur zwei gleichzeitigen Anfragen für den
ganzen Shop.

**Verfügbarkeit** (Monitor des Werkzeugs, 02.09.2026): 100 % über 24 Stunden bei 1.670
Messungen, 99,92 % über 7 Tage bei 3.935 Messungen.

### Bilder
Die meisten noch offenen Tempo-Regeln betreffen Bilder (Messblock oben, 01.10.2026): `PF16` 11 von 21 Bildern mit `srcset`, `PF17`/`PF18`/`PF19` Lazy-Loading, `fetchpriority` und Preload des LCP-Bildes, `PF23` ein Bild über 300 kB (`IMG_4376_fupstq.webp`, 389 kB), `PF24` übergroß geladene Bilder (600 statt 221 px), `PF25` fünf Bilder ohne feste Maße. Das Format ist seit Paket 267 erledigt: der Filter `cloud` setzt `.webp` (`PF15`).

Der grösste Tempohebel der Seite, und der einzige Bereich, in dem alle Regeln zugleich offen
sind — die Zahlen dazu stehen im Block oben:

| Regel | Was offen ist |
|---|---|
| PF15 modernes Format | Die Produktbilder kamen dank `f_auto` schon als WebP/AVIF, ihre Adresse endete aber auf `.jpg`/`.png` — die Messung liest das Format an der Endung. **Zweig Paket 267 (`1737e74`):** der Filter `cloud` setzt die Endung auf `.webp`; live wirkt das erst nach Merge und Deploy, nachgemessen ist es nicht |
| PF16 mehrere Grössen | kein einziges Bild mit `srcset` |
| PF18 `fetchpriority=high` | fehlt am ersten Bild im `<main>` |
| PF19 LCP-Preload | fehlt auf `/produkte/` und `/kontakt/` |
| VL15 Bilder nach Vorlage | kein WebP/AVIF, ein Teil ohne `width`/`height`, ein Teil weder lazy noch als LCP ausgezeichnet |

## Umgesetzt

**Live (main), belegt in `DOCUMENTATION.md` §8:**

- `ManifestStaticFilesStorage` mit Content-Hash und WhiteNoise (Kompression und Caching statischer Dateien)
- Produktbilder über das Cloudinary-CDN
- `loading="lazy" decoding="async"` an Bildern unter der Falz; erstes Produktbild `loading="eager" fetchpriority="high"`
- `defer` an den externen Skripten; Three.js nur Desktop (≥ 640 px), nicht bei `prefers-reduced-motion`, `setPixelRatio ≤ 1,5`, `antialias: false`
- Werbeliste 60 s im `LocMemCache`; `select_related`/`prefetch_related` in allen Listen-Views; Bulk-Fetch in den Checkout-Mails
- Juli 2026: eigener Durchgang „Startseite PageSpeed & Politur" (`2fe90a0`, 15.07.2026)
- Keine Admin-Mail mehr pro Seitenbesuch (`e58775a`, 13.07.2026) — vorher eine Brevo-Mail je Aufruf
**Verbesserungslauf 4 (`cockpit/2026-09-01-verbesserung-4`), seit dem Merge in `main` live:**

**Im Zweig `cockpit/2026-09-01-verbesserung-4`, noch nicht live:**

| Schritt | Massnahme | Beleg |
|---|---|---|
| 31 | Nicht eingebundenes Hintergrundbild (336 KB) entfernt | `64055fe` |
| 32 | Statische Bilder als WebP in mehreren Breiten (hero-dragon 640/1024/1536, ich 450/900, logo 96/192), Favicon als ICO; `src`/`srcset`/`sizes` und Preload umgestellt — **Bildsumme der Startseite 498,6 KB → 175,3 KB** | `fcd034d` |
| 33 (1/4) | `GZipMiddleware` nach WhiteNoise für dynamische Antworten (HTML, sitemap.xml, llms.txt) | `35276fd` |
| 33 (2/4) | `cache_page` 15 min auf `sitemap.xml` und `llms.txt`; zweiter Abruf mit null Datenbankabfragen | `9045654` |
| 33 (3/4) | `CACHES` ausdrücklich als `LocMemCache` (`LOCATION luviq`, `MAX_ENTRIES 300`) | `641c908` |
| 33 (4/4) | Warenkorb-Zähler mit einer `aggregate(Sum(...))`-Abfrage statt Laden plus Summieren | `f81685d` |
| 34 | Geo-IP-Abfrage in festem `ThreadPoolExecutor` (4 Plätze) statt Thread je Aufruf; Abschalter `VISITOR_TRACKING` | `0a9fe98` |
| 35 | Gunicorn `gthread`, 2 × 4 Threads, Timeout 30 s statt 120 s, Worker-Erneuerung nach 1.000 Anfragen (+ Jitter), kein `--preload` | `b0fba20` |
| — | Testmodul `test_ladezeit` (9 Tests) hält die Bildattribute und Kopfangaben fest | Zweig |
**Paket 267 (18.09.2026, Zweig `sofort/2026-09-18-kv11-und-2-weitere`, seit dem Merge `42008d9` in `main`):**

**Im Zweig `sofort/2026-09-18-kv11-und-2-weitere` (Paket 267, 18.09.2026), noch nicht gemergt, nicht live:**

| Regel | Massnahme | Beleg |
|---|---|---|
| `PF15` (anders eingebaut) | Der Filter `cloud` (`shop1/templatetags/custom_tags.py`) setzt die Endung jeder Cloudinary-Adresse auf `.webp`; `.webp`/`.avif` bleiben, fremde und lokale Adressen bleiben unverändert. Mit `f_auto` entscheidet die Endung laut Cloudinary-Doku nur, was ein Browser ohne modernes Format bekommt — AVIF-fähige Browser bekommen weiter AVIF, der Rückfall ist WebP statt JPEG/PNG. **Anders als der Rat** (`<picture>` mit altem Format als Rückfall): das wären zwei Elemente mehr je Produktbild, die Designwache liesse es nicht durch. Tests: `BildformatTest` in `test_ladezeit` (sechs Adressformen und die ausgelieferte Startseite) | `1737e74` |
| `PF26` (anders eingebaut) | `start.sh` packt die statischen Dateien nach `collectstatic` mit `python -m whitenoise.compress` (gzip). Vorher gingen `tailwind.css` und `style.css`, auf die der erste Inhalt wartet, ungepackt raus, weil `ManifestStaticFilesStorage` keine `.gz` anlegt und WhiteNoise nicht selbst packt. Gepackt sind beide laut Test kleiner als ein Drittel. **Anders als der Rat** (kritisches CSS einbetten): das hiesse Regeln aus den Stildateien in jede Seite zu verschieben, und die Stildateien stehen unter der Designwache des Tors. Tests: `StildateienGepacktTest` in `test_ladezeit`. **Nicht belegt:** ob der erste Inhalt mobil damit unter 1,8 s fällt — das zeigt erst die Messung nach dem Deploy | `5515bf3` |

## Offen

**Stand 02.10.2026 (Sammelzweig `fix/2026-10-02-luviq-fertig`, lokal geprüft, nicht gepusht):** erledigt und aus der Liste unten entfernt sind `srcset` für Produktbilder, LCP-Bild mit `fetchpriority` und Vorladen, vier Schriftdateien und Alpine.js (entfernt, `3540c1a`) — Pakete L2-B1/L2-B2 (`9402995`). Die lokale Messung zeigt PF15/PF24/PF25/VL15 nur, weil lokal JPGs aus `media/` statt Cloudinary ausgeliefert werden; live erst nach dem Deploy nachmessen. Die zweite, ältere Tabelle weiter unten ist Verlauf.
Was zu tun ist. Wie weit die genannten Regeln gerade sind und mit welchem Beleg, steht im erzeugten Block unter „Messwerte“ — hier steht keine Messzahl. Stand 01.10.2026; erledigt und entfernt sind die Merge-Aufgaben (Verbesserungslauf 4 und Paket 267 sind live).

Was zu tun ist. Wie weit die genannten Regeln gerade sind und mit welchem Beleg, steht im
erzeugten Block unter „Messwerte" — hier steht keine Messzahl.

| Punkt | Regel |
| Das eine Bild über 300 kB verkleinern (`IMG_4376_fupstq.webp`) (`width`/`height` sind seit 02.10.2026 gesetzt, Migration 0027 und Befehl `bildmasse_nachtragen`) | PF23, PF25 |
| `PageVisit`/`VisitorLog`-Schreibvorgänge aus dem Request nehmen — sie laufen synchron gegen zwei Datenbanken; nicht wegen `PF10`, sondern weil sie bei Last Antwortzeit kosten | — |
| ~~Critical CSS je Seitentyp inline~~ — seit 02.10.2026 gebaut: `tools/kritisches_css.py` erzeugt es aus `luviq.css`; nach jeder Änderung an `luviq.css` neu laufen lassen | PF26 |
| Nach einer Änderung der Seitenart oder des Verkaufsschalters nachmessen: mit Verkauf kommen Warenkorb und Kasse als neue Seiten hinzu | — |
|---|---|
| Zweig nach `main` — WebP, GZip, Cache, gthread und die kleinere Startseite wirken erst dann | PF15, PF16 |
| Produktbilder aus Cloudinary mit `srcset` ausliefern (Cloudinary kann das über Transformationsparameter). Das Format ist mit Paket 267 im Zweig angegangen (Endung `.webp`, siehe „Umgesetzt"); nach Merge und Deploy nachmessen, ob `PF15` die Bilder als modern zählt. **`/produkte/` ist der teuerste LCP der Seite** | PF15, PF16, VL15 |
| Paket 267 mergen und nach dem Deploy nachmessen: den ersten Inhalt mobil (`PF26`) und die Bildformate (`PF15`); dazu im Browser prüfen, dass `tailwind.css` und `style.css` mit `Content-Encoding: gzip` ankommen | PF15, PF26 |
| LCP-Bild je Schlüsselseite vorladen und mit `fetchpriority="high"` auszeichnen; das Logo ist heute überall das erste Bild | PF18, PF19 |
| `PageVisit`/`VisitorLog`-Schreibvorgänge aus dem Request nehmen — sie laufen synchron gegen zwei Datenbanken. **Nicht wegen `PF10`** (das misst seit `2026-09-04a` die Serverzeit aus PageSpeed und ist bestanden), sondern weil eine Schreiboperation im Request unter Last der erste Engpass ist | — |
| Critical CSS je Seitentyp inline, Hauptstilblatt asynchron (in Paket 267 bewusst nicht gebaut — die Stildateien stehen unter der Designwache des Tors; stattdessen gepackt ausgeliefert); Schriften lokal (heute von `fonts.googleapis.com`) | VL16, RE07 |
| Alpine.js und `@alpinejs/intersect` (`base.html`), GSAP und das nachgeladene Three.js (`index.html`) selbst ausliefern statt von `cdn.jsdelivr.net` — spart die Verbindung zu einem zweiten Host. Am 17.09.2026 (Paket 227) **nicht möglich:** keine der vier Dateien liegt im Projekt, der Lauf konnte sie nicht herunterladen; steht als „beim Kunden" im Bewertungsblock von [80-AUFGABEN.md](80-AUFGABEN.md). Mit den Dateien: nach `shop1/static/shop1/`, `src` auf `{% static %}`, `integrity` und `CSP_QUELLEN` nachziehen | PF31 |
| `width`/`height` an den Bildern ohne Masse (Admin-Vorlagen, `index.html:38`, `produkt_detail.html:89`) | VL15 |
| Lighthouse mobil auf 90 und Desktop auf 95 heben — die grössten Posten sind unbenutztes JavaScript und die Bildformate | PF01, PF02 |