---
bereich: inhalte
titel: Inhalte und Seitenbestand
stand: 2026-09-11
status: teilweise
fortschritt: 40
zusammenfassung: Live 14 URLs mit 1.557 Eigenwörtern (85 % dünne Seiten); main füllt neun Seiten mit Auskunft, bringt sechs Wissensbeiträge (drei belegt und indexiert, drei warten auf die Freigabe) und hält jede indexierbare Seite über 200 Wörtern. Seit IS18 (11.09.2026, Zweig sofort/2026-09-11-is18, nicht gemergt) erreichen Startseite, Produktübersicht und Wissensübersicht laut Commit mit belegtem Fliesstext die Zielgrösse ihrer Seitenart — nur die Produktseiten brauchen weiter eine eigene Beschreibung je Einzelstück.
offen: 8
quellen: LOGBUCH.md, shop1/seiten_stand.py, shop1/views/wissen.py, shop1/views/legal.py, shop1/tests/test_inhalt.py
---

# Inhalte — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Bereichswert **Substanz** des Laufs vom 02.09.2026 (Regelstand `2026-09-02a`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße.*

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

**Zweig zusätzlich:** `/wissen/` (Übersicht) und sechs Beiträge. Die drei ersten stehen auf `freigegeben: False`, also `noindex, follow` und nicht in Sitemap und llms.txt, sind aber erreichbar und getestet; die drei aus SU04 (07.09.2026) sind `freigegeben: True` und damit indexiert — sie geben ausschliesslich wieder, was an anderer Stelle dieser Seite belegt ist, und brauchen keine Zuarbeit. Die Übersicht ist damit indexierbar.

| URL (Zweig) | Titel (= h1) | Wörter | Index | Offene Sachangabe |
|---|---|---:|---|---|
| `/wissen/pflege-handbemalte-kleidung/` | Wie pflege ich handbemalte Kleidung? | 821 | nein | 30 °C, kein Trockner, kein Weichspüler, Bügeln nur von links |
| `/wissen/upcycling-mode-second-hand-vintage/` | Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand? | 941 | nein | keine strittige Zahl; Auflage nennt alle drei |
| `/wissen/groesse-bei-einzelstuecken/` | Wie finde ich bei Einzelstücken die richtige Größe? | 890 | nein | „fünf Zentimeter Unterschied in der Brustweite sind eine ganze Grösse" |
| `/wissen/bestellen-und-bezahlen/` | Wie bestelle und bezahle ich bei Luviq Universe? | 1.129 | **ja** | keine — Belege: `cart.py`, `checkout.py`, `forms.py`, `agb.html` § 2/§ 4, `liefergebiet.html` |
| `/wissen/widerruf-und-ruecksendung/` | Widerruf und Rücksendung: was gilt bei einem Einzelstück? | 1.034 | **ja** | keine — Belege: `agb.html` § 3/§ 4/§ 5, Impressum, Datenschutz; Rückporto und Rückzahlungsfrist stehen als offene Frage **im Text** |
| `/wissen/konto-und-daten/` | Was speichert der Shop – und warum braucht der Kauf ein Konto? | 1.000 | **ja** | keine — Belege: `datenschutz.html`, `forms.py`, `settings.py` (`AXES_*`), `views/auth.py` |

Jeder Beitrag: Antwort zuerst, sechs bis zehn Fragen als `h2`, `FAQPage` deckungsgleich, Verweise auf Über uns, Liefergebiet, AGB, Kontakt, Datenschutz. Kein neuer Beitrag ohne Eintrag in `WISSEN_BEITRAEGE`, `seiten_stand.py`, `WISSEN_SEITEN` (`legal.py`), `tests/_basis.py`, `FAQ_SEITEN`, `MINDESTWOERTER` und der Aufbau-Referenz (`CLAUDE.md`).

## Themen und Silos

| Silo | Seiten | Stand |
|---|---:|---|
| `/produkt/` (Einzelstücke) | 5 | hält 56 % aller Unterseiten (SU10); Übersicht ist `/produkte/`, der Pfad `/produkt/` selbst hat live keine Seite (SU09; Zweig: 301) |
| `/produkte/` | 1 | Kategorieseite; im Zweig mit Auskunft zu 1-of-1, Bestellung, Zahlung, Versand |
| `/wissen/` | 0 live / 6 + Übersicht im Zweig | Ratgeber; Zielgrösse 3 (SU04) im Zweig **erreicht**: drei belegte Beiträge indexiert, drei warten auf Freigabe |
| Betrieb | `/ueber_uns/`, `/liefergebiet/`, `/kontakt/`, `/gaestebuch/` | je eine Seite (SU08) |
| Recht | `/impressum/`, `/datenschutz/`, `/agb/` | |

