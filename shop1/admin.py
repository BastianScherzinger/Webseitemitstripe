from django.contrib import admin
from .models import UserProfile

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
