---
bereich: seo
titel: SEO und GEO
stand: 2026-11-24
status: vollständig
fortschritt: 98
zusammenfassung: Stand 02.10.2026: Wissensbereich frei und indexierbar (17 Sitemap-URLs), llms.txt und llms-full.txt, Feed, sameAs mit Instagram, TikTok und Google-Profil, @id-Schema mit speakable, Apex-301; gemessen SEO-Inhalt 94, SEO-Technik 99, GEO 100. Offen: Indexierung beantragen (Bastian, TS46), zwei Entscheidungen (Stückseiten noindex, Pfad /ueber_uns/) und die Alt-Texte je Stück (später).
offen: 4
quellen: GOOGLE_SEO_GUIDE.md, LOGBUCH.md, DOCUMENTATION.md, shop1/views/legal.py, shop1/seiten_stand.py, shop1/indexnow.py, templates/base.html
---

# SEO und GEO — Luviq Universe

*Woran sich der Fortschritt bemisst: am Mittel der drei gemessenen Bereichswerte **SEO-Technik, SEO-Inhalt und GEO** des Laufs vom 02.10.2026 (Regelstand `2026-10-02e`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße. Nennt die Datei zusätzlich einen Planfortschritt (etwa „52 von 73 Aufgaben“), steht der im Abschnitt „Stand“ — er misst den Plan, nicht die Seite.*

> **Stand 02.10.2026 (geprüft, abends):** `main` = `origin/main` = `7ae67ab` und live. Alle Arbeitszweige des Tages (`fix/2026-10-02-luviq-fertig`, `-rest`, `-luisa`, `-recht`, `-wissen`, `fix/2026-10-02d-standard`) sind gemergt (`git log origin/main..<zweig>` leer, `git branch -r --no-merged origin/main` leer); die GitHub-Prüfungen auf `main` sind grün (Lauf 37040107996, 02.10.2026). Live belegt am 02.10.2026 (curl): Sitemap mit 17 Adressen samt der drei Wissensbeiträge, `/llms-full.txt` 200, „Aktualisiert am …“ (`<time>`) auf den Wissensbeiträgen (GE47), `Permissions-Policy` im Kopf, `/health/` 200, Apex 301 auf www. Wo unten „Zweig“ oder „nicht gemergt“ steht, ist das **Verlauf** des jeweiligen Tages und gilt seit dem Merge als live, sofern der Satz nichts anderes sagt. Der **Verkauf ist aus** (`VERKAUF_AKTIV` ohne Variable = aus: Marke im Aufbau, Archiv statt Shop); nach Angabe des Betreibers ist **kein Gewerbe angemeldet** — die Seite nennt deshalb keine Unternehmensangaben (Impressum nach § 5 DDG nur mit Luisa Brehler als Person, Alsfeld, E-Mail).

> **23.10.2026 Schub 3:** Weiterlesen-Links zwischen den freigegebenen Wissensbeiträgen, Öffnungszeiten-Antwort auf `/liefergebiet/` (echte Suchanfrage), Entwurf `/wissen/so-entsteht-dein-motiv/` (noindex bis Freigabe). Einzelheiten `LOGBUCH.md`.

## SEO-Konzept, Fassung 24.11.2026 (nach Search-Console-Auswertung)

*Grundlage: Search Console, Property `https://www.luviq-luebeck.com/`, Abruf 24.11.2026 über die Search-Console-API (lesend; Chrome war nicht verbunden), Zeitraum 28.10. bis 22.11.2026 (die Domain ist erst seit 28.10. in den Daten; „16 Monate“ und „3 Monate“ liefern daher dasselbe). Zusätzlich die Vorgänger-Domain `luviq-alsfeld.com` (02.07. bis 22.11.2026). Rohdaten: `Buero\berichte\2026-11-24_LUVIQ-SEO\gsc_*.csv`. Bericht: `…\BERICHT.md`.*

### 1. Lage in Zahlen (nur belegt)

- **luviq-luebeck.com:** 8 Klicks, 363 Impressionen in 26 Tagen (Tagesschnitt zuletzt 21 bis 33 Impressionen, steigend; Oktober 14 gesamt). Klickrate gesamt 2,2 %, mittlere Position etwa 8. Handy 278 von 363 Impressionen. Deutschland 262, Österreich 47, Schweiz 33.
- **Alle 20 Sitemap-Adressen sind indexiert** („Gesendet und indexiert“, URL-Prüfung 24.11.), Sitemap ohne Fehler und Warnungen, zuletzt gelesen 23.11. Es gibt keinen Indexierungsfehler zu beheben.
- **Grenze der Daten:** Google nennt nur für 52 der 363 Impressionen die Suchanfrage (Datenschutzfilter bei seltenen Anfragen). Die Seitenzahlen sind vollständig, die Anfragezahlen nur ein Ausschnitt. Aussagen zu einzelnen Begriffen sind deshalb Hinweise, keine Messung der Nachfrage.
- **luviq-alsfeld.com (alt):** 64 Klicks, 1.973 Impressionen (Juli bis November), davon allein „second hand alsfeld“ 468 Impressionen, 21 Klicks, Position 2,8, dazu „second hand alsfeld öffnungszeiten“, „second hand in der nähe“, „geschäfte“. Das ist **Ladensuche**. Luviq hat keinen Laden (llms.txt, Über-uns); diese Nachfrage ist verloren und wird **nicht** zurückgeholt. Seit dem Umzug ist alsfeld-seitig nur noch Auslauf (November 72 Impressionen).

### 2. Wofür Luviq schon angezeigt wird („vorgeschlagen“)

| Seite | Impr. | Klicks | Klickrate | Pos. | Anfragen (soweit genannt) |
|---|---:|---:|---:|---:|---|
| `/wissen/bleach-painting-anleitung/` | 131 | 2 | 1,5 % | 9,3 | kleidung mit bleiche bemalen (9), mit bleiche auf textilien malen (9,3), t-shirt bleichen/bleaching (23 bis 42), textilien bleichen (54), mit chlor malen |
| `/wissen/bleach-painting/` | 73 | 0 | 0 % | 7,2 | was ist bleach (5,3), was heißt bleach (10), paint with bleach (18), bleaching paint (20) |
| `/wissen/pflege-handbemalte-kleidung/` | 36 | 0 | 0 % | 6,0 | (keine genannt) |
| `/wissen/upcycling-mode-second-hand-vintage/` | 33 | 1 | 3 % | 7,1 | (keine genannt) |
| `/` (Marke) | 30 | 4 | 13 % | 3,1 | luviq (Pos. 2,7) |
| `/?utm_source=google&utm_medium=organic&utm_campaign=gbp` | 32 | 0 | 0 % | 9,8 | second hand alsfeld, „in der nähe“ (Profil-Link, Ladensuche) |
| `/produkte/` | 16 | 0 | 0 % | 5,5 | luviq |
| `/kontakt/` | 10 | 0 | 0 % | 7,2 | luviq |
| `/produkt/engel-shirt-handgebleicht/` | 5 | 0 | 0 % | 9,2 | luviq |
| `/motiv-anfragen/` | 0 | 0 | | | nicht angezeigt |

Befunde daraus:
1. **Die Ratgeber tragen die Sichtbarkeit**, nicht die Verkaufsseiten. Genau dort liegt eine Marktlücke, die zu Luviq passt: Wer „mit Bleiche bemalen“ sucht, ist die Zielgruppe der handgebleichten Stücke.
2. **Hebel Platz 5 bis 20 mit Impressionen:** Anleitung (131, Pos. 9,3), Bleach Painting (73, Pos. 7,2), Pflege (36, Pos. 6), Upcycling (33, Pos. 7,1). Zusammen 273 von 363 Impressionen bei 3 Klicks. Wer von Position 7 bis 9 auf 3 bis 5 kommt, verdoppelt bis verdreifacht die Klicks; wer im Snippet besser antwortet, gewinnt schon vorher.
3. **Marke:** „luviq“ steht auf Platz 2,7 (Startseite). Kein Handlungsbedarf außer der Profil-Verlinkung (Punkt 5).
4. **Verkaufsintention fehlt vollständig:** keine Anfrage mit „kaufen“, „bestellen“, „handbemalt“, „Bleach Shirt“ in den genannten Daten. Das Engel-Shirt wird kaum gezeigt (5 Impressionen). Es ist ein Aufbau-, kein Optimierungsproblem (Seite braucht Zugang über Ratgeber, Verlinkung, Bilder, Backlinks).
5. **Profil-Link mit UTM:** Das Google-Profil verlinkt auf `/?utm_source=google…`; Google zählt die Variante getrennt (32 Impressionen, Pos. 9,8) und teilt damit die Sichtbarkeit der Startseite. Ändern nur durch Luisa/Bastian im Profil (Link ohne Parameter).

### 3. Zielbegriffe nach Beleg (Seite × Suchanfrage)

| Seite | Hauptbegriff | Nebenbegriffe | Beleg | Maßnahme |
|---|---|---|---|---|
| Anleitung | t-shirt mit bleiche bemalen | bleach painting anleitung, t-shirt bleichen, textilien bemalen | GSC-Anfragen Pos. 9 bis 54 | Title und Beschreibung umgestellt (24.11.) |
| Bleach Painting | was ist bleach painting | bleichmalerei, was ist bleach, paint with bleach | GSC „was ist bleach“ Pos. 5,3 | Beschreibung beginnt mit Frage und deutschem Begriff (24.11.) |
| Pflege | handbemaltes shirt waschen | bleach shirt waschen | Impressionen Pos. 6, keine Anfrage genannt | Titel bleibt; Messen, dann ggf. Antwort-Snippet |
| Upcycling | upcycling mode second hand | | Impressionen Pos. 7,1 | Titel bleibt; messen |
| Startseite | luviq, handbemalte shirts lübeck | | Marke Pos. 2,7 | unverändert |
| Stückseite Engel-Shirt | handbemaltes shirt, bleach shirt, engel shirt | | keine Nachfrage in GSC | Vorschlag: Zugang über Ratgeber (Abschnitt 6) |
| Motiv anfragen | shirt bemalen lassen, eigenes motiv | | 0 Impressionen | Vorschlag: Titel auf kurzen Nutzen kürzen („Shirt bemalen lassen: eigenes Motiv anfragen | Luviq“, 52 Zeichen); Test `test_direktkauf_texte` pinnt den alten Titel, daher nur mit Bastians OK |

Nicht verfolgt: Ladensuchen („second hand alsfeld“, „in der nähe“, „öffnungszeiten“): kein Laden, falsche Erwartung, verschlechtert die Klickrate.

### 4. Prioritäten nach Hebel

1. **Snippets der vier Ratgeber mit Impressionen** (Title/Meta). Erledigt für Anleitung und Bleach Painting; Pflege und Upcycling erst nach Messung (keine genannten Anfragen, Raten wäre erfunden).
2. **Beschreibungen der fünf Archivstücke** waren mitten im Satz abgeschnitten („Schwarzer Hoodie mit schmalem – Nº 004 …“). Behoben (24.11.). Betrifft alle fünf Stückseiten, indexiert.
3. **llms.txt:** Stückbeschreibung des Engel-Shirts brach mitten im Satz ab („… Jedes Shirt dieser“). Behoben (24.11.).
4. **Titel `/motiv-anfragen/`** hat 68 Zeichen (Google kürzt ab etwa 60 bis 65), die Seite hat noch keine Impressionen. Kürzung als Vorschlag, nicht umgesetzt.
5. **Profil-Link ohne UTM** (Bastian/Luisa, Punkt 2.5).

### 5. On-Page, interne Verlinkung, Snippet, GEO (Regeln)

- Pro Seite ein Hauptbegriff im Title (≤ 60 Zeichen, Marke am Ende), Beschreibung 120 bis 160 Zeichen mit Antwort zuerst, nur Aussagen, die auf der Seite stehen.
- Interne Links: Die Ratgeber mit Impressionen müssen von Seiten mit Stärke erreichbar sein (Startseite, Wissen-Übersicht, Stückseite, Über uns). Bestand: Anleitung wird von Übersicht, Bleichfleck-Ratgeber und Bleach-Painting-Ratgeber verlinkt; die Stückseite des Engel-Shirts verlinkt nur „Was ist Bleach Painting?“ (`produkt_detail.html`, Bedingung `bleach_artikel`). **Vorschlag:** dort zusätzlich die Anleitung verlinken. Das ist ein neues `<a>` und verlangt eine Nachführung der Designwache (`aufbau_referenz.json`), daher nicht ungefragt.
- Schema: Organization, WebSite, WebPage, Person, BreadcrumbList, Article + FAQPage (Ratgeber), VisualArtwork (Archiv), Service. Alles gültig lesbar. Kein `Product`/`Offer` beim Anfrage-Shop, Absicht.
- GEO: `llms.txt` und `llms-full.txt` stehen auf dem Anfrage-Stand; robots.txt erlaubt die KI-Crawler. Die Frage-Antwort-Form der Ratgeber (h2 als Frage, Antwort im ersten Absatz) bleibt Standard.

### 6. Neue Seiten, nur Vorschlag (warten auf Bastians OK; Bremse seo-geo)

Höchstzahl der indexierbaren Seiten beachten; derzeit 20.

| Vorschlag | Begründung | Beleg | Risiko |
|---|---|---|---|
| Ratgeber „T-Shirt bleichen: Unterschied zwischen Bleichen und Bleach Painting“ | Anfragen „t-shirt bleichen/bleaching“ (Pos. 23 bis 42) treffen heute die Anleitung, die sie nur halb beantwortet | GSC | Kannibalisierung mit der Anleitung; erst bauen, wenn die Anleitung nach der Titelumstellung nicht steigt |
| Keine Ortsseite Lübeck | Kein Laden, keine Nachfrage belegt | llms.txt „Einen Laden … gibt es nicht“ | Überwucherung |
| Seite „Engel-Shirt“-Ratgeber / Kollektion | fehlende Verkaufsintention; erst Bilder und Material von Luisa nötig | | Dünn ohne Material |

Bis zur nächsten Messung keine weiteren neuen Seiten.

### 7. Offpage und Backlinks (Vorschlag)

- Instagram und TikTok `luviq.archive`: Link in der Bio auf die Startseite **ohne UTM**; Beiträge zum Bleach-Painting mit Link auf die Anleitung (Verhalten der Zielgruppe: Bleach-Painting-Anleitungen laufen dort).
- Google-Unternehmensprofil: Website-Link ohne Parameter, Beschreibung auf handbemalte Shirts aus Lübeck (online) statt Second-Hand-Laden; Profilkategorie prüfen (Ladensuche-Treffer „second hand alsfeld“ stammen vom Profil).
- Verzeichnisse und Pinterest nur, wo das Motiv zeigbar ist (Bilder von Luisa); jeder Eintrag mit sauberem NAP wie im Impressum.
- Frühere Backlink-Inventur: `Buero\berichte\2026-10-29_LUVIQ-BACKLINKS-LUISA.md`.

### 8. Messplan

| Datum | Was | Maßstab |
|---|---|---|
| 01.12.2026 | Änderungen live? URL-Prüfung der geänderten Seiten, Indexierung beantragen (Liste im Bericht) | Status „indexiert“, Crawl-Datum nach Livegang |
| 08.12.2026 | Anleitung und Bleach Painting: Position, Klickrate gegen Stand 24.11. (Anleitung 9,3 / 1,5 %; Bleach 7,2 / 0 %) | Klickrate > 3 % oder Position < 8 |
| 22.12.2026 | Gesamt: Impressionen je Woche, Anfragen mit „bleiche“, erste Verkaufsbegriffe | Impressionen > 600 in 4 Wochen |
| 12.01.2027 | Entscheidung zu neuen Seiten (Abschnitt 6) | wenn die Anleitung stagniert, Ratgeber „Bleichen vs. Bleach Painting“ |

Dieselbe Abfrage wie am 24.11.: Search-Console-API, siehe Bericht.

---

*Ab hier der frühere Stand (Verlauf bis 04.11.2026); wo er dem Konzept oben widerspricht, gilt das Konzept.*

## Stand

**Es gibt keine SEO-Kampagne** wie bei Rümpelwerk, WVM-IT oder RTC-Service und keinen SEO-Plan mit
Nummern. Was es gibt: `GOOGLE_SEO_GUIDE.md` (Grundausstattung + Aufgaben der Betreiberin) und den
**Verbesserungslauf 4** (Wellen 3–6 SEO/GEO/Inhalt), der seit dem Merge auf `main` live ist.

| Bereich (Messung 01.10.2026, Regelstand 2026-09-28a) | Wert | Reifegrad |
|---|---:|---|
| SEO — Technik | 98 | Referenz |
| SEO — Inhalt | 83 | Solide |
| GEO — KI-Sichtbarkeit | 79 | Solide |
| Substanz & Reichweite | 44 | Lückenhaft |

*Zum Vergleich Messung 02.09.2026 (anderer Regelstand, nicht vergleichbar): 89,5 / 70,4 / 61,3 / 39,8.*

**Sichtbarkeit: seit dem 03.09.2026 messbar.** Die Property `sc-domain:luviq-alsfeld.com` ist geprüft,
eingetragen und per OAuth angebunden (siehe [50-LOCAL-SEO.md](50-LOCAL-SEO.md)); Klick- und Positionsdaten
liegen aber nicht ausgewertet vor (Stand 01.10.2026: keine Auswertung dokumentiert).

**Ziel-Suchbegriffe** (`meta name="keywords"` in `base.html`, laut `GOOGLE_SEO_GUIDE.md` massgeblich):
„Luviq", „Luviq Universe", „Second Hand Mode Alsfeld", „Vintage Mode Hessen", „handbemalte Kleidung
kaufen", „Upcycling Mode Deutschland", „1 of 1 Unikate". Der früher genannte Begriff „railway hosting
luviq" war falsch und ist gestrichen.

## Technik

**Live-Stand 01.10.2026 (abgerufen):**

| Baustein | Stand |
|---|---|
| `robots.txt` | 200; sperrt Konto-, Kasse- und Admin-Pfade, regelt 14 `User-agent`-Blöcke (darunter KI-Crawler ausdrücklich erlaubt, `GE02`), nennt `Sitemap: https://www.luviq-alsfeld.com/sitemap.xml` |
| `sitemap.xml` | 200, **17 URLs** (abgerufen 02.10.2026) mit `lastmod` (Daten zwischen 11.05. und 27.09.2026); **Bild-Auszeichnung seit TS19 (`36c0741`, 01.10.2026)**: Startseite mit Titelbild und fünf Entstehungsbildern, `/produkte/` und die Produktseiten mit den Stückbildern (16 `image:image`-Blöcke gesamt); Seiten ohne Inhaltsbild bleiben ohne Bild. Impressum, AGB und Danke-Seiten stehen nicht darin; der Wissensbereich (Übersicht und drei Beiträge) steht seit der Freigabe vom 02.10.2026 (`3073388`) darin |
| `llms.txt` | 200: Antwortabsatz („Marke im Aufbau … noch kein Verkauf“), Eckdaten (Luisa Brehler, Anschrift, E-Mail, Instagram `luviq.archive`, TikTok, Google-Profil), Seitenliste, Archiv der Stücke; **`llms-full.txt` gibt es seit `bf8882e` (200, abgerufen 02.10.2026)** |
| `/feed/` (RSS) | 200, die freigegebenen Wissensbeiträge (seit `3073388` drei; abgerufen 02.10.2026) |
| Canonical / Host | Canonical je Seite; **Apex `luviq-alsfeld.com` → 301 auf `www`** (`TS11` live behoben) |
| 404 | eigene Seite im Stil der „Nachtausgabe“ („Seite nicht gefunden – Luviq Universe“, `TS20`) |
| Schutzköpfe | HSTS (1 Jahr, preload), CSP scharf (mit `'unsafe-eval'`, `'unsafe-inline'` in `style-src`), `X-Frame-Options: DENY`, `nosniff`, Referrer-Policy, COOP; **keine `Permissions-Policy`** (`SI07`) |
| IndexNow | aus (`/indexnow-schluessel.txt` → 404, `INDEXNOW_KEY` nicht gesetzt) |
| Cookies | beim Abruf der Startseite nur `csrftoken` (Django-CSRF, `SameSite=Lax`, `Secure`); kein Analyse- oder Werbecookie |

**Verlauf: Tabelle der Messung vom 02.09.2026** (Spalte „Live“ = damaliges `main`; Spalte „Zweig“ = was seit den Merges live ist):

| Baustein | Live (main, 02.09.2026) | Zweig |
|---|---|---|
| `robots.txt` | 200; sperrt `/shop-admin/`, `/profil/`, `/warenkorb/`, `/checkout/`, `/payment/`, `/verify/`, `/login/`, `/logout/`, `/register/`, `/password-reset/`, `/reset/`, `/resend-verification/`, `/delete-account/`; **Sitemap-Zeile vorhanden**; keine KI-Crawler genannt (GE02) | zusätzlich `Allow: /` und **13 Antwort-Crawler namentlich zugelassen** (u. a. GPTBot, PerplexityBot, ClaudeBot, Google-Extended, Applebot-Extended, CCBot, meta-externalagent, Bytespider) |
| `sitemap.xml` | 200, 14 URLs, `lastmod` nur bei 5 Produkten (2 Daten: 14.06./11.05.2026), Bild-Auszeichnung bei 5 (TS16, TS19); eine Klasse im Code (VL07) | `lastmod` für alle statischen Seiten aus dem Register `seiten_stand.py` (`2026-09-01`, die drei SU04-Beiträge `2026-09-07`; seit IS18, `1a5f36b`, `home`, `produkte` und `wissen` `2026-09-11`; seit GE43, `5928144`, `wissen`, `wissen_bestellen`, `wissen_widerruf` und `wissen_konto` `2026-09-17`; seit KV05, `9cd641f`, auch `kontakt` `2026-09-17`); `/wissen/` und die drei belegten Beiträge stehen drin, die drei unbestätigten erst nach Freigabe; `/kontakt/danke/` (Zweig KV07) bewusst weder hier noch in `llms.txt`, Test in `test_formulare`; 15 min Cache |
| `llms.txt` | **404** | vorhanden: Antwortabsatz (Ort, PLZ 36304, Versandzeiten), Eckdaten (Betreiberin, Anschrift, E-Mail, Instagram, Zahlungsarten, § 19), Seitenliste, Abschnitt Wissen mit Übersicht und den drei belegten Beiträgen (die drei unbestätigten erst nach Freigabe); seit GE32 (Zweig 17.09.) zusätzlich die Zeile `Feed: …/feed/` unter der `Sitemap:`-Zeile; 15 min Cache. `llms-full.txt` gibt es nicht (GE31) |
| `/feed/` (RSS) | gibt es nicht | **Zweig 17.09. (GE32, `22fea97`, nicht gemergt):** RSS-Feed der **freigegebenen** Wissensbeiträge — Klasse `WissenFeed` (`django.contrib.syndication.views.Feed`) in `shop1/views/wissen.py`, Route `feed/` in `urls.py`, in `views/__init__.py` re-exportiert. Je Eintrag `title` = `titel`, `description` = `kurz`, `link` = `reverse(url_name)`, `pubDate` = `veroeffentlicht` — alles aus dem Register `WISSEN_BEITRAEGE`, kein Datei- oder Baudatum; neuester zuerst, Zeitstempel mit `timezone.make_aware` in Berliner Zeit. Dieselbe Menge wie Sitemap und `llms.txt`: ein gesperrter Beitrag steht in keiner der drei Aufstellungen. Kein `cache_page`. Fünf Tests in `test_seo` (`FeedTest`) |
| Canonical | Canonical-Tag je Seite; **Apex `luviq-alsfeld.com` antwortet 200 ohne 301** (TS11, kritisch) | `CanonicalHostMiddleware`: 301 mit vollem Pfad und `https` für die www-Nebenvariante von `CANONICAL_HOST`; **wirkt erst mit gesetzter Variable in Railway** |
| Meta | Titel 7 von 13 in 30–65 Zeichen (IS02), Beschreibungen 5 von 13 in 110–175 (IS09), 4 mit Aufforderung (IS11), 2 Titel mit Ort/Nutzen (IS06), 1 Titel doppelt (IS03), 4 Seiten teilen Beschreibungen (IS10), Marke am Ende bei 9 (IS07) | Beschreibungen aller neun Inhaltsseiten 157–171 Zeichen mit Aufforderung; Ortsbezug im automatischen Produkttitel; Produkt-Meta auf 60/160 begrenzt; Tests in `test_seo` |
| Open Graph / Twitter | vorhanden (`GOOGLE_SEO_GUIDE.md`, VL06: 80 von 91 Kopf-Bausteinen) | unverändert; og-Bild bleibt JPEG |
| Überschriften | 10 von 13 Seiten springen `h1 → h3` (IS14, BF15) | Wissensseiten ohne Sprung; Bestandsseiten **unverändert** (Designwache) |
| 404 | echter 404, aber Standardseite mit 13 Wörtern (TS20, BT05) | **Zweig 27.09.2026 (Paket 499, nicht gemergt):** eigene `templates/404.html` im „Nachtausgabe"-Stil (`lv-danke`, `noindex, follow`) statt Djangos eingebauter Standardantwort — Django findet sie automatisch (`TEMPLATES.DIRS`), kein `handler404` nötig |
| Schutzköpfe | HSTS (1 Jahr, preload), nosniff, `X-Frame-Options: DENY`, Referrer-Policy; **keine CSP, keine Permissions-Policy** (VL04, SI08, SI07) | CSP als Report-Only-Kopfzeile (`CSP_MODUS`) |
| GZip | nicht dokumentiert für main | `GZipMiddleware` für dynamische Antworten |
| IndexNow | gibt es nicht | **Zweig 18.09. (PJ13, `0b94d8e`, nicht gemergt), aus bis `INDEXNOW_KEY` in Railway gesetzt ist.** `shop1/indexnow.py`: das Signal `produkt_an_indexnow` (`signals.py`, `post_save`/`post_delete` von `Produkt`) meldet die Produktadresse und `/produkte/` nach dem Abschluss der Transaktion an `api.indexnow.org` — neue, geänderte, verkaufte (von `paypal_capture` auf inaktiv gesetzte) und gelöschte Stücke; nicht beim `loaddata`. Host und `keyLocation` kommen aus `SITE_URL`, die Schlüsseldatei liefert `/indexnow-schluessel.txt` (Route `indexnow_schluessel`, ohne gültigen Schlüssel 404). Gesendet wird in einem Pool mit einem Platz, 10 s Zeitgrenze; ein Fehlschlag steht nur im Log, die Sitemap bleibt der Rückweg. Bei `DEBUG` aus. Google nimmt nicht teil. Vier Tests in `test_seo` (`IndexNowTest`); einen echten Aufruf gab es nie |

**Strukturierte Daten (JSON-LD):**

| Knoten | Wo | Stand |
|---|---|---|
| `Organization`/`ClothingStore` mit `PostalAddress`, `areaServed` (Hessen, DE, 18 Städte), `OfferCatalog` mit drei `Product`/`Offer`, `sameAs` Instagram, dazu ein eigener `location`-Knoten vom Typ `Place` mit `PostalAddress` und `GeoCoordinates` | `base.html` | live; `geo` (`GeoCoordinates`) steht seit Zweig 28.09.2026 (GE22, Nachbesserung Paket 542) an einem eigenen `location`/`Place`-Knoten, unabhängig von `VERKAUF_AKTIV` gültig — `geo` direkt am `Organization`/`ClothingStore`-Knoten war eine erste, von der Gegenprüfung zu Recht verworfene Fassung, weil die Eigenschaft dort nach schema.org nicht gültig ist, sobald ohne Verkauf nur `"Organization"` ausgegeben wird; `sameAs` nur 1 Verweis (GE11, am 11.09. und 12.09.2026 nicht möglich — keine weitere Profiladresse im Projekt); **Telefon fehlt** — es gibt keine (GE09, VL10) |
| `WebSite` | `base.html` | live |
| `ImageObject` (Logo) | `base.html` | live |
| `ItemList` (aktuelle Produkte) | `index.html` | live; eigene `@id` (`#archiv`) seit Zweig 27.09.2026 (GE07) |
| `Product` + `Offer` + `Brand`, `BreadcrumbList` | `produkt_detail.html` | live (5 von 6 Leistungsseiten mit Offer, GE13; `/produkte/` ohne); seit Zweig 27.09.2026 (GE07) eigene `@id` (`#product`), `brand`/`seller` verweisen per `@id` auf `#organization` statt eines anonymen Zweitknotens; seit Paket 517 auch `Offer` (`#offer`) und `BreadcrumbList` (`#breadcrumb`) mit eigener `@id` |
| `LocalBusiness` mit `@id #organization` | `impressum.html` | live (`@id` Zweig) |
| `ContactPage`, `ContactPoint`, `FAQPage` (Versand, Erreichbarkeit) | `kontakt.html` | Zweig; seit 27.09.2026 (GE07) je eigene `@id` (`#contactpage`, `#faq`); seit Paket 517 auch die `BreadcrumbList` (`#breadcrumb`) |
| `FAQPage` (Liefergebiet/Herkunft) | `liefergebiet.html` | Zweig; seit 27.09.2026 (GE07) eigene `@id` (`#faq`); seit Paket 517 auch die `BreadcrumbList` (`#breadcrumb`) |
| `CollectionPage` + je `Product`/`Offer`, `BreadcrumbList` | `produkte.html` | Zweig; seit 27.09.2026 (GE07) eigene `@id` (`#collection`) und je `Product` eine `@id` (`#product`), `provider`/`brand` verweisen per `@id` auf `#organization` statt eines anonymen Zweitknotens; seit Paket 517 auch je `Offer` (`#offer`) und die `BreadcrumbList` (`#breadcrumb`) |
| `AboutPage`, `Person` (Luisa), `BreadcrumbList` | `ueber_uns.html` | Zweig; seit 27.09.2026 (GE07) eigene `@id` (`#aboutpage`); seit Paket 517 auch die `BreadcrumbList` (`#breadcrumb`) |
| `WebPage` mit `name` und `dateModified` aus `seiten_stand.py` | `base.html` über Kontextprozessor `seite` | Zweig (GE18 live: 0 von 13); `/kontakt/danke/` (Zweig KV07) steht nicht im Register und bekommt deshalb weder `name` noch `dateModified` |
| `Person` `#luisa`, `founder`/`author` verweisen darauf | `base.html` | Zweig (GE16 live: 0 von 10) |
| `BreadcrumbList` auf jeder Unterseite über zentralen Block `brotkrume_ld` | `base.html` + je Seite | Zweig (GE12 live: 6 von 12); seit Paket 517 trägt jede der 17 Vorlagen mit `brotkrume_ld` eine eigene `@id` (`#breadcrumb`) |
| `FAQPage` je Wissensseite, deckungsgleich mit den `h2`-Fragen | `wissen/*.html` | Zweig; seit Paket 517 eigene `@id` (`#faq`) auf allen sechs Beiträgen |
| `Article` je Wissensbeitrag (`headline` = `h1`, `description` = Kurztext der Übersicht, `datePublished`, `dateModified`, `author` → `#luisa`, `publisher` → `#organization`, `isPartOf` → `#website`, `mainEntityOfPage` → `#webpage`; kein `image`) | ein Teil-Template `shop1/templates/shop1/teile/wissen_article_ld.html`, per `{% include %}` im Block `schema_ld` aller sechs Beitragsvorlagen | Zweig 12.09. (GE15, `be550e3`, nicht gemergt) |
| `ItemList` der sechs Beiträge (Titel, Reihenfolge und Adressen wie sichtbar verlinkt, `mainEntityOfPage` auf den `WebPage`-Knoten) | `wissen/uebersicht.html` | Zweig 12.09. (GE15); die Übersicht bekommt bewusst **keinen** `Article` — sie ist das Verzeichnis des Bereichs, kein Beitrag |
| `openingHoursSpecification` | — | **bewusst nicht** (GE20, 12.09.2026 als nicht anwendbar eingetragen): es gibt kein Ladengeschäft, das Feld stand einmal mit Mo–So 00:00–23:59 im Graphen und wurde entfernt; `test_geo.py:156` hält seine Rückkehr auf jeder Inhaltsseite auf |
| `speakable` (`SpeakableSpecification`) im `WebPage`-Knoten, `xpath` auf `/html/head/title` und `/html/head/meta[@name='description']/@content` | `base.html` | **Zweig 18.09. (PJ13, `0b94d8e`, nicht gemergt).** XPath statt `cssSelector`, weil ein CSS-Selektor eine Klasse an einem sichtbaren Element gebraucht hätte (Designwache). `test_speakable_zeigt_auf_titel_und_beschreibung_die_es_gibt` (`test_geo`) verlangt beide Ziele und beide genau einmal, nicht leer, auf jeder Inhaltsseite (GE19) |
| `AggregateRating` | — | fehlt, und es gibt keine belegte Bewertungszahl (KV09) |

`@id` trugen zur Messung vom 02.09.2026 im Schnitt 66 % der Knoten (GE07, live), zur Messung vom 27.09.2026 (nach Paket 508) 71 %. Im Zweig vom 27.09.2026 kamen zunächst sechs weitere Knoten mit eigener `@id` dazu (`Product`, `CollectionPage`, `ContactPage`, zwei `FAQPage`, `AboutPage`, `ItemList`), dazu verweisen `brand`/`seller`/`provider` per `@id` auf `#organization` statt ihn zu verdoppeln (Paket 508). Paket 517 hat den bis dahin einzigen durchgängig anonymen Knotentyp geschlossen: die `BreadcrumbList` auf allen 17 Vorlagen mit dem Block `brotkrume_ld` trägt jetzt `#breadcrumb`, dazu die `FAQPage` der sechs Wissensbeiträge (`#faq`) und der `Offer`-Knoten auf `produkt_detail.html` und `produkte.html` (`#offer`); `Question`/`Answer`/`ListItem` bleiben bewusst ohne eigene `@id`, weil sie nach Schema.org-Konvention positionale, nicht andernorts referenzierte Werte sind — nicht nachgemessen, welchen Anteil das insgesamt ergibt.

## Inhalt und Keywords

Seitenbestand, Wortzahlen und Themen: [30-INHALTE.md](30-INHALTE.md). Kurz:

- **Dünn:** 11 von 13 Seiten unter 200 Eigenwörtern, 1.557 Eigenwörter gesamt gegen 12.000 Ziel (IS19, SU02) — Messwerte für **main**. Im Zweig liegt seit dem 08.09.2026 (`b35f6e4`) keine indexierbare Seite mehr unter 200 Wörtern im Inhaltsbereich; `/impressum/` bleibt bei 75, trägt aber `noindex` und steht weder in der Sitemap noch in `llms.txt`. Die erst am 19.09.2026 gebaute Seite `/motiv-anfragen/` lag mit 123 Wörtern erneut darunter; **im Zweig nachgezogen** (27.09.2026, `a9ae0bb`): Erklärsätze der vier Stationen, die Dauer aus `luviq_daten.DAUER` und der Hinweis auf die persönliche Bestätigung heben sie auf 213 Wörter, `MINDESTWOERTER` nachgezogen. 
- **Umfang je Seitenart (IS18):** seit dem Merge `1a5f36b` auf `main` (gebaut 11.09.2026, `2591fde`, Zweig `sofort/2026-09-11-is18`) erreichen `/` (Ziel 700), `/produkte/` (600) und `/wissen/` (900) laut Commit ihr Ziel — gezählt nach dem Verfahren des Werkzeugs und ohne ein Produkt im Bestand, mit belegtem Fliesstext in bestehenden Absätzen (die Designwache lässt keine neuen Elemente zu). Die Produktseiten (600) erreichen es nicht: ihr statischer Teil ist auf allen Stücken wortgleich, mehr davon höbe die Textgleichheit (IS21); eine eigene Beschreibung je Einzelstück kann nur die Betreiberin liefern. Einzelheiten: [30-INHALTE.md](30-INHALTE.md).
- **Kannibalisierung:** „custom print" auf drei Produktseiten; zwei Produkte mit identischem Namen und Titel (IS23, IS03) — Pflege im Shop-Admin. **Am 17.09.2026 (Paket 238) als nicht möglich beendet**, keine Zeile Code geändert: `Produkt.meta_title` nimmt den gepflegten `seo_titel` oder den `name`, `Produkt.save()` bildet den Slug aus dem `name` — beide Werte setzt nur die Betreiberin im Shop-Admin. Steht seitdem als **beim Kunden** im Bewertungsblock ([80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 8).
- **Ort:** „Alsfeld" bzw. „Hessen" in Startseiten-, Produkte-, Kontakt- und Impressumstitel; im Zweig auch in jedem Produkttitel.
- **Alt-Texte:** 21 von 39 schablonenhaft (IS25), Produkt-alt = Produktname.

## GEO und KI-Sichtbarkeit

*Tabelle: Spalte „Live“ = Messung 02.09.2026; Spalte „Zweig“ = seit den Merges live (Stand 01.10.2026). Messwert GEO aktuell: 79 („Solide“).*

| Regel | Live (02.09.2026) | Zweig |
|---|---|---|
| GE23 Antwort zuerst | 1 von 13 Seiten | **jede** Inhaltsseite: der erste Absatz sagt im ersten Satz, was die Seite ist, und trägt eine belegte Zahl (08.09.2026, `fd82efd`). `/produkte/` und `/gaestebuch/` nennen die Bestandszahl aus der Datenbank (`produkte_liste\|length`, `comments\|length`), `/kontakt/`, `/ueber_uns/` und `/liefergebiet/` PLZ 36304 und Versanddauer, `/datenschutz/` seine Abschnitte, `/agb/` seine Paragraphen und die 14-Tage-Frist, jede Produktseite Name, Preis und Herkunft aus dem Datensatz. Die Ausnahmemenge `OHNE_ZAHL_IM_ERSTEN_DRITTEL` in `test_inhalt` ist seither leer. **Vertieft im Zweig 27.09.2026** (`132cecf`, Paket 508) auf zwei von vier durch die Gegenprüfung gemeldeten Seiten: der Lead-Satz der Startseite (`luviq_daten.LEAD`) nennt jetzt die Ziffer „2 bis 5 Tage" statt nur „genau einmal", die Datenschutzerklärung schreibt „4 Abschnitten" statt „vier Abschnitten" als Wort — reine Fliesstext-Änderung; `test_inhalt` verlangt nur eine Ziffer im ersten Drittel des Inhalts und war für beide Seiten schon vorher grün (auf `/datenschutz/` durch die Adresse „Grünberger Str. 16, 36304 Alsfeld" im selben Absatz, auf `/` durch eine andere Ziffer weiter oben). **`/gaestebuch/` und `/produkt/custom-print-hoodie/` (Nachbesserung, 27.09.2026):** als beim Kunden im Bewertungsblock von [80-AUFGABEN.md](80-AUFGABEN.md) eingetragen — der Code liefert auf jeder Produktseite unabhängig von `Produkt.beschreibung` einen Kernsatz und mindestens 211, live 222 bis 224 Wörter (`antwort_produkt.html:2`, `test_inhalt.py:159`, Beleg `IS17`), im Gästebuch Kernsatz, belegte Zahl und live 524 Wörter (`gaestebuch.html:34`); die gemeldeten 91 Wörter ohne Kernsatz sind mit diesem Code nicht erreichbar und zeigen einen noch nicht ausgelieferten Stand (derselbe Rückstand wie bei `PJ16`) |
| GE25 konkrete Zahlen | 0 von 5 | PLZ, Versandzeiten, § 19 auf allen Inhaltsseiten; dazu seit 08.09.2026 (`2b26108`) auf den fünf Seiten, die noch keine nannten: 14 Tage Widerruf aus § 5 der AGB (dort jetzt zusätzlich in Ziffern), Versand 1–2 und Zustellung 1–3 Werktage in `/agb/` § 4 und `/liefergebiet/`, 5 Minuten Sperrfrist je Pfad und ein Besuch je Sitzung und Tag (`middleware.py`) sowie 14 Tage Laufzeit des Sitzungs-Cookies (`SESSION_COOKIE_AGE`) in der Datenschutzerklärung, Zahl der Beiträge und Orte aus dem Kontext auf `/wissen/` und `/liefergebiet/`. **Nicht** genannt, weil im Projekt nicht belegt: Preisrahmen, Rückporto, Antwort- und Erreichbarkeitszeiten |
| GE24 Frage-Überschriften | 2 von 13 | Wissensseiten (6–7 Fragen je Seite), FAQ auf `/kontakt/` |
| GE16 Autor | 0 | `Person #luisa` als `author`; seit GE15 (12.09.2026, Zweig) verweisen zusätzlich die sechs `Article`-Knoten der Wissensbeiträge auf dieselbe Kennung |
| GE15 Ratgeber als `Article` | 0 (nur `FAQPage`) | **Zweig 12.09.** (`be550e3`, nicht gemergt): genau ein `Article` je Beitrag, jede Angabe aus einem vorhandenen Register — `headline`/`description` aus `WISSEN_BEITRAEGE`, `dateModified` aus `seiten_stand.py`, `datePublished` aus dem neuen Registerfeld `veroeffentlicht` (belegt durch `git log --diff-filter=A` der Vorlage, `2026-09-01` bzw. `2026-09-07`), `author`/`publisher` als Verweis auf `#luisa` und `#organization`. Kein `image` (die Beiträge haben keines). Die Übersicht trägt stattdessen eine `ItemList`. Fünf Tests in `test_geo` (`RatgeberSchemaTest`) |
| GE43 Quellen in Ratgebern | — | **Zweig 17.09.** (`5928144`, nicht gemergt), **anders eingebaut**: je ein Link auf die Rechtsquelle einer Aussage, die die Seite schon trifft — `/wissen/bestellen-und-bezahlen/` und `/wissen/widerruf-und-ruecksendung/` auf § 355 BGB (`gesetze-im-internet.de`), `/wissen/konto-und-daten/` auf die DSGVO (EUR-Lex, Art. 15–17 im Text genannt), `/wissen/` auf § 19 UStG. Statt einen Link hinzuzufügen, ist je Seite ein Fliesstext-Link auf ein Ziel aus Menü oder Fuss (Über uns, AGB, Kontaktformular, Impressum) zu Text geworden — die Designwache zählt `<a>`-Elemente. Die drei gesperrten Beiträge (Pflege, Upcycling, Grösse) sind nicht angefasst |
| GE32 Feed für neue Inhalte | keiner | **Zweig 17.09.** (`22fea97`, nicht gemergt): RSS-Feed unter `/feed/` mit den freigegebenen Wissensbeiträgen — die einzige Adresse, an der ein Aggregator oder eine Antwortmaschine fragen kann, *was neu ist*, ohne die Seite abzulaufen. Gefunden wird er über `<link rel="alternate" type="application/rss+xml">` im `<head>` jeder Seite (`templates/base.html`) und über die Zeile `Feed: …` in `llms.txt`. **Bewusst nur der Wissensbereich, nicht die Produkte:** ein Einzelstück ist nach dem Verkauf weg, und ein Feed, aus dem Einträge wieder verschwinden, ist für einen Leser kaputt (begründet im Docstring von `WissenFeed`) |
| GE20 Öffnungszeiten | 0 | **nicht anwendbar** (12.09.2026, Bewertungsblock in [80-AUFGABEN.md](80-AUFGABEN.md)): kein Ladengeschäft — `ueber_uns.html:68`, `liefergebiet.html:37,84,116` und die `llms.txt` (`views/legal.py:159,216`) sagen es sichtbar, die Adresse im Schema ist die Privat- und Werkstattanschrift. Keine Zeile Code geändert |
| GE18 `dateModified` | 0 | Register, von Hand gepflegt (bewusst kein Build-Datum) |
| GE11 `sameAs` | 1 (Instagram) | unverändert — Unternehmensprofil, TikTok, Wikidata nicht dokumentiert. Paket 171 (11.09.2026) und Paket 183 (12.09.2026) je **nicht möglich**: im Projekt steht genau eine Profiladresse (`base.html:118`, dieselbe in `llms.txt`, `views/legal.py:166`), `GOOGLE_REVIEW_URL` ist im Standard ein Maps-Suchlink (`settings.py:409`) und TikTok nennt `GOOGLE_SEO_GUIDE.md` nur als Bio-Verlinkung ohne Adresse; keine Zeile Code geändert. Seit dem 12.09.2026 als **beim Kunden** im Bewertungsblock ([80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 15) |
| GE30 `llms.txt` | 404 | 200 |
| GE02 Trainings-Crawler | nicht geregelt | 13 Crawler ausdrücklich erlaubt (Entscheidung: zulassen) |
| GE19 `speakable` | 0 | **Zweig 18.09.** (`0b94d8e`, nicht gemergt): jede Seite über `base.html`, Ziele Titel und Meta-Beschreibung — siehe Tabelle „Strukturierte Daten" |
| GE23 Antwort-Baustein | — | **Zweig 18.09.** (`0b94d8e`, **anders eingebaut**): nur der Antwortsatz der Produktseiten ist ein eigener Vorlagenteil (`shop1/templates/shop1/antwort_produkt.html`: Name, Herkunft und Preis aus dem Datensatz, eingebunden in `produkt_detail.html`, Ausgabe wortgleich, reiner Text ohne Element). Die Inhaltsseiten behalten ihren eigenen Antwortabsatz — er ist je Seite ein anderer Text, `test_inhalt`/`test_geo` halten ihn schon fest, und ein gemeinsames Element mit Klasse hätte die Designwache verletzt |
| GE29 Rahmenanteil | Produktseiten 73 % | statischer Zusatz je Produktseite senkt ihn; nicht gemessen |

## Erledigt

*Einträge mit „Zweig … nicht gemergt“ sind seit dem 28.09./01.10.2026 in `main` (Merge `ac0e984`) und live.*

| Datum | Was | Beleg |
|---|---|---|
| 23.10.2026 | **Zweig `seo/2026-10-23-luviq-upgrade`, nicht gemergt, nicht live.** Befunde aus Website-Check (lokal, 22.10.2026) und Live-Abruf: canonical/og:url/hreflang und Schema-`@id` ohne Query (die sechs Vorbelegungen `/motiv-anfragen/?richtung=…` standen als eigene Seiten mit gleichem Titel im Index); `UMLEITEN_HOSTS` für zweite Domains (`luviq-luebeck.com` lieferte 200 als Kopie); llms.txt mit „Womit malt Luisa Brehler?“ und „Wie bekomme ich ein eigenes Motiv?“, Wissenszeile berichtigt; Titel ≤ 60 (Wissen, Pflege, Upcycling) und Beschreibungen ≤ 160 Zeichen (Archiv, Gästebuch, Pflege, Upcycling, Größe, Herkunft). Google-Profil/Domain: [2026-10-23_GOOGLE-PROFIL-ENTSCHEIDUNG.md](2026-10-23_GOOGLE-PROFIL-ENTSCHEIDUNG.md) | `12cc89e`, `62147a0`, `78822a0`, `189152e`, `287ed36` |
| 02.10.2026 | **Wissensbereich frei und live:** Pflege, Upcycling und Größe `index, follow`, in Sitemap (17 URLs), `llms.txt` und Feed; Titel, FAQPage, Quellen nachgeschärft; sichtbares Datum „Aktualisiert am …“ (`GE47`) | `3073388`, `c943006`, `f03bf61` (live 02.10.2026 abgerufen) |
| 02.10.2026 | **`sameAs` erweitert** (GE11, GE46): Instagram `luviq.archive`, TikTok `@luviq.archive`, Google-Unternehmensprofil „Luviq“ in `sameAs` und `llms.txt` | `3073388` (live `llms.txt` abgerufen) |
| 02.10.2026 | **`llms-full.txt`** (GE31, VL09): 200, 44 KB; von `robots.txt` und `llms.txt` genannt | `bf8882e` |
| 02.10.2026 | **Überschriftensprünge und Alt-Texte** (IS14, BF15, VL17): keine Sprünge, je Seite eine h1, kein Bild ohne `alt`, Breite und Höhe gesetzt (live 02.10.2026 geprüft) | `08db0ed`, `5a57175`, `9402995` |
| 02.10.2026 | **Apex- und Railway-Adresse** per 301 auf `www` (TS11, EIG18, EIG60); `/health/`, `security.txt` (bis 01.10.2027) | `feeb95e`, `3073388` |
| vor 25.05.2026 | Dynamische Sitemap, robots.txt, Meta/Open Graph, semantisches HTML, Schema `Organization`/`ClothingStore`/`WebSite`/`ItemList`/`Product` | `GOOGLE_SEO_GUIDE.md`, `DOCUMENTATION.md` §7 |
| 01.09.2026 | Falscher Zielbegriff „railway hosting luviq" aus dem Guide gestrichen | `GOOGLE_SEO_GUIDE.md` |
| 01.09.2026 (Zweig) | Meta-Beschreibungen, Ortsbezug im Produkttitel, Produkt-Meta-Längen, `lastmod`-Register, `/produkt/` → 301 | Schritte 11–15 (`6bfc4ea` … `23f8b24`) |
| 01.09.2026 (Zweig) | `WebPage`-, `Person`-, `BreadcrumbList`-Knoten; `llms.txt`; GEO-Tests 16 → 20 | Schritte 16–20 (`732f296` … ) |
| 01.09.2026 (Zweig) | Antwort-zuerst-Texte auf sieben Seiten; Wissensbereich mit drei Beiträgen | Schritte 21–30 |
| 02.09.2026 (Zweig) | `CanonicalHostMiddleware` (301 auf www) | Schritt 37 (`6bd5eb4`) |
| 02.09.2026 (Zweig) | Wissensbeiträge auf `noindex` bis zur Freigabe; Sitemap/llms.txt lesen das Register | Auflage 3 (`60555d0`) |
| 07.09.2026 (Zweig) | Drei belegte Wissensbeiträge (Bestellen, Widerruf, Konto), `freigegeben` ohne Vorbehalt; `/wissen/` damit indexierbar, Sitemap und llms.txt führen vier Wissensadressen | SU04 (`d7d2e0b`) |
| 08.09.2026 (Zweig) | Antwortabsatz mit belegter Zahl auf jeder Inhaltsseite (GE23), konkrete Zahlen auf den fünf Seiten ohne (GE25), keine indexierbare Seite unter 200 Wörtern im Inhaltsbereich (IS19) — ohne eine Änderung am Aufbau, `test_aufbau` unverändert | `fd82efd`, `2b26108`, `b35f6e4` |
| 11.09.2026 (Zweig `sofort/2026-09-11-is18`, seit `1a5f36b` auf `main`) | IS18 anders eingebaut: `/`, `/produkte/` und `/wissen/` mit belegtem Fliesstext auf dem Umfang ihrer Seitenart, `lastmod`/`dateModified` dieser drei Seiten auf `2026-09-11`; die fünf Produktseiten bleiben bei der Betreiberin. Ohne Änderung am Aufbau, 218/218 Tests grün laut Commit | `2591fde` |
| 11.09.2026 (Zweig `sofort/2026-09-11-kv07-und-2-weitere`, nicht gemergt) | KV07: eigene Danke-Seite `/kontakt/danke/` nach dem Kontaktformular — `noindex, follow`, weder in Sitemap noch in `llms.txt`, nicht in `seiten_stand.py`; keine indexierbare Seite verändert. Tests in `test_formulare` (`KontaktDankeTest`), 224/224 grün laut Commit | `2d78a55` |
| 12.09.2026 (Zweig `sofort/2026-09-12-mw15-und-2-weitere`, nicht gemergt) | GE15 anders eingebaut: `Article`-Knoten auf allen sechs Wissensbeiträgen aus einem gemeinsamen Teil-Template (`teile/wissen_article_ld.html`), Angaben aus `WISSEN_BEITRAEGE`, `seiten_stand.py` und dem neuen Registerfeld `veroeffentlicht`; auf der Übersicht `/wissen/` stattdessen eine `ItemList` der Beiträge, weil ein `Article` dort einen Beitrag behauptete, den es nicht gibt. Fünf neue Tests in `test_geo`, alles im `<head>` — kein Element, keine Klasse, keine Überschrift geändert, `test_aufbau` grün, `seiten_stand.py` unverändert. GE20 im selben Paket als **nicht anwendbar** eingetragen (Öffnungszeiten ohne Ladengeschäft), keine Zeile Code | `be550e3`, `bb6fee1` |
| 17.09.2026 (Zweig `sofort/2026-09-17-kv05-und-2-weitere`, nicht gemergt) | `seiten_stand.py`: `kontakt` von `2026-09-01` auf `2026-09-17`, weil der sichtbare Text der Seite mit dem Datenschutzhinweis (`KV05`) gewachsen ist — `lastmod` der Sitemap und `dateModified` des `WebPage`-Knotens folgen dem Register. Damit ist auch der Satz aus Paket 216 (`FO04`) abgedeckt, der bis dahin ohne neues Datum war. Am Schema selbst keine Änderung: der Hinweis steht als Fliesstext im Formular, kein neues Element, kein neuer Knoten. `KV09` im selben Paket **nicht möglich** (Bewertungsblock in [80-AUFGABEN.md](80-AUFGABEN.md)) — ohne belegte Bewertungszahl kein `aggregateRating`, und im Projekt gibt es bis heute keinen solchen Knoten | `9cd641f` |
| 17.09.2026 (Zweig `sofort/2026-09-17-bf24-und-2-weitere`, seit `911c26a` auf `main`) | GE32: RSS-Feed `/feed/` mit den freigegebenen Wissensbeiträgen (`WissenFeed` in `views/wissen.py`, Route in `urls.py`, re-exportiert in `views/__init__.py`), Angaben ausschliesslich aus `WISSEN_BEITRAEGE` (`titel`, `kurz`, `url_name`, `veroeffentlicht`), neuester zuerst; verlinkt als `rel="alternate"` im `<head>` von `base.html` und als Zeile `Feed:` in `llms.txt`. Genau die Menge aus Sitemap und `llms.txt` — kein gesperrter Beitrag. Fünf Tests in `test_seo` (`FeedTest`), 285 Testfunktionen gezählt. IS23 im selben Paket **nicht möglich** (Bewertungsblock in [80-AUFGABEN.md](80-AUFGABEN.md)), keine Zeile Code | `22fea97` |
| 18.09.2026 (Zweig `sofort/2026-09-18-pj06-und-2-weitere`, nicht gemergt) | PJ13 anders eingebaut: `speakable` im `WebPage`-Knoten per XPath auf Titel und Meta-Beschreibung (GE19); Antwortsatz der Produktseiten als Vorlagenteil `antwort_produkt.html`, die Inhaltsseiten behalten ihren eigenen Absatz; IndexNow für Produktänderungen (`shop1/indexnow.py`, `/indexnow-schluessel.txt`, Signal `produkt_an_indexnow`), aus bis `INDEXNOW_KEY` gesetzt ist. Nur `<head>` und ein wortgleicher Vorlagenteil — kein Element, keine Klasse neu. `IndexNowTest` (4) in `test_seo`, ein Test in `test_geo`; laut Commit 314 Tests grün | `0b94d8e` |
| 17.09.2026 (Zweig `sofort/2026-09-17-pj05-und-2-weitere`, seit `f489e76` auf `main`) | GE43 anders eingebaut: vier Wissensseiten mit je einem Gesetzeslink (§ 355 BGB zweimal, DSGVO, § 19 UStG), je ein Menü-/Fuss-Ziel im Fliesstext dafür entlinkt, kein Element neu; `seiten_stand.py` für `wissen`, `wissen_bestellen`, `wissen_widerruf`, `wissen_konto` auf `2026-09-17`. Kein Testlauf im Commit genannt. TS46 im selben Paket **nicht möglich** (Bewertungsblock in [80-AUFGABEN.md](80-AUFGABEN.md)), keine Zeile Code | `5928144` |
| 27.09.2026 (Zweig `sofort/2026-09-27-ts06-und-1-weitere`, nicht gemergt) | IS19 nachgezogen: die erst am 19.09.2026 gebaute Seite `/motiv-anfragen/` lag mit 123 Wörtern unter der am 08.09.2026 erreichten 200-Wörter-Grenze. Die vier Stationen (`luviq_daten.ANFRAGE_STATIONEN`) tragen jetzt einen Erklärsatz statt nur ihres Namens, dazu die Dauer aus `luviq_daten.DAUER` und der Hinweis auf die persönliche statt automatische Bestätigung — kein Element, keine Klasse neu, `test_aufbau` unverändert. Jetzt 213 statt 123 Wörter, `MINDESTWOERTER['/motiv-anfragen/']` von 100 auf 200, `seiten_stand.py` auf `2026-09-27`; 399/399 Tests grün. TS06 im selben Paket als **bewusst so** im Bewertungsblock in [80-AUFGABEN.md](80-AUFGABEN.md): `/agb/` trägt `noindex` nur, solange kein Verkauf stattfindet | `a9ae0bb` |
| 27.09.2026 (Zweig `sofort/2026-09-27-pj05-und-2-weitere`, nicht gemergt) | GE22 gebaut: `geo` (`GeoCoordinates`) stand im JSON-LD-Graphen bisher nur, wenn `VERKAUF_AKTIV` gesetzt ist — die `PostalAddress` selbst wird unabhängig davon immer schon ausgeliefert. Koordinaten sind keine Geschäftsbehauptung wie Preisspanne, Zahlarten oder Liefergebiet, sondern nur die maschinenlesbare Form derselben Adresse, deshalb eine Zeile in `templates/base.html` aus dem `verkauf_aktiv`-Block herausgezogen; kein neues Element, `test_aufbau` unverändert. `PJ05` (kein kritischer Code-Befund, Mail-Vorlagen sind von der Prüfung ausgenommen) und `KV08` (fehlende Telefonnummer plus zwei Eigenheiten der Katalogmessung) im selben Paket als **beim Kunden** im Bewertungsblock von [80-AUFGABEN.md](80-AUFGABEN.md) eingetragen, dafür keine Zeile Code geändert | `89643e2` |
| 28.09.2026 (Zweig `sofort/2026-09-27-pj05-und-2-weitere`, nicht gemergt, Nachbesserung) | GE22 berichtigt: Die Fassung aus `89643e2` (`geo` ausserhalb des `verkauf_aktiv`-Blocks, aber weiter direkt am `Organization`/`ClothingStore`-Knoten) war von der Gegenprüfung zu Recht abgelehnt — `geo` ist nach schema.org nur an `Place` und dessen Untertypen gültig, und ohne `VERKAUF_AKTIV` gibt der Knoten nur `"Organization"` aus. Statt dessen trägt der Organization-Knoten jetzt einen eigenen `location`-Knoten vom Typ `Place` mit eigener `PostalAddress` und `GeoCoordinates` (`templates/base.html:80-93`), unabhängig vom Verkaufsschalter gültig; `address` bleibt zusätzlich am Organization-Knoten stehen. Kein Element, keine Klasse, keine Kennung im sichtbaren Aufbau geändert, `test_aufbau` unverändert | *(dieser Zweig)* |
| 01.10.2026 | **TS19** — Bild-Auszeichnung in der Sitemap: Startseite (Titelbild, fünf Entstehungsbilder aus `luviq_daten`) und `/produkte/` (Bilder der aktiven Stücke); kein Logo als Platzhalter an Seiten ohne Inhaltsbild. Live bestätigt (Sitemap abgerufen 01.10.2026) | `36c0741` |

## Schub 23.10.2026 (Zweig, nicht live)

Sitz Lübeck, Herkunft Alsfeld in Titeln, Schema und Stückbeschreibungen; `sameAs` aus `luviq_daten.PROFILE`; fünf Motiv-Fragen (`luviq_daten.FAQ_MOTIV`) sichtbar auf `/motiv-anfragen/`, `FAQPage` erst mit Verkauf; `llms.txt` führt sie in beiden Fassungen. Keine Lübecker Ortsseite, solange Luisas persönlicher Kontakt in Lübeck ungeklärt ist (`80-AUFGABEN.md`).

## Runde 3, 30.10.2026 (Zweig, nicht live)

- Ratgeber `/wissen/bleach-painting/` und `/wissen/bleichfleck-uebermalen/` veröffentlicht (Sitemap, llms.txt, Feed, Übersicht; Article + FAQPage, Antwortsatz zuerst, Bleach mit `Article.image`).
- Bild-Sitemap: alle Galeriebilder je Stück, echte Handyfotos der Startseite, Luisas Foto auf Kontakt/Luisa, Foto des Bleach-Ratgebers.
- Mit Verkauf: `MerchantReturnPolicy` an der Organization (`#rueckgabe`, 14 Tage, DE, per Post, ohne `returnFees`), jedes Offer verweist darauf und trägt `OfferShippingDetails` (0 EUR, DE, 1–2 Tage Bearbeitung). `Person.image` = Luisas Brustbild.

## Offen

Stand 02.10.2026, gegen `origin/main` und die Live-Seite geprüft. Erledigt und entfernt: Freigabe der Wissensbeiträge, `sameAs`, `llms-full.txt`, Überschriftensprünge und Merges der Arbeitszweige (siehe „Erledigt“ oben); `INDEXNOW_KEY` steht als Bastian-Zeile in [10-TECHNIK.md](10-TECHNIK.md), Produktnamen, Beschreibung je Stück und eine belegte Bewertungszahl (`AggregateRating`, KV09) unter „Beim Kunden“ in [80-AUFGABEN.md](80-AUFGABEN.md) — dort stehen sie nur einmal.

| Punkt | Regel | Wo |
|---|---|---|
| Bei Bastian: Search Console — Indexierung der 17 Sitemap-Seiten beantragen und die Ausschlussgründe lesen (`TS46`). Grund: das geht nur mit Zugang zur Property (liegt im Konto von Luisa, `/u/3`) und im Kontingent von etwa 10 Anträgen je Konto und Tag | TS46 | Search Console |
| Bei Bastian: Entscheidung, ob die fünf Archiv-Stückseiten auf `noindex, follow` gehen. Für: sie sind bis auf Name, Nº und Beschreibung wortgleich (IS21: 10 Paare bis 100 %, IS17/SU06: unter 300 Wörtern). Gegen: sie sind die einzigen Belege der Arbeit (Bilder, Nº, Bildersuche) und verschwänden aus Google, Bild-Sitemap und `llms.txt`. Bei Ja: Bedingung für `robots` in `produkt_detail.html`, Sitemap und `llms.txt` filtern, Tests und `aufbau_referenz.json` nachziehen | IS21, IS17, SU06 | `produkt_detail.html`, `legal.py` |
| Bei Bastian: Entscheidung, ob `/ueber_uns/` auf `/ueber-uns/` mit 301 umzieht (Bindestrich ist Googles Empfehlung). Gegen: die Adresse ist live und vermutlich indexiert, jede Umbenennung kostet Zeit bis zum Umzug bei Google; dass `VL11` die Seite nicht als Über-uns-Seite erkennt, ist ein Messfehler des Musters (an das Overview-Team gemeldet). Bei Ja: neuer Pfad in `shop1/urls.py`, 301 vom alten, Pfade in Tests und `aufbau_referenz.json` | VL11 | `shop1/urls.py` |
| Später: Alt-Texte der Stückbilder je Stück beschreiben statt „Foto: <Name>, handbemaltes Einzelstück von Luviq Universe“. Grund: die zwei Stücke „Custom print hoodie“ tragen denselben Alt-Text; ein eigener Text braucht die Beschreibung je Stück von Luisa (siehe „Beim Kunden“); die Bilder der Startseite haben beschreibende Alt-Texte | IS25 | Templates |

## Update 02.11.2026 (SEO/GEO-Upgrade, Zweig `seo/2026-11-02-luviq`)

Schema ohne Privatdaten (Organization: Ort/Land, `OnlineStore`, `contactPoint` mit Kontakt-URL), Archivstücke als `VisualArtwork` ohne Angebot, `llms.txt` mit getrenntem Archiv, Engel-Seite mit FAQ + FAQPage, acht zusätzliche Inhaltslinks auf das Engel-Shirt, neuer Abschnitt „Bleichflecken entfernen“, neue Seite `/wissen/bleach-painting-anleitung/` (Quellen BfR, Verbraucherzentrale NRW). Offen für Luisa: Archivtexte und Bild-Alt (Datenbank). Details: `LOGBUCH.md` 02.11.2026.


## 04.11.2026 Deutschland-Runde (Zweig `seo/2026-11-04-deutschland`)

**Anlass:** Die alte Domain bekam fast nur Ladensuchen („second hand alsfeld“, „öffnungszeiten“, „in der nähe“); Luviq hat keinen Laden und liefert nur innerhalb Deutschlands. Ziel: deutschlandweite Online-Suchabsicht (handbemaltes Shirt, Bleach-Shirt, Unikat-Kleidung, Second-Hand-Shirt online, Engel-Shirt, Shirt mit eigenem Motiv). Begriffe und Seitenzuordnung: `Webagentur Scherzinger\Analysen\luviq-2026-11-04-seo-BEGRIFFSLANDKARTE.md`, Umsetzung und Messplan dort in `02-UMSETZUNG.md`.

- **Titel/Descriptions** aller indexierbaren Seiten neu: ein Hauptbegriff je Seite, Marke am Ende, ohne „Lübeck“ im Titel (Sitz bleibt im Text, Impressum, Schema). Startseite, Archiv, Versand, Kontakt, Motivanfrage und alle Wissensbeiträge.
- **Stückseiten:** Engel-Shirt „Engel-Shirt handbemalt, mit Bleiche gemalt – 69 € | Luviq“ (`luviq_daten.ENGEL_STUECK`; frühere Fassungen in der Datenbank werden über `*_frueher` erkannt, Luisas eigene Texte bleiben). Vergebene Archivstücke: Titel „<Name> – Nº 00x, vergeben | Luviq“ ohne „kaufen“, deutsche Description 140–160 Zeichen mit Weg zur Anfrage (`Produkt._meta_title_vergeben`, `META_BESCHREIBUNG_ZUSATZ_VERGEBEN`); ein gepflegter `seo_titel` mit „kaufen“ bei einem vergebenen Stück wird ignoriert. Beide Hoodie-Seiten haben so verschiedene Titel (Archivnummer).
- **Startseiten-Lead** (`luviq_daten._lead`): zitierfähiger Antwortsatz (Luviq, Online-Shop, handbemalte Second-Hand-Shirts und Unikate, Bleiche, Versand Deutschland).
- **Engel-FAQ** um zwei Fragen erweitert (Versand in ganz Deutschland, Bezahlung per Zahlungslink); sichtbar und als FAQPage.
- **Korrektur** `/wissen/bestellen-und-bezahlen/`: Reservierung gilt nur für Einzelstücke, das Serienstück Engel-Shirt wird nicht reserviert (`wissen_direktkauf.py`). Offen, Rechtstext: AGB § 2 (3) sagt weiter „das Stück wird damit für dich reserviert“ - nur mit Freigabe/Generator ändern.
- **Schema:** Organization trägt `brand` (Brand-Knoten `#brand`); jedes Offer trägt `eligibleRegion` und `areaServed` Deutschland (neben `shippingDetails` DE und Rückgaberegel); sonst unverändert (OnlineStore, Product, FAQPage, Article).
- **Sitemap:** vergebene Archivstücke `monthly`, Priorität 0.4 (statt weekly/0.8).
- **`llms.txt`:** deutschlandweit formuliert, zwei neue Fragen (handbemaltes Shirt online kaufen, Bleach-Shirt), Seitenliste „Versand & Abholung“.
- **Nicht gemacht:** neue Ortsseiten, neuer Wissensbeitrag (Dopplung; erst mit Material von Luisa), Änderungen an Layout/CSS.
