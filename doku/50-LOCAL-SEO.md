---
bereich: local-seo
titel: Local SEO
stand: 2026-10-03
status: teilweise
fortschritt: 60
zusammenfassung: Stand 02.10.2026: Google-Unternehmensprofil „Luviq“ vorhanden und in sameAs und llms.txt verlinkt (Bestätigung durch Google nicht belegt), Search Console verbunden (Property sc-domain:luviq-alsfeld.com), NAP auf Impressum, Kontakt, Schema und llms.txt gleich, ohne Verkauf nur Organization-Schema. Offen: Bewertungen (keine dokumentiert, nur Luisa), GOOGLE_REVIEW_URL in Railway und Bestätigungsstatus des Profils (beide Bastian).
offen: 2
unternehmensprofil: ja
search_console: ja
gsc_property: sc-domain:luviq-alsfeld.com
gsc_konto: brehlerluisa@gmail.com
bewertung: nicht dokumentiert
bewertungen_anzahl: nicht dokumentiert
quellen: GOOGLE_SEO_GUIDE.md, templates/base.html, shop1/templates/shop1/_reviews_map.html, shop1/templates/shop1/legal/impressum.html
profil_bestaetigt: unbekannt
profil_link: https://www.google.com/maps?cid=13899750731019902000
rest_bei: bastian, kunde
---

# Local SEO — Luviq Universe

> **Stand 02.10.2026 (geprüft, abends):** `main` = `origin/main` = `7ae67ab` und live. Alle Arbeitszweige des Tages (`fix/2026-10-02-luviq-fertig`, `-rest`, `-luisa`, `-recht`, `-wissen`, `fix/2026-10-02d-standard`) sind gemergt (`git log origin/main..<zweig>` leer, `git branch -r --no-merged origin/main` leer); die GitHub-Prüfungen auf `main` sind grün (Lauf 37040107996, 02.10.2026). Live belegt am 02.10.2026 (curl): Sitemap mit 17 Adressen samt der drei Wissensbeiträge, `/llms-full.txt` 200, „Aktualisiert am …“ (`<time>`) auf den Wissensbeiträgen (GE47), `Permissions-Policy` im Kopf, `/health/` 200, Apex 301 auf www. Wo unten „Zweig“ oder „nicht gemergt“ steht, ist das **Verlauf** des jeweiligen Tages und gilt seit dem Merge als live, sofern der Satz nichts anderes sagt. Der **Verkauf ist aus** (`VERKAUF_AKTIV` ohne Variable = aus: Marke im Aufbau, Archiv statt Shop); nach Angabe des Betreibers ist **kein Gewerbe angemeldet** — die Seite nennt deshalb keine Unternehmensangaben (Impressum nach § 5 DDG nur mit Luisa Brehler als Person, Alsfeld, E-Mail).


*Woran sich der Fortschritt bemisst: an vier Punkten zu je 25 — Unternehmensprofil vorhanden · Search Console verbunden · Bewertungen vorhanden · NAP überall gleich. Bei allen sechs betreuten Seiten dieselben vier Punkte.*

