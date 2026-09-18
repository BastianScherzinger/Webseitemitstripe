---
bereich: technik
titel: Technik, Hosting und Aufbau
stand: 2026-09-18
status: teilweise
fortschritt: 74
zusammenfassung: 18.09.2026: Zweig recht/2026-09-18-marke-im-aufbau (9b12276) legt den Verkaufsschalter VERKAUF_AKTIV an (shop1/verkauf.py: Kontextprozessor und Middleware, Vorgabe aus, Falle 22). 18.09.2026: Paket 282 (Zweig sofort/2026-09-18-re16-und-2-weitere, 3b2b602, 5040cc5 und 45b1477 vor main = origin/main = 42008d9, nicht gemergt) legt railway.json (Bauweg DOCKERFILE, startCommand /app/start.sh wie das CMD des Images, ohne healthcheckPath) und runtime.txt (python-3.11 wie das Basisabbild) an (VL02); DeployDateienTest in test_einstellungen hält beide und die Constraint-Zeile für requirements.lock gegen Dockerfile und requirements.txt. Laut Commit 302/302 Tests grün. Paket 267 ist seit dem Merge 42008d9 auf main und origin/main. Paket 267 (Zweig sofort/2026-09-18-kv11-und-2-weitere, 1737e74 und 5515bf3) — der Filter cloud setzt die Endung jeder Cloudinary-Adresse auf .webp, sodass der Rückfall von f_auto WebP statt JPEG/PNG ist (PF15), und start.sh packt die statischen Dateien nach collectstatic mit python -m whitenoise.compress, weil ManifestStaticFilesStorage keine .gz anlegt und WhiteNoise nur vorhandene ausliefert (PF26, nicht blockierend). 298 Testfunktionen gezählt, laut Bausitzung grün; einen Lauf der Suite nennt kein Commit. Paket 254 ist seit dem Merge ba07fc9 auf main und origin/main. Paket 254 (Zweig sofort/2026-09-18-mw21-und-2-weitere, 290f422, 845d759 und eb4ab9b) gibt der Kontaktmail eine Antwortadresse (MW21): send_brevo_email nimmt reply_to an und setzt es als replyTo in der Brevo-API und als reply_to beim SMTP-Rückfall, der dafür über EmailMultiAlternatives statt send_mail läuft; kontakt() übergibt die Adresse aus dem Formular, alle anderen Mails bleiben ohne. Dazu elf Dateien ohne Verhaltensänderung für das Code-Audit aufgeräumt (PJ07: Modulbeschreibungen, unbenutzte Einfuhren, umbrochene Zeilen, fix_pystore_schema protokolliert seinen Fehlschlag jetzt auch im Logger shop1). Vier neue Tests in test_formulare, 294 Testfunktionen gezählt; einen Lauf der Suite nennt kein Commit. Paket 248 ist seit dem Merge 31c6041 auf main und origin/main. Paket 248 (Zweig sofort/2026-09-18-re15-und-2-weitere, d58a96c, 329dbc4 und 2f51192) nimmt die Google-Karte aus dem automatischen Ladevorgang: beide Einbettungen in _reviews_map.html tragen ihre Adresse jetzt in data-src statt in src, und das Skript am Körperende von templates/base.html legt darüber einen Knopf „Karte laden" samt Hinweis auf die Übertragung und setzt src erst nach dem Klick (RE17) — vorher geht keine Anfrage an maps.google.com. Der Platzhalter entsteht bewusst im Skript und nicht in der Vorlage, damit der ausgelieferte Aufbau unverändert bleibt; ohne JavaScript bleibt der Rahmen leer. data-src ist damit das fünfte Ersatzattribut neben data-bestaetigen, data-bei-fehler-ausblenden, data-auto-absenden und data-schrift-nachladen; frame-src in CSP_QUELLEN muss maps.google.com weiter erlauben, obwohl keine Vorlage die Adresse mehr als src führt (eigener Test). Dazu heisst der Absendeknopf des Bestellformulars „Zahlungspflichtig bestellen" statt „Continue to Payment →" (RE21, nur Text) und die Datenschutzerklärung beschreibt den Platzhalter statt der automatischen Einbettung (seiten_stand.py für datenschutz auf 2026-09-18). Neue Testklasse EinbettungErstNachKlickTest in test_einstellungen; laut Commits manage.py check grün und 290/290 Tests grün, im Browser ungeprüft. RE15 (Cookie-Banner) ist nicht anwendbar — die Seite setzt kein eigenes Cookie, nutzt keinen Gerätespeicher und lädt seit RE17 nichts Einwilligungspflichtiges von selbst. 17.09.2026: Paket 243 (Zweig sofort/2026-09-17-kv05-und-2-weitere, b736994, 06503a7 und 9cd641f vor main = origin/main = 911c26a, nicht gemergt) setzt den Datenschutzhinweis ins Kontaktformular (KV05, als Fliesstext ohne eigenes Element, weil die Designwache Elemente zählt) und gibt dem Fallenfeld seine Kennzeichen an sich selbst (KV06); neue Falle 20: ein mehrzeiliger {# … #}-Kommentar bleibt im HTML stehen und seine Beispiel-Tags zählen als Elemente. Paket 238 (Zweig sofort/2026-09-17-bf24-und-2-weitere, 8014429 und 22fea97 vor main = origin/main = f489e76, nicht gemergt) nimmt die Fehlermeldung des Kontaktformulars aus dem Meldungsbereich der Seite heraus — kontakt() in views/shop.py gibt sie als Kontextwert fehler an die Vorlage, sie steht als div id=kontakt-fehler mit role=alert im Formular, und die vier Pflichtfelder verweisen mit aria-describedby darauf (BF24); dazu ein RSS-Feed unter /feed/ (Klasse WissenFeed in views/wissen.py, django.contrib.syndication; wie jede neue View in views/__init__.py re-exportiert), verlinkt im Kopf jeder Seite und in llms.txt (GE32). 285 Testfunktionen gezählt, laut Bausitzung grün. IS23 (doppelte Hauptbegriffe) ist nicht im Code lösbar — Name und seo_titel setzt nur die Betreiberin. Paket 227 ist seit dem Merge f489e76 auf main und origin/main. Paket 227 (Zweig sofort/2026-09-17-pj05-und-2-weitere, a708c7f und a8190b8) protokolliert in _bestaetigung_senden() (views/legal.py) einen Cache-Fehler der Newsletter-Tagessperre mit _log.exception statt ihn zu verschlucken (PJ05), und die Meldungen in base.html tragen role="alert" bzw. role="status", das Kontaktformular aria-live="polite" (BF24); 278 Testfunktionen, laut Bausitzung grün. PF31 (Skripte selbst ausliefern) ist nicht möglich — die vier Bibliotheksdateien liegen nicht im Projekt. Paket 223 ist seit dem Merge f8643f0 auf main und origin/main. Paket 223 (6b618e4) kennzeichnet kontakt() in views/shop.py mit einem begründeten offen-ok-Vermerk als bewusst öffentlich (PJ05 anders eingebaut, nur Kommentar, kein Verhalten geändert). Paket 219 ist seit dem Merge dd804dc auf main und origin/main (ad93081). Keine automatischen Mails mehr an eingetippte Adressen (`a437803`). Stack läuft stabil. Mit Paket 219 (SI40, MW18) steht pillow auf 12.3.0 statt 11.3.0 (SI40, requirements.txt und requirements.lock; installiert und getestet ist 12.3.0 noch nirgends), und das Kontaktformular speichert jede angenommene Anfrage vor dem Mailversand im neuen Modell KontaktAnfrage (MW18, Migration 0019, im Django-Admin nur lesen und löschen) — ein kaputter Mailweg verschluckt keine Anfrage mehr; 270 Testfunktionen, laut Bausitzung grün. Paket 216 ist seit dem Merge 8717afe auf main: dort sperrt das Kontaktformular beim Absenden seinen Knopf (neues Merkmal data-einmal-absenden, ausgewertet im head-Skript von base.html), die Newsletter-Anmeldung sperrt ihren Knopf im eigenen Skript, und doppelt_abgeschickt() in views/shop.py führt eine wortgleiche zweite Anfrage binnen zwei Minuten ohne zweite Mail zusammen (LocMemCache je Prozess); dazu Pflichtfeld-Stern und maxlength = KONTAKT_LAENGEN an den vier Kontaktfeldern; 264 Testfunktionen, laut Bausitzung grün, im Browser ungeprüft. Auf main liegen seit d978a89 die serverseitige Prüfung und die Drosselung je IP (FO06, FO09; zu_viele_anfragen, 5 Anfragen in 15 Minuten, letzter X-Forwarded-For-Eintrag), seit d90067a der Spamschutz (Fallenfeld, signierter Zeitstempel, Punkteschwelle in shop1/spamschutz.py), und der Zweig mit pruefe_mail/GE15 ist gemergt. Seit den Merges 0c18ea7, 4ec540b, 1a5f36b, c522ff9, 0d5500b und 43f25c3 liegen auf main die scharf gestellte CSP, die Nonce im script-src statt 'unsafe-inline' (Handler-Attribute durch data-Attribute ersetzt), die festgenagelten Paketfassungen samt requirements.lock (Django 5.2.17), die abgearbeiteten Audit-Funde, die Danke-Seite /kontakt/danke/ (never_cache), die Produktkarte als zwei Bausteine unter shop1/templates/shop1/teile/ (Falle: load wird an ein include nicht vererbt), integrity/crossorigin an den vier Fremdskripten und der zweite Prüfbefehl pruefe_links. Dritter Prüfbefehl ist pruefe_mail — Einstellungen beider Mailwege, Anmeldung an Brevo-API (/v3/account) und SMTP-Relay, Testmail mit --an, Geheimnisse nur als „gesetzt (n Zeichen)"; wie pruefe_links bewusst nicht an start.sh angeschlossen und gegen die echten Zugangsdaten noch nie gelaufen. Offen bleiben der Merge von Paket 227, die Skriptdateien für PF31, der erste Lauf mit pillow 12.3.0, die Speicherung der Kontaktanfragen in der Datenschutzerklärung, ein gemeinsamer Zähler über alle Worker, Bezahlseite und Ersatzskripte mit Browserkonsole, ein echter pruefe_mail-Lauf, die zwei Chart.js-Einbindungen des Admin-Panels ohne integrity, 'unsafe-eval' für Alpine.js, der erste CI-Lauf mit 5.2.17, CANONICAL_HOST in Railway, der Merge von Paket 282 (railway.json gilt erst danach) und die Permissions-Policy.
offen: 14
quellen: CLAUDE.md, DOCUMENTATION.md, LOGBUCH.md, paypal_sandbox_tutorial.md, start.sh, Dockerfile, requirements.txt
---

