---
bereich: local-seo
titel: Local SEO
stand: 2026-10-01
status: teilweise
fortschritt: 25
zusammenfassung: Stand 01.10.2026: Search Console verbunden (Property sc-domain:luviq-alsfeld.com im Konto …05), Platzhalter-NAP auf /kontakt/ und falsche Domain im Impressum live behoben; ein Google-Unternehmensprofil und Bewertungen sind weiter nicht belegt — Fragen an die Betreiberin stehen unter Offen.
offen: 4
unternehmensprofil: unbekannt
search_console: ja
gsc_property: sc-domain:luviq-alsfeld.com
gsc_konto: bastian.scherzinger05@gmail.com
bewertung: nicht dokumentiert
bewertungen_anzahl: nicht dokumentiert
quellen: GOOGLE_SEO_GUIDE.md, templates/base.html, shop1/templates/shop1/_reviews_map.html, shop1/templates/shop1/legal/impressum.html
---

# Local SEO — Luviq Universe

> **Stand 01.10.2026 (geprüft):** Alle bis dahin geführten Arbeitszweige (`sofort/…`, `mail/…`, `recht/…`, `design/…`) sind in `main` gemergt (`git branch -r --no-merged origin/main` ist leer); `main` = `origin/main` = `36c0741` (TS19, Bild-Sitemap, 01.10.2026), und die Live-Seite zeigt diesen Stand (Sitemap mit Bild-Auszeichnung am 01.10.2026 abgerufen). Wo unten „Zweig“ oder „nicht gemergt“ steht, ist das **Verlauf** des jeweiligen Tages und gilt seit dem Merge als live, sofern der Satz nichts anderes sagt. Der **Verkauf ist aus** (`VERKAUF_AKTIV` ohne Variable = aus: Marke im Aufbau, Archiv statt Shop); nach Angabe des Betreibers ist **kein Gewerbe angemeldet** — die Seite nennt deshalb keine Unternehmensangaben (Impressum nach § 5 DDG nur mit Luisa Brehler als Person, Alsfeld, E-Mail).


*Woran sich der Fortschritt bemisst: an vier Punkten zu je 25 — Unternehmensprofil vorhanden · Search Console verbunden · Bewertungen vorhanden · NAP überall gleich. Bei allen sechs betreuten Seiten dieselben vier Punkte.*

