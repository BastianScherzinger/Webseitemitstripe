---
bereich: wegweiser
titel: Wegweiser durch die Dokumentation
stand: 2026-10-03
status: vollständig
fortschritt: 100
zusammenfassung: Elf Dateien nach Doku-Standard, am 02.10.2026 gegen main (7ae67ab) und die Live-Seite geprüft; die Original-Doku im Projektstamm bleibt die Detailquelle.
quellen: CLAUDE.md, DOCUMENTATION.md, GOOGLE_SEO_GUIDE.md, LOGBUCH.md, paypal_sandbox_tutorial.md
---

# Luviq Universe — Dokumentation

Marke und (im Code) Onlineshop für handbemalte Second-Hand-Mode von **Luisa Brehler**, Alsfeld (Hessen).
Domain `www.luviq-alsfeld.com`. **Stand 02.10.2026: der Verkauf ist aus** — die Live-Seite ist „Marke im Aufbau“
mit Archiv, Motivanfrage und Warteliste, ohne Preise, Warenkorb und Kasse; es ist kein Gewerbe angemeldet.
Der Shop-Code (Bestellungen, Kundenkonten, PayPal-Zahlung, zwei Datenbanken) bleibt erhalten und hängt am
Schalter `VERKAUF_AKTIV`. **Einziger echter Shop im Bestand** — wird er eingeschaltet, kostet ein Fehler direkt
Geld: Änderungen an Warenkorb, Checkout und Zahlung nur mit Sandbox-Test (siehe `../paypal_sandbox_tutorial.md`).

> **Vier Namen, ein Projekt:** Ordner `WebseiteMAIN` · Repo `Webseitemitstripe` · Railway-Dienst
> `Luviq-Luisa` · Domain `luviq-alsfeld.com`. **Bezahlt wird mit PayPal, nicht mit Stripe.**
> Details in [90-NOTIZEN.md](90-NOTIZEN.md).

## Welche Datei wofür

| Datei | Bereich | Darin steht |
|---|---|---|
| [00-STATUS.md](00-STATUS.md) | Stand | Steckbrief, Ampel je Bereich, Messblock des Werkzeugs, die wichtigsten offenen Punkte |
| [10-TECHNIK.md](10-TECHNIK.md) | Technik | Stack, Railway-Deploy, Umgebungsvariablen (nur Namen), Testsuite, Aufbau, Fallen (zwei Datenbanken, E-Mail-Wege, Views-Package) |
| [20-DESIGN.md](20-DESIGN.md) | Design | Linie „Nachtausgabe“ (seit 19.09.2026), Schriften, Seitenaufbau, Designwache, was nicht angefasst wird |
| [30-INHALTE.md](30-INHALTE.md) | Inhalte | Seitenbestand (17 URLs in der Sitemap, Stand 02.10.2026), Wissensbereich (seit 02.10.2026 freigegeben und indexierbar), Texte und Bilder, fehlende Inhalte |
| [40-SEO.md](40-SEO.md) | SEO/GEO | Sitemap (mit Bildern), robots, Canonical-Host, Schema, llms.txt, Keywords, GEO, was erledigt und was offen ist |
| [50-LOCAL-SEO.md](50-LOCAL-SEO.md) | Local SEO | Unternehmensprofil „Luviq“ (Bestätigung nicht belegt), Search Console, Bewertungen (nicht dokumentiert), NAP |
| [60-ADS.md](60-ADS.md) | Ads | **Keine Ads.** Was für Shopping-/Suchanzeigen nötig wäre |
| [70-PERFORMANCE.md](70-PERFORMANCE.md) | Performance | PageSpeed je Seite, Antwortzeit, Verfügbarkeit, umgesetzte Massnahmen |
| [80-AUFGABEN.md](80-AUFGABEN.md) | Aufgaben | Offen (Bei Bastian / Später) · Fehlt · Verbesserungsmöglichkeiten (mit Regelkennungen) · Beim Kunden · Erledigt |
| [90-NOTIZEN.md](90-NOTIZEN.md) | Notizen | Namensfallen, Zweige und main, Widersprüche zwischen Quellen und Live-Seite, Verweise |

