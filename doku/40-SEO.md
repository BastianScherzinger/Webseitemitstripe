---
bereich: seo
titel: SEO und GEO
stand: 2026-09-11
status: teilweise
fortschritt: 74
zusammenfassung: SEO-Technik live solide (92), Inhalt 73, GEO 76; llms.txt, KI-Crawler-Regeln, WebPage/Person/Breadcrumb-Knoten, 301 auf www, drei indexierte Wissensseiten und seit dem 08.09.2026 GE23/GE25/IS19 (Antwortabsatz, belegte Zahlen, keine dünne Seite mehr) liegen fertig im Code, nicht nachgemessen. IS18 (seit dem Merge 1a5f36b auf main) bringt Startseite, Produktübersicht und Wissensübersicht laut Commit auf den Umfang ihrer Seitenart und zieht deren lastmod auf den 11.09.2026; die Produktseiten bleiben darunter. Die Danke-Seite /kontakt/danke/ (KV07, Zweig sofort/2026-09-11-kv07-und-2-weitere, nicht gemergt) ist noindex und steht weder in Sitemap noch in llms.txt. GE11 (sameAs) ist am 11.09.2026 nicht möglich, weil ausser Instagram keine Profiladresse dokumentiert ist.
offen: 9
quellen: GOOGLE_SEO_GUIDE.md, LOGBUCH.md, DOCUMENTATION.md, shop1/views/legal.py, shop1/seiten_stand.py, templates/base.html
---

# SEO und GEO — Luviq Universe

