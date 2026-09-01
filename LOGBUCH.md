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
