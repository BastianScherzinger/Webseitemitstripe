---
bereich: technik
titel: Technik, Hosting und Aufbau
stand: 2026-09-12
status: teilweise
fortschritt: 74
zusammenfassung: Stack läuft stabil. Seit den Merges 0c18ea7, 4ec540b, 1a5f36b, c522ff9, 0d5500b und 43f25c3 liegen auf main die scharf gestellte CSP, die Nonce im script-src statt 'unsafe-inline' (Handler-Attribute durch data-Attribute ersetzt), die festgenagelten Paketfassungen samt requirements.lock (Django 5.2.17), die abgearbeiteten Audit-Funde, die Danke-Seite /kontakt/danke/ (never_cache), die Produktkarte als zwei Bausteine unter shop1/templates/shop1/teile/ (Falle: load wird an ein include nicht vererbt), integrity/crossorigin an den vier Fremdskripten und der zweite Prüfbefehl pruefe_links; main = 69c1f78, ein Doku-Commit vor origin/main (43f25c3). Im Zweig sofort/2026-09-12-mw15-und-2-weitere (drei Commits, nicht gemergt) steht als dritter Prüfbefehl pruefe_mail — Einstellungen beider Mailwege, Anmeldung an Brevo-API (/v3/account) und SMTP-Relay, Testmail mit --an, Geheimnisse nur als „gesetzt (n Zeichen)"; wie pruefe_links bewusst nicht an start.sh angeschlossen und gegen die echten Zugangsdaten noch nie gelaufen. 243 Testfunktionen im Zweig. Offen bleiben der Merge, Bezahlseite und Ersatzskripte mit Browserkonsole, ein echter pruefe_mail-Lauf, die zwei Chart.js-Einbindungen des Admin-Panels ohne integrity, 'unsafe-eval' für Alpine.js, der erste CI-Lauf mit 5.2.17, CANONICAL_HOST in Railway, runtime.txt/railway.json und die Permissions-Policy.
offen: 13
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
| Framework | Django `>=5.0,<6.1` auf main; **Zweig 11.09.: `Django==5.2.17`**, jede Abhängigkeit mit `==`, Unterabhängigkeiten in `requirements.lock` (per `--constraint` aus `requirements.txt` eingebunden). Eine App `shop1`, Projektkonfiguration `mainweb/` | `requirements.txt`, `requirements.lock`, `CLAUDE.md` |
| Python | Container `python:3.11-slim`, CI Python 3.12, Entwicklungsrechner Python 3.14. Unter der Spanne auf main bekam der Container Django 5.2.x, der CI-Lauf 6.0.x. **Zweig 11.09.:** mit dem Nagel bauen Container und CI dieselbe Fassung 5.2.17 (laut PyPI Python 3.10–3.14). Der Entwicklungsrechner hatte am 11.09.2026 noch Django 6.0.5 — die Suite lief beim Bau damit, nicht mit 5.2.17; erster Nachweis ist der nächste CI-Lauf | `Dockerfile`, `requirements.txt`, `.github/workflows/pruefungen.yml`, `LOGBUCH.md` Paket 155 |
| Datenbank | PostgreSQL über `DATABASE_URL` (Railway), lokal SQLite; **zweite Datenbank `pystore`** über `PYSTORE_DATABASE_URL` | `mainweb/settings.py` |
| Server | Gunicorn; Zweig: `gthread`, 2 Worker × 4 Threads, Timeout 30 s, Worker-Erneuerung nach 1.000 Anfragen (main: Standardaufruf) | `start.sh` |
| Statische Dateien | WhiteNoise + `ManifestStaticFilesStorage` (Content-Hash im Dateinamen) | `DOCUMENTATION.md` §5 |
| Medien | Cloudinary (`django-cloudinary-storage`, `CLOUDINARY_URL`) | `DOCUMENTATION.md` §5 |
| Mail | Brevo — SMTP-Relay **und** HTTP-API (siehe Fallen) | `CLAUDE.md`, `shop1/utils.py` |
| Login-Schutz | django-axes: 10 Fehlversuche je Benutzername+IP, 1 h Sperre, eigenes Lockout-Template | `settings.py` (`AXES_*`) |
| Zahlung | PayPal (JS-SDK in `payment.html`, Capture in `views/checkout.py`) und Vorab-Überweisung (`BANK_IBAN`, `BANK_INHABER`) | `DOCUMENTATION.md` §3 |
| CSS | Tailwind-CLI aus `tailwind_input.css` nach `shop1/static/shop1/tailwind.css`; **kein `package.json`, kein npm-Build im Repo**; dazu `shop1/static/shop1/style.css` | `CLAUDE.md`, `tailwind.config.js` |
| JS | Alpine.js 3.14.8 + `@alpinejs/intersect` (base.html), GSAP 3.12.5 (Startseite), Three.js 0.158.0 (nur Desktop, ohne `prefers-reduced-motion`, nachgeladen) — alle von `cdn.jsdelivr.net`, **Zweig SI17: alle vier mit `integrity` (SHA-256 aus der jsDelivr-Dateiauskunft) und `crossorigin="anonymous"`; wer eine Fassung hochzieht, muss den Hash mitziehen, sonst lädt das Skript nicht mehr**. Alpine (Standardfassung) braucht `'unsafe-eval'` in der CSP. **Zweig SI09:** eigene Inline-Skripte nur mit `nonce="{{ csp_nonce }}"`, keine `on…`-Attribute mehr — deren Aufgaben übernimmt ein Skript im `<head>` von `base.html` über `data-bestaetigen`, `data-bei-fehler-ausblenden`, `data-auto-absenden`, `data-schrift-nachladen` | `templates/base.html`, `index.html` |
| Cache | `LocMemCache` (Zweig ausdrücklich: `LOCATION luviq`, `MAX_ENTRIES 300`); Werbeliste 60 s; Zweig: `sitemap.xml`/`llms.txt` 15 min | `settings.py`, `LOGBUCH.md` Schritt 33 |
| Zeitzone / Sprache | `Europe/Berlin`, `USE_TZ=True`, `de-de` | `settings.py` |

