---
bereich: seo
titel: SEO und GEO
stand: 2026-09-02
status: teilweise
fortschritt: 60
zusammenfassung: SEO-Technik live solide (90), Inhalt 70, GEO 61; llms.txt, KI-Crawler-Regeln, WebPage/Person/Breadcrumb-Knoten und 301 auf www liegen fertig im Zweig, nicht live.
offen: 9
quellen: GOOGLE_SEO_GUIDE.md, LOGBUCH.md, DOCUMENTATION.md, shop1/views/legal.py, shop1/seiten_stand.py, templates/base.html
---

# SEO und GEO — Luviq Universe

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

**Sichtbarkeit ist nicht gemessen** — keine Search-Console-Anbindung, keine Klick- oder
Positionsdaten (siehe [50-LOCAL-SEO.md](50-LOCAL-SEO.md)).

**Ziel-Suchbegriffe** (`meta name="keywords"` in `base.html`, laut `GOOGLE_SEO_GUIDE.md` massgeblich):
„Luviq", „Luviq Universe", „Second Hand Mode Alsfeld", „Vintage Mode Hessen", „handbemalte Kleidung
kaufen", „Upcycling Mode Deutschland", „1 of 1 Unikate". Der früher genannte Begriff „railway hosting
luviq" war falsch und ist gestrichen.

## Technik

| Baustein | Live (main, 02.09.2026) | Zweig |
|---|---|---|
| `robots.txt` | 200; sperrt `/shop-admin/`, `/profil/`, `/warenkorb/`, `/checkout/`, `/payment/`, `/verify/`, `/login/`, `/logout/`, `/register/`, `/password-reset/`, `/reset/`, `/resend-verification/`, `/delete-account/`; **Sitemap-Zeile vorhanden**; keine KI-Crawler genannt (GE02) | zusätzlich `Allow: /` und **13 Antwort-Crawler namentlich zugelassen** (u. a. GPTBot, PerplexityBot, ClaudeBot, Google-Extended, Applebot-Extended, CCBot, meta-externalagent, Bytespider) |
| `sitemap.xml` | 200, 14 URLs, `lastmod` nur bei 5 Produkten (2 Daten: 14.06./11.05.2026), Bild-Auszeichnung bei 5 (TS16, TS19); eine Klasse im Code (VL07) | `lastmod` für alle statischen Seiten aus dem Register `seiten_stand.py` (alle `2026-09-01`); Wissensseiten sobald freigegeben; 15 min Cache |
| `llms.txt` | **404** | vorhanden: Antwortabsatz (Ort, PLZ 36304, Versandzeiten), Eckdaten (Betreiberin, Anschrift, E-Mail, Instagram, Zahlungsarten, § 19), Seitenliste, Abschnitt Wissen nach Freigabe; 15 min Cache. `llms-full.txt` gibt es nicht (GE31) |
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
| `Organization`/`ClothingStore` mit `PostalAddress`, `GeoCoordinates`, `areaServed` (Hessen, DE, 18 Städte), `OfferCatalog` mit drei `Product`/`Offer`, `sameAs` Instagram | `base.html` | live; `sameAs` nur 1 Verweis (GE11); **Telefon fehlt** — es gibt keine (GE09, VL10) |
| `WebSite` | `base.html` | live |
| `ImageObject` (Logo) | `base.html` | live |
| `ItemList` (aktuelle Produkte) | `index.html` | live |
| `Product` + `Offer` + `Brand`, `BreadcrumbList` | `produkt_detail.html` | live (5 von 6 Leistungsseiten mit Offer, GE13; `/produkte/` ohne) |
| `LocalBusiness` mit `@id #organization` | `impressum.html` | live (`@id` Zweig) |
| `ContactPage`, `ContactPoint`, `FAQPage` (Versand, Erreichbarkeit) | `kontakt.html` | Zweig |
| `WebPage` mit `name` und `dateModified` aus `seiten_stand.py` | `base.html` über Kontextprozessor `seite` | Zweig (GE18 live: 0 von 13) |
| `Person` `#luisa`, `founder`/`author` verweisen darauf | `base.html` | Zweig (GE16 live: 0 von 10) |
| `BreadcrumbList` auf jeder Unterseite über zentralen Block `brotkrume_ld` | `base.html` + je Seite | Zweig (GE12 live: 6 von 12) |
| `FAQPage` je Wissensseite, deckungsgleich mit den `h2`-Fragen | `wissen/*.html` | Zweig |
| `speakable`, Antwort-zuerst-Baustein, IndexNow | — | fehlt (VL09, PJ13, GE19) |
| `AggregateRating` | — | fehlt, und es gibt keine belegte Bewertungszahl (KV09) |

