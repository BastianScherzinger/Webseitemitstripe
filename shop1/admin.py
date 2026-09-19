"""Anmeldung der Shop-Modelle im regulären Django-Admin (``ADMIN_URL``).

Das eigene Verwaltungspanel unter ``/shop-admin/`` steht in
``admin_views.py``; hier geht es nur um die Standardoberfläche von Django.
"""
from django.contrib import admin
from .models import UserProfile, Produkt, Cart, CartItem, Order, OrderItem, Subscriber, KontaktAnfrage, Motivanfrage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Kundenprofile mit Anschrift und Stand der E-Mail-Bestätigung."""
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


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    """Newsletter-Abonnentinnen: E-Mail-Adressen sind personenbezogene Daten.

    Das Panel unter ``/shop-admin/`` zeigt sie und verschickt an sie; löschen,
    suchen und einzeln nachsehen liess sich bis hierher nur über die
    Datenbank. Eine Auskunft oder Löschung nach Art. 15/17 DSGVO braucht aber
    einen Weg, der ohne Datenbankzugriff auskommt.
    """
    list_display = ('email', 'erstellt_am')
    search_fields = ('email',)
    list_filter = ('erstellt_am',)
    readonly_fields = ('erstellt_am',)
    ordering = ('-erstellt_am',)


@admin.register(KontaktAnfrage)
class KontaktAnfrageAdmin(admin.ModelAdmin):
    """Anfragen aus dem Kontaktformular (MW18): hier steht jede angenommene
    Nachricht, auch wenn ihre Mail nie angekommen ist. Personenbezogene
    Daten – löschen lässt sich jede Anfrage einzeln."""
    list_display = ('erstellt_am', 'name', 'email', 'betreff', 'mail_gestartet')
    search_fields = ('name', 'email', 'betreff', 'nachricht')
    list_filter = ('mail_gestartet', 'erstellt_am')
    readonly_fields = ('name', 'email', 'betreff', 'nachricht', 'mail_gestartet', 'erstellt_am')
    ordering = ('-erstellt_am',)

    def has_add_permission(self, request):
        return False


@admin.register(Produkt)
class ProduktAdmin(admin.ModelAdmin):
    """Stücke. ``nummer`` (Nº 001 …) ist direkt in der Liste änderbar – so
    legt Luisa die Reihenfolge des Archivs fest. Material, Technik und Maße
    erscheinen als Datenliste auf der Stückseite, leer entfällt die Zeile."""
    list_display = ('nummer', 'name', 'preis', 'aktiv', 'ersteller', 'erstellt_am')
    list_display_links = ('name',)
    list_editable = ('nummer',)
    search_fields = ('name', 'beschreibung')
    list_filter = ('aktiv', 'erstellt_am')
    ordering = ('nummer',)
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
    """Bestellungen mit Lieferdaten und ihren Posten als Inline."""
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


@admin.register(Motivanfrage)
class MotivanfrageAdmin(admin.ModelAdmin):
    """Anfragen über „Motiv anfragen" (Stufe 1). Personenbezogene Daten –
    jede Anfrage lässt sich einzeln löschen; änderbar ist nur der Status."""
    list_display = ('erstellt_am', 'richtung', 'teil', 'platzierung', 'instagram', 'email', 'status', 'mail_gestartet')
    list_filter = ('status', 'richtung', 'teil', 'erstellt_am')
    list_editable = ('status',)
    search_fields = ('instagram', 'email', 'bedeutung')
    readonly_fields = ('richtung', 'teil', 'platzierung', 'bedeutung', 'instagram', 'email', 'mail_gestartet', 'erstellt_am')
    ordering = ('-erstellt_am',)

    def has_add_permission(self, request):
        return False
