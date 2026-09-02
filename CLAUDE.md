# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektüberblick

Django-Shop "Luviq Universe" (Upcycling-Mode-Shop). Django 5+, deployed auf Railway via Docker. Ausführliche Feature-Doku (Modelle, E-Mail-Flows, Admin-Guide, SEO, Sicherheit) steht in `DOCUMENTATION.md` — bei Fragen zu bestehendem Verhalten zuerst dort nachsehen.

Die Ordner `projekt1/` und `tiktok stream/` im Repo-Root sind unversionierte Scratch-/Altablagen und **nicht** Teil dieser Django-App — ignorieren.

## Befehle

```bash
python manage.py runserver              # Dev-Server
python manage.py migrate                # Migrationen anwenden
python manage.py makemigrations shop1    # Neue Migration erzeugen (einzige App: shop1)
python manage.py test shop1              # Testsuite der App (shop1/tests/, Django-Test-Runner)
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py fix_pystore_schema      # Custom Command, siehe start.sh
```

Es gibt kein `package.json`/npm-Build. Tailwind wird eigenständig aus `tailwind_input.css` nach `shop1/static/shop1/tailwind.css` gebaut (Tailwind-CLI, `tailwind.config.js` scannt `templates/**/*.html` und `shop1/templates/**/*.html`).

Lokale Konfiguration über `.env` im Projekt-Root (`python-dotenv`, wird in `mainweb/settings.py` geladen) — nicht in Git. **Ohne `.env` läuft kein `manage.py`-Befehl**: `settings.py` wirft bei `DEBUG=False` und unverändertem Standard-`SECRET_KEY` einen `RuntimeError`. Für lokale Prüfläufe genügt eine `.env` mit einem gesetzten `SECRET_KEY`.

Änderungen an diesem Projekt werden in `LOGBUCH.md` festgehalten (was und **warum**, mit Commit-Kennung).

## Architektur

**Eine Django-App (`shop1`)**, Projekt-Konfig in `mainweb/` (settings, urls, wsgi/asgi).

### Views sind aufgeteilt, aber zentral re-exportiert
`shop1/views/` ist ein Package (`shop.py`, `auth.py`, `cart.py`, `checkout.py`, `legal.py`, `gaestebuch.py`, `wissen.py`). `shop1/urls.py` importiert nur `from . import views` — jede neue View-Funktion **muss** zusätzlich in `shop1/views/__init__.py` re-exportiert werden, sonst ist sie in `urls.py` nicht sichtbar. Interne Helfer (Decorators, Warenkorb-Sync) liegen separat in `shop1/views/_helpers.py`, nicht im Package-`__init__.py`.

**Wissensbereich (`/wissen/`, `views/wissen.py`):** Redaktionsseiten als statische Templates, angemeldet im Register `WISSEN_BEITRAEGE` (Slug → Routenname, Vorlage, Titel, Kurztext, `freigegeben`); `urls.py` baut daraus je Beitrag eine Route mit eigenem Namen. Ein neuer Beitrag ist zusätzlich in `seiten_stand.py`, `WISSEN_SEITEN` (`legal.py`), `tests/_basis.py`, `FAQ_SEITEN` (`test_geo`), `MINDESTWOERTER` (`test_inhalt`) und der Aufbau-Referenz einzutragen. `freigegeben=False` heißt: Seite erreichbar, aber `noindex` und weder in Sitemap noch in `llms.txt`; die Übersicht folgt den Beiträgen. Die Tests leiten `INDEXIERBARE_SEITEN` aus dem Register ab und schalten mit um.

**Gepflegtes Register `shop1/seiten_stand.py`:** Routenname → Datum der letzten inhaltlichen Änderung, von Hand nachzuziehen. Speist zugleich `<lastmod>` der Sitemap und `dateModified` des `WebPage`-Knotens; kein Test kann ein vergessenes Nachziehen erzwingen.

