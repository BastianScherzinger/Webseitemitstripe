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
| 7 | 33 | Doku an den Code angeglichen, Logbuch angelegt | erledigt | dieser Commit |

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

### 2026-09-01 — Welle 7, Schritt 33: Doku an den Code angeglichen (dieser Commit)

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