Hauptbegriff „custom print" liegt auf drei Produktseiten (IS23) — Folge der Produktnamen im Shop-Admin, nicht der Templates. Zwei Produkte tragen denselben Namen („Custom print hoodie") und damit denselben Titel (IS03, BF21); die Titel werden aus dem Produktnamen erzeugt (`Produkt.save()` vergibt Slug mit Suffix `-1`). Abhilfe: unterschiedliche Namen oder `seo_titel` im Standard-Admin (Test in `test_daten`, Schritt 45).

Keine Ortsseiten (VL12: 0/1) — für einen Online-Shop ohne Ladengeschäft fraglich, ob sinnvoll; nicht entschieden.

## Texte und Bilder

**Belegte Sachangaben**, die überall gleich verwendet werden (Quellen: `agb.html`, `kontakt.html`, `liefergebiet.html`, `ueber_uns.html`, Impressum):
Luisa Brehler · Grünberger Str. 16, 36304 Alsfeld, Hessen · brehlerluisa@gmail.com · Instagram `luviq.universe` · kein Ladengeschäft · Pinsel und Textilfarbe auf getragener Second-Hand-Kleidung · 1-of-1, keine Nachbestellung · PayPal oder Vorab-Überweisung · Endpreise, § 19 UStG · Versand deutschlandweit in der Regel 1–2 Werktage, in Hessen meist nach 1–3 Werktagen zugestellt · Widerruf nach AGB.

