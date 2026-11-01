---
stand: 2026-11-01
status: plan
zusammenfassung: Zahlungswege für Luviq in drei Stufen – Revolut-Zahlungslink sofort, Zahlungslink-Knopf im Shop, PayPal live mit „Später bezahlen“; Klarna nur über einen weiteren Anbieter.
---

# Zahlungen Luviq: Plan (Auftrag Bastian 01.11.2026)

Bastian: „Wir machen das selber Revolut Pro … vielleicht können die das auch dann so drüber bezahlen … nicht Vorkasse, sondern
danach bezahlen, zum Beispiel bei Klarna … aktuell schicken wir einfach direkt einzelne Rechnung, bis wir das bei ihrem Account
eingeschaltet haben … wie wir das am Handy freischalten können, dass sie da Zahlungslinks einbauen kann.“

## Was es heute gibt (Code)
- Zahlarten im Shop: `ZAHLARTEN = ('paypal', 'bank_transfer')` (`shop1/views/checkout.py:41`).
- **PayPal ist fertig eingebaut** (Bestellung, Erfassung, Eingangsbestätigung, CSP), läuft aber nicht: Live-`PAYPAL_CLIENT_ID`/`PAYPAL_SECRET` fehlen.
  Das SDK lädt mit `disable-funding=credit,card` (`payment.html:57`), Kartenzahlung über PayPal ist also abgeschaltet.
- Überweisung (Vorkasse) braucht `BANK_IBAN`/`BANK_INHABER`. Im Testpanel ist „nur Vorkasse“ eine der vier Kaufhürden (11 von 50).

## Was Revolut kann (Recherche 01.11.2026)
- **Zahlungslinks**: Der Kunde zahlt per Karte, Apple Pay, Google Pay, Revolut Pay oder Banküberweisung (Open Banking). Link erstellen und
  verschicken ist kostenlos, Gebühr nur bei Zahlung (GB-Angabe: ab 1 % + 0,20 £; EUR-Satz in Luisas App ablesen).
- **Kein Klarna, kein „später bezahlen“**: weder Zahlungslinks noch die Händler-API (dort nur Karte, Revolut Pay, SEPA-Lastschrift).
- Eine **Shop-Anbindung per API** (automatischer Bezahlknopf) gibt es nur mit einem Revolut-**Business**-Händlerkonto, nicht mit Pro.
  Pro ist ein Zusatzkonto am Privatkonto.
- Quellen: revolut.com/business/payment-links · revolut.com/en-DE/legal/payment-terms-paylinks · developer.revolut.com/docs/api/merchant ·
  wise.com/gb/blog/revolut-payment-links

## „Später bezahlen“ ohne neuen Anbieter: PayPal
PayPal-Seite DE: „Später bezahlen“ (einmal nach 30 Tagen oder 3/6/12/24 Raten) ist in der normalen Checkout-Gebühr
(**2,99 % + 0,35 €**) enthalten. Luisa bekommt den vollen Betrag sofort, PayPal trägt das Ausfallrisiko. Die Verfügbarkeit hängt vom
Händlerstatus ab, und es gibt eventuell einen Mindestbetrag: **beides im Konto prüfen**. Dazu kann PayPal Karte ohne PayPal-Konto annehmen.
Echtes **Klarna** ginge nur über einen weiteren Anbieter (z. B. Stripe), mit eigenem Konto und eigener Prüfung. Das lohnt erst, wenn Kunden danach fragen.

## Plan

| Stufe | Was | Wer | Aufwand | Ergebnis |
|---|---|---|---|---|
| **0 – ab sofort** | Bestellung kommt rein → Luisa schickt Rechnung + **Revolut-Zahlungslink** (Betrag, Bestellnummer im Text) | Luisa (Anleitung unten) | 0 | Kunde zahlt per Karte/Apple Pay statt Überweisung |
| **1 – Brücke im Shop** | Zahlart „Karte, Apple Pay, Google Pay (Zahlungslink)“. Die Bestellung wartet, Luisa fügt im Shop-Admin den Revolut-Link ein, der Shop schickt die Mail mit Knopf „Jetzt bezahlen“, Luisa setzt „bezahlt“. Kasse/AGB-§ Zahlung um den Weg ergänzen (Freigabe) | Claude baut | ~½ Tag + Tests | Kein Vorkasse-Zwang mehr im Bestellweg |
| **2 – Hauptweg** | **PayPal live**: Geschäftskonto Luisa (kostenlos), Live-App, Client-ID + Secret nach Railway; im Code `enable-funding=paylater` und Karte freischalten; Testkauf mit 1 € | Luisa/Bastian Konto, Claude Code + Test | Konto ~30 Min, Code ~2 Std | PayPal + **Später bezahlen/Raten** + Karte, alles automatisch |
| 3 – optional | Klarna über Stripe (eigenes Konto) | später | – | nur bei Nachfrage |

**Empfehlung:** Stufe 0 heute, Stufe 2 als Ziel (ein Konto bringt Karte, „danach bezahlen“ und Raten, der Code steht schon), Stufe 1 nur,
falls PayPal sich verzögert.

## Anleitung Luisa: Zahlungslink am Handy (Revolut-App)
Die Namen können je nach App-Version leicht abweichen. Im Zweifel in der App-Suche „Zahlungslink“ oder „Payment link“ eingeben.
1. Revolut-App öffnen → oben auf das Konto tippen → **Pro** wählen (falls Pro noch nicht aktiv ist: „Pro“ / „Revolut Pro starten“,
   Angaben zum Gewerbe eintragen: Luviq, Lübeck, Gewerbe seit 01.11.2026).
2. Im Pro-Bereich **„Bezahlt werden“ / „Get paid“** → **„Zahlungslink“** (beim ersten Mal „Zahlungen annehmen“ einschalten und bestätigen).
3. Betrag eintragen (z. B. 69,00 € + Versand), Beschreibung: „Luviq Bestellung Nr. …“ → **Erstellen**.
4. **Teilen** → per Mail oder WhatsApp an die Kundin schicken (oder Link in die Rechnung kopieren).
5. Bei Zahlungseingang kommt eine Mitteilung in der App → im Shop-Admin die Bestellung auf „bezahlt“ setzen und dann malen.
Gebühr pro Zahlung: in der App unter Pro → Gebühren ablesen und hier nachtragen.

## Offen (Entscheidung/Konto)
- Gehört das Pro-Konto Luisa (Geld muss auf ihr Gewerbe laufen)? → Annahme: ja.
- PayPal-Geschäftskonto für Luviq anlegen (nur Luisa/Bastian; Claude legt keine Konten an).