**Vorbemerkung:** Luviq ist ein Online-Shop **ohne Ladengeschäft** (belegt in `agb.html`, `ueber_uns.html`,
llms.txt des Zweigs). Der Ortsbezug Alsfeld ist Marke und Herkunft, kein Besuchsort. Was Local SEO hier
leisten kann, ist Markenpflege („Luviq Universe" als Entität) und der Ortsbezug in Titeln und Schema —
kein Laufkundschafts-Ranking.

## Google-Unternehmensprofil

**Nicht dokumentiert**, ob eines existiert. `GOOGLE_SEO_GUIDE.md` (Schritt 2) fordert die Betreiberin auf,
ein kostenloses Profil anzulegen und die Seite dort zu verlinken; ob das geschehen ist, steht nirgends.

Hinweise im Code:

- `_reviews_map.html` bettet eine **Google-Maps-Karte** auf die Anschrift „Grünberger Str. 16, 36304 Alsfeld" ein (`maps.google.com/maps?q=…&output=embed`) — **seit dem 18.09.2026 (`RE17`, `d58a96c`, Zweig `sofort/2026-09-18-re15-und-2-weitere`, nicht gemergt) erst nach einem Klick:** die Adresse steht in `data-src`, an ihrer Stelle liegt bis dahin ein Platzhalter „Karte laden". Wer die Karte sehen will, klickt; für Local SEO ändert das nichts (eine eingebettete Karte ist kein Rankingfaktor), für den Datenschutz alles — vorher ging die IP-Adresse jedes Besuchers ungefragt an Google. Die Anschrift selbst steht weiter als Text daneben und im Schema. Dieselbe Karte zeigt einen Knopf **„Bei Google bewerten"** mit dem Ziel aus der Umgebungsvariablen `GOOGLE_REVIEW_URL` (Kontextprozessor). Ob die Variable in Railway gesetzt ist, ist **nicht dokumentiert**; ihr **Standardwert im Code ist kein Profil, sondern ein Maps-Suchlink** (`mainweb/settings.py:409`, `https://www.google.com/maps/search/Luviq+Universe+Alsfeld`, geprüft 12.09.2026). Ein Bewertungslink setzt normalerweise ein Unternehmensprofil voraus.
- Das Schema (`base.html`) ist `ClothingStore` mit `GeoCoordinates` (50.7517, 9.2685) und `areaServed` über 18 hessische Städte — für ein Unternehmen ohne Ladengeschäft wäre `OnlineStore`/`Organization` mit `areaServed` ehrlicher; nicht entschieden.
- `sameAs` nennt nur Instagram (`https://www.instagram.com/luviq.universe/`, `base.html:118`); ein Profil-Link fehlt (GE11). Am 11.09.2026 (Paket 171) und am **12.09.2026 (Paket 183)** je als **nicht möglich** beendet, mit demselben Befund: im Projekt steht genau diese eine Profiladresse, dieselbe auch in `llms.txt` (`views/legal.py:166`); der Bewertungsknopf zeigt im Standard auf einen Maps-Suchlink, nicht auf ein Profil, und TikTok nennt `GOOGLE_SEO_GUIDE.md` nur als Bio-Verlinkung, ohne Adresse. Eine Adresse zu raten hiesse, das Schema mit einem fremden Profil zu verknüpfen; in beiden Paketen keine Zeile Code geändert. Seit dem 12.09.2026 steht GE11 als **beim Kunden** im Bewertungsblock; die Adressen liefert die Betreiberin ([80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 6 und 15).
- **GE46 (sameAs soll auch auf das Google-Unternehmensprofil verweisen)** ist am **27.09.2026 (Zweig, Paket 527)** aus demselben Befund wie `GE11` als **beim Kunden** eingetragen: ein Unternehmensprofil ist weiterhin **nicht dokumentiert** (Abschnitt oben), und `GOOGLE_REVIEW_URL` zeigt im Standard auf den Maps-Suchlink `mainweb/settings.py:442`, kein Profil. Eine `maps.google.com/…`-, `g.page/…`- oder `maps.app.goo.gl/…`-Adresse in `sameAs` einzutragen, ohne dass sie im Projekt vorkommt, hiesse, das Schema mit einem fremden oder nicht existierenden Profil zu verknüpfen — anlegen und nennen kann das Profil nur Luisa Brehler. Keine Zeile Code geändert; Beleg im Bewertungsblock von [80-AUFGABEN.md](80-AUFGABEN.md).

## Search Console

**Verbunden.** Am 03.09.2026 einzeln nachgeprüft: die Property **`sc-domain:luviq-alsfeld.com`** existiert
und liegt im Konto **`bastian.scherzinger05@gmail.com`** — zusammen mit den sechs übrigen Properties; das
zweite Konto (`…69@gmail.com`) hat keine einzige. Sie steht seither in `sites.json` des Werkzeugs, und die
Search Console ist **per OAuth** angebunden (Cloud-Projekt `gen-lang-client-0179494625`). Damit ist die
frühere Aussage dieser Datei überholt, das Werkzeug „würde raten": es rät nichts mehr.

Was weiterhin gilt: `GOOGLE_SEO_GUIDE.md` (Schritt 1) beschreibt das Vorgehen aus Sicht der Betreiberin
(Property anlegen, Verifizierungs-Tag schicken, `sitemap.xml` einreichen) und nennt als Beispiel noch die
Railway-Adresse; im `base.html` steckt kein Verifizierungs-Tag und im `static`-Ordner keine
Verifizierungsdatei (02.09.2026) — die Domain-Property braucht beides nicht, sie hängt am DNS-Eintrag.
**Ob die Property auf ein Konto der Betreiberin übergehen soll, ist nicht entschieden** (siehe „Offen").

Folge: Klicks, Impressionen und Positionen sind ab jetzt abrufbar; **eine erste Auswertung liegt noch
nicht vor**.

## Bewertungen

**Nicht dokumentiert.** Der Kasten `_reviews_map.html` zeigt „★★★★★" neben dem Firmennamen und je Gästebuch-Kommentar fünf Sterne — die Zahl „5.0" ist im Projekt **nicht belegt** und wurde deshalb im Lauf 4 bewusst nicht aufgegriffen (Logbuch Schritt 23). Es gibt kein `AggregateRating` im Schema (KV09), und es sollte auch keines geben, solange keine echte Quelle existiert. **Am 17.09.2026 (Paket 243) ist `KV09` deshalb als nicht möglich beendet worden**, keine Zeile Code geändert: von den vier fehlenden Vertrauenssignalen hat keines eine Quelle im Projekt — kein Gründungsjahr (kein Treffer für „seit 20…", „gegründet" oder `foundingDate` in `index.html`, `ueber_uns.html`, `legal/impressum.html`), kein Zertifikat und keine Mitgliedschaft ausser dem TLS-Zertifikat der Domain, und eben keine Bewertungszahl. Seit dem 17.09.2026 steht `KV09` als **beim Kunden** im Bewertungsblock; die Angaben liefert die Betreiberin ([80-AUFGABEN.md](80-AUFGABEN.md) → Beim Kunden Nr. 9 und 19).

Das **Gästebuch** (`/gaestebuch/`, Modell `Comment`, Likes, nur angemeldete Nutzer) ist die einzige eigene Stimme-der-Kunden-Funktion; Anzahl der Einträge nicht dokumentiert.

## NAP und Verzeichnisse

*Stand 01.10.2026: die Zeilen mit „live (Messung 02.09.2026)“ beschreiben den Zustand vor der Korrektur; live stimmen Kontaktseite und Impressum jetzt mit dem Schema überein (Anschrift Grünberger Str. 16, 36304 Alsfeld; E-Mail; kein Telefon).*

| Ort | Name | Anschrift | Kontakt | Stand |
|---|---|---|---|---|
| Impressum (live und Zweig) | Luisa Brehler / „Luisa Brehler – Luviq Universe" | Grünberger Str. 16, 36304 Alsfeld, Deutschland | brehlerluisa@gmail.com; **kein Telefon** | Messung 02.09.2026: „Website: www.luviq.de" (**falsche Domain**); auf `main` inzwischen `{{ request.get_host }}` (geprüft 11.09.2026, Auslieferung nicht geprüft) |
| Schema `base.html` | Luviq Universe | wie Impressum | E-Mail; kein Telefon | konsistent |
| llms.txt (Zweig) | Luisa Brehler | wie Impressum | E-Mail, Instagram | konsistent |
| `/kontakt/` **live (Messung 02.09.2026)** | — | **„Musterstraße 123, 12345 Berlin"** | **„+49 (0) 30 123456"**, **`info@luviq.universe`** | **Platzhalter — falsches NAP auf der Kontaktseite**; auf `main` inzwischen durch Grünberger Str. 16 / brehlerluisa@gmail.com ersetzt, Telefon entfernt (geprüft 11.09.2026, Auslieferung nicht geprüft). Die Danke-Seite `/kontakt/danke/` (Zweig KV07, nicht gemergt) nennt nur `brehlerluisa@gmail.com` und keine Telefonnummer |
| Instagram | `luviq.universe` | | | im `sameAs` und in llms.txt |
| TikTok | erwähnt in `GOOGLE_SEO_GUIDE.md` (Bio-Verlinkung) | | | Profiladresse nicht dokumentiert |
| Branchenverzeichnisse | — | | | nicht dokumentiert |

Die Messung meldet KV01 „1 von 13 Seiten mit tel:-Link" — dieser eine Link war die **Platzhalternummer** auf `/kontakt/`. Auf `main` ist sie entfernt; danach sind es 0 Seiten, und das ist richtig so, bis die Betreiberin eine Nummer nennt.

## Offen

Stand 01.10.2026. Erledigt und entfernt: Auslieferung der NAP-Korrektur — live geprüft: `/kontakt/` nennt Luisa Brehler, 36304 Alsfeld und `brehlerluisa@gmail.com` und sagt „eine Telefonnummer gibt es nicht“, das Impressum nennt „Website: www.luviq-alsfeld.com“ (abgerufen 01.10.2026).

| Punkt | Wer |
|---|---|
| Gibt es ein Google-Unternehmensprofil? Wohin zeigt `GOOGLE_REVIEW_URL`? — nachsehen, dokumentieren, ggf. anlegen (Profil muss auf die Betreiberin laufen) | Betreiberin + Bastian |
| Search Console: die Property `sc-domain:luviq-alsfeld.com` liegt seit dem 03.09.2026 nachweislich im Agenturkonto `…05@gmail.com` und ist im Werkzeug eingetragen — offen bleibt die Entscheidung, ob sie auf ein Konto der Betreiberin übergeht (Bastian dann als Nutzer) | Betreiberin |
| Telefonnummer und Erreichbarkeitszeiten — nur wenn es sie gibt (KV01, KV11, GE09) | Betreiberin |
| Schema-Typ (`ClothingStore` vs. `OnlineStore`) und `sameAs`-Erweiterung (Profil, TikTok) — `GE11` wartet seit dem 11.09.2026 und `GE46` seit dem 27.09.2026 auf dieselben Profiladressen (Beim Kunden Nr. 6 und 15 in [80-AUFGABEN.md](80-AUFGABEN.md)) | Bastian nach Angaben der Betreiberin |

## Backlink-Plan (16.09.2026)

Gemeinsamer Plan für alle sechs Seiten: `C:\Users\basti\Desktop\pystore-overview\docs\BACKLINK-PLAN.md` — Spielregeln, Grundpaket G1–G12, Methoden, Ablauf und Fortschrittstabelle. Kurzfassung für diese Seite:

- Geschäftsadresse vorhanden (Grünberger Str. 16, Alsfeld) — Einträge nur mit Zustimmung von Luisa Brehler.
- Stand: Bing Places ✔ Import, Bing Webmaster Tools ✔ (Sitemap `www` eingereicht); Duplikat-Host am 16.09.2026 behoben (`CANONICAL_HOST`).
- Als Nächstes: **„WIR sind Alsfeld“** / Wirtschaftsförderung Alsfeld, alsaktiv, **Pinterest**-Unternehmenskonto, Fair-Fashion-Labellisten (Fashion Changers, Utopia, endlich fair), Pressebeitrag Oberhessische Zeitung, Ausstellerlisten von Kunsthandwerker-Märkten.
