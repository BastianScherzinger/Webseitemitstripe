from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Produkt


class CustomUserCreationForm(UserCreationForm):
    """Erweiterte Registrierungsform mit zusätzlichen Feldern"""
    
    # User-Felder
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-Mail-Adresse'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="Vorname",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vorname'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label="Nachname",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nachname'
        })
    )
    
    # Profile-Felder
    telefon = forms.CharField(
        max_length=20,
        required=False,
        label="Telefon",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Telefonnummer'
        })
    )
    adresse = forms.CharField(
        max_length=255,
        required=False,
        label="Straße & Hausnummer",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Musterstraße 123'
        })
    )
    postleitzahl = forms.CharField(
        max_length=10,
        required=False,
        label="Postleitzahl",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. 12345'
        })
    )
    stadt = forms.CharField(
        max_length=100,
        required=False,
        label="Stadt",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Berlin'
        })
    )
    land = forms.CharField(
        max_length=100,
        required=False,
        label="Land",
        initial="Deutschland",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'z.B. Deutschland'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Styling für Standard-Felder
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Benutzername'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Passwort'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Passwort wiederholen'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # UserProfile abrufen (vom Signal erstellt) oder erstellen
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.telefon = self.cleaned_data.get('telefon', '')
            profile.adresse = self.cleaned_data.get('adresse', '')
            profile.postleitzahl = self.cleaned_data.get('postleitzahl', '')
            profile.stadt = self.cleaned_data.get('stadt', '')
            profile.land = self.cleaned_data.get('land', 'Deutschland')
            profile.save()
        
        return user


class UserProfileForm(forms.ModelForm):
    """Form für die Bearbeitung des User Profiles"""
    
    # User-Felder
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label="Vorname",
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label="Nachname",
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ('telefon', 'adresse', 'postleitzahl', 'stadt', 'land', 'geburtsdatum')
        labels = {
            'telefon': 'Telefon',
            'adresse': 'Straße & Hausnummer',
            'postleitzahl': 'Postleitzahl',
            'stadt': 'Stadt',
            'land': 'Land',
            'geburtsdatum': 'Geburtsdatum',
        }
        widgets = {
            'telefon': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'postleitzahl': forms.TextInput(attrs={'class': 'form-control'}),
            'stadt': forms.TextInput(attrs={'class': 'form-control'}),
            'land': forms.TextInput(attrs={'class': 'form-control'}),
            'aktiv': forms.CheckboxInput(attrs={'class': 'w-6 h-6 rounded-lg bg-white/5 border-white/10 text-glow-orange focus:ring-glow-orange'}),
            'lagerbestand': forms.NumberInput(attrs={'class': 'form-input w-full p-4 rounded-xl', 'min': '0'}),
            'geburtsdatum': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # User-Felder speichern
        if profile.user:
            profile.user.first_name = self.cleaned_data['first_name']
            profile.user.last_name = self.cleaned_data['last_name']
            profile.user.email = self.cleaned_data['email']
            if commit:
                profile.user.save()
        
        if commit:
            profile.save()
        
        return profile


class ProduktForm(forms.ModelForm):
    """Form für das Hochladen und Bearbeiten von Produkten"""
    
    class Meta:
        model = Produkt
        fields = ('name', 'beschreibung', 'preis', 'lagerbestand', 'bild', 'aktiv')
        labels = {
            'name': 'Produktname',
            'beschreibung': 'Beschreibung',
            'preis': 'Preis (€)',
            'lagerbestand': 'Verfügbare Anzahl (Stock)',
            'bild': 'Produktbild',
            'aktiv': 'Aktiv (sichtbar im Shop)',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'z.B. Premium T-Shirt'
            }),
            'beschreibung': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Detaillierte Produktbeschreibung...',
                'rows': 5
            }),
            'preis': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '19.99',
                'step': '0.01',
                'min': '0'
            }),
            'lagerbestand': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '1',
                'min': '0'
            }),
            'bild': forms.FileInput(attrs={
                'class': 'form-input',
                'accept': 'image/*'
            }),
            'aktiv': forms.CheckboxInput(attrs={
                'class': 'w-6 h-6 rounded-lg bg-white/5 border-white/10 text-glow-orange focus:ring-glow-orange'
            }),
        }

    send_newsletter = forms.BooleanField(
        required=False,
        initial=True,
        label="Newsletter an alle Abonnenten verschicken?",
        widget=forms.CheckboxInput(attrs={
            'class': 'w-6 h-6 rounded-lg bg-white/5 border-white/10 text-glow-orange focus:ring-glow-orange'
        })
    )


class AdminUserEditForm(forms.ModelForm):
    """Spezielle Form für Admins, um User-Daten und Status zu bearbeiten"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    is_staff = forms.BooleanField(required=False, label="Mitarbeiter-Status (Produkte)", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_superuser = forms.BooleanField(required=False, label="Admin-Status (System)", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    # Profile-Felder
    telefon = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    adresse = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    postleitzahl = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    stadt = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    land = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email_verified = forms.BooleanField(required=False, label="Email verifiziert", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            profile, _ = UserProfile.objects.get_or_create(user=self.instance)
            self.fields['telefon'].initial = profile.telefon
            self.fields['adresse'].initial = profile.adresse
            self.fields['postleitzahl'].initial = profile.postleitzahl
            self.fields['stadt'].initial = profile.stadt
            self.fields['land'].initial = profile.land
            self.fields['email_verified'].initial = profile.email_verified

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.telefon = self.cleaned_data['telefon']
            profile.adresse = self.cleaned_data['adresse']
            profile.postleitzahl = self.cleaned_data['postleitzahl']
            profile.stadt = self.cleaned_data['stadt']
            profile.land = self.cleaned_data['land']
            profile.email_verified = self.cleaned_data['email_verified']
            profile.save()
        return user


class AdminUserCreationForm(CustomUserCreationForm):
    """Erweiterte Creation Form für Admins, um direkt Status zu setzen"""
    is_staff = forms.BooleanField(required=False, label="Mitarbeiter-Status (Produkte)", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    is_superuser = forms.BooleanField(required=False, label="Admin-Status (System)", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    email_verified = forms.BooleanField(required=False, initial=True, label="Email direkt verifizieren", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data['is_staff']
        user.is_superuser = self.cleaned_data['is_superuser']
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.email_verified = self.cleaned_data['email_verified']
            profile.save()
        return user
