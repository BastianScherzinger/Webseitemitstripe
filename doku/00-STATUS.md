---
bereich: status
titel: Stand der Seite
stand: 2026-09-02
status: teilweise
fortschritt: 70
zusammenfassung: Gesamtstand 70,1 „Brauchbar" (02.09.2026); Verbesserungslauf 4 ist gepusht, aber nicht auf main — wartet auf die Betreiberin.
offen: 3
quellen: CLAUDE.md, DOCUMENTATION.md, LOGBUCH.md
---

# Stand — Luviq Universe

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
| **Technik** | Django (≥ 5.0, < 6.1), Docker (`python:3.11-slim`), PostgreSQL, Cloudinary (Bilder), Brevo (Mail), django-axes, Tailwind-CLI (kein npm im Repo) |
| **Live-Stand** | `main` @ `2a17edd` (15.07.2026); letzte Railway-Auslieferung 18.08.2026 (`645842b`, „docs: README zum Luviq-Universe-Onlineshop", SUCCESS) |
| **Ordner-Stand** | Zweig `cockpit/2026-09-01-verbesserung-4` @ `511ffe5` (02.09.2026), **63 Commits vor main**, gepusht, Arbeitsbaum sauber |
| **Zertifikat** | Let's Encrypt, TLS 1.3, gültig bis 30.11.2026 (Messung 02.09.2026: 89 Resttage); Alias eigenes Zertifikat bis 30.11.2026 |
| **Verfügbarkeit** | 24 h: 100 % (1.670 Messungen, Ø 1.029 ms) · 7 Tage: 99,92 % (3.935 Messungen, Ø 1.099 ms) — Messung 02.09.2026 |

## Ampel je Bereich

Aus den Köpfen der zehn Bereichsdateien (Stand 02.09.2026).

| Bereich | Status | Fortschritt | Zusammenfassung | Datei |
|---|---|---:|---|---|
| Wegweiser | vollständig | 100 | Elf Dateien nach Doku-Standard; die Original-Doku im Projektstamm bleibt die Detailquelle. | [README.md](README.md) |
| Technik | teilweise | 75 | Stack läuft stabil; im Zweig warten Testsuite (215 Tests), Prüfbefehl, CSP (Report-Only) und Canonical-Host; offen bleiben `ALLOWED_HOSTS='*'`, ungepinnte Abhängigkeiten und der Python-Versionsunterschied. | [10-TECHNIK.md](10-TECHNIK.md) |
| Design | vollständig | 90 | Dunkelbraun-Gold-Linie mit Glas-Karten steht und ist durch die Designwache eingefroren; offen sind Google-Schriften von fremdem Server und englische Restbeschriftungen. | [20-DESIGN.md](20-DESIGN.md) |
| Inhalte | teilweise | 40 | Live 14 URLs mit 1.557 Eigenwörtern (85 % dünne Seiten); der Zweig füllt neun Seiten mit Auskunft und bringt drei Wissensbeiträge, die bis zur Freigabe auf noindex stehen. | [30-INHALTE.md](30-INHALTE.md) |
| SEO / GEO | teilweise | 60 | SEO-Technik live solide (90), Inhalt 70, GEO 61; llms.txt, KI-Crawler-Regeln, WebPage/Person/Breadcrumb-Knoten und 301 auf www liegen fertig im Zweig, nicht live. | [40-SEO.md](40-SEO.md) |
| Local SEO | fehlt | 10 | Unternehmensprofil, Search Console und Bewertungen sind nirgends dokumentiert; NAP steht konsistent im Impressum und im Schema, live auf /kontakt/ aber noch Platzhalterdaten. | [50-LOCAL-SEO.md](50-LOCAL-SEO.md) |
| Ads | nicht zutreffend | — | Es gibt keine Google-Ads-Kampagne und kein Konto; Voraussetzungen für Shopping-/Suchanzeigen sind benannt. | [60-ADS.md](60-ADS.md) |
| Performance | teilweise | 70 | PageSpeed mobil 68 (Start) bis 89, LCP mobil 5,3 s auf der Startseite und 23 s auf /produkte/; der Zweig bringt WebP, GZip, Cache und gthread, live ist davon nichts. | [70-PERFORMANCE.md](70-PERFORMANCE.md) |
| Aufgaben | teilweise | 50 | Nächster Schritt ist der Merge des Zweigs nach main samt `CANONICAL_HOST`; danach Schriften lokal, Sprungmarke, Permissions-Policy, Danke-Seite; drei Freigaben liegen bei der Betreiberin. | [80-AUFGABEN.md](80-AUFGABEN.md) |
| Notizen | vollständig | 100 | Vier Namen für ein Projekt, PayPal statt Stripe, Zweig gegenüber main, zehn Widersprüche zwischen Quellen und Live-Seite. | [90-NOTIZEN.md](90-NOTIZEN.md) |

## Messung

<!-- messung:anfang -->
**Messung vom 02.09.2026** (Webagentur Scherzinger Overview, Regelstand 2026-09-02a) — **Gesamtstand 70,1 von 100**, Reifegrad „Brauchbar“. 230 von 244 Regeln an 14 URLs und 114 Dateien (23.859 Zeilen) geprüft.

| Bereich | Wert | Reifegrad |
|---|---:|---|
| Substanz & Reichweite | **40** | Rohbau |
| Vorlagen-Konformität | **60** | Brauchbar |
| GEO — KI-Sichtbarkeit | **61** | Brauchbar |
| Konversion | **62** | Brauchbar |
| SEO — Inhalt | **70** | Brauchbar |
| Performance & Core Web Vitals | **70** | Brauchbar |
| Recht & Vertrauen | **70** | Brauchbar |
| Code-Qualität & Projektreife | **74** | Brauchbar |
| Barrierefreiheit | **77** | Solide |
| Sicherheit | **87** | Solide |
| Betrieb & Auslieferung | **89** | Solide |
| SEO — Technik | **90** | Solide |

Keine Sperre greift.

Quelltext: 114 Dateien, **115 Befunde**, davon 2 kritisch und 36 wichtig.

Kritische Befunde:

- **Alle Domainvarianten landen auf einer Adresse** (`TS11`) — 0 von 1 Nebenadressen landen auf der Hauptadresse — offen: https://luviq-alsfeld.com
- **Umfang passt zur Aufgabe der Seite** (`IS18`) — Unter dem Umfang, den ihre Aufgabe verlangt: 7 von 7 Seiten — / (390/700 W), /produkte/ (62/600 W), /produkt/custom-hoodie-mit-print/ (26/600 W), /produkt/custom-print-hoodie-1/ (25/600 W), /produkt/custom-pants-sold/ (25/600 W) … (+2)
- **Kein nennenswerter Anteil dünner Seiten** (`IS19`) — 85% der Seiten sind dünn (11 von 13): /produkte/ (62 W), /kontakt/ (91 W), /datenschutz/ (185 W), /agb/ (179 W), /gaestebuch/ (70 W) … (+6)
- **Wissensinhalte vorhanden** (`SU04`) — 0 Wissensseiten, Zielgröße 3 — es gibt keinen einzigen Ratgeberbereich
- **Alle Formularfelder sind beschriftet** (`BF05`) — 5 von 5 Feldern ohne Beschriftung: / (1), /kontakt/ (4) (Spamfallen sind ausgenommen)
- **Die Datenschutzerklärung nennt die tatsächlich eingebundenen Dienste** (`RE06`) — 3 von 3 eingebundenen Diensten stehen nicht in der Datenschutzerklärung: cdn.jsdelivr.net, fonts.googleapis.com, maps.google.com
- **Keine Google-Schriften von fremden Servern nachgeladen** (`RE07`) — 13 von 13 Seiten laden Google-Schriften von fremden Servern: fonts.googleapis.com, https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700 · betroffen: /, /produkte/, /kontakt/ … (+10)
- **Antwort zuerst: der erste Absatz beantwortet die Frage** (`GE23`) — 1 von 13 Seiten beginnen mit einer zitierfähigen Antwort — schwach: / (weder Definition noch Zahl), /produkte/ (nur 4 Wörter), /kontakt/ (weder Definition noch Zahl), /datenschutz/ (weder Definition noch Zahl), /agb/ (weder Definition noch 
- **Die Telefonnummer ist anklickbar und steht auf jeder Seite** (`KV01`) — 1 von 13 Seiten mit tel:-Link (Startseite: nein) — ohne: /, /produkte/, /datenschutz/, /agb/, /gaestebuch/ … (+7)
- **Genug eigener Inhalt insgesamt** (`SU02`) — 1.557 Eigenwörter über 13 Seiten, Zielgröße 12.000 (von 2.434 Wörtern Gesamttext); die umfangreichsten Seiten: / (390 W), /liefergebiet/ (259 W), /ueber_uns/ (194 W)
- **Das Projektgerüst liegt an der vereinbarten Stelle** (`VL01`) — Projektgerüst: 1 von 6 Gerüst-Merkmalen erfüllt — es fehlt: config/settings.py, config/urls.py, config/wsgi.py, apps/-Paket statt Wurzelmodule, reine Datenmodule (data/)
- **Es gibt keinen kritischen Datei-Befund** (`PJ05`) — 2 kritische Befunde: mainweb/settings.py:59 ALLOWED_HOSTS steht auf '*', shop1/middleware.py:218 Ausnahme wird verschluckt
- … und 3 weitere
<!-- messung:ende -->

**Letzter bekannter Stand** (Messung vom 02.09.2026, Regelstand 2026-09-02a): Gesamt **70,1 — „Brauchbar"**, 230 von 244 Regeln gemessen, 123 bestanden, 14 nicht messbar, keine Sperre. Gemessen wurde die **Live-Seite (main)**, der Code-Audit lief über den **lokalen Ordner (Zweig)** — die Zahl mischt also zwei Stände (siehe [90-NOTIZEN.md](90-NOTIZEN.md)).

| Bereich | Wert | Reifegrad |
|---|---:|---|
| SEO — Technik | 89,5 | Solide |
| Betrieb & Auslieferung | 88,6 | Solide |
| Sicherheit | 86,7 | Solide |
| Barrierefreiheit | 77,3 | Solide |
| Code-Qualität & Projektreife | 74,0 | Brauchbar |
| Recht & Vertrauen | 70,5 | Brauchbar |
| SEO — Inhalt | 70,4 | Brauchbar |
| Performance & Core Web Vitals | 70,4 | Brauchbar |
| Konversion | 62,1 | Brauchbar |
| GEO — KI-Sichtbarkeit | 61,3 | Brauchbar |
| Vorlagen-Konformität | 60,1 | Brauchbar |
| **Substanz & Reichweite** | **39,8** | **Rohbau** |

## Die drei wichtigsten offenen Punkte

1. **Den Zweig `cockpit/2026-09-01-verbesserung-4` nach `main` bringen** und in Railway `CANONICAL_HOST=www.luviq-alsfeld.com` setzen. Damit gehen auf einen Schlag live: 215 Tests, `pruefe_seite`, llms.txt, 301 für `luviq-alsfeld.com` (TS11), Inhalt auf neun Seiten, WebP-Bilder, GZip, Datenschutzerklärung mit allen Diensten (RE06), echte Kontaktdaten statt „Musterstraße 123, Berlin" auf /kontakt/. Der Rest des Laufs braucht **keine** Antwort der Betreiberin (Logbuch, Auflage 3).
2. **Freigabe der Betreiberin** für die drei Wissensbeiträge (Pflegeangaben 30 °C / kein Trockner / kein Weichspüler / Bügeln von links; Faustregel „fünf Zentimeter sind eine ganze Grösse"). Danach je Beitrag `'freigegeben': True` in `shop1/views/wissen.py` — Sitemap, llms.txt und robots-Meta folgen von selbst. Bis dahin bleibt Substanz bei 40 (SU04, SU01, SU07).
3. **Google-Schriften lokal hosten** (RE07, 13 von 13 Seiten laden Inter/Outfit von `fonts.googleapis.com`) — der einzige kritische Rechtsbefund, den der Zweig **nicht** behebt; `base.html` Zeile 172–175.

## Zuletzt erledigt

| Datum | Was | Beleg |
|---|---|---|
| 02.09.2026 | Auflagen der Gegenprüfung (1, 3, 4, 5) umgesetzt; Lauf 4 damit „live-fertig", Zweig gepusht | `b750337`, `60555d0`, `270c5f9`, `511ffe5` |
| 02.09.2026 | Welle 9: Warenkorb-, Zahlungs-, Konto-, Zugriffsschutz- und Invarianten-Tests (174 → 215 Tests) | `87a4e85` … `2e9b051` |
| 02.09.2026 | Welle 8: CSP-Middleware (Report-Only), Canonical-Host-Middleware, `pruefe_seite` in `start.sh` | `3a9c2d3`, `6bd5eb4`, `50d68da` |
| 01.09.2026 | Wellen 1–7: Barrierefreiheit, Meta, Schema-Knoten, Inhalt, Wissensbereich, WebP, GZip, Gunicorn gthread | `65a1bd0` … `b0fba20` |
| 01.09.2026 | Lauf 3, Schritte 32–33: toter Code entfernt, Doku an den Code angeglichen, `LOGBUCH.md` angelegt | `c6e0cce`, `342f7fd` |
| 18.08.2026 | README im GitHub-Repo, letzte Railway-Auslieferung | `645842b` (Railway) |
| 15.07.2026 | Startseite PageSpeed und Politur; `CLAUDE.md` versioniert — **letzter Stand auf main** | `2fe90a0`, `2a17edd` |
| 13.07.2026 | Admin-Mail pro Seitenbesuch vollständig entfernt (Mail-Flut durch Bots) | `e58775a`, `26b6e72` |
