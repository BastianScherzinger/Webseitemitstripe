---
bereich: notizen
titel: Notizen, Fallen und Verweise
stand: 2026-09-02
status: vollständig
fortschritt: 100
zusammenfassung: Vier Namen für ein Projekt, PayPal statt Stripe, Zweig gegenüber main, zehn Widersprüche zwischen Quellen und Live-Seite.
quellen: CLAUDE.md, DOCUMENTATION.md, GOOGLE_SEO_GUIDE.md, LOGBUCH.md, paypal_sandbox_tutorial.md
---

# Notizen — Luviq Universe

## Besonderheiten

### Der einzige echte Shop im Bestand

Fünf der sechs betreuten Seiten sind Prospekte. Luviq nicht: Es gibt Kundenkonten mit
E-Mail-Verifizierung, Warenkörbe, Bestellungen, PayPal-Zahlung und Vorab-Überweisung, ein eigenes
Admin-Panel mit 24 Routen und zwei Datenbanken. **Ein Fehler kostet hier direkt Geld.** Daraus
folgen zwei Regeln, die in keinem anderen Projekt gelten:

1. **Änderungen an Warenkorb, Checkout oder Zahlung nur mit Sandbox-Test** nach
   [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md) — Sandbox-Business- und
   -Personal-Konto anlegen, Sandbox-Client-ID in `PAYPAL_CLIENT_ID`, Testkauf durchführen, prüfen
   ob die Bestellung auf „bezahlt" springt und der Artikel deaktiviert wird (1-of-1-Logik). Vor der
   Live-Schaltung eine Live-App und die Live-Client-ID einsetzen.
2. **Die Denormalisierung bleibt.** `CartItem` und `OrderItem` speichern Produktname und Preis als
   eigene Felder statt als Fremdschlüssel — Absicht, damit geänderte oder gelöschte Produkte alte
   Bestellungen nicht verändern.

### Lauf 4 liegt gepusht auf einem Zweig und ist nicht live

Der Projektordner steht auf **`cockpit/2026-09-01-verbesserung-4`** (Commit `511ffe5`,
02.09.2026, 02:56), **63 Commits vor `main`**, Arbeitsbaum sauber, auf GitHub gepusht,
215/215 Tests grün. `main` steht seit dem 15.07.2026 auf `2a17edd`; die letzte Railway-Auslieferung
war am 18.08.2026 (`645842b`). **Die Live-Seite zeigt also main, nicht diesen Zweig.**

Der Zweig ändert 95 Dateien (+13.811 / −2.390 Zeilen). Die grössten Posten:

| Was | Umfang |
|---|---|
| Testsuite `shop1/tests/` — 14 Module, 215 Tests, `_basis.py`, `_aufbau.py`, `aufbau_referenz.json` (5.148 Zeilen) | neu, rund 5.000 Zeilen Testcode |
| `LOGBUCH.md` | +1.260 Zeilen |
| Prüfbefehl `shop1/management/commands/pruefe_seite.py` | +438 Zeilen |
| Wissensbereich: `views/wissen.py`, `templates/shop1/wissen/` (Übersicht + drei Beiträge) | +654 Zeilen |
| `shop1/middleware.py` (CanonicalHost, CSP, Geo-Pool, Abschalter) | +202 Zeilen |
| `mainweb/settings.py` (CSP-Quellen, CACHES, CANONICAL_HOST, GZip) | +115 Zeilen |
| `shop1/views/legal.py` (robots mit 13 KI-Crawlern, llms.txt, Sitemap mit lastmod) | +252 Zeilen |
| `shop1/seiten_stand.py` (Register für lastmod und dateModified) | neu |
| Bilder: WebP in mehreren Breiten, Favicon als ICO; ein totes Hintergrundbild (336 KB) entfernt | |
| Gelöscht: `django_tutorial.html` (1.862 Zeilen), `railway_deployment_tutorial.html` (80 Zeilen) | Altlasten |

