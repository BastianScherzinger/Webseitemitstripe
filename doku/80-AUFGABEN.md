---
bereich: aufgaben
titel: Aufgaben
stand: 2026-09-03
status: teilweise
fortschritt: 40
zusammenfassung: Nächster Schritt ist der Merge des Zweigs nach main samt CANONICAL_HOST; danach Schriften lokal, Sprungmarke, Permissions-Policy, Danke-Seite; drei Freigaben liegen bei der Betreiberin.
offen: 9
quellen: LOGBUCH.md, CLAUDE.md, GOOGLE_SEO_GUIDE.md
---

# Aufgaben — Luviq Universe

*Woran sich der Fortschritt bemisst: am Anteil der erledigten an allen in dieser Datei geführten Aufgaben — „Erledigt“ gegen „Erledigt + Offen + Fehlt + Beim Kunden“, auf Zehner gerundet. „Verbesserungsmöglichkeiten“ zählen nicht mit, sie sind Kür, keine Zusage. Bei allen sechs betreuten Seiten dieselbe Rechnung.*

Regelkennungen verweisen auf die **Messung vom 02.09.2026 (Regelstand 2026-09-02a)**.
„Offen" = konkret als Nächstes · „Fehlt" = noch nicht begonnen ·
„Verbesserungsmöglichkeiten" = die grössten Hebel aus den offenen Regeln ·
„Beim Kunden" = braucht Zuarbeit der Betreiberin · „Erledigt" = mit Datum.

## Offen

Alles hier ist vorbereitet und wartet nur auf Ausführung.

| # | Aufgabe | Warum jetzt | Wo |
|---|---|---|---|
| 1 | **Zweig `cockpit/2026-09-01-verbesserung-4` nach `main` mergen und pushen** (63 Commits, gepusht, Arbeitsbaum sauber, 215/215 Tests grün) | Der ganze Lauf 4 ist „live-fertig"; nur die drei Wissensbeiträge warten auf die Betreiberin, und die stehen bis dahin auf `noindex` — der Rest kann ohne ihre Antwort raus | `git merge` + Push, Railway baut selbst |
| 2 | **`CANONICAL_HOST=www.luviq-alsfeld.com` in Railway setzen** (Dienst `Luviq-Luisa`, Umgebung `shop`) | Ohne die Variable tut die `CanonicalHostMiddleware` nichts, und `luviq-alsfeld.com` antwortet weiter mit 200 statt 301 (`TS11`, kritisch) | Railway-Variablen |
| 3 | Nach dem Deploy nachmessen: 301 des Apex, `llms.txt` = 200, Sitemap mit `lastmod`, `/kontakt/` ohne Platzhalterdaten, Datenschutz mit allen Diensten | Der Merge trifft laut Logbuch `TS11`, `GE30`, `GE18`, `RE06`, `BF05` und mehrere Meta-Regeln — belegt ist das erst nach der Messung | Werkzeug, Messlauf |
| 4 | **Google-Schriften lokal hosten** (Inter 400–700, Outfit 700/900 als WOFF2, `@font-face`, `font-display: swap`) | `RE07` ist der einzige **kritische** Rechtsbefund, den der Zweig nicht behebt: 13 von 13 Seiten laden von `fonts.googleapis.com`, die Adresse des Besuchers geht vor jeder Einwilligung zu Google | `templates/base.html`, Zeilen 172–175 |
| 5 | **Sprungmarke „Zum Inhalt"** als erstes fokussierbares Element im `body`, Ziel-`id` im `<main>` | `BF08`/`VL17`: 13 von 13 Seiten ohne. Änderung am Seitengerüst → Designwache-Referenz bewusst nachziehen | `templates/base.html`, `aufbau_referenz.json` |
| 6 | **Menüknopf und Icon-Knöpfe benennen** (`aria-label`), dazu die 5 namenlosen Links auf `/produkte/` | `BF12` (13 namenlose Schaltflächen), `BF11`, `VL18` — reine Attributarbeit, die Designwache bleibt grün | Templates |
| 7 | **`Permissions-Policy`-Kopfzeile** setzen (mindestens `geolocation=()`, `camera=()`, `microphone=()`, dazu `payment=()`, `usb=()`, `browsing-topics=()`) | `SI07`, `VL04`: fehlt auf 14 von 14 Seiten; die CSP-Middleware aus dem Zweig ist die passende Stelle | `shop1/middleware.py` |
| 8 | **CSP von `report-only` auf `scharf`** — vorher `/`, `/produkte/`, `/gaestebuch/`, `/checkout/`, `/payment/<id>/` und das Admin-Panel mit offener Browserkonsole prüfen; null `[Report Only]`-Meldungen sind die Bedingung | `SI08` (keine durchgesetzte CSP), Auflage 6 der Gegenprüfung | `CSP_MODUS` in Railway |
| 9 | **Eigene Danke-Seite** nach dem Kontaktformular (`/kontakt/danke/`) statt einer Meldung auf derselben Seite | `KV07`: ohne eigene URL ist kein Abschluss messbar — Voraussetzung für jede spätere Messung, auch ohne Ads | `views/shop.py`, `urls.py`, neues Template |