## Original-Dokumentation im Projekt

| Datei | Ein Satz |
|---|---|
| [`../CLAUDE.md`](../CLAUDE.md) | Architektur und Fallstricke, die beim Anfassen zählen — Views-Package, zwei Datenbanken, drei eigene Middlewares, Testsuite, Designwache, Wissensbereich mit Freigabeschalter; Fortgeschrieben bis 28.09.2026. |
| [`../DOCUMENTATION.md`](../DOCUMENTATION.md) | Modelle, E-Mail-Flows (Bank, PayPal, Verifikation), Admin-Guide, Deployment, §6 bekannte Eigenheiten, SEO-Schema, Performance, Sicherheit; Grundstand 25.05.2026, zuletzt 01.09.2026 angepasst — danach nicht mehr nachgezogen; im Zweifel gilt der Code. |
| [`../GOOGLE_SEO_GUIDE.md`](../GOOGLE_SEO_GUIDE.md) | Was am Code für Google gemacht wurde und was die Betreiberin selbst tun muss (Search Console, Unternehmensprofil, Backlinks). |
| [`../LOGBUCH.md`](../LOGBUCH.md) | Was und **warum** je Schritt der Verbesserungsläufe 3 und 4 geändert wurde, mit Commit-Kennung, Gegenbeweisen und offenen Fragen; über 2.500 Zeilen (Stand 02.10.2026). |
| [`../paypal_sandbox_tutorial.md`](../paypal_sandbox_tutorial.md) | Zahlung testen, ohne echtes Geld — Sandbox-Konten, Client-ID, Testkauf. |
| [`../docs/design-2026-09-BERICHT.md`](../docs/design-2026-09-BERICHT.md) | Bericht zum Umbau „Nachtausgabe“ vom 19.09.2026. |

## Für Claude: bei Aufgabe X zuerst Datei Y

| Aufgabe | Zuerst lesen |
|---|---|
| Irgendetwas am Code ändern | [10-TECHNIK.md](10-TECHNIK.md) → Fallen, dann `../CLAUDE.md` |
| Warenkorb, Checkout, Zahlung | [10-TECHNIK.md](10-TECHNIK.md) → Fallen **und** `../paypal_sandbox_tutorial.md`; Tests `test_warenkorb`, `test_zahlung` |
| Text, Meta, Schema | [40-SEO.md](40-SEO.md), [30-INHALTE.md](30-INHALTE.md); Designwache in [20-DESIGN.md](20-DESIGN.md) beachten |
| Aussehen | [20-DESIGN.md](20-DESIGN.md) — die Designwache (`test_aufbau`) blockiert jede Strukturänderung |
| Deploy, Railway, Umgebungsvariablen | [10-TECHNIK.md](10-TECHNIK.md) → Hosting; `CANONICAL_HOST=www.luviq-alsfeld.com` ist gesetzt (der Apex leitet seit dem 16.09.2026 per 301 auf www, abgerufen 02.10.2026) |
| Was ist der nächste Schritt? | [80-AUFGABEN.md](80-AUFGABEN.md) → Offen; [90-NOTIZEN.md](90-NOTIZEN.md) → Zweige und main |
| Google Ads | [60-ADS.md](60-ADS.md) — es gibt keine; nichts anlegen ohne Konto der Betreiberin |
| Verkauf einschalten | [80-AUFGABEN.md](80-AUFGABEN.md) → „Verkauf einschalten nach Gewerbeanmeldung“ — nicht ohne Gewerbe, nicht ohne Freigabe |
| Warum sieht die Live-Seite anders aus als erwartet? | [90-NOTIZEN.md](90-NOTIZEN.md) — live ist `main`; der Verkaufsschalter ist aus, deshalb fehlen Preise, Warenkorb und Kasse |