**Was der Merge live bringt:** 301 vom Apex auf `www` (nur mit `CANONICAL_HOST` in Railway),
`llms.txt`, KI-Crawler-Regeln, `WebPage`/`Person`/`BreadcrumbList`-Knoten, gepflegte `lastmod`,
Meta-Beschreibungen in der Zielspanne, Antwort-zuerst-Texte auf sieben Seiten, beschriftete
Formularfelder, die vollständige Datenschutzerklärung, WebP-Bilder, GZip, Caches, Gunicorn mit
Threads, den Prüfbefehl in `start.sh` — und die Korrektur der Platzhalter-Kontaktdaten.

**Was der Merge nicht bringt:** die drei Wissensbeiträge in den Index (sie stehen auf
`freigegeben: False` → `noindex`, nicht in Sitemap und llms.txt) und die lokal gehosteten
Schriften (`RE07`).

### Zwei Datenbanken

`default` (Shop-Daten) und `pystore` (seitenübergreifende Werbe- und Besucherdaten,
`PYSTORE_DATABASE_URL`). `shop1/routers.py::WerbungRouter` zwingt `Werbung`, `WerbungStat` und
`VisitorLog` nach `pystore` und **blockt deren Migrationen dort**, weil das separate
PyStore-Projekt diese Tabellen verwaltet (`PYSTORE_IS_EXTERNAL`). Fehlt die Variable, ist `pystore`
eine **Kopie** von `default` — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der
Test-Runner die Namen der beiden Testdatenbanken. `PyStoreVisitorLog` ist ein `managed=False`-Proxy
auf dieselbe Tabelle (`db_column='site'`, das Feld heisst im Modell `seite`). Jeder Test braucht
`databases = {'default', 'pystore'}`, weil die Besuchs-Middleware bei jeder Antwort schreibt.

### Zwei E-Mail-Wege

1. Django-`send_mail` über SMTP (Brevo-Relay), im Entwicklungsmodus Console-Backend.
2. `shop1/utils.py::send_brevo_email()` — direkter HTTP-Aufruf an die Brevo-API in einem Thread,
   **weil Railway SMTP-Ports blockt**. Für Bestell- und Benachrichtigungsmails wird dieser Weg
   bevorzugt. Ein Mailausfall lässt die Bestellung bestehen und steht im Protokoll.

Seit `e58775a` (13.07.2026) gibt es **keine Admin-Mail pro Seitenbesuch** mehr: Clients und Bots
ohne Cookies galten bei jedem Aufruf als neu und lösten eine Mail-Flut aus, die Brevo überlastete.
Admin-Mails gibt es nur noch nutzergetriggert (Kontaktformular, Bestellungen).

### Startreihenfolge im Container

`start.sh`: `migrate` → Superuser aus `ADMIN_USERNAME`/`ADMIN_PASSWORD`/`ADMIN_EMAIL` anlegen oder
abgleichen → `loaddata initial_data.json` (optional) → `fix_pystore_schema` → `collectstatic --clear`
→ **`pruefe_seite`** (Zweig, nicht blockierend) → Gunicorn. **Das Passwort des Admin-Kontos wird bei
jedem Start neu gesetzt** — eine im Panel geänderte Angabe hält nur bis zum nächsten Deploy.

### Designwache

`test_aufbau` mit `aufbau_referenz.json` friert den sichtbaren Aufbau jeder öffentlichen Seite ein:
Tag-Reihenfolge, `id` und `class`, Überschriften, Elementzahlen. Nicht erfasst: alles im `<head>`
sowie `alt`, `aria-*`, `src`, `srcset`. Die Referenz wird für neue Seiten **gezielt ergänzt**, nie
gelöscht und neu erzeugt — das hebt den Schutz der bestehenden Seiten still auf. Deshalb wuchs
neuer Text in den Läufen immer in **vorhandenen** Absätzen: kein neues Element, keine neue Klasse.

## Namens- und Pfadfallen

### 1. Vier Namen, ein Projekt