# Technik — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Bereichswert **Code-Qualität** des Laufs vom 02.09.2026 (Regelstand `2026-09-02a`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße.*

Detailquelle bleibt [`../CLAUDE.md`](../CLAUDE.md) (Architektur, Fallstricke) und
[`../DOCUMENTATION.md`](../DOCUMENTATION.md) (Modelle, E-Mail-Flows, Admin, Sicherheit).

> **Der Ordner steht auf dem Zweig `cockpit/2026-09-01-verbesserung-4`, live läuft `main`.**
> Wo unten „Zweig" steht, ist es noch nicht ausgeliefert. Der Unterschied ist in
> [90-NOTIZEN.md](90-NOTIZEN.md) aufgeschlüsselt.
>
> **Nachtrag 11.09.2026:** `cockpit/2026-09-01-verbesserung-4` ist inzwischen in
> `main` enthalten (`511ffe5` liegt auf `main`). Der Ordner steht jetzt auf
> **`sofort/2026-09-11-pj05-und-2-weitere`**, drei Commits vor `main`
> (`9ebad08` PJ05, `9a3226f` SI08, `51cbf74` PJ11). Was unten mit
> „Zweig 11.09." markiert ist, steckt nur dort und ist noch nicht ausgeliefert.
>
> **Zweiter Nachtrag 11.09.2026 (Paket 164):** `sofort/2026-09-11-pj05-und-2-weitere`
> ist mit `0c18ea7` in `main` gemergt; `main` und `origin/main` stehen auf
> `bc36dd6`. Was unten „Zweig 11.09." heisst, liegt damit auf `main` — ob
> Railway es ausgeliefert hat, ist hier nicht geprüft. Der Ordner steht jetzt
> auf **`sofort/2026-09-11-si09`**, ein Commit vor `main` (`28d1ca3` SI09);
> was mit „Zweig SI09" markiert ist, steckt nur dort.
>
> **Dritter Nachtrag 11.09.2026 (Paket 171):** `sofort/2026-09-11-si09` ist mit
> `4ec540b`, `sofort/2026-09-11-is18` mit `1a5f36b` in `main` gemergt; `main` und
> `origin/main` stehen auf `5722d70` (lokale Referenz). Was unten „Zweig SI09"
> heisst, liegt damit auf `main` — ob Railway es ausgeliefert hat, ist nicht
> geprüft. Der Ordner steht jetzt auf **`sofort/2026-09-11-kv07-und-2-weitere`**,
> zwei Commits vor `main` (`2d78a55` KV07, `7919341` VL01 — nur Doku); was mit
> „Zweig KV07" markiert ist, steckt nur dort.

## Stack

| Baustein | Was | Quelle |
|---|---|---|
| Framework | Django `>=5.0,<6.1` auf main; **Zweig 11.09.: `Django==5.2.17`**, jede Abhängigkeit mit `==`, Unterabhängigkeiten in `requirements.lock` (per `--constraint` aus `requirements.txt` eingebunden). **Zweig 17.09. (`SI40`, `2cfa8ee`):** `pillow==12.3.0` statt `11.3.0` (laut `LOGBUCH.md` hatte 11.3.0 acht bekannte Lücken; Pillow nur über Djangos `ImageField` genutzt) — auf dem Entwicklungsrechner ist weiter 11.3.0 installiert. Eine App `shop1`, Projektkonfiguration `mainweb/` | `requirements.txt`, `requirements.lock`, `CLAUDE.md` |
| Python | Container `python:3.11-slim`, CI Python 3.12, Entwicklungsrechner Python 3.14. Unter der Spanne auf main bekam der Container Django 5.2.x, der CI-Lauf 6.0.x. **Zweig 11.09.:** mit dem Nagel bauen Container und CI dieselbe Fassung 5.2.17 (laut PyPI Python 3.10–3.14). Der Entwicklungsrechner hatte am 11.09.2026 noch Django 6.0.5 — die Suite lief beim Bau damit, nicht mit 5.2.17; erster Nachweis ist der nächste CI-Lauf | `Dockerfile`, `requirements.txt`, `.github/workflows/pruefungen.yml`, `LOGBUCH.md` Paket 155 |
| Datenbank | PostgreSQL über `DATABASE_URL` (Railway), lokal SQLite; **zweite Datenbank `pystore`** über `PYSTORE_DATABASE_URL` | `mainweb/settings.py` |
| Server | Gunicorn; Zweig: `gthread`, 2 Worker × 4 Threads, Timeout 30 s, Worker-Erneuerung nach 1.000 Anfragen (main: Standardaufruf) | `start.sh` |
| Statische Dateien | WhiteNoise + `ManifestStaticFilesStorage` (Content-Hash im Dateinamen). **Falle:** `ManifestStaticFilesStorage` legt keine `.gz` an, und WhiteNoise packt nicht selbst — es liefert nur eine vorhandene `datei.gz` aus. Bis Paket 267 gingen deshalb alle statischen Dateien ungepackt raus, auch `tailwind.css` und `style.css`, auf die der erste Inhalt wartet. **Zweig Paket 267 (`5515bf3`, `PF26`):** `start.sh` packt nach `collectstatic` mit `python -m whitenoise.compress --quiet staticfiles` (in `whitenoise==6.12.0` enthalten, keine neue Abhängigkeit; ohne `brotli` nur gzip), nicht blockierend. Bewusst ein eigener Aufruf statt `CompressedManifestStaticFilesStorage`. `StildateienGepacktTest` in `test_ladezeit` hält Lage und Reihenfolge des Schritts in `start.sh` fest | `DOCUMENTATION.md` §5, `start.sh`, `LOGBUCH.md` Paket 267 |
| Medien | Cloudinary (`django-cloudinary-storage`, `CLOUDINARY_URL`). Vorlagen binden Cloudinary-Bilder über den Filter `cloud` (`shop1/templatetags/custom_tags.py`) ein, der `f_auto,q_auto` einsetzt. **Zweig Paket 267 (`1737e74`, `PF15`):** der Filter setzt zusätzlich die Endung jeder Cloudinary-Adresse auf `.webp` (`.jpg`, `.png`, `.gif` usw. und Adressen ohne Endung; `.webp`/`.avif` bleiben, Abfrageteil bleibt erhalten). Mit `f_auto` bestimmt die Endung nur den Rückfall für Browser ohne Formataushandlung — der ist damit WebP statt JPEG/PNG. Fremde und lokale `/media/`-Adressen bleiben unverändert. Tests: `BildformatTest` in `test_ladezeit` | `DOCUMENTATION.md` §5, `LOGBUCH.md` Paket 267 |
| Mail | Brevo — SMTP-Relay **und** HTTP-API (siehe Fallen) | `CLAUDE.md`, `shop1/utils.py` |
| Login-Schutz | django-axes: 10 Fehlversuche je Benutzername+IP, 1 h Sperre, eigenes Lockout-Template | `settings.py` (`AXES_*`) |
| Zahlung | PayPal (JS-SDK in `payment.html`, Capture in `views/checkout.py`) und Vorab-Überweisung (`BANK_IBAN`, `BANK_INHABER`) | `DOCUMENTATION.md` §3 |
| CSS | Tailwind-CLI aus `tailwind_input.css` nach `shop1/static/shop1/tailwind.css`; **kein `package.json`, kein npm-Build im Repo**; dazu `shop1/static/shop1/style.css` | `CLAUDE.md`, `tailwind.config.js` |
| JS | Alpine.js 3.14.8 + `@alpinejs/intersect` (base.html), GSAP 3.12.5 (Startseite), Three.js 0.158.0 (nur Desktop, ohne `prefers-reduced-motion`, nachgeladen) — alle von `cdn.jsdelivr.net`, **Zweig SI17: alle vier mit `integrity` (SHA-256 aus der jsDelivr-Dateiauskunft) und `crossorigin="anonymous"`; wer eine Fassung hochzieht, muss den Hash mitziehen, sonst lädt das Skript nicht mehr**. Alpine (Standardfassung) braucht `'unsafe-eval'` in der CSP. **Zweig SI09:** eigene Inline-Skripte nur mit `nonce="{{ csp_nonce }}"`, keine `on…`-Attribute mehr — deren Aufgaben übernimmt ein Skript im `<head>` von `base.html` über `data-bestaetigen`, `data-bei-fehler-ausblenden`, `data-auto-absenden`, `data-schrift-nachladen`. **Fünftes Ersatzattribut seit dem 18.09.2026 (`RE17`, `d58a96c`): `data-src`** an den beiden Google-Maps-Rahmen in `_reviews_map.html` — ausgewertet nicht im `<head>`, sondern im Skript am Körperende von `base.html` (`:513` ff.), das den Platzhalterknopf „Karte laden" erzeugt und `src` erst im Klick setzt. Ein Test in `test_einstellungen` zählt die Ersatzattribute und verlangt jedes davon im Skripttext von `base.html`. **Selbst ausliefern (`PF31`) ist am 17.09.2026 als nicht möglich beendet** — die vier Dateien liegen nicht im Projekt, unter `shop1/static/` gibt es keine `.js`-Datei ([80-AUFGABEN.md](80-AUFGABEN.md), Bewertungsblock) | `templates/base.html`, `index.html` |
| Cache | `LocMemCache` (Zweig ausdrücklich: `LOCATION luviq`, `MAX_ENTRIES 300`); Werbeliste 60 s; Zweig: `sitemap.xml`/`llms.txt` 15 min | `settings.py`, `LOGBUCH.md` Schritt 33 |
| Zeitzone / Sprache | `Europe/Berlin`, `USE_TZ=True`, `de-de` | `settings.py` |

## Hosting und Deploy