Das custom Admin-Panel (`/shop-admin/...`) ist eine eigene View-Datei `shop1/admin_views.py`, geschützt durch den `admin_required`-Decorator, den diese Datei **selbst** definiert (`admin_views.py:37-45`) — nicht durch `_helpers.py`. Dort gab es bis Commit `93b3cde` eine zweite, von keinem Modul importierte Fassung; sie ist entfernt. "Admin" heißt: `is_superuser=True` ODER `username == os.getenv('ADMIN_USERNAME')` — das ist unabhängig vom regulären Django-Admin, dessen URL selbst über `ADMIN_URL` (Env-Var) konfigurierbar ist (Standard verstecken vor Scanner-Bots), siehe `mainweb/urls.py`.

### Zwei-Datenbank-Setup (wichtigster Architektur-Fallstrick)
`mainweb/settings.py` definiert `default` (Shop-Daten, SQLite lokal / Postgres via `DATABASE_URL`) und `pystore` (site-übergreifende Werbe-/Besucherdaten via `PYSTORE_DATABASE_URL`, fällt ohne diese Var auf eine **Kopie** von `default` zurück — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der Test-Runner die Namen der beiden Testdatenbanken). `shop1/routers.py` (`WerbungRouter`) leitet `Werbung`, `WerbungStat`, `VisitorLog` zwingend nach `pystore` und blockt deren Migrationen dort (`allow_migrate` → `False`), weil diese Tabellen vom separaten "pystore"-Projekt verwaltet werden. Diese Sperre gilt nur, solange `PYSTORE_DATABASE_URL` gesetzt ist (`settings.PYSTORE_IS_EXTERNAL`); ohne die Variable ist `pystore` die eigene Datenbank und wird migriert — sonst fehlten die Tabellen lokal und im Testlauf komplett. `PyStoreVisitorLog` in `models.py` ist ein `managed=False`-Proxy auf dieselbe `shop1_visitorlog`-Tabelle in `pystore` — nur zum expliziten Schreiben via `.using('pystore')`, keine eigene Migration.

### Testsuite (`shop1/tests/`)
Django-Test-Runner, ein Paket aus vierzehn Modulen (`test_seiten`, `test_seo`, `test_geo`, `test_inhalt`, `test_formulare`, `test_daten`, `test_einstellungen`, `test_barrierefreiheit`, `test_ladezeit`, `test_aufbau`, `test_warenkorb`, `test_zahlung`, `test_konto`, `test_zugriffsschutz`) plus `_basis.py` (Basisklasse, Seitenlisten, Testdaten-Helfer) und `_aufbau.py` (Fingerabdruck der Designwache). Ein zweites Testwerkzeug gibt es bewusst nicht. Laufzeit rund 2,5 Minuten; einzelne Module laufen mit `python manage.py test shop1.tests.<modul>`.

Drei Fallstricke, die `_basis.LuviqTestCase` abfängt und die man beim Schreiben neuer Tests kennen muss:
1. **`secure=True` ist Pflicht.** `SECURE_SSL_REDIRECT = not DEBUG` beantwortet im Betriebsmodus jeden HTTP-Abruf mit 301. Deshalb immer `self.hole(...)` / `self.sende(...)` statt `self.client.get/post` — sonst prüft der Test nur die Weiterleitung.
2. **`databases = {'default', 'pystore'}`.** `PageVisitMiddleware` schreibt bei jeder Antwort einen `VisitorLog` in `pystore`; ohne die Angabe scheitert jeder Seitentest.
3. **Cache wird vor jedem Test geleert** (`_pre_setup`). `sitemap.xml` und `llms.txt` laufen über `cache_page` (15 min) im `LocMemCache`, der die Datenbank-Rücksetzung zwischen zwei Tests überlebt.

**Designwache (`test_aufbau`, `aufbau_referenz.json`):** Fingerabdruck des sichtbaren Aufbaus jeder öffentlichen Seite (Tag-Reihenfolge, `id`/`class`, Überschriften, Elementzahlen); alles im `<head>` und Attribute wie `alt`, `aria-*`, `src`, `srcset` sind bewusst nicht erfasst. Die Referenz wird für neue Seiten **gezielt ergänzt**, nie gelöscht und neu erzeugt — das hebt den Schutz der bestehenden Seiten still auf.