## Hosting und Deploy

| | |
|---|---|
| Railway | Projekt **`webseiten`** → Dienst **`Luviq-Luisa`**, Umgebung **`shop`**; Railway-Adresse `luviq-luisa-shop.up.railway.app` (antwortet 200, 02.09.2026) |
| Domain | `www.luviq-alsfeld.com`; Apex `luviq-alsfeld.com` zeigt auf denselben Dienst (eigenes Let's-Encrypt-Zertifikat, 200 ohne Weiterleitung — Stand 02.09.2026) |
| Deploy | Push auf `main` löst den Docker-Bau aus; kein Knopf nötig. Letzte Auslieferung 18.08.2026 (`645842b`, SUCCESS); Erfolgsquote 100 % (1 bewertbare Auslieferung, Messung 02.09.2026) |
| Container | `Dockerfile`: `python:3.11-slim`, `libpq-dev`/`gcc`, `pip install -r requirements.txt`, `CMD /app/start.sh`, Port 8000. **Zweig 11.09.:** kopiert `requirements.txt` **und** `requirements.lock` — ohne die Lockdatei bricht pip an der `--constraint`-Zeile ab |
| Push von diesem Rechner | `git -c credential.helper='!gh auth git-credential' push origin <zweig>` (Credential Manager ist auf diesem PC kaputt) |

**Startreihenfolge im Container (`start.sh`, Zweig):**

1. `migrate --noinput`
2. Superuser aus `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` anlegen oder abgleichen (`is_staff`, `is_superuser`, Passwort wird **bei jedem Start** neu gesetzt)
3. `loaddata initial_data.json` (optional, Fehler ignoriert)
4. `fix_pystore_schema` (eigener Befehl, behebt die `seite`-Spalte in `pystore`)
5. `collectstatic --noinput --clear`
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
| **Nur Zweig** | `CANONICAL_HOST`, `CSP_MODUS` (`scharf` · `report-only` · `aus`; Vorgabe im Zweig 11.09. `scharf`), `VISITOR_TRACKING`, `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT` |
| **Altlast in Railway** | `STRIPE_*` — aus einer frühen Planungsphase; kein Code im Projekt liest sie (Suche 02.09.2026 ohne Treffer). Entfernen, sobald jemand im Railway-Dienst nachgesehen hat, welche Namen dort genau stehen — sie sind nirgends dokumentiert. |

## Formular und Missbrauchsschutz

*Pflichtabschnitt nach [DOKU-STANDARD §3a](file:///C:/Users/basti/Desktop/pystore-overview/docs/DOKU-STANDARD.md).
Erhoben am 04.09.2026 aus dem Quelltext dieses Projekts — „ja" heisst gefunden,
nicht bewiesen. Anlass war eine Spam-Einsendung, die auf der Hauptseite mit
Spam-Score 0 durchkam und eine Mail auslöste.*

| Baustein | Was er verhindert | Stand |
|---|---|---|
| CSRF-Token | fremde Seiten schicken in fremdem Namen ab | ja |
| Honeypot | einfache Formular-Bots | **nein** |
| Zeitfalle (signierter Zeitstempel) | der POST ohne gerendertes Formular | **nein** |
| Inhalts-Score mit Schwelle | Werbetexte, fremde Schriften, Linklisten | **nein** |
| Adresse ohne `http://` erkannt | die Masche vom 04.09.2026 | **nein** |
| Fremde Domain mit eigenem Markennamen | Vertrauen erschleichen | **nein** |
| Rate-Limit je IP | Serien aus einer Quelle | ja |
| Erst speichern, dann mailen | verlorene Anfrage bei Mailausfall | ja |
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
`/kontakt/`. Ein späterer Zustellfehler im Thread von `send_brevo_email`
erreicht die Besucherin weiter nicht — die Danke-Seite erscheint trotzdem
(`EIG10` in [80-AUFGABEN.md](80-AUFGABEN.md)). An den Bausteinen der Tabelle
ändert das nichts.

## Prüfbefehle und Tests

| Befehl | Was | Stand |
|---|---|---|
| `python manage.py test shop1` | Testsuite in 14 Modulen, Laufzeit rund 2,5 Minuten; main: **218 Tests** (seit `4ec540b` mit den drei SI09-Tests in `test_einstellungen`), Zweig KV07: **224 Tests** (sechs neue in `test_formulare`), main seit `43f25c3` (PJ01): **230 Tests** (sechs neue in `test_einstellungen` zu `pruefe_links`), Zweig 12.09. MW15/GE15: **243 Testfunktionen** (acht neue in `test_einstellungen` zu `pruefe_mail`, fünf in `test_geo` zum `Article`-Knoten; `def test_` über `shop1/tests/` gezählt am 12.09.2026) | Zweig MW15/GE15 laut Commit grün |
| `python manage.py test shop1.tests.<modul>` | einzelnes Modul | Zweig |
| `python manage.py pruefe_seite [--streng]` | Prüfbefehl: Einstellungen, beide Datenbanken, aktive Produkte (Pflichtwerte, doppelte Slugs), jede Sitemap-Adresse 200 mit Titel, Beschreibung 110–175, canonical, robots, JSON-LD, Schutzkopfzeilen samt CSP; hinterlässt keine Spuren (`VISITOR_TRACKING` aus, zurückgerollte Transaktion) | Zweig |
| `python manage.py pruefe_links [--streng]` | Prüfbefehl (Zweig 12.09., PJ01): liest `/`, jede Sitemap- und jede llms.txt-Adresse und ruft **jeden `<a href>` darin** ab — tote eigene Adressen sind Fehler, Weiterleitungen Warnungen (ausser auf `LOGIN_URL`), fremde Ziele werden nur auf `https` geprüft, nicht abgerufen; verändernde Pfade (Warenkorb, Abmeldung, Werbeklick, Kommentar) stehen in `KEINE_PRUEFUNG`. Gleiche Vorsorge wie oben: kein Besuchsprotokoll, zurückgerollte Transaktion | seit `43f25c3` auf `main` |
| `python manage.py pruefe_mail [--ohne-verbindung] [--streng] [--an ADRESSE]` | Prüfbefehl (Zweig 12.09., MW15): **beide** Mailwege. Zeigt die Einstellungen (Backend, `DEFAULT_FROM_EMAIL`, `ADMIN_EMAIL`, `SITE_URL`, Host/Port/Verschlüsselung, Benutzer — von Schlüsseln und Passwörtern nur „gesetzt (n Zeichen)", die Ausgabe darf in ein Container-Log) und versucht die **Anmeldung**: Brevo-API-Schlüssel gegen die Kontoauskunft `/v3/account` (Lesezugriff, verschickt nichts), SMTP über `get_connection().open()`. Console-Backend ist im Entwicklungsmodus eine Warnung und im Betrieb ein Fehler; leerer `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` ein Fehler; fehlender `BREVO_API_KEY` und der Vorgabeabsender `noreply@luviq-shop.de` je eine Warnung. `--an ADRESSE` schickt eine Testmail **synchron und ohne `fail_silently`**, `--ohne-verbindung` lässt jeden Netzzugriff aus. Gegen die echten Zugangsdaten dieses Dienstes noch nie gelaufen | Zweig |
| `python manage.py check --deploy` | Django-Prüfung | beide |
| `python manage.py fix_pystore_schema` | `seite`-Spalte in `pystore` | beide |
| `python manage.py makemigrations shop1` | einzige App; 18 Migrationen (Zweig, `0018` legt die pystore-Tabellen auch ohne PostgreSQL an) | |

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
│   ├── models.py       UserProfile, Subscriber, Produkt, Cart, CartItem, Order, OrderItem, Werbung, WerbungStat, VisitorLog, PageVisit, Comment, PyStoreVisitorLog
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

## Fallen

1. **Einziger echter Shop — Änderungen an Warenkorb, Checkout, Zahlung nur mit Sandbox-Test.** Anleitung [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md): Sandbox-Business- und -Personal-Konto, Sandbox-Client-ID in `PAYPAL_CLIENT_ID`, Testkauf, Bestellung springt auf „bezahlt", Artikel wird deaktiviert (1-of-1). Vor Live-Schaltung Live-App und Live-Client-ID. Die Tests `test_warenkorb`, `test_zahlung`, `test_konto` (Zweig) prüfen die Pfade ohne PayPal-Aufruf.
2. **Zwei Datenbanken.** `default` = Shop-Daten, `pystore` = seitenübergreifende Werbe-/Besucherdaten (`Werbung`, `WerbungStat`, `VisitorLog`). `shop1/routers.py::WerbungRouter` zwingt sie nach `pystore` und **blockt ihre Migrationen dort** (`PYSTORE_IS_EXTERNAL`), weil das PyStore-Projekt diese Tabellen verwaltet. Ohne `PYSTORE_DATABASE_URL` ist `pystore` eine **Kopie** von `default` — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der Test-Runner die Testdatenbanken. `PyStoreVisitorLog` ist ein `managed=False`-Proxy auf `shop1_visitorlog` in `pystore` (`db_column='site'`). Migrationen `0013`/`0014` legen die Tabellen nur auf PostgreSQL an, `0018` auf allen anderen Backends.
3. **Views sind ein Package, aber zentral re-exportiert.** `shop1/urls.py` macht nur `from . import views` — **jede neue View muss in `shop1/views/__init__.py` re-exportiert werden**, sonst ist sie unsichtbar. Helfer liegen in `views/_helpers.py`.
4. **Zwei E-Mail-Wege.** (1) Django-`send_mail` über SMTP (Brevo-Relay, `USE_SMTP_EMAIL` oder `DEBUG=False`; sonst Console-Backend). (2) `shop1/utils.py::send_brevo_email()` — direkter HTTP-Aufruf an die Brevo-API in einem Thread, weil Railway SMTP-Ports blockt. **Bestell- und Benachrichtigungsmails gehen über Weg 2.** Ein Mailausfall lässt die Bestellung bestehen (Test in `test_zahlung`). **Beide Wege fallen still aus** — der API-Weg protokolliert einen Fehlschlag nur ins Log (`utils.py:41`, `:59`), während die Bestellung als aufgegeben gilt; ein geblockter SMTP-Port heisst, dass niemand sein Passwort zurücksetzen kann. Seit dem 12.09.2026 (Zweig, `MW15`) sieht sich `python manage.py pruefe_mail` genau das an: Einstellungen und Anmeldung beider Wege, auf Wunsch eine Testmail. Er hängt **nicht** an `start.sh`.
5. **Denormalisierte Bestelldaten.** `CartItem` und `OrderItem` speichern Name und Preis als eigene Felder, nicht als Fremdschlüssel — **Absicht**, damit geänderte oder gelöschte Produkte alte Bestellungen nicht verändern. Erhalten.
6. **`PageVisitMiddleware`** läuft nach jeder Antwort. Geo-IP (`ip-api.com`) im festen `ThreadPoolExecutor` (4 Plätze; voll → kein Lookup), **die Datenbankschreibvorgänge laufen synchron im Request** und verzögern die Auslieferung. Dedup: `PageVisit` einmal je Session und Tag, `VisitorLog` einmal je Pfad alle 5 Minuten. **Keine Admin-Mail pro Besuch mehr** (seit `e58775a`, Mail-Flut durch Bots). Neue externe Aufrufe gehören in den Pool, nicht in einen Thread je Anfrage. Abschalter `VISITOR_TRACKING` (Zweig).
7. **Zwei Admins.** Eigenes Panel `/shop-admin/…` (`admin_views.py`, `admin_required`: `is_superuser` **oder** Benutzername gleich `ADMIN_USERNAME`); regulärer Django-Admin hinter `ADMIN_URL` (Schutz vor Scannern). **Zweig 11.09.:** dort ist zusätzlich `Subscriber` registriert (Liste, Suche nach Adresse, Filter nach Datum, `erstellt_am` schreibgeschützt), damit eine Auskunft oder Löschung nach Art. 15/17 DSGVO ohne Datenbankzugriff geht; das Panel bleibt unverändert. Bekannte, dokumentierte Lücken (Tests halten den Ist-Zustand fest): `comment_delete`, `admin_produkt_toggle`, `admin_resend_newsletter`, `admin_newsletter_reset` reagieren auf GET; eine E-Mail-Adresse kann sich zweimal registrieren — **wartet auf Freigabe der Betreiberin**.
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
18. **Paketfassungen ändern (Zweig 11.09.):** `requirements.txt` und `requirements.lock` gehören zusammen. Wer eine Fassung ändert, schreibt die Lockdatei neu — frische Umgebung, `pip install -r requirements.txt`, Testsuite grün, dann die Fassungen aus `pip freeze` eintragen (Kopf von `requirements.lock`). Das Code-Audit des Werkzeugs liest `.lock`-Dateien nicht und meldet deshalb weiter „kein Lockfile".

## Offen

| Punkt | Beleg | Regel |
|---|---|---|
| Zweig `sofort/2026-09-12-mw15-und-2-weitere` nach `main` mergen und pushen (`sofort/2026-09-12-si17-und-2-weitere` ist mit `43f25c3` gemergt und in `origin/main`; `main` = `69c1f78`, ein Doku-Commit vor `origin/main`); danach einmal das Kontaktformular live abschicken | `4fd7776`, `be550e3`, `bb6fee1` — drei Commits vor `main`; `MW15` legt nur eine neue Datei unter `management/commands/` an, `GE15` schreibt allein in den `<head>` | MW15, GE15, KV07 |
| `python manage.py pruefe_mail` einmal mit den echten Zugangsdaten fahren (Railway-Konsole oder lokal mit gesetztem `BREVO_API_KEY`/`EMAIL_HOST_*`) | die acht Tests laufen alle mit `--ohne-verbindung`, die beiden Anmeldeprüfungen gegen ein vorgetäuschtes Gegenüber — ob Brevo und das Relay diese Zugangsdaten annehmen, ist damit nicht belegt | MW15 |
| `CANONICAL_HOST` in Railway setzen | live 02.09.2026: Apex antwortet 200 ohne 301; die Vorgabe von `CANONICAL_HOST` ist auch im Zweig SI09 leer (`mainweb/settings.py:45`) | TS11 |
| Nach dem Push: ersten CI-Lauf mit Django 5.2.17 abwarten; lokal `pip install -r requirements.txt` | die Suite lief beim Bau mit Django 6.0.5 (`pip install`/`docker build` gesperrt, `LOGBUCH.md` Paket 155) | PJ11 |
| Nach dem Deploy mit offener Browserkonsole ansehen: `/payment/<id>/`, dazu mit dem Zweig SI09 Löschrückfrage im Profil, „Reset" in der Panel-Statistik, Bestellfilter, Kampagnenknöpfe, Nachladen der Schriften | CSP scharf, Deckung nur durch Tests belegt; das Verhalten der Ersatzskripte ist ungeprüft (`28d1ca3`) | SI08, SI09 |
| `'unsafe-eval'` aus `script-src` (CSP-Fassung von Alpine, jeder Ausdruck als registrierte Komponente), `'unsafe-inline'` aus `style-src` | laut `LOGBUCH.md` Paket 164 224 Treffer auf Alpine-Attribute in 19 Vorlagen; nur mit Browser prüfbar | SI09 |
| `runtime.txt`/`railway.json` | fehlen; `==` und Lockfile im Zweig 11.09. erledigt (`51cbf74`) | VL02 |
| Permissions-Policy-Kopfzeile | live: 4 von 7 Schutzköpfen; die CSP ist im Zweig 11.09. als echte Kopfzeile erledigt (`9a3226f`) | SI07, VL04 |
| **Rest von `SI17`:** die zwei Chart.js-Einbindungen des Admin-Panels ohne `integrity` | `admin/werbung_list.html:365` lädt `chart.js@4.4.0/dist/chart.umd.min.js` — eine Datei, die jsDelivr beim Abruf selbst erzeugt und für die es keinen veröffentlichten Hash gibt; `admin/stats.html:246` lädt `chart.js` ganz ohne Fassung. Beide abzusichern hiesse, die Einbindung auf eine andere Datei umzustellen. Die vier Fremdskripte der öffentlichen Seiten sind seit `680a641` abgesichert | SI17 |
| Gestaltete 404-Seite (kein `404.html` im Projekt) | live: 13 Wörter, ohne Navigation | BT05, TS20 |
| Fehler-Monitoring (Sentry o. ä.) — **der zweite und der dritte Prüfbefehl sind seit dem 12.09.2026 gebaut** (`pruefe_links`, `11acccc`, seit `43f25c3` auf `main`; `pruefe_mail`, `4fd7776`, im Zweig), ein CI-Lauf bei jedem Push steht in `.github/workflows/pruefungen.yml` | 3 von 7 QS-Bausteinen (Messung 02.09.2026) | VL19, PJ01, MW15 |
| `STRIPE_*`-Variablen in Railway entfernen | nicht dokumentiert, welche Namen genau | — |
| Zehn Module ohne eigenen Test (`forms.py`, `signals.py`, `views/_helpers.py`, `views/auth.py`, `views/cart.py`, `views/checkout.py`, `views/gaestebuch.py`, `views/shop.py`, `pruefe_seite.py`, `tiktok stream/streamtest.py`) — die View-Module sind über Seiten-, Konto- und Zahlungstests indirekt abgedeckt, das Audit zählt nur direkte Importe. Die beiden jüngeren Prüfbefehle `pruefe_links` und `pruefe_mail` haben eigene Testklassen in `test_einstellungen` | PJ03 | PJ03 |
