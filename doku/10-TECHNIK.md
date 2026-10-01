---
bereich: technik
titel: Technik, Hosting und Aufbau
stand: 2026-10-01
status: teilweise
fortschritt: 86
zusammenfassung: Stand 01.10.2026: alle Zweige in main (36c0741, live); Django 5.2.17, Mail über Gmail-SMTP (seit 27.09.), Verkaufsschalter aus, Fehler-Monitoring per AdminEmailHandler (VL19), CSP scharf, Apex-301 aktiv; Missbrauchsschutz-Tabelle (§3a) und Offen-Liste gegen Code und Live-Seite erneuert.
offen: 14
quellen: CLAUDE.md, DOCUMENTATION.md, LOGBUCH.md, paypal_sandbox_tutorial.md, start.sh, Dockerfile, requirements.txt
---

# Technik — Luviq Universe

*Woran sich der Fortschritt bemisst: am gemessenen Bereichswert **Code-Qualität** des Laufs vom 02.09.2026 (Regelstand `2026-09-02a`), gerundet — bei allen sechs betreuten Seiten dieselbe Bezugsgröße.*

Detailquelle bleibt [`../CLAUDE.md`](../CLAUDE.md) (Architektur, Fallstricke) und
[`../DOCUMENTATION.md`](../DOCUMENTATION.md) (Modelle, E-Mail-Flows, Admin, Sicherheit).

> **Stand 01.10.2026 (geprüft):** Alle bis dahin geführten Arbeitszweige (`sofort/…`, `mail/…`, `recht/…`, `design/…`) sind in `main` gemergt (`git branch -r --no-merged origin/main` ist leer); `main` = `origin/main` = `36c0741` (TS19, Bild-Sitemap, 01.10.2026), und die Live-Seite zeigt diesen Stand (Sitemap mit Bild-Auszeichnung am 01.10.2026 abgerufen). Wo unten „Zweig“ oder „nicht gemergt“ steht, ist das **Verlauf** des jeweiligen Tages und gilt seit dem Merge als live, sofern der Satz nichts anderes sagt. Der **Verkauf ist aus** (`VERKAUF_AKTIV` ohne Variable = aus: Marke im Aufbau, Archiv statt Shop); nach Angabe des Betreibers ist **kein Gewerbe angemeldet** — die Seite nennt deshalb keine Unternehmensangaben (Impressum nach § 5 DDG nur mit Luisa Brehler als Person, Alsfeld, E-Mail).

## Stack

| Baustein | Was | Quelle |
|---|---|---|
| Framework | Django `>=5.0,<6.1` auf main; **Zweig 11.09.: `Django==5.2.17`**, jede Abhängigkeit mit `==`, Unterabhängigkeiten in `requirements.lock` (per `--constraint` aus `requirements.txt` eingebunden). **Zweig 17.09. (`SI40`, `2cfa8ee`):** `pillow==12.3.0` statt `11.3.0` (laut `LOGBUCH.md` hatte 11.3.0 acht bekannte Lücken; Pillow nur über Djangos `ImageField` genutzt) — auf dem Entwicklungsrechner ist weiter 11.3.0 installiert. Eine App `shop1`, Projektkonfiguration `mainweb/` | `requirements.txt`, `requirements.lock`, `CLAUDE.md` |
| Python | Container `python:3.11-slim`, CI Python 3.12, Entwicklungsrechner Python 3.14. Unter der Spanne auf main bekam der Container Django 5.2.x, der CI-Lauf 6.0.x. **Zweig 11.09.:** mit dem Nagel bauen Container und CI dieselbe Fassung 5.2.17 (laut PyPI Python 3.10–3.14). Der Entwicklungsrechner hatte am 11.09.2026 noch Django 6.0.5 — die Suite lief beim Bau damit, nicht mit 5.2.17; erster Nachweis ist der nächste CI-Lauf | `Dockerfile`, `requirements.txt`, `.github/workflows/pruefungen.yml`, `LOGBUCH.md` Paket 155 |
| Datenbank | PostgreSQL über `DATABASE_URL` (Railway), lokal SQLite; **zweite Datenbank `pystore`** über `PYSTORE_DATABASE_URL` | `mainweb/settings.py` |
| Server | Gunicorn: `gthread`, 2 Worker × 4 Threads, Timeout 30 s, Worker-Erneuerung nach 1.000 Anfragen (live) | `start.sh` |
| Statische Dateien | WhiteNoise + `ManifestStaticFilesStorage` (Content-Hash im Dateinamen). **Falle:** `ManifestStaticFilesStorage` legt keine `.gz` an, und WhiteNoise packt nicht selbst — es liefert nur eine vorhandene `datei.gz` aus. Bis Paket 267 gingen deshalb alle statischen Dateien ungepackt raus, auch `tailwind.css` und `style.css`, auf die der erste Inhalt wartet. **Zweig Paket 267 (`5515bf3`, `PF26`):** `start.sh` packt nach `collectstatic` mit `python -m whitenoise.compress --quiet staticfiles` (in `whitenoise==6.12.0` enthalten, keine neue Abhängigkeit; ohne `brotli` nur gzip), nicht blockierend. Bewusst ein eigener Aufruf statt `CompressedManifestStaticFilesStorage`. `StildateienGepacktTest` in `test_ladezeit` hält Lage und Reihenfolge des Schritts in `start.sh` fest | `DOCUMENTATION.md` §5, `start.sh`, `LOGBUCH.md` Paket 267 |
| Medien | Cloudinary (`django-cloudinary-storage`, `CLOUDINARY_URL`). Vorlagen binden Cloudinary-Bilder über den Filter `cloud` (`shop1/templatetags/custom_tags.py`) ein, der `f_auto,q_auto` einsetzt. **Zweig Paket 267 (`1737e74`, `PF15`):** der Filter setzt zusätzlich die Endung jeder Cloudinary-Adresse auf `.webp` (`.jpg`, `.png`, `.gif` usw. und Adressen ohne Endung; `.webp`/`.avif` bleiben, Abfrageteil bleibt erhalten). Mit `f_auto` bestimmt die Endung nur den Rückfall für Browser ohne Formataushandlung — der ist damit WebP statt JPEG/PNG. Fremde und lokale `/media/`-Adressen bleiben unverändert. Tests: `BildformatTest` in `test_ladezeit` | `DOCUMENTATION.md` §5, `LOGBUCH.md` Paket 267 |
| Mail | **Gmail-SMTP** (`smtp.gmail.com:587`, Postfach der Betreiberin) seit 27.09.2026; `shop1/utils.py::send_brevo_email()` heißt noch so, nimmt aber ohne `BREVO_API_KEY` den SMTP-Weg (siehe „E-Mail-Versand“) | `CLAUDE.md`, `mainweb/settings.py`, `shop1/utils.py` |
| Login-Schutz | django-axes: 10 Fehlversuche je Benutzername+IP, 1 h Sperre, eigenes Lockout-Template | `settings.py` (`AXES_*`) |
| Zahlung | PayPal (JS-SDK in `payment.html`, Capture in `views/checkout.py`) und Vorab-Überweisung (`BANK_IBAN`, `BANK_INHABER`) | `DOCUMENTATION.md` §3 |
| CSS | Tailwind-CLI aus `tailwind_input.css` nach `shop1/static/shop1/tailwind.css`; **kein `package.json`, kein npm-Build im Repo**; dazu `shop1/static/shop1/style.css` | `CLAUDE.md`, `tailwind.config.js` |
| JS | **Stand 01.10.2026: GSAP und Three.js stehen in keiner Vorlage mehr (Umbau vom 19.09.2026); Alpine.js nur noch auf Seiten mit altem Markup (`{% block alpine %}`: Warenkorb, Konto, Gästebuch, Admin).** Frühere Fassung: Alpine.js 3.14.8 + `@alpinejs/intersect` (base.html), GSAP 3.12.5 (Startseite), Three.js 0.158.0 (nur Desktop, ohne `prefers-reduced-motion`, nachgeladen) — alle von `cdn.jsdelivr.net`, **Zweig SI17: alle vier mit `integrity` (SHA-256 aus der jsDelivr-Dateiauskunft) und `crossorigin="anonymous"`; wer eine Fassung hochzieht, muss den Hash mitziehen, sonst lädt das Skript nicht mehr**. Alpine (Standardfassung) braucht `'unsafe-eval'` in der CSP. **Zweig SI09:** eigene Inline-Skripte nur mit `nonce="{{ csp_nonce }}"`, keine `on…`-Attribute mehr — deren Aufgaben übernimmt ein Skript im `<head>` von `base.html` über `data-bestaetigen`, `data-bei-fehler-ausblenden`, `data-auto-absenden`, `data-schrift-nachladen`. **Fünftes Ersatzattribut seit dem 18.09.2026 (`RE17`, `d58a96c`): `data-src`** an den beiden Google-Maps-Rahmen in `_reviews_map.html` — ausgewertet nicht im `<head>`, sondern im Skript am Körperende von `base.html` (`:513` ff.), das den Platzhalterknopf „Karte laden" erzeugt und `src` erst im Klick setzt. Ein Test in `test_einstellungen` zählt die Ersatzattribute und verlangt jedes davon im Skripttext von `base.html`. **Selbst ausliefern (`PF31`) ist am 17.09.2026 als nicht möglich beendet** — die vier Dateien liegen nicht im Projekt, unter `shop1/static/` gibt es keine `.js`-Datei ([80-AUFGABEN.md](80-AUFGABEN.md), Bewertungsblock) | `templates/base.html`, `index.html` |
| Cache | `LocMemCache` (Zweig ausdrücklich: `LOCATION luviq`, `MAX_ENTRIES 300`); Werbeliste 60 s; Zweig: `sitemap.xml`/`llms.txt` 15 min | `settings.py`, `LOGBUCH.md` Schritt 33 |
| Zeitzone / Sprache | `Europe/Berlin`, `USE_TZ=True`, `de-de` | `settings.py` |

