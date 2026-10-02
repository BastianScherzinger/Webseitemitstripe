# Fallen — Luviq Universe

Kurzfassung der Stolpersteine, die schon einmal Zeit gekostet haben oder still etwas brechen. Je Eintrag: Datum der
Erkenntnis, was passiert, Beleg im Projekt. **Der Volltext mit allen Nummern steht in
[`../doku/10-TECHNIK.md`](../doku/10-TECHNIK.md) Abschnitt „Fallen“** — hier wird nichts weitergepflegt, was dort
steht; ein neuer Eintrag kommt zuerst dorthin und wird hier nur mit Datum, Satz und Beleg verlinkt.
Neuester Eintrag oben.

| Datum | Falle | Beleg |
|---|---|---|
| 2026-09-26 | **Neue Stücke sind ohne Verkauf „vergeben“.** Ohne `VERKAUF_AKTIV` erscheint jedes aktive Stück als „Nº 00x · Archiv“, auch ein frisch hochgeladenes. Mit Verkauf bekommen umgekehrt alle aktiven Stücke wieder Preis und Warenkorb — vergebene vorher auf inaktiv setzen. | `shop1/verkauf.py`, `mainweb/settings.py` (`VERKAUF_AKTIV`), `doku/10-TECHNIK.md` Falle 23 |
| 2026-09-26 | **Kaufweg-Wissensbeiträge verschwinden ohne Verkauf.** `nur_mit_verkauf` leitet die Adresse mit 302 auf `/wissen/`, nimmt sie aus Sitemap, `llms.txt` und Feed. Drei weitere Beiträge stehen auf `freigegeben: False` (`noindex`), bis die Betreiberin ihre Sachangaben bestätigt. Wer sie freischaltet, ohne zu fragen, übergeht eine Auflage. | `shop1/views/wissen.py` (`_sichtbar`, `WISSEN_BEITRAEGE`), `doku/30-INHALTE.md` |
| 2026-09-19 | **Mehrzeilige Vorlagenkommentare nur mit `{% comment %}`.** `{# … #}` gilt für eine Zeile; über mehrere Zeilen landet der Text sichtbar auf der Seite und die Designwache zählt Beispiel-Tags darin als Elemente. | `CLAUDE.md` Abschnitt „Look Nachtausgabe“, `doku/10-TECHNIK.md` Falle 20 |
| 2026-09-18 | **Die Karte lädt erst nach einem Klick.** `maps.google.com` in `CSP_QUELLEN['frame-src']` sieht aus wie ein Überbleibsel, ohne ihn bricht die Karte still, weil der Rahmen sein `src` erst im Browser bekommt. Kein `<iframe>` darf wieder ein fremdes `src` tragen. | `templates/base.html` (`iframe[data-src]`), `doku/10-TECHNIK.md` Falle 21, Test `EinbettungErstNachKlickTest` |
| 2026-09-18 | **Jedes Speichern eines `Produkt` meldet an IndexNow**, sobald `INDEXNOW_KEY` gesetzt ist (nach dem Commit, auch beim Löschen). | `shop1/signals.py` (`produkt_an_indexnow`), `doku/10-TECHNIK.md` Falle 22 |
| 2026-09-12 | **Fremdskript-Fassung ändern heißt Hash ändern.** Alpine und weitere Fremdskripte tragen `integrity="sha256-…"`; bleibt der alte Hash bei neuer Fassung stehen, führt der Browser das Skript gar nicht aus. | `templates/base.html` (Zeilen mit `integrity`), `doku/10-TECHNIK.md` Falle 17 |
| 2026-09-12 | **`{% load %}` wird an ein `{% include %}` nicht vererbt.** Ein Baustein unter `shop1/templates/shop1/teile/` lädt seine Bibliotheken selbst, sonst fehlt z. B. der Filter `cloud`. | `doku/10-TECHNIK.md` Falle 11 |
| 2026-09-11 | **Inline-Skripte brauchen die CSP-Nonce.** `script-src` hat kein `'unsafe-inline'`; jedes `<script>` im Template braucht `nonce="{{ csp_nonce }}"`, Handler-Attribute wie `onclick` gehen gar nicht (dafür `data-…`-Hilfen im Kopfskript). Jede neue Fremdquelle gehört in `CSP_QUELLEN`. | `templates/base.html` (`nonce="{{ csp_nonce }}"`), `shop1/tests/test_einstellungen.py`, `CLAUDE.md` Abschnitt „Eigene Middleware“ |
| 2026-09-11 | **Designwache (`test_aufbau`).** Tag-Reihenfolge, `id`/`class`, Überschriften und Elementzahlen jeder öffentlichen Seite sind eingefroren. Die Referenz wird für beabsichtigte Seiten gezielt ergänzt, nie komplett gelöscht und neu erzeugt — das hebt den Schutz der übrigen Seiten still auf. | `shop1/tests/aufbau_referenz.json`, `doku/20-DESIGN.md` |
| 2026-09 | **Tests brauchen `secure=True` und beide Datenbanken.** `SECURE_SSL_REDIRECT` beantwortet im Betriebsmodus jeden HTTP-Abruf mit 301, deshalb `self.hole(...)`/`self.sende(...)` statt `self.client.get/post`; ohne `databases = {'default', 'pystore'}` scheitert jeder Seitentest. | `shop1/tests/_basis.py` (`hole`, `sende`, `databases`) |
| 2026-09 | **Zwei Datenbanken.** `default` = Shop, `pystore` = Werbe-/Besucherdaten (`WerbungRouter`). Mit gesetzter `PYSTORE_DATABASE_URL` sind deren Migrationen dort gesperrt; ohne sie ist `pystore` eine Kopie von `default`. | `shop1/routers.py`, `CLAUDE.md` Abschnitt „Zwei-Datenbank-Setup“ |
| 2026-09 | **Neue View ohne Re-Export ist unsichtbar.** `urls.py` importiert nur `from . import views`; jede View gehört zusätzlich in `shop1/views/__init__.py`. | `shop1/views/__init__.py`, `doku/10-TECHNIK.md` Falle 3 |
| 2026-09 | **Der Superuser wird bei jedem Containerstart mit `ADMIN_PASSWORD` überschrieben.** Ein im Panel geändertes Passwort hält nur bis zum nächsten Deploy. | `start.sh` (Zeilen 8–15) |
| 2026-09 | **Vier Namen, ein Projekt:** Ordner `WebseiteMAIN`, Repo `Webseitemitstripe`, Railway-Dienst `Luviq-Luisa`, Domain `luviq-alsfeld.com`. Bezahlt wird mit PayPal, nicht mit Stripe. | `doku/README.md`, `doku/90-NOTIZEN.md` |

Neuen Eintrag hinzufügen: Datum, ein Satz zur Falle, Datei oder Test als Beleg. Erst wenn die Falle in
`doku/10-TECHNIK.md` nummeriert steht, hier darauf verweisen.