**Vorbemerkung:** Luviq ist ein Online-Shop **ohne Ladengeschäft** (belegt in `agb.html`, `ueber_uns.html`,
llms.txt des Zweigs). Der Ortsbezug Alsfeld ist Marke und Herkunft, kein Besuchsort. Was Local SEO hier
leisten kann, ist Markenpflege („Luviq Universe" als Entität) und der Ortsbezug in Titeln und Schema —
kein Laufkundschafts-Ranking.

## Google-Unternehmensprofil

Seit dem 02.10.2026 gibt es ein **Google-Unternehmensprofil „Luviq“** (Angabe Bastians für Luisa im Commit `3073388`); es ist in `sameAs`, in `llms.txt` und im Schema verlinkt:
`https://www.google.com/maps?cid=13899750731019902000` (live in `llms.txt` abgerufen am 02.10.2026). **Nicht belegt** ist, ob Google das Profil bestätigt hat (`profil_bestaetigt: unbekannt`) — das sieht nur, wer im Profil angemeldet ist.

Hinweise im Code:

- `_reviews_map.html` bettet eine **Google-Maps-Karte** auf die Anschrift „Grünberger Str. 16, 36304 Alsfeld“ ein (`maps.google.com/maps?q=…&output=embed`) — seit `RE17` (`d58a96c`) erst nach einem Klick: die Adresse steht in `data-src`, bis dahin liegt ein Platzhalter „Karte laden“. Für Local SEO ändert das nichts (eine eingebettete Karte ist kein Rankingsignal).
- **Schema:** ohne Verkauf nur `Organization` (kein `ClothingStore`/`LocalBusiness`, keine Preisspanne, keine Zahlarten, kein Liefergebiet), weil ohne angemeldetes Gewerbe eine Geschäftsbehauptung irreführend wäre (`templates/base.html`, `25ff237`; live am 02.10.2026: `Organization`, `Place`, `Person`, `PostalAddress`). Damit ist die frühere Frage „`ClothingStore` oder `OnlineStore`“ erledigt; mit Verkauf kommt der alte Typ zurück.
- **`sameAs`** (GE11, GE46) nennt seit `3073388` Instagram `luviq.archive`, TikTok `@luviq.archive` und das Google-Profil (live abgerufen 02.10.2026). Das alte Instagram-Konto `luviq.universe` gibt es nicht mehr.
- **Bewertungsknopf:** `GOOGLE_REVIEW_URL` ist in Railway **nicht** auf einen echten Bewertungslink gesetzt — live zeigt `/gaestebuch/` den Knopf „Luviq Universe auf Google Maps suchen“ (Maps-Suchlink, Vorgabe in `mainweb/settings.py`). Absicht des Codes: ein Kartenlink ist kein Bewertungsformular, der Knopf hieße sonst zu Unrecht „bewerten“ (EIG87). Der echte Link (`g.page/r/…/review`) ist eine Railway-Variable und steht unter „Offen“.

## Search Console

**Verbunden.** Nach Bastians Angabe vom 02.10.2026 liegt die Property **`sc-domain:luviq-alsfeld.com`** im Konto von Luisa (`brehlerluisa@gmail.com`, nicht neu geprüft). Am 03.09.2026 einzeln nachgeprüft lag sie im Konto **`bastian.scherzinger05@gmail.com`** — zusammen mit den sechs übrigen Properties; das
zweite Konto (`…69@gmail.com`) hat keine einzige. Sie steht seither in `sites.json` des Werkzeugs, und die
Search Console ist **per OAuth** angebunden (Cloud-Projekt `gen-lang-client-0179494625`). Damit ist die
frühere Aussage dieser Datei überholt, das Werkzeug „würde raten": es rät nichts mehr.

Was weiterhin gilt: `GOOGLE_SEO_GUIDE.md` (Schritt 1) beschreibt das Vorgehen aus Sicht der Betreiberin
(Property anlegen, Verifizierungs-Tag schicken, `sitemap.xml` einreichen) und nennt als Beispiel noch die
Railway-Adresse; im `base.html` steckt kein Verifizierungs-Tag und im `static`-Ordner keine
Verifizierungsdatei (02.09.2026) — die Domain-Property braucht beides nicht, sie hängt am DNS-Eintrag.
**Die Property liegt nach Bastians Angabe vom 02.10.2026 inzwischen im Konto von Luisa** (`gsc_konto` im Kopf); die Überprüfung am 03.09.2026 sah sie noch im Konto `…05`, neu geprüft wurde das nicht (kein Zugang für Agenten).

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
| Instagram | `luviq.archive` | | | im `sameAs` und in `llms.txt` (live 02.10.2026) |
| TikTok | `@luviq.archive` | | | im `sameAs` und in `llms.txt` (live 02.10.2026) |
| Google-Unternehmensprofil | „Luviq“ | | | `maps?cid=13899750731019902000`, in `sameAs` und `llms.txt` (live 02.10.2026); Bestätigung nicht belegt |
| Branchenverzeichnisse | — | | | nicht dokumentiert |

Die Messung meldet KV01 „1 von 13 Seiten mit tel:-Link" — dieser eine Link war die **Platzhalternummer** auf `/kontakt/`. Auf `main` ist sie entfernt; danach sind es 0 Seiten, und das ist richtig so, bis die Betreiberin eine Nummer nennt.

## Offen

Stand 02.10.2026, gegen Code und Live-Seite geprüft. Erledigt und entfernt: Auslieferung der NAP-Korrektur (live: `/kontakt/` nennt Luisa Brehler, 36304 Alsfeld und `brehlerluisa@gmail.com`, „eine Telefonnummer gibt es nicht“, Antwort in der Regel innerhalb von 2 Stunden; das Impressum nennt „Website: www.luviq-alsfeld.com“), Profiladressen für `sameAs`, Schema-Typ (ohne Verkauf nur `Organization`), Telefonnummer und Zeiten (bewusst keine, siehe Bewertungsblock KV01/KV08 in [80-AUFGABEN.md](80-AUFGABEN.md)), Übergabe der Search Console. Echte Google-Bewertungen sammeln kann nur Luisa (80-AUFGABEN, „Beim Kunden“).

| Punkt | Wer |
|---|---|
| Bei Bastian: den echten Bewertungslink des Profils (`g.page/r/…/review`) als Railway-Variable `GOOGLE_REVIEW_URL` setzen; live zeigt der Knopf noch den Maps-Suchlink. Grund: Railway-Variablen setzt nur Bastian, und ein Agent darf sie nicht ändern | Bastian |
| Bei Bastian: im Profil nachsehen, ob Google es bestätigt hat, und `profil_bestaetigt` im Kopf dieser Datei auf `ja` oder `ausstehend` setzen. Grund: das sieht nur, wer im Profil angemeldet ist; ein Agent hat keinen Zugang | Bastian |

## Backlink-Plan (16.09.2026)

Gemeinsamer Plan für alle sechs Seiten: `C:\Users\basti\Desktop\pystore-overview\docs\BACKLINK-PLAN.md` — Spielregeln, Grundpaket G1–G12, Methoden, Ablauf und Fortschrittstabelle. Kurzfassung für diese Seite:

- Geschäftsadresse vorhanden (Grünberger Str. 16, Alsfeld) — Einträge nur mit Zustimmung von Luisa Brehler.
- Stand: Bing Places ✔ Import, Bing Webmaster Tools ✔ (Sitemap `www` eingereicht); Duplikat-Host am 16.09.2026 behoben (`CANONICAL_HOST`).
- Als Nächstes: **„WIR sind Alsfeld“** / Wirtschaftsförderung Alsfeld, alsaktiv, **Pinterest**-Unternehmenskonto, Fair-Fashion-Labellisten (Fashion Changers, Utopia, endlich fair), Pressebeitrag Oberhessische Zeitung, Ausstellerlisten von Kunsthandwerker-Märkten.
