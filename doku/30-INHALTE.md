---
bereich: inhalte
titel: Inhalte und Seitenbestand
stand: 2026-10-03
status: teilweise
fortschritt: 85
zusammenfassung: Stand 02.10.2026: 17 Sitemap-URLs (Start, Archiv, Gästebuch, Luisa, Motiv anfragen, Herkunft, Kontakt, Datenschutz, Wissensbereich mit drei Beiträgen, fünf Archivstücke), llms-full.txt und Feed live, Archiv statt Shop; Substanz & Reichweite 85 gemessen (02.10.2026). Offen bei Luisa: Beschreibung je Stück, Produktnamen, Stoff für zweite Seiten, Textfreigabe; zwei Später-Punkte.
offen: 2
quellen: LOGBUCH.md, shop1/seiten_stand.py, shop1/views/wissen.py, shop1/views/legal.py, shop1/tests/test_inhalt.py
rest_bei: kunde, spaeter
---

# Inhalte — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Bereichswert **Substanz** des Laufs vom 02.10.2026 (Regelstand `2026-10-02e`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße.*

> **Stand 02.10.2026 (geprüft, abends):** `main` = `origin/main` = `7ae67ab` und live. Alle Arbeitszweige des Tages (`fix/2026-10-02-luviq-fertig`, `-rest`, `-luisa`, `-recht`, `-wissen`, `fix/2026-10-02d-standard`) sind gemergt (`git log origin/main..<zweig>` leer, `git branch -r --no-merged origin/main` leer); die GitHub-Prüfungen auf `main` sind grün (Lauf 37040107996, 02.10.2026). Live belegt am 02.10.2026 (curl): Sitemap mit 17 Adressen samt der drei Wissensbeiträge, `/llms-full.txt` 200, „Aktualisiert am …“ (`<time>`) auf den Wissensbeiträgen (GE47), `Permissions-Policy` im Kopf, `/health/` 200, Apex 301 auf www. Wo unten „Zweig“ oder „nicht gemergt“ steht, ist das **Verlauf** des jeweiligen Tages und gilt seit dem Merge als live, sofern der Satz nichts anderes sagt. Der **Verkauf ist aus** (`VERKAUF_AKTIV` ohne Variable = aus: Marke im Aufbau, Archiv statt Shop); nach Angabe des Betreibers ist **kein Gewerbe angemeldet** — die Seite nennt deshalb keine Unternehmensangaben (Impressum nach § 5 DDG nur mit Luisa Brehler als Person, Alsfeld, E-Mail).

## Seitenbestand

**Live (main, Sitemap und Stichproben, abgerufen 02.10.2026): 17 URLs in der Sitemap** — acht statische Seiten, der Wissensbereich (Übersicht und drei Beiträge) und fünf Archivstücke (Produktseiten). Messung 02.10.2026: Substanz & Reichweite 85 von 100 (Messblock in [00-STATUS.md](00-STATUS.md)); lokal gemessen mit den drei freigegebenen Wissensbeiträgen 7.202 Eigenwörter über 17 Seiten gegen das Ziel von 12.000 (`SU02`) und 17 rankfähige Seiten gegen 30 (`SU01`, Bewertungsblock in [80-AUFGABEN.md](80-AUFGABEN.md)).

