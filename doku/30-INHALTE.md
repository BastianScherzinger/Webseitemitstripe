---
bereich: inhalte
titel: Inhalte und Seitenbestand
stand: 2026-09-02
status: teilweise
fortschritt: 40
zusammenfassung: Live 14 URLs mit 1.557 Eigenwörtern (85 % dünne Seiten); der Zweig füllt neun Seiten mit Auskunft und bringt drei Wissensbeiträge, die bis zur Freigabe auf noindex stehen.
offen: 7
quellen: LOGBUCH.md, shop1/seiten_stand.py, shop1/views/wissen.py, shop1/views/legal.py
---

# Inhalte — Luviq Universe

## Seitenbestand

**Live (main, Sitemap 02.09.2026): 14 URLs** — 9 statische Seiten ohne `lastmod`, 5 Produktseiten mit `lastmod`.

| URL | Seite | Eigenwörter live (Messung 02.09.2026) | Ziel | Titel live |
|---|---|---:|---:|---|
| `/` | Startseite | 390 | 700 | Luviq Universe – Handbemalte Second Hand Mode aus Alsfeld \| Hessen (66 Z.) |
| `/produkte/` | Produktübersicht „The Drop" | 62 | 600 | Second Hand & Vintage Mode kaufen \| Luviq Universe – Alsfeld, Hessen (68 Z.) |
| `/produkt/custom-hoodie-mit-print/` | Produkt, 59,00 € | 26 | 600 | |
| `/produkt/custom-print-hoodie-1/` | Produkt, 59,00 € | 25 | 600 | „Custom print hoodie kaufen – Luviq Universe" — **doppelt** mit `custom-print-hoodie` |
| `/produkt/custom-pants-sold/` | Produkt, 69,99 € (verkauft) | 25 | 600 | |
| `/produkt/custom-print-jacke/` | Produkt, 69,00 € | 25 | 600 | |
| `/produkt/custom-print-hoodie/` | Produkt, 58,96 € | 25 | 600 | |
| `/kontakt/` | Kontakt, Formular (Name, E-Mail, Betreff, Nachricht) | 91 | | Kontakt – Luviq Universe \| Handbemalte Vintage Mode |
| `/ueber_uns/` | Über uns | 194 | | (70 Z.) |
| `/liefergebiet/` | Liefergebiet | 259 | | |
| `/gaestebuch/` | Gästebuch (Kommentare angemeldeter Nutzer, Likes) | 70 | | |
| `/impressum/` | Impressum — **`noindex, follow`, steht trotzdem in der Sitemap** | | | Impressum – Luviq Universe \| Alsfeld, Hessen |
| `/datenschutz/` | Datenschutz | 185 | | (28 Z.) |
| `/agb/` | AGB inkl. Widerrufsbelehrung (ohne Muster-Widerrufsformular) | 179 | | (20 Z.) |

Summe: **1.557 Eigenwörter** über 13 abgerufene Seiten (von 2.434 Wörtern Gesamttext), Zielgrösse 12.000 (SU02); im Schnitt 120 je Seite, Ziel 400 (SU06); 11 von 13 Seiten unter 200 Wörtern (IS19); Rahmenanteil auf Produktseiten 73 % (GE29). Die Zahlen gelten für **main**; der Zweig ist live nicht gemessen.

**Nicht in der Sitemap, aber erreichbar:** `/login/`, `/register/`, `/profil/`, `/warenkorb/`, `/checkout/`, `/payment/…`, `/verify/…`, `/password-reset/…`, `/delete-account/`, `/newsletter/subscribe/`, `/shop-admin/…` — alle per `robots.txt` gesperrt. `/produkt/<id>/` leitet auf die Slug-URL um (Altlink-Kompatibilität); `/produkt/` → 301 auf `/produkte/` (Zweig; live 404).

**Zweig zusätzlich:** `/wissen/` (Übersicht) und drei Beiträge — alle `freigegeben: False`, daher `noindex, follow`, nicht in Sitemap und llms.txt, aber erreichbar und getestet.