## Fehlt

Noch nicht begonnen — kein Code, kein Plan, kein Termin.

| Bereich | Was fehlt | Regel |
|---|---|---|
| Qualitätssicherung | CI-Lauf bei jedem Push, Fehler-Monitoring (Sentry o. ä.), zweiter Prüfbefehl für Links und Konsistenz | `VL19`, `PJ01` |
| Auslieferung | `requirements.txt` mit `==` festnageln plus Lockfile, `runtime.txt`, `railway.json` | `PJ11`, `VL02` |
| Container | Python-Fassung angleichen: Basis-Image auf `python:3.12-slim` **oder** `Django<6.0` — heute prüft die Testsuite Django 6.0, der Container fährt 5.2 | Kommentar in `requirements.txt`, Logbuch „Schritt 38" |
| Fehlerseite | Gestaltete 404-Seite mit Navigation (heute Django-Standard, 13 Wörter) | `BT05`, `TS20` |
| Sicherheit | `integrity`/`crossorigin` an den drei jsdelivr-Skripten (Alpine, Alpine-Intersect, GSAP) | `SI17` |
| Recht | Muster-Widerrufsformular als eigene, aus dem Fuss verlinkte Seite; Erklärung zur Barrierefreiheit (BFSG), sofern die Kleinstunternehmens-Ausnahme nicht greift — ob sie greift, ist **nicht dokumentiert** | `RE09`, `RE12` |
| Formular | Honigtopf im Kontaktformular; Datenschutzhinweis unter dem Formular | `KV06`, `KV05` |
| GEO | `speakable`, Antwort-zuerst-Baustein als Vorlagenteil, IndexNow, `llms-full.txt` | `VL09`, `PJ13`, `GE19`, `GE31` |
| Sitemap | Segmentierung in mehrere Klassen, Sitemap-Index, Bild-Erweiterung für alle Einträge | `VL07`, `TS19` |
| Bilder | Produktbilder aus Cloudinary als WebP/AVIF und mit `srcset` (der Zweig fasst nur die statischen Bilder an) | `PF15`, `PF16`, `VL15` |
| Vorlage | Eigener Angebotsbaustein (`templates/teile/angebot.html`), aus Start- und Kategorieseite eingebunden | `VL21`, `KV14` |
| Betrieb | `STRIPE_*`-Variablen in Railway entfernen — welche Namen dort genau stehen, ist nicht dokumentiert | — |

## Verbesserungsmöglichkeiten

Die grössten Hebel aus den offenen Regeln der Messung vom 02.09.2026. Der schwächste Bereich ist
**Substanz & Reichweite mit 43,6 („Lückenhaft“)** — dort liegt fast alles, was den Gesamtstand von 75,8 nach oben zieht.

### Substanz — der grösste Hebel

| Regel | Befund | Was es braucht |
|---|---|---|
| **`SU02`** | **1.557 Eigenwörter über 13 Seiten, Zielgrösse 12.000** (von 2.434 Wörtern Gesamttext); umfangreichste Seiten `/` (390 W), `/liefergebiet/` (259 W), `/ueber_uns/` (194 W) | Auskunft statt Werbung: Abläufe, Preisrahmen, echte Fälle, beantwortete Fragen. Die drei Wissensbeiträge im Zweig bringen zusammen rund 2.650 Wörter — sie verdoppeln den Bestand, sobald sie freigegeben sind |
| **`SU01`** | **13 rankfähige Seiten, Zielgrösse 30** für diese Geschäftsart | Je wiederkehrender Kundenfrage eine Seite; die drei Wissensseiten sind der Anfang, weitere Themen: Bestellablauf, Rückgabe, Versand, Materialien |
| **`SU04`** | **0 Wissensseiten, Zielgrösse 3** — kein einziger Ratgeberbereich | Liegt fertig im Zweig (`/wissen/` und drei Beiträge), blockiert allein durch die Freigabe |
| `SU07` | 0 Wissensseiten auf 6 Verkaufsseiten; Ziel eine je drei | dito |
| `SU06` | im Schnitt 120 Eigenwörter je Seite, Ziel 400; dünnste: Produktseiten mit 25 W | Echte Produktbeschreibungen der Betreiberin; der Zweig ergänzt nur den für alle Produkte gleichen Zusatz |
| `SU08` · `SU09` · `SU10` | 4 von 5 Themenbereichen mit nur einer Seite; `/produkt/` ohne Übersichtsseite (Zweig: 301 auf `/produkte/`); `/produkt/` hält 56 % aller Unterseiten | Bereiche ausbauen statt weitere Einzelseiten anlegen |

