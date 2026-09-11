---
bereich: status
titel: Stand der Seite
stand: 2026-09-11
status: teilweise
fortschritt: 70
zusammenfassung: Gesamtstand 76,5 „Solide“ (04.09.2026). Verbesserungslauf 4, SU04 und GE23/GE25/IS19 liegen auf origin/main; drei belegte Wissensbeiträge, Antwortabsätze mit belegten Zahlen, keine dünne Seite mehr. PJ05 (kritische Audit-Funde abgearbeitet oder begründet), SI08 (CSP blockiert) und PJ11 (Paketfassungen samt Lockfile) sind seit dem Merge 0c18ea7, SI09 (Nonce statt 'unsafe-inline' im script-src, im Browser ungeprüft) seit dem Merge 4ec540b auf main und origin/main. IS18 liegt auf dem Zweig sofort/2026-09-11-is18, nicht gemergt: Startseite, Produktübersicht und Wissensübersicht erreichen laut Commit mit belegtem Fliesstext den Umfang ihrer Seitenart. TS11 wartet weiter auf CANONICAL_HOST. Die drei ersten Beiträge und die Produktbeschreibungen warten auf die Betreiberin.
offen: 3
quellen: CLAUDE.md, DOCUMENTATION.md, LOGBUCH.md
---

# Stand — Luviq Universe

*Woran sich der Fortschritt bemisst: am Gesamtstand der letzten Messung. Die Bezugsgröße jedes Bereichs steht in der jeweiligen Datei unter der Überschrift; sie ist bei allen sechs betreuten Seiten dieselbe.*

## Steckbrief