| URL (Zweig) | Titel (= h1) | Wörter (Logbuch) | Offene Sachangabe |
|---|---|---:|---|
| `/wissen/pflege-handbemalte-kleidung/` | Wie pflege ich handbemalte Kleidung? | 821 | 30 °C, kein Trockner, kein Weichspüler, Bügeln nur von links |
| `/wissen/upcycling-mode-second-hand-vintage/` | Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand? | 941 | keine strittige Zahl; Auflage nennt alle drei |
| `/wissen/groesse-bei-einzelstuecken/` | Wie finde ich bei Einzelstücken die richtige Größe? | 890 | „fünf Zentimeter Unterschied in der Brustweite sind eine ganze Grösse" |

Jeder Beitrag: Antwort zuerst, sechs bis sieben Fragen als `h2`, `FAQPage` deckungsgleich, Verweise auf Über uns, Liefergebiet, AGB, Kontakt. Kein neuer Beitrag ohne Eintrag in `WISSEN_BEITRAEGE`, `seiten_stand.py`, `WISSEN_SEITEN` (`legal.py`), `tests/_basis.py`, `FAQ_SEITEN`, `MINDESTWOERTER` und der Aufbau-Referenz (`CLAUDE.md`).

## Themen und Silos

| Silo | Seiten | Stand |
|---|---:|---|
| `/produkt/` (Einzelstücke) | 5 | hält 56 % aller Unterseiten (SU10); Übersicht ist `/produkte/`, der Pfad `/produkt/` selbst hat live keine Seite (SU09; Zweig: 301) |
| `/produkte/` | 1 | Kategorieseite; im Zweig mit Auskunft zu 1-of-1, Bestellung, Zahlung, Versand |
| `/wissen/` | 0 live / 3 + Übersicht im Zweig | Ratgeber; Zielgrösse 3 (SU04) — erreicht, sobald freigegeben |
| Betrieb | `/ueber_uns/`, `/liefergebiet/`, `/kontakt/`, `/gaestebuch/` | je eine Seite (SU08) |
| Recht | `/impressum/`, `/datenschutz/`, `/agb/` | |

Hauptbegriff „custom print" liegt auf drei Produktseiten (IS23) — Folge der Produktnamen im Shop-Admin, nicht der Templates. Zwei Produkte tragen denselben Namen („Custom print hoodie") und damit denselben Titel (IS03, BF21); die Titel werden aus dem Produktnamen erzeugt (`Produkt.save()` vergibt Slug mit Suffix `-1`). Abhilfe: unterschiedliche Namen oder `seo_titel` im Standard-Admin (Test in `test_daten`, Schritt 45).

Keine Ortsseiten (VL12: 0/1) — für einen Online-Shop ohne Ladengeschäft fraglich, ob sinnvoll; nicht entschieden.

## Texte und Bilder

**Belegte Sachangaben**, die überall gleich verwendet werden (Quellen: `agb.html`, `kontakt.html`, `liefergebiet.html`, `ueber_uns.html`, Impressum):
Luisa Brehler · Grünberger Str. 16, 36304 Alsfeld, Hessen · brehlerluisa@gmail.com · Instagram `luviq.universe` · kein Ladengeschäft · Pinsel und Textilfarbe auf getragener Second-Hand-Kleidung · 1-of-1, keine Nachbestellung · PayPal oder Vorab-Überweisung · Endpreise, § 19 UStG · Versand deutschlandweit in der Regel 1–2 Werktage, in Hessen meist nach 1–3 Werktagen zugestellt · Widerruf nach AGB.

**Nicht belegt und deshalb nicht behauptet:** dass verkaufte Stücke aus dem Shop verschwinden (`views/shop.py` filtert nur `aktiv`); Markt- oder Umweltzahlen; die „5.0 ★★★★★" im Bewertungskasten; eine Telefonnummer; Öffnungs-/Antwortzeiten (live steht auf `/kontakt/` „Operationell: 24/7" und „Wir antworten schneller als das Licht" — Platzhaltertext auf main).

