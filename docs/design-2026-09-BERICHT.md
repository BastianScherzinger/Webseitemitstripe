# Umbau „Nachtausgabe" – Bericht (19.09.2026)

Grundlage: `C:\Users\basti\Desktop\Webagentur Scherzinger\Design\luviq\FINALER-BAUPLAN.md`
(verbindlich), Vorlage `…\Design\luviq\vorlage\luviq-final.html` mit Aufnahmen,
Markenwissen `…\Design\luviq\MARKENWISSEN-luisa.md` (Luisas Befragung vom 19.09.2026).
Gebaut im Zweig `design/2026-09-b3-panorama` (Worktree `webseiten buisnes\luviq-design`).

## Was gebaut ist

**Fundament**
- `shop1/static/shop1/luviq.css`: Tokens auf `:root` (Grund `#0A0A0A`/`#131211`, Text
  `#F2EEE6`, leise `#9C968C`, Linien, **ein** Akzent `--lv-akzent` `#C8763F`, Kachel
  `#E8E1D6`). Radius 0, keine Schatten, keine Verläufe, kein Glas, kein Glühen.
  Desktop 1:1 zur Vorlage über `--u: min(1vw, 14.4px)`, unter 1024 px feste Werte aus dem
  Handy-Rahmen.
- Schriften **selbst gehostet** (`shop1/static/shop1/fonts/`, OFL daneben):
  Cormorant Garamond kursiv 500, Schibsted Grotesk 400–700, JetBrains Mono 400–500.
  Zugeschnitten mit `tools/schriften_zuschneiden.py` (Quellen in `_quellen/schriften/`),
  Ersatzschriften mit gerechneten Metriken, Preload nur Cormorant + Schibsted.
  **Google Fonts ist raus** (Rechtsbefund RE07 erledigt), auch aus `CSP_QUELLEN`.
- `shop1/luviq_daten.py`: Markensatz, Lead, Laufband, Drop (`DROP_TERMIN`, `DROP_NUMMER`),
  Teaser, Auswahl der Anfrage, fünf Schritte, Luisas Satz. Kein Datum in Vorlagen.
- `templates/base.html`: Laufband, Kopf (Wortmarke, „Motiv anfragen" zuerst, Instagram,
  Konto), Handy-Menü als `<details>` (ohne JavaScript bedienbar), Fuß mit großer Wortmarke,
  Handy-Leiste „Eigenes Motiv? Kostet nichts". **Entfernt:** Three.js-Partikel, GSAP,
  Nebel, Glas, Scroll-Fortschritt, 3D-Kartenkippen, alte untere Navigation.
  Tailwind + `style.css` + Alpine laden nur noch auf den Seiten, die ihr Markup brauchen
  (Konto, Kasse, Gästebuch, Wissen, Rechtstexte, Admin).

**Startseite** in der Reihenfolge der Vorlage: Hero H4 (Kopfzeile, Panorama 21:9 / Handy 4:5
ohne Text, Bildunterschrift mit Archivnummer, H1 = Markensatz, Lead, Knopf, Drop-Kasten mit
Countdown und „Vormerken" = Newsletter mit Double-Opt-in) · Motiv anfragen (drei Zeilen,
sechs Richtungen als Links auf `/motiv-anfragen/?richtung=…`) · „Nº …, in Teilen" (entfällt,
solange `TEASER` leer ist) · fünf Schritte (Handy: seitlich wischen) · Archiv-Raster ·
Luisa-Zitat · Warteliste · Fuß.

**Motiv anfragen (Stufe 1)**: Seite `/motiv-anfragen/` + Danke-Seite (noindex), Modell
`Motivanfrage` (Migration `0023`), Django-Admin + Liste im Panel `/shop-admin/motivanfragen/`
mit Status neu / in Arbeit / erledigt. Spamschutz wie Kontakt (Falle, Zeitstempel, Punkte,
Drossel je IP, Doppelt-Sperre), erst speichern, dann mailen – **nur an Luisa**
(`MOTIV_EMPFAENGER`, sonst `ADMIN_EMAIL`), **nie** an die eingetippte Adresse. Kein Preis,
keine Zahlung, keine Zusage. Schalter `MOTIVANFRAGE_AKTIV` (Vorgabe an). Bild-Upload bewusst
nicht angelegt.

**Übrige Seiten**: `/produkte/` → „Das Archiv" (nach Nummer sortiert, Text unverändert
darunter), Stückseite (Nummer groß, Name kursiv, Datenliste, beide Verkaufszustände),
`/ueber_uns/` → „Luisa" (ihr Satz, Anfang ohne Legende, fünf Schritte, Anfrage, **kein
Porträt**). Alle anderen Seiten laufen über eine Übersetzungsschicht in `luviq.css`
(`.lv-alt`): Radius 0, keine Schatten/Glas, Überschriften Cormorant, Knöpfe hell, lesbarer
Fließtext. Überschriften auf Deutsch (Kontakt, Gästebuch, Impressum, Datenschutz, AGB,
Anmelden, Konto anlegen).

