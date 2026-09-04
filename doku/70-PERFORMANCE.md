---
bereich: performance
titel: Performance und Core Web Vitals
stand: 2026-09-03
status: teilweise
fortschritt: 70
zusammenfassung: Der LCP der Produktseite ist der teuerste Posten der Seite (Cloudinary-Bilder ohne WebP und ohne srcset); der Zweig bringt WebP, GZip, Cache und gthread, live ist davon nichts. Die gemessenen Werte stehen im erzeugten Block unter „Messwerte".
offen: 7
pagespeed_mobil: 87
pagespeed_desktop: 70
antwortzeit_ms: 2
quellen: DOCUMENTATION.md, LOGBUCH.md, start.sh
antwortzeit_quelle: PageSpeed server-response-time
---

# Performance — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Tempo-Wert des **letzten** Laufs (PageSpeed mobil doppelt, Desktop einfach gewichtet), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße. Die Zahl selbst steht im erzeugten Block unter „Messwerte“, nicht in diesem Satz.*

Gemessen wird die **Live-Seite**, also der Stand `main`. Der Verbesserungslauf 4 (Zweig) ist
**nicht** enthalten — seine Tempomassnahmen sind unten unter „Umgesetzt (im Zweig)" aufgeführt
und live noch nicht wirksam.

## Messwerte

<!-- tempo:anfang -->
**Messung vom 04.09.2026** (Webagentur Scherzinger Overview, Regelstand 2026-09-04a). Bereich „Performance & Core Web Vitals“: **91,3 von 100**, Reifegrad „Referenz“.

### Lighthouse je Seite

| Seite | Gerät | Leistung | LCP | CLS | TBT | Serverzeit |
|---|---|---:|---:|---:|---:|---:|
| `/` | mobile | **75** | 3,90 s | 0,000 | 308 ms | 3 ms |
| `/` | desktop | **58** | 1,08 s | 0,000 | 4.078 ms | 4 ms |
| `/datenschutz/` | mobile | **90** | 2,74 s | 0,000 | 0 ms | 2 ms |
| `/datenschutz/` | desktop | **58** | 1,09 s | 0,000 | 10.334 ms | 1 ms |
| `/impressum/` | mobile | **92** | 2,71 s | 0,000 | 0 ms | 2 ms |
| `/impressum/` | desktop | **66** | 0,69 s | 0,000 | 1.330 ms | 2 ms |
| `/kontakt/` | mobile | **89** | 2,71 s | 0,014 | 0 ms | 2 ms |
| `/kontakt/` | desktop | **96** | 0,70 s | 0,000 | 132 ms | 1 ms |
| `/produkte/` | mobile | **88** | 3,31 s | 0,000 | 0 ms | 2 ms |
| `/produkte/` | desktop | _nicht gemessen_ | — | — | — | — |

10 Abrufe, davon 0 wiederholt und **1 endgültig ohne Ergebnis**. Ein Abruf ohne Ergebnis steht oben als „nicht gemessen“ — bei CLS und TBT wäre eine Null der Bestwert und damit ein Lob für etwas, das niemand gemessen hat.

**Serverzeit (`server-response-time` aus PageSpeed): 2,1 ms** im Mittel. Das ist die Zahl, an der `PF09` und `PF10` hängen. Die Sekundenwerte, die der eigene Prüfstand je Seite notiert, sind Wanduhrzeiten bei sechs gleichzeitigen Abrufen samt Kaltstart — sie messen den Prüfstand, nicht den Server.

### Tempo-Regeln, die offen sind

