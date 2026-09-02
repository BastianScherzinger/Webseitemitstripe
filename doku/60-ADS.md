---
bereich: ads
titel: Google Ads
stand: 2026-09-02
status: nicht zutreffend
zusammenfassung: Es gibt keine Google-Ads-Kampagne und kein Konto; Voraussetzungen für Shopping-/Suchanzeigen sind benannt.
offen: 0
quellen: GOOGLE_SEO_GUIDE.md, templates/base.html
---

# Google Ads — Luviq Universe

## Stand

**Für Luviq Universe gibt es keine Google-Ads-Kampagne, kein Google-Ads-Konto und keine Anzeigen
auf einer anderen Plattform, die dokumentiert wären.** Im Quelltext findet sich kein Conversion-Tag,
kein `gtag`, kein Google Tag Manager, kein Analytics, kein Meta-Pixel (Suche über `templates/`,
`shop1/templates/`, `shop1/static/` am 02.09.2026 ohne Treffer). `GOOGLE_SEO_GUIDE.md` nennt Ads nicht.

Der Bereich zählt im Werkzeug weder als Lücke noch als erfüllt.

## Konto und Zugang

Kein Konto. **Sollte eines entstehen, muss es auf die Betreiberin laufen** (Luisa Brehler), nicht auf
die Agentur: Ein durchgereichtes Werbebudget wäre sonst Umsatz der Agentur und sprengt die
Kleinunternehmergrenze. Bastian höchstens als Nutzer mit Verwaltungsrecht.

## Kampagnen

Keine.

## Messung und Conversions

Keine. Was fehlt, damit überhaupt gemessen werden könnte:

| Voraussetzung | Stand | Regel |
|---|---|---|
| Eigene Danke-/Bestätigungs-URL nach Kontaktformular | fehlt — Meldung auf derselben Seite | KV07 |
| Bestellabschluss als eigene URL | vorhanden: `/payment/success/<order_id>/` (per `robots.txt` gesperrt, was richtig ist) | — |
| Conversion-Tag oder serverseitige Conversion | fehlt; jedes Tag braucht eine Einwilligung (Consent) — es gibt heute **kein Consent-Banner**, weil nichts Einwilligungspflichtiges geladen wird | — |
| Einträge in der Datenschutzerklärung | Ads/Conversion nicht genannt (müsste bei Einführung ergänzt werden) | RE06 |

## Regeln und Sperren

- Kein Konto anlegen, keine Kampagne entwerfen, kein Tag einbauen ohne ausdrücklichen Auftrag der Betreiberin und ohne Konto in ihrem Namen.
- Kein Tracking ohne Consent-Lösung; heute läuft die Seite bewusst ohne Einwilligungsbanner.
- Änderungen am Checkout für Conversion-Messung zählen als Änderung am Zahlungspfad → nur mit Sandbox-Test ([10-TECHNIK.md](10-TECHNIK.md) → Fallen).

### Was für Shopping- oder Suchanzeigen nötig wäre

Ohne Zahlen — keine Budgets, keine Klickpreise geschätzt.

1. **Konto bei der Betreiberin** (Google Ads, bei Shopping zusätzlich Merchant Center), Zwei-Faktor-Anmeldung, Zahlungsmittel der Betreiberin.
2. **Produktdaten:** `Product`/`Offer`-Schema ist auf den Produktseiten vorhanden (Preis, Verfügbarkeit, Bild, Marke); für das Merchant Center zusätzlich ein Produktfeed oder die automatische Feed-Erzeugung aus den strukturierten Daten — nicht vorhanden. Bei 1-of-1-Artikeln muss `availability` sofort auf „ausverkauft" springen, sonst laufen Anzeigen auf verkaufte Stücke; heute filtert der Shop nur nach `aktiv`.
3. **Conversion-Tag** oder serverseitige Messung des Bestellabschlusses (`/payment/success/`) — mit Consent-Banner und Ergänzung der Datenschutzerklärung.
4. **Landingpages:** Kategorieseite `/produkte/` und Produktseiten sind heute dünn (62 bzw. 25 Eigenwörter live); Anzeigen auf dünne Seiten haben schlechte Qualitätsfaktoren.
5. **Rechtliches:** Widerrufsbelehrung mit Muster-Widerrufsformular (RE09), vollständige Datenschutzerklärung (RE06), Telefonnummer oder zweiter Kontaktweg im Impressum (RE03) — Google prüft Shop-Anzeigen auf Rückgabe- und Kontaktangaben.

## Erledigt

Nichts — es gab nie Ads.

## Offen

Nichts offen, solange die Betreiberin keine Anzeigen möchte. Sollte sie es wollen: erst die Punkte
unter „Was nötig wäre", dann ein Konto in ihrem Namen, dann diese Datei mit den Schlüsseln des
Doku-Standards (`konto`, `konto_inhaber`, `conversion_tracking`, …) neu anlegen.
