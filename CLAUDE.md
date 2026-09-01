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
`shop1/views/` ist ein Package (`shop.py`, `auth.py`, `cart.py`, `checkout.py`, `legal.py`, `gaestebuch.py`). `shop1/urls.py` importiert nur `from . import views` — jede neue View-Funktion **muss** zusätzlich in `shop1/views/__init__.py` re-exportiert werden, sonst ist sie in `urls.py` nicht sichtbar. Interne Helfer (Decorators, Warenkorb-Sync) liegen separat in `shop1/views/_helpers.py`, nicht im Package-`__init__.py`.

Das custom Admin-Panel (`/shop-admin/...`) ist eine eigene View-Datei `shop1/admin_views.py`, geschützt durch den `admin_required`-Decorator, den diese Datei **selbst** definiert (`admin_views.py:37-45`) — nicht durch `_helpers.py`. Dort gab es bis Commit `93b3cde` eine zweite, von keinem Modul importierte Fassung; sie ist entfernt. "Admin" heißt: `is_superuser=True` ODER `username == os.getenv('ADMIN_USERNAME')` — das ist unabhängig vom regulären Django-Admin, dessen URL selbst über `ADMIN_URL` (Env-Var) konfigurierbar ist (Standard verstecken vor Scanner-Bots), siehe `mainweb/urls.py`.

### Zwei-Datenbank-Setup (wichtigster Architektur-Fallstrick)
`mainweb/settings.py` definiert `default` (Shop-Daten, SQLite lokal / Postgres via `DATABASE_URL`) und `pystore` (site-übergreifende Werbe-/Besucherdaten via `PYSTORE_DATABASE_URL`, fällt ohne diese Var auf eine **Kopie** von `default` zurück — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der Test-Runner die Namen der beiden Testdatenbanken). `shop1/routers.py` (`WerbungRouter`) leitet `Werbung`, `WerbungStat`, `VisitorLog` zwingend nach `pystore` und blockt deren Migrationen dort (`allow_migrate` → `False`), weil diese Tabellen vom separaten "pystore"-Projekt verwaltet werden. Diese Sperre gilt nur, solange `PYSTORE_DATABASE_URL` gesetzt ist (`settings.PYSTORE_IS_EXTERNAL`); ohne die Variable ist `pystore` die eigene Datenbank und wird migriert — sonst fehlten die Tabellen lokal und im Testlauf komplett. `PyStoreVisitorLog` in `models.py` ist ein `managed=False`-Proxy auf dieselbe `shop1_visitorlog`-Tabelle in `pystore` — nur zum expliziten Schreiben via `.using('pystore')`, keine eigene Migration.

### Testsuite (`shop1/tests/`)
Django-Test-Runner, ein Paket aus fünf Modulen (`test_seiten`, `test_seo`, `test_formulare`, `test_daten`, `test_einstellungen`) plus `_basis.py` mit der Basisklasse und den Seitenlisten. Ein zweites Testwerkzeug gibt es bewusst nicht.

Zwei Fallstricke, die `_basis.LuviqTestCase` abfängt und die man beim Schreiben neuer Tests kennen muss:
1. **`secure=True` ist Pflicht.** `SECURE_SSL_REDIRECT = not DEBUG` beantwortet im Betriebsmodus jeden HTTP-Abruf mit 301. Deshalb immer `self.hole(...)` / `self.sende(...)` statt `self.client.get/post` — sonst prüft der Test nur die Weiterleitung.
2. **`databases = {'default', 'pystore'}`.** `PageVisitMiddleware` schreibt bei jeder Antwort einen `VisitorLog` in `pystore`; ohne die Angabe scheitert jeder Seitentest.

Neue Templates mit `{% block %}` in einer erbenden Datei: eine Bedingung **um** einen Block herum wirkt nicht — Blöcke werden beim Übersetzen eingesammelt, nicht beim Rendern. Die Bedingung gehört in den Block (siehe `produkt_detail.html`).