| | |
|---|---|
| Railway | Projekt **`webseiten`** → Dienst **`Luviq-Luisa`**, Umgebung **`shop`**; Railway-Adresse `luviq-luisa-shop.up.railway.app` (antwortet 200, 02.09.2026) |
| Domain | `www.luviq-alsfeld.com`; Apex `luviq-alsfeld.com` zeigt auf denselben Dienst (eigenes Let's-Encrypt-Zertifikat, 200 ohne Weiterleitung — Stand 02.09.2026) |
| Deploy | Push auf `main` löst den Docker-Bau aus; kein Knopf nötig. Letzte Auslieferung 18.08.2026 (`645842b`, SUCCESS); Erfolgsquote 100 % (1 bewertbare Auslieferung, Messung 02.09.2026) |
| Container | `Dockerfile`: `python:3.11-slim`, `libpq-dev`/`gcc`, `pip install -r requirements.txt`, `CMD /app/start.sh`, Port 8000. **Zweig 11.09.:** kopiert `requirements.txt` **und** `requirements.lock` — ohne die Lockdatei bricht pip an der `--constraint`-Zeile ab |
| Railway-Konfiguration | **Zweig Paket 282 (`45b1477`, `VL02`):** `railway.json` — `build.builder` `DOCKERFILE`, `dockerfilePath` `Dockerfile`, `deploy.startCommand` `/app/start.sh` (dasselbe wie das `CMD`), **kein `healthcheckPath`** (sonst hinge der Healthcheck an `CanonicalHostMiddleware`, siehe [80-AUFGABEN.md](80-AUFGABEN.md) „Offen" Nr. 0a). `railway.json` gewinnt auf Railway gegen das `CMD` des Images — wer den Startbefehl ändert, muss beide Stellen ändern. `runtime.txt`: `python-3.11` wie `FROM python:3.11-slim`, ohne Patchstand. `DeployDateienTest` (`test_einstellungen`) bricht, sobald eine der Angaben vom `Dockerfile` abweicht |
| Push von diesem Rechner | `git -c credential.helper='!gh auth git-credential' push origin <zweig>` (Credential Manager ist auf diesem PC kaputt) |

**Startreihenfolge im Container (`start.sh`, Zweig):**

1. `migrate --noinput`
2. Superuser aus `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` anlegen oder abgleichen (`is_staff`, `is_superuser`, Passwort wird **bei jedem Start** neu gesetzt)
3. `loaddata initial_data.json` (optional, Fehler ignoriert)
4. `fix_pystore_schema` (eigener Befehl, behebt die `seite`-Spalte in `pystore`)
5. `collectstatic --noinput --clear`
5a. **Zweig Paket 267 (`5515bf3`):** `python -m whitenoise.compress --quiet staticfiles` — legt die `.gz`-Fassungen an, die WhiteNoise ausliefert; **nicht blockierend** (`|| echo "WARNING…"`, ohne `.gz` liefert WhiteNoise wie bisher ungepackt). Muss nach Schritt 5 stehen, sonst löscht `--clear` die Dateien wieder — das prüft `test_start_packt_die_statischen_dateien_nach_dem_sammeln`
6. **Zweig:** `pruefe_seite` — Einstellungen, Datenbanken, aktive Produkte, jede Sitemap-Adresse per Testclient; **nicht blockierend**, nur Log (`--streng` würde Warnungen zu Fehlern machen)
7. `gunicorn mainweb.wsgi:application --worker-class gthread --workers ${GUNICORN_WORKERS:-2} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-30} --max-requests 1000 --max-requests-jitter 100`, kein `--preload` (teilte Datenbankverbindungen über den Fork)

Auf main fehlen Schritt 6 und die Gunicorn-Parameter; `DOCUMENTATION.md` §5 nennt nur drei Schritte und ist veraltet.

**In Railway zu setzen:** `CANONICAL_HOST=www.luviq-alsfeld.com` (sonst bleibt die 301 für den Apex wirkungslos — der Zweig vom 11.09. ändert daran nichts, die Vorgabe ist dort weiter leer). Optional: `CSP_MODUS` (Vorgabe `scharf`, seit `0c18ea7` auf main; `report-only` ist der Rückweg, falls die Bezahlseite oder — mit dem Zweig SI09 — ein Ersatzskript im Browser etwas blockiert), `VISITOR_TRACKING` (Vorgabe an), `GUNICORN_*`.

## Umgebungsvariablen

Nur Namen. Werte stehen in Railway bzw. in der lokalen `.env` (nicht in Git).
**Ohne `.env` mit gesetztem `SECRET_KEY` läuft lokal kein `manage.py`-Befehl** — `settings.py` wirft bei `DEBUG=False` und Standard-Schlüssel einen `RuntimeError`.

| Gruppe | Variablen |
|---|---|
| Kern | `SECRET_KEY`, `DEBUG` (ohne Variable `False`), `ALLOWED_HOSTS_EXTRA` (Komma-Liste; `https://`-Präfix wird toleriert), `SITE_URL`, `SITE_NAME`, `PORT` |
| Datenbanken | `DATABASE_URL`, `PYSTORE_DATABASE_URL` (fehlt sie, ist `pystore` eine Kopie von `default` und wird migriert) |
| Admin | `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`, `ADMIN_URL` (Pfad des regulären Django-Admins) |
| Mail | `USE_SMTP_EMAIL`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, `BREVO_API_KEY` |
| Zahlung | `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`, `PAYPAL_MODE`, `PAYPAL_EMAIL`, `BANK_IBAN`, `BANK_INHABER` |
| Medien / Werbung | `CLOUDINARY_URL`, `WERBUNG_CLOUDINARY_URL`, `PYSTORE_CLOUDINARY_CLOUD_NAME`, `PYSTORE_MEDIA_URL` |
| Sonstiges | `GOOGLE_REVIEW_URL` (Bewertungslink im Kontextprozessor) |
| **Verkauf (Zweig `recht/2026-09-18-marke-im-aufbau`)** | `VERKAUF_AKTIV` — **Vorgabe aus** (`1/true/yes/on/ja/an` schaltet ein). Aus = Marke im Aufbau: keine Preise, kein Warenkorb, keine Kasse, kein PayPal, keine Sätze zu § 19 UStG/Zahlung/Versand, `Organization` statt `Offer`/`LocalBusiness`, AGB und Kaufweg-Wissensbeiträge `noindex` und aus Sitemap/llms.txt. Siehe Falle 22. `BETREIBER_KONTEN` (Komma-Liste, Vorgabe `luisabre`): Gästebuch-Beiträge dieser Konten erscheinen nicht auf der Startseite |
| **Nur Zweig** | `CANONICAL_HOST`, `CSP_MODUS` (`scharf` · `report-only` · `aus`; Vorgabe im Zweig 11.09. `scharf`), `VISITOR_TRACKING`, `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT` |
| **Altlast in Railway** | `STRIPE_*` — aus einer frühen Planungsphase; kein Code im Projekt liest sie (Suche 02.09.2026 ohne Treffer). Entfernen, sobald jemand im Railway-Dienst nachgesehen hat, welche Namen dort genau stehen — sie sind nirgends dokumentiert. |

## Formular und Missbrauchsschutz

*Pflichtabschnitt nach [DOKU-STANDARD §3a](file:///C:/Users/basti/Desktop/pystore-overview/docs/DOKU-STANDARD.md).
Erhoben am 04.09.2026 aus dem Quelltext dieses Projekts, am 17.09.2026 am Code
von `main` (`d90067a`) und dem Zweig von Paket 216 nachgezogen, am selben Tag am Zweig von
Paket 219 (`MW18`) — „ja" heisst gefunden,
nicht bewiesen. Anlass war eine Spam-Einsendung, die auf der Hauptseite mit
Spam-Score 0 durchkam und eine Mail auslöste.*

| Baustein | Was er verhindert | Stand |
|---|---|---|
| CSRF-Token | fremde Seiten schicken in fremdem Namen ab | ja |
| Honeypot | einfache Formular-Bots | **ja, seit `d90067a`** (Feld `webseite`, `shop1/spamschutz.py`, nur Kontaktformular). Seit `06503a7` (`KV06`, im Zweig) trägt das Feld seine Kennzeichen **selbst** statt nur am umgebenden Kasten: `aria-hidden="true"`, eigene Verschiebung aus dem Bild (`left:-10000px`), `tabindex="-1"`, `autocomplete="off"` — fällt der Kasten weg oder macht ein späterer Stil ihn sichtbar, füllt sonst ein Mensch das Feld aus, und seine Anfrage verschwindet still (eine Eingabe sind 10 Punkte bei `SCHWELLE` = 5). `test_das_fallenfeld_ist_an_sich_selbst_versteckt` hält alle vier Kennzeichen am Feld fest und verbietet „honey" im Markup |
| Zeitfalle (signierter Zeitstempel) | der POST ohne gerendertes Formular | **ja, seit `d90067a`** (`signing.dumps`, Feld `formzeit`, mindestens 3 s, höchstens 24 h) |
| Inhalts-Score mit Schwelle | Werbetexte, fremde Schriften, Linklisten | **ja, seit `d90067a`** (Punkte ab `SCHWELLE` = 5 → still auf die Danke-Seite, keine Mail) |
| Adresse ohne `http://` erkannt | die Masche vom 04.09.2026 | **teilweise** — `www.`, `telegra.ph`, `t.me/`, `bit.ly`; eine beliebige nackte Domain nicht |
| Fremde Domain mit eigenem Markennamen | Vertrauen erschleichen | **nein** |
| Rate-Limit je IP | Serien aus einer Quelle | **ja, seit `d978a89`** (`FO09`) — das „ja" der Erhebung vom 04.09. traf auf Kontakt und Newsletter nicht zu, `django-axes` schützt nur die Anmeldung |
| Duplikatsperre | Doppelklick, wiederholtes Absenden | **ja, seit `8717afe`** (`FO03`) — nur wortgleiche Kontaktanfragen, zwei Minuten, je Prozess |
| Erst speichern, dann mailen | verlorene Anfrage bei Mailausfall | **erst im Zweig 17.09. (Paket 219, `MW18`)** — Modell `KontaktAnfrage`, nur Kontaktformular. Das „ja" der früheren Fassung dieser Tabelle traf nicht zu: `kontakt` verschickte die Anfrage nur per Mail |
| **Keine Mail an eingetippte Adressen** | die eigene Seite als Versandhilfe für Betrugstexte an Fremde | ja, seit 17.09.2026 — Newsletter mit Double-Opt-in (`Subscriber.bestaetigt`, Link ohne Formulartext, höchstens einer je Adresse am Tag), Registrierungsmail ohne eingetippten Namen, Registrierung und erneuter Versand je IP gedrosselt |
| Mail-Obergrenze je Tag | ein volles Postfach | **nein** |
| Prüfbefehl für die Abwehr | dass niemand es nachrechnet | **nein** |

**Was diese Tabelle nicht leistet:** Ein ferngesteuerter echter Browser mit
einem unauffälligen deutschen Satz besteht Honeypot, Zeitfalle und
Inhaltsprüfung. Dagegen tragen nur Rate-Limit, Duplikatsperre und
Mail-Obergrenze — und die verhindern nicht die Anfrage, sondern das volle
Postfach.

**Nach dem Absenden (`KV07`, `2d78a55`, seit dem Merge `c522ff9` auf `main`):** `views/shop.py::kontakt` leitet
nach dem Start des Versands mit 302 auf `/kontakt/danke/` (View `kontakt_danke`,
in `views/__init__.py` re-exportiert, `never_cache`; Vorlage
`kontakt_danke.html` mit `noindex, follow`, nicht in Sitemap und `llms.txt`).
Ein Neuladen schickt die Anfrage damit nicht mehr ein zweites Mal ab. Leere
Felder und ein Fehler beim **Start** des Versands bleiben als Meldung auf
`/kontakt/` — **seit Paket 238 (`8014429`, `BF24`) nicht mehr über `messages`
im Meldungsbereich von `base.html`, sondern als Kontextwert `fehler` in der
Vorlage** (siehe unten). Ein späterer Zustellfehler im Thread von `send_brevo_email`
erreicht die Besucherin weiter nicht — die Danke-Seite erscheint trotzdem
(`EIG10` in [80-AUFGABEN.md](80-AUFGABEN.md)). An den Bausteinen der Tabelle
ändert das nichts.

**Serverseitige Prüfung und Drosselung (Paket 208, 16.09.2026, Zweig
`sofort/2026-09-16-fo06-und-2-weitere`, seit dem Merge `d978a89` auf `main`):**

- **Prüfung (`FO06`, `278e715`).** `views/shop.py::kontakt_fehler` prüft alle
  vier Kontaktfelder auf leer, auf Obergrenzen (`KONTAKT_LAENGEN`: Name 100,
  E-Mail 254, Betreff 150, Nachricht 5000) und die Adresse mit
  `validate_email`; der Grund steht als Meldung auf `/kontakt/`.
  `views/legal.py::newsletter_subscribe` prüft die Adresse mit
  `validate_email` und auf höchstens 254 Zeichen (Länge des `EmailField`;
  `validate_email` allein lässt 320 zu). Keine Django-Form — sie hätte die
  Meldungen und das JSON des Newsletter-Skripts umgebaut. Die Eingaben gehen
  bei einer Fehlermeldung weiter verloren (`EIG90`).
- **Drosselung (`FO09`, `6aa3087`).** `views/_helpers.py::zu_viele_anfragen(request, bereich)`:
  höchstens `ANFRAGE_GRENZE` = 5 POST-Anfragen je Adresse und Bereich in
  `ANFRAGE_FENSTER` = 15 Minuten, gezählt vor der Prüfung (auch ungültige).
  `cache.add` startet das Fenster, `cache.incr` zählt — das Fenster
  verlängert sich nicht. Darüber: `/kontakt/` mit Meldung und **429**, der
  Newsletter ein JSON-Fehler mit **429**, den das bestehende Skript rot zeigt.
- **Welche Adresse.** `_client_ip` nimmt den **letzten** Eintrag aus
  `X-Forwarded-For` (sonst `REMOTE_ADDR`), weil laut `DOCUMENTATION.md` §1
  nur der Railway-Proxy vor Gunicorn steht und den ersten Eintrag der
  Absender selbst setzen kann. `PageVisitMiddleware._get_ip` nimmt weiter den
  **ersten** — zwei Stellen, zwei Regeln.
- **Grenze.** Der Zähler liegt im `LocMemCache` und damit je
  Gunicorn-Prozess: bei zwei Workern (`start.sh`) im ungünstigsten Fall zehn
  Anfragen je Viertelstunde. Ein gemeinsamer Zähler bräuchte Redis oder den
  Datenbank-Cache. Neustart eines Workers setzt seinen Zähler zurück.
- **Zählbarer Abschluss (`FO08`, `9b3fc07`).** Eine *neue* Anmeldung
  antwortet mit `neu: true`; das Skript in `index.html` schiebt dann
  `{event: 'generate_lead', lead_quelle: 'newsletter'}` in `window.dataLayer`.
  Ohne eingebundenes Messskript bleibt das Ereignis im Browser — siehe
  [60-ADS.md](60-ADS.md).

**Erst speichern, dann mailen (Paket 219, 17.09.2026, Zweig
`sofort/2026-09-17-bf29-und-2-weitere`, nicht gemergt):**

- **Modell (`MW18`, `0eb7589`).** `KontaktAnfrage` in `shop1/models.py`:
  `name`, `email`, `betreff`, `nachricht`, `mail_gestartet`, `erstellt_am`;
  Migration `0019_kontaktanfrage`, Datenbank `default`. Im Django-Admin
  (`shop1/admin.py`) mit Liste, Suche und Filter, alle Felder
  schreibgeschützt, kein „Hinzufügen" — lesen und löschen. Das Panel unter
  `/shop-admin/` zeigt die Anfragen nicht.
- **Ablauf in `views/shop.py::kontakt`.** Drosselung → Prüfung → Spamschutz →
  Duplikatsperre → **Speichern** (eigenes `transaction.atomic()`, fängt
  `DatabaseError`) → Versand → `mail_gestartet=True` per `update()`.
  Weiterleitung auf `/kontakt/danke/`, sobald die Anfrage gespeichert **oder**
  der Versand gestartet ist; nur wenn beides scheitert, bleibt die
  Fehlermeldung und der Doppel-Merker wird gelöscht. Jeder Fehlschlag steht
  mit `_log.exception` im Log. Abgewiesene Eingaben, Spam und Doppelklicks
  werden nicht gespeichert.
- **Grenze.** `mail_gestartet` heisst „Versand angestoßen", nicht
  „zugestellt" — `send_brevo_email` läuft weiter im Thread (`EIG10`). Eine
  Anfrage mit `mail_gestartet` = nein ist im Admin filterbar und muss von
  Hand beantwortet werden. Personenbezogene Daten liegen jetzt im Shop;
  Datenschutzerklärung und Löschfrist sind nicht nachgezogen
  ([80-AUFGABEN.md](80-AUFGABEN.md), „Beim Kunden" Nr. 17).
- **Tests.** Wer das Speichern in einem Test ausfallen lässt, patcht
  `KontaktAnfrage.objects.create` mit `DatabaseError` (`test_formulare`).

**Doppeltes Absenden, Pflichtfelder, Längen (Paket 216, 17.09.2026, Zweig
`sofort/2026-09-17-fo03-und-2-weitere`, seit dem Merge `8717afe` auf `main`):**

- **Absendesperre im Browser (`FO03`, `3e0a59f`).** Neues Merkmal
  `<form data-einmal-absenden>`, ausgewertet im `<head>`-Skript von
  `templates/base.html` neben `data-bestaetigen`: beim ersten `submit`
  bekommen die Absendeknöpfe `disabled` plus `data-gesperrt`, das Formular
  `aria-busy="true"`. Der Zuhörer liegt in der **Blasenphase** und übergeht
  `defaultPrevented` — die `data-bestaetigen`-Rückfrage hört in der
  Fangphase, eine abgelehnte Rückfrage sperrt also nichts. Ein
  `pageshow`-Zuhörer gibt die Knöpfe wieder frei, wenn die Seite per
  Zurück-Taste aus dem Verlaufsspeicher kommt. Gesetzt ist das Merkmal heute
  nur am Kontaktformular. Die Newsletter-Anmeldung in `index.html` sendet
  per `fetch` und sperrt ihren Knopf deshalb im eigenen Skript, bis die
  Antwort da ist (`finally`). Kein Handler-Attribut, keine neue Nonce nötig.
- **Duplikatsperre auf dem Server (`FO03`).** `views/shop.py::doppelt_abgeschickt(email, betreff, nachricht)`
  legt per `cache.add` einen Schlüssel `kontakt-doppelt:<SHA-256>` aus
  Adresse (klein geschrieben), Betreff und Text für `DOPPELT_FENSTER` =
  2 Minuten an. Schlägt `add` fehl, war dieselbe Anfrage gerade da: Weiterleitung
  auf `/kontakt/danke/`, keine Mail, ein `INFO`-Eintrag im Log. Reihenfolge
  in `kontakt`: Drosselung → Prüfung → Spamschutz → Duplikatsperre →
  Versand. Scheitert der Versandstart, löscht der `except`-Zweig den
  Schlüssel wieder. **Grenze:** `LocMemCache`, also je Gunicorn-Prozess —
  zwei gleiche Anfragen auf zwei Workern gehen beide hinaus. Wer Tests für
  das Kontaktformular schreibt, braucht je Anfrage einen anderen Text, sonst
  greift die Zusammenführung (`DrosselungTest._kontakt`).
- **Pflichtfelder (`FO04`, `370fce7`).** Beschriftung mit „ *",
  `aria-label` mit „(Pflichtfeld)" am Ende, ein erklärender Satz im
  Einleitungsabsatz von `kontakt.html`. Die `<label>` haben weiter kein
  `for` — eine neue `id` änderte den Fingerabdruck der Designwache.
- **Längen (`FO07`, `641153b`).** `maxlength` an den vier Kontaktfeldern =
  `KONTAKT_LAENGEN` (ein Kommentar in `kontakt.html` und ein Test halten
  beides gleich). `kontakt_fehler` zählt `\r\n` als ein Zeichen, weil der
  Browser einen Umbruch für `maxlength` einfach zählt, aber als `\r\n`
  schickt.

**Die Fehlermeldung steht im Formular (Paket 238, 17.09.2026, `BF24`,
`8014429`, Zweig `sofort/2026-09-17-bf24-und-2-weitere`, nicht gemergt):**

- **Weg der Meldung.** `views/shop.py::kontakt` gibt den Fehlertext auf allen
  drei Wegen als Kontextwert `fehler` zurück — Drosselung (Status 429),
  `kontakt_fehler` und ein gescheiterter Versandstart. `from django.contrib
  import messages` ist aus dem Modul entfernt; der Meldungsbereich in
  `templates/base.html` bleibt für die übrigen Views, sieht aber vom
  Kontaktformular nichts mehr.
- **Im Template.** `kontakt.html` rendert
  `<div id="kontakt-fehler" role="alert">` als erstes Kind des `<form>`; die
  vier Pflichtfelder tragen `aria-describedby="kontakt-fehler"`. Das Formular
  behält `aria-live="polite"` und `data-einmal-absenden`.
- **Warum bedingt (`{% if fehler %}`).** Ein dauerhaft vorhandener, leerer
  Meldungsbereich wäre ein Element mehr im sichtbaren Aufbau der Seite, und
  den friert die Designwache ein (Falle 9). Deshalb steht der Verweis der
  Felder auch dann, wenn es das Ziel nicht gibt — ein Vorleseprogramm
  überliest ein fehlendes `aria-describedby`-Ziel. `aufbau_referenz.json` ist
  nicht angefasst.
- **Tests.** `test_barrierefreiheit::FehleransageTest` (13 → 15 Funktionen im
  Modul): Wortlaut samt `id` und `role="alert"`, die Meldung liegt zwischen
  `<form>` und `</form>`, und jedes Pflichtfeld verweist darauf (`subTest` je
  Feld). **Nicht belegt:** was ein Bildschirmleser tatsächlich ansagt.

**Feed der Wissensbeiträge (Paket 238, `GE32`, `22fea97`, derselbe Zweig):**
`/feed/` liefert die **freigegebenen** Beiträge als RSS — Klasse `WissenFeed`
(`django.contrib.syndication.views.Feed`) in `views/wissen.py`, Route in
`urls.py`, in `views/__init__.py` re-exportiert (Falle 3). Jede Angabe kommt
aus dem Register `WISSEN_BEITRAEGE` (`titel`, `kurz`, `url_name`,
`veroeffentlicht`), nicht aus einer Datei- oder Bauzeit; `pubDate` wird mit
`timezone.make_aware` in Berliner Zeit gesetzt, weil `USE_TZ=True` sonst warnt
und der Zeitstempel ohne Zone bei jedem Leser anders landet. Der Feed führt
genau die Menge aus Sitemap und `llms.txt` — ein Beitrag mit `noindex` steht in
keiner der drei Aufstellungen. Verlinkt ist er im `<head>` von
`templates/base.html` und als Zeile `Feed: …` in `llms.txt`
(`views/legal.py`); diese Zeile ist wie `Sitemap: …` **kein** Markdown-Link
und wird von `pruefe_links` daher nicht abgerufen (`_MD_LINK`). Kein
`cache_page`.

## Prüfbefehle und Tests

| Befehl | Was | Stand |
|---|---|---|
| `python manage.py test shop1` | Testsuite in 14 Modulen, Laufzeit rund 2,5 Minuten; main: **218 Tests** (seit `4ec540b` mit den drei SI09-Tests in `test_einstellungen`), Zweig KV07: **224 Tests** (sechs neue in `test_formulare`), main seit `43f25c3` (PJ01): **230 Tests** (sechs neue in `test_einstellungen` zu `pruefe_links`), Zweig 12.09. MW15/GE15: **243 Testfunktionen** (acht neue in `test_einstellungen` zu `pruefe_mail`, fünf in `test_geo` zum `Article`-Knoten; `def test_` über `shop1/tests/` gezählt am 12.09.2026), Zweig 16.09. FO06/FO08/FO09: **252 Testfunktionen** (neun neue in `test_formulare`, das damit 25 zählt; gezählt am 16.09.2026), FO03/FO04/FO07 (seit `8717afe` auf `main`): **264 Testfunktionen** (`test_formulare` 37, davon 8 aus Paket 216; gezählt am 17.09.2026), Zweig 17.09. SI40/MW18: **270 Testfunktionen** (`test_formulare` 43, sechs neue zu `KontaktAnfrage`; gezählt am 17.09.2026), Paket 227 (seit `f489e76` auf `main`): **278**, Zweig 17.09. BF24/GE32 (Paket 238): **285 Testfunktionen** (`test_barrierefreiheit` 15, zwei neue zur Lage der Fehlermeldung und zu `aria-describedby`; `test_seo` 36, fünf neue in `FeedTest`; gezählt am 17.09.2026) | Zweig MW15/GE15 laut Commit grün; Zweig 16.09. laut `LOGBUCH.md` grün; Paket 216 laut `LOGBUCH.md` (Nachbesserung) grün; Paket 219 laut Bausitzung grün, mit Pillow 11.3.0; Paket 238 laut Bausitzung grün — kein Commit nennt einen Testlauf |
| `python manage.py test shop1.tests.<modul>` | einzelnes Modul | Zweig |
| `python manage.py pruefe_seite [--streng]` | Prüfbefehl: Einstellungen, beide Datenbanken, aktive Produkte (Pflichtwerte, doppelte Slugs), jede Sitemap-Adresse 200 mit Titel, Beschreibung 110–175, canonical, robots, JSON-LD, Schutzkopfzeilen samt CSP; hinterlässt keine Spuren (`VISITOR_TRACKING` aus, zurückgerollte Transaktion) | Zweig |
| `python manage.py pruefe_links [--streng]` | Prüfbefehl (Zweig 12.09., PJ01): liest `/`, jede Sitemap- und jede llms.txt-Adresse und ruft **jeden `<a href>` darin** ab — tote eigene Adressen sind Fehler, Weiterleitungen Warnungen (ausser auf `LOGIN_URL`), fremde Ziele werden nur auf `https` geprüft, nicht abgerufen; verändernde Pfade (Warenkorb, Abmeldung, Werbeklick, Kommentar) stehen in `KEINE_PRUEFUNG`. Gleiche Vorsorge wie oben: kein Besuchsprotokoll, zurückgerollte Transaktion | seit `43f25c3` auf `main` |
| `python manage.py pruefe_mail [--ohne-verbindung] [--streng] [--an ADRESSE]` | Prüfbefehl (Zweig 12.09., MW15): **beide** Mailwege. Zeigt die Einstellungen (Backend, `DEFAULT_FROM_EMAIL`, `ADMIN_EMAIL`, `SITE_URL`, Host/Port/Verschlüsselung, Benutzer — von Schlüsseln und Passwörtern nur „gesetzt (n Zeichen)", die Ausgabe darf in ein Container-Log) und versucht die **Anmeldung**: Brevo-API-Schlüssel gegen die Kontoauskunft `/v3/account` (Lesezugriff, verschickt nichts), SMTP über `get_connection().open()`. Console-Backend ist im Entwicklungsmodus eine Warnung und im Betrieb ein Fehler; leerer `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` ein Fehler; fehlender `BREVO_API_KEY` und der Vorgabeabsender `noreply@luviq-shop.de` je eine Warnung. `--an ADRESSE` schickt eine Testmail **synchron und ohne `fail_silently`**, `--ohne-verbindung` lässt jeden Netzzugriff aus. Gegen die echten Zugangsdaten dieses Dienstes noch nie gelaufen | Zweig |
| `python manage.py check --deploy` | Django-Prüfung | beide |
| `python manage.py fix_pystore_schema` | `seite`-Spalte in `pystore` | beide |
| `python manage.py makemigrations shop1` | einzige App; 18 Migrationen auf `main` (`0018` legt die pystore-Tabellen auch ohne PostgreSQL an), im Zweig 17.09. 19 (`0019_kontaktanfrage`, `MW18`) | |

**Testmodule (Zweig 12.09., `def test_` je Datei, gezählt am 12.09.2026):** `test_seiten` (14), `test_seo` (31), `test_geo` (25, davon 5 zum `Article`/`ItemList`-Schema des Wissensbereichs), `test_inhalt` (15), `test_formulare` (16), `test_daten` (22), `test_einstellungen` (59, davon 6 zu `pruefe_links` und 8 zu `pruefe_mail`), `test_barrierefreiheit` (11), `test_ladezeit` (9), `test_aufbau` (2, Designwache), `test_warenkorb` (8), `test_zahlung` (11), `test_konto` (10), `test_zugriffsschutz` (10) — zusammen **243**; dazu `_basis.py` (Basisklasse `LuviqTestCase`) und `_aufbau.py` (Fingerabdruck) mit `aufbau_referenz.json` (5.148 Zeilen).

**Drei Regeln für neue Tests** (`CLAUDE.md`): `secure=True` ist Pflicht (sonst prüft man nur die 301 der SSL-Weiterleitung) → `self.hole()` / `self.sende()`; `databases = {'default', 'pystore'}` (die Besuchs-Middleware schreibt bei jeder Antwort); der Cache wird vor jedem Test geleert (`sitemap.xml`/`llms.txt` liegen 15 min im LocMemCache).

**Was fehlt (Messung 02.09.2026, VL19, PJ01, MW15):** Fehler-Monitoring (Sentry o. ä.). Der zweite Prüfbefehl liegt seit dem Merge `43f25c3` auf `main` (`pruefe_links`, `11acccc`), der dritte seit dem 12.09.2026 im Zweig (`pruefe_mail`, `4fd7776`); **beide sind bewusst nicht an `start.sh` angeschlossen** — sie fassen fremde Server an und gehören vor den Commit, nicht in den Containerstart. Ein CI-Lauf bei jedem Push steht in `.github/workflows/pruefungen.yml`. Kein Test kann ein vergessenes Nachziehen des Registers `seiten_stand.py` erzwingen.

## Aufbau des Projekts

```
WebseiteMAIN/
├── mainweb/            settings.py, urls.py, wsgi/asgi
├── shop1/              einzige App
│   ├── views/          Package: shop.py, auth.py, cart.py, checkout.py, legal.py, gaestebuch.py, wissen.py (Zweig), _helpers.py
│   ├── admin_views.py  eigenes Admin-Panel /shop-admin/… (24 Routen), Decorator admin_required dort selbst definiert
│   ├── models.py       UserProfile, Subscriber, Produkt, Cart, CartItem, Order, OrderItem, Werbung, WerbungStat, VisitorLog, PageVisit, KontaktAnfrage (Zweig 17.09.), Comment, PyStoreVisitorLog
│   ├── middleware.py   CanonicalHost (Zweig), ContentSecurityPolicy (Zweig), PageVisit
│   ├── routers.py      WerbungRouter → pystore
│   ├── seiten_stand.py Register lastmod/dateModified (Zweig)
│   ├── context_processors.py (Zweig SI09: csp_nonce), signals.py, forms.py, utils.py (send_brevo_email)
│   ├── management/commands/  fix_pystore_schema.py, pruefe_seite.py, pruefe_links.py, pruefe_mail.py (Zweig 12.09.)
│   ├── tests/          14 Module (Zweig)
│   ├── templates/shop1/  Seiten, legal/, wissen/ (Zweig), admin/, teile/ (Zweig 12.09.: angebot.html, angebot_galerie.html, wissen_article_ld.html)
│   └── static/shop1/   style.css, tailwind.css, images/ (Zweig: WebP in mehreren Breiten, flavicon.ico)
├── templates/base.html Navigation, Fusszeile, JSON-LD-Graph, Schriften, Alpine
├── start.sh · Dockerfile · requirements.txt · requirements.lock (Zweig 11.09.) · tailwind.config.js · tailwind_input.css
├── .github/workflows/pruefungen.yml   CI bei jedem Push und Pull Request (Python 3.12, collectstatic, manage.py test)
├── CLAUDE.md · DOCUMENTATION.md · GOOGLE_SEO_GUIDE.md · LOGBUCH.md · paypal_sandbox_tutorial.md
└── projekt1/ · tiktok stream/   unversionierte Altablagen, NICHT Teil der App (in .gitignore)
```

Code-Audit (Messung 02.09.2026, lokaler Ordner = Zweig): 114 Dateien, 23.859 Zeilen (53 Python, 45 Templates, 6 Konfig, 5 Doku, 3 CSS, 1 JS, 1 Skript); 115 Befunde (2 kritisch, 36 wichtig, 77 Hinweise), 71 Dateien ohne Befund, Note 0,952; 10 Module ohne Test; 4 „verwaiste" Templates (`lockout.html` ist über `AXES_LOCKOUT_TEMPLATE` in Gebrauch, die drei `wissen/*.html` über das Register — Fehlalarme des Audits). Die dichtesten Befunde liegen in `tiktok stream/` (Altablage, 13 + 11) und `shop1/admin_views.py` (8).

**Aufräumlauf für das Audit (Zweig 18.09., `eb4ab9b`, `PJ07`):** elf Dateien ohne Verhaltensänderung nachgezogen — Modulbeschreibungen (`admin.py`, `context_processors.py`, `routers.py`, `urls.py`, `models.py`, `middleware.py`, `templatetags/custom_tags.py`, `fix_pystore_schema.py`), unbenutzte Einfuhren (`static` in `mainweb/urls.py`, `os` in `custom_tags.py`), umbrochene Zeilen (`views/__init__.py`, `models.py`), ein `print` aus `test_zugriffsschutz.py`, ein zusätzliches `_log.exception` im Schema-Fix und `_track` in `PageVisitMiddleware` gekürzt. `admin_views.py` und `views/checkout.py` blieben bewusst unberührt (Verwaltung und Kasse, nur mit Sandbox-Test). Wie viele Dateien das Audit danach ohne Befund zählt, steht im Messblock von [00-STATUS.md](00-STATUS.md).

## Fallen

1. **Einziger echter Shop — Änderungen an Warenkorb, Checkout, Zahlung nur mit Sandbox-Test.** Anleitung [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md): Sandbox-Business- und -Personal-Konto, Sandbox-Client-ID in `PAYPAL_CLIENT_ID`, Testkauf, Bestellung springt auf „bezahlt", Artikel wird deaktiviert (1-of-1). Vor Live-Schaltung Live-App und Live-Client-ID. Die Tests `test_warenkorb`, `test_zahlung`, `test_konto` (Zweig) prüfen die Pfade ohne PayPal-Aufruf.
2. **Zwei Datenbanken.** `default` = Shop-Daten, `pystore` = seitenübergreifende Werbe-/Besucherdaten (`Werbung`, `WerbungStat`, `VisitorLog`). `shop1/routers.py::WerbungRouter` zwingt sie nach `pystore` und **blockt ihre Migrationen dort** (`PYSTORE_IS_EXTERNAL`), weil das PyStore-Projekt diese Tabellen verwaltet. Ohne `PYSTORE_DATABASE_URL` ist `pystore` eine **Kopie** von `default` — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der Test-Runner die Testdatenbanken. `PyStoreVisitorLog` ist ein `managed=False`-Proxy auf `shop1_visitorlog` in `pystore` (`db_column='site'`). Migrationen `0013`/`0014` legen die Tabellen nur auf PostgreSQL an, `0018` auf allen anderen Backends.
3. **Views sind ein Package, aber zentral re-exportiert.** `shop1/urls.py` macht nur `from . import views` — **jede neue View muss in `shop1/views/__init__.py` re-exportiert werden**, sonst ist sie unsichtbar. Das gilt auch für klassenbasierte Views: `WissenFeed` (Zweig 17.09., `GE32`) steht in `__init__.py` und im `__all__`, und `urls.py` bindet sie als **Instanz** ein (`path('feed/', views.WissenFeed(), name='wissen_feed')`). Helfer liegen in `views/_helpers.py`.
4. **Zwei E-Mail-Wege.** (1) Django-`send_mail` über SMTP (Brevo-Relay, `USE_SMTP_EMAIL` oder `DEBUG=False`; sonst Console-Backend). (2) `shop1/utils.py::send_brevo_email()` — direkter HTTP-Aufruf an die Brevo-API in einem Thread, weil Railway SMTP-Ports blockt. **Bestell- und Benachrichtigungsmails gehen über Weg 2.** Ein Mailausfall lässt die Bestellung bestehen (Test in `test_zahlung`). **Beide Wege fallen still aus** — der API-Weg protokolliert einen Fehlschlag nur ins Log (`utils.py:41`, `:59`), während die Bestellung als aufgegeben gilt; ein geblockter SMTP-Port heisst, dass niemand sein Passwort zurücksetzen kann. Seit dem 12.09.2026 (Zweig, `MW15`) sieht sich `python manage.py pruefe_mail` genau das an: Einstellungen und Anmeldung beider Wege, auf Wunsch eine Testmail. Er hängt **nicht** an `start.sh`. **Zweig 17.09. (`MW18`):** Kontaktanfragen liegen vor dem Versand in `KontaktAnfrage` und überleben damit einen Mailausfall; für Bestell- und Newslettermails gilt das nicht. **Antwortadresse (Zweig 18.09., `290f422`, `MW21`):** `send_brevo_email(…, reply_to=…)` setzt sie auf beiden Wegen — `replyTo` in der Brevo-API, `reply_to` beim SMTP-Rückfall. Der Rückfall läuft deshalb über `EmailMultiAlternatives` mit angehängtem HTML-Teil statt über `send_mail`, das keine Antwortadresse kennt. Nur `kontakt()` übergibt eine (die Adresse aus dem Formular); ohne sie ginge „Antworten" an die eigene Versandadresse. Wer eine weitere Mail an die Betreiberin einführt, die im Namen eines Besuchers kommt, gibt `reply_to` mit. Gehalten von `AntwortadresseTest` in `test_formulare`. **Tagessperre der Newsletter-Bestätigung:** `_bestaetigung_senden()` (`views/legal.py`) schickt höchstens einen Link je Adresse am Tag und merkt sich das per `cache.add` im `LocMemCache`. Fällt der Cache aus, geht der Link **ohne** Sperre hinaus; seit `a708c7f` (Zweig 17.09., Paket 227, `PJ05`) steht das als `Newsletter: Tagessperre im Cache nicht pruefbar` mit Stacktrace im Logger `shop1`, vorher verschwand es still.
5. **Denormalisierte Bestelldaten.** `CartItem` und `OrderItem` speichern Name und Preis als eigene Felder, nicht als Fremdschlüssel — **Absicht**, damit geänderte oder gelöschte Produkte alte Bestellungen nicht verändern. Erhalten.
6. **`PageVisitMiddleware`** läuft nach jeder Antwort. Geo-IP (`ip-api.com`) im festen `ThreadPoolExecutor` (4 Plätze; voll → kein Lookup), **die Datenbankschreibvorgänge laufen synchron im Request** und verzögern die Auslieferung. Dedup: `PageVisit` einmal je Session und Tag, `VisitorLog` einmal je Pfad alle 5 Minuten. **Keine Admin-Mail pro Besuch mehr** (seit `e58775a`, Mail-Flut durch Bots). Neue externe Aufrufe gehören in den Pool, nicht in einen Thread je Anfrage. Abschalter `VISITOR_TRACKING` (Zweig).
7. **Zwei Admins.** Eigenes Panel `/shop-admin/…` (`admin_views.py`, `admin_required`: `is_superuser` **oder** Benutzername gleich `ADMIN_USERNAME`); regulärer Django-Admin hinter `ADMIN_URL` (Schutz vor Scannern). **Zweig 11.09.:** dort ist zusätzlich `Subscriber` registriert (Liste, Suche nach Adresse, Filter nach Datum, `erstellt_am` schreibgeschützt), damit eine Auskunft oder Löschung nach Art. 15/17 DSGVO ohne Datenbankzugriff geht; das Panel bleibt unverändert. **Zweig 17.09.:** ebenso `KontaktAnfrage` (nur lesen und löschen) — die Anfragen stehen also nur im Django-Admin, nicht im Panel. Bekannte, dokumentierte Lücken (Tests halten den Ist-Zustand fest): `comment_delete`, `admin_produkt_toggle`, `admin_resend_newsletter`, `admin_newsletter_reset` reagieren auf GET; eine E-Mail-Adresse kann sich zweimal registrieren — **wartet auf Freigabe der Betreiberin**.
8. **Werbe-Impressionen** werden nur in `startseite()` gezählt, nicht im Kontextprozessor (war ein Bug).
9. **Designwache** (`test_aufbau`, `aufbau_referenz.json`): jede Änderung an Tag-Reihenfolge, `id`/`class`, Überschriften oder Elementzahlen einer öffentlichen Seite macht die Suite rot. Referenz für neue Seiten **gezielt ergänzen**, nie neu erzeugen. Siehe [20-DESIGN.md](20-DESIGN.md).
10. **Template-Blöcke:** eine Bedingung **um** einen `{% block %}` in einer erbenden Datei wirkt nicht — die Bedingung gehört **in** den Block (`produkt_detail.html`, `meta_robots` der Wissensseiten).
11. **`{% load %}` wird an ein `{% include %}` nicht vererbt** (Zweig 12.09., `5f517de`). Ein Baustein unter `shop1/templates/shop1/teile/` muss seine Bibliotheken **selbst** laden: ohne `{% load custom_tags %}` kennt er den Filter `cloud` nicht, auch wenn die einbindende Vorlage ihn geladen hat — Startseite und Produktübersicht antworten dann mit 500 (`Invalid filter: 'cloud'`). `produkt` und `forloop` kommen dagegen aus dem umgebenden Kontext, solange das `{% include %}` ohne `only` steht. Steht als Kommentar in `teile/angebot.html` und `teile/angebot_galerie.html`.
12. **Zeitzone in Tests:** `.date()` eines UTC-Zeitstempels ist zwischen 22:00 und 24:00 UTC falsch → `timezone.localtime()` (Auflage 4, `270c5f9`).
13. **CSP blockiert standardmässig** (seit `0c18ea7` auf main). `CSP_MODUS` hat die Vorgabe `scharf`; die geplante Konsolenprüfung aller Seiten vor dem Umschalten ersetzt die Testsuite: `test_einstellungen` hält jedes `<script src>`, jedes Stylesheet, jedes Iframe und nachgeladene Skripte jeder öffentlichen Seite und jeder Panel-Seite gegen `CSP_QUELLEN`, dazu die PayPal-Einträge gegen PayPals Angabe für das JS-SDK (`*.paypal.com`, `*.paypalobjects.com`, `*.venmo.com` in `script-`, `style-`, `connect-`, `frame-src`). **Jede neue Fremdquelle in einem Template gehört in `CSP_QUELLEN`**, sonst blockiert der Browser sie. Ein Browser hat die Bezahlseite nicht gesehen: nach dem Deploy `/payment/<id>/` mit offener Konsole ansehen; fällt etwas aus, `CSP_MODUS=report-only` (wirkt je Antwort, ohne neuen Stand). Auf main bleiben `script-src`/`style-src` wegen Inline-Code offen (`'unsafe-inline'`, `'unsafe-eval'`); `form-action` erlaubt neben `'self'` vorsorglich `*.paypal.com`. **Zweig SI09 (`28d1ca3`):** `script-src` ohne `'unsafe-inline'` — die Middleware erzeugt je Anfrage eine Nonce (`request.csp_nonce`, Kontextprozessor `csp_nonce`) und hängt sie an. **Jedes neue Inline-`<script>` braucht `nonce="{{ csp_nonce }}"`**, sonst blockiert der Browser es; **Handler-Attribute (`onclick`, `onsubmit`, `onerror` …) deckt keine Nonce** — dafür die `data-`-Attribute aus dem `<head>`-Skript von `base.html`. `test_einstellungen` hält beides gegen jede Vorlage und jede gerenderte Seite. Eine Nonce verträgt kein Zwischenspeichern der Seite: `cache_page` nur auf Antworten ohne Skript (`sitemap.xml`, `llms.txt`). Weiter offen: `'unsafe-eval'` (Alpine.js-Standardfassung) und `'unsafe-inline'` im `style-src`. Nicht angefasst: `SECURE_CROSS_ORIGIN_OPENER_POLICY` ist nicht gesetzt, Django sendet damit `same-origin`, PayPal empfiehlt `same-origin-allow-popups` (`LOGBUCH.md`, Paket 155).
14. **`ALLOWED_HOSTS = ['*']`** bei `DEBUG=True`; im Betrieb `['localhost', '127.0.0.1', '.up.railway.app'] + ALLOWED_HOSTS_EXTRA` (+ `CANONICAL_HOST`, falls gesetzt). Der Code-Audit meldete die Zeile als kritisch (K02); im Zweig 11.09. trägt sie einen begründeten Vermerk `# audit-ok K02:`, gehalten von `test_die_hostliste_ist_nicht_offen`. `DEBUG` darf in Railway nie auf `True` stehen.
15. **`db.sqlite3`, `staticfiles/`, `media/`, `.env`, `*.log`** liegen im Ordner, sind aber in `.gitignore`. `runserver.err.log` vom 03.07.2026 ebenfalls.
16. **Der Superuser wird bei jedem Containerstart mit `ADMIN_PASSWORD` überschrieben** — ein im Panel geändertes Passwort dieses Kontos hält nur bis zum nächsten Deploy.
17. **Fassung eines Fremdskripts hochziehen (Zweig 12.09., `680a641`):** Alpine, `@alpinejs/intersect`, GSAP und das nachgeladene Three.js tragen `integrity="sha256-…"`. Wer die Fassung in der URL ändert und den Hash stehen lässt, sorgt dafür, dass der Browser das Skript **gar nicht mehr ausführt** — Alpine hängt über `base.html` in jeder Seite, und **kein lokaler Test bemerkt es**: die Suite ruft keine fremden Server ab. Beim nachgeladenen Three.js stehen `s.integrity` und `s.crossOrigin` vor `s.src`, weil erst `appendChild` den Abruf auslöst (`index.html`). Hashes und ihre Herkunft: `LOGBUCH.md`, Paket 196.
18. **Paketfassungen ändern (Zweig 11.09.):** `requirements.txt` und `requirements.lock` gehören zusammen. Wer eine Fassung ändert, schreibt die Lockdatei neu — frische Umgebung, `pip install -r requirements.txt`, Testsuite grün, dann die Fassungen aus `pip freeze` eintragen (Kopf von `requirements.lock`). Das Code-Audit des Werkzeugs liest `.lock`-Dateien nicht und meldet deshalb weiter „kein Lockfile". **Paket 219 (`SI40`)** hat `pillow` ohne diesen Ablauf gehoben — `pip install` war gesperrt, die Lockdatei ist von Hand in einer Zeile geändert (Pillow hat keine Unterabhängigkeiten); der erste echte Installationslauf ist CI oder Deploy.
19. **Vermerk `# offen-ok:` an öffentlichen, schreibenden Views** (`6b618e4`, Paket 223, seit dem Merge `f8643f0` auf `main`). Das Code-Audit meldet jede View, die ohne Anmeldung etwas speichert (`K06`). Wo die Öffnung gewollt ist, steht über der Funktion ein `# offen-ok:` mit dem Grund — seit Paket 223 auch über `kontakt()` in `views/shop.py`, weil das Formular ohne Konto erreichbar bleiben muss und die `KontaktAnfrage` (`MW18`) erst nach Drosselung, `kontakt_fehler`, Spamschutz und Doppelsperre geschrieben wird. Wer einer öffentlichen View einen Schreibzugriff gibt, prüft, ob ein solcher Vermerk nötig ist, und schreibt nur eine Begründung hinein, die der Code hergibt — der Vermerk an `register()` nennt eine Begrenzung durch django-axes, die für Registrierungen nicht gilt (`EIG71` in [80-AUFGABEN.md](80-AUFGABEN.md)).
20. **Mehrzeilige Vorlagenkommentare nur mit `{% comment %}`** (Paket 243, `b736994`). Die kurze Klammerform `{# … #}` gilt **nur für eine Zeile**; über mehrere Zeilen geschrieben landet ihr Text im ausgelieferten HTML. Stehen darin Beispiel-Tags, zählt die Designwache sie als echte Elemente — hier meldete `test_aufbau` für `/kontakt/` `tags: 171 vorher, 173 jetzt` und einen Verweis mehr, obwohl die Änderung reiner Text war. Der Fehler ist im Quelltext der Vorlage nicht zu sehen; er zeigt sich erst im gerenderten HTML.
21. **Die Karte lädt erst nach einem Klick — und steht deshalb in keiner Vorlage mehr als `src`** (Paket 248, `d58a96c`). `maps.google.com` in `CSP_QUELLEN['frame-src']` sieht seitdem aus wie ein Überbleibsel; wer die Positivliste danach „aufräumt", bricht die Karte **still** — der Rahmen bekommt sein `src` erst im Browser, und kein Deckungstest über gerenderte Vorlagen schlägt an. Dagegen steht `test_die_karte_bleibt_in_der_richtlinie_erlaubt` (`EinbettungErstNachKlickTest`). Umgekehrt gilt: **kein `<iframe>` einer öffentlichen Seite darf wieder ein fremdes `src` bekommen** — derselbe Testfall meldet genau die Seite, die es tut. Wer ein weiteres Fremd-Einbettungsziel aufnimmt, nimmt es in `data-src` und in `frame-src` auf. Ohne JavaScript entsteht weder Platzhalter noch Karte: der Rahmen bleibt leer, ein `<noscript>`-Ersatz gibt es nicht.

22. **Verkaufsschalter `VERKAUF_AKTIV`** (Zweig `recht/2026-09-18-marke-im-aufbau`, `9b12276`). Ein Modul, drei Stellen: `shop1/verkauf.py` (`verkauf_aktiv()`, Kontextprozessor `verkauf_kontext`, `VerkaufsschalterMiddleware`). Die Middleware fängt in `process_view` die Routennamen `warenkorb`, `add_to_cart`, `remove_from_cart`, `update_cart`, `checkout`, `payment`, `payment_success`, `payment_cancel` ab (302 auf `/#newsletter-form` mit Meldung) und `paypal_capture` (JSON 409) — die Views selbst wissen nichts vom Schalter. **Eine neue Kaufroute gehört in `KAUFROUTEN`**, sonst ist sie ohne Verkauf offen. Vorlagen schalten mit `{% if verkauf_aktiv %}…{% else %}…{% endif %}` **innerhalb** vorhandener Elemente um (Designwache); wo ein Element wegfällt, steht ein gleich gebautes an seiner Stelle. Wissensbeiträge mit `nur_mit_verkauf` zählen nur bei eingeschaltetem Verkauf zu `freigegebene_beitraege()`; `wissen_beitrag()` gibt den Vorlagen die **wirksame** Freigabe als `beitrag.freigegeben`. Gelesen wird der Schalter je Anfrage aus `settings` — `override_settings(VERKAUF_AKTIV=True)` wirkt in Tests; die Testlisten in `_basis.py` (`NICHT_INDEXIERBARE_SEITEN`) werden dagegen beim Import aus dem Vorgabezustand gebildet. `sitemap.xml`/`llms.txt` liegen 15 min im Cache: nach dem Umschalten in Railway kommt der neue Stand mit dem Neustart des Dienstes (Variable ändern = Neustart). Tests: `test_verkauf`.

## Offen

| Punkt | Beleg | Regel |
|---|---|---|
| Zweig `sofort/2026-09-18-mw21-und-2-weitere` nach `main` mergen und pushen (drei Commits vor `31c6041`); danach eine Kontaktanfrage abschicken, im Postfach der Betreiberin „Antworten" klicken — Empfänger muss der Anfragende sein —, und `pruefe_mail` gegen die echten Zugangsdaten fahren (SMTP-Rückfall jetzt über `EmailMultiAlternatives`) | `290f422` — `reply_to` ist nur gegen einen nachgebildeten Versand getestet (`AntwortadresseTest`), nicht gegen Brevo | MW21, PJ07 |
| ~~Zweig `sofort/2026-09-18-re15-und-2-weitere` nach `main` mergen und pushen~~ (gemergt und gepusht mit `31c6041`); danach `/` und `/gaestebuch/` mit offenem Netzwerkfenster ansehen — vor dem Klick keine Anfrage an `maps.google.com`, nach dem Klick die Karte —, dieselben Seiten einmal ohne JavaScript, und einen Sandbox-Kauf über den Knopf „Zahlungspflichtig bestellen" | `d58a96c`, `329dbc4` — `RE17` ist nur gegen gerendertes HTML getestet (`EinbettungErstNachKlickTest`); Platzhalter und Knopf entstehen erst im Browser, ohne JavaScript bleibt der Kartenrahmen leer | RE17, RE21 |
| Zweig `sofort/2026-09-17-bf24-und-2-weitere` nach `main` mergen und pushen (zwei Commits vor `f489e76`); danach mit einem Bildschirmleser eine Fehlermeldung auf `/kontakt/` auslösen und `/feed/` in einem Feedleser abonnieren | `8014429`, `22fea97` — `BF24` und `GE32` sind nur gegen das gerenderte HTML bzw. XML getestet; kein Bildschirmleser und kein Feedleser hat sie gesehen | BF24, GE32 |
| ~~Zweig `sofort/2026-09-17-pj05-und-2-weitere` erneut nach `main` mergen und pushen~~ (gemergt mit `f489e76`, `main` = `origin/main`); die Bildschirmleserprobe bleibt offen, siehe Zeile darüber | `a708c7f`, `a8190b8` — `BF24` war nur als Attribut im gerenderten HTML getestet | PJ05, BF24 |
| Die vier Fremdskripte beschaffen und nach `shop1/static/shop1/` legen, dann `src`, `integrity` und `CSP_QUELLEN` umstellen | keine `.js`-Datei unter `shop1/static/`; der Lauf in Paket 227 konnte nicht herunterladen | PF31 |
| ~~Zweig `sofort/2026-09-17-bf29-und-2-weitere` nach `main` mergen und pushen~~ (gemergt mit `dd804dc`); danach eine Kontaktanfrage abschicken und im Django-Admin unter „Kontaktanfragen" nachsehen, ersten CI-Lauf mit `pillow==12.3.0` abwarten, lokal `pip install -r requirements.txt` | `2cfa8ee`, `0eb7589` — die Suite lief mit Pillow 11.3.0 (`LOGBUCH.md`, Paket 219) | SI40, MW18 |
| Speicherung der Kontaktanfragen in der Datenschutzerklärung nennen, Löschfrist festlegen | seit `0eb7589` liegen Name, E-Mail, Betreff und Nachricht im Shop; Entscheidung der Betreiberin | MW18 |
| ~~Zweig `sofort/2026-09-17-fo03-und-2-weitere` nach `main` mergen und pushen~~ (gemergt mit `8717afe`); danach im Browser doppelt absenden (Kontakt und Newsletter), Zurück-Taste, eine `data-bestaetigen`-Rückfrage ablehnen | `3e0a59f`, `370fce7`, `641153b` — die Absendesperre ist nur als Attribut und Skripttext im gerenderten HTML getestet | FO03, FO04, FO07 |
| `pruefe_seite` fahren und live eine ungültige Kontaktadresse sowie eine neue Newsletter-Anmeldung ausprobieren (Paket 208 ist mit `d978a89` gemergt) | `278e715`, `9b3fc07`, `6aa3087` — `pruefe_seite` lief beim Bau nicht (`LOGBUCH.md`, Paket 208) | FO06, FO08, FO09 |
| Gemeinsamer Drosselzähler und Doppel-Merker über alle Gunicorn-Worker (Redis oder Datenbank-Cache) und eine Mail-Obergrenze je Tag | Zähler und Merker liegen im `LocMemCache` je Prozess; beides braucht einen neuen Dienst oder eine Tabelle | FO09, FO03 |
| Einmal das Kontaktformular live abschicken (der Zweig mit `MW15`/`GE15` ist inzwischen in `main`) | `4fd7776`, `be550e3`, `bb6fee1` | MW15, GE15, KV07 |
| `python manage.py pruefe_mail` einmal mit den echten Zugangsdaten fahren (Railway-Konsole oder lokal mit gesetztem `BREVO_API_KEY`/`EMAIL_HOST_*`) | die acht Tests laufen alle mit `--ohne-verbindung`, die beiden Anmeldeprüfungen gegen ein vorgetäuschtes Gegenüber — ob Brevo und das Relay diese Zugangsdaten annehmen, ist damit nicht belegt | MW15 |
| `CANONICAL_HOST` in Railway setzen | live 02.09.2026: Apex antwortet 200 ohne 301; die Vorgabe von `CANONICAL_HOST` ist auch im Zweig SI09 leer (`mainweb/settings.py:45`) | TS11 |
| Nach dem Push: ersten CI-Lauf mit Django 5.2.17 abwarten; lokal `pip install -r requirements.txt` | die Suite lief beim Bau mit Django 6.0.5 (`pip install`/`docker build` gesperrt, `LOGBUCH.md` Paket 155) | PJ11 |
| Nach dem Deploy mit offener Browserkonsole ansehen: `/payment/<id>/`, dazu mit dem Zweig SI09 Löschrückfrage im Profil, „Reset" in der Panel-Statistik, Bestellfilter, Kampagnenknöpfe, Nachladen der Schriften | CSP scharf, Deckung nur durch Tests belegt; das Verhalten der Ersatzskripte ist ungeprüft (`28d1ca3`) | SI08, SI09 |
| `'unsafe-eval'` aus `script-src` (CSP-Fassung von Alpine, jeder Ausdruck als registrierte Komponente), `'unsafe-inline'` aus `style-src` | laut `LOGBUCH.md` Paket 164 224 Treffer auf Alpine-Attribute in 19 Vorlagen; nur mit Browser prüfbar | SI09 |
| ~~`runtime.txt`/`railway.json`~~ — im Zweig Paket 282 angelegt (`45b1477`); offen nur Merge, Push und ein Blick ins Railway-Log, ob Bau und Start wie bisher laufen | `==` und Lockfile seit 11.09. erledigt (`51cbf74`); die Messung liest `requirements.lock` nicht als Lockfile (`LOGBUCH.md`, Paket 155) | VL02 |
| Permissions-Policy-Kopfzeile | live: 4 von 7 Schutzköpfen; die CSP ist im Zweig 11.09. als echte Kopfzeile erledigt (`9a3226f`) | SI07, VL04 |
| **Rest von `SI17`:** die zwei Chart.js-Einbindungen des Admin-Panels ohne `integrity` | `admin/werbung_list.html:365` lädt `chart.js@4.4.0/dist/chart.umd.min.js` — eine Datei, die jsDelivr beim Abruf selbst erzeugt und für die es keinen veröffentlichten Hash gibt; `admin/stats.html:246` lädt `chart.js` ganz ohne Fassung. Beide abzusichern hiesse, die Einbindung auf eine andere Datei umzustellen. Die vier Fremdskripte der öffentlichen Seiten sind seit `680a641` abgesichert | SI17 |
| Gestaltete 404-Seite (kein `404.html` im Projekt) | live: 13 Wörter, ohne Navigation | BT05, TS20 |
| Fehler-Monitoring (Sentry o. ä.) — **der zweite und der dritte Prüfbefehl sind seit dem 12.09.2026 gebaut** (`pruefe_links`, `11acccc`, seit `43f25c3` auf `main`; `pruefe_mail`, `4fd7776`, im Zweig), ein CI-Lauf bei jedem Push steht in `.github/workflows/pruefungen.yml` | 3 von 7 QS-Bausteinen (Messung 02.09.2026) | VL19, PJ01, MW15 |
| `STRIPE_*`-Variablen in Railway entfernen | nicht dokumentiert, welche Namen genau | — |
| Zehn Module ohne eigenen Test (`forms.py`, `signals.py`, `views/_helpers.py`, `views/auth.py`, `views/cart.py`, `views/checkout.py`, `views/gaestebuch.py`, `views/shop.py`, `pruefe_seite.py`, `tiktok stream/streamtest.py`) — die View-Module sind über Seiten-, Konto- und Zahlungstests indirekt abgedeckt, das Audit zählt nur direkte Importe. Die beiden jüngeren Prüfbefehle `pruefe_links` und `pruefe_mail` haben eigene Testklassen in `test_einstellungen` | PJ03 | PJ03 |
