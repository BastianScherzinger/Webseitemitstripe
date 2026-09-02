---
bereich: technik
titel: Technik, Hosting und Aufbau
stand: 2026-09-02
status: teilweise
fortschritt: 75
zusammenfassung: Stack läuft stabil; im Zweig warten Testsuite (215 Tests), Prüfbefehl, CSP (Report-Only) und Canonical-Host; offen bleiben ALLOWED_HOSTS='*', ungepinnte Abhängigkeiten und der Python-Versionsunterschied.
offen: 7
quellen: CLAUDE.md, DOCUMENTATION.md, LOGBUCH.md, paypal_sandbox_tutorial.md, start.sh, Dockerfile, requirements.txt
---

# Technik — Luviq Universe

Detailquelle bleibt [`../CLAUDE.md`](../CLAUDE.md) (Architektur, Fallstricke) und
[`../DOCUMENTATION.md`](../DOCUMENTATION.md) (Modelle, E-Mail-Flows, Admin, Sicherheit).

> **Der Ordner steht auf dem Zweig `cockpit/2026-09-01-verbesserung-4`, live läuft `main`.**
> Wo unten „Zweig" steht, ist es noch nicht ausgeliefert. Der Unterschied ist in
> [90-NOTIZEN.md](90-NOTIZEN.md) aufgeschlüsselt.

## Stack

| Baustein | Was | Quelle |
|---|---|---|
| Framework | Django `>=5.0,<6.1` (Zweig; auf main `<7.0`), eine App `shop1`, Projektkonfiguration `mainweb/` | `requirements.txt`, `CLAUDE.md` |
| Python | Container `python:3.11-slim` → pip installiert Django 5.2; Entwicklungsrechner Python 3.14 → Django 6.0. **Die Testsuite prüft eine andere Hauptversion als der Betrieb** (ungelöst, Kommentar in `requirements.txt`) | `Dockerfile`, `requirements.txt` |
| Datenbank | PostgreSQL über `DATABASE_URL` (Railway), lokal SQLite; **zweite Datenbank `pystore`** über `PYSTORE_DATABASE_URL` | `mainweb/settings.py` |
| Server | Gunicorn; Zweig: `gthread`, 2 Worker × 4 Threads, Timeout 30 s, Worker-Erneuerung nach 1.000 Anfragen (main: Standardaufruf) | `start.sh` |
| Statische Dateien | WhiteNoise + `ManifestStaticFilesStorage` (Content-Hash im Dateinamen) | `DOCUMENTATION.md` §5 |
| Medien | Cloudinary (`django-cloudinary-storage`, `CLOUDINARY_URL`) | `DOCUMENTATION.md` §5 |
| Mail | Brevo — SMTP-Relay **und** HTTP-API (siehe Fallen) | `CLAUDE.md`, `shop1/utils.py` |
| Login-Schutz | django-axes: 10 Fehlversuche je Benutzername+IP, 1 h Sperre, eigenes Lockout-Template | `settings.py` (`AXES_*`) |
| Zahlung | PayPal (JS-SDK in `payment.html`, Capture in `views/checkout.py`) und Vorab-Überweisung (`BANK_IBAN`, `BANK_INHABER`) | `DOCUMENTATION.md` §3 |
| CSS | Tailwind-CLI aus `tailwind_input.css` nach `shop1/static/shop1/tailwind.css`; **kein `package.json`, kein npm-Build im Repo**; dazu `shop1/static/shop1/style.css` | `CLAUDE.md`, `tailwind.config.js` |
| JS | Alpine.js 3.14.8 + `@alpinejs/intersect` (base.html), GSAP 3.12.5 (Startseite), Three.js 0.158.0 (nur Desktop, ohne `prefers-reduced-motion`, nachgeladen) — alle von `cdn.jsdelivr.net`, ohne `integrity` | `templates/base.html`, `index.html` |
| Cache | `LocMemCache` (Zweig ausdrücklich: `LOCATION luviq`, `MAX_ENTRIES 300`); Werbeliste 60 s; Zweig: `sitemap.xml`/`llms.txt` 15 min | `settings.py`, `LOGBUCH.md` Schritt 33 |
| Zeitzone / Sprache | `Europe/Berlin`, `USE_TZ=True`, `de-de` | `settings.py` |

## Hosting und Deploy