## Hosting und Deploy

| | |
|---|---|
| Railway | Projekt **`webseiten`** → Dienst **`Luviq-Luisa`**, Umgebung **`shop`**; Railway-Adresse `luviq-luisa-shop.up.railway.app` (antwortet 200, 02.09.2026) |
| Domain | `www.luviq-alsfeld.com`; Apex `luviq-alsfeld.com` zeigt auf denselben Dienst und **leitet per 301 auf www** (abgerufen 01.10.2026, `CanonicalHostMiddleware`); Zertifikat Let's Encrypt bis 30.11.2026 (geprüft 01.10.2026) |
| Deploy | Push auf `main` löst den Docker-Bau aus (Auto-Deploy); kein Knopf nötig. Letzte Auslieferung: `36c0741` vom 01.10.2026 — an der Live-Sitemap mit Bild-Auszeichnung belegt (die Railway-Auslieferungsliste wurde nicht abgefragt). Railway-Inventur 26.09.2026: letzter Deploy SUCCESS |
| Container | `Dockerfile`: `python:3.11-slim`, `libpq-dev`/`gcc`, `pip install -r requirements.txt`, `CMD /app/start.sh`, Port 8000. **Zweig 11.09.:** kopiert `requirements.txt` **und** `requirements.lock` — ohne die Lockdatei bricht pip an der `--constraint`-Zeile ab |
| Railway-Konfiguration | **Zweig Paket 282 (`45b1477`, `VL02`):** `railway.json` — `build.builder` `DOCKERFILE`, `dockerfilePath` `Dockerfile`, `deploy.startCommand` `/app/start.sh` (dasselbe wie das `CMD`), **kein `healthcheckPath`** (sonst hinge der Healthcheck an `CanonicalHostMiddleware`, siehe [80-AUFGABEN.md](80-AUFGABEN.md) „Offen" Nr. 0a). `railway.json` gewinnt auf Railway gegen das `CMD` des Images — wer den Startbefehl ändert, muss beide Stellen ändern. `runtime.txt`: `python-3.11` wie `FROM python:3.11-slim`, ohne Patchstand. `DeployDateienTest` (`test_einstellungen`) bricht, sobald eine der Angaben vom `Dockerfile` abweicht |
| Push von diesem Rechner | `git -c credential.helper='!gh auth git-credential' push origin <zweig>` (Credential Manager ist auf diesem PC kaputt) |

**Startreihenfolge im Container (`start.sh`, auf `main`):**

1. `migrate --noinput`
2. Superuser aus `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` anlegen oder abgleichen (`is_staff`, `is_superuser`, Passwort wird **bei jedem Start** neu gesetzt)
3. `loaddata initial_data.json` (optional, Fehler ignoriert)
4. `fix_pystore_schema` (eigener Befehl, behebt die `seite`-Spalte in `pystore`)
5. `collectstatic --noinput --clear`
5a. **Zweig Paket 267 (`5515bf3`):** `python -m whitenoise.compress --quiet staticfiles` — legt die `.gz`-Fassungen an, die WhiteNoise ausliefert; **nicht blockierend** (`|| echo "WARNING…"`, ohne `.gz` liefert WhiteNoise wie bisher ungepackt). Muss nach Schritt 5 stehen, sonst löscht `--clear` die Dateien wieder — das prüft `test_start_packt_die_statischen_dateien_nach_dem_sammeln`
6. **Zweig:** `pruefe_seite` — Einstellungen, Datenbanken, aktive Produkte, jede Sitemap-Adresse per Testclient; **nicht blockierend**, nur Log (`--streng` würde Warnungen zu Fehlern machen)
7. `gunicorn mainweb.wsgi:application --worker-class gthread --workers ${GUNICORN_WORKERS:-2} --threads ${GUNICORN_THREADS:-4} --timeout ${GUNICORN_TIMEOUT:-30} --max-requests 1000 --max-requests-jitter 100`, kein `--preload` (teilte Datenbankverbindungen über den Fork)

Diese Reihenfolge gilt auf `main`; `DOCUMENTATION.md` §5 nennt nur drei Schritte und ist veraltet.

**In Railway (gesetzt seit 16.09.2026, live bestätigt 01.10.2026):** `CANONICAL_HOST=www.luviq-alsfeld.com` (ohne sie bliebe die 301 für den Apex wirkungslos; die Vorgabe im Code ist leer). Optional: `CSP_MODUS` (Vorgabe `scharf`, seit `0c18ea7` auf main; `report-only` ist der Rückweg, falls die Bezahlseite oder — mit dem Zweig SI09 — ein Ersatzskript im Browser etwas blockiert), `VISITOR_TRACKING` (Vorgabe an), `GUNICORN_*`.

### Railway-Inventur 26.09.2026

Erhoben lesend am 26.09.2026 (Werte nie notiert; „gleich“ über Hash im Speicher verglichen). Gesamtbild und Befunde K1–K13: `Webagentur Scherzinger\Betrieb-Railway\RAILWAY-INVENTAR.md`; Plan zur Entflechtung: `…\Betrieb-Railway\TRENNUNGSPLAN.md`.

| Punkt | Stand 26.09.2026 |
|---|---|
| Railway | Projekt `webseiten`, Umgebung `shop`, Dienst `Luviq-Luisa` (`2f19cb96-4b35-4f82-ac08-cba3be9698a2`), Repo `Webseitemitstripe`, `main`, Auto-Deploy |
| Letzter Deploy | SUCCESS 26.09.2026; 5xx-Quote 7 Tage: 4 von 11 785 |
| Datenbank | `DATABASE_URL`: **gemeinsame Supabase-Datenbank „A“**, Schema `public`, App `shop1` — dieselben Tabellen `auth_user`, `django_migrations`, `django_session` wie RTC, Rümpelwerk, WVM-IT, JARVIS 4 (K1, hoch). `PYSTORE_DATABASE_URL`: Supabase „B“, außer Luviq nur von toten Diensten genutzt |
| Variablen (eigene Werte) | `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_URL`, `ADMIN_USERNAME`, `ALLOWED_HOSTS`, `ALLOWED_HOSTS_EXTRA`, `BANK_IBAN`, `BANK_INHABER`, `BREVO_API_KEY`, `CANONICAL_HOST`, `CLOUDINARY_URL`, `DATABASE_URL`, `DEBUG`, `DEFAULT_FROM_EMAIL`, `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_HOST_PASSWORD`, `EMAIL_HOST_USER`, `EMAIL_PORT`, `EMAIL_USE_SSL`, `EMAIL_USE_TLS`, `PAYPAL_CLIENT_ID`, `PAYPAL_EMAIL`, `PAYPAL_MODE`, `PAYPAL_SECRET`, `PYSTORE_DATABASE_URL`, `SECRET_KEY`, `SITE_NAME`, `SITE_URL`, `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `USE_SMTP_EMAIL`, `WERBUNG_CLOUDINARY_URL` |
| Geteilte Werte | **Stripe (alle drei), PayPal Client/Secret, Brevo, SMTP-Zugang, Admin-Benutzer und -Passwort sind gleich wie in den toten Diensten `tutorials` und `pixvault`** (K7, hoch). `CLOUDINARY_URL` = Rümpelwerk; `WERBUNG_CLOUDINARY_URL` = WVM-IT/JARVIS (K6) |
| Domains | luviq-alsfeld.com (301 → www), www.luviq-alsfeld.com (200) |

## Umgebungsvariablen

Nur Namen. Werte stehen in Railway bzw. in der lokalen `.env` (nicht in Git).
**Ohne `.env` mit gesetztem `SECRET_KEY` läuft lokal kein `manage.py`-Befehl** — `settings.py` wirft bei `DEBUG=False` und Standard-Schlüssel einen `RuntimeError`.

| Gruppe | Variablen |
|---|---|
| Kern | `SECRET_KEY`, `DEBUG` (ohne Variable `False`), `ALLOWED_HOSTS_EXTRA` (Komma-Liste; `https://`-Präfix wird toleriert), `SITE_URL`, `SITE_NAME`, `PORT` |
| Datenbanken | `DATABASE_URL`, `PYSTORE_DATABASE_URL` (fehlt sie, ist `pystore` eine Kopie von `default` und wird migriert) |
| Admin | `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`, `ADMIN_URL` (Pfad des regulären Django-Admins) |
| Mail | `USE_SMTP_EMAIL`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` (ohne Variable `noreply@luviq-alsfeld.com` seit `MW22`, `ed835a9`, auf `main` — vorher `noreply@luviq-shop.de`, eine Domain, die es nicht gibt; Brevo verschickt davon erst, wenn `luviq-alsfeld.com` im Brevo-Konto bestätigt ist), `BREVO_API_KEY` |
| Zahlung | `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`, `PAYPAL_MODE`, `PAYPAL_EMAIL`, `BANK_IBAN`, `BANK_INHABER` |
| Medien / Werbung | `CLOUDINARY_URL`, `WERBUNG_CLOUDINARY_URL`, `PYSTORE_CLOUDINARY_CLOUD_NAME`, `PYSTORE_MEDIA_URL` |
| Sonstiges | `GOOGLE_REVIEW_URL` (Bewertungslink im Kontextprozessor) |
| **Verkauf** | `VERKAUF_AKTIV` — **Vorgabe aus** (`1/true/yes/on/ja/an` schaltet ein). Aus = Marke im Aufbau: keine Preise, kein Warenkorb, keine Kasse, kein PayPal, keine Sätze zu § 19 UStG/Zahlung/Versand, `Organization` statt `Offer`/`LocalBusiness`, AGB `noindex` und aus Sitemap/llms.txt, Kaufweg-Wissensbeiträge leiten mit 302 auf `/wissen/`; die Stücke erscheinen als Archiv bisheriger, bereits vergebener Stücke („Nº 00x · Archiv"). Siehe Falle 22 und 23. `BETREIBER_KONTEN` (Komma-Liste, Vorgabe `luisabre`): Gästebuch-Beiträge dieser Konten erscheinen nicht auf der Startseite |
| **IndexNow (Paket 306)** | `INDEXNOW_KEY` — Schlüssel für IndexNow (`shop1/indexnow.py`), 8–128 Zeichen aus Buchstaben, Ziffern und Bindestrich; leer oder ungültig = aus (Vorgabe). Gemeldet wird unter dem Host von `SITE_URL` — `SITE_URL` muss also auf `https://www.luviq-alsfeld.com/` stehen (seit 16.09.2026 so gesetzt, [80-AUFGABEN.md](80-AUFGABEN.md) „Offen" Nr. 0) |
| **Betrieb** | `CANONICAL_HOST`, `CSP_MODUS` (`scharf` · `report-only` · `aus`; Vorgabe im Zweig 11.09. `scharf`), `VISITOR_TRACKING`, `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT` |
| **Nachtausgabe und Mail (seit 19.–27.09.2026)** | `MOTIVANFRAGE_AKTIV` (Vorgabe an), `MOTIV_EMPFAENGER` (leer = `ADMIN_EMAIL`), `DROP_TERMIN` (Vorgabe im Code `2026-10-08T18:00+02:00`, leer = kein Countdown), `DROP_NUMMER` (leer = nächste freie Archivnummer), `BETREIBER_KOPIE_AN` (Kopie jeder Anfrage an die Webagentur, `aus` schaltet ab) — Quellen: `mainweb/settings.py`, `shop1/luviq_daten.py`, `shop1/mails.py` |
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

## E-Mail-Versand

**Stand 27.09.2026 — Versand über Gmail statt Brevo.** Alle Mails gehen per SMTP über
Luisas Postfach `brehlerluisa@gmail.com` (`smtp.gmail.com:587`, STARTTLS). Railway
(webseiten/shop/Luviq-Luisa): `EMAIL_HOST=smtp.gmail.com`, `EMAIL_PORT=587`,
`EMAIL_HOST_USER` = `DEFAULT_FROM_EMAIL` = `brehlerluisa@gmail.com`, `EMAIL_HOST_PASSWORD` =
Google-App-Passwort (nur in Railway, von Bastian eingetragen), **`BREVO_API_KEY` entfernt** →
`send_brevo_email()` nimmt den SMTP-Zweig (der Funktionsname bleibt). Gmail verschickt nur von
der eigenen Adresse, deshalb ist der Absender dieselbe Adresse wie die Anmeldung.
Vorgeschichte: Der alte Brevo-Schlüssel gehörte einem fremden Brevo-Konto mit IP-Sperre (401
„unrecognised IP“ seit mindestens 17.09.; keine echte Anfrage verloren, alle in `KontaktAnfrage`/
`Motivanfrage` gespeichert), am 27.09. kurz Brevo-Konto …69, dann Gmail. Texte auf Startseite,
Kontakt, Datenschutz und Wissen nennen Gmail (Google Ireland) statt Brevo; `DatenschutzTest`
hält das. Offen: `pruefe_mail` spricht in Meldungen noch von Brevo (prüft den SMTP-Weg aber
richtig). Vergleich aller Seiten: `pystore-overview/docs/MAILVERSAND.md`.

Stand 26.09.2026, Zweig `mail/2026-09-26-benachrichtigung` (seit dem 27.09.2026 gemergt: Pull Request #1, `5e95126`).
Alle Mails laufen über `shop1/utils.py::send_brevo_email` (Brevo-API, ohne
`BREVO_API_KEY` SMTP mit `EmailMultiAlternatives`), jede mit Text- **und**
HTML-Teil. Gestaltung und Kopie an die Webagentur stehen in `shop1/mails.py`.

| Formular | Mail an Luisa (`ADMIN_EMAIL` bzw. `MOTIV_EMPFAENGER`) | Kopie an die Webagentur | Mail an den Besucher |
|---|---|---|---|
| Kontakt (`/kontakt/`, `views/shop.py`) | ja, `Reply-To` = Besucher, Betreff `Kontaktformular: …` wie bisher | ja, `[Luviq] Neue Kontaktanfrage – Name` | **keine** (bewusst, Lehre vom 17.09.2026) |
| Motiv anfragen (`views/motiv.py`) | ja, Betreff `Motivanfrage: …` wie bisher | ja, `[Luviq] Neue Motivanfrage – @name` | **keine** (Danke-Seite sagt es) |
| Registrierung (`views/auth.py`) | – | ja, nur Benutzername und Adresse, kein Passwort, kein Link | Bestätigungslink (Signal, ohne Namen) |
| Newsletter (`views/legal.py`) | – | – | Double-Opt-in-Link |
| Bestellung (nur bei `VERKAUF_AKTIV`, `views/checkout.py`) | – | – | Bestell- und Zahlungsmail, **unverändert** |

- **Vorlagen** unter `shop1/templates/emails/`: `basis.html` (Tabellenlayout,
  600 px, nur Inline-Styles, Farben aus `luviq.css`, Wortmarke als Text, kein
  Bild, Dunkelmodus-Ergänzung im `<style>`), `_felder.html`,
  `anfrage_admin.html` (Luisa, mit „Antworten"-Knopf und Admin-Link),
  `betreiber_kopie.html` (Webagentur), `besucher.html` (Konto/Newsletter
  bestätigen, ohne Namen und ohne eingetippten Text). Eingaben escapet
  Django, Nachrichten mit `linebreaksbr`. Scheitert die Gestaltung, geht die
  Mail an Luisa mit der Textfassung hinaus.
- **Kopie an die Webagentur:** Umgebungsvariable `BETREIBER_KOPIE_AN`
  (kommagetrennt; ohne Variable `bastian.scherzinger05@gmail.com`; leer oder
  `aus` schaltet ab). Eigene Mail mit eigenem `try/except`, erst nach
  Drosselung, Feldprüfung, Spamschutz und Doppelsperre — Spam und
  Doppelklicks lösen keine Kopie aus. Ist die Adresse schon regulärer
  Empfänger, entfällt sie (Groß-/Kleinschreibung egal). Links zeigen auf
  `CANONICAL_HOST` (sonst `www.luviq-alsfeld.com`), nicht auf `SITE_URL`.
- **Keine Preise, kein Bestell-Wortlaut, keine Kleinunternehmer-Sätze** in
  diesen Mails; die Bestellmails aus `checkout.py` sind nicht angefasst.
- **Notschalter:** `MOTIVANFRAGE_AKTIV` (Formular zu, keine Mail);
  `BETREIBER_KOPIE_AN=aus` für die Kopie. Einen allgemeinen Mail-Notschalter
  gibt es nicht.
- **Vorschau:** `python tools/mailvorschau.py <zielordner>` schreibt jede
  Mailart mit Beispieldaten als HTML-Datei, verschickt nichts.
- **Tests:** `shop1/tests/test_mailversand.py` (Kopie bei echter Anfrage,
  Spam, Doppelklick, Abschalten, keine Dublette, Fehler bricht nichts,
  HTML-Teil maskiert `<script>`). `LuviqTestCase` ersetzt den Versand der
  Kopie in jedem Test (`self.kopie_versand`).

## Prüfbefehle und Tests

| Befehl | Was | Stand |
|---|---|---|
| `python manage.py test shop1` | Testsuite in 17 Modulen (`CLAUDE.md`), 400 `def test_` im Code (gezählt 01.10.2026); Laufzeit rund 2,5 Minuten; zuletzt 399 Tests grün in Paket 544 (28.09.2026), seitdem TS19 mit einem Test mehr — nicht neu gelaufen | main |
| `python manage.py test shop1.tests.<modul>` | einzelnes Modul | main |
| `python manage.py pruefe_seite [--streng]` | Prüfbefehl: Einstellungen, beide Datenbanken, aktive Produkte (Pflichtwerte, doppelte Slugs), jede Sitemap-Adresse 200 mit Titel, Beschreibung 110–175, canonical, robots, JSON-LD, Schutzkopfzeilen samt CSP; hinterlässt keine Spuren (`VISITOR_TRACKING` aus, zurückgerollte Transaktion) | Zweig |
| `python manage.py pruefe_links [--streng]` | Prüfbefehl (Zweig 12.09., PJ01): liest `/`, jede Sitemap- und jede llms.txt-Adresse und ruft **jeden `<a href>` darin** ab — tote eigene Adressen sind Fehler, Weiterleitungen Warnungen (ausser auf `LOGIN_URL`), fremde Ziele werden nur auf `https` geprüft, nicht abgerufen; verändernde Pfade (Warenkorb, Abmeldung, Werbeklick, Kommentar) stehen in `KEINE_PRUEFUNG`. Gleiche Vorsorge wie oben: kein Besuchsprotokoll, zurückgerollte Transaktion | seit `43f25c3` auf `main` |
| `python manage.py pruefe_mail [--ohne-verbindung] [--streng] [--an ADRESSE]` | Prüfbefehl (Zweig 12.09., MW15): **beide** Mailwege. Zeigt die Einstellungen (Backend, `DEFAULT_FROM_EMAIL`, `ADMIN_EMAIL`, `SITE_URL`, Host/Port/Verschlüsselung, Benutzer — von Schlüsseln und Passwörtern nur „gesetzt (n Zeichen)", die Ausgabe darf in ein Container-Log) und versucht die **Anmeldung**: Brevo-API-Schlüssel gegen die Kontoauskunft `/v3/account` (Lesezugriff, verschickt nichts), SMTP über `get_connection().open()`. Console-Backend ist im Entwicklungsmodus eine Warnung und im Betrieb ein Fehler; leerer `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` ein Fehler; fehlender `BREVO_API_KEY` und der Vorgabeabsender `noreply@luviq-shop.de` je eine Warnung. `--an ADRESSE` schickt eine Testmail **synchron und ohne `fail_silently`**, `--ohne-verbindung` lässt jeden Netzzugriff aus. Gegen die echten Zugangsdaten dieses Dienstes noch nie gelaufen | Zweig |
| `python manage.py check --deploy` | Django-Prüfung | beide |
| `python manage.py fix_pystore_schema` | `seite`-Spalte in `pystore` | beide |
| `python manage.py makemigrations shop1` | einzige App; 18 Migrationen auf `main` (`0018` legt die pystore-Tabellen auch ohne PostgreSQL an), im Zweig 17.09. 19 (`0019_kontaktanfrage`, `MW18`) | |

**Testmodule (Zweig 12.09., `def test_` je Datei, gezählt am 12.09.2026):** `test_seiten` (14), `test_seo` (31), `test_geo` (25, davon 5 zum `Article`/`ItemList`-Schema des Wissensbereichs), `test_inhalt` (15), `test_formulare` (16), `test_daten` (22), `test_einstellungen` (59, davon 6 zu `pruefe_links` und 8 zu `pruefe_mail`), `test_barrierefreiheit` (11), `test_ladezeit` (9), `test_aufbau` (2, Designwache), `test_warenkorb` (8), `test_zahlung` (11), `test_konto` (10), `test_zugriffsschutz` (10) — zusammen **243**; dazu `_basis.py` (Basisklasse `LuviqTestCase`) und `_aufbau.py` (Fingerabdruck) mit `aufbau_referenz.json` (5.148 Zeilen).

**Drei Regeln für neue Tests** (`CLAUDE.md`): `secure=True` ist Pflicht (sonst prüft man nur die 301 der SSL-Weiterleitung) → `self.hole()` / `self.sende()`; `databases = {'default', 'pystore'}` (die Besuchs-Middleware schreibt bei jeder Antwort); der Cache wird vor jedem Test geleert (`sitemap.xml`/`llms.txt` liegen 15 min im LocMemCache).

**Fehler-Monitoring (VL19, seit Paket 544, 28.09.2026 auf `main`):** kein Sentry (neue Abhängigkeit), sondern Djangos `AdminEmailHandler` — bei `DEBUG=False` und gesetzter `ADMIN_EMAIL` geht jeder serverseitige 500er als Mail an die Betreiberin; `login`/`register`/`change_password` tragen `@sensitive_post_parameters()`, ein Logging-Filter (`shop1/logging_filters.py`, `FehlermailDrossel`) bremst Wiederholungen. Die Katalogregel `VL19` misst den Baustein nur am Dateinamen `sentry` und bleibt deshalb auf „fehlt“. Die drei Prüfbefehle `pruefe_seite`, `pruefe_links` und `pruefe_mail` liegen auf `main`.

## Aufbau des Projekts

```
WebseiteMAIN/
├── mainweb/            settings.py, urls.py, wsgi/asgi
├── shop1/              einzige App
│   ├── views/          Package: shop.py, auth.py, cart.py, checkout.py, legal.py, gaestebuch.py, wissen.py, motiv.py, _helpers.py
│   ├── admin_views.py  eigenes Admin-Panel /shop-admin/… (24 Routen), Decorator admin_required dort selbst definiert
│   ├── models.py       UserProfile, Subscriber, Produkt, Cart, CartItem, Order, OrderItem, Werbung, WerbungStat, VisitorLog, PageVisit, KontaktAnfrage, Comment, PyStoreVisitorLog
│   ├── middleware.py   CanonicalHost, ContentSecurityPolicy, PageVisit
│   ├── routers.py      WerbungRouter → pystore
│   ├── verkauf.py      Verkaufsschalter VERKAUF_AKTIV (Kontextprozessor, Middleware)
│   ├── mails.py        gestaltete Mails und Kopie an die Webagentur
│   ├── luviq_daten.py  Texte und Werte der „Nachtausgabe“ (Markensatz, Drop, Schritte)
│   ├── spamschutz.py   Honeypot, Zeitfalle, Inhalts-Score
│   ├── logging_filters.py  FehlermailDrossel (VL19)
│   ├── seiten_stand.py Register lastmod/dateModified
│   ├── context_processors.py (csp_nonce), signals.py, forms.py, utils.py (send_brevo_email)
│   ├── indexnow.py     IndexNow-Meldungen für Produktänderungen (aus ohne INDEXNOW_KEY)
│   ├── management/commands/  fix_pystore_schema.py, pruefe_seite.py, pruefe_links.py, pruefe_mail.py
│   ├── tests/          17 Module
│   ├── templates/shop1/  Seiten, legal/, wissen/, admin/, teile/ (archiv_karte.html, wissen_article_ld.html)
│   └── static/shop1/   style.css, tailwind.css, images/ (WebP in mehreren Breiten, luviq.css, fonts/)
├── templates/base.html Navigation, Fusszeile, JSON-LD-Graph, Schriften, Alpine
├── start.sh · Dockerfile · requirements.txt · requirements.lock · tailwind.config.js · tailwind_input.css
├── .github/workflows/pruefungen.yml   CI bei jedem Push und Pull Request (Python 3.12, collectstatic, manage.py test)
├── CLAUDE.md · DOCUMENTATION.md · GOOGLE_SEO_GUIDE.md · LOGBUCH.md · paypal_sandbox_tutorial.md
└── projekt1/ · tiktok stream/   unversionierte Altablagen, NICHT Teil der App (in .gitignore)
```

Code-Audit (Messung 02.09.2026, lokaler Ordner = Zweig): 114 Dateien, 23.859 Zeilen (53 Python, 45 Templates, 6 Konfig, 5 Doku, 3 CSS, 1 JS, 1 Skript); 115 Befunde (2 kritisch, 36 wichtig, 77 Hinweise), 71 Dateien ohne Befund, Note 0,952; 10 Module ohne Test; 4 „verwaiste" Templates (`lockout.html` ist über `AXES_LOCKOUT_TEMPLATE` in Gebrauch, die drei `wissen/*.html` über das Register — Fehlalarme des Audits). Die dichtesten Befunde liegen in `tiktok stream/` (Altablage, 13 + 11) und `shop1/admin_views.py` (8).

**Aufräumlauf für das Audit (Zweig 18.09., `eb4ab9b`, `PJ07`):** elf Dateien ohne Verhaltensänderung nachgezogen — Modulbeschreibungen (`admin.py`, `context_processors.py`, `routers.py`, `urls.py`, `models.py`, `middleware.py`, `templatetags/custom_tags.py`, `fix_pystore_schema.py`), unbenutzte Einfuhren (`static` in `mainweb/urls.py`, `os` in `custom_tags.py`), umbrochene Zeilen (`views/__init__.py`, `models.py`), ein `print` aus `test_zugriffsschutz.py`, ein zusätzliches `_log.exception` im Schema-Fix und `_track` in `PageVisitMiddleware` gekürzt. `admin_views.py` und `views/checkout.py` blieben bewusst unberührt (Verwaltung und Kasse, nur mit Sandbox-Test). Wie viele Dateien das Audit danach ohne Befund zählt, steht im Messblock von [00-STATUS.md](00-STATUS.md).

**Zweiter Aufräumlauf und protokollierte Ausnahmen (Zweig 18.09., Paket 306, `PJ06`/`PJ07`):** `156176e` gibt acht `except`-Zweigen eine Logzeile im Logger `shop1` — in `views/checkout.py` `checkout()` („Bestellung konnte nicht angelegt werden") und `paypal_capture()` („PayPal-Abschluss für Bestellung … fehlgeschlagen"), beide mit `_log.exception`; in `views/auth.py` die Erfolgsmeldung von `register()`; in `admin_views.py` fünf Stellen (Werbezählung im Dashboard, Werbung anlegen/löschen, Statistik zurücksetzen, Bestellung laden). Der Ablauf bleibt derselbe, die Kundin sieht dieselbe Meldung. `newsletter_subscribe()` fängt beim JSON-Lesen nur noch `ValueError`/`AttributeError`. In `_verify_paypal_order()` steht `timeout=10` jetzt direkt hinter der Adresse — der Audit-Befund `K10` war ein Fehlalarm, die Zeitgrenze stand schon da. `dd339b1` räumt `signals.py`, `views/auth.py` und `forms.py` auf (Modulbeschreibungen, `send_mail` und `_get_or_create_cart` als nie benutzte Einfuhren entfernt, Zeilen umbrochen), ohne Verhaltensänderung. An `views/checkout.py`, das `eb4ab9b` bewusst ausgelassen hatte, ändern sich damit nur Protokollzeilen und die Reihenfolge eines Arguments.

## Fallen

1. **Einziger echter Shop — Änderungen an Warenkorb, Checkout, Zahlung nur mit Sandbox-Test.** Anleitung [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md): Sandbox-Business- und -Personal-Konto, Sandbox-Client-ID in `PAYPAL_CLIENT_ID`, Testkauf, Bestellung springt auf „bezahlt", Artikel wird deaktiviert (1-of-1). Vor Live-Schaltung Live-App und Live-Client-ID. Die Tests `test_warenkorb`, `test_zahlung`, `test_konto` (Zweig) prüfen die Pfade ohne PayPal-Aufruf.
2. **Zwei Datenbanken.** `default` = Shop-Daten, `pystore` = seitenübergreifende Werbe-/Besucherdaten (`Werbung`, `WerbungStat`, `VisitorLog`). `shop1/routers.py::WerbungRouter` zwingt sie nach `pystore` und **blockt ihre Migrationen dort** (`PYSTORE_IS_EXTERNAL`), weil das PyStore-Projekt diese Tabellen verwaltet. Ohne `PYSTORE_DATABASE_URL` ist `pystore` eine **Kopie** von `default` — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der Test-Runner die Testdatenbanken. `PyStoreVisitorLog` ist ein `managed=False`-Proxy auf `shop1_visitorlog` in `pystore` (`db_column='site'`). Migrationen `0013`/`0014` legen die Tabellen nur auf PostgreSQL an, `0018` auf allen anderen Backends.
3. **Views sind ein Package, aber zentral re-exportiert.** `shop1/urls.py` macht nur `from . import views` — **jede neue View muss in `shop1/views/__init__.py` re-exportiert werden**, sonst ist sie unsichtbar. Das gilt auch für klassenbasierte Views: `WissenFeed` (Zweig 17.09., `GE32`) steht in `__init__.py` und im `__all__`, und `urls.py` bindet sie als **Instanz** ein (`path('feed/', views.WissenFeed(), name='wissen_feed')`). Helfer liegen in `views/_helpers.py`.
4. **Zwei E-Mail-Wege.** (1) Django-`send_mail` über SMTP (Brevo-Relay, `USE_SMTP_EMAIL` oder `DEBUG=False`; sonst Console-Backend). (2) `shop1/utils.py::send_brevo_email()` — direkter HTTP-Aufruf an die Brevo-API in einem Thread, weil Railway SMTP-Ports blockt. **Bestell- und Benachrichtigungsmails gehen über Weg 2.** Ein Mailausfall lässt die Bestellung bestehen (Test in `test_zahlung`). **Beide Wege fallen still aus** — der API-Weg protokolliert einen Fehlschlag nur ins Log (`utils.py:41`, `:59`), während die Bestellung als aufgegeben gilt; ein geblockter SMTP-Port heisst, dass niemand sein Passwort zurücksetzen kann. Seit dem 12.09.2026 (Zweig, `MW15`) sieht sich `python manage.py pruefe_mail` genau das an: Einstellungen und Anmeldung beider Wege, auf Wunsch eine Testmail. Er hängt **nicht** an `start.sh`. **Zweig 17.09. (`MW18`):** Kontaktanfragen liegen vor dem Versand in `KontaktAnfrage` und überleben damit einen Mailausfall; für Bestell- und Newslettermails gilt das nicht. **Antwortadresse (Zweig 18.09., `290f422`, `MW21`):** `send_brevo_email(…, reply_to=…)` setzt sie auf beiden Wegen — `replyTo` in der Brevo-API, `reply_to` beim SMTP-Rückfall. Der Rückfall läuft deshalb über `EmailMultiAlternatives` mit angehängtem HTML-Teil statt über `send_mail`, das keine Antwortadresse kennt. Nur `kontakt()` übergibt eine (die Adresse aus dem Formular); ohne sie ginge „Antworten" an die eigene Versandadresse. Wer eine weitere Mail an die Betreiberin einführt, die im Namen eines Besuchers kommt, gibt `reply_to` mit. Gehalten von `AntwortadresseTest` in `test_formulare`. **Tagessperre der Newsletter-Bestätigung:** `_bestaetigung_senden()` (`views/legal.py`) schickt höchstens einen Link je Adresse am Tag und merkt sich das per `cache.add` im `LocMemCache`. Fällt der Cache aus, geht der Link **ohne** Sperre hinaus; seit `a708c7f` (Zweig 17.09., Paket 227, `PJ05`) steht das als `Newsletter: Tagessperre im Cache nicht pruefbar` mit Stacktrace im Logger `shop1`, vorher verschwand es still.
5. **Denormalisierte Bestelldaten.** `CartItem` und `OrderItem` speichern Name und Preis als eigene Felder, nicht als Fremdschlüssel — **Absicht**, damit geänderte oder gelöschte Produkte alte Bestellungen nicht verändern. Erhalten.
6. **`PageVisitMiddleware`** (zuletzt, seit 18.09.2026 cookielos): zählt je Tag über eine Tageskennung (HMAC aus Datum, IP, Browserkennung; Modell `TagesBesucher`, Vortage werden gelöscht) — keine Sitzung, keine IP in der DB (`VisitorLog.ip_address=None`, nur Geräteklasse), kein Fremddienst (ip-api.com entfernt). Nur GET/200/HTML von Browsern, Bots zählen nicht. `VISITOR_TRACKING` schaltet ab (Vorgabe an). `besucher_anonymisieren` in `start.sh` leert Altbestände.
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
22. **Jedes Speichern eines `Produkt` löst eine IndexNow-Meldung aus** (Zweig 18.09., Paket 306, `0b94d8e`) — sobald `INDEXNOW_KEY` gesetzt ist. Das Signal `produkt_an_indexnow` (`signals.py`) hängt an `post_save` **und** `post_delete`, meldet erst in `transaction.on_commit` (eine zurückgerollte Änderung geht nicht hinaus) und überspringt `raw=True`, also das `loaddata` in `start.sh`. Wer Produkte in einer Schleife speichert (Massenänderung, Datenübernahme), erzeugt je Stück eine Meldung; der Pool in `shop1/indexnow.py` hat **einen** Platz, die Schlange liegt im Gunicorn-Prozess und geht bei einem Neustart verloren. Tests, die einen gültigen Schlüssel setzen, ersetzen `shop1.indexnow._POOL` durch eine Attrappe (`IndexNowTest`); ohne Schlüssel und bei `DEBUG` meldet der Code nichts. Die Schlüsseldatei `/indexnow-schluessel.txt` steht an zwei Stellen — Route in `urls.py` und `SCHLUESSEL_PFAD` in `indexnow.py`; ein Test hält beide gleich.

22. **Verkaufsschalter `VERKAUF_AKTIV`** (Zweig `recht/2026-09-18-marke-im-aufbau`, `9b12276`). Ein Modul, drei Stellen: `shop1/verkauf.py` (`verkauf_aktiv()`, Kontextprozessor `verkauf_kontext`, `VerkaufsschalterMiddleware`). Die Middleware fängt in `process_view` die Routennamen `warenkorb`, `add_to_cart`, `remove_from_cart`, `update_cart`, `checkout`, `payment`, `payment_success`, `payment_cancel` ab (302 auf `/#newsletter-form` mit Meldung) und `paypal_capture` (JSON 409) — die Views selbst wissen nichts vom Schalter. **Eine neue Kaufroute gehört in `KAUFROUTEN`**, sonst ist sie ohne Verkauf offen. Vorlagen schalten mit `{% if verkauf_aktiv %}…{% else %}…{% endif %}` **innerhalb** vorhandener Elemente um (Designwache); wo ein Element wegfällt, steht ein gleich gebautes an seiner Stelle. Wissensbeiträge mit `nur_mit_verkauf` zählen nur bei eingeschaltetem Verkauf zu `freigegebene_beitraege()`; `wissen_beitrag()` gibt den Vorlagen die **wirksame** Freigabe als `beitrag.freigegeben`. Gelesen wird der Schalter je Anfrage aus `settings` — `override_settings(VERKAUF_AKTIV=True)` wirkt in Tests; die Testlisten in `_basis.py` (`NICHT_INDEXIERBARE_SEITEN`) werden dagegen beim Import aus dem Vorgabezustand gebildet. `sitemap.xml`/`llms.txt` liegen 15 min im Cache: nach dem Umschalten in Railway kommt der neue Stand mit dem Neustart des Dienstes (Variable ändern = Neustart). Tests: `test_verkauf`.
23. **Ohne Verkauf ist jedes aktive Stück „Archiv — bereits vergeben"** (Zweig `recht/2026-09-18-archiv-statt-verkauf`). Die bisher gezeigten Stücke wurden nie verkauft (keine Rechnungen) und kommen in keinem Drop; deshalb zeigen Karten, Karussell und Produktseite statt „Kommender Drop" `Nº {{ produkt.archiv_nummer }} · Archiv` (Primärschlüssel, dreistellig, `Produkt.archiv_nummer`) und den Satz „Dieses Stück ist bereits vergeben. Neue Stücke gibt es mit dem ersten Drop – trag dich in die Warteliste ein". `meta_title` lässt ohne Verkauf das „kaufen" weg, `meta_description` endet auf „… aus dem Archiv von Luviq Universe". **Folge:** ein neues Stück, das vor dem Einschalten hochgeladen wird, steht ebenfalls als „vergeben" da — neue Drop-Stücke erst mit dem Einschalten hochladen (oder ein Feld je Stück einführen, braucht Freigabe). Umgekehrt bekommen mit `VERKAUF_AKTIV=1` **alle** aktiven Stücke wieder Preis und Warenkorb — die vergebenen Stücke vorher im Admin auf inaktiv setzen (Checkliste in `80-AUFGABEN.md`). **Alte Slugs:** Migration `0022` nimmt einen angehängten Vermerk „(Sold)", „Sold", „Sold out", „Verkauft", „Ausverkauft" aus `name`, `seo_titel`, `beschreibung`, `seo_beschreibung` und bildet einen Slug auf `-sold`/`-verkauft`/`-ausverkauft` neu; `produkt_detail_slug` leitet eine solche alte Adresse per 301 auf das Stück ohne Vermerk um (`alter_verkaufsslug` in `views/shop.py`, ohne Register alter Slugs). Ein Vermerk mitten im Text bleibt stehen. **Kaufweg-Beiträge:** `wissen_beitrag()` leitet `nur_mit_verkauf`-Beiträge ohne Verkauf mit 302 auf `/wissen/`, die Übersicht listet sie nicht; in `_basis.py` fallen sie über `ohne_kaufweg()` aus `OEFFENTLICHE_SEITEN`, `INHALTSSEITEN`, `FAQ_SEITEN` und `MINDESTWOERTER`, die Designwache erfasst sie mit `VERKAUF_AKTIV=True`.

## Offen

Stand 01.10.2026, gegen Code und Live-Seite geprüft. Erledigte Merge-Aufgaben früherer Fassungen sind entfernt (alle Zweige sind in `main`); der Verlauf steht in [80-AUFGABEN.md](80-AUFGABEN.md) „Erledigt“ und im `LOGBUCH.md`.

| Punkt | Beleg | Regel |
|---|---|---|
| Fremdskripte selbst ausliefern: Alpine.js und `@alpinejs/intersect` (nur auf Seiten mit altem Markup) und Chart.js im Admin-Panel kommen von `cdn.jsdelivr.net` (GSAP und Three.js sind seit dem Umbau vom 19.09.2026 nicht mehr eingebunden) | CSP-Kopfzeile live nennt `https://cdn.jsdelivr.net` (01.10.2026); `admin/werbung_list.html:365` lädt Chart.js ohne `integrity`; im Projekt liegt keine `.js`-Datei unter `shop1/static/` | PF31, SI17 |
| `'unsafe-eval'` aus `script-src` (Alpine-CSP-Fassung) und `'unsafe-inline'` aus `style-src` | beides steht in der CSP-Kopfzeile live (01.10.2026); nur mit Browserprüfung machbar | SI09 |
| `Permissions-Policy`-Kopfzeile fehlt | in den Antwortköpfen von `/` nicht vorhanden (01.10.2026) | SI07, VL04 |
| Gemeinsamer Drosselzähler über alle Gunicorn-Worker (Redis oder Datenbank-Cache) und eine Mail-Obergrenze je Tag | Zähler und Merker liegen im `LocMemCache` je Prozess | FO09, FO03 |
| `INDEXNOW_KEY` in Railway setzen oder bewusst aus lassen | `/indexnow-schluessel.txt` antwortet live mit 404 (01.10.2026), also ist IndexNow aus | PJ13 |
| `CustomUserCreationForm.save()` setzt `land` bei leerem Feld auf `''` statt „Deutschland“ | `shop1/forms.py:123` (`.get('land', 'Deutschland')` greift nur bei fehlendem Schlüssel) | — |
| `STRIPE_*`-Variablen in Railway entfernen | Railway-Inventur 26.09.2026: vorhanden, kein Code liest sie; Namen nicht einzeln dokumentiert | — |
| Eigene Datenbank für Luviq statt der geteilten Supabase-Datenbank „A“ | Railway-Inventur 26.09.2026, Befund K1 (hoch): dieselben Tabellen `auth_user`, `django_migrations`, `django_session` wie weitere betreute Seiten; Plan: `Webagentur Scherzinger\Betrieb-Railway\TRENNUNGSPLAN.md` | — |
| Geteilte Zugangswerte (PayPal, SMTP-Zugang, Admin-Passwort) mit stillgelegten Diensten trennen | Railway-Inventur 26.09.2026, Befund K7 (hoch) | — |
| `pruefe_mail` spricht in Meldungen noch von Brevo (prüft den SMTP-Weg aber richtig) | `10-TECHNIK.md` „E-Mail-Versand“ (27.09.2026) | MW15 |
| Einen Kontaktanfrage-Eingang live abschicken und die Mail samt „Antworten“-Knopf im Postfach der Betreiberin prüfen; Bildschirmleserprobe der Fehlermeldung auf `/kontakt/` (`BF24`) | in keiner Doku als erledigt belegt; nur die Testsuite hat es gesehen | MW21, BF24 |
| Nach dem Einschalten des Verkaufs: `/payment/<id>/` mit offener Browserkonsole (CSP scharf, PayPal-SDK) und Sandbox-Testkauf | erst relevant, wenn `VERKAUF_AKTIV` gesetzt wird | SI09 |
| Module ohne eigenen Test (Rest der ursprünglich zehn gemeldeten) | Stand 18.09.2026 (Paket 306): sieben direkt eingeführt, Rest nicht neu gezählt | PJ06 |
| Admin-Aktionen, die auf GET reagieren (`comment_delete`, `admin_produkt_toggle`, `admin_resend_newsletter`, `admin_newsletter_reset`) und doppelte Registrierung derselben Adresse | `CLAUDE.md` „Sicherheit“: bewusst dokumentierte Lücken, warten auf die Freigabe der Betreiberin | — |
