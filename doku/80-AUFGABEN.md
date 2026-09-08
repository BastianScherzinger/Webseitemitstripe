---
bereich: aufgaben
titel: Aufgaben
stand: 2026-09-08
status: teilweise
fortschritt: 40
zusammenfassung: Im Zweig sind SU04, GE23, GE25 und IS19 erledigt und seit dem 08.09.2026 zusätzlich SI08 (CSP scharf statt Report-Only), TS11 (CANONICAL_HOST hat die Hauptadresse als Vorgabe, die 301 braucht keinen Railway-Eingriff mehr) und PJ05 (V11 im Django-Admin registriert, die verschluckte Ausnahme protokolliert, sechs weitere Funde mit Vermerk im Code festgehalten). Nächster Schritt bleibt der Merge des Arbeitszweigs nach main; danach Schriften lokal, Sprungmarke, Permissions-Policy, Danke-Seite; drei Freigaben und die Produktbeschreibungen liegen weiter bei der Betreiberin.
offen: 7
quellen: LOGBUCH.md, CLAUDE.md, GOOGLE_SEO_GUIDE.md
---

# Aufgaben — Luviq Universe

*Woran sich der Fortschritt bemisst: am Anteil der erledigten an allen in dieser Datei geführten Aufgaben — „Erledigt“ gegen „Erledigt + Offen + Fehlt + Beim Kunden“, auf Zehner gerundet. „Verbesserungsmöglichkeiten“ zählen nicht mit, sie sind Kür, keine Zusage. Bei allen sechs betreuten Seiten dieselbe Rechnung.*

Regelkennungen verweisen auf die **Messung vom 02.09.2026 (Regelstand 2026-09-02a)**.
„Offen" = konkret als Nächstes · „Fehlt" = noch nicht begonnen ·
„Verbesserungsmöglichkeiten" = die grössten Hebel aus den offenen Regeln ·
„Beim Kunden" = braucht Zuarbeit der Betreiberin · „Erledigt" = mit Datum.

## Missbrauchsschutz am Formular (Erhebung 04.09.2026)

Aus dem Pflichtabschnitt in [10-TECHNIK.md](10-TECHNIK.md). Jede Zeile ist ein
Baustein, der im Quelltext dieses Projekts **nicht** gefunden wurde. Die
Hauptseite führt alle; was dort steht, lässt sich übernehmen.

- [ ] **Honeypot**
- [ ] **Zeitfalle (signierter Zeitstempel)**
- [ ] **Inhalts-Score mit Schwelle**
- [ ] **Adresse ohne `http://` erkannt**
- [ ] **Fremde Domain mit eigenem Markennamen**
- [ ] **Mail-Obergrenze je Tag**
- [ ] **Prüfbefehl für die Abwehr**

## Offen

Alles hier ist vorbereitet und wartet nur auf Ausführung.

| # | Aufgabe | Warum jetzt | Wo |
|---|---|---|---|
| 1 | **Arbeitszweig `sofort/2026-09-08-pj05-und-2-weitere` nach `main` mergen und pushen** (drei Commits, `git log main..HEAD`; 216/216 Tests grün laut Commit `a1169a4`) | Erst mit dem Deploy wirken die 301 des Apex (`TS11`), die durchgesetzte CSP (`SI08`) und die Newsletter-Verwaltung (`V11`). Der Lauf 4 selbst ist bereits auf `main` (`511ffe5` ist dort enthalten) | `git merge` + Push, Railway baut selbst |
| 2 | Nach dem Deploy nachmessen: 301 des Apex, `Content-Security-Policy` statt `-Report-Only` auf jeder Seite, `llms.txt` = 200, Sitemap mit `lastmod` | `TS11` und `SI08` sind im Code erledigt, gemessen wird aber die Live-Seite — belegt ist es erst nach der Messung | Werkzeug, Messlauf |
| 3 | **Google-Schriften lokal hosten** (Inter 400–700, Outfit 700/900 als WOFF2, `@font-face`, `font-display: swap`) | `RE07` ist der einzige **kritische** Rechtsbefund, den der Zweig nicht behebt: 13 von 13 Seiten laden von `fonts.googleapis.com`, die Adresse des Besuchers geht vor jeder Einwilligung zu Google | `templates/base.html`, Zeilen 172–175 |
| 4 | **Sprungmarke „Zum Inhalt"** als erstes fokussierbares Element im `body`, Ziel-`id` im `<main>` | `BF08`/`VL17`: 13 von 13 Seiten ohne. Änderung am Seitengerüst → Designwache-Referenz bewusst nachziehen | `templates/base.html`, `aufbau_referenz.json` |
| 5 | **Menüknopf und Icon-Knöpfe benennen** (`aria-label`), dazu die 5 namenlosen Links auf `/produkte/` | `BF12` (13 namenlose Schaltflächen), `BF11`, `VL18` — reine Attributarbeit, die Designwache bleibt grün | Templates |
| 6 | **`Permissions-Policy`-Kopfzeile** setzen (mindestens `geolocation=()`, `camera=()`, `microphone=()`, dazu `payment=()`, `usb=()`, `browsing-topics=()`) | `SI07`, `VL04`: fehlt auf 14 von 14 Seiten; die CSP-Middleware ist die passende Stelle | `shop1/middleware.py` |
| 7 | **Eigene Danke-Seite** nach dem Kontaktformular (`/kontakt/danke/`) statt einer Meldung auf derselben Seite | `KV07`: ohne eigene URL ist kein Abschluss messbar — Voraussetzung für jede spätere Messung, auch ohne Ads | `views/shop.py`, `urls.py`, neues Template |

