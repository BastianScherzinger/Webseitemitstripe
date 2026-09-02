# Logbuch

Hier steht, was am Projekt geändert wurde und **warum**. Ein Eintrag pro
Welle des jeweiligen Verbesserungslaufs, jeweils mit Commit-Kennung.
Zweck: Wer in einem halben Jahr eine Änderung nicht versteht, findet hier
den Grund, ohne den Commit-Verlauf durchsuchen zu müssen.

Regel für neue Einträge: Datum, Welle, Schritt-Nummer, Commit-Kürzel,
ein Satz *was*, ein Satz *warum*. Keine Aussage ohne Beleg im Code.

---

## Verbesserungslauf 3 (Zweig `cockpit/2026-09-01-verbesserung-3`)

Der Lauf war in sieben Wellen mit 33 Schritten geplant. In diesem
Repository-Stand sind nur die Schritte 32 und 33 ausgeführt worden; die
Wellen 1 bis 6 und die Schritte 30/31 sind hier **nicht** angekommen
(belegt durch `git log --oneline --all`: außer den beiden unten genannten
gibt es keinen Commit mit dem Präfix „Schritt"). Die Einträge dafür stehen
deshalb als offen im Logbuch — sie werden nachgetragen, sobald die
zugehörigen Commits existieren.

| Welle | Schritte | Thema | Stand | Commit |
|---|---|---|---|---|
| 1 | 1–5 | Fundament, Tests, Prüfbefehl, Pinning | offen | — |
| 2 | 6–10 | Barrierefreiheit | offen | — |
| 3 | 11–15 | Ladezeit | offen | — |
| 4 | 16–20 | SEO-Technik | offen | — |
| 5 | 21–25 | GEO, Schema | offen | — |
| 6 | 26–29 | Inhalt | offen | — |
| 7 | 30–31 | Sicherheit (CSP, Härtung) | offen | — |
| 7 | 32 | Toten Code entfernt | erledigt | `c6e0cce` |
| 7 | 33 | Doku an den Code angeglichen, Logbuch angelegt | erledigt | `342f7fd` |

### 2026-09-01 — Welle 7, Schritt 32: Toter Code entfernt (`c6e0cce`)

**Was:** Fünf unerreichbare Fundstellen gelöscht — `_setup_admin_user()` in
`shop1/views/_helpers.py`, die Regex `_BOT_UA_RE` in `shop1/middleware.py`,
die Templates `shop1/templates/shop1/django_tutorial.html` (1.862 Zeilen)
und `railway_deployment_tutorial.html` (80 Zeilen), sowie der ungenutzte
Kontextwert `'anzahl': 42` in `shop1/views/shop.py`. Die dadurch tot
gewordenen Importe `User` und `re` fielen mit weg. Zusammen 1.999 Zeilen,
keine einzige hinzugefügt.

**Warum:** Jede Fundstelle war per Projektsuche als verweisfrei belegt.
Zwei davon waren mehr als Ballast: `_setup_admin_user()` konnte über
`User.objects.create_superuser` einen Superuser anlegen — eine solche
Funktion soll nicht ungenutzt herumliegen (die Superuser-Anlage im Betrieb
macht `start.sh`). `railway_deployment_tutorial.html` riet in Zeile 55
ausdrücklich zu `ALLOWED_HOSTS = *`; das widerspricht dem Code in
`mainweb/settings.py` und wäre früher oder später von jemandem für eine
gültige Anleitung gehalten worden.

**Bewusst nicht angefasst:** `admin_required` existiert doppelt
(`shop1/views/_helpers.py` und `shop1/admin_views.py`) — dieselbe
Sicherheitsprüfung in zwei Fassungen. Ein Zusammenführen wäre eine
Verhaltensänderung an einer Sicherheitsprüfung und gehört nicht in einen
Aufräumschritt.

**Geprüft:** `manage.py check` grün, `manage.py test shop1` grün (die App
enthält derzeit keine Tests), `collectstatic --noinput --clear` läuft
durch (148 Dateien).

### 2026-09-01 — Welle 7, Schritt 33: Doku an den Code angeglichen (`342f7fd`)

**Was:** Drei Stellen korrigiert, an denen die Dokumentation das Gegenteil
des Codes behauptete, plus zwei falsche Angaben im SEO-Leitfaden:

1. `DOCUMENTATION.md` behauptete „CSP: per settings-Variable, angepasst pro
   Deployment". Es gibt **keine** CSP — weder ein Header in
   `mainweb/settings.py` noch eine CSP-Middleware (Suche nach
   `csp`/`content.security` in `settings.py`, `requirements.txt` und
   `middleware.py` bleibt ohne Treffer). Die Zeile wurde durch die
   tatsächlich gesetzten Schutzköpfe ersetzt und das Fehlen der CSP als
   offener Punkt vermerkt.
2. `CLAUDE.md` und `DOCUMENTATION.md` behaupteten, `PageVisitMiddleware`
   blockiere den Response „niemals". Das gilt für den Geo-Lookup, nicht für
   die Datenbankschreibvorgänge: `_track()` läuft in `__call__` vor dem
   `return response`, `PageVisit` und `VisitorLog.objects.create` also
   synchron im Request-Zyklus. Beide Stellen sagen das jetzt.
3. `CLAUDE.md` nannte für das `VisitorLog`-Dedup ein 30-Minuten-Fenster,
   weil der Kommentar in `shop1/middleware.py` das so sagt. Der Code prüft
   `diff < 300`, also **5 Minuten**. Angeglichen wurde die Dokumentation an
   den Code — nicht umgekehrt, denn eine Änderung des Fensters wäre eine
   Verhaltensänderung und war nicht beauftragt. Der irreführende Kommentar
   in `middleware.py` selbst steht noch; die Doku weist ausdrücklich darauf
   hin, dass der Code maßgeblich ist.
4. `GOOGLE_SEO_GUIDE.md` empfahl als Ziel-Suchbegriff „railway hosting
   luviq". Railway ist der Hosting-Anbieter — danach sucht keine
   Kundschaft. Ersetzt durch die Begriffe, die in `templates/base.html`
   tatsächlich als `meta name="keywords"` hinterlegt sind.
5. `GOOGLE_SEO_GUIDE.md` behauptete, `DEBUG` stehe „aktuell auf `True`".
   `mainweb/settings.py` liest `os.getenv('DEBUG', 'False') == 'True'`,
   der Standard ist also `False`. Richtiggestellt samt der Folgen, die
   `DEBUG=True` hätte (Debug-Details öffentlich, kein HSTS, keine
   Secure-Cookies, `ALLOWED_HOSTS = ['*']`).

Zusätzlich hält `CLAUDE.md` jetzt fest, dass ohne `.env` mit gesetztem
`SECRET_KEY` **kein** `manage.py`-Befehl läuft — `settings.py` bricht bei
`DEBUG=False` und unverändertem Standardschlüssel mit `RuntimeError` ab.
Das kostet sonst bei jedem neuen Arbeitsplatz Zeit.

**Warum überhaupt:** Eine Dokumentation, die das Gegenteil des Codes
behauptet, ist schlimmer als keine — besonders bei Sicherheitsaussagen.
Wer der alten Zeile geglaubt hätte, hätte eine CSP für vorhanden gehalten
und nicht nachgeprüft.

**Geprüft:** `manage.py check` grün, `manage.py test shop1` grün. Reine
Textarbeit an Dateien, die nicht ausgeliefert werden.

---

## Verbesserungslauf 4 (Zweig `cockpit/2026-09-01-verbesserung-4`)

Die Wellen 1 und 2 (Schritte 1–10, Commits `65a1bd0` bis `8222aed`) haben
keinen Logbuch-Eintrag hinterlassen; ihre Commit-Nachrichten nennen das
*Was*. Ab Welle 3 wird je Schritt hier eingetragen.

### 2026-09-01 — Welle 3, Schritt 11: Meta-Beschreibungen auf 110–175 Zeichen, Schluss mit Aufforderung

**Was:** Die `meta_description` aller neun Inhaltsseiten (`index`,
`produkte`, `kontakt`, `ueber_uns`, `liefergebiet`, `gaestebuch`,
`impressum`, `datenschutz`, `agb`) neu gefasst: 157–171 Zeichen, je Seite
verschieden, jede endet mit einem Verb (entdecken, bestellen, anfragen,
kennenlernen, nachlesen, schreiben). Nur Angaben, die auf der jeweiligen
Seite selbst stehen (Alsfeld/Hessen, Luisa Brehler, E-Mail auf der
Kontaktseite, „in Hessen meist in 1–3 Werktagen zugestellt" aus dem
FAQ-Text der Liefergebietsseite). Gestrichen: „Frankfurt" (kein Beleg als
Liefergebiet), „made in Germany", „§ 5 TMG" (Gesetz seit 2024 abgelöst,
siehe offene Frage im Bericht der Welle).