**Was der Zweig an Text geändert hat** (Logbuch Schritte 11–13, 21–24): Startseite beginnt mit einer zitierfähigen Antwort („Was ist Luviq Universe?"), drei Feature-Absätze mit Auskunft; `/produkte/` Absatz auf ~100 Wörter; `/ueber_uns/`, `/gaestebuch/`, Produktseiten (statischer Zusatz), Impressum (Unterzeile); Meta-Beschreibungen aller neun Inhaltsseiten auf 157–171 Zeichen mit Aufforderung; Ortsbezug „Alsfeld" im automatischen Produkttitel; Produkt-Metaangaben auf 60/160 Zeichen begrenzt. Drei Beschriftungen ohne Aussage ersetzt („Status: Active", „Galaxy-Wide Delivery", „Premium Energy Matrix").

**Bilder (Messung 02.09.2026, live):** 44 Bilder, 0 in WebP/AVIF, 0 mit `srcset`, 10 ohne `width`/`height`, 0 ohne `alt`; 21 von 39 alt-Texten schablonenhaft („Custom print hoodie", „Luviq Universe Logo") — die Produkt-alt-Texte kommen aus dem Produktnamen. Zweig: statische Bilder als WebP in mehreren Breiten, alt-Texte für Logo/Karussell/Werbebilder umgeschrieben (Schritt 8); Produktbilder bleiben Cloudinary-Originale ohne `srcset`.

**Werbung:** Modell `Werbung` (Titel, Bild, URL, Zeitraum) aus der `pystore`-Datenbank, Impressionen/Klicks in `WerbungStat`; wird auf der Startseite ausgespielt; Pflege im Shop-Admin `/shop-admin/werbung/`.

## Fehlende Inhalte

| Was fehlt | Beleg (Messung 02.09.2026) | Regel |
|---|---|---|
| Ratgeber live — 0 Wissensseiten (im Zweig 3, `noindex` bis Freigabe) | Zielgrösse 3 | SU04, SU07, VL11, VL12 |
| Umfang: 13 statt 30 rankfähige Seiten; Startseite 390/700, Produktseiten 25/600 Wörter | | SU01, IS18, IS17 |
| Konkrete Zahlen auf `/`, `/datenschutz/`, `/agb/`, `/ueber_uns/`, `/liefergebiet/` (live) — Zweig ergänzt Versandzeiten, PLZ, § 19 | 0 von 5 | GE25 |
| Frage-Überschriften (live 2 von 13 Seiten; Zweig: Wissensseiten durchgehend) | | GE24 |
| Über-uns-Seite mit **benannter Person** im Sinne der Vorlage (Luisa Brehler steht als Text, im Zweig auch als `Person`-Knoten `#luisa`) | | VL11 |
| Muster-Widerrufsformular als eigene, aus dem Fuss verlinkte Seite | Widerrufsbelehrung nur in `/agb/` | RE09 |
| Erklärung zur Barrierefreiheit (BFSG) — sofern nicht als Kleinstunternehmen ausgenommen; **nicht dokumentiert**, ob die Ausnahme greift | | RE12 |
| Öffnungs-/Erreichbarkeitszeiten auf Startseite und Kontakt — es gibt keine belegten | | KV11 |
| Eigene Danke-Seite nach dem Kontaktformular | | KV07 |
| Datenschutzhinweis unter dem Kontaktformular; Honigtopf | 0 von 1 | KV05, KV06 |

## Offen

1. **Freigabe der drei Wissensbeiträge** durch die Betreiberin → `'freigegeben': True` (siehe [80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden).
2. Zweig mergen, damit die neuen Texte, Meta-Angaben und die Platzhalter-Korrektur auf `/kontakt/` live sind.
3. Impressum aus der Sitemap nehmen **oder** `noindex` entfernen — heute widersprechen sich beide (SU11).
4. Produktnamen im Shop-Admin eindeutig machen („Custom print hoodie" ×2) — Pflegeaufgabe der Betreiberin, oder `seo_titel` setzen.
5. Weitere Wissensbeiträge nach Kundenfragen (Versand, Rückgabe, Bestellablauf) — erst nach Freigabe der ersten drei.
6. Muster-Widerrufsformular als eigene Seite.
7. Entscheidung Öffnungs-/Antwortzeiten und Telefonnummer — nur die Betreiberin kann sie nennen.