### Inhalt und Titel

| Regel | Befund | Was es braucht |
|---|---|---|
| **`IS19`** | **85 % der Seiten sind dünn (11 von 13)**: `/produkte/` 62 W, `/kontakt/` 91 W, `/datenschutz/` 185 W, `/agb/` 179 W, `/gaestebuch/` 70 W … (+6) | Seiten unter 200 Eigenwörtern ausbauen, zusammenlegen oder auf `noindex` — sie senken die Bewertung der ganzen Domain, nicht nur ihre eigene |
| **`IS18`** | **Umfang passt nicht zur Aufgabe: 7 von 7 Seiten darunter** — `/` 390/700 W, `/produkte/` 62/600 W, Produktseiten je 25/600 W | Mindestumfang je Seitenart halten; bei Produktseiten heisst das eine echte Beschreibung je Einzelstück |
| `IS17` | 12 von 13 Seiten unter 300 Eigenwörtern | dito |
| **`IS23`** | **Kannibalisierung: „custom print" auf 3 Seiten** (`/produkt/custom-print-hoodie-1/`, `/produkt/custom-print-jacke/`, `/produkt/custom-print-hoodie/`), 3 von 5 Seiten betroffen | Je Begriff eine Seite: Produktnamen im Shop-Admin unterscheidbar machen oder `seo_titel` setzen; zwei Produkte tragen sogar denselben Titel (`IS03`, `BF21`) |
| `IS02` · `IS09` · `IS11` · `IS06` | Titel 7 von 13 in der Zielspanne, Beschreibungen 5 von 13, Handlungsaufforderung in 4 von 13, Ort oder Nutzen im Titel bei 2 von 13 | Grösstenteils im Zweig erledigt (Schritte 11–13); nach dem Merge nachmessen |
| `IS14` | 10 von 13 Seiten springen `h1 → h3` | Nur mit bewusster Änderung der Designwache-Referenz |

### Recht und Vertrauen

| Regel | Befund | Was es braucht |
|---|---|---|
| **`RE06`** | **3 von 3 eingebundenen Diensten fehlen in der Datenschutzerklärung**: `cdn.jsdelivr.net`, `fonts.googleapis.com`, `maps.google.com` | **Im Zweig behoben** — die Erklärung nennt jetzt Cloudinary, Google Fonts, Google Maps, Railway, jsDelivr, ip-api, Brevo und PayPal. Live steht noch die alte Fassung (nur PayPal, Railway) |
| **`RE07`** | **13 von 13 Seiten laden Google-Schriften von fremden Servern** (`fonts.googleapis.com`, Inter und Outfit) | Selbst hosten — **nicht** im Zweig behoben, siehe „Offen" Nr. 4 |
| `RE03` | Im Impressum nicht auffindbar: Anbietername oder Rechtsform, Strasse mit Hausnummer (gefunden: PLZ mit Ort, E-Mail, zweiter Kontaktweg) — der Prüfer erkennt „Luisa Brehler" und „Grünberger Str. 16" nicht als solche | Angaben klarer auszeichnen; inhaltlich sind sie vorhanden |
| `RE09` | Widerrufsbelehrung in `/agb/`, aber ohne Muster-Widerrufsformular | Eigene Seite, aus dem Fuss verlinkt |

### Konversion und Barrierefreiheit

