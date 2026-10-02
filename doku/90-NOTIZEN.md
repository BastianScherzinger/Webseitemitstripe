---
bereich: notizen
titel: Notizen, Fallen und Verweise
stand: 2026-10-03
status: vollständig
fortschritt: 100
zusammenfassung: Stand 02.10.2026: Vier Namen für ein Projekt, PayPal statt Stripe (Verkauf aus, kein Gewerbe), alle Zweige in main (7ae67ab), Mail über Gmail; die Widerspruchstabelle vom 02.09.2026 ist am 01.10.2026 gegen die Live-Seite nachgeprüft (sechs behoben, vier bleiben), der Stand von main und der Live-Seite am 02.10.2026 erneuert.
quellen: CLAUDE.md, DOCUMENTATION.md, GOOGLE_SEO_GUIDE.md, LOGBUCH.md, paypal_sandbox_tutorial.md
---

# Notizen — Luviq Universe

> **Stand 02.10.2026 (geprüft, abends):** `main` = `origin/main` = `7ae67ab` und live. Alle Arbeitszweige des Tages (`fix/2026-10-02-luviq-fertig`, `-rest`, `-luisa`, `-recht`, `-wissen`, `fix/2026-10-02d-standard`) sind gemergt (`git log origin/main..<zweig>` leer, `git branch -r --no-merged origin/main` leer); die GitHub-Prüfungen auf `main` sind grün (Lauf 37040107996, 02.10.2026). Live belegt am 02.10.2026 (curl): Sitemap mit 17 Adressen samt der drei Wissensbeiträge, `/llms-full.txt` 200, „Aktualisiert am …“ (`<time>`) auf den Wissensbeiträgen (GE47), `Permissions-Policy` im Kopf, `/health/` 200, Apex 301 auf www. Wo unten „Zweig“ oder „nicht gemergt“ steht, ist das **Verlauf** des jeweiligen Tages und gilt seit dem Merge als live, sofern der Satz nichts anderes sagt. Der **Verkauf ist aus** (`VERKAUF_AKTIV` ohne Variable = aus: Marke im Aufbau, Archiv statt Shop); nach Angabe des Betreibers ist **kein Gewerbe angemeldet** — die Seite nennt deshalb keine Unternehmensangaben (Impressum nach § 5 DDG nur mit Luisa Brehler als Person, Alsfeld, E-Mail).

## Besonderheiten

### Der einzige echte Shop im Bestand

Fünf der sechs betreuten Seiten sind Prospekte. Luviq nicht: Es gibt Kundenkonten mit
E-Mail-Verifizierung, Warenkörbe, Bestellungen, PayPal-Zahlung und Vorab-Überweisung, ein eigenes
Admin-Panel mit 24 Routen und zwei Datenbanken — **Stand 02.10.2026: der Verkauf ist abgeschaltet** (`VERKAUF_AKTIV`, Marke im Aufbau, kein Gewerbe angemeldet); der Code bleibt. **Mit eingeschaltetem Verkauf kostet ein Fehler hier direkt Geld.** Daraus
folgen zwei Regeln, die in keinem anderen Projekt gelten:

1. **Änderungen an Warenkorb, Checkout oder Zahlung nur mit Sandbox-Test** nach
   [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md) — Sandbox-Business- und
   -Personal-Konto anlegen, Sandbox-Client-ID in `PAYPAL_CLIENT_ID`, Testkauf durchführen, prüfen
   ob die Bestellung auf „bezahlt" springt und der Artikel deaktiviert wird (1-of-1-Logik). Vor der
   Live-Schaltung eine Live-App und die Live-Client-ID einsetzen.
2. **Die Denormalisierung bleibt.** `CartItem` und `OrderItem` speichern Produktname und Preis als
   eigene Felder statt als Fremdschlüssel — Absicht, damit geänderte oder gelöschte Produkte alte
   Bestellungen nicht verändern.

### Zweige und main (Stand 02.10.2026)

Der Projektordner steht auf **`main`**, `main` = `origin/main` = **`7ae67ab`** (02.10.2026; letzter Code-Commit `f03bf61`). Alle Arbeitszweige sind gemergt (auch `fix/2026-10-02-*`: `git log origin/main..<zweig>` ist für jeden leer; `cockpit/…`, `sofort/…`, `mail/…`, `recht/…`, `design/…` ebenso — `git branch -r --no-merged origin/main` ist leer); die Live-Seite zeigt diesen Stand (Sitemap mit Wissensbeiträgen, `llms-full.txt` und `Permissions-Policy` am 02.10.2026 abgerufen). Einige alte lokale Zweige (`sofort/2026-09-*`, `sicherung/2026-09-07-vor-squash`) tragen Commits, die hash-weise nicht in `main` stehen, weil `main` per Pull Request oder Squash entstand; ihr Inhalt ist enthalten, die Remote-Zweige sind gemergt. Der frühere Abschnitt „Lauf 4 liegt gepusht auf einem Zweig und ist nicht live“ (Stand 02.09.2026: Zweig `cockpit/2026-09-01-verbesserung-4`, 63 Commits vor `main`, `main` auf `2a17edd`) ist überholt: der Zweig steckt seit dem 11.09.2026 in `main`.

