import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

class UserProfile(models.Model):
    """Extended User Profile mit zusätzlichen Informationen"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Persönliche Daten
    telefon = models.CharField(max_length=20, blank=True, null=True)
    stadt = models.CharField(max_length=100, blank=True, null=True)
    postleitzahl = models.CharField(max_length=10, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    land = models.CharField(max_length=100, blank=True, null=True, default='Deutschland')
    
    # Geburtsdatum
    geburtsdatum = models.DateField(blank=True, null=True)
    
    # Profil Info
    bio = models.TextField(blank=True, null=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)
    
    # Email-Verifikation
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    
    # Marketing
    has_welcome_discount = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Profile von {self.user.username}"
    
    def regenerate_token(self):
        """Generiert einen neuen Verifikations-Token"""
        self.verification_token = uuid.uuid4()
        self.save(update_fields=['verification_token'])
        return self.verification_token
    
    class Meta:
        verbose_name_plural = "User Profiles"


class Subscriber(models.Model):
    """Newsletter Abonnenten"""
    email = models.EmailField(unique=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Produkt(models.Model):
    """Produkt-Modell für den Shop"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    beschreibung = models.TextField(blank=True)
    seo_titel = models.CharField(max_length=60, blank=True, help_text='SEO-Titel (max. 60 Zeichen). Leer = automatisch.')
    seo_beschreibung = models.CharField(max_length=160, blank=True, help_text='Meta-Description (max. 160 Zeichen). Leer = aus Beschreibung.')
    preis = models.DecimalField(max_digits=10, decimal_places=2)
    bild = models.ImageField(upload_to='produkte/', blank=True, null=True)
    aktiv = models.BooleanField(default=True)
    lagerbestand = models.PositiveIntegerField(default=1)
    newsletter_gesendet = models.BooleanField(default=False)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)
    ersteller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='produkte')

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or f"produkt-{self.pk or 'neu'}"
            slug = base
            n = 1
            while Produkt.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        if self.slug:
            return reverse('produkt_detail_slug', args=[self.slug])
        return reverse('produkt_detail', args=[self.id])

    @property
    def meta_title(self):
        if self.seo_titel:
            return self.seo_titel
        return f"{self.name} kaufen – Luviq Universe"

    @property
    def meta_description(self):
        if self.seo_beschreibung:
            return self.seo_beschreibung
        desc = self.beschreibung[:155].rsplit(' ', 1)[0] if len(self.beschreibung) > 155 else self.beschreibung
        return f"{desc} – Einzigartiges 1-of-1 Upcycling-Unikat bei Luviq Universe."

    def __str__(self):
        return f"{self.name} ({self.preis} €)"

    class Meta:
        verbose_name_plural = "Produkte"
        ordering = ['-erstellt_am']


class Cart(models.Model):
    """Warenkorb – wird in der Datenbank persistiert"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Warenkorb von {self.user.username}"
    
    @property
    def gesamt_preis(self):
        return sum(item.gesamt_preis for item in self.items.all())
    
    @property
    def anzahl_items(self):
        return sum(item.menge for item in self.items.all())
    
    class Meta:
        verbose_name = "Warenkorb"
        verbose_name_plural = "Warenkörbe"


class CartItem(models.Model):
    """Einzelnes Produkt im Warenkorb"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    produkt_name = models.CharField(max_length=200)
    produkt_preis = models.DecimalField(max_digits=10, decimal_places=2)
    produkt_bild = models.CharField(max_length=255, blank=True, default='')
    menge = models.PositiveIntegerField(default=1)
    hinzugefuegt_am = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.menge}x {self.produkt_name}"
    
    @property
    def gesamt_preis(self):
        return self.produkt_preis * self.menge
    
    class Meta:
        verbose_name = "Warenkorb-Artikel"
        verbose_name_plural = "Warenkorb-Artikel"


