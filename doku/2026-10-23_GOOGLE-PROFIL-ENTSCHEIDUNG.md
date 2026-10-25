---
titel: Entscheidungsvorlage Google-Profil und Domain
stand: 2026-10-23
status: Vorlage – Entscheidung bei Bastian und Luisa
---

# Google-Profil und Domain für Luviq – Entscheidungsvorlage (23.10.2026)

**Frage (Bastian, 22.10.2026):** zwei Webseiten, zwei Google-Profile – funktioniert das, dürfen wir das, lohnt es sich?

## Empfehlung in drei Sätzen

1. **Kein zweites Google-Profil**: Google erlaubt ein Profil je Unternehmen, und ein reines Online-Label ohne persönlichen Kundenkontakt ist nach Googles eigener Richtlinie gar nicht profilberechtigt – ein zweites Profil wäre eine Dublette und gefährdet beide.
2. **Das bestehende Profil nur behalten, wenn Luisa ab 01.11. wirklich persönlichen Kontakt anbietet** (z. B. Übergabe oder Anprobe in Lübeck nach Termin) – dann dieses eine Profil auf Lübeck umstellen, als Servicegebiet **ohne sichtbare Wohnadresse**, Name nur „Luviq“; sonst nicht weiter ausbauen und stattdessen ab Verkaufsstart das Google Merchant Center (kostenlose Produkteinträge) nutzen.
3. **Eine Domain, nicht zwei**: Hauptdomain wird `www.luviq-luebeck.com`, aber erst **zusammen mit dem Impressum aus dem Generator** (frühestens 01.11.); `luviq-alsfeld.com` leitet dann jede Seite per 301 dorthin, mindestens ein Jahr.

## Ausgangslage (belegt)

| Punkt | Stand | Beleg |
|---|---|---|
| Google-Profil „Luviq“ | Adresse Grünberger Str. 16, 36304 Alsfeld; ob Google es bestätigt hat: unbekannt | `doku/50-LOCAL-SEO.md`, `shop1/luviq_daten.py` (`GOOGLE_PROFIL`) |
| Gewerbe | „Luviq“, Hansestadt Lübeck, Beginn 01.11.2026, Nebenerwerb, eingereicht 22.10.2026 | `Buero\luisa\wissen\DOKUMENTE.md` |
| Geschäftsart | Online-Label: Second-Hand-Teile mit Bleiche bemalt, Versand per Post, **kein Ladengeschäft**, keine Telefonnummer | Seite live, `doku/00-STATUS.md` |
| Domains | `www.luviq-alsfeld.com` Hauptadresse; `luviq-luebeck.com` und `www.` antworten am 22.10.2026 mit **200 als Kopie** (canonical zeigt auf Alsfeld) | curl 22.10.2026; `Buero\luisa\planung\DOMAIN-LUEBECK-PLAN.md` |
| Widerspruch | `DOKUMENTE.md` sagt „Domain Lübeck: nur Vorschlag, nichts gekauft“, die Domain ist aber live → bitte dort berichtigen | – |
| Impressum | nennt noch die Alsfelder Anschrift; Luisa ist laut eigener Antwort (22.10.) in Lübeck gemeldet | `GEWERBE-UND-RECHT-START-2026-10-22.md` Z. 13, 105 |

## Was Google vorschreibt (Primärquellen, abgerufen 23.10.2026)