Was der Merge der Läufe live gebracht hat (belegt am 01.10.2026): 301 vom Apex auf `www`, `llms.txt`, KI-Crawler-Regeln in der `robots.txt`, Schema-Knoten mit `@id`, gepflegte `lastmod` (Register `seiten_stand.py`), WebP-Bilder, GZip, Gunicorn mit Threads, scharfe CSP, der Prüfbefehl in `start.sh` — und die Korrektur der Platzhalter-Kontaktdaten. **Nicht live sichtbar:** die drei Wissensbeiträge `pflege`, `upcycling`, `groesse` stehen auf `noindex` (`'freigegeben': False`), die drei verkaufsnahen leiten ohne Verkauf um.

**Zwei lokale Stände, die man nicht verwechseln darf:** Das Werkzeug schreibt seine Messcommits („Doku: Messung vom …“) lokal auf `main`; sie liegen erst nach dem Push auf `origin/main`.

### Zwei Datenbanken

`default` (Shop-Daten) und `pystore` (seitenübergreifende Werbe- und Besucherdaten,
`PYSTORE_DATABASE_URL`). `shop1/routers.py::WerbungRouter` zwingt `Werbung`, `WerbungStat` und
`VisitorLog` nach `pystore` und **blockt deren Migrationen dort**, weil das separate
PyStore-Projekt diese Tabellen verwaltet (`PYSTORE_IS_EXTERNAL`). Fehlt die Variable, ist `pystore`
eine **Kopie** von `default` — kein zweiter Verweis auf dasselbe dict, sonst verwechselt der
Test-Runner die Namen der beiden Testdatenbanken. `PyStoreVisitorLog` ist ein `managed=False`-Proxy
auf dieselbe Tabelle (`db_column='site'`, das Feld heisst im Modell `seite`). Jeder Test braucht
`databases = {'default', 'pystore'}`, weil die Besuchs-Middleware bei jeder Antwort schreibt.

### Mail (Stand 27.09.2026): Gmail statt Brevo

Aller Versand läuft über SMTP von Luisas Gmail-Postfach (`smtp.gmail.com:587`; Railway: `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` als App-Passwort, `BREVO_API_KEY` entfernt). `shop1/utils.py::send_brevo_email()` heißt weiter so, nimmt ohne `BREVO_API_KEY` aber den SMTP-Weg und läuft in einem Thread; ein Mailausfall lässt die Anfrage bestehen (sie liegt in `KontaktAnfrage` bzw. `Motivanfrage`). Die frühere Beschreibung „zwei Wege: Brevo-Relay und Brevo-API“ gilt nicht mehr; Einzelheiten in [10-TECHNIK.md](10-TECHNIK.md), „E-Mail-Versand“.

Seit `e58775a` (13.07.2026) gibt es **keine Admin-Mail pro Seitenbesuch** mehr: Clients und Bots ohne Cookies galten bei jedem Aufruf als neu und lösten eine Mail-Flut aus. Admin-Mails gibt es nur noch nutzergetriggert (Kontaktformular, Motivanfrage, Registrierung).

### Startreihenfolge im Container

`start.sh`: `migrate` → Superuser aus `ADMIN_USERNAME`/`ADMIN_PASSWORD`/`ADMIN_EMAIL` anlegen oder
abgleichen → `loaddata initial_data.json` (optional) → `fix_pystore_schema` → `collectstatic --clear`
→ **`python -m whitenoise.compress --quiet staticfiles`** (seit Paket 267, `5515bf3`, in `main`; nicht blockierend, muss **nach** `collectstatic --clear`
stehen, sonst löscht `--clear` die `.gz`-Dateien wieder) → **`pruefe_seite`** (nicht blockierend) → Gunicorn. **Das Passwort des Admin-Kontos wird bei
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
| 8 | Der Gesamtstand 75,8 mischt zwei Stände: die 230 Regeln wurden an der **Live-Seite (main)** gemessen, das Code-Audit lief über den **lokalen Ordner (Zweig)** | Beim Lesen der Bereichswerte mitdenken: „Code-Qualität 68,8“ beschreibt den Zweig, „SEO-Technik 92,0“ die Live-Seite |
| 9 | Die Überblicksdoku `docs/luviq.md` nennt 67,0 (Index) bzw. 70,1 (Messabschnitt) | 70,1 ist die Zahl vom 02.09.2026; 67,0 stammt aus einem älteren Lauf. Ältere Zahlen sind ohnehin nicht vergleichbar — am 01.09.2026 wurde der Maßstab von 54 auf 244 Regeln umgestellt |
| 10 | Das Code-Audit meldet vier „verwaiste" Templates: `lockout.html` und die drei `wissen/*.html` | Fehlalarm: `lockout.html` hängt an `AXES_LOCKOUT_TEMPLATE`, die Wissensseiten am Register `WISSEN_BEITRAEGE` — beide werden nicht per `render('…')` im Klartext referenziert |