class Order(models.Model):
    """Bestellung mit Zahlungsinformationen"""
    STATUS_CHOICES = [
        ('pending', 'Ausstehend / Unbezahlt'),
        ('paid', 'Bezahlt (Gesehen)'),
        ('processing', 'In Bearbeitung'),
        ('ready_for_shipping', 'Zum Versand bereit'),
        ('shipped', 'Versendet'),
        ('failed', 'Zahlung Fehlgeschlagen'),
        ('cancelled', 'Abgebrochen / Storniert'),
    ]
    
    PAYMENT_METHODS = [
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Überweisung'),
        ('pickup', 'Abholung (Lokal)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    paypal_order_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='paypal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Lieferdaten
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)
    email = models.EmailField()
    adresse = models.CharField(max_length=255)
    stadt = models.CharField(max_length=100)
    postleitzahl = models.CharField(max_length=10)
    land = models.CharField(max_length=100)
    telefon = models.CharField(max_length=20, blank=True)
    
    # Gesamtbetrag
    gesamt_betrag = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Zeitstempel
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bestellung #{self.id} - {self.user.username}"
    
    class Meta:
        verbose_name = "Bestellung"
        verbose_name_plural = "Bestellungen"
        ordering = ['-erstellt_am']


class OrderItem(models.Model):
    """Einzelne Artikel in einer Bestellung"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    produkt_name = models.CharField(max_length=200)
    produkt_preis = models.DecimalField(max_digits=10, decimal_places=2)
    menge = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.menge}x {self.produkt_name} (Bestellung #{self.order.id})"
    
    @property
    def gesamt_preis(self):
        return self.produkt_preis * self.menge
    
    class Meta:
        verbose_name = "Bestellungs-Artikel"
        verbose_name_plural = "Bestellungs-Artikel"


class Werbung(models.Model):
    """Werbebanner – in dieser Datenbank verwaltet, von anderen Sites (tutorials) mitgenutzt."""
    titel = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True, default='')
    link = models.URLField(max_length=500)
    bild = models.CharField(max_length=500, blank=True, default='')
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    laufzeit_tage = models.PositiveIntegerField(default=30)
    ablauf_email_gesendet = models.BooleanField(default=False)
    aktiv = models.BooleanField(default=True)
    impressionen = models.PositiveIntegerField(default=0)
    klicks = models.PositiveIntegerField(default=0)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Werbung'
        verbose_name_plural = 'Werbungen'
        ordering = ['-erstellt_am']

    def __str__(self):
        return self.titel

    @property
    def name(self):
        return self.titel

    @property
    def ausgegeben(self):
        from decimal import Decimal
        imp = Decimal(self.impressionen or 0)
        klk = Decimal(self.klicks or 0)
        return (imp * Decimal('0.0025')) + (klk * Decimal('0.005'))  # 0,25ct/View · 0,5ct/Klick

    @property
    def verbleibendes_budget(self):
        from decimal import Decimal
        budget = self.budget or Decimal('0')
        remaining = budget - self.ausgegeben
        return remaining if remaining > Decimal('0') else Decimal('0')

    @property
    def budget_prozent_genutzt(self):
        from decimal import Decimal
        budget = self.budget or Decimal('0')
        if not budget:
            return 100
        pct = int((self.ausgegeben / budget) * 100)
        return min(pct, 100)

    @property
    def ist_aktiv(self):
        from decimal import Decimal
        budget = self.budget or Decimal('0')
        return bool(self.aktiv) and (budget - self.ausgegeben) > Decimal('0')

    @property
    def bild_src(self):
        """Gibt eine vollständige HTTPS-URL für das Werbungsbild zurück.

        pystore speichert bild als ImageField → Cloudinary public_id (z.B. 'werbung/img.jpg').
        Luviq speichert bild als volle URL. Beide Fälle werden korrekt aufgelöst.
        """
        val = str(self.bild or '').strip()
        if not val:
            return ''
        if val.startswith('http'):
            return val
        # Relativer Pfad → Cloudinary-URL konstruieren
        import os
        from urllib.parse import urlparse
        cloud_name = os.getenv('PYSTORE_CLOUDINARY_CLOUD_NAME', '')
        if not cloud_name:
            for env_key in ('PYSTORE_CLOUDINARY_URL', 'CLOUDINARY_URL'):
                env_val = os.getenv(env_key, '')
                if env_val:
                    try:
                        cloud_name = urlparse(env_val).hostname or ''
                    except Exception:
                        pass
                    if cloud_name:
                        break
        if cloud_name:
            return f'https://res.cloudinary.com/{cloud_name}/image/upload/{val}'
        media_base = os.getenv('PYSTORE_MEDIA_URL', '').rstrip('/')
        if media_base:
            return f'{media_base}/{val}'
        return ''


class WerbungStat(models.Model):
    """Klick-/View-Statistik pro Werbung, Seite und Tag."""
    werbung = models.ForeignKey(Werbung, on_delete=models.CASCADE, related_name='stats')
    seite = models.CharField(max_length=100)
    impressionen = models.PositiveIntegerField(default=0)
    klicks = models.PositiveIntegerField(default=0)
    datum = models.DateField()

    class Meta:
        verbose_name = 'Werbung Statistik'
        verbose_name_plural = 'Werbung Statistiken'
        unique_together = ('werbung', 'seite', 'datum')

    def __str__(self):
        return f"{self.werbung.titel} – {self.seite} ({self.datum})"


class VisitorLog(models.Model):
    """Einzelne Besuchereinträge mit IP, Geo-Daten und Quell-Site."""
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default='')
    country_code = models.CharField(max_length=5, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    path = models.CharField(max_length=255, blank=True, default='')
    user_agent = models.CharField(max_length=500, blank=True, default='')
    seite = models.CharField(max_length=100, blank=True, default='pystore', db_column='site')

    @property
    def country_flag(self):
        code = (self.country_code or '').upper()
        if len(code) == 2 and code.isalpha():
            return chr(0x1F1E6 + ord(code[0]) - 65) + chr(0x1F1E6 + ord(code[1]) - 65)
        return '🌍'

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Besucher Log'
        verbose_name_plural = 'Besucher Logs'

    def __str__(self):
        loc = f"{self.city}, {self.country}" if self.city else (self.country or self.ip_address or 'Unbekannt')
        return f"{loc} – {self.timestamp.strftime('%d.%m.%Y %H:%M')}"


class PageVisit(models.Model):
    """Speichert die Anzahl der Seitenbesuche pro Tag"""
    date = models.DateField(unique=True, verbose_name="Datum")
    visits = models.PositiveIntegerField(default=0, verbose_name="Besuche")

    class Meta:
        verbose_name = "Seitenbesuch"
        verbose_name_plural = "Seitenbesuche"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date}: {self.visits} Besuche"


class Comment(models.Model):
    """Bewertungs- und Kommentar-Modell"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name="Nachricht")
    
    # Für Antworten (Verschachtelung)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    # Likes
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    
    # Metadaten
    is_admin_reply = models.BooleanField(default=False)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kommentar"
        verbose_name_plural = "Kommentare"
        ordering = ['-erstellt_am']

    def __str__(self):
        return f"Kommentar von {self.user.username} ({self.erstellt_am.strftime('%d.%m.%Y')})"
    
    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def is_parent(self):
        return self.parent is None


class PyStoreVisitorLog(models.Model):
    """Unmanaged Proxy — spiegelt luviq-Besucher in die pystore-DB (shop1_visitorlog).

    Wird nur zum Schreiben per .using('pystore') verwendet.
    managed=False → keine eigene Migration, Tabelle existiert bereits in pystore.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True, default='')
    country_code = models.CharField(max_length=5, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    path = models.CharField(max_length=255, blank=True, default='')
    user_agent = models.CharField(max_length=500, blank=True, default='')
    seite = models.CharField(max_length=100, blank=True, default='luviq')

    class Meta:
        managed = False
        db_table = 'shop1_visitorlog'
        app_label = 'shop1'

    def __str__(self):
        return f"{self.seite} – {self.ip_address}"
