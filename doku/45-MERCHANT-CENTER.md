---
stand: 2026-11-01
status: Anleitung bereit, Konto noch nicht angelegt (macht Luisa oder Bastian)
zusammenfassung: Kurzanleitung für das Google Merchant Center von luviq-luebeck.com; was die Seite schon liefert, was von Hand eingetragen werden muss.
---

# Google Merchant Center für Luviq

**Wichtig:** Das Konto wurde in der Nacht zum 01.11.2026 **nicht** angelegt. Das erledigt Luisa (Inhaberin) oder Bastian
mit ihrem Einverständnis. Die Seite ist vorbereitet: Das Produkt-Schema auf jeder kaufbaren Stückseite liefert Preis,
Lieferbarkeit, Versand und Rückgabe in der Form, die Google für Händlereinträge liest.

## Was die Seite schon liefert (Product-JSON-LD, `shop1/templates/shop1/produkt_detail.html`)

| Angabe | Wert beim Engel-Shirt Nº 006 |
|---|---|
| Name, Beschreibung, Bilder | aus dem Stück, Bilder als absolute Adressen |
| Marke | `Brand`: Luviq |
| Größe (`size`) | M (aus dem Feld „Maße“) |
| Material | 100 % Baumwolle |
| Zustand | gebraucht (`UsedCondition`), Second Hand |
| Preis / Währung | 69,00 EUR, Endpreis, nach § 19 UStG ohne Umsatzsteuer |
| Verfügbarkeit | `InStock`, solange das Stück `kaufbar` ist (Serienstück bleibt nach einer Bestellung bestellbar) |
| Versand | Deutschland, 0 EUR (im Preis enthalten), Bearbeitung 3 Werktage, Laufzeit 1–2 Werktage |
| Rückgabe | gesetzliches Widerrufsrecht, 14 Tage, Rücksendung per Post, Deutschland |

Prüfen: <https://search.google.com/test/rich-results> mit der Stückadresse, oder in der Search Console unter „Händlerlisten“.

## Schritte im Merchant Center

1. Mit dem Google-Konto der Inhaberin unter <https://merchants.google.com> ein Konto anlegen. Land Deutschland, Währung EUR.
2. Unternehmensangaben wie im Impressum (Luisa Brehler, Luviq, Anschrift laut Gewerbeanmeldung 22.10.2026). Kontakt: `brehlerluisa@gmail.com`.
3. Website `https://www.luviq-luebeck.com` eintragen und bestätigen. Die Search Console ist bereits bestätigt (Meta-Tag im Kopf der Seite), die Bestätigung lässt sich dort übernehmen.
4. Versand einstellen: Deutschland, kostenlos, Bearbeitungszeit 3 Werktage, Lieferzeit 1–2 Werktage (insgesamt höchstens 5 Werktage wie in AGB § 5).
5. Rückgabe einstellen: 14 Tage, Rücksendung per Post, gesetzliches Widerrufsrecht. Keine längere oder kürzere „Rückgabegarantie“ versprechen. **Nie** „Rückgabe ausgeschlossen“ eintragen: Verbrauchern steht der Widerruf zu (§ 312g BGB).
6. Steuern: Kleinunternehmer nach § 19 UStG, Preise ohne Umsatzsteuerausweis.
7. Produkte: entweder die Stückseite von Google automatisch auslesen lassen (Schema, siehe oben) oder das Stück von Hand anlegen: Zustand „gebraucht“, keine GTIN („Kennung nicht vorhanden“), Marke Luviq, Größe M, Farbe Schwarz, Geschlecht und Altersgruppe nach Luisas Angabe.
8. Kostenlose Einträge („Free listings“) aktivieren. Anzeigen sind ein eigener, späterer Schritt.

## Fallen

- Preis und Verfügbarkeit im Merchant Center müssen mit der Seite übereinstimmen, sonst lehnt Google ab. Ändert Luisa den Preis im Admin, ändert sich das Schema sofort mit; im Merchant Center ggf. nachziehen.
- Fotos: Das Hauptbild ist ein **Studiobild (KI)** aus dem echten Foto und ist als solches gekennzeichnet. Für Google Shopping sind echte Produktfotos besser; das echte Foto liegt als zweites Bild in der Galerie.
- Maße: Es gibt keine gemessenen Maße. „Maße auf Anfrage“ steht so auf der Seite; Maße nicht erfinden.