| Regel | Befund | Was es braucht |
|---|---|---|
| **`KV01`** | **1 von 13 Seiten mit `tel:`-Link** — und dieser eine ist die Platzhalternummer „+49 (0) 30 123456" auf `/kontakt/` (main). Nach dem Merge sind es 0 | Nur die Betreiberin kann eine echte Nummer nennen (siehe „Beim Kunden"). Ohne Nummer bleibt die Regel offen — eine zu erfinden ist ausgeschlossen |
| **`BF05`** | **5 von 5 Formularfeldern ohne Beschriftung**: `/` (1), `/kontakt/` (4) | **Im Zweig behoben** (Schritt 6, `4f0f878`: jedem Feld ein zugänglicher Name; Auflage 1 korrigierte acht zusammengeklebte Attribute im Checkout) — live noch offen |
| `KV09` | 2 von 6 Vertrauenssignalen auf der Startseite; es fehlen Zertifikate, Referenzen, Jahreszahl, Bewertung im Schema | Nur mit belegbaren Angaben — die sichtbaren „5.0 ★★★★★" sind nicht belegt und dürfen nicht ins Schema |
| `KV05` · `KV06` · `KV07` | Formular ohne Datenschutzhinweis, ohne Honigtopf, ohne Danke-Seite | Siehe „Offen" Nr. 9 und „Fehlt" |
| `BF08` · `BF12` · `BF15` | Keine Sprungmarke, 13 namenlose Schaltflächen, 10 Seiten mit Überschriftensprung | Siehe „Offen" Nr. 5 und 6 |

### Code und Projektgerüst

| Regel | Befund | Was es braucht |
|---|---|---|
| **`PJ05`** | **2 kritische Datei-Befunde: `mainweb/settings.py:59` — `ALLOWED_HOSTS` steht auf `'*'` — und `shop1/middleware.py:218` — Ausnahme wird verschluckt** | Der `'*'`-Zweig greift nur bei `DEBUG=True` (in Railway steht `DEBUG` nicht auf `True`), ist aber trotzdem zu entschärfen; die verschluckte Ausnahme protokollieren — die übrigen acht wurden in Schritt 3 (`2fbf8bd`) bereits mit Protokoll versehen |
| **`VL01`** | **Projektgerüst: 1 von 6 Merkmalen erfüllt** — es fehlen `config/settings.py`, `config/urls.py`, `config/wsgi.py`, ein `apps/`-Paket statt Wurzelmodulen und reine Datenmodule (`data/`) | **Bewusst nicht angefasst.** Der Umbau von `mainweb/` + `shop1/` auf `config/` + `apps/` berührt jeden Import, jede Migration und den Startbefehl — bei der einzigen Seite mit echten Bestellungen ein unverhältnismässiges Risiko für einen Formregelpunkt. Wenn überhaupt, dann als eigener Lauf mit Sandbox-Test |
| `PJ11` · `VL02` | 11 von 11 Abhängigkeiten ohne feste Fassung, kein Lockfile, kein `runtime.txt`, kein `railway.json` | Siehe „Fehlt" |
| `PJ03` | 43 von 53 Python-Modulen von einem Test berührt | Die zehn gemeldeten Module sind über Seiten-, Konto- und Zahlungstests indirekt abgedeckt; das Audit zählt nur direkte Importe |
| `VL19` | 3 von 7 QS-Bausteinen | Siehe „Fehlt" |

## Beim Kunden

Braucht Zuarbeit von **Luisa Brehler**. Nichts davon darf erfunden oder geschätzt werden.