**Archivnummern**: Feld `Produkt.nummer` (eindeutig), Migration `0024` vergibt die aktiven
Stücke aufsteigend nach `erstellt_am` als 1, 2, 3 …; neue Stücke bekommen beim Speichern die
nächste freie Nummer, der Drop die übernächste freie (`drop_nummer`). Die Doppelbelegung
„Nº 006" ist damit weg. Dazu optionale Felder `material`, `technik`, `masse` für die
Datenliste der Stückseite.

## Nebenbefunde, gleich behoben

- `kontakt.html`: ein mehrzeiliger `{# … #}`-Kommentar stand **sichtbar** auf der Live-Seite
  (Django kennt `{# #}` nur einzeilig) → `{% comment %}`.
- `kontakt.html` zeigte das alte freigestellte Foto von Luisa → entfernt (Markenwissen § 9).
- Datenschutz und Wissensbeitrag „Konto und Daten" nannten Google Fonts und die Karte „auf der
  Startseite" – beides nicht mehr eingebunden → gestrichen.
- Englische Überschriften/Knöpfe („Get in Touch", „Guest Book", „Legal Notice", „Initiate
  Access", „Post to Orbit" …) auf den öffentlichen Seiten → deutsch.

## Tests und Prüfungen

- Volle Suite **383 Tests grün** (vorher 357; neu `test_motivanfrage` mit 26 Tests: Anzeige,
  Vorbelegung, Pflichtfelder, eins von beiden, Spam still verworfen, Mail nur an Luisa, keine
  Mail an die Absenderin, Maskierung, Drossel, Schalter aus, Admin).
- **Designwache bewusst neu erfasst** (`aufbau_referenz.json`, 25 Seiten inkl. der zwei
  neuen): jede Seite trägt den neuen Kopf und Fuß.
- Bewusst geänderte Tests: Startseiten-Wortschwelle 655 → 300 (die Vorlage ist knapp, die
  langen Erklärtexte stehen auf Archiv und Luisa), Logo-Alternativtext → sprechbarer Name der
  Wortmarke, Archiv-Überschriften, Karte nur noch im Gästebuch, Google Fonts nicht mehr in der
  Datenschutzerklärung, Fokus-/Bewegungsregeln auch in `luviq.css`.
- `pruefe_seite --streng`: 13 von 13 Sitemap-Adressen 200 (lokal nur Umgebungsfehler:
  Zugangsdaten fehlen in der lokalen `.env`). `pruefe_links --streng`: jeder Verweis kommt an.
- Handy 360/390, Tablet 768, 1024: kein Überlauf; Tippziele ≥ 44 px.
- Kontrast: Text 17,1:1, leise 6,8:1 (auf Grund-2 6,4:1), Akzent 5,8:1, Knopf auf Akzent 5,8:1.
- Formular im Browser leer / ohne Kontakt / voll, Handy und Desktop: Meldung, Auswahl bleibt,
  Danke-Seite, Eintrag gespeichert, Mail nur an Luisa.

## Luisa bitte ansehen / freigeben

1. **Texte** in ihren Worten: Lead („Ich bemale in Alsfeld …"), Abschnitt „Du hast eine
   Idee?", Anfrageseite, Danke-Seite, Seite „Luisa". Alle in `shop1/luviq_daten.py` bzw. den
   Vorlagen, jeder Satz darf geändert werden. *Geändert gegenüber der Vorlage:* „Ein Bild darfst
   du mitschicken" und „meistens innerhalb von ein, zwei Tagen" sind raus (Upload gibt es noch
   nicht, die Antwortzeit hat Luisa nicht genannt).
2. **Datenschutz**: der Satz zum Kontaktformular nennt jetzt auch „die Motivanfrage"; Google
   Fonts und die Karte auf der Startseite sind aus der Dienstliste gestrichen (Firmenregel § 3:
   Freigabe durch Luisa).
3. **Archivnummern**: Reihenfolge prüfen (Django-Admin → Produkte, Spalte „Nummer" direkt
   änderbar).
4. **Drop-Termin 08.10.2026, 18 Uhr**: bestätigen oder `DROP_TERMIN` in Railway leeren
   (dann „Die nächste Ausgabe ist in Arbeit." ohne Uhr).
5. **Neue Fotos** (Porträt vor echter Wand, Arbeitsfoto): in
   `Webagentur Scherzinger\Design\luviq\fotos-neu\` legen; dann Porträt auf „Luisa" und die
   Entstehungsbilder Schritt 2–4 tauschen.

## Offen, nicht blockierend

- Kasse, Warenkorb, Zahlung und Profil tragen noch „Orbit/Mission"-Texte; sie sind ohne
  Verkauf gesperrt. Vor `VERKAUF_AKTIV=1` sprachlich nachziehen.
- Datenschutzerklärung enthält noch die Wendung „im digitalen Orbit" (Rechtstext, nur mit
  Generator/Freigabe ändern).
- Stückseite: bis zu vier Bilder mit Vorschauleiste braucht ein Bildermodell (heute ein Bild je
  Stück).
- Material/Technik/Maße sind leer, bis Luisa sie im Admin einträgt (leer = Zeile entfällt).
- Bild-Upload in der Anfrage erst nach Datenschutz-Ergänzung; Stufe 2 (Preis, Anzahlung, AGB,
  Widerrufsbelehrung § 312g Abs. 2 Nr. 1 BGB) erst mit Gewerbe; Pinterest-Weg
  (Markenwissen § 10.1) vor dem Verkauf klären.