| URL | Seite | Index |
|---|---|---|
| `/` | Startseite „Nachtausgabe“ (Markensatz, Motiv anfragen, Drop-Countdown, Entstehung, Archiv, Warteliste) | ja, Sitemap |
| `/produkte/` | Archiv der bisherigen Stücke („bereits vergeben“, keine Preise) | ja, Sitemap |
| `/produkt/custom-hoodie-mit-print/`, `/produkt/custom-print-hoodie-1/`, `/produkt/custom-pants/`, `/produkt/custom-print-jacke/`, `/produkt/custom-print-hoodie/` | je ein Archivstück (`custom-pants` hieß bis 18.09.2026 `custom-pants-sold`, leitet per 301 um) | ja, Sitemap |
| `/motiv-anfragen/` | Motiv anfragen (Stufe 1: ohne Preis, Zahlung, Zusage) | ja, Sitemap |
| `/ueber_uns/` | „Luisa“ | ja, Sitemap |
| `/liefergebiet/` | „Herkunft“ (mit Verkauf „Liefergebiet“) | ja, Sitemap |
| `/kontakt/` | Kontakt, Formular | ja, Sitemap |
| `/gaestebuch/` | Gästebuch (Kommentare angemeldeter Nutzer) | ja, Sitemap |
| `/datenschutz/` | Datenschutzerklärung | ja, Sitemap |
| `/impressum/`, `/agb/` | Impressum, AGB | `noindex, follow`, **nicht** in der Sitemap (der frühere Widerspruch Impressum/Sitemap ist behoben) |
| `/wissen/` und `/wissen/pflege-handbemalte-kleidung/`, `/wissen/upcycling-mode-second-hand-vintage/`, `/wissen/groesse-bei-einzelstuecken/` | Wissensbereich: 200, `index, follow`, mit „Aktualisiert am …“ (`<time>`), seit der Freigabe vom 02.10.2026 (`3073388`) in Sitemap und `llms.txt` | ja, Sitemap |
| `/wissen/bestellen-und-bezahlen/`, `/wissen/widerruf-und-ruecksendung/`, `/wissen/konto-und-daten/` | verkaufsnahe Beiträge: leiten ohne Verkauf per 302 um (`nur_mit_verkauf`) | nein |
| `/kontakt/danke/`, `/motiv-anfragen/danke/` | Danke-Seiten, `noindex, follow` | nein |
| `/feed/`, `/llms.txt`, `/llms-full.txt`, `/robots.txt`, `/sitemap.xml` | Feed der freigegebenen Wissensbeiträge, KI-Übersicht (kurz und ausführlich, `bf8882e`), Crawler-Regeln, Sitemap (alle 200, abgerufen 02.10.2026) | — |

Nicht in der Sitemap, aber erreichbar und per `robots.txt` gesperrt: `/login/`, `/register/`, `/profil/`, `/warenkorb/` (ohne Verkauf 302), `/checkout/` (302), `/payment/…`, `/verify/…`, `/password-reset/…`, `/delete-account/`, `/shop-admin/…`.

**Verlauf: Messung vom 02.09.2026** (Wortzahlen und Preise gelten für die Zeit vor dem Umbau und vor dem Abschalten des Verkaufs):

| URL | Seite | Eigenwörter live (Messung 02.09.2026) | Ziel | Titel live |
|---|---|---:|---:|---|
| `/` | Startseite | 390 | 700 | Luviq Universe – Handbemalte Second Hand Mode aus Alsfeld \| Hessen (66 Z.) |
| `/produkte/` | Produktübersicht „The Drop" | 62 | 600 | Second Hand & Vintage Mode kaufen \| Luviq Universe – Alsfeld, Hessen (68 Z.) |
| `/produkt/custom-hoodie-mit-print/` | Produkt, 59,00 € | 26 | 600 | |
| `/produkt/custom-print-hoodie-1/` | Produkt, 59,00 € | 25 | 600 | „Custom print hoodie kaufen – Luviq Universe" — **doppelt** mit `custom-print-hoodie` |
| `/produkt/custom-pants/` (bis 18.09.2026 `/produkt/custom-pants-sold/`, leitet per 301 um) | Produkt „Custom Pants" (vorher „Custom Pants (Sold)"; nie verkauft, Migration 0022), ohne Verkauf im Archiv | 25 | 600 | |
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

**`/gaestebuch/` seit Paket 282 (18.09.2026, `3b2b602`, Zweig):** Das Messwerkzeug streicht jeden `<header>`, auch den im Inhaltsbereich — dort stand der Text, mit dem `IS19` die Seite gefüllt hatte, und er zählte für `IS17` nicht mit. Neuer Text steht im Anmeldehinweis (Glas-Karte für Abgemeldete, `gaestebuch.html`): Länge eines Beitrags, sofortige Veröffentlichung, Reihenfolge, Antworten, Markierung, Löschen samt Antworten, Folgen einer Kontolöschung, Auszug auf der Startseite, Abgrenzung zur Google-Bewertung. Der Test `test_das_gaestebuch_hat_300_eigenwoerter_ausserhalb_seines_kopfes` zählt wie das Werkzeug und verlangt 300 Wörter ohne einen Beitrag. Angemeldete sehen diesen Absatz nicht — sie bekommen das Eingabefeld.

**Nicht in der Sitemap, aber erreichbar:** `/login/`, `/register/`, `/profil/`, `/warenkorb/`, `/checkout/`, `/payment/…`, `/verify/…`, `/password-reset/…`, `/delete-account/`, `/newsletter/subscribe/`, `/shop-admin/…` — alle per `robots.txt` gesperrt. `/produkt/<id>/` leitet auf die Slug-URL um (Altlink-Kompatibilität); `/produkt/` → 301 auf `/produkte/` (Zweig; live 404).