| # | Was | Warum es hängt | Was danach passiert |
|---|---|---|---|
| 1 | **Freigabe der Pflegeangaben:** Waschen auf links bei **30 °C**, **kein Trockner**, **kein Weichspüler**, **Bügeln nur von links** | Die Angaben sind im Projekt nirgends belegt; auf der eigenen Shopseite liest man eine Pflegeanleitung als Anweisung der Verkäuferin — eine falsche Angabe ruiniert ein Einzelstück | `'freigegeben': True` beim Beitrag `pflege-handbemalte-kleidung` in `shop1/views/wissen.py` |
| 2 | **Freigabe der Grössen-Faustregel:** „fünf Zentimeter Unterschied in der Brustweite sind eine ganze Grösse" | Dieselbe Begründung; die Regel entscheidet über Rücksendungen | `'freigegeben': True` bei `groesse-bei-einzelstuecken` |
| 3 | **Freigabe des Upcycling-Beitrags** (keine strittige Zahl darin, die Auflage nennt aber alle drei Beiträge) | Gegenprüfung Lauf 4, Auflage 3 | `'freigegeben': True` bei `upcycling-mode-second-hand-vintage` |
| | **Wirkung der drei Freigaben zusammen** | | Die Beiträge verlieren `noindex, follow`, kommen in Sitemap und `llms.txt`, `/wissen/` wird indexierbar. Sitemap, llms.txt, robots-Angabe und die Tests folgen dem Register **von selbst** — es ist je Beitrag ein Wort. Trifft `SU04`, `SU07`, `SU01`, `SU02`, `VL11`, `VL12` |
| 4 | **Telefonnummer** — gibt es eine geschäftliche? | `KV01`, `GE09`, `VL10`, `RE03`: der Betriebsknoten im Schema hat kein Telefon, keine Seite einen `tel:`-Link. Die Platzhalternummer wurde entfernt, statt eine zu erfinden | `tel:`-Link in Kopf und Fuss, `telephone` im Schema, Ergänzung im Impressum |
| 5 | **Erreichbarkeits- oder Antwortzeiten** | `KV11`: „Operationell: 24/7" auf `/kontakt/` (main) ist Platzhaltertext | Angabe auf Start- und Kontaktseite, `openingHoursSpecification` im Schema |
| 6 | **Google-Unternehmensprofil**: existiert eines? Wohin zeigt `GOOGLE_REVIEW_URL`? | Auf der Startseite steht ein Knopf „Bei Google bewerten"; ob dahinter ein Profil liegt, ist nicht dokumentiert. Das Profil muss auf die Betreiberin laufen | Profiladresse in `sameAs` (`GE11`), Local SEO wird messbar |
| 7 | **Search Console**: Property `sc-domain:luviq-alsfeld.com` auf einem Konto der Betreiberin anlegen, Sitemap einreichen, Bastian als Nutzer aufnehmen | `GOOGLE_SEO_GUIDE.md` Schritt 1 — seit Mai 2026 offen; ohne Property ist die Sichtbarkeit nicht gemessen | `gsc_property` in `sites.json`, Klick- und Positionsdaten im Werkzeug |
| 8 | **Produktnamen**: zwei aktive Produkte heissen beide „Custom print hoodie" | `IS03`, `IS10`, `IS23`, `BF21`: gleicher Titel, geteilte Beschreibung, drei Seiten auf demselben Begriff | Eindeutige Namen im Shop-Admin; Titel und Slugs folgen automatisch |
| 9 | **Bewertungszahl**: ist „5.0 ★★★★★" belegt? | Wurde deshalb bewusst nicht ins Schema übernommen (`KV09`) | Erst mit echter Quelle ein `AggregateRating` |
| 10 | **Freigabe für zwei bekannte Lücken**: `comment_delete`, `admin_produkt_toggle`, `admin_resend_newsletter` und `admin_newsletter_reset` reagieren auf GET; eine E-Mail-Adresse kann sich zweimal registrieren | Beides ist durch Tests als Ist-Zustand festgehalten; die Änderung berührt Abläufe, die die Betreiberin täglich benutzt | Umstellung auf POST bzw. Eindeutigkeitsprüfung |
| 11 | **Sichtprüfung des Fokusrings** im Browser (Auflage 2 der Gegenprüfung) | Geschmacksentscheidung, keine Messfrage | Anpassung oder Bestätigung |
| 12 | **Dedup-Fenster der Besuchszählung**: 5 oder 30 Minuten? | Der Kommentar im Code nannte bis `93b3cde` fälschlich 30 Minuten; der Ist-Zustand sind 5 (`middleware.py`) | Wert bestätigen oder ändern |

## Erledigt