`@id` tragen im Schnitt 66 % der Knoten (GE07, live).

## Inhalt und Keywords

Seitenbestand, Wortzahlen und Themen: [30-INHALTE.md](30-INHALTE.md). Kurz:

- **Dünn:** 11 von 13 Seiten unter 200 Eigenwörtern, 1.557 Eigenwörter gesamt gegen 12.000 Ziel (IS19, SU02). Der Zweig hebt neun Seiten an, ohne die Zielgrössen zu erreichen — die Designwache lässt keine neuen Absätze zu, nur volle bestehende.
- **Kannibalisierung:** „custom print" auf drei Produktseiten; zwei Produkte mit identischem Namen und Titel (IS23, IS03) — Pflege im Shop-Admin.
- **Ort:** „Alsfeld" bzw. „Hessen" in Startseiten-, Produkte-, Kontakt- und Impressumstitel; im Zweig auch in jedem Produkttitel.
- **Alt-Texte:** 21 von 39 schablonenhaft (IS25), Produkt-alt = Produktname.

## GEO und KI-Sichtbarkeit

| Regel | Live (02.09.2026) | Zweig |
|---|---|---|
| GE23 Antwort zuerst | 1 von 13 Seiten | Startseite, `/produkte/`, `/ueber_uns/`, `/gaestebuch/`, Produktseiten, Impressum, Wissensseiten mit Antwortabsatz |
| GE25 konkrete Zahlen | 0 von 5 | PLZ, Versandzeiten, § 19 auf allen Inhaltsseiten |
| GE24 Frage-Überschriften | 2 von 13 | Wissensseiten (6–7 Fragen je Seite), FAQ auf `/kontakt/` |
| GE16 Autor | 0 | `Person #luisa` als `author` |
| GE18 `dateModified` | 0 | Register, von Hand gepflegt (bewusst kein Build-Datum) |
| GE11 `sameAs` | 1 (Instagram) | unverändert — Unternehmensprofil, TikTok, Wikidata nicht dokumentiert |
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

## Offen

| Punkt | Regel | Wo |
|---|---|---|
| Zweig nach main + `CANONICAL_HOST` in Railway → 301 für den Apex, llms.txt, Schema-Knoten, Meta live | TS11, GE30, GE12, GE16, GE18 | Merge + Railway |
| Freigabe der Wissensbeiträge → aus `noindex`, in Sitemap und llms.txt | SU04, SU07, VL11 | Betreiberin, dann `views/wissen.py` |
| Impressum: `noindex` **und** Sitemap-Eintrag widersprechen sich | SU11 | `legal.py` oder `impressum.html` |
| Überschriftensprünge `h1 → h3` auf 10 Bestandsseiten — nur mit bewusster Änderung der Designwache-Referenz | IS14, BF15 | Templates + `aufbau_referenz.json` |
| Sitemap in drei Klassen segmentieren, Sitemap-Index, Bild-Erweiterung für alle Einträge | VL07, TS19 | `legal.py` |
| `speakable`, Antwort-Baustein, IndexNow, `llms-full.txt` | VL09, PJ13, GE19, GE31 | |
| `sameAs` erweitern (Unternehmensprofil, TikTok, weitere Profile) — Adressen nicht dokumentiert | GE11 | Betreiberin |
| Produktnamen/-titel eindeutig, „custom print"-Kannibalisierung | IS03, IS10, IS23, BF21 | Shop-Admin |
| Search Console anbinden, Sitemap einreichen (Guide Schritt 1) — Konto nicht dokumentiert | — | Betreiberin + Werkzeug |