**Wissensbereich (Stand 02.10.2026):** `/wissen/` (Übersicht) und sechs Beiträge. Pflege, Upcycling und Größe sind seit `3073388` freigegeben, indexierbar und in Sitemap und `llms.txt`; Bestellen, Widerruf und Konto sind `nur_mit_verkauf` und leiten ohne Verkauf per 302 um. Die Beiträge zeigen ihr Datum sichtbar (`GE47`, `f03bf61`) und wurden nach der Freigabe nachgeschärft (`c943006`).

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

| URL | Titel (= h1) | Wörter (Stand der Messung 02.09.2026) | Index (live 02.10.2026) | Freigabe |
|---|---|---:|---|---|
| `/wissen/pflege-handbemalte-kleidung/` | Wie pflege ich handbemalte Kleidung? | 821 | **ja** | freigegeben 02.10.2026 (`3073388`) |
| `/wissen/upcycling-mode-second-hand-vintage/` | Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand? | 941 | **ja** | freigegeben 02.10.2026 (`3073388`) |
| `/wissen/groesse-bei-einzelstuecken/` | Wie finde ich bei Einzelstücken die richtige Größe? | 890 | **ja** | freigegeben 02.10.2026 (`3073388`) |
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
| `/wissen/` | 3 Beiträge und Übersicht live (02.10.2026) | Ratgeber; Zielgrösse 3 (SU04) erreicht: Pflege, Upcycling, Größe indexierbar (`3073388`); die drei Kaufweg-Beiträge leiten ohne Verkauf um |
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

*Stand 02.10.2026, gegen die Live-Seite geprüft.* Nichts mehr, wofür kein Zuständiger genannt wäre: Der Wissensbereich ist live (`3073388`), die Danke-Seite (KV07), der Datenschutzhinweis am Kontaktformular und der Honigtopf (KV05/KV06, `38bb573`) sowie die konkreten Zahlen (GE25) stehen auf `main`, Frage-Überschriften (GE24) sind „bewusst so“ im Bewertungsblock von [80-AUFGABEN.md](80-AUFGABEN.md), und die Über-uns-Seite gibt es (`/ueber_uns/`, Luisa Brehler namentlich; dass `VL11` sie nicht erkennt, ist ein Messfehler des Musters, siehe Bewertungsblock). Was an Inhalt noch fehlt, braucht Angaben von Luisa und steht deshalb dort unter „Beim Kunden“: eigene Beschreibung je Einzelstück und eindeutige Produktnamen (`SU06`, `IS21`, `IS23`), Stoff für zweite Seiten je Bereich (`SU08`, `SU01`, `SU02`: 17 statt 30 rankfähige Seiten, 7.202 statt 12.000 Eigenwörter lokal), Vertrauenssignale (`KV09`) und das Gegenlesen der „Nachtausgabe“-Texte. Muster-Widerrufsformular (RE09) und BFSG-Erklärung (RE12) gibt es erst mit Verkauf (80-AUFGABEN, „Offen“, Später). Eine Telefonnummer und Öffnungszeiten gibt es bewusst nicht (KV01, KV08, KV11 im Bewertungsblock; die Antwortzeit „in der Regel innerhalb von 2 Stunden“ steht seit `3073388` auf `/kontakt/`).

## Offen

Stand 02.10.2026. Erledigt und entfernt: Freigabe der drei Wissensbeiträge (`3073388`), Datenschutzhinweis an beiden Newsletter-Formularen (`c49b121`) und Honigtopf (`38bb573`) (Gästebuch und Registrierung tragen einen Datenschutzhinweis, Quelltext am 02.10.2026), Merge der Texte und der Platzhalter-Korrektur auf `/kontakt/` (live), Widerspruch Impressum `noindex` und Sitemap, `seiten_stand.py` für `kontakt`. Die Zeilen zu Gegenlesen der Texte, Produktnamen und Beschreibung je Stück stehen nur noch unter „Beim Kunden“ in [80-AUFGABEN.md](80-AUFGABEN.md), die zu Rücksendekosten, Muster-Widerrufsformular und BFSG unter „Offen“ (Später: erst mit Verkauf).

- Später: weitere Wissensbeiträge nach Kundenfragen. Grund: es sind keine Kundenfragen dokumentiert, und jeder neue Beitrag braucht belegte Angaben (Eintrag in `WISSEN_BEITRAEGE`, `seiten_stand.py`, Tests, Aufbau-Referenz).
- Später: Datenschutzhinweis am Anmeldeformular (`login.html`). Grund: das Formular fragt nur Benutzername und Passwort; was beim Anmelden gespeichert wird (Anmeldeprotokoll), nennt die Datenschutzerklärung, der Hinweis am Formular selbst fehlt.