**Zeitzone in Tests:** `USE_TZ=True`, `TIME_ZONE='Europe/Berlin'`. Templates rendern Zeitstempel in Berliner Zeit; ein Vergleich mit `.date()` eines UTC-Zeitstempels ist zwischen 22:00 und 24:00 UTC falsch. Immer `timezone.localtime(...)` (siehe `test_geo`).

Neue Templates mit `{% block %}` in einer erbenden Datei: eine Bedingung **um** einen Block herum wirkt nicht — Blöcke werden beim Übersetzen eingesammelt, nicht beim Rendern. Die Bedingung gehört in den Block (siehe `produkt_detail.html`).

Migrationen `0013` und `0014` legen `shop1_werbung`, `shop1_werbungstat` und `shop1_visitorlog` nur auf PostgreSQL an (`SeparateDatabaseAndState`). `0018` zieht sie auf allen anderen Backends nach, sonst existieren sie lokal und im Testlauf nicht.

### Denormalisierte Bestell-/Warenkorbdaten
`CartItem` und `OrderItem` speichern `produkt_name`/`produkt_preis` als eigene Felder statt FK auf `Produkt` — absichtlich, damit gelöschte oder geänderte Produkte bestehende Bestellungen/Warenkörbe nicht verändern oder brechen. Bei Änderungen an Warenkorb-/Checkout-Logik diese Denormalisierung erhalten.

### Produkt-Slugs
`Produkt.save()` generiert den Slug automatisch aus dem Namen (mit Kollisions-Suffix `-1`, `-2`, …) falls keiner gesetzt ist. Es existieren zwei URL-Routen: `produkt/<int:produkt_id>/` (Redirect auf Slug-URL, Altlink-Kompatibilität) und `produkt/<slug:slug>/` (kanonisch).

### E-Mail: zwei parallele Wege
1. Standard-Django-`send_mail` über SMTP (Brevo-Relay), konfiguriert in `settings.py` (`USE_SMTP_EMAIL`/`DEBUG`-abhängig, Console-Backend im Dev-Modus).
2. `shop1/utils.py::send_brevo_email()` — direkter HTTP-Call an die Brevo-API (Bypass für von Railway blockierte SMTP-Ports), läuft asynchron in einem `threading.Thread`. Für Bestell- und Benachrichtigungs-Mails wird dieser Weg bevorzugt.

### Eigene Middleware (`shop1/middleware.py`)
Drei Klassen, Reihenfolge in `settings.MIDDLEWARE`:

