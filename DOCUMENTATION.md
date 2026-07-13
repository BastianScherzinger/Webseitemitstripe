# Luviq Universe – Projektdokumentation
**Stand:** 2026-05-25 | Django 5+ | Railway | Brevo | Cloudinary

---

## 1. ARCHITEKTUR-ÜBERSICHT

```
webseitemain/
├── mainweb/              Django-Projekt (settings, urls, wsgi)
├── shop1/                Einzige App
│   ├── views/            Views-Package (aufgeteilt in Module)
│   │   ├── __init__.py   Re-exportiert alle Views für urls.py
│   │   ├── shop.py       startseite, produkte, produkt_detail, kontakt, werbung_klick
│   │   ├── auth.py       login, logout, register, verify_email, profil, change_password
│   │   ├── cart.py       warenkorb, add_to_cart, remove_from_cart, update_cart
│   │   ├── checkout.py   checkout, payment, paypal_capture, payment_success, payment_cancel
│   │   ├── legal.py      impressum, datenschutz, agb, robots_txt, sitemap_xml, newsletter
│   │   └── gaestebuch.py gaestebuch, comment_add, comment_like, comment_delete
│   ├── models.py         Alle Modelle
│   ├── admin_views.py    Admin-Panel Views (geschützt durch admin_required)
│   ├── context_processors.py  shop_owner_check + werbung_aktiv
│   ├── middleware.py     PageVisitMiddleware (Geo-IP, Background-Thread)
│   ├── routers.py        WerbungRouter (pystore-Datenbank)
│   ├── utils.py          Hilfsfunktionen mit logging
│   └── static/shop1/     CSS, JS, Bilder, manifest.json
├── templates/
│   ├── base.html         Haupt-Layout (Navbar, Footer, Schema.org)
│   └── shop1/            Alle Shop-Templates
└── .env                  Lokale ENV-Variablen (nicht in Git)
```

### Request-Flow
```
Browser → Railway Proxy (HTTPS) → Gunicorn → Django
→ SecurityMiddleware → WhiteNoise → SessionMiddleware
→ CsrfViewMiddleware → AuthenticationMiddleware
→ axes.AxesMiddleware → MessageMiddleware
→ shop1.PageVisitMiddleware  (zählt Besuche, enriched mit Geo-IP im Background)
→ View-Funktion → Template → Response
```

---

## 2. MODELLE

### Produkt
```python
class Produkt(models.Model):
    name         # CharField
    beschreibung # TextField
    preis        # DecimalField
    bild         # ImageField (Cloudinary in Production)
    lagerbestand # PositiveIntegerField
    ist_aktiv    # BooleanField
```

### Bestellung (DENORMALISIERT – kein FK zu Produkt)
```python
class Bestellung(models.Model):
    user             # ForeignKey(User)
    status           # neu → bezahlt → versendet → abgeschlossen
    zahlungsart      # bank / paypal
    # Denormalisierte Produktdaten (gespeichert bei Bestellung):
    # CartItem.produkt_name, CartItem.preis → strings, keine FKs
```

**Wichtig:** `CartItem` speichert `produkt_name` und `preis` als Strings, nicht als FK. Das verhindert, dass gelöschte Produkte alte Bestellungen kaputt machen.

### PageVisit
```python
class PageVisit(models.Model):
    ip_adresse  # CharField
    user_agent  # TextField
    pfad        # CharField (URL-Pfad)
    land        # CharField (ISO, via ip-api.com)
    stadt       # CharField
    zeitpunkt   # DateTimeField(auto_now_add=True)
```

### Werbung + WerbungStat
- `Werbung` – Werbeanzeigen (titel, bild, url, aktiv, datum_start, datum_ende)
- `WerbungStat` – Klick/Impression-Zähler pro Werbung
- Gespeichert in `pystore` Datenbank (via `WerbungRouter`)
- Cache: 60 Sekunden in `LocMemCache`