## Fehlt

Noch nicht begonnen — kein Code, kein Plan, kein Termin.

| Bereich | Was fehlt | Regel |
|---|---|---|
| **Tor** | **Ein einziger Eintrag in `sites.json` → `pruefbefehle`** — die Liste ist **leer**, und damit fährt das Paket-Tor an dieser Seite **keinen** Prüfbefehl: `tor_hindernisse()` prüft Bedingung 3 als `if rot:`, und was nie gefahren wurde, ist nie rot. Ein Paket passiert hier mit „0 von 0 grün“. Die Testsuite ist vorhanden und **grün** (215 Funktionen, 137 s, gemessen 06.09.2026); es fehlt nur `"python manage.py test"` in der Liste. Erhebung über alle sechs Seiten: `pystore-overview/docs/BEFUNDE-UEBERTRAGBAR.md` **B22** | — (Werkzeugseite) |
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
| **`SU02`** | **1.557 Eigenwörter über 13 Seiten, Zielgrösse 12.000** (von 2.434 Wörtern Gesamttext); umfangreichste Seiten `/` (390 W), `/liefergebiet/` (259 W), `/ueber_uns/` (194 W) | Auskunft statt Werbung: Abläufe, Preisrahmen, echte Fälle, beantwortete Fragen. Die drei ersten Wissensbeiträge im Zweig bringen zusammen rund 2.650 Wörter, warten aber auf die Freigabe; die drei aus SU04 bringen 3.163 Wörter (1.129 + 1.034 + 1.000, gemessen 07.09.2026, festgehalten in `MINDESTWOERTER`) und zählen ohne Rückfrage mit, sobald der Zweig live ist |
| **`SU01`** | **13 rankfähige Seiten, Zielgrösse 30** für diese Geschäftsart | Je wiederkehrender Kundenfrage eine Seite. Bestellablauf, Widerruf und Konto sind mit SU04 gebaut; offen bleiben Themen, die Angaben der Betreiberin brauchen (Materialien, Preisrahmen, Rückporto) |
| **`SU04`** | **0 Wissensseiten, Zielgrösse 3** — kein einziger Ratgeberbereich | **Im Zweig erfüllt** (07.09.2026, `d7d2e0b`): drei Beiträge, deren jede Sachangabe aus AGB, Datenschutz, Impressum, Liefergebiet oder dem Shop-Code belegt ist, stehen auf `freigegeben: True` — `/wissen/bestellen-und-bezahlen/`, `/wissen/widerruf-und-ruecksendung/`, `/wissen/konto-und-daten/`. Sie brauchen keine Zuarbeit; Sitemap und `llms.txt` führen sie samt Übersicht (vier Adressen), `/wissen/` ist dadurch indexierbar. Live zählt der Punkt erst nach dem Merge |
| `SU07` | 0 Wissensseiten auf 6 Verkaufsseiten; Ziel eine je drei | Die drei belegten Beiträge zählen ab dem Merge mit; die drei gesperrten erst nach der Freigabe |
| `SU06` | im Schnitt 120 Eigenwörter je Seite, Ziel 400; dünnste: Produktseiten mit 25 W | Echte Produktbeschreibungen der Betreiberin. Der Zweig ergänzt nur den für alle Produkte gleichen Zusatz — mit IS19 (08.09.2026) ist dieser Zusatz länger geworden, aber auf allen fünf Stücken **derselbe Text**. Das hebt die Wortzahl, nicht die Eigenständigkeit: die Textgleichheit zwischen den Produktseiten (`IS21`) sinkt dadurch nicht |
| `SU08` · `SU09` · `SU10` | 4 von 5 Themenbereichen mit nur einer Seite; `/produkt/` ohne Übersichtsseite (Zweig: 301 auf `/produkte/`); `/produkt/` hält 56 % aller Unterseiten | Bereiche ausbauen statt weitere Einzelseiten anlegen |

### Inhalt und Titel

