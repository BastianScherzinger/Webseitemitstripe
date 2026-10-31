---
bereich: anleitung
titel: Neues Stück anlegen (zweites, drittes … Stück)
stand: 2026-10-31
status: vollständig
zusammenfassung: Wie ein weiteres Unikat in den Shop kommt – Daten, Bilder, Befehl, Prüfung. Direktkauf und Reservierung laufen für jedes aktive Stück von selbst.
---

# Neues Stück anlegen

Der Direktkauf (`views/direktkauf.py`) braucht nichts Stückspezifisches: Jedes **aktive**, nicht vergebene
Stück mit Lagerbestand 1 und vollständigen Pflichtangaben (`Produkt.kaufbar`) zeigt auf seiner Seite das Formular
„Zahlungspflichtig bestellen“; die Karte in der Übersicht trägt den Preis „inkl. Versand“.

## Weg A: im Django-Admin (Luisa oder Bastian, ohne Code)
1. Admin → Produkte → Hinzufügen. Pflicht: **Name, Preis** (Gesamtpreis inkl. Versand, Dezimalpunkt), **Größe/Maße** (`masse`, z. B. „Größe M“; Zentimeter erst eintragen, wenn gemessen), **Material** (Faserzusammensetzung, z. B. „100 % Baumwolle“ – bei neuen Textilien Pflicht, sonst nicht kaufbar), **Zustand** („Neu“ oder „Gebraucht (Second Hand) …“), **Technik** („Mit Bleiche von Hand gemalt“).
2. Lagerbestand **1**, „aktiv“ an, „Archiv (vergeben)“ aus. Nummer leer lassen = nächste freie Nº.
3. Bilder: Hauptbild hochladen (geht über Cloudinary); weitere Fotos als **Zusatzbilder** (Reihenfolge `position`; „KI-Studiobild“ nur ankreuzen, wenn es eines ist). Format **4:5 hochkant**, Hauptbild mind. 800 × 1000 px, Zusatzbilder 960 × 1200 px, WebP oder JPG.
4. Speichern. Der Slug entsteht aus dem Namen, die Seite steht unter `/produkt/<slug>/`.

## Weg B: als Code (Bilder liegen im Repo, wie beim Engel-Shirt)
1. Daten in `shop1/luviq_daten.py` als eigenes Dict nach dem Muster von `ENGEL_STUECK` (slug, name, preis, masse, material, technik, zustand, seo_*, beschreibung, `bild_statisch`, `zusatzbilder`).
2. Bilder als WebP-Reihe unter `shop1/static/shop1/images/stuecke/` (Breiten 600/900/960 bzw. 480/640/800), Schreibweise `pfad-{w}.webp@600,900,960#960x1200`.
3. Befehl nach dem Muster von `shop1/management/commands/luviq_engel_anlegen.py` (idempotent, überschreibt nichts), in `start.sh` eintragen.
4. Danach `python manage.py collectstatic --noinput` und `python manage.py pruefe_seite`.

## Prüfen
- `/produkte/` zeigt beide Karten sauber untereinander (390 px: zwei Spalten) – geprüft am 31.10.2026 mit Testdaten, Bild `screens-direktkauf/08-uebersicht-2-stuecke-390.png`.
- Stückseite: Formular sichtbar, Gesamtpreis über dem Knopf, Galerie wischt.
- Neues Stück in `shop1/seiten_stand.py`/Sitemap: kommt aus der Datenbank, nichts nachzutragen.
- Ein verkauftes Stück: nach Zahlungseingang im Admin „Archiv (vergeben)“ ankreuzen (Bestellung Status „Bezahlt“). Eine nicht bezahlte Bestellung gibt das Stück frei, wenn ihr Status auf „Abgebrochen“ steht (die Reservierung löscht der Code nicht selbst, siehe `RESERVIERUNG_TAGE`).