---

## 3. E-MAIL-FLOWS

### 3.1 SMTP-Konfiguration

```python
# settings.py
USE_SMTP_EMAIL = os.getenv('USE_SMTP_EMAIL', 'False') == 'True'
if USE_SMTP_EMAIL or not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp-relay.brevo.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True  # Port 587
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 3.2 Flow: Banküberweisung-Bestellung

```
Checkout → payment() View
→ Order erstellt mit status='neu', zahlungsart='bank'
→ send_bank_details_email(order) → Kunde bekommt IBAN/BIC/Betrag
→ Admin bekommt Bestellungs-Benachrichtigung
→ Admin setzt status='bezahlt' → Kunde bekommt Bestätigungs-Mail
→ Admin setzt status='versendet' → Kunde bekommt Versand-Mail
```

### 3.3 Flow: PayPal-Bestellung

```
checkout() → payment() → paypal_capture()
→ PayPal-SDK verifiziert Zahlung
→ Order erstellt mit zahlungsart='paypal', status='bezahlt'
→ send_order_confirmation_email(order)
→ Redirect zu payment_success
```

### 3.4 E-Mail-Verifikation bei Registrierung

```
register() → EmailVerificationToken erstellen
→ Token per E-Mail senden (verify_email-Link)
→ verify_email() prüft Token → User wird aktiviert
→ Login möglich
```

---

## 4. ADMIN-GUIDE

### Wer ist Admin?
- `is_superuser=True` ODER `user.username == os.getenv('ADMIN_USERNAME')`
- Geprüft durch `context_processors.shop_owner_check`
- Admin-Panel URL: aus ENV-Variable (nicht `/admin/`)

### Admin-Funktionen (admin_views.py)
- Dashboard: Statistiken, letzte Bestellungen, Besucher-Logs
- Produkt-Management: Erstellen, Bearbeiten, Löschen, Bild-Upload
- Bestellungs-Management: Status ändern, Kunden-Infos, Zahlungs-Status
- Werbungs-Management: Neue Werbung, Klick-Statistiken
- Nutzer-Management: Liste, Details, Rollen

### shop_owner_check Context-Processor
```python
# Injiziert in jedes Template:
# is_shop_owner: bool (Admin-Check)
# werbung_aktiv: list (gecachte aktive Werbungen, 60s)
```

---

## 5. DEPLOYMENT (RAILWAY)

### Start-Sequenz
```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn mainweb.wsgi:application --bind 0.0.0.0:$PORT
```

### ENV-Variablen (Railway)
```
SECRET_KEY=<64-zeichen>
DEBUG=False
DATABASE_URL=postgresql://...
PYSTORE_DATABASE_URL=postgresql://... (optional, Werbungs-DB)
ALLOWED_HOSTS_EXTRA=<custom-domain>
ADMIN_USERNAME=<admin-name>
CLOUDINARY_URL=cloudinary://<key>:<secret>@<cloud>
USE_SMTP_EMAIL=True
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_HOST_USER=<brevo-email>
EMAIL_HOST_PASSWORD=<brevo-smtp-key>
DEFAULT_FROM_EMAIL=noreply@luviq-shop.de
SITE_URL=https://luviq-luisa-production.up.railway.app
PAYPAL_CLIENT_ID=<paypal-client-id>
```

### Cloudinary
- Media-Files (Produktbilder) → Cloudinary CDN
- Static-Files → WhiteNoise (via ManifestStaticFilesStorage)
- Cloudinary-URL wird von `django-cloudinary-storage` geparst

---

## 6. BEKANNTE QUIRKS

### Zwei-Datenbank-Setup
```python
# settings.py
DATABASES = {
    'default': ...,       # Shop-Daten
    'pystore': ...,       # Werbungs-Daten (cross-site)
}
DATABASE_ROUTERS = ['shop1.routers.WerbungRouter']
```
`WerbungRouter` leitet `Werbung` und `WerbungStat` Models in die `pystore`-Datenbank.

### CartItem denormalisiert
```python
# CartItem speichert keine FK zu Produkt:
produkt_name = models.CharField(...)  # String-Kopie
preis = models.DecimalField(...)      # Preis-Kopie zum Bestellzeitpunkt
```
→ Gelöschte Produkte brechen keine alten Bestellungen.

### PageVisitMiddleware
```python
# Macht HTTP-Request zu ip-api.com im Background-Thread
# → Blockiert NIEMALS den Response
# → Geo-Daten kommen asynchron in die DB
```
**Kein E-Mail-Versand pro Besuch (Stand 2026-07):** Früher verschickte die
Middleware pro (vermeintlich neuem) Besucher eine Admin-Mail via Brevo. Das
führte trotz Bot-Filter/Session-Dedup zu einer Mail-Flut (Clients/Bots ohne
Cookies gelten bei jedem Hit als „neu") und überlastete Brevo. `_notify_admin`
und der Aufruf-Block wurden komplett entfernt. Besuche werden weiterhin still
in `PageVisit` (Tagesstatistik) und `VisitorLog` (Dashboard, inkl. Geo-IP)
protokolliert — nur ohne jegliche E-Mail. Admin-Mails gibt es nur noch
nutzergetriggert (Kontaktformular, Bestellungen).

### Werbungs-Cache
```python
# context_processors.py
cache.set('werbung_aktiv_list', werbung_aktiv, 60)  # 60s LocMemCache
# Impression-Counting NICHT im Context-Processor (war ein Bug)
# Impressionen werden nur in startseite() View gezählt
```

---

## 7. SEO (SCHEMA.ORG JSON-LD)

### Sitewide (base.html)
- `Organization` + `ClothingStore` (Gründerin: Luisa Brehler)
- `WebSite` Schema

### Pro Seite
- `index.html` → `ItemList` (aktuelle Produkte)
- `produkt_detail.html` → `Product` (mit Preis, Verfügbarkeit, Bild) + `BreadcrumbList`

### Ziel
- Google Knowledge Panel für "Luviq Universe"
- Rich Snippets in Google Shopping
- Google Maps / Local Knowledge Graph (ClothingStore)

---

## 8. PERFORMANCE

### Static Files
- `ManifestStaticFilesStorage` → Content-Hash im Dateinamen (Cache-Busting)
- WhiteNoise → komprimiert und cached Static Files
- `defer` auf alle externen Scripts (HTMX, Alpine.js)

### Bilder
- Produktbilder auf Cloudinary CDN
- `loading="lazy" decoding="async"` auf alle nicht-LCP-Bilder
- Erstes Produktbild: `loading="eager" fetchpriority="high"`

### Caching
- Werbungs-Liste: 60s in `LocMemCache`
- N+1 Fixes: `select_related` / `prefetch_related` in allen list-Views
- Bulk-Fetch in Checkout-E-Mails (statt pro-Item-Query)

### 3D Hero (Three.js)
- Nur auf Desktop (>= 640px)
- `prefers-reduced-motion: reduce` → Three.js deaktiviert
- `setPixelRatio(min(devicePixelRatio, 1.5))` → kein 2x auf Retina
- `antialias: false` → bessere Performance

---

## 9. SICHERHEIT

- `django-axes`: 10 Versuche, 1h Sperre, Username+IP-basiert
- `AXES_LOCKOUT_TEMPLATE`: eigene Lockout-Seite
- HSTS: 1 Jahr, inkl. Subdomains, Preload
- CSRF: Secure-Cookie, SameSite=Lax
- CSP: per settings-Variable, angepasst pro Deployment
- X-Frame-Options: DENY
- `SECURE_REFERRER_POLICY`: strict-origin-when-cross-origin
- Email-Header-Injection-Schutz in Kontaktformular

---

*Dokumentation erstellt: 2026-05-25*