| Regel | Befund | Was es braucht |
|---|---|---|
| **`IS19`** | **85 % der Seiten sind dünn (11 von 13)**: `/produkte/` 62 W, `/kontakt/` 91 W, `/datenschutz/` 185 W, `/agb/` 179 W, `/gaestebuch/` 70 W … (+6) | **Im Zweig behoben** (08.09.2026, `b35f6e4`): keine indexierbare Seite liegt noch unter 200 Wörtern im Inhaltsbereich (gemessen mit einem Produkt und ohne Kommentare). `/impressum/` bleibt bei 75 Wörtern — es trägt `noindex` und steht weder in der Sitemap noch in `llms.txt`. Live gilt weiter der Messwert |
| **`IS18`** | **Umfang passt nicht zur Aufgabe: 7 von 7 Seiten darunter** — `/` 390/700 W, `/produkte/` 62/600 W, Produktseiten je 25/600 W | Mindestumfang je Seitenart halten. Der Zweig hebt `/produkte/` auf 238 und die Produktseiten auf 211 Wörter — die Zielgrösse 600 erreicht keine davon; dafür braucht es eine echte Beschreibung je Einzelstück, die nur die Betreiberin liefern kann (`SU06`) |
| `IS17` | 12 von 13 Seiten unter 300 Eigenwörtern | dito |
| **`IS23`** | **Kannibalisierung: „custom print" auf 3 Seiten** (`/produkt/custom-print-hoodie-1/`, `/produkt/custom-print-jacke/`, `/produkt/custom-print-hoodie/`), 3 von 5 Seiten betroffen | Je Begriff eine Seite: Produktnamen im Shop-Admin unterscheidbar machen oder `seo_titel` setzen; zwei Produkte tragen sogar denselben Titel (`IS03`, `BF21`) |
| `IS02` · `IS09` · `IS11` · `IS06` | Titel 7 von 13 in der Zielspanne, Beschreibungen 5 von 13, Handlungsaufforderung in 4 von 13, Ort oder Nutzen im Titel bei 2 von 13 | Grösstenteils im Zweig erledigt (Schritte 11–13); nach dem Merge nachmessen |
| `IS14` | 10 von 13 Seiten springen `h1 → h3` | Nur mit bewusster Änderung der Designwache-Referenz |

### Recht und Vertrauen

| Regel | Befund | Was es braucht |
|---|---|---|
| **`RE06`** | **3 von 3 eingebundenen Diensten fehlen in der Datenschutzerklärung**: `cdn.jsdelivr.net`, `fonts.googleapis.com`, `maps.google.com` | **Im Zweig behoben** — die Erklärung nennt jetzt Cloudinary, Google Fonts, Google Maps, Railway, jsDelivr, ip-api, Brevo und PayPal. Live steht noch die alte Fassung (nur PayPal, Railway) |
| **`RE07`** | **13 von 13 Seiten laden Google-Schriften von fremden Servern** (`fonts.googleapis.com`, Inter und Outfit) | Selbst hosten — **nicht** im Zweig behoben, siehe „Offen" Nr. 3 |
| `RE03` | Im Impressum nicht auffindbar: Anbietername oder Rechtsform, Strasse mit Hausnummer (gefunden: PLZ mit Ort, E-Mail, zweiter Kontaktweg) — der Prüfer erkennt „Luisa Brehler" und „Grünberger Str. 16" nicht als solche | Angaben klarer auszeichnen; inhaltlich sind sie vorhanden |
| `RE09` | Widerrufsbelehrung in `/agb/`, aber ohne Muster-Widerrufsformular | Eigene Seite, aus dem Fuss verlinkt |

### Konversion und Barrierefreiheit

| Regel | Befund | Was es braucht |
|---|---|---|
| **`KV01`** | **1 von 13 Seiten mit `tel:`-Link** — und dieser eine ist die Platzhalternummer „+49 (0) 30 123456" auf `/kontakt/` (main). Nach dem Merge sind es 0 | Nur die Betreiberin kann eine echte Nummer nennen (siehe „Beim Kunden"). Ohne Nummer bleibt die Regel offen — eine zu erfinden ist ausgeschlossen |
| **`BF05`** | **5 von 5 Formularfeldern ohne Beschriftung**: `/` (1), `/kontakt/` (4) | **Im Zweig behoben** (Schritt 6, `4f0f878`: jedem Feld ein zugänglicher Name; Auflage 1 korrigierte acht zusammengeklebte Attribute im Checkout) — live noch offen |
| `KV09` | 2 von 6 Vertrauenssignalen auf der Startseite; es fehlen Zertifikate, Referenzen, Jahreszahl, Bewertung im Schema | Nur mit belegbaren Angaben — die sichtbaren „5.0 ★★★★★" sind nicht belegt und dürfen nicht ins Schema |
| `KV05` · `KV06` · `KV07` | Formular ohne Datenschutzhinweis, ohne Honigtopf, ohne Danke-Seite | Siehe „Offen" Nr. 7 und „Fehlt" |
| `BF08` · `BF12` · `BF15` | Keine Sprungmarke, 13 namenlose Schaltflächen, 10 Seiten mit Überschriftensprung | Siehe „Offen" Nr. 4 und 5 |

### Code und Projektgerüst

