# Wegweiser — Luviq Universe

Django-Projekt „Luviq Universe“ (Marke und Shop-Code von Luisa Brehler, Alsfeld), Domain `www.luviq-alsfeld.com`.
**Der Verkauf ist aus** (`VERKAUF_AKTIV`, `mainweb/settings.py`), es ist kein Gewerbe angemeldet; die Live-Seite zeigt
Archiv, Motivanfrage und Warteliste. Dieser Wegweiser kopiert nichts: er sagt, in welcher Datei die Antwort steht.
Die Pflege liegt dort, nicht hier.

## Zuerst lesen

| Frage | Datei |
|---|---|
| Was gilt beim Ändern, was sind die Regeln für Claude? | [`../CLAUDE.md`](../CLAUDE.md) |
| Welche Fallen gibt es, mit Datum und Beleg? | [`FALLEN.md`](FALLEN.md) (Kurzfassung) und `../doku/10-TECHNIK.md` Abschnitt „Fallen“ (Volltext, nummeriert) |
| Wie steht die Seite da? | [`../doku/00-STATUS.md`](../doku/00-STATUS.md) |
| Was ist offen, was beim Kunden? | [`../doku/80-AUFGABEN.md`](../doku/80-AUFGABEN.md) |
| Was wurde wann und warum geändert? | [`../LOGBUCH.md`](../LOGBUCH.md) (neuester Eintrag oben) |

## Die Doku nach Thema (`doku/`, Einstieg [`../doku/README.md`](../doku/README.md))

| Thema | Datei |
|---|---|
| Stack, Hosting, Umgebungsvariablen, Tests | `../doku/10-TECHNIK.md` |
| Look „Nachtausgabe“, Designwache | `../doku/20-DESIGN.md` |
| Seitenbestand, Texte, Wissensbereich | `../doku/30-INHALTE.md` |
| SEO und GEO (Sitemap, Schema, llms.txt) | `../doku/40-SEO.md` |
| Unternehmensprofil, Search Console | `../doku/50-LOCAL-SEO.md` |
| Ads | `../doku/60-ADS.md` |
| Geschwindigkeit | `../doku/70-PERFORMANCE.md` |
| Namensfallen, Zweige, Widersprüche zwischen Quellen | `../doku/90-NOTIZEN.md` |

## Weitere Dateien im Projekt

| Datei | Wofür |
|---|---|
| [`../DOCUMENTATION.md`](../DOCUMENTATION.md) | Modelle, Mail-Abläufe, Admin-Anleitung; Grundstand Mai 2026, im Zweifel gilt der Code |
| [`../GOOGLE_SEO_GUIDE.md`](../GOOGLE_SEO_GUIDE.md) | Was für Google getan ist und was die Betreiberin selbst tun muss |
| [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md) | Zahlung testen ohne echtes Geld (nur relevant, wenn der Verkauf je eingeschaltet wird) |
| [`design-2026-09-BERICHT.md`](design-2026-09-BERICHT.md) | Bericht zum Umbau „Nachtausgabe“ vom 19.09.2026 |

## Prüfbefehle

`python manage.py test shop1` · `python manage.py pruefe_seite` · `python manage.py pruefe_links` ·
`python manage.py pruefe_mail` — Umgebung und Aufruf stehen in `../CLAUDE.md`, Abschnitt „Befehle“.
