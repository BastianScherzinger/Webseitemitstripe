---
bereich: inhalte
titel: Inhalte und Seitenbestand
stand: 2026-09-18
status: teilweise
fortschritt: 40
zusammenfassung: Paket 248 (18.09.2026, Zweig sofort/2026-09-18-re15-und-2-weitere, d58a96c, 329dbc4 und 2f51192 vor main = 8114dd9, nicht gemergt) ändert drei Textstellen: der Absendeknopf des Bestellformulars heisst „Zahlungspflichtig bestellen" statt „Continue to Payment →" und deckt sich damit mit den AGB, die diese Beschriftung schon immer nennen (RE21); der Abschnitt „Hosting & Infrastruktur" der Datenschutzerklärung führt Google Maps nicht mehr unter den beim Aufruf nachgeladenen Anbietern, sondern beschreibt Platzhalter und Klick (RE17), und seiten_stand.py führt datenschutz seitdem mit 2026-09-18 statt 2026-09-01. Der sichtbare Platzhaltertext „Karte laden" entsteht erst im Skript von base.html und steht in keiner Vorlage, zählt also in keiner Wortzahl mit. Paket 243 (17.09.2026, Zweig sofort/2026-09-17-kv05-und-2-weitere, b736994, 06503a7 und 9cd641f vor main = origin/main = 911c26a, nicht gemergt) setzt neuen sichtbaren Text auf /kontakt/: zwischen Nachrichtenfeld und Absendeknopf steht jetzt der Datenschutzhinweis (KV05) — was gespeichert wird, dass die Antwort über Brevo hinausgeht, wo es Auskunft und Löschung gibt und unter welcher Adresse die Datenschutzerklärung steht; jede Angabe stammt aus legal/datenschutz.html, die Adresse steht als Text statt als Link, weil die Designwache die Elemente zählt. Das Register seiten_stand.py führt kontakt seitdem mit 2026-09-17 (vorher 2026-09-01), lastmod und dateModified der Seite stimmen also wieder. KV09 (Vertrauenssignale auf der Startseite) ist im selben Paket nicht möglich: Gründungsjahr, Zertifikate und eine belegte Bewertungszahl gibt es im Projekt nicht. Paket 216 (17.09.2026, Zweig sofort/2026-09-17-fo03-und-2-weitere, seit 8717afe auf main) ändert auf /kontakt/ nur Beschriftungen und einen Satz — die vier Feldbeschriftungen tragen einen Stern, der Einleitungsabsatz erklärt ihn („Im Formular sind alle vier Felder Pflichtfelder und mit einem Stern (*) gekennzeichnet."); seiten_stand.py führte kontakt dabei weiter mit 2026-09-01 — mit 9cd641f (Paket 243) ist das nachgezogen. Live 14 URLs mit 1.557 Eigenwörtern (85 % dünne Seiten); main füllt neun Seiten mit Auskunft, bringt sechs Wissensbeiträge (drei belegt und indexiert, drei warten auf die Freigabe) und hält jede indexierbare Seite über 200 Wörtern. Seit IS18 (Merge 1a5f36b auf main) erreichen Startseite, Produktübersicht und Wissensübersicht laut Commit mit belegtem Fliesstext die Zielgrösse ihrer Seitenart — nur die Produktseiten brauchen weiter eine eigene Beschreibung je Einzelstück. Der Zweig sofort/2026-09-11-kv07-und-2-weitere (nicht gemergt) bringt die Danke-Seite /kontakt/danke/ (KV07): noindex, Text nur mit Angaben, die schon auf kontakt.html stehen. SU08 (jeder Themenbereich mit mehr als einer Seite) ist am 12.09.2026 geprüft und als nicht möglich beendet: /produkte/ ist die Übersicht zu /produkt/<slug>/, und /gaestebuch/, /ueber_uns/ und /liefergebiet/ bräuchten Inhalte, die es im Projekt nicht gibt (kein Kategoriefeld am Produktmodell, 16 Seiten im Register) — keine Zeile Code geändert. GE15 (12.09.2026, Zweig sofort/2026-09-12-mw15-und-2-weitere, nicht gemergt) gibt den sechs Beiträgen einen Article-Knoten samt Autorin und Erscheinungsdatum aus dem neuen Registerfeld veroeffentlicht und der Übersicht eine ItemList; sichtbarer Text und Wortzahlen bleiben unverändert.
offen: 9
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

**Zweig `sofort/2026-09-11-kv07-und-2-weitere` zusätzlich (KV07, `2d78a55`, nicht gemergt):** `/kontakt/danke/` — Ziel nach dem Absenden des Kontaktformulars, auch direkt abrufbar, `noindex, follow`, weder in Sitemap noch in `llms.txt`. Titel „Nachricht abgeschickt – Luviq Universe", `h1` „Danke für deine Nachricht". Der Text nennt nur, was schon auf `kontakt.html` steht: die Nachricht geht an Luisa Brehler, geantwortet wird per E-Mail an die Adresse aus dem Formular, eine Telefonnummer gibt es nicht, `brehlerluisa@gmail.com` als zweiter Weg; dazu Verweise auf die drei freigegebenen Wissensbeiträge (Bestellen und Bezahlen, Widerruf und Rücksendung, Konto und Daten). **Keine Antwortzeit** — im Projekt steht keine. Die Seite sagt „abgeschickt", nicht „zugestellt", weil der Versand erst im Thread scheitern kann (`EIG10`). Sie steht nicht in `seiten_stand.py`, trägt deshalb kein `dateModified`, und zählt nicht zu `INHALTSSEITEN` (keine Wortzahl-Vorgabe).

**Zweig `sofort/2026-09-17-kv05-und-2-weitere` zusätzlich (KV05, `b736994`, nicht gemergt):** neuer sichtbarer Absatz auf `/kontakt/`, zwischen Nachrichtenfeld und Absendeknopf. Wortlaut: „Datenschutz: Name, E-Mail-Adresse, Betreff und Nachricht werden gespeichert und zur Beantwortung deiner Anfrage über den Dienstleister Brevo per E-Mail weitergeleitet. Auskunft und Löschung jederzeit formlos per E-Mail an brehlerluisa@gmail.com. Was mit den Daten geschieht, steht vollständig in der Datenschutzerklärung unter /datenschutz/ – in der Fußzeile jeder Seite verlinkt." Jede Angabe stammt aus `legal/datenschutz.html` (Brevo, Auskunft und Löschung) und aus dem Modell `KontaktAnfrage` (`MW18`) — **keine Rechtsgrundlage genannt**, weil die Erklärung für Kontaktanfragen keine nennt, und **keine Aufbewahrungsfrist**, weil es keine gibt (siehe [80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 17). Der Text steht als **reiner Fliesstext ohne eigenes Element und ohne eigene Klasse**: ein `<p>` und ein `<a>` mehr wären zwei Elemente mehr im sichtbaren Aufbau, den die Designwache einfriert — deshalb steht die Adresse der Erklärung ausgeschrieben statt verlinkt. Wie der Absatz im Browser aussieht, hat niemand geprüft. Der Honigtopf desselben Pakets (`KV06`, `06503a7`) ändert am sichtbaren Text nichts: das Fallenfeld bleibt für Menschen unsichtbar und unerreichbar.

**Zweig `sofort/2026-09-18-re15-und-2-weitere` zusätzlich (Paket 248, nicht gemergt):** drei
Textstellen. (1) Der Absendeknopf des Bestellformulars heisst „Zahlungspflichtig bestellen" statt
„Continue to Payment →" (`RE21`, `329dbc4`, `checkout.html:114`) — dieselbe Beschriftung, die
die AGB seit jeher nennen (`legal/agb.html:42`: „Durch den Klick auf 'Zahlungspflichtig bestellen'
gibst du ein verbindliches Angebot ab"); die Seite widersprach sich vorher selbst. (2) An der
Stelle der Google-Karte auf `/` und `/gaestebuch/` steht bis zum Klick der Text „Karte laden" und
„Beim Laden werden Daten an Google Maps übertragen." (`RE17`, `d58a96c`) — er steht **nicht in der
Vorlage**, sondern entsteht im Skript von `base.html`, taucht also weder im ausgelieferten HTML
noch in einer Wortzählung auf. (3) Abschnitt 2 der Datenschutzerklärung („Hosting &
Infrastruktur", `legal/datenschutz.html:51`) nennt Google Maps nicht mehr unter den Anbietern, die
beim Aufruf nachgeladen werden, sondern beschreibt Platzhalter und Klick: „Die eingebettete Karte
von Google Maps auf der Startseite und im Gästebuch wird nicht automatisch geladen: Sie sehen dort
zunächst nur einen Platzhalter, und erst wenn Sie auf 'Karte laden' klicken, wird die Karte von
Google abgerufen und Ihre IP-Adresse dorthin übertragen." `seiten_stand.py` führt `datenschutz`
deshalb mit `2026-09-18` statt `2026-09-01` — `lastmod` und `dateModified` der Seite stimmen also.

| URL (Zweig) | Titel (= h1) | Wörter | Index | Offene Sachangabe |
|---|---|---:|---|---|
| `/wissen/pflege-handbemalte-kleidung/` | Wie pflege ich handbemalte Kleidung? | 821 | nein | 30 °C, kein Trockner, kein Weichspüler, Bügeln nur von links |
| `/wissen/upcycling-mode-second-hand-vintage/` | Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand? | 941 | nein | keine strittige Zahl; Auflage nennt alle drei |
| `/wissen/groesse-bei-einzelstuecken/` | Wie finde ich bei Einzelstücken die richtige Größe? | 890 | nein | „fünf Zentimeter Unterschied in der Brustweite sind eine ganze Grösse" |
| `/wissen/bestellen-und-bezahlen/` | Wie bestelle und bezahle ich bei Luviq Universe? | 1.129 | **ja** | keine — Belege: `cart.py`, `checkout.py`, `forms.py`, `agb.html` § 2/§ 4, `liefergebiet.html` |
| `/wissen/widerruf-und-ruecksendung/` | Widerruf und Rücksendung: was gilt bei einem Einzelstück? | 1.034 | **ja** | keine — Belege: `agb.html` § 3/§ 4/§ 5, Impressum, Datenschutz; Rückporto und Rückzahlungsfrist stehen als offene Frage **im Text** |
| `/wissen/konto-und-daten/` | Was speichert der Shop – und warum braucht der Kauf ein Konto? | 1.000 | **ja** | keine — Belege: `datenschutz.html`, `forms.py`, `settings.py` (`AXES_*`), `views/auth.py` |

Jeder Beitrag: Antwort zuerst, sechs bis zehn Fragen als `h2`, `FAQPage` deckungsgleich, Verweise auf Über uns, Liefergebiet, AGB, Kontakt, Datenschutz. Kein neuer Beitrag ohne Eintrag in `WISSEN_BEITRAEGE`, `seiten_stand.py`, `WISSEN_SEITEN` (`legal.py`), `tests/_basis.py`, `FAQ_SEITEN`, `MINDESTWOERTER` und der Aufbau-Referenz (`CLAUDE.md`).

**Seit GE15 (12.09.2026, Zweig `sofort/2026-09-12-mw15-und-2-weitere`, `be550e3`, nicht gemergt)** trägt jeder Beitrag zusätzlich einen `Article`-Knoten im `<head>` — ein gemeinsames Teil-Template `shop1/templates/shop1/teile/wissen_article_ld.html`, eingebunden im Block `schema_ld` aller sechs Vorlagen. Er nimmt `headline` und `description` aus `WISSEN_BEITRAEGE` (Titel = `h1`, Kurztext = der Satz der Übersicht), `dateModified` aus `seiten_stand.py` und `datePublished` aus dem **neuen Registerfeld `veroeffentlicht`** in `shop1/views/wissen.py`; das ist der Tag, an dem die Vorlage angelegt wurde (`git log --diff-filter=A`: `2026-09-01` für Pflege, Upcycling und Grösse, `2026-09-07` für Bestellen, Widerruf und Konto), und es wird wie das Standregister **von Hand** geführt. Ein neuer Beitrag braucht deshalb auch dieses Feld. Die Übersicht `/wissen/` bekommt bewusst keinen `Article` — sie ist das Verzeichnis, kein Beitrag — sondern eine `ItemList` mit den Titeln, der Reihenfolge und den Adressen, die darunter sichtbar verlinkt sind. Am sichtbaren Text und am Aufbau ändert das nichts.

## Themen und Silos

| Silo | Seiten | Stand |
|---|---:|---|
| `/produkt/` (Einzelstücke) | 5 | hält 56 % aller Unterseiten (SU10); Übersicht ist `/produkte/`, der Pfad `/produkt/` selbst hat live keine Seite (SU09; Zweig: 301) |
| `/produkte/` | 1 | Kategorieseite; im Zweig mit Auskunft zu 1-of-1, Bestellung, Zahlung, Versand |
| `/wissen/` | 0 live / 6 + Übersicht im Zweig | Ratgeber; Zielgrösse 3 (SU04) im Zweig **erreicht**: drei belegte Beiträge indexiert, drei warten auf Freigabe |
| Betrieb | `/ueber_uns/`, `/liefergebiet/`, `/kontakt/`, `/gaestebuch/` | je eine Seite (SU08) |
| Recht | `/impressum/`, `/datenschutz/`, `/agb/` | |

**`SU08` („jeder Themenbereich hat mehr als eine Seite") am 12.09.2026 geprüft und als
nicht möglich beendet** (Paket 196, keine Zeile Code geändert). Der Befund trifft zu —
`/produkte/`, `/gaestebuch/`, `/ueber_uns/` und `/liefergebiet/` haben je eine Seite —,
schliessen lässt er sich hier nicht:

* **`/produkte/`** ist die Übersicht des Produktbereichs, seine Detailseiten liegen unter
  `/produkt/<slug>/` (`shop1/urls.py`). Die beiden zusammenzulegen hiesse, jede indexierte
  Produktadresse umzuziehen — ein Eingriff in die kanonischen Adressen der laufenden Seite.
* **`/gaestebuch/`, `/ueber_uns/`, `/liefergebiet/`** bräuchten je eine zweite Seite, und
  deren Inhalt gibt es im Projekt nicht: `Produkt` hat **kein Kategoriefeld**
  (`shop1/models.py`), aus dem sich Unterseiten ableiten liessen, und das Register
  `shop1/seiten_stand.py` führt genau 16 Seiten. Orte, Lieferzeiten oder eine zweite
  Werkstattseite kann nur die Betreiberin liefern — siehe „Beim Kunden" Nr. 16 in
  [80-AUFGABEN.md](80-AUFGABEN.md).

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

**Paket 165 (11.09.2026, `2591fde`, Zweig `sofort/2026-09-11-is18`, seit dem Merge `1a5f36b` auf `main`) —
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
| Eigene Danke-Seite nach dem Kontaktformular — **im Zweig erledigt** (11.09.2026, `2d78a55` auf `sofort/2026-09-11-kv07-und-2-weitere`, nicht gemergt): `/kontakt/danke/`, siehe „Seitenbestand" | | KV07 (Zweig erfüllt) |
| Datenschutzhinweis am Kontaktformular; Honigtopf — **beides im Zweig erledigt** (17.09.2026, `b736994` und `06503a7` auf `sofort/2026-09-17-kv05-und-2-weitere`, nicht gemergt): der Hinweis steht als Fliesstext zwischen Nachrichtenfeld und Absendeknopf, der Honigtopf wirkt seit `d90067a` auf `main` und trägt seine Kennzeichen jetzt am Feld selbst. Beides gilt nur für `/kontakt/` — Newsletter, Gästebuch, Anmeldung und Registrierung haben weiter keinen Hinweis und keine Falle. Live nachgemessen ist nichts davon | 0 von 1 (Messung 02.09.2026) | KV05, KV06 (Zweig erfüllt für `/kontakt/`) |

## Offen

1. **Freigabe der drei Wissensbeiträge** durch die Betreiberin → `'freigegeben': True` (siehe [80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden).
2. Zweig mergen, damit die neuen Texte, Meta-Angaben und die Platzhalter-Korrektur auf `/kontakt/` live sind.
3. Impressum aus der Sitemap nehmen **oder** `noindex` entfernen — heute widersprechen sich beide (SU11).
4. Produktnamen im Shop-Admin eindeutig machen („Custom print hoodie" ×2) — Pflegeaufgabe der Betreiberin, oder `seo_titel` setzen.
5. Weitere Wissensbeiträge nach Kundenfragen. Bestellablauf, Widerruf und Konto sind mit SU04 (07.09.2026) gebaut; alles Weitere braucht Angaben der Betreiberin — namentlich die Kosten der Rücksendung und die Frist der Rückzahlung, die heute in `/wissen/widerruf-und-ruecksendung/` ausdrücklich als ungeklärt stehen.
6. Muster-Widerrufsformular als eigene Seite.
7. Entscheidung Öffnungs-/Antwortzeiten und Telefonnummer — nur die Betreiberin kann sie nennen.
8. **Eine eigene Beschreibung je Einzelstück** (`Produkt.beschreibung` im Shop-Admin). Der Zuwachs aus IS19 (08.09.2026) beschreibt den Kauf, nicht das Stück, und steht wortgleich auf allen fünf Produktseiten — siehe [80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 14. Seit IS18 (11.09.2026) ist das der einzige offene Teil des Umfangs je Seitenart.
9. ~~**`seiten_stand.py` für `kontakt` nachziehen**~~ — **erledigt am 17.09.2026** (`9cd641f`, Paket 243, im Zweig): das Register nennt für `kontakt` jetzt `2026-09-17` statt `2026-09-01`. Anlass war der Datenschutzhinweis aus `KV05`; der Satz aus Paket 216 (`370fce7`, `FO04`) ist damit mit abgedeckt. `lastmod` der Sitemap und `dateModified` des `WebPage`-Knotens folgen dem Register — live gilt der neue Stand erst nach dem Merge. Kein Test erzwingt das Nachziehen.
10. **Datenschutzhinweis und Honigtopf an den übrigen Formularen** (Newsletter auf `/`, Gästebuch, Anmeldung, Registrierung): Paket 243 hat nur `/kontakt/` angefasst. Der Wortlaut lässt sich von dort übernehmen, muss aber je Formular stimmen — gespeichert wird bei Newsletter und Gästebuch anderes als beim Kontaktformular.
