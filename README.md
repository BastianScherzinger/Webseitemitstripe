# Luviq Universe — Onlineshop

Vollständiger Onlineshop für handbemalte Second-Hand-Mode aus Alsfeld. Django 5, live unter **[luviq-alsfeld.com](https://www.luviq-alsfeld.com)**.

Das war das erste Projekt, das ich für eine andere Person gebaut habe — und der Punkt, an dem aus „ich programmiere für mich" ein Projekt mit echten Nutzern, echten Bestellungen und echter Verantwortung wurde.

> **Zum Repository-Namen:** Der Name `Webseitemitstripe` stammt aus einer frühen Planungsphase. Bezahlt wird über **PayPal**, Stripe ist nicht eingebunden. Der Name bleibt vorerst, weil bestehende Verweise sonst brechen.

---

## Funktionsumfang

**Shop** — Produktübersicht, Detailseiten, Warenkorb mit Mengenänderung, Checkout mit PayPal-Abwicklung inklusive Erfolgs- und Abbruchbehandlung.

**Konten** — Registrierung mit E-Mail-Verifizierung, Anmeldung, Profilverwaltung, Passwortänderung. Brute-Force-Schutz über `django-axes`.

**Rechtliches und SEO** — Impressum, Datenschutz, AGB, `robots.txt` und `sitemap.xml` werden aus dem Bestand erzeugt, dazu Newsletter-Anmeldung.

**Medien** — Produktbilder liegen bei Cloudinary, nicht im Repository. Dadurch bleibt das Deployment schlank und Bilder werden ausgeliefert, ohne den Anwendungsserver zu belasten.

---

## Aufbau

```
mainweb/            Django-Projekt (settings, urls, wsgi, asgi)
shop1/
  views/            nach Zuständigkeit getrennt statt einer grossen views.py
    shop.py         Startseite, Produkte, Detailseiten, Kontakt
    auth.py         Registrierung, Anmeldung, Verifizierung, Profil
    cart.py         Warenkorb
    checkout.py     Checkout, PayPal, Erfolg und Abbruch
    legal.py        Impressum, Datenschutz, AGB, robots.txt, sitemap.xml
  middleware.py     eigene Middleware
  signals.py        Ereignisbehandlung
  routers.py        Datenbank-Routing
  management/       eigene manage.py-Befehle
```

Die Aufteilung der Views in ein Package war die Entscheidung, die sich am meisten ausgezahlt hat. In der ersten Fassung lag alles in einer Datei; ab etwa tausend Zeilen war jede Änderung eine Sucherei.

---

## Technik

`Django 5` · `PostgreSQL` · `PayPal` · `Cloudinary` · `Brevo` (E-Mail-Versand) · `django-axes` · `Gunicorn` · `Whitenoise` · `Docker` · Railway

---

## Was ich heute anders machen würde

- **Keine Tests.** Bei einem Shop, der Bestellungen und Zahlungen verarbeitet, ist das die Lücke, die mich am meisten stört. Checkout und Warenkorb gehören als Erstes abgesichert.
- **Bestellstatus** ist knapp modelliert — für Rücksendungen und Teilstornos reicht das nicht.
- **Konfiguration** liegt teils in `settings.py` statt durchgehend in Umgebungsvariablen.

---

## Einrichtung

```bash
pip install -r requirements.txt
cp .env.example .env      # Datenbank, PayPal, Cloudinary, Brevo eintragen
python manage.py migrate
python manage.py runserver
```

Weitere Details in `DOCUMENTATION.md`, Deployment-Hinweise in `railway_deployment_tutorial.html` und `paypal_sandbox_tutorial.md`.

---

Gebaut von [Bastian Scherzinger](https://github.com/BastianScherzinger).
