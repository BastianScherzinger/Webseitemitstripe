import uuid
from django.db import models
from django.contrib.auth.models import User

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
    beschreibung = models.TextField(blank=True)
    preis = models.DecimalField(max_digits=10, decimal_places=2)
    bild = models.ImageField(upload_to='produkte/', blank=True, null=True)
    aktiv = models.BooleanField(default=True)
    lagerbestand = models.PositiveIntegerField(default=1)
    newsletter_gesendet = models.BooleanField(default=False)
    erstellt_am = models.DateTimeField(auto_now_add=True)
    aktualisiert_am = models.DateTimeField(auto_now=True)
    ersteller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='produkte')
    
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
        return (Decimal(self.impressionen) * Decimal('0.0025')) + (Decimal(self.klicks) * Decimal('0.095'))

    @property
    def verbleibendes_budget(self):
        from decimal import Decimal
        remaining = self.budget - self.ausgegeben
        return remaining if remaining > Decimal('0') else Decimal('0')

    @property
    def budget_prozent_genutzt(self):
        if not self.budget:
            return 100
        pct = int((self.ausgegeben / self.budget) * 100)
        return min(pct, 100)

    @property
    def ist_aktiv(self):
        from decimal import Decimal
        return bool(self.aktiv) and (self.budget - self.ausgegeben) > Decimal('0')


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