| Datum | Was | Beleg |
|---|---|---|
| 02.09.2026 | Auflage 5: Logbuch-Einträge für die Schritte 1–10 nachgetragen, `CLAUDE.md` auf den heutigen Code gezogen (14 Testmodule, Middlewares, Wissensbereich, Prüfbefehl, Gunicorn) | `511ffe5` |
| 02.09.2026 | Auflage 3: Wissensbeiträge mit Freigabeschalter aus dem Index genommen (`noindex`, nicht in Sitemap und llms.txt), `WissensfreigabeTest` | `60555d0` |
| 02.09.2026 | Auflage 1: acht zusammengeklebte Attribute in `checkout.html` repariert, `AttributSyntaxTest` prüft den Rohtext jedes Start-Tags | `b750337` |
| 02.09.2026 | Auflage 4: `test_geo` vergleicht das Änderungsdatum in der Zeitzone der Seite — die Suite ist nicht mehr täglich zwischen 22 und 24 Uhr UTC rot | `270c5f9` |
| 02.09.2026 | Welle 9: Warenkorb-, Zahlungs-, Konto-, Zugriffsschutz- und Invarianten-Tests (174 → 215) | `87a4e85`, `bbdd58e`, `b776c6e`, `3d73147`, `2e9b051` |
| 02.09.2026 | Welle 8: CSP-Middleware (Report-Only), `CanonicalHostMiddleware` (301), `pruefe_seite` auf die ausgelieferte Seite ausgeweitet und in `start.sh` angeschlossen, Betriebs- und Schutztests | `3a9c2d3`, `6bd5eb4`, `50d68da`, `0bcd0ef` |
| 01.09.2026 | Welle 7: totes Hintergrundbild entfernt, WebP in mehreren Breiten (498,6 → 175,3 KB), GZip, Sitemap- und llms-Cache, `CACHES` gesetzt, Warenkorb-Zähler in einer Abfrage, Geo-Pool, Gunicorn `gthread` | `64055fe` … `b0fba20` |
| 01.09.2026 | Welle 6: Wissensbereich angelegt und angeschlossen — Register, Routen, Übersicht, drei Beiträge (821 / 941 / 890 Wörter) | Schritte 26–30 (`74fba7a`) |
| 01.09.2026 | Welle 5: Antwort-zuerst-Texte auf Startseite, `/produkte/`, `/ueber_uns/`, `/gaestebuch/`, Produktseiten und Impressum; Inhaltstests messen Wortzahlen statt zu schätzen | Schritte 21–25 |
| 01.09.2026 | Welle 4: `WebPage`-Knoten mit gepflegtem `dateModified`, `Person`-Knoten `#luisa`, `BreadcrumbList` zentral, `llms.txt` mit Ort, Versandzeiten und Instagram, GEO-Tests 16 → 20 | Schritte 16–20 |
| 01.09.2026 | Welle 3: Meta-Beschreibungen 157–171 Zeichen mit Aufforderung, Ortsbezug im Produkttitel, Produkt-Metaangaben auf 60/160 begrenzt, `lastmod`-Register, `/produkt/` → 301 | Schritte 11–15 |
| 01.09.2026 | Welle 2: jedes Formularfeld mit zugänglichem Namen, Symbol-Links benannt, Alternativtexte als Beschreibungen, Tastaturfokus sichtbar | Schritte 6–10 |
| 01.09.2026 | Welle 1: `pruefe_seite` unter Versionskontrolle, vertauschte Rechte-Beschriftungen Staff/Admin richtiggestellt, acht verschluckte Ausnahmen protokolliert, tote Importe entfernt, fünf schwache Tests scharf gestellt | Schritte 1–5 |
| 01.09.2026 | Lauf 3: toter Code entfernt, Doku an den Code angeglichen, `LOGBUCH.md` angelegt | `c6e0cce`, `342f7fd` |
| 01.09.2026 | `GOOGLE_SEO_GUIDE.md`: falscher Zielbegriff „railway hosting luviq" gestrichen, DEBUG-Abschnitt richtiggestellt | `691b866` |
| 18.08.2026 | README im Repo; letzte Railway-Auslieferung (SUCCESS) | `645842b` |
| 15.07.2026 | Startseite PageSpeed und Politur; `CLAUDE.md` versioniert — **letzter Stand auf `main`** | `2fe90a0`, `2a17edd` |
| 13.07.2026 | Admin-Mail pro Seitenbesuch vollständig entfernt (Mail-Flut durch Bots ohne Cookies) | `e58775a`, `26b6e72` |
| 05.07.2026 | Bot-Filter geschärft, Hero-Showcase überarbeitet | `8b854c2` |
| 03.07.2026 | Hero der Startseite mit Produktfoto, Trust-Badges und Ticker | `82f3077`, `67fb4fb` |
| 25.05.2026 | Grundausstattung SEO: dynamische Sitemap, robots.txt, Meta und Open Graph, Schema `Organization`/`ClothingStore`/`WebSite`/`ItemList`/`Product` | `GOOGLE_SEO_GUIDE.md`, `DOCUMENTATION.md` |

## Bewertung der Messpunkte

<!-- bewertung:anfang -->
| Punkt | Zustand | Grund | seit |
|---|---|---|---|
<!-- bewertung:ende -->

## Eigene Punkte

<!-- eigenepunkte:anfang -->
| Punkt | Titel | Bereich | Zustand | Beleg | seit |
|---|---|---|---|---|---|
<!-- eigenepunkte:ende -->