| | |
|---|---|
| Railway | Projekt **`webseiten`** → Dienst **`Luviq-Luisa`**, Umgebung **`shop`**; Railway-Adresse `luviq-luisa-shop.up.railway.app` (antwortet 200, 02.09.2026) |
| Domain | `www.luviq-alsfeld.com`; Apex `luviq-alsfeld.com` zeigt auf denselben Dienst (eigenes Let's-Encrypt-Zertifikat, 200 ohne Weiterleitung — Stand 02.09.2026) |
| Deploy | Push auf `main` löst den Docker-Bau aus; kein Knopf nötig. Letzte Auslieferung 18.08.2026 (`645842b`, SUCCESS); Erfolgsquote 100 % (1 bewertbare Auslieferung, Messung 02.09.2026) |
| Container | `Dockerfile`: `python:3.11-slim`, `libpq-dev`/`gcc`, `pip install -r requirements.txt`, `CMD /app/start.sh`, Port 8000 |
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

**Nach dem Merge des Zweigs in Railway zu setzen:** `CANONICAL_HOST=www.luviq-alsfeld.com` (sonst bleibt die 301 für den Apex wirkungslos). Optional: `CSP_MODUS` (Vorgabe `report-only`), `VISITOR_TRACKING` (Vorgabe an), `GUNICORN_*`.

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
| **Nur Zweig** | `CANONICAL_HOST`, `CSP_MODUS` (`report-only` · `scharf` · `aus`), `VISITOR_TRACKING`, `GUNICORN_WORKERS`, `GUNICORN_THREADS`, `GUNICORN_TIMEOUT` |
| **Altlast in Railway** | `STRIPE_*` — aus einer frühen Planungsphase; kein Code im Projekt liest sie (Suche 02.09.2026 ohne Treffer). Entfernen, sobald jemand im Railway-Dienst nachgesehen hat, welche Namen dort genau stehen — sie sind nirgends dokumentiert. |

## Prüfbefehle und Tests

| Befehl | Was | Stand |
|---|---|---|
| `python manage.py test shop1` | Testsuite; Zweig: **215 Tests in 14 Modulen**, Laufzeit rund 2,5 Minuten; main: `shop1/tests.py` mit 3 Zeilen, praktisch keine Tests | Zweig grün (`511ffe5`) |
| `python manage.py test shop1.tests.<modul>` | einzelnes Modul | Zweig |
| `python manage.py pruefe_seite [--streng]` | Prüfbefehl: Einstellungen, beide Datenbanken, aktive Produkte (Pflichtwerte, doppelte Slugs), jede Sitemap-Adresse 200 mit Titel, Beschreibung 110–175, canonical, robots, JSON-LD, Schutzkopfzeilen samt CSP; hinterlässt keine Spuren (`VISITOR_TRACKING` aus, zurückgerollte Transaktion) | Zweig |
| `python manage.py check --deploy` | Django-Prüfung | beide |
| `python manage.py fix_pystore_schema` | `seite`-Spalte in `pystore` | beide |
| `python manage.py makemigrations shop1` | einzige App; 18 Migrationen (Zweig, `0018` legt die pystore-Tabellen auch ohne PostgreSQL an) | |

**Testmodule (Zweig):** `test_seiten` (14), `test_seo` (31), `test_geo` (20), `test_inhalt` (15), `test_formulare` (10), `test_daten` (22), `test_einstellungen` (42), `test_barrierefreiheit` (11), `test_ladezeit` (9), `test_aufbau` (2, Designwache), `test_warenkorb` (8), `test_zahlung` (11), `test_konto` (10), `test_zugriffsschutz` (10); dazu `_basis.py` (Basisklasse `LuviqTestCase`) und `_aufbau.py` (Fingerabdruck) mit `aufbau_referenz.json` (5.148 Zeilen). Zahlen: `def test_` je Datei, 02.09.2026.

**Drei Regeln für neue Tests** (`CLAUDE.md`): `secure=True` ist Pflicht (sonst prüft man nur die 301 der SSL-Weiterleitung) → `self.hole()` / `self.sende()`; `databases = {'default', 'pystore'}` (die Besuchs-Middleware schreibt bei jeder Antwort); der Cache wird vor jedem Test geleert (`sitemap.xml`/`llms.txt` liegen 15 min im LocMemCache).

**Was fehlt (Messung 02.09.2026, VL19, PJ01):** ein zweiter Prüfbefehl (Links, Konsistenz), ein CI-Lauf bei jedem Push, Fehler-Monitoring (Sentry o. ä.). Kein Test kann ein vergessenes Nachziehen des Registers `seiten_stand.py` erzwingen.

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
│   ├── context_processors.py, signals.py, forms.py, utils.py (send_brevo_email)
│   ├── management/commands/  fix_pystore_schema.py, pruefe_seite.py (Zweig)
│   ├── tests/          14 Module (Zweig)
│   ├── templates/shop1/  Seiten, legal/, wissen/ (Zweig), admin/
│   └── static/shop1/   style.css, tailwind.css, images/ (Zweig: WebP in mehreren Breiten, flavicon.ico)
├── templates/base.html Navigation, Fusszeile, JSON-LD-Graph, Schriften, Alpine
├── start.sh · Dockerfile · requirements.txt · tailwind.config.js · tailwind_input.css
├── CLAUDE.md · DOCUMENTATION.md · GOOGLE_SEO_GUIDE.md · LOGBUCH.md · paypal_sandbox_tutorial.md
└── projekt1/ · tiktok stream/   unversionierte Altablagen, NICHT Teil der App (in .gitignore)
```

Code-Audit (Messung 02.09.2026, lokaler Ordner = Zweig): 114 Dateien, 23.859 Zeilen (53 Python, 45 Templates, 6 Konfig, 5 Doku, 3 CSS, 1 JS, 1 Skript); 115 Befunde (2 kritisch, 36 wichtig, 77 Hinweise), 71 Dateien ohne Befund, Note 0,952; 10 Module ohne Test; 4 „verwaiste" Templates (`lockout.html` ist über `AXES_LOCKOUT_TEMPLATE` in Gebrauch, die drei `wissen/*.html` über das Register — Fehlalarme des Audits). Die dichtesten Befunde liegen in `tiktok stream/` (Altablage, 13 + 11) und `shop1/admin_views.py` (8).

## Fallen

1. **Einziger echter Shop — Änderungen an Warenkorb, Checkout, Zahlung nur mit Sandbox-Test.** Anleitung [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md): Sandbox-Business- und -Personal-Konto, Sandbox-Client-ID in `PAYPAL_CLIENT_ID`, Testkauf, Bestellung springt auf „bezahlt", Artikel wird deaktiviert (1-of-1). Vor Live-Schaltung Live-App und Live-Client-ID. Die Tests `test_warenkorb`, `test_zahlung`, `test_konto` (Zweig) prüfen die Pfade ohne PayPal-Aufruf.
2. **Zwei Datenbanken.** `default` = Shop-Daten, `pystore` = seitenübergreifende Werbe-/Besucherdaten (`Werbung`, `WerbungStat`, `VisitorLog`). `shop1/routers.py::WerbungRouter` zwingt sie nach `pystore` und **blockt ihre Migrationen dort** (`PYSTORE_IS_EXTERNAL`), weil das PyStore-Projekt diese Tabellen verwaltet. Ohne `PYSTORE_DATABASE_URL` ist `pystore` eine **Kopie** von `default` — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der Test-Runner die Testdatenbanken. `PyStoreVisitorLog` ist ein `managed=False`-Proxy auf `shop1_visitorlog` in `pystore` (`db_column='site'`). Migrationen `0013`/`0014` legen die Tabellen nur auf PostgreSQL an, `0018` auf allen anderen Backends.
3. **Views sind ein Package, aber zentral re-exportiert.** `shop1/urls.py` macht nur `from . import views` — **jede neue View muss in `shop1/views/__init__.py` re-exportiert werden**, sonst ist sie unsichtbar. Helfer liegen in `views/_helpers.py`.
4. **Zwei E-Mail-Wege.** (1) Django-`send_mail` über SMTP (Brevo-Relay, `USE_SMTP_EMAIL` oder `DEBUG=False`; sonst Console-Backend). (2) `shop1/utils.py::send_brevo_email()` — direkter HTTP-Aufruf an die Brevo-API in einem Thread, weil Railway SMTP-Ports blockt. **Bestell- und Benachrichtigungsmails gehen über Weg 2.** Ein Mailausfall lässt die Bestellung bestehen (Test in `test_zahlung`).
5. **Denormalisierte Bestelldaten.** `CartItem` und `OrderItem` speichern Name und Preis als eigene Felder, nicht als Fremdschlüssel — **Absicht**, damit geänderte oder gelöschte Produkte alte Bestellungen nicht verändern. Erhalten.
6. **`PageVisitMiddleware`** läuft nach jeder Antwort. Geo-IP (`ip-api.com`) im festen `ThreadPoolExecutor` (4 Plätze; voll → kein Lookup), **die Datenbankschreibvorgänge laufen synchron im Request** und verzögern die Auslieferung. Dedup: `PageVisit` einmal je Session und Tag, `VisitorLog` einmal je Pfad alle 5 Minuten. **Keine Admin-Mail pro Besuch mehr** (seit `e58775a`, Mail-Flut durch Bots). Neue externe Aufrufe gehören in den Pool, nicht in einen Thread je Anfrage. Abschalter `VISITOR_TRACKING` (Zweig).
7. **Zwei Admins.** Eigenes Panel `/shop-admin/…` (`admin_views.py`, `admin_required`: `is_superuser` **oder** Benutzername gleich `ADMIN_USERNAME`); regulärer Django-Admin hinter `ADMIN_URL` (Schutz vor Scannern). Bekannte, dokumentierte Lücken (Tests halten den Ist-Zustand fest): `comment_delete`, `admin_produkt_toggle`, `admin_resend_newsletter`, `admin_newsletter_reset` reagieren auf GET; eine E-Mail-Adresse kann sich zweimal registrieren — **wartet auf Freigabe der Betreiberin**.
8. **Werbe-Impressionen** werden nur in `startseite()` gezählt, nicht im Kontextprozessor (war ein Bug).
9. **Designwache** (`test_aufbau`, `aufbau_referenz.json`): jede Änderung an Tag-Reihenfolge, `id`/`class`, Überschriften oder Elementzahlen einer öffentlichen Seite macht die Suite rot. Referenz für neue Seiten **gezielt ergänzen**, nie neu erzeugen. Siehe [20-DESIGN.md](20-DESIGN.md).
10. **Template-Blöcke:** eine Bedingung **um** einen `{% block %}` in einer erbenden Datei wirkt nicht — die Bedingung gehört **in** den Block (`produkt_detail.html`, `meta_robots` der Wissensseiten).
11. **Zeitzone in Tests:** `.date()` eines UTC-Zeitstempels ist zwischen 22:00 und 24:00 UTC falsch → `timezone.localtime()` (Auflage 4, `270c5f9`).
12. **CSP vor dem Scharfschalten prüfen:** `/`, `/produkte/`, `/gaestebuch/`, `/checkout/`, `/payment/<id>/` und das Admin-Panel mit offener Browserkonsole; null `[Report Only]`-Meldungen sind die Bedingung. `script-src`/`style-src` bleiben wegen Inline-Code offen (`'unsafe-inline'`, `'unsafe-eval'`).
13. **`ALLOWED_HOSTS = ['*']`** bei `DEBUG=True` (`settings.py` Zeile 59); im Betrieb `['localhost', '127.0.0.1', '.up.railway.app'] + ALLOWED_HOSTS_EXTRA` (+ `CANONICAL_HOST` im Zweig). Der Code-Audit meldet die Zeile als kritisch (K02); `DEBUG` darf in Railway nie auf `True` stehen.
14. **`db.sqlite3`, `staticfiles/`, `media/`, `.env`, `*.log`** liegen im Ordner, sind aber in `.gitignore`. `runserver.err.log` vom 03.07.2026 ebenfalls.
15. **Der Superuser wird bei jedem Containerstart mit `ADMIN_PASSWORD` überschrieben** — ein im Panel geändertes Passwort dieses Kontos hält nur bis zum nächsten Deploy.

## Offen

| Punkt | Beleg | Regel |
|---|---|---|
| Zweig nach `main` mergen, `CANONICAL_HOST` in Railway setzen | live 02.09.2026: Apex antwortet 200 ohne 301 | TS11 |
| `requirements.txt` mit `==` festnageln, Lockfile beilegen; `runtime.txt`/`railway.json` | 11 von 11 ohne feste Fassung (Zweig: nur Obergrenzen) | PJ11, VL02 |
| Python-Fassung angleichen (Basis-Image `python:3.12-slim` **oder** `Django<6.0`) — braucht einen Build zum Nachweis | Kommentar `requirements.txt`; Logbuch „Schritt 38 mit Docker" verschoben | — |
| `ALLOWED_HOSTS='*'`-Zweig im Debug-Fall entschärfen; `shop1/middleware.py:218` verschluckte Ausnahme | Code-Audit K02, P02 | PJ05, VL03 |
| Permissions-Policy und CSP als echte Kopfzeile (`CSP_MODUS=scharf` nach Konsolenprüfung) | live: 4 von 7 Schutzköpfen | SI07, SI08, VL04 |
| `integrity`/`crossorigin` an den drei jsdelivr-Skripten | 3 von 3 ohne | SI17 |
| Gestaltete 404-Seite (kein `404.html` im Projekt) | live: 13 Wörter, ohne Navigation | BT05, TS20 |
| CI-Lauf bei jedem Push, Fehler-Monitoring, zweiter Prüfbefehl | 3 von 7 QS-Bausteinen | VL19, PJ01 |
| `STRIPE_*`-Variablen in Railway entfernen | nicht dokumentiert, welche Namen genau | — |
| Zehn Module ohne eigenen Test (`forms.py`, `signals.py`, `views/_helpers.py`, `views/auth.py`, `views/cart.py`, `views/checkout.py`, `views/gaestebuch.py`, `views/shop.py`, `pruefe_seite.py`, `tiktok stream/streamtest.py`) — die View-Module sind über Seiten-, Konto- und Zahlungstests indirekt abgedeckt, das Audit zählt nur direkte Importe | PJ03 | PJ03 |