**Nicht belegt und deshalb nicht behauptet:** dass ein Stück schon mit der Bestellung aus dem Shop verschwindet (`views/shop.py` filtert nur `aktiv`; abgeschaltet wird erst nach der Zahlung — bei PayPal in `checkout.py:231`, bei Vorab-Überweisung erst mit dem Eintrag „bezahlt" im Panel, `admin_views.py:746-751`; so steht es seit IS18 auch auf `/` und `/produkte/`. Beide Stellen suchen das Stück über seinen Namen, siehe `EIG08` in [80-AUFGABEN.md](80-AUFGABEN.md)); Markt- oder Umweltzahlen; die „5.0 ★★★★★" im Bewertungskasten; eine Telefonnummer; Öffnungs-/Antwortzeiten (live steht auf `/kontakt/` „Operationell: 24/7" und „Wir antworten schneller als das Licht" — Platzhaltertext auf main).

**Was der Zweig an Text geändert hat** (Logbuch Schritte 11–13, 21–24): Startseite beginnt mit einer zitierfähigen Antwort („Was ist Luviq Universe?"), drei Feature-Absätze mit Auskunft; `/produkte/` Absatz auf ~100 Wörter; `/ueber_uns/`, `/gaestebuch/`, Produktseiten (statischer Zusatz), Impressum (Unterzeile); Meta-Beschreibungen aller neun Inhaltsseiten auf 157–171 Zeichen mit Aufforderung; Ortsbezug „Alsfeld" im automatischen Produkttitel; Produkt-Metaangaben auf 60/160 Zeichen begrenzt. Drei Beschriftungen ohne Aussage ersetzt („Status: Active", „Galaxy-Wide Delivery", „Premium Energy Matrix").

**Paket 135 (08.09.2026, `fd82efd`, `2b26108`, `b35f6e4`) — GE23, GE25, IS19.** Drei
Textpunkte, **kein einziger Eingriff in den Aufbau**: kein neues Element, keine
geänderte Klasse, keine Kennung. Der ganze Zuwachs steht in Absätzen, die es schon
gab — die Designwache erfasst Tags, Kennungen, Klassen, Überschriften und
Elementzahlen, den Fliesstext darin bewusst nicht.

- **Antwort zuerst (GE23):** jeder erste Absatz nennt im ersten Satz, was die Seite
  ist, und trägt eine belegte Zahl. `/produkte/` und `/gaestebuch/` ziehen die
  Bestandszahl aus der Datenbank (`produkte_liste|length`, `comments|length`),
  `/kontakt/`, `/ueber_uns/` und `/liefergebiet/` nennen PLZ 36304 und Versanddauer,
  `/datenschutz/` seine vier Abschnitte, `/agb/` seine fünf Paragraphen und die
  14-Tage-Frist, jede Produktseite Name, Preis und Herkunft aus dem Datensatz.
- **Zahlen (GE25):** ergänzt sind nur Angaben mit Beleg im Projekt — 14 Tage
  Widerruf (§ 5 AGB, dort jetzt zusätzlich in Ziffern), Versand 1–2 und Zustellung
  1–3 Werktage, 5 Minuten Sperrfrist je Pfad und ein Besuch je Sitzung und Tag
  (`middleware.py`), 14 Tage Laufzeit des Sitzungs-Cookies (`SESSION_COOKIE_AGE`),
  Zahl der Wissensbeiträge und der genannten Orte aus dem Kontext. **Nicht** genannt:
  Preisrahmen, Rückporto, Antwort- und Erreichbarkeitszeiten — sie stehen nirgends im
  Projekt (siehe „Nicht belegt und deshalb nicht behauptet").
- **Dünne Seiten (IS19):** keine indexierbare Seite bleibt unter 200 Wörtern.
  Gemessen im Inhaltsbereich mit einem Produkt und ohne Kommentare (die Zahlen sind
  in `MINDESTWOERTER` in `shop1/tests/test_inhalt.py` festgehalten, nicht mit den
  „Eigenwörtern" der Messung oben vergleichbar):

| Seite | vorher | nachher |
|---|---:|---:|
| `/produkte/` | 111 | 238 |
| `/kontakt/` | 135 | 245 |
| `/gaestebuch/` | 99 | 300 |
| Produktseite (`/produkt/bemalte-bomberjacke/`) | 103 | 211 |
| `/agb/` | 177 | 240 |
| `/ueber_uns/` · `/liefergebiet/` · `/datenschutz/` · `/wissen/` | — | 392 · 312 · 441 · 425 |
| `/impressum/` | 75 | 75 (`noindex`, nicht in Sitemap und llms.txt) |

Inhaltlich ist der Zuwachs der Kaufablauf, die Widerrufsfrist, die Beschaffenheit der
gebrauchten Basisteile (§ 3 AGB) und der Weg für Fragen zu einem einzelnen Stück —
alles aus AGB, Datenschutzerklärung und dem Code des Bestellvorgangs. **Was das
nicht löst:** auf den Produktseiten ist dieser Zuwachs auf allen fünf Stücken
derselbe Text. Er hebt die Wortzahl, sagt aber nichts über das einzelne Teil und
senkt deshalb die Textgleichheit zwischen den Produktseiten (IS21) nicht.

**Paket 165 (11.09.2026, `2591fde`, Zweig `sofort/2026-09-11-is18`, nicht gemergt) —
IS18, anders eingebaut.** Der Umfang je Seitenart (Startseite 700, Kategorieseite 600,
Wissensübersicht 900 Wörter) ist für die drei Seiten aufgeholt, die die Beschreibung je
Stück gar nicht ausgeben. Wie bei IS19 steht der ganze Zuwachs in Absätzen, die es schon
gab — kein Element, keine Klasse, keine Kennung, keine Überschrift. Gezählt hat der Bau
nach dem Verfahren des Werkzeugs (Text in `<main>` ohne Navigation, Kopf, Fuss, `aside`,
Skript und Stil) und **ohne ein Produkt im Bestand**, damit der Umfang nicht mit jedem
verkauften Stück wieder unter die Grenze fällt; die Zahlen vorher und nachher stehen im
Commit und in `LOGBUCH.md`, live gezählt ist der Stand nicht.

| Seite | Wo der Text dazukam | Worüber |
|---|---|---|
| `/` | die drei Feature-Absätze, Absatz von Luisa Brehler, Newsletter-Absatz, Anmeldehinweis im Kommentarbereich (`_reviews_map.html`, Kompaktfassung) | Unregelmäßigkeiten nach § 3 AGB, eine Größe je Basisteil, Kauf eines vorhandenen Stücks statt Auftrag, bis zu acht neueste Stücke auf der Startseite, Bestellablauf, PayPal-Prüfung und Bankdaten per E-Mail, Versanddauer, Widerruf ab Ankunft der Ware (§ 5), Bestellstand im Profil, Newsletter über Brevo ohne Konto, Kommentare öffentlich mit Benutzername und Datum |
| `/produkte/` | Einleitungsabsatz | Reihenfolge der Karten, kein Warenkorb-Knopf auf der Übersicht, Menge bis zum Bestand, keine Reservierung durch den Warenkorb, Abschalten nach der Zahlung (PayPal und Vorab-Überweisung getrennt), keine weitere Zahlungsart, Eigentumsvorbehalt (§ 4), kein Umtausch, Widerruf ohne Formvorgabe mit Rücksendeanschrift, Rückporto ungeregelt, echter Mangel gegen § 3, Registrierungsfelder, Bestellbestätigung |
| `/wissen/` | Einleitungsabsatz, die zwei Absätze unter „Woher die Angaben stammen" | Kernantworten der drei belegten Beiträge (Konto, Zahlung, Widerrufsfrist, § 3, Anmeldesperre, Konto löschen); Zuordnung jeder Angabe zu ihrer Quelle (AGB, Impressum, Datenschutzerklärung, Liefergebiet, Shop-Code); Pflichtfelder des Bestellvorgangs und des Kontaktformulars; kein eigenes Feld für Maße oder Material |

Jede Angabe hat eine Fundstelle im Projekt (Belegliste in `LOGBUCH.md`, Paket 165);
**nicht** genannt sind weiter Versandkosten, Rückporto und eine Rückzahlungsfrist.
Die Nachbesserung zu Paket 165 hat zwei Sätze berichtigt, die die Gegenprüfung nicht
trug: `/produkte/` behauptete, das Foto stehe erst auf der Detailseite (die Karten zeigen
es), und `/wissen/` erklärte Antworten der Betreiberin auf eine Nachfrage für verbindlich
(nirgends belegt, quer zu § 2 AGB). Gezählt ohne Produkt bleiben danach `/` 732,
`/produkte/` 616 und `/wissen/` 921 Wörter.
`MINDESTWOERTER` hält den Stand in der Zählung der Suite fest (`/` 690, `/produkte/` 595,
`/wissen/` 895), `seiten_stand.py` führt `home`, `produkte` und `wissen` auf dem
11.09.2026. **Bewusst ungefüllt bleiben die fünf Produktseiten:** noch mehr gleicher Text
auf allen Stücken höbe die Wortzahl und zugleich die Textgleichheit (IS21) — ihren Umfang
kann nur eine eigene Beschreibung je Stück liefern (Offen Nr. 8). Nebenbefund zum Aussehen
von `/produkte/`: [20-DESIGN.md](20-DESIGN.md).

**Bilder (Messung 02.09.2026, live):** 44 Bilder, 0 in WebP/AVIF, 0 mit `srcset`, 10 ohne `width`/`height`, 0 ohne `alt`; 21 von 39 alt-Texten schablonenhaft („Custom print hoodie", „Luviq Universe Logo") — die Produkt-alt-Texte kommen aus dem Produktnamen. Zweig: statische Bilder als WebP in mehreren Breiten, alt-Texte für Logo/Karussell/Werbebilder umgeschrieben (Schritt 8); Produktbilder bleiben Cloudinary-Originale ohne `srcset`.

**Werbung:** Modell `Werbung` (Titel, Bild, URL, Zeitraum) aus der `pystore`-Datenbank, Impressionen/Klicks in `WerbungStat`; wird auf der Startseite ausgespielt; Pflege im Shop-Admin `/shop-admin/werbung/`.

## Fehlende Inhalte

| Was fehlt | Beleg (Messung 02.09.2026) | Regel |
|---|---|---|
| Ratgeber live — 0 Wissensseiten (im Zweig 6: drei indexiert, drei `noindex` bis Freigabe) | Zielgrösse 3 | SU04 (Zweig erfüllt), SU07, VL11, VL12 |
| Umfang: 13 statt 30 rankfähige Seiten; Startseite 390/700, Produktseiten 25/600 Wörter — **Umfang je Seitenart im Zweig** (11.09.2026, `2591fde`) für `/`, `/produkte/` und `/wissen/` aufgeholt, für die Produktseiten nicht | | SU01, IS18 (Zweig: 3 Seitenarten), IS17 |
| Konkrete Zahlen auf `/`, `/datenschutz/`, `/agb/`, `/ueber_uns/`, `/liefergebiet/` (live) — **im Zweig ergänzt** (08.09.2026): Versandzeiten, PLZ, § 19, 14-Tage-Frist, Cookie-Laufzeit, Dedup-Fenster der Besuchszählung | 0 von 5 | GE25 (Zweig erfüllt) |
| Eigene Beschreibung je Einzelstück — der Zusatz aus IS19 ist auf allen fünf Produktseiten wortgleich | Produktseiten 211 W, davon nichts über das einzelne Teil | SU06, IS18, IS21 |
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
5. Weitere Wissensbeiträge nach Kundenfragen. Bestellablauf, Widerruf und Konto sind mit SU04 (07.09.2026) gebaut; alles Weitere braucht Angaben der Betreiberin — namentlich die Kosten der Rücksendung und die Frist der Rückzahlung, die heute in `/wissen/widerruf-und-ruecksendung/` ausdrücklich als ungeklärt stehen.
6. Muster-Widerrufsformular als eigene Seite.
7. Entscheidung Öffnungs-/Antwortzeiten und Telefonnummer — nur die Betreiberin kann sie nennen.
8. **Eine eigene Beschreibung je Einzelstück** (`Produkt.beschreibung` im Shop-Admin). Der Zuwachs aus IS19 (08.09.2026) beschreibt den Kauf, nicht das Stück, und steht wortgleich auf allen fünf Produktseiten — siehe [80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 14. Seit IS18 (11.09.2026) ist das der einzige offene Teil des Umfangs je Seitenart.
