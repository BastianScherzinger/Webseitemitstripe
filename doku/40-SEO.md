---
bereich: seo
titel: SEO und GEO
stand: 2026-10-02
status: teilweise
fortschritt: 87
zusammenfassung: Stand 01.10.2026: Bild-Sitemap TS19 live (36c0741), llms.txt, Feed, @id-Schema mit speakable und location/Place, Apex-301, noindex für Wissensbereich bis zur Freigabe; Messwerte SEO-Technik 98, SEO-Inhalt 83, GEO 79. Offen sind Freigaben und Profiladressen der Betreiberin sowie llms-full.txt und IndexNow. Seit 02.10.2026 im Code (nicht ausgeliefert): sichtbares Änderungsdatum der Wissensbeiträge aus SEITEN_STAND (GE47).
offen: 9
quellen: GOOGLE_SEO_GUIDE.md, LOGBUCH.md, DOCUMENTATION.md, shop1/views/legal.py, shop1/seiten_stand.py, shop1/indexnow.py, templates/base.html
---

# SEO und GEO — Luviq Universe

*Woran sich der Fortschritt bemisst: am Mittel der drei gemessenen Bereichswerte **SEO-Technik, SEO-Inhalt und GEO** des Laufs vom 02.09.2026 (Regelstand `2026-09-02a`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße. Nennt die Datei zusätzlich einen Planfortschritt (etwa „52 von 73 Aufgaben“), steht der im Abschnitt „Stand“ — er misst den Plan, nicht die Seite.*

> **Stand 01.10.2026 (geprüft):** Alle bis dahin geführten Arbeitszweige (`sofort/…`, `mail/…`, `recht/…`, `design/…`) sind in `main` gemergt (`git branch -r --no-merged origin/main` ist leer); `main` = `origin/main` = `36c0741` (TS19, Bild-Sitemap, 01.10.2026), und die Live-Seite zeigt diesen Stand (Sitemap mit Bild-Auszeichnung am 01.10.2026 abgerufen). Wo unten „Zweig“ oder „nicht gemergt“ steht, ist das **Verlauf** des jeweiligen Tages und gilt seit dem Merge als live, sofern der Satz nichts anderes sagt. Der **Verkauf ist aus** (`VERKAUF_AKTIV` ohne Variable = aus: Marke im Aufbau, Archiv statt Shop); nach Angabe des Betreibers ist **kein Gewerbe angemeldet** — die Seite nennt deshalb keine Unternehmensangaben (Impressum nach § 5 DDG nur mit Luisa Brehler als Person, Alsfeld, E-Mail).

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
| `sitemap.xml` | 200, **13 URLs** mit `lastmod` (Daten zwischen 11.05. und 27.09.2026); **Bild-Auszeichnung seit TS19 (`36c0741`, 01.10.2026)**: Startseite mit Titelbild und fünf Entstehungsbildern, `/produkte/` und die Produktseiten mit den Stückbildern (16 `image:image`-Blöcke gesamt); Seiten ohne Inhaltsbild bleiben ohne Bild. Impressum, AGB, Wissensbereich und Danke-Seiten stehen nicht darin |
| `llms.txt` | 200: Antwortabsatz („Marke im Aufbau … noch kein Verkauf“), Eckdaten (Luisa Brehler, Anschrift, E-Mail, Instagram), Seitenliste, Archiv der Stücke; `llms-full.txt` gibt es nicht (404) |
| `/feed/` (RSS) | 200, Wissensbeiträge (nur freigegebene — derzeit leer) |
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

## Offen

Stand 01.10.2026. Erledigt und entfernt: Merges der Arbeitszweige (alle in `main`), `CANONICAL_HOST`/Apex-301, Impressum-Widerspruch, Bild-Erweiterung der Sitemap (TS19).

| Punkt | Regel | Wo |
|---|---|---|
| Freigabe der drei ersten Wissensbeiträge (Pflege, Upcycling, Größe) → aus `noindex`, in Sitemap, `llms.txt` und Feed; die verkaufsnahen drei erscheinen erst mit Verkauf | SU04, SU07, SU01, VL11 | `shop1/views/wissen.py` — Entscheidung der Betreiberin |
| `sameAs` erweitern (Unternehmensprofil, TikTok) — Adressen nicht dokumentiert, am 11./12.09. und 27.09.2026 als nicht möglich beendet | GE11, GE46 | beim Kunden ([80-AUFGABEN.md](80-AUFGABEN.md)) |
| `llms-full.txt` fehlt (404) | GE31, VL09 | `views/legal.py` |
| IndexNow ist aus — `INDEXNOW_KEY` in Railway setzen oder bewusst aus lassen | PJ13 | Railway |
| Produktnamen/-titel eindeutig, „custom print“-Kannibalisierung | IS23, IS03 | beim Kunden (Name und `seo_titel` setzt nur die Betreiberin) |
| Search Console: Indexierung der Sitemap-Seiten beantragen und Ausschlussgründe lesen (`TS46`) — geht nur im Konto `…05@gmail.com`; ob die Sitemap dort eingereicht ist, steht in keiner Doku | TS46 | Search Console |
| Überschriftensprünge `h1 → h3` auf Bestandsseiten — seit dem Umbau vom 19.09.2026 nicht neu gezählt | IS14, BF15 | Templates + `aufbau_referenz.json` |
| Alt-Texte schablonenhaft (Messung 02.09.2026: 21 von 39) — nicht neu gezählt | IS25 | Templates |
| `AggregateRating` fehlt, und es gibt keine belegte Bewertungszahl | KV09 | bewusst nicht erfunden |