| Regel | Befund | Was es braucht |
|---|---|---|
| **`PJ05`** | **2 kritische Datei-Befunde der Messung vom 04.09.2026: `mainweb/settings.py:59` — `ALLOWED_HOSTS` steht auf `'*'` — und `shop1/middleware.py:218` — Ausnahme wird verschluckt** | **Im Zweig abgearbeitet** (08.09.2026, `e36f4bc`), acht Funde des Code-Audits an ihrer Stelle: `middleware.py:218` schreibt die Ausnahme beim Schliessen der pystore-Verbindung jetzt als Warnung ins Protokoll (Ablauf unverändert, der Platz wird weiter im `finally` freigegeben); `Subscriber` ist in `shop1/admin.py` registriert (`V11`: Liste, Suche nach Adresse, Filter nach Datum, `erstellt_am` schreibgeschützt — eine Auskunft oder Löschung nach DSGVO braucht keinen Datenbankzugriff mehr; das Panel unter `/shop-admin/` bleibt unverändert). Sechs Stellen bleiben bewusst, wie sie sind, und tragen dafür einen Vermerk im Code: `ALLOWED_HOSTS = ['*']` steht nur im `DEBUG`-Zweig (`# audit-ok K02:`, Test `test_die_hostliste_ist_nicht_offen`), und fünf Views ohne Anmeldeschutz (`_helpers.py:22`, `auth.py:47`, `legal.py:336`, `shop.py:18`, `shop.py:47`) tragen je ein `# offen-ok:` mit dem Grund. Ob der nächste Messlauf diese Vermerke anerkennt, zeigt erst die Messung |
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
| | **Wirkung der drei Freigaben zusammen** | | Die Beiträge verlieren `noindex, follow` und kommen in Sitemap und `llms.txt`. Sitemap, llms.txt, robots-Angabe und die Tests folgen dem Register **von selbst** — es ist je Beitrag ein Wort. Trifft `SU07`, `SU01`, `SU02`, `VL11`, `VL12`. **Nicht mehr davon abhängig:** `SU04` und die Indexierbarkeit von `/wissen/` — beides ist seit SU04 (07.09.2026) durch die drei belegten Beiträge erfüllt |
| 4 | **Telefonnummer** — gibt es eine geschäftliche? | `KV01`, `GE09`, `VL10`, `RE03`: der Betriebsknoten im Schema hat kein Telefon, keine Seite einen `tel:`-Link. Die Platzhalternummer wurde entfernt, statt eine zu erfinden | `tel:`-Link in Kopf und Fuss, `telephone` im Schema, Ergänzung im Impressum |
| 5 | **Erreichbarkeits- oder Antwortzeiten** | `KV11`: „Operationell: 24/7" auf `/kontakt/` (main) ist Platzhaltertext | Angabe auf Start- und Kontaktseite, `openingHoursSpecification` im Schema |
| 6 | **Google-Unternehmensprofil**: existiert eines? Wohin zeigt `GOOGLE_REVIEW_URL`? | Auf der Startseite steht ein Knopf „Bei Google bewerten"; ob dahinter ein Profil liegt, ist nicht dokumentiert. Das Profil muss auf die Betreiberin laufen | Profiladresse in `sameAs` (`GE11`), Local SEO wird messbar |
| 7 | **Search Console**: Property `sc-domain:luviq-alsfeld.com` auf einem Konto der Betreiberin anlegen, Sitemap einreichen, Bastian als Nutzer aufnehmen | `GOOGLE_SEO_GUIDE.md` Schritt 1 — seit Mai 2026 offen; ohne Property ist die Sichtbarkeit nicht gemessen | `gsc_property` in `sites.json`, Klick- und Positionsdaten im Werkzeug |
| 8 | **Produktnamen**: zwei aktive Produkte heissen beide „Custom print hoodie" | `IS03`, `IS10`, `IS23`, `BF21`: gleicher Titel, geteilte Beschreibung, drei Seiten auf demselben Begriff | Eindeutige Namen im Shop-Admin; Titel und Slugs folgen automatisch |
| 9 | **Bewertungszahl**: ist „5.0 ★★★★★" belegt? | Wurde deshalb bewusst nicht ins Schema übernommen (`KV09`) | Erst mit echter Quelle ein `AggregateRating` |
| 10 | **Freigabe für zwei bekannte Lücken**: `comment_delete`, `admin_produkt_toggle`, `admin_resend_newsletter` und `admin_newsletter_reset` reagieren auf GET; eine E-Mail-Adresse kann sich zweimal registrieren | Beides ist durch Tests als Ist-Zustand festgehalten; die Änderung berührt Abläufe, die die Betreiberin täglich benutzt | Umstellung auf POST bzw. Eindeutigkeitsprüfung |
| 11 | **Sichtprüfung des Fokusrings** im Browser (Auflage 2 der Gegenprüfung) | Geschmacksentscheidung, keine Messfrage | Anpassung oder Bestätigung |
| 12 | **Dedup-Fenster der Besuchszählung**: 5 oder 30 Minuten? | Der Kommentar im Code nannte bis `93b3cde` fälschlich 30 Minuten; der Ist-Zustand sind 5 (`middleware.py`) | Wert bestätigen oder ändern |
| 13 | **Rücksendung: wer trägt das Rückporto, und binnen welcher Frist wird zurückgezahlt?** (neu mit SU04) | Weder AGB noch Datenschutzerklärung noch der Code regeln das. `/wissen/widerruf-und-ruecksendung/` sagt deshalb ausdrücklich, dass die Seite dazu nichts festlegt, statt eine Zahl zu nennen — eine erfundene Angabe wäre hier eine Zusage an den Käufer | Satz im Beitrag ersetzen, Aufnahme in die AGB und in `/wissen/` prüfen |
| 14 | **Eine eigene Beschreibung je Einzelstück** — welches Basisteil, welches Motiv, welche Grösse, welcher Zustand (neu mit IS19) | Der Zuwachs aus IS19 ist auf allen fünf Produktseiten wortgleich; er stammt aus AGB, Datenschutzerklärung und dem Code des Bestellvorgangs und beschreibt deshalb den **Kauf**, nicht das **Stück**. Was ein einzelnes Teil ausmacht, steht nirgends im Projekt und lässt sich nicht aus dem Code ableiten | `SU06`, `IS18`, `IS21`: eigener Text je Produkt im Shop-Admin (`Produkt.beschreibung`); die Produktseite gibt ihn ungeändert aus |

## Erledigt

