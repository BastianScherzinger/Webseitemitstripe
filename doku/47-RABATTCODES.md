---
stand: 2026-11-01
status: gebaut
zusammenfassung: Rabattcodes in Prozent, standardmäßig nur für die erste Bestellung (E-Mail + Anschrift), öffentlicher 10-%-Code im Hero, in FAQ/llms.txt/AGB; Codes nur in der Datenbank.
---

# Rabattcodes (Auftrag Bastian 01.11.2026)

Bastian: Rabattcodes für die erste Bestellung, „dass das wirklich die erste Bestellung bleibt“, 10 % immer auf der
Website und im Hero als Call to Action, in SEO/GEO angeteasert, ein 10-%- und ein 20-%-Code mit nicht erratbaren
Wörtern für Freunde und Karten, Knopf trägt den Rabatt automatisch ein, später auch mit Online-Zahlung.

**Die echten Codes stehen nicht im Repo**, sondern in der Datenbank und in
`Webagentur Scherzinger\Buero\luisa\arbeitsplatz\webseite\RABATTCODES.md`.

## So funktioniert es
| Teil | Wo |
|---|---|
| Modell `Rabattcode` (Code, Prozent, nur Erstbestellung, öffentlich, aktiv, gültig bis, Höchstzahl, Zweck) | `shop1/models.py`, Migration 0035 |
| Prüfung, Schlüssel, Betrag, öffentlicher Code | `shop1/rabatt.py` |
| Bestellformular: Feld „Rabattcode“ + „Einlösen“ (zeigt neuen Gesamtpreis, bestellt nicht) | `teile/direktkauf_formular.html`, `views/direktkauf.py` |
| Link `/rabatt/<CODE>/` merkt den Code in der Sitzung und springt ins Formular (Hero-Knopf, QR auf Karten) | `views/direktkauf.rabatt_einloesen` |
| Hero: „Jetzt bestellen · 10 % sparen“ + Zeile mit Code und Link „Bedingungen“ (AGB § 3) | `index.html`, nur wenn es einen aktiven öffentlichen Code gibt |
| FAQ „Gibt es einen Rabattcode für die erste Bestellung?“ (sichtbar + FAQPage-Schema) | `wissen_direktkauf.rabatt_faq`, Beitrag Bestellen |
| llms.txt-Frage | `views/legal._llms_rabatt_frage` |
| AGB § 3 (3), Datenschutz (Abgleich, Sitzungs-Cookie) | `legal/generator/agb.html`, `datenschutz.html` |
| Mails (Kundin: Rabattzeile; Luisa: „Rechnung über diesen Betrag“), Danke-Seite, Shop-Admin-Bestellung | `direktkauf.py`, `_vertragsunterlagen.html`, `admin/order_detail.html` |
| Verwalten | Django-Admin „Rabattcodes“ oder `python manage.py rabattcode liste|anlegen|aus|an` |

**Erste Bestellung:** Es zählt jede Bestellung außer `cancelled`/`failed`, unter derselben E-Mail (klein, ohne `+Zusatz`,
Gmail ohne Punkte) **oder** derselben Lieferanschrift (Straße+PLZ vereinheitlicht). Die Schlüssel stehen in
`Order.email_schluessel`/`anschrift_schluessel` (bei jedem Speichern gesetzt, Altbestand per Migration nachgetragen).
Geprüft wird in der Bestell-Transaktion mit gesperrter Code-Zeile (keine doppelte Einlösung bei gleichzeitigen Bestellungen).
Gilt der Code beim Absenden nicht, wird **nicht bestellt**; die Kundin sieht die Meldung und den Preis ohne Code
(§ 312j BGB: der Preis über dem Knopf muss stimmen).

**Grenzen (bewusst):** Wer neue E-Mail **und** neue Anschrift nimmt, bekommt den Rabatt erneut; Abholung hat keine
Anschrift. Bei 10 % auf ein 69-€-Shirt ist das hinnehmbar; mehr Schutz (Telefon, Name) würde echte Erstkundinnen treffen.

## Online-Zahlung später (Mollie)
Der Rabatt steckt fertig in der Bestellung: `Order.gesamt_betrag` ist schon reduziert, `rabatt_betrag`/`rabatt_code_text`
stehen daneben. Beim Mollie-Einbau (Plan `46-ZAHLUNGEN-PLAN.md`):
- Zahlung über **`order.gesamt_betrag`** anlegen, nie über die Postensumme; Beschreibung „Luviq Bestellung #… (Code …)“.
- Keinen zweiten Rabatt bei Mollie anlegen (Mollie-Gutscheine sind Essensgutscheine o. ä., nicht dasselbe).
- Bei Klarna über Mollie Posten mitschicken: Artikelzeile (Listenpreis) + Rabattzeile (`type: discount`, negativ), Summe = `gesamt_betrag`.
- Erst „bezahlt“ per Webhook zählt als Kauf; die Erstbestellungsprüfung zählt aber schon die offene Bestellung (verhindert Rabatt-Schleifen).
- Hinweis aus der Bug-Prüfung: `checkout.reserviert()` zählt nur `bank_transfer` – beim Mollie-Einbau `mollie` ergänzen.

## Plan: Reichweite statt Geld verschenken
1. **Jetzt live:** öffentlicher 10-%-Code im Hero, Formular-Hinweis, FAQ/Schema, llms.txt.
2. **Karten:** Code `KREIDEFUCHS-…` (10 %) als QR (`/rabatt/<CODE>/`) auf Karten ins Paket und zum Verteilen; `TRAVEWIND-…` (20 %, max. 30) nur persönlich.
   Messen: Admin-Spalte „eingelöst“ je Code (Website vs. Karten vs. Freunde).
3. **Instagram/TikTok:** je Kampagne eigener Code (`rabattcode anlegen --zufall INSTA --prozent 10 --bis …`), so sieht man, was verkauft.
4. **Google Merchant Center „Angebote“ (Promotions):** den öffentlichen Code dort als Angebot anlegen (erscheint als „Sonderangebot“ in Shopping). Braucht Merchant-Freigabe (`45-MERCHANT-CENTER.md`).
5. **Nach 4 Wochen (~01.12.):** Einlösungen vs. Bestellungen ohne Code ansehen. Kaufen fast alle mit Code, ist 10 % de facto der Preis → dann Code im Hero durch „Versand frei/Geschenkverpackung“ ersetzen oder Code nur noch für Newsletter.
