---
bereich: wegweiser
titel: Wegweiser durch die Dokumentation
stand: 2026-09-02
status: vollständig
fortschritt: 100
zusammenfassung: Elf Dateien nach Doku-Standard; die Original-Doku im Projektstamm bleibt die Detailquelle.
quellen: CLAUDE.md, DOCUMENTATION.md, GOOGLE_SEO_GUIDE.md, LOGBUCH.md, paypal_sandbox_tutorial.md
---

# Luviq Universe — Dokumentation

Onlineshop für handbemalte Second-Hand-Mode von **Luisa Brehler**, Alsfeld (Hessen).
Domain `www.luviq-alsfeld.com`. **Einziger echter Shop im Bestand**: Bestellungen, Kundenkonten,
PayPal-Zahlung, zwei Datenbanken. Ein Fehler kostet hier direkt Geld — Änderungen an Warenkorb,
Checkout und Zahlung nur mit Sandbox-Test (siehe `../paypal_sandbox_tutorial.md`).

> **Vier Namen, ein Projekt:** Ordner `WebseiteMAIN` · Repo `Webseitemitstripe` · Railway-Dienst
> `Luviq-Luisa` · Domain `luviq-alsfeld.com`. **Bezahlt wird mit PayPal, nicht mit Stripe.**
> Details in [90-NOTIZEN.md](90-NOTIZEN.md).

## Welche Datei wofür

| Datei | Bereich | Darin steht |
|---|---|---|
| [00-STATUS.md](00-STATUS.md) | Stand | Steckbrief, Ampel je Bereich, Messblock des Werkzeugs, die drei wichtigsten offenen Punkte |
| [10-TECHNIK.md](10-TECHNIK.md) | Technik | Stack, Railway-Deploy, Umgebungsvariablen (nur Namen), Testsuite, Aufbau, Fallen (zwei Datenbanken, E-Mail-Wege, Views-Package) |
| [20-DESIGN.md](20-DESIGN.md) | Design | Dunkelbraun-Gold-Linie, Schriften, Seitenaufbau, Designwache, was nicht angefasst wird |
| [30-INHALTE.md](30-INHALTE.md) | Inhalte | Seitenbestand (14 URLs live), Wissensbereich im Zweig, Texte und Bilder, fehlende Inhalte |
| [40-SEO.md](40-SEO.md) | SEO/GEO | Sitemap, robots, Canonical-Host, Schema, llms.txt, Keywords, was live ist und was im Zweig wartet |
| [50-LOCAL-SEO.md](50-LOCAL-SEO.md) | Local SEO | Unternehmensprofil, Search Console, Bewertungen, NAP — weitgehend nicht dokumentiert |
| [60-ADS.md](60-ADS.md) | Ads | **Keine Ads.** Was für Shopping-/Suchanzeigen nötig wäre |
| [70-PERFORMANCE.md](70-PERFORMANCE.md) | Performance | PageSpeed je Seite, Antwortzeit, Verfügbarkeit, umgesetzte Massnahmen |
| [80-AUFGABEN.md](80-AUFGABEN.md) | Aufgaben | Offen · Fehlt · Verbesserungsmöglichkeiten (mit Regelkennungen) · Beim Kunden · Erledigt |
| [90-NOTIZEN.md](90-NOTIZEN.md) | Notizen | Namensfallen, Zweig gegenüber main, Widersprüche zwischen Quellen, Verweise |

## Original-Dokumentation im Projekt

| Datei | Ein Satz |
|---|---|
| [`../CLAUDE.md`](../CLAUDE.md) | Architektur und Fallstricke, die beim Anfassen zählen — Views-Package, zwei Datenbanken, drei eigene Middlewares, Testsuite, Designwache, Wissensbereich mit Freigabeschalter; Stand 02.09.2026 (Zweig). |
| [`../DOCUMENTATION.md`](../DOCUMENTATION.md) | Modelle, E-Mail-Flows (Bank, PayPal, Verifikation), Admin-Guide, Deployment, §6 bekannte Eigenheiten, SEO-Schema, Performance, Sicherheit; Grundstand 25.05.2026, zuletzt 01.09.2026 angepasst. |
| [`../GOOGLE_SEO_GUIDE.md`](../GOOGLE_SEO_GUIDE.md) | Was am Code für Google gemacht wurde und was die Betreiberin selbst tun muss (Search Console, Unternehmensprofil, Backlinks). |
| [`../LOGBUCH.md`](../LOGBUCH.md) | Was und **warum** je Schritt der Verbesserungsläufe 3 und 4 geändert wurde, mit Commit-Kennung, Gegenbeweisen und offenen Fragen; 1.260 Zeilen. |
| [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md) | Zahlung testen, ohne echtes Geld — Sandbox-Konten, Client-ID, Testkauf. |

## Für Claude: bei Aufgabe X zuerst Datei Y

| Aufgabe | Zuerst lesen |
|---|---|
| Irgendetwas am Code ändern | [10-TECHNIK.md](10-TECHNIK.md) → Fallen, dann `../CLAUDE.md` |
| Warenkorb, Checkout, Zahlung | [10-TECHNIK.md](10-TECHNIK.md) → Fallen **und** `../paypal_sandbox_tutorial.md`; Tests `test_warenkorb`, `test_zahlung` |
| Text, Meta, Schema | [40-SEO.md](40-SEO.md), [30-INHALTE.md](30-INHALTE.md); Designwache in [20-DESIGN.md](20-DESIGN.md) beachten |
| Aussehen | [20-DESIGN.md](20-DESIGN.md) — die Designwache (`test_aufbau`) blockiert jede Strukturänderung |
| Deploy, Railway, Umgebungsvariablen | [10-TECHNIK.md](10-TECHNIK.md) → Hosting; nach dem Merge des Zweigs `CANONICAL_HOST` setzen |
| Was ist der nächste Schritt? | [80-AUFGABEN.md](80-AUFGABEN.md) → Offen; [90-NOTIZEN.md](90-NOTIZEN.md) → Zweig gegenüber main |
| Google Ads | [60-ADS.md](60-ADS.md) — es gibt keine; nichts anlegen ohne Konto der Betreiberin |
| Warum sieht die Live-Seite anders aus als der Code? | [90-NOTIZEN.md](90-NOTIZEN.md) — der Ordner steht auf dem Zweig `cockpit/2026-09-01-verbesserung-4`, live ist `main` |
