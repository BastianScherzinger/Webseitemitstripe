---
bereich: performance
titel: Performance und Core Web Vitals
stand: 2026-09-03
status: teilweise
fortschritt: 70
zusammenfassung: PageSpeed mobil 68 (Start) bis 89, LCP mobil 5,3 s auf der Startseite und 23 s auf /produkte/; der Zweig bringt WebP, GZip, Cache und gthread, live ist davon nichts.
offen: 8
pagespeed_mobil: 91
pagespeed_desktop: 78
antwortzeit_ms: 5453
quellen: DOCUMENTATION.md, LOGBUCH.md, start.sh
---

# Performance — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Tempo-Wert des Laufs vom 02.09.2026 (PageSpeed mobil doppelt, Desktop einfach gewichtet), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße.*

Alle Zahlen: **Messung vom 02.09.2026 (Regelstand 2026-09-02a)**, gemessen an der Live-Seite,
also am Stand `main`. Der Verbesserungslauf 4 (Zweig) ist **nicht** enthalten — seine
Tempomassnahmen sind unten unter „Umgesetzt (im Zweig)" aufgeführt und live noch nicht wirksam.

## Messwerte

### Lighthouse je Seite

| Seite | Leistung mobil | Leistung Desktop | LCP mobil | LCP Desktop | CLS | TBT mobil | Barrierefreiheit mobil | SEO |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `/` | **68** | 84 | **5,26 s** | 1,29 s | 0 | 296 ms | 100 | 100 |
| `/produkte/` | **70** | 78 | **23,03 s** | 4,18 s | 0 | 0 ms | 93 | 100 |
| `/kontakt/` | 88 | 98 | 3,14 s | 0,84 s | 0 | 0 ms | 98 | 100 |
| `/impressum/` | 89 | 99 | 3,16 s | 0,70 s | 0 | 0 ms | 98 | **69** (wegen `noindex`) |
| `/datenschutz/` | 88 | 99 | 3,17 s | 0,70 s | 0 | 0 ms | 98 | 100 |

Mittel: **mobil 81 von 100** (PF01, Ziel 90), **Desktop 92 von 100** (PF02, Ziel 95), je 5 Messungen.
**LCP im Labor 4,55 s** im Mittel über 10 Messungen (PF03, Ziel < 2,5 s). CLS überall 0 — gut.
Best Practices durchgehend 100. Feldwerte (CrUX) gibt es nicht: PF06 (INP), PF07 (LCP), PF08 (CLS)
sind **nicht messbar** — zu wenig Verkehr.

Der Ausreisser `/produkte/` mit 23 s LCP mobil betrifft die Produktbilder von Cloudinary
(kein `srcset`, kein modernes Format, kein Preload auf dieser Seite).

### Antwortzeit des Servers

| Messung | Wert |
|---|---|
| Mittlere Antwortzeit über 14 Seiten (PF10, Ziel < 600 ms) | **5.475 ms** |
| Median (BT04) | 3.220 ms |
| Langsamste Seiten | `/` 10.097 ms · `/agb/` 9.962 ms · `/produkte/` 9.833 ms · `/datenschutz/` 9.811 ms · `/impressum/` 7.706 ms · `/kontakt/` 7.177 ms |
| Einzelabruf Startseite (Uptime-Prüfung 02.09.2026) | 721 ms |
| Verfügbarkeit 24 h | 100 %, 1.670 Messungen, Ø 1.029 ms |
| Verfügbarkeit 7 Tage | 99,92 %, 3.935 Messungen, Ø 1.099 ms |
| TTFB laut PageSpeed | 2–12 ms (Railway-Kante; die langen Zeiten entstehen dahinter in der Anwendung) |
| Frühere Messung 29.08.2026 | **1,35 s** — damals die **langsamste der sechs betreuten Seiten** |

Die grossen Werte stammen aus Reihenmessungen mit Kaltstart-Anteil; ein einzelner warmer Abruf
liegt bei 0,7–1,0 s. Beides zusammen ergibt das Bild: die Seite ist nicht schnell, aber erreichbar.
Bekannte Ursachen im Code: die Besuchs-Middleware schreibt `PageVisit` und `VisitorLog`
**synchron im Request** (zwei Datenbanken), und auf main läuft Gunicorn mit nur zwei
gleichzeitigen Anfragen für den ganzen Shop.

### Bilder

| Regel | Befund |
|---|---|
| PF15 modernes Format | 0 von 44 Bildern in WebP/AVIF |
| PF16 mehrere Grössen | 0 von 44 Bildern mit `srcset` |
| PF18 `fetchpriority=high` | 13 von 13 Seiten ohne — erstes Bild ist überall das Logo |
| PF19 LCP-Preload | 2 von 3 Schlüsselseiten ohne (`/produkte/`, `/kontakt/`) |
| VL15 Bilder nach Vorlage | 44 geprüft: 44 nicht WebP/AVIF, 10 ohne `width`/`height`, 0 ohne `alt`, 14 weder lazy noch als LCP ausgezeichnet |

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

| Punkt | Beleg (Messung 02.09.2026) | Regel |
|---|---|---|
| Zweig nach `main` — WebP, GZip, Cache, gthread und die kleinere Startseite wirken erst dann | — | PF15, PF16, PF10 |
| Produktbilder aus Cloudinary in WebP/AVIF und mit `srcset` ausliefern (Cloudinary kann das über Transformationsparameter) — der Zweig fasst nur die statischen Bilder an | 0 von 44 mit `srcset`; `/produkte/` LCP mobil 23,0 s | PF15, PF16, VL15 |
| LCP-Bild je Schlüsselseite vorladen und mit `fetchpriority="high"` auszeichnen; das Logo ist heute überall das erste Bild | PF18, PF19 | PF18, PF19 |
| Mittlere Antwortzeit unter 600 ms bringen: `PageVisit`/`VisitorLog`-Schreibvorgänge aus dem Request nehmen, Abfragen der Startseite und von `/agb/`, `/datenschutz/` einzeln nachmessen | 5.475 ms Mittel, 4 Seiten über 9,6 s | PF10, BT04 |
| Seitencache für die reinen Textseiten (`/agb/`, `/datenschutz/`, `/impressum/`) — sie sind statisch und trotzdem unter den langsamsten | | PF10 |
| Critical CSS je Seitentyp inline, Hauptstilblatt asynchron; Schriften lokal (heute von `fonts.googleapis.com`) | 4 von 6 Tempo-Vorkehrungen | VL16, RE07 |
| `width`/`height` an den 10 Bildern ohne Masse (Admin-Vorlagen, `index.html:38`, `produkt_detail.html:89`) | | VL15 |
| Lighthouse mobil auf 90 und Desktop auf 95 heben — die drei grössten Posten sind unbenutztes JavaScript, Bildformate, Serverantwortzeit | mobil 81, Desktop 92 | PF01, PF02 |