**Warum:** Google kürzt Beschreibungen über etwa 160–175 Zeichen mitten im
Satz ab; die Startseite lag bei 193, Produkte bei 180. Eine Beschreibung
ohne Aufforderung verschenkt den Klick aus der Trefferliste.

### 2026-09-01 — Welle 3, Schritt 12: Ortsbezug im Titel jeder Seite

**Was:** Der automatische Produkttitel (`Produkt.meta_title`, wenn
`seo_titel` leer ist) heißt jetzt „<Name> kaufen – Luviq Universe, Alsfeld".
Die drei im Plan genannten Templates (`agb`, `datenschutz`, `gaestebuch`)
trugen zum Zeitpunkt dieser Welle bereits Ort („Alsfeld") bzw. Nutzen
(„Vintage Upcycling Mode") im `<title>` — „Alsfeld" seit Commit `df94e14`
des vorigen Laufs, der Gästebuch-Titel seit `99e9bd7` — und blieben
unverändert. Ein gepflegter `seo_titel` hat
weiterhin Vorrang.

**Warum:** Ein Titel ohne Ort oder Nutzen konkurriert mit jedem Shop im
Land; „Alsfeld" ist die einzige belegte Ortsangabe des Impressums.

### 2026-09-01 — Welle 3, Schritt 13: Abgeleitete Produkt-Metaangaben auf gültige Längen begrenzt

**Was:** In `shop1/models.py` rechnen `Produkt.meta_title` und
`Produkt.meta_description` jetzt gegen feste Grenzen (`META_TITEL_MAX` =
60, `META_BESCHREIBUNG_MAX` = 160 – dieselben Werte wie die Hilfetexte der
gepflegten Felder). Die Beschreibung wird um die Länge des Nachsatzes
gekürzt, das Ende liegt an einer Wortgrenze (`_kuerze_an_wortgrenze`). Beim
Titel entfällt der Zusatz stufenweise („kaufen – Luviq Universe, Alsfeld" →
„– Luviq Universe" → nur der Name), statt abgeschnitten zu werden. Gepflegte
`seo_titel`/`seo_beschreibung` behalten Vorrang. Nebenwirkung: Zeilenumbrüche
in der Beschreibung werden zu Leerzeichen, und ohne Beschreibung steht der
Name vor dem Nachsatz statt eines führenden „–". Keine Migration.

**Warum:** Vorher wurde erst auf 155 Zeichen gekürzt und dann ein ~60
Zeichen langer Nachsatz angehängt – bis zu ~215 Zeichen, die Google mitten
im Satz abschneidet (Befund 4.35).

### 2026-09-01 — Welle 3, Schritt 14: `lastmod` für die statischen Sitemap-Seiten, `/produkt/` → `/produkte/`

**Was:** (a) `shop1/views/legal.py` führt das Register `SEITEN_STAND`
(Routenname → ISO-Datum, von Hand gepflegt); jede der acht statischen
Sitemap-Seiten trägt daraus ein `<lastmod>`. Startwert überall
`2026-09-01`, belegt durch `git log -1 --date=short` je Template (alle
Seiten wurden in diesem und dem vorigen Lauf am selben Tag zuletzt
geändert). `impressum` steht mit im Register, obwohl es nicht in der
Sitemap ist – Schritt 16 braucht das Datum für den `WebPage`-Knoten.
(b) Neue View `produkt_uebersicht_redirect` (in `legal.py`, re-exportiert
in `views/__init__.py`), Route `produkt/` in `shop1/urls.py` **vor**
`produkt/<slug:slug>/`: 301 auf `/produkte/`.

**Warum:** Ohne `lastmod` crawlt Google statische Seiten nach eigenem
Ermessen und erkennt Änderungen spät (Befund 4.16). Ein Datei- oder
Build-Datum wäre falsch, weil es bei jedem Deploy hochspringt – deshalb
das gepflegte Register. `/produkt/` ist der Elternpfad jeder Produktseite
und lief ins 404 (Befund SU09).

### 2026-09-01 — Welle 3, Schritt 15: SEO-Tests auf die neuen Zusagen verschärft

**Was:** In `shop1/tests/test_seo.py`: (1) der Längentest verlangt für
Inhaltsseiten 110–175 Zeichen Beschreibung (vorher 50–200 für alle; die
gesperrten Konto-Seiten behalten 50–200); (2) neuer Test: jede Beschreibung
endet auf ein Verb aus `HANDLUNGSVERBEN`; (3) neuer Test: jeder Titel
nennt Ort oder Nutzen (`ORT_ODER_NUTZEN`); (4) neuer Test: **jeder**
`<url>`-Eintrag der Sitemap trägt ein `lastmod` im Format JJJJ-MM-TT, das
nicht in der Zukunft liegt – die 200-Prüfung jeder Sitemap-Adresse bestand
schon; (5) neue Klasse `ProduktMetaangabenTest` mit sechs Tests für die
Ersatzfassung von `meta_title`/`meta_description` (400 Zeichen
Beschreibung, 90 Zeichen Name, mittellanger Name, kurze Fälle, Auslieferung
im Seitenkopf). Dazu ein Test, dass `/produkt/` mit 301 auf `/produkte/`
leitet und `/produkt/<slug>/` weiterhin 200 liefert. Gegenbeweis geführt:
Startseiten-Beschreibung auf 205 Zeichen verlängert → Test (1) rot
(„/: Beschreibung 205 Zeichen, erlaubt 110–175"), danach zurückgesetzt.

**Warum:** Ohne diese Tests kann die nächste Textänderung die Zusagen aus
Schritt 11–14 still wieder brechen; die Suite meldet es jetzt sofort.

### 2026-09-01 — Welle 4, Schritt 16: `WebPage`-Knoten mit gepflegtem Änderungsdatum je Seite

**Was:** Das Register `SEITEN_STAND` aus Schritt 14 ist nach
`shop1/seiten_stand.py` gewandert (`views/legal.py` importiert es weiter
unter demselben Namen, die Sitemap ist unverändert). Daneben steht
`SEITEN_NAME` (Routenname → Bezeichnung, wörtlich wie im Menü von
`base.html`) und `seite_fuer(url_name)`, das beides als Dict oder `None`
liefert. `context_processors.shop_owner_check` legt das Ergebnis als
`seite` in jeden Template-Kontext (reines Dict-Nachschlagen über
`request.resolver_match.url_name`, kein Datenbankzugriff). Der `@graph` in
`base.html` trägt einen dritten Knoten `WebPage` mit `@id`
(`<Seitenadresse>#webpage`), `url`, `isPartOf` → `#website`, `inLanguage`
und – nur wenn die Route im Register steht – `name` und `dateModified`.
Produkt-, Konto- und Admin-Seiten bekommen den Knoten ohne diese beiden
Angaben statt eines erfundenen Datums.

**Warum:** `dateModified` gab es bisher nur auf Produktseiten (Befund
4.28/GE18); Antwortmaschinen konnten die Aktualität der übrigen Seiten
nicht einschätzen. Weil Sitemap-`lastmod` und Schema aus **einem**
Register kommen, können sie nicht auseinanderlaufen.

### 2026-09-01 — Welle 4, Schritt 17: `Person`-Knoten mit Kennung, `founder` und `author` verweisen darauf

**Was:** Im `@graph` von `base.html` steht die Gründerin jetzt als eigener
Knoten `Person` mit `@id` `/#luisa`, `name`, `jobTitle` (unverändert
„Gründerin & Creative Director") und `worksFor` → `#organization`.
`founder` am Unternehmensknoten ist ein Verweis auf diese Kennung statt
eines eingebetteten Knotens; der `WebPage`-Knoten aus Schritt 16 trägt
`author` mit demselben Verweis. Die Kennung `#luisa` ist dieselbe, die
`ueber_uns.html` für seinen ausführlicheren `Person`-Knoten schon benutzt
– JSON-LD führt beide zu einer Person zusammen. Keine neuen Angaben (keine
Biografie, kein Geburtsjahr, keine Qualifikation).

**Warum:** `<meta name="author">` nannte die Autorin, das Schema kannte nur
einen `founder` und keinen `author` (Befund 4.13/GE16). Antwortmaschinen
werten `author` als Signal, wer für den Inhalt einsteht.

### 2026-09-01 — Welle 4, Schritt 18: `BreadcrumbList` auf jeder Unterseite über einen zentralen Block

**Was:** `base.html` hat im `<head>` einen neuen, leeren Block
`brotkrume_ld` (vor `schema_ld`). Die neun Unterseiten `produkte`,
`kontakt`, `ueber_uns`, `gaestebuch`, `liefergebiet`, `impressum`,
`datenschutz`, `agb` und `produkt_detail` füllen ihn mit je einem
`BreadcrumbList`-Script. Die zwei bestehenden Brotkrumen (`produkt_detail`,
`liefergebiet`) sind in den Block gezogen; das FAQ-Schema von
`liefergebiet` bleibt in `schema_ld`. Die Startseite füllt den Block nicht.
Stationsnamen sind wörtlich die sichtbaren Menübeschriftungen aus
`base.html` („Home", „Produkte", „Gästebuch", „Kontakt", „Über uns",
„Liefergebiet", „Datenschutz", „Impressum", „AGB"); die Produktseite behält
„Orbit"/„Objekte" aus ihrer sichtbaren Brotkrume. Sichtbare Brotkrumen
wurden nicht ergänzt, der Seitenaufbau ist unverändert.

**Warum:** Sieben von neun Inhaltsseiten hatten keinen Brotkrumenpfad
(Befund 4.38/GE12); Suchmaschinen zeigen ohne ihn die rohe Adresse in der
Trefferliste. Ein zentraler Block statt neun Einzellösungen, damit die
nächste Seite denselben Weg geht.

### 2026-09-01 — Welle 4, Schritt 19: `llms.txt` mit Ort, Versandzeiten und Instagram; Wissensbereich vorbereitet

**Was:** In `views/legal.py::llms_txt`: (a) der Einleitungsabsatz nennt
jetzt Postleitzahl und Lage („Alsfeld (36304) in Hessen, zwischen Fulda und
Giessen") sowie die belegten Versandzeiten („in der Regel innerhalb von 1-2
Werktagen; innerhalb Hessens meist nach 1-3 Werktagen") – beides steht
wörtlich auf `/liefergebiet/` bzw. im Impressum; (b) die Eckdaten führen
das Instagram-Profil `https://www.instagram.com/luviq.universe/`, das
bisher nur im `sameAs` des Schemas stand; (c) neue Modulliste
`WISSEN_SEITEN` (Routenname, Ankertext, Beschreibung) – solange sie leer
ist, wird kein Abschnitt „Wissen" ausgegeben; Schritt 30 trägt die Seiten
ein. `robots.txt` ist unverändert: die dreizehn Antwort-Crawler bleiben
zugelassen, nichts wird zusätzlich gesperrt.

**Warum:** Antwortmaschinen zitieren den ersten sachlichen Absatz; ohne
Zahl und Ort ist er nicht zitierfähig (Arbeitsfeld GEO). Ein Profil, das
nur im Schema steht, kann eine Antwortmaschine nicht nachlesen (Befund
4.34/GE11). Ein leerer Abschnitt wäre ein Versprechen ohne Inhalt, daher
die Bedingung.

### 2026-09-01 — Welle 4, Schritt 20: GEO-Tests auf die neuen Schema-Knoten ausgeweitet (16 → 20)

**Was:** Vier neue Tests in `shop1/tests/test_geo.py`: (1) jede
Inhaltsseite trägt genau einen `WebPage`-Knoten mit `isPartOf` →
`#website`, einem sichtbaren `name` und einem `dateModified` im Format
JJJJ-MM-TT, nicht in der Zukunft und **gleich dem `lastmod` derselben
Adresse in der Sitemap**; (2) genau eine `Person`-Kennung je Seite, und
jedes `founder`/`author` ist ein Verweis (`{"@id": …}`) darauf, kein
eingebetteter Knoten; (3) jede Unterseite und die Produktseite tragen
genau eine `BreadcrumbList` mit lückenlosen Positionen, jeder Stationsname
steht sichtbar auf der Seite, jede Stationsadresse antwortet mit 200, die
letzte Station ist die Seite selbst, die Startseite trägt keine; (4) jede
Frage im FAQ-Schema steht **wortgleich** als Überschrift `h1`–`h6` auf
derselben Seite (neuer Helfer `_Ueberschriftenleser`). Der bestehende
Öffnungszeiten-Test ist unangetastet. Gegenbeweis geführt: Überschrift
„Zahlungsmethoden?" in `kontakt.html` zu „Welche Zahlungsmethoden gibt
es?" umformuliert → Test (4) rot („steht nicht wortgleich als Überschrift
auf der Seite"), danach zurückgesetzt.

**Warum:** Die Schritte 16–19 sind Zusagen im Quelltext, die eine spätere
Änderung still brechen kann. Der Test (1) sichert zusätzlich den Zweck des
gemeinsamen Registers: Sitemap und Schema dürfen nicht auseinanderlaufen.

### 2026-09-01 — Welle 5, Schritt 21: Startseite beginnt mit einer zitierfähigen Antwort

**Was:** Fünf bestehende Absätze in `shop1/templates/shop1/index.html` mit
Auskunft gefüllt – kein neuer Absatz, keine neue Überschrift, kein neuer
Link, kein neues Element (die Designwache `test_aufbau` erfasst jedes
Tag). Der erste Absatz nach der `h1` (`#hero-sub`) beantwortet jetzt „Was
ist Luviq Universe?": Online-Shop von Luisa Brehler aus Alsfeld, Hessen,
für handbemalte Second-Hand- und Vintage-Kleidung; jedes Stück 1-of-1,
keine Nachproduktion; Versand deutschlandweit in der Regel innerhalb von
1-2 Werktagen (belegte Zahl, wörtlich von `/liefergebiet/` und
`/kontakt/`). Die drei Feature-Absätze erklären Arbeitsweise (Pinsel und
Textilfarbe – belegt in `ueber_uns.html`), Grundlage (getragene
Second-Hand-Kleidung) und Vertrieb (ausschließlich online, kein
Ladengeschäft). Der Absatz über Luisa Brehler nennt zusätzlich Zahlungsart
(PayPal oder Vorab-Überweisung), Endpreise und § 19 UStG – wörtlich wie in
`agb.html`. Nicht behauptet: dass verkaufte Stücke aus dem Shop
verschwinden (`views/shop.py` filtert nur nach `aktiv`, nicht nach
Lagerbestand); formuliert ist „kein zweites Exemplar, keine
Nachbestellung".

**Warum:** Die wichtigste Seite begann mit Badge, Wortmarke und einem
Slogan ohne Zahl und ohne Festlegung (Befund 4.9/GE23, 4.14/GE25);
Antwortmaschinen zitieren den ersten sachlichen Absatz. Gemessen im
Inhaltsbereich (`<main>`, ein Produkt im Testbestand): vorher 261 Wörter.

### 2026-09-01 — Welle 5, Schritt 22: /produkte/ von der Bildergalerie zur Kategorieseite

**Was:** In `shop1/templates/shop1/produkte.html` bekommt der einzige
Fließtextabsatz unter der `h1` Auskunft zu allem, was ein Besucher vor der
Bestellung wissen muss: was 1-of-1 bedeutet (ein Motiv, ein Teil, keine
zweite Auflage), wie ein Stück entsteht (getragenes Basisteil, Pinsel und
Textilfarbe), wie bestellt und bezahlt wird (Anmeldung, Warenkorb, PayPal
oder Vorab-Überweisung, Endpreise nach § 19 UStG), Versanddauer (in der
Regel 1-2 Werktage) und was mit einem verkauften Stück geschieht (keine
Neuauflage). Zwei Beschriftungen an jeder Produktkarte wurden ersetzt:
„Vintage Custom Art" → „Handbemaltes 1-of-1 Unikat", „Investition" →
„Endpreis" (belegt in `agb.html` § 4). CSS-Klassen, Elemente und Reihenfolge
sind unverändert.

**Entscheidung:** Der Plan sah den neuen Text in „normal gesetzten Stellen"
vor. `produkte.html` hat keine: außer der `h1` und den Kartenbeschriftungen
gibt es nur diesen einen Absatz (Versalien, `tracking-[0.4em]`). Ein neues
Element ist durch Regel 1 ausgeschlossen, also wächst der vorhandene Absatz
– auf rund 100 Wörter begrenzt, damit die Versalienfläche nicht zur Wand wird.

**Warum:** Die wichtigste Ranking-Seite hatte im Inhaltsbereich gemessen 41
Wörter (Befund 4.3/IS19, Prüfstand 62 von 600).

### 2026-09-01 — Welle 5, Schritt 23: /ueber_uns/ und /gaestebuch/ auf Substanz gebracht

**Was:** `shop1/templates/shop1/ueber_uns.html`: der Antwortabsatz unter der
`h1` nennt jetzt eine Zahl (Versand in der Regel innerhalb von 1-2
Werktagen) und den Vertriebsweg (nur online, kein Ladengeschäft); der
Absatz über Luisa Brehler beschreibt die Arbeitsweise in drei Schritten
(Basisteil aussuchen, von Hand bemalen, in den Shop) samt Zahlungsart,
Endpreisen und § 19 UStG; die drei Wertekarten (Kuration, Veredelung,
Exklusivität) und der Visionsabsatz bekommen je einen Satz mit Auskunft
(nichts neu produziert; Pinsel und Textilfarbe, kein Motiv wiederholt;
keine Nachbestellung). `shop1/templates/shop1/gaestebuch.html`: der
Antwortabsatz nennt Postleitzahl 36304, Ort, kein Ladengeschäft,
Einzelstück und die Versandangabe; der Hinweis für nicht angemeldete
Besucher sagt, wer Beiträge schreiben kann. Die sichtbare Angabe „5.0
★★★★★" aus `_reviews_map.html` wurde weder aufgegriffen noch angefasst –
ihre Quelle ist nicht belegt. Keine neuen Elemente, Klassen unverändert.

**Warum:** `/ueber_uns/` enthielt keine einzige Zahl (Befund 4.14/GE25),
`/gaestebuch/` hatte gemessen 55 statische Wörter (Befund 4.3/IS19).

### 2026-09-01 — Welle 5, Schritt 24: Produktdetailseiten und Impressum mit Auskunft gefüllt

**Was:** `shop1/templates/shop1/produkt_detail.html`: der Absatz unter
„Spezifikationen" trägt nach der Produktbeschreibung einen statischen Teil,
der auf **jeder** Produktseite gilt – 1-of-1 Unikat von Luisa Brehler aus
Alsfeld, existiert genau einmal, keine Nachbestellung; PayPal oder
Vorab-Überweisung, Endpreis, § 19 UStG; Versand deutschlandweit in der Regel
innerhalb von 1-2 Werktagen, in Hessen meist nach 1-3 Werktagen zugestellt
(wörtlich aus `agb.html`, `kontakt.html`, `liefergebiet.html`). Kein
eigenes Element, weil die Designwache jedes Tag erfasst. Drei
Beschriftungen ohne Aussage wurden ersetzt: „Status: Active" →
„Einzelstück · 1 of 1", „Galaxy-Wide Delivery" → „Versand deutschlandweit
· in der Regel 1-2 Werktage", „Premium Energy Matrix" → „PayPal oder
Vorab-Überweisung · Endpreis nach § 19 UStG". `legal/impressum.html`: die
Unterzeile unter der `h1` bekommt einen erklärenden Satz (Anbieterin,
Ort, Inhalt der Seite). `agb.html` und `datenschutz.html` unangetastet.

**Warum:** Produktseiten hatten gemessen 23 statische Wörter und keinen
Einleitungsabsatz; das Impressum keinen (Befund 4.9/GE23, IS17/IS18).

### 2026-09-01 — Welle 5, Schritt 25: Inhaltstests messen Wortzahlen statt zu schätzen (11 → 15)

**Was:** `shop1/tests/test_inhalt.py` bekommt (1) die Messfunktionen
`inhaltstext()` (sichtbarer Text innerhalb von `<main>`, ohne
`script`/`style`/`noscript`/`template`) und `wortzahl()` (Stücke mit
mindestens einem Buchstaben oder einer Ziffer; „·", „—", „★★★★★" zählen
nicht) – mit einer Gegenprobe an bekanntem HTML, bevor die Schwellen
gelten; (2) `MINDESTWOERTER` je Seite, gesetzt auf den nach Welle 5
**gemessenen** Stand minus wenige Wörter (`/` 390, `/produkte/` 105,
`/kontakt/` 130, `/ueber_uns/` 350, `/liefergebiet/` 240, `/gaestebuch/` 95,
`/impressum/` 70, `/datenschutz/` 360, `/agb/` 170, Produktseite 95) – ein
Rückfallschutz, kein Ziel; dazu ein Test, dass jede `INHALTSSEITE` in der
Liste steht; (3) jede Inhaltsseite und die Produktseite nennen im ersten
Drittel des Inhalts eine Zahl – Ausnahme `/liefergebiet/`
(`OHNE_ZAHL_IM_ERSTEN_DRITTEL`): dort stehen die Zahlen erst in der FAQ am
Seitenende, und die Vorlage gehörte nicht zu den Dateien dieser Welle;
(4) der Antwort-zuerst-Test gilt jetzt auch für `/impressum/`; `/agb/` und
`/datenschutz/` bleiben ausgenommen, weil an Rechtstexten nicht formuliert
wird (Schritt 24). Gegenbeweis: den Absatz auf `/produkte/` auf den alten
Umfang gekürzt → Umfangs- und Zahlentest rot für `/produkte/`; danach
zurückgesetzt, `git status` zeigte nur `test_inhalt.py`.

**Warum:** Alle Wortzahlen des Laufs waren Schätzungen aus den Vorlagen
(`01-BEFUND.md` 7). Erst gemessen sind die Schritte 21–24 nachweisbar, und
erst mit Schwellen fällt auf, wenn ein Umbau den Inhalt still wieder kürzt.

### 2026-09-01 — Welle 6, Schritt 26: Wissensbereich angelegt (Route, View, Übersicht)

**Was:** Neues View-Modul `shop1/views/wissen.py` mit dem Register
`WISSEN_BEITRAEGE` (Slug → Routenname, Vorlage, Titel, Kurztext; zunächst
leer), der Übersicht `wissen()` und der Beitragsview `wissen_beitrag(slug)`;
beide samt Register in `shop1/views/__init__.py` re-exportiert.
`shop1/urls.py`: `/wissen/` (Name `wissen`) und je Registereintrag eine Route
`/wissen/<slug>/` mit festem Pfad und **eigenem Routennamen** – eine gemeinsame
`<slug>`-Route hätte für alle Beiträge nur einen Namen, aber Sitemap
(`lastmod`), `seiten_stand.py` (WebPage-Knoten) und `llms.txt` sprechen
Seiten über den Routennamen an. Übersichtsvorlage
`shop1/templates/shop1/wissen/uebersicht.html`: Antwortabsatz mit Ort, PLZ
und Einzelstück-Regel, Beitragsliste aus dem Register, ein Abschnitt „Woher
die Angaben stammen" mit Verweisen auf Über uns, Liefergebiet, AGB und
Kontakt. Keine Migration, kein Link in Navigation oder Fusszeile (Plan,
Verworfen Zeile 7). Bestehende Seiten unverändert.

**Warum:** Null Wissensseiten, 13 rankfähige Seiten gegen 30, vier
Themenbereiche mit je einer Seite (Befunde SU01, SU04, SU07, SU08, SU09).

### 2026-09-01 — Welle 6, Schritt 27: Wissensseite „Wie pflege ich handbemalte Kleidung?"

**Was:** `shop1/templates/shop1/wissen/pflege.html` unter
`/wissen/pflege-handbemalte-kleidung/` (Registereintrag `wissen_pflege` in
`views/wissen.py`). Aufbau nach dem Bauplan für alle drei Wissensseiten:
Antwort im ersten Absatz mit Festlegung (auf links, kalt oder 30 °C,
Schonprogramm, Lufttrocknung, Bügeln nur von links), sechs
Zwischenüberschriften **als Fragen** in `h2` direkt unter der `h1` – kein
Ebenensprung –, je Frage ein Antwortabsatz ohne Inline-Elemente und ein
vertiefender Absatz. `FAQPage`-Schema mit genau diesen sechs Fragen und den
wortgleichen Antwortabsätzen; Brotkrume Home → Wissen → Seite. Gemessen:
821 Wörter im Inhaltsbereich, Zahl im ersten Drittel, Titel 63 und
Beschreibung 171 Zeichen. Textilpflege ist allgemeines Sachwissen und so
formuliert (Regel 2); über Luviq steht nur Belegtes: Pinsel und Textilfarbe
auf getragener Second-Hand-Kleidung (Über uns), Einzelstück, Versand 1-2
Werktage (Liefergebiet), Kontaktformular. Keine Garantie, keine
Haltbarkeitszusage, kein Farbfabrikat – der Abschnitt zu Luviq sagt
ausdrücklich, dass diese Seite dafür keine Zahl nennt.

**Warum:** Erste Wissensseite (SU04); Fragen als Zwischenüberschriften
(GE24) und saubere Überschriftenhierarchie (IS14/BF15) kosten auf einer
neuen Seite nichts.

### 2026-09-01 — Welle 6, Schritt 28: Wissensseite „Was ist Upcycling-Mode – und was unterscheidet sie von Second Hand?"

**Was:** `shop1/templates/shop1/wissen/upcycling.html` unter
`/wissen/upcycling-mode-second-hand-vintage/` (Registereintrag
`wissen_upcycling`). Gleicher Bauplan wie Schritt 27: Antwort im ersten
Absatz mit Definition und Abgrenzung (Upcycling = getragen plus
handwerkliche Bearbeitung; Second Hand = gebraucht, unverändert; Vintage =
Alter und Stil, Faustregel „üblicherweise mindestens etwa 20 Jahre" als
ausdrückliche Konvention), sieben Fragen als `h2`, `FAQPage` wortgleich,
Brotkrume Home → Wissen → Seite. Gemessen: 941 Wörter, Zahl im ersten
Drittel, Titel 65 und Beschreibung 164 Zeichen. **Keine Marktzahlen, keine
Umweltbilanz, keine Prozentangaben zu Wasser oder CO₂** – die Frage nach
der Nachhaltigkeit wird beantwortet, indem die Seite sagt, warum sie dafür
keine Zahl nennt. Über Luviq nur Belegtes: Pinsel und Textilfarbe, keine
Drucke, kein Motiv wiederholt, keine zweite Auflage (Über uns), Bestellweg
nach Anmeldung über den Warenkorb (Produkte), PayPal oder
Vorab-Überweisung, Endpreise, § 19 UStG, Widerruf vierzehn Tage (AGB § 4,
§ 5), Versand 1-2 bzw. 1-3 Werktage, kein Ladengeschäft, 36304 Alsfeld
(Liefergebiet, Impressum).

**Warum:** Die Frage, für die eine Antwortmaschine eine Definition sucht
(SU04, GE23); zweite von drei Wissensseiten.

### 2026-09-01 — Welle 6, Schritt 29: Wissensseite „Wie finde ich bei Einzelstücken die richtige Größe?"

**Was:** `shop1/templates/shop1/wissen/groesse.html` unter
`/wissen/groesse-bei-einzelstuecken/` (Registereintrag `wissen_groesse`).
Gleicher Bauplan: Antwort im ersten Absatz (Vergleich mit der eigenen
Kleidung statt Etikett; Maße vorab erfragen), sechs Fragen als `h2`,
`FAQPage` wortgleich, Brotkrume Home → Wissen → Seite. Inhalt: warum es nur
eine Größe gibt, Messmethode (flach hinlegen; Brustweite, Länge,
Ärmellänge, Schulterbreite), warum Vintage-Schnitte und ältere
Konfektionsgrößen abweichen, welche Maße man kennen sollte, wie man über
das Kontaktformular oder brehlerluisa@gmail.com nachfragt (Kontaktseite),
was bei Nichtpassen gilt (kein Größentausch bei einem Einzelstück;
Widerruf binnen vierzehn Tagen wörtlich nach AGB § 5, Einzelheiten dort).
**Keine Größentabelle mit Zentimeterwerten** – im Projekt ist keine
hinterlegt; die Seite sagt an zwei Stellen ausdrücklich, warum nicht.
Gemessen: 890 Wörter, Zahl im ersten Drittel (36304, 1-of-1), Titel 67 und
Beschreibung 162 Zeichen. Damit sind drei Wissensseiten erreicht (SU04);
mit den sechs Verkaufsseiten ist SU07 erfüllt.

**Warum:** Grössenfrage ist bei Einzelstücken ohne Anprobe die Kaufhürde
und ein Retourengrund; eine erfundene Tabelle wäre beides zugleich.

### 2026-09-01 — Welle 6, Schritt 30: Wissensbereich angeschlossen und unter die Designwache gestellt

**Was:** (1) `shop1/seiten_stand.py`: vier Registereinträge (`wissen`,
`wissen_pflege`, `wissen_upcycling`, `wissen_groesse`, Stand 2026-09-01) mit
Namen – die Übersicht „Wissen", die Beiträge ihr `h1`-Text, weil sie in
keinem Menü stehen. (2) `shop1/views/legal.py`: vier Sitemap-Einträge mit
`lastmod` aus dem Register; `WISSEN_SEITEN` gefüllt, damit `llms.txt` den
Abschnitt „Wissen" mit beschreibendem Ankertext ausliefert. (3)
`shop1/tests/_basis.py`: die vier Adressen in `OEFFENTLICHE_SEITEN` und
`INHALTSSEITEN` – damit erben sie die bestehenden Prüfungen (200, Titel,
Beschreibung, canonical, h1, Alternativtexte, Bedienelemente, Ladezeit,
Antwort-zuerst, Zahl im ersten Drittel, WebPage-Knoten, Brotkrume,
Person-Verweise, Sitemap-Abgleich). `BEWACHTE_SEITEN` in `test_aufbau.py`
leitet sich aus `OEFFENTLICHE_SEITEN` ab und umfasst sie damit ohne
Änderung an der Datei. (4) `shop1/tests/test_geo.py`: die drei Beiträge in
`FAQ_SEITEN`, sonst meldete der FAQ-Abgleich „Schema auf Seite gefunden,
die nicht in der Liste steht"; jetzt prüft er dort Frage-für-Frage
Überschrift und Antwort. (5) `shop1/tests/test_inhalt.py`: vier Schwellen in
`MINDESTWOERTER` (gemessen 261/821/941/890 → 250/800/920/870), weil
`test_jede_inhaltsseite_ist_in_der_schwellenliste` sie verlangt. (6)
`shop1/tests/aufbau_referenz.json`: die vier Fingerabdrücke **gezielt
ergänzt** – über ein Wegwerf-Testmodul, das die Datei liest, nur fehlende
Schlüssel anfügt und mit denselben `json.dumps`-Einstellungen wie
`test_aufbau.py` zurückschreibt. `git diff --numstat`: 1054 Zeilen
hinzugefügt, **0 gelöscht**; 15 → 19 Seiten. Die Datei wurde **nicht**
gelöscht und neu erzeugt – das hätte den Schutz der fünfzehn bestehenden
Seiten still aufgehoben.

**Warum:** Ohne diesen Schritt wären die drei Seiten unsichtbar (nicht in
Sitemap und llms.txt) und ungeschützt (in keiner Testliste). Befunde SU01,
SU04, SU07, SU09, PJ02.

### 2026-09-01 — Welle 7, Schritt 31: Nicht eingebundenes Hintergrundbild entfernt

**Was:** `shop1/static/shop1/images/backgroundpics/hintergund_design_farbe_der_seite.jpeg`
(336.579 Byte, die grösste statische Datei des Projekts) gelöscht; der
Ordner `backgroundpics/` ist damit leer und verschwindet aus Git.

**Warum:** Die Datei wurde nirgends referenziert – erneute Suche vor dem
Löschen über `*.html`, `*.css`, `*.py`, `*.json`, `*.js`, `*.sh`, `*.md`
einschliesslich `tailwind_input.css` und `manifest.json`: kein Treffer;
der einzige Fund war der Eintrag im Build-Artefakt `staticfiles/staticfiles.json`,
das nicht versioniert ist und bei jedem `collectstatic --clear` neu entsteht.
Sie wanderte bei jedem Deploy durch `collectstatic` (`start.sh:36`) und wurde
inhaltsgehasht abgelegt, ohne je ausgeliefert zu werden. Befund
`01-BEFUND.md` 4.20. Geprüft: `collectstatic --noinput` ohne Fehler,
`manage.py check` grün, `manage.py test shop1` grün (147 Tests).

### 2026-09-01 — Welle 7, Schritt 32: Statische Bilder als WebP in mehreren Breiten, Favicon als ICO

**Was:** Mit Pillow (bereits in `requirements.txt`, keine neue Bibliothek)
aus den vier statischen JPEGs erzeugt, Qualität 80, Seitenverhältnis
unverändert: `hero-dragon-640/1024/1536.webp` (24,7 / 53,6 / 102,0 KB statt
179,4 KB), `ich-450/900.webp` (19,6 / 64,9 KB statt 115,2 KB),
`logo-luviq-96/192.webp` (1,1 / 2,3 KB statt 133,0 KB für ein 40-px-Logo)
und `flavicon.ico` mit 16/32/48 px (7,3 KB statt 71,0 KB, aus dem
1254-px-JPEG). Umgestellt: `index.html` (Preload mit `imagesrcset`/
`imagesizes`, Hero-`<img>` mit `srcset`/`sizes="100vw"`, Gründerinnenbild),
`kontakt.html` und `ueber_uns.html` (Gründerinnenbild mit `srcset`),
`base.html` (Favicon-Links auf `.ico`, Logo mit `srcset`/`sizes="48px"`),
`_reviews_map.html` und `login.html` (Logo). Nur `src`, `srcset`, `sizes`
und `href` geändert – keine neuen Elemente, kein `<picture>`,
`width`/`height`/`class`/`alt` unverändert.

**Bewusst auf JPEG belassen:** `og:image`, `twitter:image`, die
Bildadressen im JSON-LD, `apple-touch-icon` und `manifest.json` – Vorschau-
Dienste und iOS-Startbildschirm-Symbole nehmen WebP nicht durchgängig an,
und die alten JPEGs bleiben laut Plan liegen. Die Weiterleitungen
`/favicon.ico` → `flavicon.jpeg` in `urls.py` wurden nicht angefasst
(nicht im Plan; siehe Bericht „Für den nächsten Lauf").

**Warum:** Das Hero-Bild ist das LCP-Element der Startseite und wurde ohne
`srcset` auf jedem Handy in Desktop-Auflösung geladen; Logo und Favicon
kamen als 1290- bzw. 1254-px-JPEG auf jeder Seite mit. Summe der
Bilddateien der Startseite vorher 498,6 KB, nachher 175,3 KB (Desktop,
1536 px breit) bzw. 126,9 KB (1024 px). Befunde PF15, PF16,
`01-BEFUND.md` 4.20, 4.21. Geprüft: `collectstatic --noinput` (8 neue
Dateien, alle im Manifest), `manage.py check` grün, `manage.py test shop1`
grün (147 Tests, darunter `test_aufbau` und `test_ladezeit`).

### 2026-09-01 — Welle 7, Schritt 33 (1/4): GZip-Kompression für dynamische Antworten

**Was:** `django.middleware.gzip.GZipMiddleware` in `mainweb/settings.py`
eingetragen, direkt nach `WhiteNoiseMiddleware`. Neuer Test
`test_html_antworten_werden_komprimiert_ausgeliefert` in
`shop1/tests/test_einstellungen.py`: die Startseite trägt mit
`Accept-Encoding: gzip` den Kopf `Content-Encoding: gzip`, ohne die Angabe
kommt Klartext.

**Warum:** Bisher ging jede HTML-Seite, die Sitemap und `llms.txt`
unkomprimiert über die Leitung (Befund PF10, `01-BEFUND.md` 4.25 (4)). Die
Middleware steht **nach** WhiteNoise, weil statische Dateien dort schon
beantwortet werden und nicht bei jedem Abruf neu gepackt werden sollen –
vorkomprimierte Static-Dateien wären ein Wechsel des Storage-Backends und
stehen nicht im Plan. Django polstert gzip-Antworten seit 4.2 mit
Zufallsbytes gegen BREACH; der CSRF-Token ist ohnehin maskiert. Geprüft:
`manage.py check` grün, `manage.py test shop1` grün (148 Tests).

### 2026-09-01 — Welle 7, Schritt 33 (2/4): sitemap.xml und llms.txt aus dem Cache

**Was:** `sitemap_xml` und `llms_txt` in `shop1/views/legal.py` tragen
`@cache_page(AUSGABE_CACHE_SEKUNDEN)` (15 Minuten). `shop1/tests/_basis.py`
leert den Cache in `_pre_setup` vor jedem Test – der `LocMemCache` überlebt
die Datenbank-Rücksetzung zwischen zwei Tests, und jeder Sitemap-Test hätte
sonst den Produktbestand seines Vorgängers gesehen. Neuer Test
`AusgabecacheTest` in `test_einstellungen.py`: der zweite Abruf beider
Adressen kommt mit **null** Datenbankabfragen aus und liefert denselben
Inhalt.

**Warum:** Beide Antworten sind für jeden Abrufer gleich (kein Nutzerbezug,
keine Session) und luden bei jedem Crawler-Abruf alle aktiven Produkte
(Befund PF10, `01-BEFUND.md` 4.25 (4)). Messung mit 40 Produkten über ein
Wegwerf-Testmodul, lokal (SQLite): vorher je Abruf eine Produktabfrage;
nachher Abruf 1 mit einer Abfrage, Abruf 2 mit null Abfragen, 2,3 ms statt
129 ms (Sitemap) und 1,5 ms statt 7,7 ms (`llms.txt`) – die Absolutwerte
sagen lokal wenig, die Null bei den Abfragen ist der Beleg. Ein neues Stück
erscheint spätestens nach 15 Minuten; `cache_page` setzt zusätzlich
`Cache-Control: max-age=900`. Geprüft: `manage.py check` grün,
`manage.py test shop1` grün (149 Tests).

### 2026-09-01 — Welle 7, Schritt 33 (3/4): CACHES ausdrücklich gesetzt

**Was:** `CACHES` in `mainweb/settings.py`: `LocMemCache`, `LOCATION`
`luviq`, `MAX_ENTRIES` 300, `CULL_FREQUENCY` 3. Verhalten unverändert –
Django nahm ohne Eintrag denselben Backend-Typ.

**Warum:** Ein Cache, der nur implizit existiert, wird bei jeder
Konfigurationsfrage übersehen (Befund `01-BEFUND.md` 4.25 (4)). Der
Kommentar hält fest, was der Betreiber wissen muss: der Speicher lebt je
Gunicorn-Worker, Threads eines Workers teilen ihn, und `cache_page` sowie
die Werbeliste hängen daran. Ein prozessübergreifender Cache (Redis,
Datenbank) wäre eine neue Abhängigkeit bzw. Infrastruktur und steht nicht
im Plan. Geprüft: `manage.py check` grün, `manage.py test shop1` grün
(149 Tests).

### 2026-09-01 — Welle 7, Schritt 33 (4/4): Warenkorb-Zähler mit einer Abfrage

**Was:** `shop_owner_check` in `shop1/context_processors.py` zählt den
Warenkorb per `CartItem.objects.filter(cart__user=…).aggregate(Sum('menge'))`
statt `Cart` zu laden und `anzahl_items` (eine zweite Abfrage plus Aufbau
aller Posten-Objekte) in Python zu summieren; `None` wird wie bisher zu 0.
Neuer Test in `shop1/tests/test_daten.py`: 3 + 2 Stück ergeben 5, mit genau
einer Abfrage; ohne Warenkorb 0.

**Warum:** Der Kontextprozessor läuft bei **jedem** Seitenabruf eines
angemeldeten Nutzers; die Zählung war dort die teuerste Abfrage ohne Cache
(Befund `01-BEFUND.md` 4.25 (4), `context_processors.py:18`). Ein Cache
kam nicht in Frage – der Zähler muss sofort nach „In den Warenkorb"
stimmen. Geprüft: `manage.py check` grün, `manage.py test shop1` grün
(150 Tests).

### 2026-09-01 — Welle 7, Schritt 34: Besuchs-Middleware mit Abschalter und festem Geo-Pool

**Was:** `shop1/middleware.py`: (1) Umgebungsvariable `VISITOR_TRACKING`
(Vorgabe an; `0/false/off/no/nein/aus` schaltet ab), je Anfrage gelesen in
`tracking_aktiv()`; steht sie auf aus, endet `__call__` vor `_track()`.
(2) Der Geo-Lookup läuft in einem `ThreadPoolExecutor` mit `GEO_PLAETZE`
= 4 Threads aus der Standardbibliothek statt in einem neuen
Betriebssystem-Thread je Seitenaufruf; eine `BoundedSemaphore` zählt die
belegten Plätze, und `_geo_einreihen()` lässt den Lookup aus, wenn alle
belegt sind (Land/Stadt bleiben dann leer) oder die Adresse privat ist.
`_geo_enrich()` gibt den Platz im `finally` zurück. Das synchrone Schreiben
von `PageVisit` und `VisitorLog` bleibt unverändert – es hängt an der
Session, und ein Thread machte die Reihenfolge der Session-Schreibvorgänge
unbestimmt (Plan). Zwei neue Tests in `test_einstellungen.py`:
Abschalter beidseitig (aus → keine Einträge, Antwort 200; ohne Variable →
Einträge) und Pool (private Adresse → kein Auftrag; öffentliche → genau
einer; alle Plätze belegt → ausgelassen, keine Warteschlange); `submit`
wird abgefangen, kein Netzzugriff im Test.

**Warum:** Ohne Abschalter wartete bei einer hakenden pystore-Datenbank
jeder Besucher auf den Verbindungstimeout; ohne Obergrenze erzeugte ein
Crawler-Schwarm beliebig viele Threads, jeder mit 4 s Netz-Timeout
(Befund PF10, `01-BEFUND.md` 4.25 (2, 3), 6.2). Geprüft: `manage.py check`
grün, `manage.py test shop1` grün (152 Tests – die Basisklasse ruft die
Middleware bei jedem Abruf auf).

### 2026-09-01 — Welle 7, Schritt 35: Gunicorn mit Threads, Worker-Erneuerung und kürzerem Timeout

**Was:** `start.sh`: `--worker-class gthread --threads 4` (je Worker, also
2 × 4 = 8 gleichzeitige Anfragen statt 2), `--timeout 30` statt 120,
`--max-requests 1000 --max-requests-jitter 100`. Worker, Threads und
Timeout sind über `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT`
ohne Deploy zurücknehmbar. Kein `--preload`.

**Warum:** Zwei gleichzeitige Anfragen waren die Obergrenze für den ganzen
Shop, und eine hängende blockierte zwei Minuten lang einen halben Pool –
die Erklärung für Ausreisser bis 11 s (Befund PF10, `01-BEFUND.md` 4.25
(1)). 30 s liegen fast dreifach über der langsamsten gemessenen Seite.
Jeder Thread hält eine eigene Datenbankverbindung (`CONN_MAX_AGE=600`),
dazu bis zu 4 je Worker aus dem Geo-Pool – zusammen höchstens 16 Verbindungen
je Datenbank; der `LocMemCache` wird je Worker von seinen Threads geteilt.
Geprüft: `sh -n start.sh` Exitcode 0, `manage.py check` grün, `manage.py
test shop1` grün (152 Tests). Gunicorn läuft nicht unter Windows; ein
lokaler Start mit denselben Parametern war deshalb nicht möglich – die
Wirkung lässt sich erst am veröffentlichten Stand messen.

### 2026-09-02 — Welle 8, Schritt 36: Content-Security-Policy als Report-Only

**Was:** `shop1/middleware.py`: neue `ContentSecurityPolicyMiddleware`
(eigener Code, keine Abhängigkeit), in `MIDDLEWARE` hinter WhiteNoise.
`mainweb/settings.py`: `CSP_QUELLEN` (Positivliste) und `CSP_MODUS`
(Umgebungsvariable; `report-only` = Vorgabe, `scharf`, `aus`; ein
unbekannter Wert fällt auf Report-Only zurück). `script-src`/`style-src`
mit `'unsafe-inline'`/`'unsafe-eval'` plus `cdn.jsdelivr.net`,
`fonts.googleapis.com`, `fonts.gstatic.com`, `*.paypal.com`,
`*.paypalobjects.com`; `frame-src` für `maps.google.com`, `www.google.com`
und PayPal; `img-src https:`; scharf: `frame-ancestors 'none'`,
`base-uri 'self'`, `form-action 'self'`, `object-src 'none'`.

**Warum:** Es gab keine CSP (Befund SI08, `01-BEFUND.md` 4.19). Eine
strenge Richtlinie ist mit dem Inline-Code der Templates nicht möglich,
ohne den sichtbaren Aufbau zu ändern (Regel 1). Die Kopfzeile geht
zuerst als `Content-Security-Policy-Report-Only` hinaus: der Browser
meldet Verstösse nur in der Konsole und blockiert nichts. Erst nach der
Prüfung im Browser auf `/`, `/produkte/`, `/gaestebuch/`, `/checkout/`,
`/payment/` und im Admin-Panel wird `CSP_MODUS=scharf` gesetzt – ohne
Deploy. `img-src https:` statt nur Cloudinary, weil `Werbung.bild` frei
eingetragene Bild-URLs beliebiger Hosts enthält. Geprüft: `manage.py
check` grün; `manage.py test shop1`: 151 von 152 grün, der eine
Fehlschlag (`test_geo.test_die_produktseite_nennt_ihr_aenderungsdatum`)
ist zeitbedingt und vorbestehend – er vergleicht das UTC-Datum von
`aktualisiert_am` mit dem in Europe/Berlin gerenderten `dateModified`
und schlägt zwischen 22:00 und 24:00 UTC fehl (Lauf um 23:17 UTC); die
Tests in Schritt 40 belegen die Kopfzeile.

### 2026-09-02 — Welle 8, Schritt 37: Domainvarianten per 301 auf den kanonischen Host

**Was:** `shop1/middleware.py`: neue `CanonicalHostMiddleware`, ganz vorn
in `MIDDLEWARE` (vor der HTTPS-Weiterleitung der `SecurityMiddleware`).
`mainweb/settings.py`: `CANONICAL_HOST` aus der Umgebungsvariablen
(Schema und Pfad werden abgestreift); ist sie gesetzt, kommen der Host und
seine www-Nebenvariante zusätzlich in `ALLOWED_HOSTS` und
`CSRF_TRUSTED_ORIGINS`. Umgeleitet wird **nur** der Host, der sich vom
kanonischen durch das `www.` unterscheidet – mit 301, vollem Pfad samt
Query und `https`, sobald die Anfrage sicher ist oder
`SECURE_SSL_REDIRECT` gilt (eine Weiterleitung statt der Kette
http → https → www). Railway-Adresse, `localhost` und alle anderen Hosts
bleiben unberührt; ohne Variable tut die Middleware nichts.

**Warum:** Beide Schreibweisen antworteten mit 200, nur ein `canonical`
unterschied sie – Google darf den ignorieren, eine 301 nicht (Befund
TS11, `01-BEFUND.md` 4.1). `PREPEND_WWW` schied aus, weil es auch
`*.up.railway.app` umschriebe. Der kanonische Host selbst wird nie
umgeleitet, deshalb ist keine Schleife möglich. Geprüft: `manage.py
check` grün; `manage.py test shop1`: 151 von 152 grün, derselbe
zeitbedingte, vorbestehende Fehlschlag in `test_geo` wie bei Schritt 36
(Lauf vor 00:00 UTC). Die vier Weiterleitungsfälle prüft Schritt 40.
Offen beim Hoster: der DNS-Eintrag der Nebenvariante muss auf denselben
Dienst zeigen, und `CANONICAL_HOST=www.luviq-alsfeld.com` muss in Railway
gesetzt werden – erst dann wirkt die Regel.

### 2026-09-02 — Welle 8, Schritt 39: Prüfbefehl auf die ausgelieferte Seite ausgeweitet und in start.sh angeschlossen

**Was:** `shop1/management/commands/pruefe_seite.py`: zwei neue
Prüfungen. (1) `_pruefe_produkte`: kein aktives Produkt ohne Name, Slug,
Beschreibung oder Preis (FEHLER), ohne Bild (WARNUNG); kein Slug doppelt
(Vergleich in Kleinschreibung). (2) `_pruefe_ausgelieferte_seite`: über
den Django-Testclient (kein Netzzugriff) wird `/sitemap.xml` geholt und
jede genannte Adresse abgerufen – 200 Pflicht; je Seite genau ein Titel
(25–70 Zeichen, sonst WARNUNG), genau eine Beschreibung (über 175 Zeichen
FEHLER, unter 110 FEHLER auf Inhaltsseiten und WARNUNG auf Produktseiten),
`canonical` auf sich selbst, `robots` ohne `noindex`; jedes JSON-LD parst
und enthält `Organization`, `WebPage` (Inhaltsseiten) bzw. `Product`
(Produktseiten) und ausser auf `/` eine `BreadcrumbList`; auf `/` die
Schutzkopfzeilen (nosniff, `X-Frame-Options: DENY`, Referrer-Policy, HSTS
ausser bei DEBUG) und die CSP aus Schritt 36 mit `frame-ancestors 'none'`,
`base-uri 'self'`, `form-action 'self'`, `object-src 'none'` – fehlt sie
ganz, FEHLER; läuft sie als Report-Only, WARNUNG. Die Abrufe laufen mit
`VISITOR_TRACKING=False` und in je einer Transaktion auf `default` und
`pystore`, die am Ende zurückgerollt wird: keine Sitzung, kein
Besuchseintrag und – wichtig – keine Werbe-Impression, die
`startseite()` sonst bei jedem Abruf von `/` zählt und dem Werbekunden
berechnet. Host der Abrufe: `CANONICAL_HOST`, sonst der Host aus
`SITE_URL`, sonst `localhost`. `start.sh`: Aufruf nach `collectstatic`
(die Seiten brauchen das Manifest) und vor Gunicorn, nicht blockierend
(`|| echo "WARNING: …"` wie bei `collectstatic`); scharf per `--streng`.

**Warum:** Der Befehl prüfte nur Einstellungen und Datenbanken, der
Katalog verlangt die ausgelieferte Seite (Befund PJ01 Teil 2,
`01-BEFUND.md` 4.5). Ein blockierender Aufruf nähme die Seite bei einer
fehlenden Variablen offline. Geprüft: `manage.py check` grün; im
Testumfeld meldet der Befehl „13 von 13 Sitemap-Adressen antworten mit
200 und wurden geprüft" ohne FEHLER aus den neuen Prüfungen; `manage.py
test shop1`: 151 von 152 grün, derselbe zeitbedingte, vorbestehende
Fehlschlag in `test_geo` (Lauf vor 00:00 UTC). `sh -n start.sh` liess
die Sandbox nicht zu; die Änderung ist eine Zeile nach dem Muster der
`collectstatic`-Zeile darüber.

### 2026-09-02 — Welle 8, Schritt 40: Betriebs- und Schutztests nachgezogen

**Was:** `shop1/tests/test_einstellungen.py`, 27 → 42 Tests. (1) CSP:
Kopfzeile gesetzt (Vorgabe Report-Only) mit `frame-ancestors 'none'`,
`base-uri 'self'`, `form-action 'self'`, `object-src 'none'`; `scharf`
sendet dieselbe Richtlinie blockierend, `aus` keine, ein Tippfehler fällt
auf Report-Only zurück; Gegenbeweis als Test (Middleware per
`modify_settings` entfernt → keine Kopfzeile); jede von öffentlichen
Seiten und Admin-Panel eingebundene Fremdquelle (`<script src>`,
Stylesheet, Iframe, Nachladen per `.src =`) muss in der passenden
Direktive stehen; PayPal-SDK-Adresse aus `payment.html` sowie
`www.paypal.com`, `www.sandbox.paypal.com`, `www.paypalobjects.com` gegen
`script-src`/`img-src`/`frame-src`/`connect-src`. (2) Weiterleitung, die
vier Fälle des Plans: kanonischer Host → 200; Nebenvariante → 301 mit
vollem Pfad samt Query auf `https://www.…`, auch aus einem HTTP-Aufruf in
einer Antwort; Railway-Adresse und `localhost` → keine Weiterleitung;
Variable leer → keine Weiterleitung; dazu die Bereinigung von
`CANONICAL_HOST` (Schema, Schrägstrich, Grossschreibung) und die Aufnahme
beider Varianten in `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`. (3) HSTS wird
auf `/` und `/produkte/` mit `max-age ≥ 31536000`, `includeSubDomains`,
`preload` gesendet (die übrigen Schutzkopfzeilen prüfte
`test_jede_antwort_traegt_die_schutzkoepfe` schon). (4) Fehlt `DEBUG` in
der Umgebung, gilt der Betriebsmodus und der Startschutz wirft bei
unverändertem Schlüssel `RuntimeError` (die Fälle „DEBUG=False" und
„unsicherer Schlüssel" bestanden bereits). (5) Prüfbefehl: Bericht nennt
„n von n Sitemap-Adressen" mit n ≥ 13 und Exitcode 0 im sauberen Zustand;
aktives Produkt mit leerer Beschreibung (per `update()`) → Exitcode 1 und
FEHLER; `CSP_MODUS=aus` → FEHLER, Report-Only → WARNUNG; der Lauf
hinterlässt keine Spuren (Werbe-Impressionen 0, kein `VisitorLog`, kein
`PageVisit`). Der Fall „fehlende Pflichtvariable → Exitcode 1" bestand
bereits (`test_fehlende_admin_zugangsdaten_werden_gemeldet`).

**Warum:** Sichert Schritt 36–39 (Befunde PJ02, PJ04, SI08, TS11).
Gegenbeweise: der Spuren-Test wurde ohne die `set_rollback`-Zeilen rot
(„2 != 0" – `/` wird zweimal abgerufen); der Middleware-Gegenbeweis
steckt als eigener Test in der Suite. Geprüft: `manage.py check` grün;
`manage.py test shop1`: 166 von 167 grün, derselbe zeitbedingte,
vorbestehende Fehlschlag in `test_geo` (Lauf um 23:28 UTC).

### 2026-09-02 — Welle 9, Schritt 41: Warenkorb-Tests

**Was:** Neues Modul `shop1/tests/test_warenkorb.py`, 8 Tests über die
Views in `views/cart.py` und den Sitzungsabgleich `_sync_session_to_db`
(`views/_helpers.py`): Hinzufügen kopiert Name und Preis, und kein Feld
von `CartItem` verweist auf `Produkt`; eine spätere Preisänderung (per
`update()`) wirkt nicht rückwirkend; ein gelöschtes Produkt bricht die
Warenkorbseite nicht; zweimal Hinzufügen erhöht die Menge statt eine
zweite Zeile anzulegen; die Menge bleibt beim Lagerbestand stehen und
ein ausverkauftes Produkt kommt nicht hinein; Entfernen nimmt nur diesen
Posten heraus und die Summe stimmt; der Sitzungswarenkorb wandert beim
Anmelden über `/login/` in die Datenbank, ein vorhandener Posten wird in
der Menge zusammengeführt statt verdoppelt, die Sitzung ist danach leer
und eine zweite Anmeldung fügt nichts hinzu; fremde Warenkörbe sind
weder sichtbar noch per Entfernen-Adresse veränderbar (eigener
Testclient für die zweite Kundin, weil die noch nicht angezeigte
Erfolgsmeldung sonst im Cookie mitreist).

**Warum:** `views/cart.py` und `_sync_session_to_db` hatten null Tests
(Befunde PJ02, PJ04, 01-BEFUND 3.3); die Zusage der Denormalisierung war
nur am Modell geprüft, nicht auf dem Weg, den eine Kundin nimmt. Alle
Klassen erben von `LuviqTestCase` (`secure=True`, beide Datenbanken).
Geprüft: `manage.py check` grün; `manage.py test shop1`: 174 von 175
grün, derselbe zeitbedingte, vorbestehende Fehlschlag in `test_geo`
(Lauf um 23:55 UTC).

### 2026-09-02 — Welle 9, Schritt 42: Zahlungspfad-Tests

**Was:** Neues Modul `shop1/tests/test_zahlung.py`, 11 Tests über
`views/checkout.py`. Der PayPal-Aufruf (`requests` im Modul `checkout`)
und der Mailversand werden ersetzt, geprüft wird die Entscheidung der
Anwendung: (1) ein zu niedrig bezahlter Betrag (1 € für 80 €, Status
`COMPLETED`, echte Kennung) wird abgelehnt – die Bestellung bleibt
`pending`, Lagerbestand und `aktiv` unverändert; (2) 80 in USD werden
abgelehnt; (3) eine PayPal unbekannte Kennung (404) wird abgelehnt, die
Abfrage geht an `api-m.sandbox.paypal.com/v2/checkout/orders/<Kennung>`;
(4) Status `CREATED` statt `COMPLETED` wird abgelehnt; (5) `/checkout/`
legt genau eine Bestellung an, `OrderItem` kopiert Name, Preis und
Menge, und Umbenennen, Umpreisen oder Löschen des Produkts ändert die
Bestellung nicht; (6) Gegenprobe: eine passende Zahlung markiert die
Bestellung als `paid`, bucht das Einzelstück ab (Bestand 0, inaktiv)
und die Erfolgsseite leert den Warenkorb; (7) dieselbe Kennung ein
zweites Mal: für dieselbe Bestellung antwortet der Server ohne PayPal
erneut zu fragen, für eine andere Bestellung mit 400 „bereits
verwendet" – es bleibt bei einer bezahlten Bestellung; (8) wirft der
Mailversand, bleibt die Bestellung bezahlt und der Ausfall steht mit
Bestellnummer im Protokoll `shop1`; (9) eine fremde Bestellung lässt
sich nicht bezahlt melden (404, kein PayPal-Aufruf); (10) der
Willkommensrabatt senkt den Betrag auf 72 € und erlischt nach der
Zahlung; (11) Checkout (GET und POST) und Zahlungsmeldung verlangen eine
Anmeldung.

**Warum:** `checkout.py` hatte null Tests, einschliesslich
`_verify_paypal_order` (Befunde PJ02, PJ04, 01-BEFUND 3.3, 6.1 (5)).
Gegenbeweis nach Plan: Betragsvergleich in `_verify_paypal_order` auf
`return True` gesetzt → Test (1) und Test (2) rot, danach
zurückgenommen (`git status` zeigt `checkout.py` unverändert). Der
Betragsvergleich hat dabei keinen Fehler gezeigt – kein
Sicherheitsbefund. Geprüft: `manage.py check` grün; `manage.py test
shop1`: 186 von 186 grün (Lauf nach 00:00 UTC, daher auch der
zeitbedingte Test in `test_geo` grün).

### 2026-09-02 — Welle 9, Schritt 43: Konto-Tests (Registrierung, Verifizierung, Passwort, Löschung, Axes)

**Was:** Neues Modul `shop1/tests/test_konto.py`, 10 Tests. Registrierung
legt Nutzer und `UserProfile` an (unbestätigt) und verschickt genau eine
Mail an die eingetragene Adresse, deren Inhalt den Link mit dem Token
des Profils trägt; ein gültiger Verifizierungslink setzt
`email_verified`, ein zweiter Aufruf schadet nicht und verbrennt den
Token nicht; ein gefälschter Token (fremde UUID, kein UUID, Nullen)
verifiziert nichts und leitet ohne 500 zur Startseite; ein vergebener
Benutzername legt kein zweites Konto an und verschickt nichts; der
Passwortwechsel verlangt das alte Passwort und meldet nicht ab; die
Kontolöschung löscht nur per POST (GET leitet zum Profil), entfernt
Konto und Profil und meldet ab; das Konto der Shopbesitzerin lässt sich
nicht löschen; `django-axes` sperrt nach `AXES_FAILURE_LIMIT`
Fehlversuchen den Benutzernamen von dieser Adresse auch mit richtigem
Passwort (Sperrstatus laut `AXES_HTTP_RESPONSE_CODE`, Vorgabe 429, mit
`AXES_LOCKOUT_TEMPLATE`), während eine andere Kundin von derselben
Adresse weiter hineinkommt; ein einzelner Fehlversuch sperrt nicht und
eine gelungene Anmeldung setzt die Zählung zurück. Sperrzustand wird in
`setUp`/`tearDown` per `axes.utils.reset()` geleert. Die Anmeldeklassen
laufen mit dem MD5-Test-Hasher (`override_settings`), weil rund
dreissig PBKDF2-Hashes den Lauf um über eine Minute verlängerten.

**Befund:** Der Plan erwartete „eine vorhandene E-Mail legt kein
zweites Konto an". Das stimmt nicht: `CustomUserCreationForm` prüft die
Adresse nicht auf Eindeutigkeit, die zweite Registrierung legt ein
zweites Konto an und verschickt eine zweite Mail. Nicht behoben (Formular
steht nicht im Plan, Verhalten der Registrierung ist eine Entscheidung
über den Shop); stattdessen hält
`test_eine_vorhandene_email_legt_heute_ein_zweites_konto_an` den
heutigen Zustand fest und nennt im Docstring, wie er umzudrehen ist,
sobald eine `clean_email`-Prüfung kommt.

**Warum:** Null funktionale Tests für Registrierung, Verifizierung,
Passwortwechsel, Kontolöschung (Befunde PJ02, PJ04, 01-BEFUND 3.3); die
Axes-Einstellung „Benutzername und Adresse" war nur als Wert, nicht im
Verhalten geprüft. Geprüft: `manage.py check` grün; `manage.py test
shop1`: 196 von 196 grün.
