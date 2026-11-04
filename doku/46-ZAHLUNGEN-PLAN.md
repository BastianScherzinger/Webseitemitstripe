---
stand: 2026-11-04
status: umgesetzt (Zahlungslink); Mollie offen
zusammenfassung: Revolut-Zahlungslink sofort (Anleitung an Luisa 01.11.), Ziel ein Anbieter für Karte/Apple Pay/Klarna mit Auszahlung auf Revolut Pro (Vorschlag Mollie); PayPal direkt vorerst nicht.
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

## Nachtrag 01.11.2026 nachmittags: Bastians Wunsch „ein Weg für alles“
Bastian: PayPal-Konto direkt **erst mal nicht**. Am liebsten eine Zahlungsquelle (Revolut Pro), über die auch Klarna, PayPal und
Rechnung laufen. Luisa hat nur ein normales Revolut-Konto. Die Anleitung „Pro einschalten + Zahlungslink“ ging ihr am 01.11. um 15:31 per Telegram zu.

- **Revolut allein kann das nicht.** Pro (kostenlos, nur für Selbstständige, Antrag in der App: Konto-Auswahl → „+ Neu hinzufügen“ → Pro)
  nimmt Karte, Apple Pay und Google Pay an, aber kein Klarna, kein PayPal und keinen Rechnungskauf.
- **So kommt man am nächsten heran:** ein Zahlungsanbieter für die Kasse, der alles bündelt und auf das Revolut-Pro-Konto auszahlt.
  Das Geld landet dann gesammelt bei Revolut. Vorschlag **Mollie** (Preisliste DE, abgerufen 01.11.):

| Zahlart | Gebühr |
|---|---|
| Karte (EU, privat), Apple Pay | 1,80 % + 0,25 € |
| Klarna (Rechnung/später bezahlen) | 2,99 % + 0,35 € |
| PayPal | PayPal-Gebühr + 0,10 € (braucht trotzdem ein verknüpftes PayPal-Konto, kann also später dazukommen) |
| SEPA-Überweisung | 0,25 € |

  Keine Monatsgebühr; bis 5 Auszahlungen im Monat kostenlos, auf ein eigenes Konto (Revolut-Pro-IBAN).
  Alternative wäre Stripe (ähnlicher Umfang). Mollie ist für deutsche Shops üblicher.
- **Ablauf:** (1) Luisa macht Revolut Pro an. (2) Luisa legt ein Mollie-Konto an und hinterlegt die Pro-IBAN als Auszahlungskonto;
  Claude legt keine Konten an. (3) Claude baut Mollie in die Kasse ein: Zahlarten Karte/Apple Pay/Klarna, Rückmeldung „bezahlt“
  automatisch, Testmodus zuerst. Aufwand ~1 Tag + Tests. (4) Rechtstexte § Zahlung anpassen (Freigabe). (5) Testkauf.
- Bis dahin gilt Stufe 0: Rechnung + Revolut-Zahlungslink.
- Quellen: mollie.com/de/pricing · help.revolut.com (Revolut Pro: wer darf, Funktionen) · revolut.com/en-DE/legal/pro

## An Luisa geschickt (Telegram, 01.11.2026, Bastians Auftrag)
- 15:31 Revolut Pro einschalten + Zahlungslink erstellen (5 Schritte).
- 15:37 „Bezahlen im Shop: der Plan in 3 Schritten“: Pro → Mollie-Konto (Einzelunternehmen, Website, Ausweis, Pro-IBAN mit
  Prüf-Überweisung, Zahlarten Karte/Apple Pay/Klarna) → wir bauen ein. Mit Warnung: den API-Schlüssel **nie** per Chat schicken,
  Bastian trägt ihn am PC ein. Dazu „Warum es sich lohnt“ (Vorkasse-Hürde weg, Klarna trägt Ausfallrisiko, 69-€-Shirt: Karte ~1,50 €, Klarna ~2,40 €).
- 15:37 Fragen: (1) Pro geklappt? (2) Mailadresse für Mollie? (3) Shirt-Maße in cm je Größe? (4) neues Foto für „Über Luisa“?
- Bastian schickt ihr zusätzlich eine eigene Zusammenfassung.

## Offen (Entscheidung/Konto)
- Gehört das Pro-Konto Luisa (Geld muss auf ihr Gewerbe laufen)? → Annahme: ja.
- Mollie-Konto (Luisa) und Klarna-Freigabe durch Mollie; danach Schlüssel über `key_einrichten.py`/Railway durch Bastian.
- Steuer: Mollie sitzt in den Niederlanden. Ob für die Gebühren § 13b (Reverse Charge) greift oder sie als Finanzumsatz steuerfrei sind,
  vor der ersten Mollie-Rechnung in der Buchhaltung klären (vgl. Webagentur BUCHHALTUNG.md §4).
- PayPal direkt: vorerst nicht (Bastian 01.11.).

## Nachtrag 04.11.2026: Zahlungslink ist Hauptweg
Bastian: „Wir bezahlen über Revolut-Zahlungslinks, und das geben wir auf der Website an.“ Umgesetzt (Zweig `bau/2026-11-04-zahlungslink`, Stufe 0/1 des Plans, ohne Mollie):
- **Ablauf:** Bestellung im Direktkauf (Stück reserviert) → Luisa schickt innerhalb von 1 bis 2 Werktagen Rechnung (Lexware) mit persönlichem Revolut-Zahlungslink → Kundin zahlt mit Karte (Visa, Mastercard), Apple Pay, Google Pay oder Revolut Pay, alternativ Überweisung auf die Rechnungs-IBAN → nach Zahlungseingang wird gemalt (Engel-Shirt, 3 Werktage) und verschickt. Kein Klarna, kein PayPal, kein „Pay by bank“ versprochen.
- **Shop:** Zahlart `zahlungslink` (Direktkauf-Vorgabe), Feld `Order.zahlungslink` nur zur Übersicht im Shop-Admin (kein automatischer Mailversand). Mails: Kundin „reserviert“ (Zahlungslink und Rechnung separat), Luisa-Checkliste. Reservierung weiter 3 Tage ab Rechnungsdatum (`RESERVIERUNG_TAGE`). Lieferfrist einheitlich „ab dem Tag nach deiner Zahlung“.
- **Werte an einer Stelle:** `shop1/luviq_daten.py` (`ZAHLUNG`, `RECHNUNG_FRIST`, `FRIST_BEGINN`).
- **Weiter offen:** PayPal-Code bleibt, aber ohne sichtbare Zahlungsbehauptung. Mollie/Klarna nur bei Nachfrage. Gebühr pro Zahlungslink in Luisas Revolut-App ablesen und hier nachtragen. Für Revolut-Gebühren gilt weiter die Steuerfrage aus dem Abschnitt „Offen“.