1. **`CanonicalHostMiddleware`** (ganz vorn, vor `SecurityMiddleware`): leitet **nur** die www-/Nicht-www-Nebenvariante von `CANONICAL_HOST` (Umgebungsvariable, z. B. `www.luviq-alsfeld.com`) per 301 mit vollem Pfad und `https` um. Railway-Adresse und `localhost` bleiben unberührt; ohne Variable tut sie nichts. Ist die Variable gesetzt, kommen Host und Nebenvariante zusätzlich in `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`. Wirkt erst, wenn der DNS-Eintrag der Nebenvariante auf denselben Dienst zeigt.
2. **`ContentSecurityPolicyMiddleware`** (nach WhiteNoise): eigener Code, kein Paket. Positivliste `CSP_QUELLEN` und Betriebsart `CSP_MODUS` in `settings.py` — `report-only` (Vorgabe: Browser meldet nur in der Konsole), `scharf` (blockiert), `aus`; ein unbekannter Wert fällt auf Report-Only zurück. `script-src`/`style-src` bleiben wegen des Inline-Codes der Templates offen; scharf sind `frame-ancestors 'none'`, `base-uri`, `form-action`, `object-src`. **Vor dem Umschalten auf `scharf`** `/`, `/produkte/`, `/gaestebuch/`, `/checkout/`, `/payment/<id>/` und das Admin-Panel mit offener Browserkonsole prüfen; null `[Report Only]`-Meldungen sind die Bedingung.
3. **`PageVisitMiddleware`** (zuletzt): läuft nach jeder Response (`_track()` vor dem `return response`). Umgebungsvariable `VISITOR_TRACKING` (Vorgabe an; `0/false/off/no/nein/aus` schaltet ab, je Anfrage gelesen). Der Geo-IP-Lookup bei `ip-api.com` läuft in einem festen `ThreadPoolExecutor` (`GEO_PLAETZE` = 4, `BoundedSemaphore`); sind alle Plätze belegt, entfällt der Lookup, Land/Stadt bleiben leer. Die Datenbankschreibvorgänge (`PageVisit`, `VisitorLog`) laufen dagegen **synchron im Request-Zyklus** — sie verzögern die Auslieferung. Session-basiertes Dedup: ein `PageVisit`-Eintrag pro Session/Tag, ein `VisitorLog`-Eintrag pro Pfad alle **5 Minuten** (`diff < 300`). Admin-Benachrichtigungs-Mails pro Seitenbesuch gibt es seit Commit `e58775a` **nicht mehr**. Externe Aufrufe in neuer Tracking-Logik gehören in den Pool, nicht in einen Thread je Anfrage.

Dazu Djangos `GZipMiddleware` nach WhiteNoise (dynamische Antworten werden komprimiert, statische Dateien nicht erneut).

### Context Processor (`shop1/context_processors.py`)
`shop_owner_check` injiziert `is_shop_owner`, `cart_count`, `werbung_aktiv` (60s `LocMemCache`) und `GOOGLE_REVIEW_URL` in jedes Template. Werbe-Impressionen werden bewusst **nicht** hier gezählt (war ein Bug), sondern nur in der `startseite()`-View.

### Sicherheit
`django-axes` sperrt nach 10 Fehlversuchen pro Username+IP-Kombination (nicht nur IP) für 1h, eigenes Lockout-Template `shop1/lockout.html`. CSRF/Session-Cookies, HSTS und Referrer-Policy sind in `settings.py` zentral gesetzt und production-abhängig (`DEBUG`-Flag). Die Content-Security-Policy kommt aus der eigenen Middleware (siehe oben), Vorgabe Report-Only. Bekannte, bewusst dokumentierte Lücken (Tests in `test_zugriffsschutz` und `test_konto` halten den heutigen Zustand fest): `comment_delete`, `admin_produkt_toggle`, `admin_resend_newsletter` und `admin_newsletter_reset` reagieren auf GET; eine E-Mail-Adresse kann sich zweimal registrieren. Beides wartet auf eine Freigabe der Betreiberin.

### Deployment (Railway, `start.sh`)
Reihenfolge beim Container-Start: `migrate` → Superuser aus `ADMIN_USERNAME`/`ADMIN_PASSWORD`/`ADMIN_EMAIL` anlegen/syncen → `loaddata initial_data.json` (optional) → `fix_pystore_schema` (Custom Command, behebt `seite`-Spalte in `pystore`) → `collectstatic --clear` → `pruefe_seite` (Prüfbefehl: Einstellungen, Datenbanken, aktive Produkte, jede Sitemap-Adresse per Testclient; **nicht blockierend**, meldet nur ins Log; scharf per `--streng`) → Gunicorn (`gthread`, `GUNICORN_WORKERS`/`GUNICORN_THREADS`/`GUNICORN_TIMEOUT`, Vorgabe 2 × 4 Threads, Timeout 30 s, Worker-Erneuerung nach 1000 Anfragen). Media-Dateien laufen über Cloudinary (`CLOUDINARY_URL`), Static-Dateien über WhiteNoise + `ManifestStaticFilesStorage` (Cache-Busting per Content-Hash). `requirements.txt` ist nicht festgenagelt (kein `==`); lokal kann eine andere Django-Hauptversion laufen als im Container.
