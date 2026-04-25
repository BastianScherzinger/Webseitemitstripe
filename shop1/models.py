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
    
    def __str__(self):
        return f"Profile von {self.user.username}"
    
    def regenerate_token(self):
        """Generiert einen neuen Verifikations-Token"""
        self.verification_token = uuid.uuid4()
        self.save(update_fields=['verification_token'])
        return self.verification_token
    
    class Meta:
        verbose_name_plural = "User Profiles"


class Produkt(models.Model):
    """Produkt-Modell für den Shop"""
    name = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True)
    preis = models.DecimalField(max_digits=10, decimal_places=2)
    bild = models.ImageField(upload_to='produkte/', blank=True, null=True)
    aktiv = models.BooleanField(default=True)
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
        ('pending', 'Ausstehend'),
        ('paid', 'Bezahlt'),
        ('failed', 'Fehlgeschlagen'),
        ('cancelled', 'Abgebrochen'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
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