| Regel | Titel | Ergebnis | Beleg |
|---|---|---|---|
| `PF01` | Lighthouse Leistung mobil erreicht 90 von 100 | teilweise | Lighthouse Leistung mobil: 87 von 100 über 5 Messungen; unter 90: / (75), /produkte/ (88), /kontakt/ (89) |
| `PF02` | Lighthouse Leistung Desktop erreicht 95 von 100 | teilweise | Lighthouse Leistung Desktop: 70 von 100 über 4 Messungen; unter 95: / (58), /impressum/ (66), /datenschutz/ (58) |
| `PF15` | Bilder liegen in einem modernen Format vor | teilweise | 19 von 44 Bildern in WebP oder AVIF, 25 im alten Format: / → IMG_4376_fupstq, / → Photoroom_20260504_222908_zundp7, / → Photoroom_20260504_222730_jjwtm5, / → Photoroom_20260504_222549_kmlpwf, / → Photoroom_20260504_22182 |
| `PF17` | Lazy-Loading unterhalb des Falzes, nicht auf dem LCP-Bild | teilweise | 23 von 31 Bildern unterhalb des ersten sind lazy; 3 von 13 Seiten laden ihr erstes Bild lazy: /kontakt/ → ich-900.5b4b9566ab5b.webp, /gaestebuch/ → logo-luviq-96.72290a22b8e2.webp, /ueber_uns/ → ich-900.5b4b9566ab5b.webp |
| `PF16` | Bilder werden in mehreren Grössen angeboten | teilweise | 29 von 44 Bildern mit srcset; ohne: / → IMG_4376_fupstq, / → Photoroom_20260504_222908_zundp7, / → Photoroom_20260504_222730_jjwtm5, / → Photoroom_20260504_222549_kmlpwf, / → Photoroom_20260504_221823_rh0ykx |
| `PF18` | Das Hero-Bild trägt fetchpriority=high | teilweise | 3 von 10 Seiten ohne fetchpriority=high am ersten Bild: /kontakt/ → ich-900.5b4b9566ab5b.webp, /gaestebuch/ → logo-luviq-96.72290a22b8e2.webp, /ueber_uns/ → ich-900.5b4b9566ab5b.webp |
| `PF19` | Das LCP-Bild wird vorgeladen, und nur dort, wo es eins gibt | teilweise | 2 von 3 Schlüsselseiten mit Bild laden es nicht vor: /produkte/, /kontakt/ |

### Die grössten Bremsen laut Lighthouse

Keine Einsparchance über 150 ms.
<!-- tempo:ende -->

**Was hier erzeugt wird und was von Hand kommt.** Jede gemessene Zahl steht im Block
darüber; geschrieben hat ihn das Werkzeug („Messung nachziehen"). Von Hand steht hier nur,
was keine Messung hergibt. Bis zum 04.09.2026 stand an dieser Stelle eine PageSpeed-Tabelle
aus `2026-09-02a` — richtig beim Schreiben, zwei Katalogstände später falsch (CLAUDE.md §14).

**Die drei Deutungen, die keine Messung ersetzt:**
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
Datenbanken), und auf `main` läuft Gunicorn mit nur zwei gleichzeitigen Anfragen für den
ganzen Shop.

**Verfügbarkeit** (Monitor des Werkzeugs, 02.09.2026): 100 % über 24 Stunden bei 1.670
Messungen, 99,92 % über 7 Tage bei 3.935 Messungen.

### Bilder

Der grösste Tempohebel der Seite, und der einzige Bereich, in dem alle Regeln zugleich offen
sind — die Zahlen dazu stehen im Block oben:

| Regel | Was offen ist |
|---|---|
| PF15 modernes Format | kein einziges Bild in WebP/AVIF |
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

## Offen

Was zu tun ist. Wie weit die genannten Regeln gerade sind und mit welchem Beleg, steht im
erzeugten Block unter „Messwerte" — hier steht keine Messzahl.

| Punkt | Regel |
|---|---|
| Zweig nach `main` — WebP, GZip, Cache, gthread und die kleinere Startseite wirken erst dann | PF15, PF16 |
| Produktbilder aus Cloudinary in WebP/AVIF und mit `srcset` ausliefern (Cloudinary kann das über Transformationsparameter) — der Zweig fasst nur die statischen Bilder an. **`/produkte/` ist der teuerste LCP der Seite** | PF15, PF16, VL15 |
| LCP-Bild je Schlüsselseite vorladen und mit `fetchpriority="high"` auszeichnen; das Logo ist heute überall das erste Bild | PF18, PF19 |
| `PageVisit`/`VisitorLog`-Schreibvorgänge aus dem Request nehmen — sie laufen synchron gegen zwei Datenbanken. **Nicht wegen `PF10`** (das misst seit `2026-09-04a` die Serverzeit aus PageSpeed und ist bestanden), sondern weil eine Schreiboperation im Request unter Last der erste Engpass ist | — |
| Critical CSS je Seitentyp inline, Hauptstilblatt asynchron; Schriften lokal (heute von `fonts.googleapis.com`) | VL16, RE07 |
| `width`/`height` an den Bildern ohne Masse (Admin-Vorlagen, `index.html:38`, `produkt_detail.html:89`) | VL15 |
| Lighthouse mobil auf 90 und Desktop auf 95 heben — die grössten Posten sind unbenutztes JavaScript und die Bildformate | PF01, PF02 |