| Regel | Wortlaut | Quelle |
|---|---|---|
| Berechtigung | „To qualify for a Business Profile on Google, a business must make in-person contact with customers during its stated hours.“ | [Overview of Google Business Profile policies](https://support.google.com/business/answer/13762416) |
| Nicht berechtigt | „Brands, organizations, artists, and other online-only businesses.“ | ebd. |
| Ein Profil je Unternehmen | „There should only be one profile per business“ · „Do not create more than one page for each location of your business, either in a single account or multiple accounts.“ | [Richtlinien für die Darstellung Ihres Unternehmens](https://support.google.com/business/answer/3038177) |
| Echte Adresse | „Create your Business Profile for your actual, real-world location.“ | ebd. |
| Servicegebiet | „If you’re a service-area business, you should hide your business address from customers.“ | ebd. |
| Name | „Including unnecessary information in your business name isn't permitted“ – also **„Luviq“**, nicht „Luviq Lübeck“ | ebd. |
| Domainumzug | 301/308 verwenden; Adressänderungs-Tool nur bei Domainwechsel; Weiterleitungen „generally at least 1 year“; Neuordnung dauert bei mittleren Seiten „a few weeks or more“ | [Site moves with URL changes](https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes) |
| Statt Profil für Online-Shops | kostenlose Produkteinträge in Suche, Shopping, Bilder, Maps; Voraussetzung u. a. Rückgabebedingungen auf der Website und im Merchant Center, Versand eingerichtet (Pflicht für Deutschland) | [Merchant Center: Produkteinträge](https://support.google.com/merchants/answer/9199328?hl=de) |

## Die einzelnen Fragen

**Darf Luviq ein Profil haben?** Nur mit persönlichem Kundenkontakt zu angegebenen Zeiten. Reiner Versand reicht nicht – Google nennt „online-only businesses“ und „artists“ ausdrücklich als nicht berechtigt. Berechtigt wäre Luviq, wenn Luisa z. B. Abholung, Übergabe oder Anprobe in Lübeck zu festen Zeiten oder nach Termin anbietet (dann Servicegebiet „Lübeck“, Adresse ausgeblendet) – **nur, wenn sie das wirklich tut**. Das entscheidet Luisa, nicht die Agentur.

**Zweites Profil für Lübeck neben Alsfeld?** Nein. Gleiche Marke, eine Person, kein zweiter Standort mit Kundenkontakt = Dublette. Folge im schlechtesten Fall: Sperrung, Bestätigungsschleifen, und das betrifft dann auch das erste Profil.

**Umzug des bestehenden Profils?** Wenn ein Profil, dann dieses eine bearbeiten (Adresse Lübeck, Adresse ausblenden, Einzugsgebiet Lübeck), nicht neu anlegen. Erst ab dem tatsächlichen Start (01.11.), weil eine Adressänderung meist eine neue Bestätigung (oft per Video) auslöst – vorher wäre die neue Angabe noch nicht wahr. Wichtig für Luisa: ohne Ausblenden stünde ihre **Wohnadresse öffentlich in Google Maps**.

**Nutzen gegen Risiko.** Nutzen klein: Luviq lebt von Instagram, TikTok und der Google-Suche nach Marke und Motiv, nicht von „in der Nähe“-Suchen; Bewertungen gibt es bisher keine. Risiko real: Richtlinienverstoß, Sperrung, öffentliche Privatadresse, Pflegeaufwand. **Mehr bringen nach dem Verkaufsstart:** Merchant Center (kostenlose Produkteinträge) und eine saubere Domain mit Search Console.

**Zwei Webseiten?** Zwei Domains mit gleicher Seite sind für Google eine Kopie; es zeigt nur eine und teilt die Signale, statt sie zu verdoppeln. Richtig ist ein Umzug: eine Hauptdomain, die andere leitet jede Seite per 301 weiter. Der Ort im Domainnamen ist kein nennenswerter Rankingfaktor; `luviq-luebeck.com` passt aber zu Gewerbe und Impressum. (Eine ortsfreie Domain würde einen späteren Umzug ersparen – kostet Geld, nur auf Bastians Wunsch prüfen, nichts gekauft.)

## Was im Code vorbereitet ist (Zweig `seo/2026-10-23-luviq-upgrade`, nicht live)

- Neue Railway-Variable **`UMLEITEN_HOSTS`** (Komma-Liste): diese Domains leiten per 301 mit Pfad auf `CANONICAL_HOST`. Leer = aus.
- **Jetzt nicht** `UMLEITEN_HOSTS=luviq-luebeck.com` setzen, wenn der Umzug in den nächsten Wochen kommt: Browser merken sich 301 sehr lange, eine spätere Gegenrichtung (Alsfeld → Lübeck) liefe bei Testgeräten im Kreis. Bis zum Umzug genügt das canonical.
- **Am Umzugstag:** `CANONICAL_HOST=www.luviq-luebeck.com`, `UMLEITEN_HOSTS=luviq-alsfeld.com` (deckt `www.` mit ab). Wird der Umzug verworfen: `UMLEITEN_HOSTS=luviq-luebeck.com`.
- **Nachtrag 23.10.2026 (Tag):** Impressum, Datenschutz und alle Texte sind im selben Zweig auf Lübeck umgestellt (Sitz Lübeck, Herkunft Alsfeld), unabhängig von der Domain. `canonical` bleibt auf `CANONICAL_HOST`; das Schema verweist per `sameAs` weiter auf das Alsfelder Google-Profil, bis Luisa entschieden hat.

## Was freigegeben werden muss

| Wer | Was |
|---|---|
| Luisa | Bietet sie ab 01.11. persönlichen Kontakt (Übergabe/Anprobe) an? Ja → Profil umstellen. Nein → Profil nicht ausbauen. |
| Luisa | Impressum/Datenschutz mit Lübecker Anschrift aus dem Generator freigeben (Agenturregel 3). **Stimmt die Alsfelder Anschrift heute noch?** Wenn nicht, ist das Impressum schon jetzt falsch. |
| Bastian | Termin für den Domainumzug (Railway-Variablen, Search Console Adressänderung, Bing Site Move). |
| Bastian | Im Profil nachsehen, ob es bestätigt ist; nichts ändern, bevor Luisa entschieden hat. |