**Nachprüfung am 01.10.2026 gegen die Live-Seite:**

| # | Stand heute |
|---|---|
| 1 | **behoben:** `/kontakt/` nennt Luisa Brehler, 36304 Alsfeld, `brehlerluisa@gmail.com` und „eine Telefonnummer gibt es nicht“ |
| 2 | **behoben:** Impressum nennt „Website: www.luviq-alsfeld.com“ |
| 3 | **behoben:** Apex antwortet mit 301 auf `www` |
| 4 | gilt weiter: `DOCUMENTATION.md` ist an dieser Stelle veraltet, `start.sh` gilt |
| 5 | überholt: die Startseite wurde am 19.09.2026 neu gebaut (Panoramafoto, kein Three.js/GSAP mehr in `index.html` und `base.html`); `DOCUMENTATION.md` §8 beschreibt die alte Startseite |
| 6 | **behoben:** die CSP-Middleware ist live und scharf (Kopfzeile `content-security-policy` abgerufen) |
| 7 | **behoben:** das Impressum steht nicht mehr in der Sitemap |
| 8 | **behoben:** Live-Seite und lokaler Ordner sind derselbe Stand (`main`) |
| 9 | gilt weiter: ältere Zahlen sind nicht vergleichbar (Regelstand 2026-09-28a, 373 Regeln) |
| 10 | gilt weiter (Fehlalarm des Code-Audits: `lockout.html` und Wissensseiten hängen an Einstellung bzw. Register); die Wissensvorlagen sind inzwischen sieben |

### Weitere Beobachtungen

- **Die Sitemap trägt `lastmod` für alle Einträge** (Daten zwischen 11.05. und 27.09.2026, abgerufen 01.10.2026) — die statischen Seiten aus dem Register `shop1/seiten_stand.py`, das **von Hand** nachgezogen wird (bewusst kein Datei- oder Build-Datum, weil das bei jedem Deploy hochspringt; kein Test kann ein vergessenes Nachziehen erzwingen). Seit `36c0741` hängen an Start- und Produktseite Bild-Auszeichnungen.
- **Die `robots.txt` lässt KI-Crawler namentlich zu** (14 `User-agent`-Blöcke, GPTBot, PerplexityBot, ClaudeBot, Google-Extended u. a.) — eine bewusste Entscheidung für Sichtbarkeit in Antwortmaschinen (`GE02`).
- **Der Bewertungskasten** (`_reviews_map.html`) zeigt „5.0 ★★★★★" und einen Knopf „Bei Google
  bewerten" (Ziel aus `GOOGLE_REVIEW_URL`). Die Zahl ist **nicht belegt** und wurde deshalb weder
  aufgegriffen noch ins Schema übernommen.
- **Der Shop filtert nur nach `aktiv`, nicht nach Lagerbestand** — verkaufte Stücke verschwinden
  nicht von selbst. Deshalb formulieren die Texte „kein zweites Exemplar, keine Nachbestellung"
  statt „verkauft ist weg".
- **`db.sqlite3` liegt im Ordner** (356 KB, zuletzt 02.09.2026) und ist in `.gitignore` — die
  lokale Entwicklungsdatenbank, nicht der Betriebsbestand.
- **Kein Consent-Banner** — heute richtig, weil nichts Einwilligungspflichtiges geladen wird:
  die Seite setzt kein eigenes Cookie und greift auf keinen Gerätespeicher zu (kein Treffer für
  `set_cookie`, `localStorage`, `sessionStorage` in `shop1/`, `templates/`, `mainweb/`), die
  Besuchszählung läuft serverseitig in `PageVisitMiddleware` ohne Analysedienst, und die einzige
  fremde Einbettung — die Google-Karte auf `/gaestebuch/` (auf der Startseite seit dem Umbau vom 19.09.2026 nicht mehr) — lädt **seit `RE17`
  (18.09.2026, `d58a96c`) erst nach einem Klick** auf „Karte laden". Bis dahin stimmte der Satz
  nicht: der Kartenrahmen holte sich seine Adresse ungefragt bei Google (eigener Punkt `EIG14`,
  jetzt erledigt). Sitzungs- und CSRF-Cookie von Django bleiben — sie sind für Warenkorb und
  Anmeldung nötig und nach § 25 Abs. 2 TDDDG einwilligungsfrei. Mit dem ersten Tracking-Tag
  (z. B. für Ads) ändert sich das. Begründung als Ausnahme `RE15` im Bewertungsblock von
  [80-AUFGABEN.md](80-AUFGABEN.md).

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