| | |
|---|---|
| **Kundin** | Luisa Brehler (Anrede: Frau Brehler) |
| **Sitz** | Grünberger Str. 16, 36304 Alsfeld (Hessen) · brehlerluisa@gmail.com · kein Ladengeschäft, Verkauf nur online |
| **Art** | echter Onlineshop mit Bestellungen, Kundenkonten und Zahlung — kein Prospekt |
| **Angebot** | handbemalte Second-Hand-/Vintage-Kleidung, jedes Stück 1-of-1; Versand deutschlandweit, in der Regel 1–2 Werktage |
| **Bezahlung** | **PayPal** oder Vorab-Überweisung; Endpreise nach § 19 UStG (Kleinunternehmerin) — **kein Stripe** |
| **Domain** | `https://www.luviq-alsfeld.com` (200) · Alias `https://luviq-alsfeld.com` (**antwortet ebenfalls 200, keine Weiterleitung** — Stand 02.09.2026) · Railway `luviq-luisa-shop.up.railway.app` (200) |
| **Projektordner** | `C:\Users\basti\Desktop\webseiten buisnes\WebseiteMAIN` |
| **GitHub** | `BastianScherzinger/Webseitemitstripe` · Hauptzweig `main` |
| **Railway** | Projekt `webseiten` → Dienst `Luviq-Luisa` (Umgebung `shop`) |
| **Technik** | Django (≥ 5.0, < 6.1; im Zweig vom 11.09.2026 `==5.2.17` mit `requirements.lock`), Docker (`python:3.11-slim`), PostgreSQL, Cloudinary (Bilder), Brevo (Mail), django-axes, Tailwind-CLI (kein npm im Repo) |
| **Live-Stand** | `main` @ `2a17edd` (15.07.2026); letzte Railway-Auslieferung 18.08.2026 (`645842b`, „docs: README zum Luviq-Universe-Onlineshop", SUCCESS) |
| **Ordner-Stand** | Zweig `sofort/2026-09-11-is18` @ `2591fde` (11.09.2026), ein Commit vor `main`, nicht gemergt und in keinem Remote-Zweig. `sofort/2026-09-11-si09` ist mit `4ec540b`, `sofort/2026-09-11-pj05-und-2-weitere` mit `0c18ea7` in `main` gemergt; `main` = `origin/main` = `4ec540b` (lokale Referenz, geprüft 11.09.2026). `cockpit/2026-09-01-verbesserung-4` (`511ffe5`) ist in `origin/main` enthalten — die Zeile „Live-Stand" darüber ist damit überholt (siehe eigener Punkt `EIG11` in [80-AUFGABEN.md](80-AUFGABEN.md)) |
| **Zertifikat** | Let's Encrypt, TLS 1.3, gültig bis 30.11.2026 (Messung 02.09.2026: 89 Resttage); Alias eigenes Zertifikat bis 30.11.2026 |
| **Verfügbarkeit** | 24 h: 100 % (1.670 Messungen, Ø 1.029 ms) · 7 Tage: 99,92 % (3.935 Messungen, Ø 1.099 ms) — Messung 02.09.2026 |

## Ampel je Bereich

Aus den Köpfen der zehn Bereichsdateien (Stand 02.09.–11.09.2026).

| Bereich | Status | Fortschritt | Zusammenfassung | Datei |
|---|---|---:|---|---|
| Wegweiser | vollständig | 100 | Elf Dateien nach Doku-Standard; die Original-Doku im Projektstamm bleibt die Detailquelle. | [README.md](README.md) |
| Technik | teilweise | 74 | Stack läuft stabil. Seit dem Merge `0c18ea7` liegen auf main auch die scharf gestellte CSP, die festgenagelten Paketfassungen samt `requirements.lock` (Django 5.2.17) und die abgearbeiteten Audit-Funde. Im Zweig `sofort/2026-09-11-si09` (ein Commit, nicht gemergt) erlaubt `script-src` Inline-Code nur noch mit der Nonce der Anfrage, Handler-Attribute sind durch `data-`-Attribute ersetzt, 218 Tests. Offen bleiben der Merge, Bezahlseite und Ersatzskripte mit Browserkonsole, `'unsafe-eval'` für Alpine.js, der erste CI-Lauf mit 5.2.17, `CANONICAL_HOST` in Railway, `runtime.txt`/`railway.json` und die Permissions-Policy. | [10-TECHNIK.md](10-TECHNIK.md) |
| Design | teilweise | 77 | Dunkelbraun-Gold-Linie mit Glas-Karten steht und ist durch die Designwache eingefroren; offen sind Google-Schriften von fremdem Server, englische Restbeschriftungen und seit IS18 die Satzart des langen Versalien-Absatzes auf `/produkte/` (braucht Freigabe). | [20-DESIGN.md](20-DESIGN.md) |
| Inhalte | teilweise | 40 | Live 14 URLs mit 1.557 Eigenwörtern (85 % dünne Seiten); main füllt neun Seiten mit Auskunft, bringt sechs Wissensbeiträge (drei belegt und indexiert, drei warten auf die Freigabe) und hält jede indexierbare Seite über 200 Wörtern. Seit IS18 (11.09.2026, Zweig `sofort/2026-09-11-is18`, nicht gemergt) erreichen Startseite, Produktübersicht und Wissensübersicht laut Commit mit belegtem Fliesstext die Zielgrösse ihrer Seitenart — nur die Produktseiten brauchen weiter eine eigene Beschreibung je Einzelstück. | [30-INHALTE.md](30-INHALTE.md) |
| SEO / GEO | teilweise | 74 | SEO-Technik live solide (92), Inhalt 73, GEO 76; llms.txt, KI-Crawler-Regeln, WebPage/Person/Breadcrumb-Knoten, 301 auf www, drei indexierte Wissensseiten und seit dem 08.09.2026 GE23/GE25/IS19 (Antwortabsatz, belegte Zahlen, keine dünne Seite mehr) liegen fertig im Code, nicht nachgemessen. IS18 (11.09.2026, Zweig `sofort/2026-09-11-is18`, nicht gemergt) bringt Startseite, Produktübersicht und Wissensübersicht laut Commit auf den Umfang ihrer Seitenart und zieht deren lastmod auf den 11.09.2026; die Produktseiten bleiben darunter. | [40-SEO.md](40-SEO.md) |
| Local SEO | teilweise | 25 | Search Console seit 03.09.2026 verbunden (Property `sc-domain:luviq-alsfeld.com` im Konto …05@gmail.com); Unternehmensprofil und Bewertungen bleiben nicht dokumentiert, live auf /kontakt/ stehen noch Platzhalterdaten. | [50-LOCAL-SEO.md](50-LOCAL-SEO.md) |
| Ads | nicht zutreffend | — | Es gibt keine Google-Ads-Kampagne und kein Konto; Voraussetzungen für Shopping-/Suchanzeigen sind benannt. | [60-ADS.md](60-ADS.md) |
| Performance | teilweise | 70 | PageSpeed mobil 68 (Start) bis 89, LCP mobil 5,3 s auf der Startseite und 23 s auf /produkte/; der Zweig bringt WebP, GZip, Cache und gthread, live ist davon nichts. | [70-PERFORMANCE.md](70-PERFORMANCE.md) |
| Aufgaben | teilweise | 40 | SU04, GE23, GE25, IS19, PJ05, SI08, PJ11 und seit dem Merge `4ec540b` auch SI09 liegen auf main und origin/main (Auslieferung durch Railway nicht geprüft; SI09 im Browser ungeprüft). IS18 ist am 11.09.2026 auf dem Zweig `sofort/2026-09-11-is18` anders eingebaut (`2591fde`, nicht gemergt): Startseite, Produktübersicht und Wissensübersicht erreichen laut Commit die Zielgrösse ihrer Seitenart, die fünf Produktseiten bleiben bei der Betreiberin. Nächster Schritt ist der Merge, danach Nachmessung, Bezahlseite und Ersatzskripte mit Browserkonsole und der erste CI-Lauf mit Django 5.2.17; Schriften lokal, Sprungmarke, Permissions-Policy, Danke-Seite und die Freigaben der Betreiberin bleiben offen. | [80-AUFGABEN.md](80-AUFGABEN.md) |
| Notizen | vollständig | 100 | Vier Namen für ein Projekt, PayPal statt Stripe, Zweig gegenüber main, zehn Widersprüche zwischen Quellen und Live-Seite. | [90-NOTIZEN.md](90-NOTIZEN.md) |

## Messung

<!-- messung:anfang -->
**Messung vom 04.09.2026** (Webagentur Scherzinger Overview, Regelstand 2026-09-05a) — **Gesamtstand 76,5 von 100**, Reifegrad „Solide“. 230 von 244 Regeln an 14 URLs und 126 Dateien (25.340 Zeilen) geprüft.

| Bereich | Wert | Reifegrad |
|---|---:|---|
| Substanz & Reichweite | **44** | Lückenhaft |
| Konversion | **58** | Lückenhaft |
| Vorlagen-Konformität | **64** | Brauchbar |
| SEO — Inhalt | **73** | Brauchbar |
| Code-Qualität & Projektreife | **73** | Brauchbar |
| GEO — KI-Sichtbarkeit | **76** | Solide |
| Recht & Vertrauen | **79** | Solide |
| Sicherheit | **87** | Solide |
| Barrierefreiheit | **90** | Solide |
| SEO — Technik | **92** | Referenz |
| Performance & Core Web Vitals | **93** | Referenz |
| Betrieb & Auslieferung | **93** | Referenz |

Keine Sperre greift.

Quelltext: 126 Dateien, **115 Befunde**, davon 2 kritisch und 36 wichtig.

Kritische Befunde:

- **Alle Domainvarianten landen auf einer Adresse** (`TS11`) — 0 von 1 Nebenadressen landen dauerhaft auf der Hauptadresse — offen: https://luviq-alsfeld.com: 200 → https://luviq-alsfeld.com/
- **Umfang passt zur Aufgabe der Seite** (`IS18`) — Unter dem Umfang, den ihre Aufgabe verlangt: 7 von 7 Seiten — / (533/700 W), /produkte/ (160/600 W), /produkt/custom-hoodie-mit-print/ (111/600 W), /produkt/custom-print-hoodie-1/ (110/600 W), /produkt/custom-pants-sold/ (110/600 W) … (+2)
- **Kein nennenswerter Anteil dünner Seiten** (`IS19`) — 69% der Seiten sind dünn (9 von 13): /produkte/ (160 W), /kontakt/ (142 W), /agb/ (179 W), /gaestebuch/ (78 W), /produkt/custom-hoodie-mit-print/ (111 W) … (+4)
- **Keine Beinahe-Duplikate zwischen Seiten** (`IS21`) — 10 Seitenpaare über 60 Prozent Textgleichheit, höchster Wert 100%: /produkt/custom-hoodie-mit-print/ = /produkt/custom-print-hoodie-1/ (100%), /produkt/custom-hoodie-mit-print/ = /produkt/custom-print-hoodie/ (98%), /produkt/custom-print-ho
- **Wissensinhalte vorhanden** (`SU04`) — 0 Wissensseiten, Zielgröße 3 — es gibt keinen einzigen Ratgeberbereich
- **Die Telefonnummer ist anklickbar und steht auf jeder Seite** (`KV01`) — 0 von 13 Seiten mit tel:-Link (Startseite: nein) — ohne: /, /produkte/, /kontakt/, /datenschutz/, /agb/ … (+8)
- **Keine Google-Schriften von fremden Servern nachgeladen** (`RE07`) — 13 von 13 Seiten laden Google-Schriften von fremden Servern: fonts.googleapis.com, https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700 · betroffen: /, /produkte/, /kontakt/ … (+10)
- **Das Projektgerüst liegt an der vereinbarten Stelle** (`VL01`) — Projektgerüst: 1 von 6 Gerüst-Merkmalen erfüllt — es fehlt: config/settings.py, config/urls.py, config/wsgi.py, apps/-Paket statt Wurzelmodule, reine Datenmodule (data/)
- **Genug eigener Inhalt insgesamt** (`SU02`) — 2.650 Eigenwörter über 13 Seiten, Zielgröße 12.000 (von 3.586 Wörtern Gesamttext); die umfangreichsten Seiten: / (533 W), /ueber_uns/ (376 W), /datenschutz/ (371 W)
- **Es gibt keinen kritischen Datei-Befund** (`PJ05`) — 2 kritische Befunde: mainweb/settings.py:59 ALLOWED_HOSTS steht auf '*', shop1/middleware.py:218 Ausnahme wird verschluckt
- **Keine Kannibalisierung durch gleiche Hauptbegriffe** (`IS23`) — Von mehreren Seiten besetzte Hauptbegriffe: 1; betroffen sind 3 von 5 Seiten — custom print auf 3 Seiten (/produkt/custom-print-hoodie-1/, /produkt/custom-print-jacke/ … (+1))
- **Die Qualitätssicherung der Vorlage ist verdrahtet** (`VL19`) — Prüfbefehle: pruefe_seite; 215 Testfunktionen in 14 Dateien: 3 von 7 QS-Bausteinen erfüllt — es fehlt: zweiter Prüfbefehl (Links, Konsistenz), eigene Management-Befehle, CI-Lauf bei jedem Push, Fehler-Monitoring (Sentry o. ä.)
- … und 1 weitere
<!-- messung:ende -->

Gemessen wurde die **Live-Seite (main)**, der Code-Audit lief über den **lokalen
Ordner (Zweig)** — die Zahl mischt also zwei Stände, siehe
[90-NOTIZEN.md](90-NOTIZEN.md).

## Die drei wichtigsten offenen Punkte

1. **Den Zweig `sofort/2026-09-11-is18` nach `main` bringen und pushen, in Railway `CANONICAL_HOST=www.luviq-alsfeld.com` setzen.** Durchgesetzte CSP, feste Paketfassungen, Subscriber im Django-Admin (`0c18ea7`) und SI09 (`4ec540b`, Nonce statt `'unsafe-inline'`) sind bereits auf `main` und `origin/main`; offen sind `2591fde` (IS18, längere belegte Texte auf `/`, `/produkte/` und `/wissen/` — danach nachmessen) und die 301 für `luviq-alsfeld.com` (TS11), deren Vorgabe weiter leer ist. Danach mit offener Browserkonsole die Bezahlseite `/payment/<id>/` und die Ersatzskripte für die früheren `on…`-Attribute (Löschrückfragen, Bestellfilter, Kampagnenknöpfe) ansehen und den ersten CI-Lauf mit Django 5.2.17 abwarten — beides ist bisher nicht belegt.
2. **Freigabe der Betreiberin** für die drei **ersten** Wissensbeiträge (Pflegeangaben 30 °C / kein Trockner / kein Weichspüler / Bügeln von links; Faustregel „fünf Zentimeter sind eine ganze Grösse"). Danach je Beitrag `'freigegeben': True` in `shop1/views/wissen.py` — Sitemap, llms.txt und robots-Meta folgen von selbst. `SU04` hängt seit dem 07.09.2026 **nicht mehr** daran: drei belegte Beiträge (Bestellen, Widerruf, Konto) sind ohne Vorbehalt freigegeben und erreichen die Zielgrösse 3. Die Freigabe trifft weiter `SU07`, `SU01` und den grösseren Teil von `SU02`.
3. **Google-Schriften lokal hosten** (RE07, 13 von 13 Seiten laden Inter/Outfit von `fonts.googleapis.com`) — der einzige kritische Rechtsbefund, den der Zweig **nicht** behebt; `base.html` Zeile 172–175.

## Zuletzt erledigt

| Datum | Was | Beleg |
|---|---|---|
| 11.09.2026 | `IS18` (anders eingebaut) auf `sofort/2026-09-11-is18` (nicht gemergt): Startseite, Produktübersicht und Wissensübersicht mit belegtem Fliesstext in bestehenden Absätzen auf dem Umfang ihrer Seitenart (laut Commit gezählt wie das Werkzeug, ohne Produkt im Bestand), jede Angabe mit Fundstelle in `LOGBUCH.md`; `MINDESTWOERTER` und `seiten_stand.py` nachgezogen, kein Element, keine Klasse, keine Kennung verändert, 218/218 Tests grün laut Commit. Offen: die fünf Produktseiten (eigene Beschreibung je Stück, Betreiberin), Live-Nachmessung | `2591fde` |
| 11.09.2026 | `SI09` auf `sofort/2026-09-11-si09`, seit `4ec540b` auf `main`: `script-src` ohne `'unsafe-inline'`, Nonce je Anfrage an jedem Inline-Skript und am PayPal-SDK, 17 Handler-Attribute durch `data-`-Attribute ersetzt, drei neue Tests; kein Element, keine Klasse, keine Kennung verändert, 218/218 Tests grün laut Commit. Offen: Verhalten der Ersatzskripte im Browser, `'unsafe-eval'` (Alpine.js) und `'unsafe-inline'` im `style-src` | `28d1ca3` |
| 11.09.2026 | `PJ05`, `SI08`, `PJ11` auf `sofort/2026-09-11-pj05-und-2-weitere`, seit `0c18ea7` auf `main`: kritische Audit-Funde abgearbeitet oder mit Vermerk im Code begründet, `Subscriber` im Django-Admin; `CSP_MODUS`-Vorgabe `scharf`, PayPal-Hosts nach PayPals Angabe; jede Abhängigkeit mit `==` plus `requirements.lock`, Django 5.2.17. Kein Template berührt, 215/215 Tests grün laut Commits. Offen: Bezahlseite mit Browserkonsole nach dem Deploy, erster CI-Lauf mit 5.2.17 | `9ebad08`, `9a3226f`, `51cbf74` |
| 08.09.2026 | `GE23`, `GE25`, `IS19`: Antwortabsatz mit belegter Zahl auf jeder Inhaltsseite, konkrete Zahlen auf den fünf Seiten ohne, keine indexierbare Seite mehr unter 200 Wörtern im Inhaltsbereich — ohne eine Änderung am Aufbau, 215/215 Tests grün. Offen bleibt eine eigene Beschreibung je Einzelstück | `fd82efd`, `2b26108`, `b35f6e4` |
| 07.09.2026 | `SU04`: drei belegte Wissensbeiträge ohne Freigabevorbehalt (Bestellen und Bezahlen, Widerruf und Rücksendung, Konto und Daten); `/wissen/` damit indexierbar, Sitemap und llms.txt führen vier Wissensadressen | `d7d2e0b` |
| 02.09.2026 | Auflagen der Gegenprüfung (1, 3, 4, 5) umgesetzt; Lauf 4 damit „live-fertig", Zweig gepusht | `b750337`, `60555d0`, `270c5f9`, `511ffe5` |
| 02.09.2026 | Welle 9: Warenkorb-, Zahlungs-, Konto-, Zugriffsschutz- und Invarianten-Tests (174 → 215 Tests) | `87a4e85` … `2e9b051` |
| 02.09.2026 | Welle 8: CSP-Middleware (Report-Only), Canonical-Host-Middleware, `pruefe_seite` in `start.sh` | `3a9c2d3`, `6bd5eb4`, `50d68da` |
| 01.09.2026 | Wellen 1–7: Barrierefreiheit, Meta, Schema-Knoten, Inhalt, Wissensbereich, WebP, GZip, Gunicorn gthread | `65a1bd0` … `b0fba20` |
| 01.09.2026 | Lauf 3, Schritte 32–33: toter Code entfernt, Doku an den Code angeglichen, `LOGBUCH.md` angelegt | `c6e0cce`, `342f7fd` |
| 18.08.2026 | README im GitHub-Repo, letzte Railway-Auslieferung | `645842b` (Railway) |
| 15.07.2026 | Startseite PageSpeed und Politur; `CLAUDE.md` versioniert — **letzter Stand auf main** | `2fe90a0`, `2a17edd` |
| 13.07.2026 | Admin-Mail pro Seitenbesuch vollständig entfernt (Mail-Flut durch Bots) | `e58775a`, `26b6e72` |