| Datum | Was | Beleg |
|---|---|---|
| 08.09.2026 | `PJ05`, `TS11`, `SI08` — drei Punkte, je ein Commit, **ohne eine Änderung an Template, Aufbau oder Klasse**. *`SI08`:* Vorgabe von `CSP_MODUS` ist `scharf` statt `report-only` — der Browser blockiert jetzt, was nicht in `CSP_QUELLEN` steht, statt es nur in der Konsole zu melden. An die Stelle der geplanten Browserprüfung tritt der Beleg aus der Testsuite (die beiden Deckungstests halten jedes `<script src>`, jedes Stylesheet, jedes Iframe und das PayPal-SDK jeder öffentlichen Seite und jeder Panel-Seite gegen die Liste). Eine Direktive wurde dabei weiter: `form-action` erlaubt neben `'self'` jetzt `https://*.paypal.com`, weil das SDK den Bezahlvorgang notfalls per Formular in ein neues Fenster schickt. Rückweg ohne neuen Stand: `CSP_MODUS=report-only`. *`TS11`:* `CANONICAL_HOST` hat die Hauptadresse `www.luviq-alsfeld.com` als Vorgabe statt einer leeren Zeichenkette — die Variable war in Railway nie gesetzt, deshalb lief die 301 seit Schritt 37 nie. Die Umgebungsvariable behält den Vorrang, ein leerer Wert schaltet die Weiterleitung weiter ab. *`PJ05`:* siehe „Verbesserungsmöglichkeiten → Code und Projektgerüst". Prüfbefehl grün, 216/216 Tests grün, `test_aufbau` unverändert | `e36f4bc`, `ecc84f2`, `a1169a4` |
| 08.09.2026 | `GE23`, `GE25`, `IS19` — drei Textpunkte, je ein Commit, **ohne eine Änderung am Aufbau** (kein neues Element, keine geänderte Klasse, keine Kennung; der Zuwachs steht in Absätzen, die es schon gab). *Antwort zuerst:* jeder erste Absatz nennt im ersten Satz, was die Seite ist, und trägt eine belegte Zahl — `/produkte/` und `/gaestebuch/` die Bestandszahl aus der Datenbank (`produkte_liste\|length`, `comments\|length`), `/kontakt/`, `/ueber_uns/` und `/liefergebiet/` die PLZ 36304 und die Versanddauer, `/datenschutz/` seine vier Abschnitte, `/agb/` seine fünf Paragraphen und die 14-Tage-Frist, jede Produktseite Name, Preis und Herkunft aus dem Datensatz; die Ausnahmemenge `OHNE_ZAHL_IM_ERSTEN_DRITTEL` ist damit leer. *Zahlen:* nur Angaben mit Beleg im Projekt (14 Tage aus § 5 AGB, Versand 1–2 und Zustellung 1–3 Werktage, 5 Minuten Sperrfrist und ein Besuch je Sitzung und Tag aus `middleware.py`, `SESSION_COOKIE_AGE = 1209600` = 14 Tage). *Dünne Seiten:* keine indexierbare Seite unter 200 Wörtern im Inhaltsbereich — gemessen mit einem Produkt und ohne Kommentare `/produkte/` 111 → 238, `/kontakt/` 135 → 245, `/gaestebuch/` 99 → 300, Produktseite 103 → 211, `/agb/` 177 → 240; `MINDESTWOERTER` nachgezogen, 215/215 Tests grün, `test_aufbau` unverändert | `fd82efd`, `2b26108`, `b35f6e4` |
| 07.09.2026 | `SU04`: drei Wissensbeiträge ohne Freigabevorbehalt — Bestellen und Bezahlen (1.129 W), Widerruf und Rücksendung (1.034 W), Konto und Daten (1.000 W); jede Sachangabe aus AGB, Datenschutz, Impressum, Liefergebiet oder dem Shop-Code belegt. Angemeldet in `WISSEN_BEITRAEGE`, `seiten_stand.py` (Stand und Name), `WISSEN_SEITEN`, `tests/_basis.py`, `FAQ_SEITEN`, `MINDESTWOERTER` und der Designwache-Referenz (gezielt ergänzt); `/wissen/` damit indexierbar, kein Designwechsel, 215/215 Tests grün | `d7d2e0b` |
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
| SU09 | beim Kunden | `/produkt/` leitet seit Welle 3 per 301 auf die Übersicht `/produkte/` (`shop1/views/legal.py::produkt_uebersicht_redirect`, Test `test_seo.test_produkt_ohne_kennung_leitet_auf_die_uebersicht`); gemessen wurde die Live-Seite, auf der der Zweig noch nicht ausgeliefert ist — eine zweite Übersichtsseite unter `/produkt/` wäre ein Volltext-Duplikat von `/produkte/` und träfe den Befund IS21. | 2026-09-05 |
| SU02 | beim Kunden | Von 9.350 fehlenden Eigenwörtern liegen 2.913 fertig, aber wegen `'freigegeben': False` auf `noindex`, und die restlichen rund 6.400 verlangen Preisrahmen, Abläufe und echte Fälle, die im Repository nirgends stehen — beides kann nur die Betreiberin liefern. | 2026-09-06 |
| SU07 | beim Kunden | Drei fertige Wissensbeiträge auf sechs Verkaufsseiten übertreffen die Zielgrösse bereits, stehen aber wegen unbelegter Pflege- und Grössenangaben auf `'freigegeben': False` (`shop1/views/wissen.py:53,62,71`) und damit auf `noindex` — nur die Betreiberin kann diese Angaben bestätigen. | 2026-09-07 |
| KV01 | beim Kunden | Im ganzen Projekt steht keine geschäftliche Telefonnummer; die frühere Platzhalternummer wurde entfernt und steht als verbotenes Ziel in `FALSCHE_ZIELE` (`shop1/tests/test_inhalt.py`). Eine Nummer zu erfinden hiesse, Kunden auf einen Anschluss zu schicken, der der Betreiberin nicht gehört — nur Luisa Brehler kann eine nennen (siehe „Beim Kunden" Nr. 4). Es wurde dafür keine Zeile geändert. | 2026-09-08 |
| IS21 | beim Kunden | Alle zehn gemeldeten Paare sind Produktseiten-Paare, und deren Text unterscheidet sich laut `produkt_detail.html:78,115,119,129,130` allein durch Name, Preis und Beschreibung — zwei aktive Stücke tragen beide identisch, und `models.py:85-99` bietet kein weiteres Feld, aus dem sich Unterschied gewinnen liesse. | 2026-09-08 |
| TS11 | beim Kunden | Die 301 bleibt gebaut (`mainweb/settings.py:56-57`, `shop1/middleware.py:32`, Test `shop1/tests/test_einstellungen.py:136`); neu ist der Eintrag im Bewertungsblock `doku/80-AUFGABEN.md:186` als **beim Kunden** mit Beleg — Codestelle, Live-Befund EIG19 und die Fundstelle der Messlücke; der Punkt bleibt damit in der Wertung | 2026-09-08 |
<!-- bewertung:ende -->

## Eigene Punkte

<!-- eigenepunkte:anfang -->
| Punkt | Titel | Bereich | Zustand | Beleg | seit |
|---|---|---|---|---|---|
| EIG01 | Eine gelöschte Datenvariable steht noch in llms.txt und llms-full.txt | technik | offen | bei einer anderen betreuten Seite aufgefallen am 07.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-07 |
| EIG02 | Startseite und Über-mich melden lastmod 04.09., obwohl sie am 06./07.09. geändert wurden | seo | offen | bei einer anderen betreuten Seite aufgefallen am 07.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-07 |
| EIG03 | Die Inhalte-Doku kennt vier Ratgebertexte nicht und widerspricht ihrem eigenen Kopf | inhalte | offen | bei einer anderen betreuten Seite aufgefallen am 07.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-07 |
| EIG04 | Ratgebertexte melden og:type „website", das Schema nennt sie Article | seo | offen | bei einer anderen betreuten Seite aufgefallen am 07.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-07 |
| EIG05 | Impressum zitiert drei aufgehobene Rechtsgrundlagen | recht | offen | bei einer anderen betreuten Seite aufgefallen am 07.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-07 |
| EIG06 | Die Bewertung des eigenen Entwicklers steht sichtbar als Kundenstimme | inhalte | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG07 | Das Schema baut seine Bild-URLs von Hand am Static-Manifest vorbei | seo | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG08 | Ein Kauf schaltet das Stück über seinen Namen ab — zwei Stücke heißen gleich | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: kritisch): shop1/views/checkout.py:226` bildet `{p.name: p …}`, `shop1/admin_views.py:748` nimmt `filter(name=…).first()`; live tragen `/produkt/custom-print-hoodie-1/` und `/produkt/custom-print-hoodie/` beide den Namen „Custom print hoodie" (llms.txt, 08.09.2026). Der Kauf des einen kann das andere deaktivieren und das verkaufte im Shop stehen lassen | 2026-09-08 |
| EIG09 | Vier von fünf Einzelstücken tragen „-ausverkauft" im Text und stehen trotzdem als kaufbar im Shop | inhalte | offen | Tiefenanalyse 08.09.2026 (Schwere: kritisch): llms.txt live: „Custom hoodie mit print: 59.00 EUR – Hoodie mit backprint -ausverkauft" (ebenso `custom-print-hoodie-1`, `custom-print-jacke`, `custom-print-hoodie`); `/produkte/` zeigt dieselben Stücke am 08.09.2026 als „Unique Limited" mit Preis, `/produkt/custom-print-hoodie/` zeigt „-ausverkauft" neben dem Kaufweg | 2026-09-08 |
| EIG10 | Das Kontaktformular meldet Erfolg, auch wenn die Mail nie hinausgeht | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: kritisch): shop1/views/shop.py:85-86` meldet „erfolgreich gesendet" im `try` um `send_brevo_email`, das in `shop1/utils.py:62` nur einen `threading.Thread` startet — jeder echte Sendefehler landet ausschließlich im Protokoll. Die Anfrage wird nirgends gespeichert (kein Modell dafür) | 2026-09-08 |
| EIG11 | Die Doku beschreibt einen Live-Stand, den es seit dem Deploy nicht mehr gibt | status | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): doku/00-STATUS.md:30` („Live-Stand `main` @ `2a17edd` (15.07.2026)") und `doku/90-NOTIZEN.md:36` („Die Live-Seite zeigt also main, nicht diesen Zweig") gegen live: sitemap.xml führt am 08.09.2026 `/wissen/`, `/wissen/bestellen-und-bezahlen/`, `/wissen/widerruf-und-ruecksendung/`, `/wissen/konto-und-daten/`; `/kontakt/` nennt „Grünberger Str. 16, 36304 Alsfeld" statt der in `doku/90-NOTIZEN.md:167` beschriebenen Platzhalter | 2026-09-08 |
| EIG12 | Die indexierte Wissens-Übersicht veröffentlicht genau die Angaben, für die die Freigabe fehlt | inhalte | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): shop1/views/wissen.py:61-66`: der Kurztext „Waschen auf links bei 30 °C, Trocknen an der Luft, Bügeln nur von links" steht bei `'freigegeben': False`. Live steht dieser Satz auf https://www.luviq-alsfeld.com/wissen/ — einer Seite, die in der Sitemap steht und indexiert wird. Das `noindex` des Beitrags schützt die unbelegte Angabe damit nicht | 2026-09-08 |
| EIG13 | Fünf Sterne ohne Bewertung: „5.0" fest verdrahtet, jeder Kommentar bekommt Sterne, zwei von drei aus eigenen Konten | inhalte | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): shop1/templates/shop1/_reviews_map.html:116-117` schreibt „5.0 ★★★★★" als festen Text, `:56` hängt an **jeden** Gästebuch-Kommentar ★★★★★, obwohl `Comment` kein Bewertungsfeld hat. Live auf `/gaestebuch/` (08.09.2026) drei Kommentare, davon „shopbesitzer" (09.05.2026) und „luisabre" (08.05.2026) | 2026-09-08 |
| EIG14 | Google-Maps-iframe lädt vor jeder Einwilligung — die Doku sagt, es werde nichts Einwilligungspflichtiges geladen | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): shop1/templates/shop1/_reviews_map.html:13-19` und `:97-103` binden `maps.google.com` auf `/` und `/gaestebuch/` ein; `doku/90-NOTIZEN.md:196`: „Kein Consent-Banner — heute richtig, weil nichts Einwilligungspflichtiges geladen wird". Der Messbefund bestätigt den Host live (RE06: `maps.google.com` eingebunden) | 2026-09-08 |
| EIG15 | Der Willkommensrabatt wird nur bei PayPal verbraucht | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): shop1/views/checkout.py:220` setzt `has_welcome_discount = False` ausschließlich in `paypal_capture`; der Zweig `bank_transfer` (`checkout.py:132-138`) geht direkt auf `payment_success`. Wer per Vorab-Überweisung zahlt, behält die 10 % für jede weitere Bestellung | 2026-09-08 |
| EIG16 | Die Bestellbestätigung nennt Einzelpreise, deren Summe nicht zum Gesamtbetrag passt | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): shop1/views/checkout.py:267-286`: die Mail listet `menge x produkt_preis` und darunter `order.gesamt_betrag`, der bereits um 10 % gemindert ist. Das Modell `Order` hat kein Rabattfeld; der Wert lebt nur in der Session (`checkout.py:120`), taucht also weder in der Mail noch in der Bestellansicht auf | 2026-09-08 |
| EIG17 | Newsletter ohne Bestätigungsschritt, ohne Adressprüfung, ohne Abmeldeweg | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): shop1/views/legal.py:351` legt mit `Subscriber.objects.create(email=email)` sofort einen Empfänger an — keine Bestätigungsmail, keine Validierung (`.create()` umgeht die `EmailField`-Prüfung). `shop1/utils.py:65-127` versendet an alle Abonnenten, ohne einen Abmeldelink zu enthalten; ausgelöst aus `shop1/admin_views.py:555 | 2026-09-08 |
| EIG18 | Bestätigungs- und Newsletter-Links hängen an `SITE_URL`; der Vorgabewert zeigt auf einen toten Host | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): mainweb/settings.py:275` fällt ohne die Variable auf `https://luviq-luisa-production.up.railway.app` zurück — dieser Host antwortete am 08.09.2026 mit HTTP 404 (dokumentiert ist der Dienst als `luviq-luisa-shop.up.railway.app`). `shop1/signals.py:48-49` baut daraus den Verifikationslink, `shop1/utils.py:68` die Newsletter-Links. Ohne bestätigtes Konto gibt es keinen Kauf; `pruefe_seite.py:204` warnt nur ins Log | 2026-09-08 |
| EIG19 | Die 301 auf `www` liegt live im Code — es fehlt allein die Umgebungsvariable | seo | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): CanonicalHostMiddleware` wirkt nur mit gesetztem `CANONICAL_HOST` (`mainweb/settings.py:44-48`). Der Zweig ist ausgeliefert (Sitemap führt `/wissen/`), trotzdem liefert `https://luviq-alsfeld.com/` am 08.09.2026 die Seite selbst statt einer Weiterleitung. TS11 ist damit kein Code-, sondern ein Railway-Punkt | 2026-09-08 |
| EIG20 | Die Search Console zählt drei Hostvarianten getrennt — die stärkste ist die ungesicherte Apex-Adresse | seo | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): GSC 09.08.–05.09.2026: `http://luviq-alsfeld.com/` 12 Klicks / 452 Impressionen, `https://www.luviq-alsfeld.com/` 4 / 102, dazu `https://luviq-alsfeld.com/produkte/` 2 / 20 gegen `https://www.luviq-alsfeld.com/liefergebiet/` 0 / 29. 12 von 17 Klicks laufen über eine Adresse, die weder kanonisch noch verschlüsselt ist | 2026-09-08 |
| EIG21 | „second hand alsfeld öffnungszeiten": Platz 1.4, 23 Impressionen, 1 Klick — keine Seite beantwortet die Frage | local-seo | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): GSC 09.08.–05.09.2026; dazu „geschäfte jetzt geöffnet" (Platz 11) und „second hand in der nähe jetzt geöffnet" (Platz 1). Dass es kein Ladengeschäft gibt, steht live nur im Fließtext (`shop1/templates/shop1/ueber_uns.html:68`) und in llms.txt — in keinem Titel und keiner Meta-Beschreibung, die im Suchergebnis erscheint | 2026-09-08 |
| EIG22 | Für Gäste endet die Produktseite in zwei englischen Systemtexten statt in einem Kaufweg | inhalte | offen | Tiefenanalyse 08.09.2026 (Schwere: wichtig): Live `/produkt/custom-print-hoodie/` (08.09.2026) zeigt abgemeldeten Besuchern als einzige Handlungsangebote „🔐 Auth Required" und „📝 Initiate Registration"; Warenkorb und Checkout sind `@login_required` (`shop1/views/cart.py`, `checkout.py:73`). Bei 486 Impressionen im Monat ist die Pflichtregistrierung die erste Abbruchstelle, und sie wird auf Englisch angekündigt | 2026-09-08 |
| EIG23 | Bei Vorab-Überweisung wird der Warenkorb geleert, bevor irgendetwas bezahlt ist | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: hinweis): shop1/views/checkout.py:132-138` leitet nach dem Versand der Bankdaten direkt auf `payment_success`, und `checkout.py:255` löscht dort `cart.items.all()`. Die Bestellung bleibt `pending`, das Stück bleibt für alle kaufbar — der Käufer hat aber weder Ware noch Warenkorb | 2026-09-08 |
| EIG24 | Zwei Doku-Punkte stehen als offen, sind live aber erledigt | aufgaben | offen | Tiefenanalyse 08.09.2026 (Schwere: hinweis): doku/30-INHALTE.md:100` und `doku/90-NOTIZEN.md:173` führen den Widerspruch „Impressum `noindex`, steht aber in der Sitemap" (SU11) als ungelöst; live enthält sitemap.xml am 08.09.2026 kein `/impressum/`, und `shop1/views/legal.py:281-285` begründet den Ausschluss ausdrücklich. Ebenso ist `doku/30-INHALTE.md:73` („live steht auf `/kontakt/` Operationell: 24/7") überholt | 2026-09-08 |
| EIG25 | Die Sitemap bricht mit `KeyError`, sobald eine Seite ohne Registereintrag ergänzt wird | technik | offen | Tiefenanalyse 08.09.2026 (Schwere: hinweis): shop1/views/legal.py:291` greift ungeschützt mit `SEITEN_STAND[page["name"]]` zu, während `shop1/seiten_stand.py:74` für denselben Zweck bewusst `None` zurückgibt. Heute passt beides zusammen; ein vergessener Eintrag nimmt nicht eine Zeile, sondern die ganze sitemap.xml aus dem Betrieb | 2026-09-08 |
| EIG26 | zaehle()` erneuert die Ablaufzeit bei jedem Treffer — kein Zeitfenster ist eins | technik | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG27 | /ueber-mich/` steht in keiner Navigation und in keiner Fußzeile | konversion | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG28 | Der Kopf von `00-STATUS.md` nennt 84,4, der Messblock darunter 93,1 | status | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG29 | Fünf Punkte stehen als „offen" oder „fehlt", sind live erledigt | aufgaben | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG30 | Die Tabelle „Zahlen, die in mehreren Quellen unterschiedlich stehen" nennt selbst drei überholte Werte | notizen | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG31 | theme-color` ist zwei Stufen heller als der Seitengrund | design | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG32 | /favicon.ico` und `/apple-touch-icon.png` lösen statische Pfade in Python auf, die keine Prüfung abdeckt | technik | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG33 | Der Messbefund PJ10 „zwei Views ohne Route" trifft nicht zu | technik | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG34 | anfrage_verarbeiten` sagt im Vertrag „False bei Fehler" und gibt immer True | technik | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG35 | priceRange` im Schema nennt 500 € als Untergrenze, die es einzeln nicht gibt | seo | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG36 | Die Datenschutzerklärung sagt „kein weiterer Anbieter beteiligt", während jede Formularnachricht über Webador läuft | inhalte | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG37 | „100 % Echte Aufträge" und „5★ Kundenzufriedenheit" stehen unbelegt auf der Galerieseite | inhalte | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG38 | Die Kundenliste nennt als wichtigsten Punkt ein Passwort, das seit dem 06.09. gesetzt ist | aufgaben | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG39 | Auf `/ueber-uns/` ist der auffälligste Knopf ein Verweis auf die Website des Entwicklers | inhalte | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
| EIG40 | Die Datenschutzerklärung datiert sich mit `{% now %}` selbst und ist damit immer „aktuell" | technik | offen | bei einer anderen betreuten Seite aufgefallen am 08.09.2026. **An dieser Seite noch nicht geprüft.** | 2026-09-08 |
<!-- eigenepunkte:ende -->
