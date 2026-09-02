---
bereich: local-seo
titel: Local SEO
stand: 2026-09-02
status: fehlt
fortschritt: 10
zusammenfassung: Unternehmensprofil, Search Console und Bewertungen sind nirgends dokumentiert; NAP steht konsistent im Impressum und im Schema, live auf /kontakt/ aber noch Platzhalterdaten.
offen: 5
unternehmensprofil: unbekannt
search_console: unbekannt
gsc_property: nicht dokumentiert
gsc_konto: nicht dokumentiert
bewertung: nicht dokumentiert
bewertungen_anzahl: nicht dokumentiert
quellen: GOOGLE_SEO_GUIDE.md, templates/base.html, shop1/templates/shop1/_reviews_map.html, shop1/templates/shop1/legal/impressum.html
---

# Local SEO — Luviq Universe

**Vorbemerkung:** Luviq ist ein Online-Shop **ohne Ladengeschäft** (belegt in `agb.html`, `ueber_uns.html`,
llms.txt des Zweigs). Der Ortsbezug Alsfeld ist Marke und Herkunft, kein Besuchsort. Was Local SEO hier
leisten kann, ist Markenpflege („Luviq Universe" als Entität) und der Ortsbezug in Titeln und Schema —
kein Laufkundschafts-Ranking.

## Google-Unternehmensprofil

**Nicht dokumentiert**, ob eines existiert. `GOOGLE_SEO_GUIDE.md` (Schritt 2) fordert die Betreiberin auf,
ein kostenloses Profil anzulegen und die Seite dort zu verlinken; ob das geschehen ist, steht nirgends.

Hinweise im Code:

- `_reviews_map.html` bettet eine **Google-Maps-Karte** auf die Anschrift „Grünberger Str. 16, 36304 Alsfeld" ein (`maps.google.com/maps?q=…&output=embed`) und zeigt einen Knopf **„Bei Google bewerten"** mit dem Ziel aus der Umgebungsvariablen `GOOGLE_REVIEW_URL` (Kontextprozessor). Ob die Variable in Railway gesetzt ist und wohin sie zeigt, ist **nicht dokumentiert**. Ein Bewertungslink setzt normalerweise ein Unternehmensprofil voraus.
- Das Schema (`base.html`) ist `ClothingStore` mit `GeoCoordinates` (50.7517, 9.2685) und `areaServed` über 18 hessische Städte — für ein Unternehmen ohne Ladengeschäft wäre `OnlineStore`/`Organization` mit `areaServed` ehrlicher; nicht entschieden.
- `sameAs` nennt nur Instagram (`https://www.instagram.com/luviq.universe/`); ein Profil-Link fehlt (GE11).

## Search Console

**Nicht dokumentiert.** `GOOGLE_SEO_GUIDE.md` (Schritt 1) beschreibt das Vorgehen — Property anlegen,
Verifizierungs-Tag oder -Datei an Bastian schicken, `sitemap.xml` einreichen — als **offene Aufgabe der
Betreiberin**; der Guide nennt als Beispiel noch die Railway-Adresse als Property. Kein Verifizierungs-Tag
im `base.html`, keine Verifizierungsdatei im `static`-Ordner gefunden (02.09.2026). Im Werkzeug ist für
`luviq` keine `gsc_property` hinterlegt (`sites.json`); das Werkzeug würde `sc-domain:luviq-alsfeld.com`
**raten** — das ist ein Vorschlag, keine Tatsache.

Folge: **Sichtbarkeit ist nicht gemessen** — keine Klicks, Impressionen oder Positionen bekannt.

## Bewertungen

**Nicht dokumentiert.** Der Kasten `_reviews_map.html` zeigt „★★★★★" neben dem Firmennamen und je Gästebuch-Kommentar fünf Sterne — die Zahl „5.0" ist im Projekt **nicht belegt** und wurde deshalb im Lauf 4 bewusst nicht aufgegriffen (Logbuch Schritt 23). Es gibt kein `AggregateRating` im Schema (KV09), und es sollte auch keines geben, solange keine echte Quelle existiert.

Das **Gästebuch** (`/gaestebuch/`, Modell `Comment`, Likes, nur angemeldete Nutzer) ist die einzige eigene Stimme-der-Kunden-Funktion; Anzahl der Einträge nicht dokumentiert.

## NAP und Verzeichnisse

| Ort | Name | Anschrift | Kontakt | Stand |
|---|---|---|---|---|
| Impressum (live und Zweig) | Luisa Brehler / „Luisa Brehler – Luviq Universe" | Grünberger Str. 16, 36304 Alsfeld, Deutschland | brehlerluisa@gmail.com; **kein Telefon** | live: „Website: www.luviq.de" (**falsche Domain**); Zweig: `{{ request.get_host }}` |
| Schema `base.html` | Luviq Universe | wie Impressum | E-Mail; kein Telefon | konsistent |
| llms.txt (Zweig) | Luisa Brehler | wie Impressum | E-Mail, Instagram | konsistent |
| `/kontakt/` **live (main)** | — | **„Musterstraße 123, 12345 Berlin"** | **„+49 (0) 30 123456"**, **`info@luviq.universe`** | **Platzhalter — falsches NAP auf der Kontaktseite**; im Zweig durch Grünberger Str. 16 / brehlerluisa@gmail.com ersetzt, Telefon entfernt |
| Instagram | `luviq.universe` | | | im `sameAs` und in llms.txt |
| TikTok | erwähnt in `GOOGLE_SEO_GUIDE.md` (Bio-Verlinkung) | | | Profiladresse nicht dokumentiert |
| Branchenverzeichnisse | — | | | nicht dokumentiert |

Die Messung meldet KV01 „1 von 13 Seiten mit tel:-Link" — dieser eine Link ist die **Platzhalternummer** auf `/kontakt/` (main). Nach dem Merge sind es 0 Seiten, und das ist richtig so, bis die Betreiberin eine Nummer nennt.

## Offen

| Punkt | Wer |
|---|---|
| Zweig mergen — beseitigt das falsche NAP (Berlin, 030-Nummer, `info@luviq.universe`) und „www.luviq.de" im Impressum | Bastian |
| Gibt es ein Google-Unternehmensprofil? Wohin zeigt `GOOGLE_REVIEW_URL`? — nachsehen, dokumentieren, ggf. anlegen (Profil muss auf die Betreiberin laufen) | Betreiberin + Bastian |
| Search Console: Property (empfohlen `sc-domain:luviq-alsfeld.com`) auf ein Konto der Betreiberin, Bastian als Nutzer; danach `gsc_property` in `sites.json` | Betreiberin |
| Telefonnummer und Erreichbarkeitszeiten — nur wenn es sie gibt (KV01, KV11, GE09) | Betreiberin |
| Schema-Typ (`ClothingStore` vs. `OnlineStore`) und `sameAs`-Erweiterung (Profil, TikTok) | Bastian nach Angaben der Betreiberin |
