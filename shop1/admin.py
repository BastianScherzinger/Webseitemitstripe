from django.contrib import admin
from .models import UserProfile, Produkt, Cart, CartItem, Order, OrderItem

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'stadt', 'land', 'email_verified', 'erstellt_am')
    search_fields = ('user__username', 'stadt', 'adresse')
    list_filter = ('land', 'email_verified', 'erstellt_am')
    readonly_fields = ('erstellt_am', 'aktualisiert_am', 'verification_token')
    
    fieldsets = (
        ('Benutzer', {
            'fields': ('user',)
        }),
        ('Kontaktinformationen', {
            'fields': ('telefon', 'adresse', 'postleitzahl', 'stadt', 'land')
        }),
        ('Zusätzliche Informationen', {
            'fields': ('geburtsdatum', 'bio')
        }),
        ('E-Mail Verifikation', {
            'fields': ('email_verified', 'verification_token')
        }),
        ('Zeitstempel', {
            'fields': ('erstellt_am', 'aktualisiert_am'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Produkt)
class ProduktAdmin(admin.ModelAdmin):
    list_display = ('name', 'preis', 'aktiv', 'ersteller', 'erstellt_am')
    search_fields = ('name', 'beschreibung')
    list_filter = ('aktiv', 'erstellt_am')
    readonly_fields = ('erstellt_am', 'aktualisiert_am')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'anzahl_items', 'gesamt_preis', 'erstellt_am')
    search_fields = ('user__username',)
    readonly_fields = ('erstellt_am', 'aktualisiert_am')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('produkt_name', 'menge', 'produkt_preis', 'gesamt_preis', 'hinzugefuegt_am')
    search_fields = ('produkt_name', 'cart__user__username')
    list_filter = ('hinzugefuegt_am',)


# Order und OrderItem zusammen anzeigen (Inline)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('gesamt_preis',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'gesamt_betrag', 'erstellt_am')
    search_fields = ('user__username', 'email', 'paypal_order_id')
    list_filter = ('status', 'erstellt_am', 'land')
    readonly_fields = ('paypal_order_id', 'erstellt_am', 'aktualisiert_am')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Bestellung', {
            'fields': ('user', 'status', 'paypal_order_id')
        }),
        ('Lieferdaten', {
            'fields': ('vorname', 'nachname', 'email', 'adresse', 'postleitzahl', 'stadt', 'land', 'telefon')
        }),
        ('Zahlung', {
            'fields': ('gesamt_betrag',)
        }),
        ('Zeitstempel', {
            'fields': ('erstellt_am', 'aktualisiert_am'),
            'classes': ('collapse',)
        }),
    )