*Woran sich der Fortschritt bemisst: am Mittel der drei gemessenen Bereichswerte **SEO-Technik, SEO-Inhalt und GEO** des Laufs vom 02.09.2026 (Regelstand `2026-09-02a`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße. Nennt die Datei zusätzlich einen Planfortschritt (etwa „52 von 73 Aufgaben“), steht der im Abschnitt „Stand“ — er misst den Plan, nicht die Seite.*

## Stand

**Es gibt keine SEO-Kampagne** wie bei Rümpelwerk, WVM-IT oder RTC-Service und keinen SEO-Plan mit
Nummern. Was es gibt: `GOOGLE_SEO_GUIDE.md` (Grundausstattung + Aufgaben der Betreiberin) und den
**Verbesserungslauf 4** (Wellen 3–6 SEO/GEO/Inhalt), der im Zweig liegt.

| Bereich (Messung 02.09.2026, live = main) | Wert | Reifegrad |
|---|---:|---|
| SEO — Technik | 89,5 | Solide |
| SEO — Inhalt | 70,4 | Brauchbar |
| GEO — KI-Sichtbarkeit | 61,3 | Brauchbar |
| Substanz & Reichweite | 39,8 | Rohbau |

**Sichtbarkeit: seit dem 03.09.2026 messbar.** Die Property `sc-domain:luviq-alsfeld.com` ist geprüft,
eingetragen und per OAuth angebunden (siehe [50-LOCAL-SEO.md](50-LOCAL-SEO.md)); Klick- und Positionsdaten
liegen aber noch nicht ausgewertet vor.

**Ziel-Suchbegriffe** (`meta name="keywords"` in `base.html`, laut `GOOGLE_SEO_GUIDE.md` massgeblich):
„Luviq", „Luviq Universe", „Second Hand Mode Alsfeld", „Vintage Mode Hessen", „handbemalte Kleidung
kaufen", „Upcycling Mode Deutschland", „1 of 1 Unikate". Der früher genannte Begriff „railway hosting
luviq" war falsch und ist gestrichen.

## Technik

| Baustein | Live (main, 02.09.2026) | Zweig |
|---|---|---|
| `robots.txt` | 200; sperrt `/shop-admin/`, `/profil/`, `/warenkorb/`, `/checkout/`, `/payment/`, `/verify/`, `/login/`, `/logout/`, `/register/`, `/password-reset/`, `/reset/`, `/resend-verification/`, `/delete-account/`; **Sitemap-Zeile vorhanden**; keine KI-Crawler genannt (GE02) | zusätzlich `Allow: /` und **13 Antwort-Crawler namentlich zugelassen** (u. a. GPTBot, PerplexityBot, ClaudeBot, Google-Extended, Applebot-Extended, CCBot, meta-externalagent, Bytespider) |
| `sitemap.xml` | 200, 14 URLs, `lastmod` nur bei 5 Produkten (2 Daten: 14.06./11.05.2026), Bild-Auszeichnung bei 5 (TS16, TS19); eine Klasse im Code (VL07) | `lastmod` für alle statischen Seiten aus dem Register `seiten_stand.py` (`2026-09-01`, die drei SU04-Beiträge `2026-09-07`; seit IS18, `1a5f36b`, `home`, `produkte` und `wissen` `2026-09-11`); `/wissen/` und die drei belegten Beiträge stehen drin, die drei unbestätigten erst nach Freigabe; `/kontakt/danke/` (Zweig KV07) bewusst weder hier noch in `llms.txt`, Test in `test_formulare`; 15 min Cache |
| `llms.txt` | **404** | vorhanden: Antwortabsatz (Ort, PLZ 36304, Versandzeiten), Eckdaten (Betreiberin, Anschrift, E-Mail, Instagram, Zahlungsarten, § 19), Seitenliste, Abschnitt Wissen mit Übersicht und den drei belegten Beiträgen (die drei unbestätigten erst nach Freigabe); 15 min Cache. `llms-full.txt` gibt es nicht (GE31) |
| Canonical | Canonical-Tag je Seite; **Apex `luviq-alsfeld.com` antwortet 200 ohne 301** (TS11, kritisch) | `CanonicalHostMiddleware`: 301 mit vollem Pfad und `https` für die www-Nebenvariante von `CANONICAL_HOST`; **wirkt erst mit gesetzter Variable in Railway** |
| Meta | Titel 7 von 13 in 30–65 Zeichen (IS02), Beschreibungen 5 von 13 in 110–175 (IS09), 4 mit Aufforderung (IS11), 2 Titel mit Ort/Nutzen (IS06), 1 Titel doppelt (IS03), 4 Seiten teilen Beschreibungen (IS10), Marke am Ende bei 9 (IS07) | Beschreibungen aller neun Inhaltsseiten 157–171 Zeichen mit Aufforderung; Ortsbezug im automatischen Produkttitel; Produkt-Meta auf 60/160 begrenzt; Tests in `test_seo` |
| Open Graph / Twitter | vorhanden (`GOOGLE_SEO_GUIDE.md`, VL06: 80 von 91 Kopf-Bausteinen) | unverändert; og-Bild bleibt JPEG |
| Überschriften | 10 von 13 Seiten springen `h1 → h3` (IS14, BF15) | Wissensseiten ohne Sprung; Bestandsseiten **unverändert** (Designwache) |
| 404 | echter 404, aber Standardseite mit 13 Wörtern (TS20, BT05) | unverändert |
| Schutzköpfe | HSTS (1 Jahr, preload), nosniff, `X-Frame-Options: DENY`, Referrer-Policy; **keine CSP, keine Permissions-Policy** (VL04, SI08, SI07) | CSP als Report-Only-Kopfzeile (`CSP_MODUS`) |
| GZip | nicht dokumentiert für main | `GZipMiddleware` für dynamische Antworten |

**Strukturierte Daten (JSON-LD):**

| Knoten | Wo | Stand |
|---|---|---|
| `Organization`/`ClothingStore` mit `PostalAddress`, `GeoCoordinates`, `areaServed` (Hessen, DE, 18 Städte), `OfferCatalog` mit drei `Product`/`Offer`, `sameAs` Instagram | `base.html` | live; `sameAs` nur 1 Verweis (GE11, am 11.09.2026 nicht möglich — keine weitere Profiladresse im Projekt); **Telefon fehlt** — es gibt keine (GE09, VL10) |
| `WebSite` | `base.html` | live |
| `ImageObject` (Logo) | `base.html` | live |
| `ItemList` (aktuelle Produkte) | `index.html` | live |
| `Product` + `Offer` + `Brand`, `BreadcrumbList` | `produkt_detail.html` | live (5 von 6 Leistungsseiten mit Offer, GE13; `/produkte/` ohne) |
| `LocalBusiness` mit `@id #organization` | `impressum.html` | live (`@id` Zweig) |
| `ContactPage`, `ContactPoint`, `FAQPage` (Versand, Erreichbarkeit) | `kontakt.html` | Zweig |
| `WebPage` mit `name` und `dateModified` aus `seiten_stand.py` | `base.html` über Kontextprozessor `seite` | Zweig (GE18 live: 0 von 13); `/kontakt/danke/` (Zweig KV07) steht nicht im Register und bekommt deshalb weder `name` noch `dateModified` |
| `Person` `#luisa`, `founder`/`author` verweisen darauf | `base.html` | Zweig (GE16 live: 0 von 10) |
| `BreadcrumbList` auf jeder Unterseite über zentralen Block `brotkrume_ld` | `base.html` + je Seite | Zweig (GE12 live: 6 von 12) |
| `FAQPage` je Wissensseite, deckungsgleich mit den `h2`-Fragen | `wissen/*.html` | Zweig |
| `speakable`, Antwort-zuerst-Baustein, IndexNow | — | fehlt (VL09, PJ13, GE19) |
| `AggregateRating` | — | fehlt, und es gibt keine belegte Bewertungszahl (KV09) |

`@id` tragen im Schnitt 66 % der Knoten (GE07, live).

## Inhalt und Keywords

Seitenbestand, Wortzahlen und Themen: [30-INHALTE.md](30-INHALTE.md). Kurz:

- **Dünn:** 11 von 13 Seiten unter 200 Eigenwörtern, 1.557 Eigenwörter gesamt gegen 12.000 Ziel (IS19, SU02) — Messwerte für **main**. Im Zweig liegt seit dem 08.09.2026 (`b35f6e4`) keine indexierbare Seite mehr unter 200 Wörtern im Inhaltsbereich; `/impressum/` bleibt bei 75, trägt aber `noindex` und steht weder in der Sitemap noch in `llms.txt`. 
- **Umfang je Seitenart (IS18):** seit dem Merge `1a5f36b` auf `main` (gebaut 11.09.2026, `2591fde`, Zweig `sofort/2026-09-11-is18`) erreichen `/` (Ziel 700), `/produkte/` (600) und `/wissen/` (900) laut Commit ihr Ziel — gezählt nach dem Verfahren des Werkzeugs und ohne ein Produkt im Bestand, mit belegtem Fliesstext in bestehenden Absätzen (die Designwache lässt keine neuen Elemente zu). Die Produktseiten (600) erreichen es nicht: ihr statischer Teil ist auf allen Stücken wortgleich, mehr davon höbe die Textgleichheit (IS21); eine eigene Beschreibung je Einzelstück kann nur die Betreiberin liefern. Einzelheiten: [30-INHALTE.md](30-INHALTE.md).
- **Kannibalisierung:** „custom print" auf drei Produktseiten; zwei Produkte mit identischem Namen und Titel (IS23, IS03) — Pflege im Shop-Admin.
- **Ort:** „Alsfeld" bzw. „Hessen" in Startseiten-, Produkte-, Kontakt- und Impressumstitel; im Zweig auch in jedem Produkttitel.
- **Alt-Texte:** 21 von 39 schablonenhaft (IS25), Produkt-alt = Produktname.

## GEO und KI-Sichtbarkeit

| Regel | Live (02.09.2026) | Zweig |
|---|---|---|
| GE23 Antwort zuerst | 1 von 13 Seiten | **jede** Inhaltsseite: der erste Absatz sagt im ersten Satz, was die Seite ist, und trägt eine belegte Zahl (08.09.2026, `fd82efd`). `/produkte/` und `/gaestebuch/` nennen die Bestandszahl aus der Datenbank (`produkte_liste\|length`, `comments\|length`), `/kontakt/`, `/ueber_uns/` und `/liefergebiet/` PLZ 36304 und Versanddauer, `/datenschutz/` seine vier Abschnitte, `/agb/` seine fünf Paragraphen und die 14-Tage-Frist, jede Produktseite Name, Preis und Herkunft aus dem Datensatz. Die Ausnahmemenge `OHNE_ZAHL_IM_ERSTEN_DRITTEL` in `test_inhalt` ist seither leer |
| GE25 konkrete Zahlen | 0 von 5 | PLZ, Versandzeiten, § 19 auf allen Inhaltsseiten; dazu seit 08.09.2026 (`2b26108`) auf den fünf Seiten, die noch keine nannten: 14 Tage Widerruf aus § 5 der AGB (dort jetzt zusätzlich in Ziffern), Versand 1–2 und Zustellung 1–3 Werktage in `/agb/` § 4 und `/liefergebiet/`, 5 Minuten Sperrfrist je Pfad und ein Besuch je Sitzung und Tag (`middleware.py`) sowie 14 Tage Laufzeit des Sitzungs-Cookies (`SESSION_COOKIE_AGE`) in der Datenschutzerklärung, Zahl der Beiträge und Orte aus dem Kontext auf `/wissen/` und `/liefergebiet/`. **Nicht** genannt, weil im Projekt nicht belegt: Preisrahmen, Rückporto, Antwort- und Erreichbarkeitszeiten |
| GE24 Frage-Überschriften | 2 von 13 | Wissensseiten (6–7 Fragen je Seite), FAQ auf `/kontakt/` |
| GE16 Autor | 0 | `Person #luisa` als `author` |
| GE18 `dateModified` | 0 | Register, von Hand gepflegt (bewusst kein Build-Datum) |
| GE11 `sameAs` | 1 (Instagram) | unverändert — Unternehmensprofil, TikTok, Wikidata nicht dokumentiert. Paket 171 (11.09.2026) **nicht möglich**: keine weitere Profiladresse im Projekt, TikTok nennt `GOOGLE_SEO_GUIDE.md` nur als Bio-Verlinkung ohne Adresse; keine Zeile Code geändert ([80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 15) |
| GE30 `llms.txt` | 404 | 200 |
| GE02 Trainings-Crawler | nicht geregelt | 13 Crawler ausdrücklich erlaubt (Entscheidung: zulassen) |
| GE19 `speakable` | 0 | 0 |
| GE29 Rahmenanteil | Produktseiten 73 % | statischer Zusatz je Produktseite senkt ihn; nicht gemessen |

## Erledigt

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

## Offen

| Punkt | Regel | Wo |
|---|---|---|
| Zweig nach main + `CANONICAL_HOST` in Railway → 301 für den Apex, llms.txt, Schema-Knoten, Meta live | TS11, GE30, GE12, GE16, GE18 | Merge + Railway |
| Freigabe der **drei ersten** Wissensbeiträge (Pflege, Upcycling, Grösse) → aus `noindex`, in Sitemap und llms.txt. Die drei Beiträge aus SU04 (Bestellen, Widerruf, Konto) stehen bereits drin — sie brauchen keine Freigabe | SU07, VL11 | Betreiberin, dann `views/wissen.py` |
| Impressum: `noindex` **und** Sitemap-Eintrag widersprechen sich | SU11 | `legal.py` oder `impressum.html` |
| Überschriftensprünge `h1 → h3` auf 10 Bestandsseiten — nur mit bewusster Änderung der Designwache-Referenz | IS14, BF15 | Templates + `aufbau_referenz.json` |
| Sitemap in drei Klassen segmentieren, Sitemap-Index, Bild-Erweiterung für alle Einträge | VL07, TS19 | `legal.py` |
| `speakable`, Antwort-Baustein, IndexNow, `llms-full.txt` | VL09, PJ13, GE19, GE31 | |
| `sameAs` erweitern (Unternehmensprofil, TikTok, weitere Profile) — Adressen nicht dokumentiert; am 11.09.2026 als nicht möglich beendet, wartet auf die Adressen ([80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 15) | GE11 | Betreiberin, dann `base.html` und `llms.txt` |
| Produktnamen/-titel eindeutig, „custom print"-Kannibalisierung | IS03, IS10, IS23, BF21 | Shop-Admin |
| Search Console anbinden, Sitemap einreichen (Guide Schritt 1) — Konto nicht dokumentiert | — | Betreiberin + Werkzeug |
