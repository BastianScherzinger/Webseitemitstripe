---
bereich: local-seo
titel: Local SEO
stand: 2026-09-03
status: teilweise
fortschritt: 25
zusammenfassung: Search Console seit 03.09.2026 verbunden (Property sc-domain:luviq-alsfeld.com im Konto …05@gmail.com); Unternehmensprofil und Bewertungen bleiben nicht dokumentiert, live auf /kontakt/ stehen noch Platzhalterdaten.
offen: 5
unternehmensprofil: unbekannt
search_console: ja
gsc_property: sc-domain:luviq-alsfeld.com
gsc_konto: bastian.scherzinger05@gmail.com
bewertung: nicht dokumentiert
bewertungen_anzahl: nicht dokumentiert
quellen: GOOGLE_SEO_GUIDE.md, templates/base.html, shop1/templates/shop1/_reviews_map.html, shop1/templates/shop1/legal/impressum.html
---

# Local SEO — Luviq Universe

*Woran sich der Fortschritt bemisst: an vier Punkten zu je 25 — Unternehmensprofil vorhanden · Search Console verbunden · Bewertungen vorhanden · NAP überall gleich. Bei allen sechs betreuten Seiten dieselben vier Punkte.*

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
| Search Console: die Property `sc-domain:luviq-alsfeld.com` liegt seit dem 03.09.2026 nachweislich im Agenturkonto `…05@gmail.com` und ist im Werkzeug eingetragen — offen bleibt die Entscheidung, ob sie auf ein Konto der Betreiberin übergeht (Bastian dann als Nutzer) | Betreiberin |
| Telefonnummer und Erreichbarkeitszeiten — nur wenn es sie gibt (KV01, KV11, GE09) | Betreiberin |
| Schema-Typ (`ClothingStore` vs. `OnlineStore`) und `sameAs`-Erweiterung (Profil, TikTok) | Bastian nach Angaben der Betreiberin |