Migrationen `0013` und `0014` legen `shop1_werbung`, `shop1_werbungstat` und `shop1_visitorlog` nur auf PostgreSQL an (`SeparateDatabaseAndState`). `0018` zieht sie auf allen anderen Backends nach, sonst existieren sie lokal und im Testlauf nicht.

### Denormalisierte Bestell-/Warenkorbdaten
`CartItem` und `OrderItem` speichern `produkt_name`/`produkt_preis` als eigene Felder statt FK auf `Produkt` — absichtlich, damit gelöschte oder geänderte Produkte bestehende Bestellungen/Warenkörbe nicht verändern oder brechen. Bei Änderungen an Warenkorb-/Checkout-Logik diese Denormalisierung erhalten.

### Produkt-Slugs
`Produkt.save()` generiert den Slug automatisch aus dem Namen (mit Kollisions-Suffix `-1`, `-2`, …) falls keiner gesetzt ist. Es existieren zwei URL-Routen: `produkt/<int:produkt_id>/` (Redirect auf Slug-URL, Altlink-Kompatibilität) und `produkt/<slug:slug>/` (kanonisch).

### E-Mail: zwei parallele Wege
1. Standard-Django-`send_mail` über SMTP (Brevo-Relay), konfiguriert in `settings.py` (`USE_SMTP_EMAIL`/`DEBUG`-abhängig, Console-Backend im Dev-Modus).
2. `shop1/utils.py::send_brevo_email()` — direkter HTTP-Call an die Brevo-API (Bypass für von Railway blockierte SMTP-Ports), läuft asynchron in einem `threading.Thread`. Für Bestell- und Benachrichtigungs-Mails wird dieser Weg bevorzugt.

### PageVisitMiddleware (`shop1/middleware.py`)
Läuft nach jeder Response (`_track()` vor dem `return response`). Der Geo-IP-Lookup bei `ip-api.com` läuft **im Background-Thread** und blockiert die Antwort nicht. Die Datenbankschreibvorgänge selbst (`PageVisit`, `VisitorLog`) laufen dagegen **synchron im Request-Zyklus** — sie verzögern die Auslieferung. Session-basiertes Dedup: ein `PageVisit`-Eintrag pro Session/Tag, ein `VisitorLog`-Eintrag pro Pfad alle **5 Minuten** (`diff < 300` in `middleware.py`; der Kommentar über dem Block nannte bis Commit `93b3cde` fälschlich 30 Minuten und steht jetzt auf 5). Admin-Benachrichtigungs-Mails pro Seitenbesuch gibt es seit Commit `e58775a` **nicht mehr**. Externe Aufrufe in neuer Tracking-Logik gehören weiterhin in einen Thread.

### Context Processor (`shop1/context_processors.py`)
`shop_owner_check` injiziert `is_shop_owner`, `cart_count`, `werbung_aktiv` (60s `LocMemCache`) und `GOOGLE_REVIEW_URL` in jedes Template. Werbe-Impressionen werden bewusst **nicht** hier gezählt (war ein Bug), sondern nur in der `startseite()`-View.

### Sicherheit
`django-axes` sperrt nach 10 Fehlversuchen pro Username+IP-Kombination (nicht nur IP) für 1h, eigenes Lockout-Template `shop1/lockout.html`. CSRF/Session-Cookies, HSTS und Referrer-Policy sind in `settings.py` zentral gesetzt und production-abhängig (`DEBUG`-Flag).

### Deployment (Railway, `start.sh`)
Reihenfolge beim Container-Start: `migrate` → Superuser aus `ADMIN_USERNAME`/`ADMIN_PASSWORD`/`ADMIN_EMAIL` anlegen/syncen → `loaddata initial_data.json` (optional) → `fix_pystore_schema` (Custom Command, behebt `seite`-Spalte in `pystore`) → `collectstatic --clear` → Gunicorn. Media-Dateien laufen über Cloudinary (`CLOUDINARY_URL`), Static-Dateien über WhiteNoise + `ManifestStaticFilesStorage` (Cache-Busting per Content-Hash).