| Rolle | Name |
|---|---|
| Ordner auf dem PC | **`WebseiteMAIN`** (`C:\Users\basti\Desktop\webseiten buisnes\WebseiteMAIN` — mit dem Tippfehler „buisnes") |
| GitHub-Repo | **`BastianScherzinger/Webseitemitstripe`** |
| Railway-Dienst | **`Luviq-Luisa`** (Projekt `webseiten`, Umgebung `shop`) |
| Domain | **`luviq-alsfeld.com`** / `www.luviq-alsfeld.com`, Railway-Adresse `luviq-luisa-shop.up.railway.app` |

Wer nach „Luviq" sucht, findet den Ordner nicht; wer nach „WebseiteMAIN" sucht, findet das Repo nicht.

### 2. „mit Stripe" stimmt nicht — bezahlt wird mit PayPal

Der Repo-Name `Webseitemitstripe` stammt aus einer frühen Planungsphase. Im Shop wird über
**PayPal** oder **Vorab-Überweisung** bezahlt (`views/checkout.py`, `payment.html`, AGB § 4).
Es gibt **keine Stripe-Integration**. In Railway liegen noch **`STRIPE_*`-Variablen** — Altlast;
kein Code im Projekt liest sie (Suche 02.09.2026 ohne Treffer). Welche Namen dort genau stehen,
ist nicht dokumentiert; entfernen, sobald jemand im Dienst nachgesehen hat.

Ebenfalls verwechslungsgefährdet: Im Werkzeug-Bestand heisst ein **anderes** Projekt „pystore"
(`pystore-websites`, Florin Feier). Die Datenbank `pystore` in diesem Shop gehört zu **jenem**
Projekt, nicht zu Luviq — sie hält nur die seitenübergreifenden Werbe- und Besucherdaten.

### 3. Views sind ein Package und müssen re-exportiert werden

`shop1/views/` ist ein Paket (`shop.py`, `auth.py`, `cart.py`, `checkout.py`, `legal.py`,
`gaestebuch.py`, `wissen.py`, `_helpers.py`), aber `shop1/urls.py` macht nur `from . import views`.
**Jede neue View-Funktion muss zusätzlich in `shop1/views/__init__.py` re-exportiert werden**,
sonst ist sie in `urls.py` unsichtbar. Interne Helfer bleiben bewusst draussen.

### 4. Zwei Admin-Zugänge, zwei Bedeutungen von „Admin"

Eigenes Panel `/shop-admin/…` (`shop1/admin_views.py`) mit dem dort **selbst** definierten
`admin_required` (`admin_views.py:37-45`, nicht aus `_helpers.py`): „Admin" heisst `is_superuser`
**oder** Benutzername gleich `ADMIN_USERNAME`. Der reguläre Django-Admin liegt hinter einer über
`ADMIN_URL` konfigurierbaren Adresse (Schutz vor Scannern).

### 5. Weitere Fallen in Kürze

- **Ohne `.env` läuft lokal kein `manage.py`-Befehl** — `settings.py` wirft bei `DEBUG=False` und
  unverändertem Standard-`SECRET_KEY` einen `RuntimeError`. Für Prüfläufe genügt eine `.env` mit
  gesetztem `SECRET_KEY`.
- **`secure=True` ist in Tests Pflicht** (`SECURE_SSL_REDIRECT = not DEBUG` beantwortet jeden
  HTTP-Abruf mit 301) → `self.hole()` / `self.sende()` statt `self.client.get/post`.
- **Cache leeren:** `sitemap.xml` und `llms.txt` liegen 15 Minuten im `LocMemCache`, der die
  Datenbank-Rücksetzung zwischen zwei Tests überlebt (`_pre_setup` erledigt es).
- **Zeitzone:** `USE_TZ=True`, `Europe/Berlin` — ein Vergleich mit `.date()` eines UTC-Zeitstempels
  ist zwischen 22:00 und 24:00 UTC falsch; `timezone.localtime()` benutzen.
- **Template-Blöcke:** Eine Bedingung **um** einen `{% block %}` in einer erbenden Datei wirkt
  nicht — Blöcke werden beim Übersetzen eingesammelt, nicht beim Rendern. Die Bedingung gehört
  **in** den Block.
- **`projekt1/` und `tiktok stream/`** im Repo-Stamm sind unversionierte Altablagen und **nicht**
  Teil der Django-App (in `.gitignore`). Das Code-Audit zählt ihre Dateien trotzdem mit — die
  „dichtesten Befunde" (`streamtest.py` 13, `main.py` 11) stammen von dort.
- **Kein npm-Build im Repo:** Tailwind wird mit der CLI aus `tailwind_input.css` nach
  `shop1/static/shop1/tailwind.css` gebaut; es gibt kein `package.json`.
- **Push von diesem Rechner:** `git -c credential.helper='!gh auth git-credential' push origin <zweig>`
  (der Git Credential Manager ist auf diesem PC kaputt).

## Zusätzliche Informationen

### Widersprüche zwischen Quellen und Live-Seite (Stand 02.09.2026)

| # | Widerspruch | Was gilt |
|---|---|---|
| 1 | `/kontakt/` nennt **live** „Musterstraße 123, 12345 Berlin", „+49 (0) 30 123456" und `info@luviq.universe`; das Impressum nennt Grünberger Str. 16, 36304 Alsfeld und `brehlerluisa@gmail.com` | Das Impressum gilt. Die Platzhalter sind im Zweig ersetzt, die Telefonnummer ersatzlos entfernt (es gibt keine belegte). Bis zum Merge steht auf der Kontaktseite ein falsches NAP |
| 2 | Impressum nennt **live** „Website: www.luviq.de" — eine Adresse, unter der das Projekt nicht erreichbar ist | Im Zweig durch den tatsächlichen Host ersetzt |
| 3 | Beide Domainschreibweisen antworten mit **200 ohne Weiterleitung** (`luviq-alsfeld.com` und `www.luviq-alsfeld.com`), obwohl ein `canonical` gesetzt ist | Der `canonical` genügt nicht (`TS11`); die 301 liegt im Zweig und braucht `CANONICAL_HOST` in Railway |
| 4 | `DOCUMENTATION.md` §5 nennt eine dreistufige Startsequenz und `SITE_URL=…up.railway.app`; `start.sh` hat sieben Stufen und die Domain ist längst eine eigene | `start.sh` gilt; die Doku ist an dieser Stelle veraltet |
| 5 | `DOCUMENTATION.md` §8 beschreibt einen „3D Hero (Three.js)"; die Startseite lädt Three.js nur auf Desktop und nachträglich, GSAP macht die sichtbare Animation | Beides trifft zu, die Doku ist unvollständig |
| 6 | `DOCUMENTATION.md` behauptete früher eine CSP „per settings-Variable"; sie existierte nie. Seit Schritt 36 gibt es eine echte Middleware, Vorgabe **Report-Only** | Die Doku ist am 01.09.2026 richtiggestellt worden; live ist auch die Middleware noch nicht |
| 7 | Das Impressum liefert `noindex, follow`, steht aber in der Sitemap (`SU11`), und PageSpeed meldet für `/impressum/` deshalb SEO 69 | Widerspruch in der Sache — eines von beiden muss weichen |
| 8 | Der Gesamtstand 70,1 mischt zwei Stände: die 230 Regeln wurden an der **Live-Seite (main)** gemessen, das Code-Audit lief über den **lokalen Ordner (Zweig)** | Beim Lesen der Bereichswerte mitdenken: „Code-Qualität 74" beschreibt den Zweig, „SEO-Technik 89,5" die Live-Seite |
| 9 | Die Überblicksdoku `docs/luviq.md` nennt 67,0 (Index) bzw. 70,1 (Messabschnitt) | 70,1 ist die Zahl vom 02.09.2026; 67,0 stammt aus einem älteren Lauf. Ältere Zahlen sind ohnehin nicht vergleichbar — am 01.09.2026 wurde der Maßstab von 54 auf 244 Regeln umgestellt |
| 10 | Das Code-Audit meldet vier „verwaiste" Templates: `lockout.html` und die drei `wissen/*.html` | Fehlalarm: `lockout.html` hängt an `AXES_LOCKOUT_TEMPLATE`, die Wissensseiten am Register `WISSEN_BEITRAEGE` — beide werden nicht per `render('…')` im Klartext referenziert |

### Weitere Beobachtungen

- **Die Sitemap kennt keine `lastmod` für statische Seiten** (live): nur die fünf Produktseiten
  tragen eines, mit zwei verschiedenen Daten (14.06. und 11.05.2026). Der Zweig speist alle
  statischen Seiten aus dem Register `shop1/seiten_stand.py`, das **von Hand** nachgezogen wird —
  bewusst kein Datei- oder Build-Datum, weil das bei jedem Deploy hochspringt. Kein Test kann ein
  vergessenes Nachziehen erzwingen.
- **13 KI-Crawler sind im Zweig namentlich zugelassen** (GPTBot, PerplexityBot, ClaudeBot,
  Google-Extended, Applebot-Extended, CCBot, meta-externalagent, Bytespider u. a.) — eine bewusste
  Entscheidung für Sichtbarkeit in Antwortmaschinen (`GE02`).
- **Der Bewertungskasten** (`_reviews_map.html`) zeigt „5.0 ★★★★★" und einen Knopf „Bei Google
  bewerten" (Ziel aus `GOOGLE_REVIEW_URL`). Die Zahl ist **nicht belegt** und wurde deshalb weder
  aufgegriffen noch ins Schema übernommen.
- **Der Shop filtert nur nach `aktiv`, nicht nach Lagerbestand** — verkaufte Stücke verschwinden
  nicht von selbst. Deshalb formulieren die Texte „kein zweites Exemplar, keine Nachbestellung"
  statt „verkauft ist weg".
- **`db.sqlite3` liegt im Ordner** (356 KB, zuletzt 02.09.2026) und ist in `.gitignore` — die
  lokale Entwicklungsdatenbank, nicht der Betriebsbestand.
- **Kein Consent-Banner** — heute richtig, weil nichts Einwilligungspflichtiges geladen wird.
  Mit dem ersten Tracking-Tag (z. B. für Ads) ändert sich das.

## Verweise

| Ziel | Pfad |
|---|---|
| Architektur und Fallstricke (führende Quelle) | [`../CLAUDE.md`](../CLAUDE.md) |
| Modelle, E-Mail-Flows, Admin, Deployment, Sicherheit | [`../DOCUMENTATION.md`](../DOCUMENTATION.md) |
| Was für Google getan wurde, was die Betreiberin tun muss | [`../GOOGLE_SEO_GUIDE.md`](../GOOGLE_SEO_GUIDE.md) |
| Arbeitsprotokoll der Läufe 3 und 4, je Schritt mit Grund und Commit | [`../LOGBUCH.md`](../LOGBUCH.md) |
| Zahlung testen ohne echtes Geld | [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md) |
| Wegweiser dieser Doku | [README.md](README.md) |
| Stand, Ampel, Messblock | [00-STATUS.md](00-STATUS.md) |
| Nächste Schritte und Freigaben der Betreiberin | [80-AUFGABEN.md](80-AUFGABEN.md) |
| Register für `lastmod` und `dateModified` | `../shop1/seiten_stand.py` |
| Register der Wissensbeiträge samt Freigabeschalter | `../shop1/views/wissen.py` |
| robots.txt, sitemap.xml, llms.txt (erzeugt) | `../shop1/views/legal.py` |
| Designwache und ihr Fingerabdruck | `../shop1/tests/_aufbau.py`, `../shop1/tests/aufbau_referenz.json` |
| Prüfbefehl | `../shop1/management/commands/pruefe_seite.py` |
| GitHub | https://github.com/BastianScherzinger/Webseitemitstripe |
| Live | https://www.luviq-alsfeld.com |
| Instagram | https://www.instagram.com/luviq.universe/ |
