from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from functools import wraps
import os
from .forms import CustomUserCreationForm, UserProfileForm, ProduktForm
from .models import UserProfile, Cart, CartItem, Produkt


# ═══ HILFSFUNKTIONEN ═══

def _setup_admin_user():
    """Synchronisiert den Admin-User aus der .env mit der Datenbank."""
    try:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@shop.de')
        admin_password = os.getenv('ADMIN_PASSWORD', 'AdminPassword123!')
        
        user = User.objects.filter(username=admin_username).first()
        if user:
            # Nur updaten, wenn sich etwas geändert hat, um Session-Invalidierung zu vermeiden
            changed = False
            if user.email != admin_email:
                user.email = admin_email
                changed = True
            
            if not user.check_password(admin_password):
                user.set_password(admin_password)
                changed = True
                
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                changed = True
                
            if changed:
                user.save()
        else:
            # Neuen Superuser anlegen
            user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            
        # E-Mail Verifikation für Admin automatisch setzen
        if hasattr(user, 'profile'):
            if not user.profile.email_verified:
                user.profile.email_verified = True
                user.profile.save()
    except Exception:
        pass

def _is_admin(user):
    """Prüft ob Benutzer der Admin/Shopbesitzer ist"""
    if not user.is_authenticated:
        return False
    admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
    return user.username == admin_username


def admin_required(view_func):
    """Decorator - nur Admin kann zugreifen"""
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not _is_admin(request.user):
            messages.error(request, 'Du hast keine Berechtigung für diese Seite.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapped


def _get_or_create_cart(user):
    """Holt oder erstellt den Warenkorb für einen User."""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def _sync_session_to_db(request, user):
    """Synct Session-Warenkorb in die Datenbank beim Login."""
    session_cart = request.session.get('warenkorb', {})
    if not session_cart:
        return
    
    cart = _get_or_create_cart(user)
    
    for key, item in session_cart.items():
        existing = cart.items.filter(produkt_name=item['name']).first()
        if existing:
            existing.menge += item.get('menge', 1)
            existing.save()
        else:
            CartItem.objects.create(
                cart=cart,
                produkt_name=item['name'],
                produkt_preis=item['preis'],
                produkt_bild=item.get('bild', ''),
                menge=item.get('menge', 1),
            )
    
    # Session-Warenkorb leeren nach Sync
    request.session['warenkorb'] = {}
    request.session.modified = True


# ═══ SEITEN ═══

def startseite(request):
    context = {
        'titel': 'Mein Shop',
        'anzahl': 42,
    }
    return render(request, 'shop1/index.html', context)


def kontakte(request, produkt_id):
    return HttpResponse(f"Kontakt für Produkt {produkt_id}")


from django.core.mail import send_mail

def kontakt(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        betreff = request.POST.get('betreff', '')
        nachricht = request.POST.get('nachricht', '')
        
        if name and email and betreff and nachricht:
            # Email zusammenbauen
            subject = f"Kontaktformular: {betreff}"
            message = f"Neue Nachricht von {name} ({email}):\n\n{nachricht}"
            from_email = settings.DEFAULT_FROM_EMAIL
            # E-Mail an dich (Shop-Betreiber) senden
            recipient_list = [settings.EMAIL_HOST_USER]  # Oder eine andere Ziel-Email eintragen
            
            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                messages.success(request, 'Deine Nachricht wurde erfolgreich gesendet! Wir melden uns in Kürze.')
            except Exception as e:
                import logging
                logging.error(f"Fehler beim Senden der Kontakt-Email: {str(e)}")
                messages.error(request, 'Entschuldigung, es gab ein Problem beim Senden deiner Nachricht. Bitte versuche es später noch einmal.')
        else:
            messages.error(request, 'Bitte fülle alle Felder aus.')
    
    return render(request, 'shop1/kontakt.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            # Session-Warenkorb in DB syncen
            _sync_session_to_db(request, user)
            
            # NUR EINE Nachricht anzeigen
            try:
                if not user.profile.email_verified:
                    messages.info(
                        request, 
                        f'Willkommen, {user.first_name or user.username}! '
                        f'Bitte bestätige noch deine E-Mail-Adresse.'
                    )
                else:
                    messages.success(request, f'Willkommen zurück, {user.first_name or user.username}!')
            except UserProfile.DoesNotExist:
                messages.success(request, f'Willkommen zurück, {user.first_name or user.username}!')
            
            return redirect('home')
        else:
            messages.error(request, 'Ungültige Anmeldedaten')
            return render(request, 'shop1/login.html', {'error': 'Ungültige Anmeldedaten'})
    return render(request, 'shop1/login.html')


@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return render(request, 'shop1/logout.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Verifikationslink für die Nachricht holen
            try:
                token = user.profile.verification_token
                verify_url = f"{settings.SITE_URL}/verify/{token}/"
                messages.success(
                    request,
                    f'Account erfolgreich erstellt! '
                    f'Eine Bestätigungs-E-Mail wurde an {user.email} gesendet. '
                    f'Prüfe dein Postfach (auch Spam-Ordner).'
                )
            except Exception:
                messages.success(request, 'Account erfolgreich erstellt! Bitte melden Sie sich an.')
            
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'shop1/register.html', {'form': form})


def ueber_uns(request):
    return render(request, 'shop1/ueber_uns.html')


def impressum(request):
    """Impressum Seite"""
    return render(request, 'shop1/legal/impressum.html')


def datenschutz(request):
    """Datenschutzerklärung Seite"""
    return render(request, 'shop1/legal/datenschutz.html')


def agb(request):
    """AGB Seite"""
    return render(request, 'shop1/legal/agb.html')


def produkte(request):
    """Zeigt alle aktiven Produkte aus der Datenbank"""
    produkte_liste = Produkt.objects.filter(aktiv=True)
    return render(request, 'shop1/produkte.html', {
        'produkte_liste': produkte_liste
    })


def produkt_detail(request, produkt_id):
    """Zeigt die Detailseite eines einzelnen Produkts."""
    produkt = get_object_or_404(Produkt, id=produkt_id, aktiv=True)
    return render(request, 'shop1/produkt_detail.html', {
        'produkt': produkt
    })


# ═══ WARENKORB ═══

@login_required(login_url='login')
def add_to_cart(request, produkt_id):
    """Fügt ein Produkt zum Warenkorb hinzu. Nur für eingeloggte User."""
    produkt = get_object_or_404(Produkt, id=produkt_id)
    
    # DB-Warenkorb
    cart = _get_or_create_cart(request.user)
    item, created = cart.items.get_or_create(
        produkt_name=produkt.name,
        defaults={
            'produkt_preis': produkt.preis,
            'produkt_bild': produkt.bild.url if produkt.bild else '',
            'menge': 1,
        }
    )
    if not created:
        item.menge += 1
        item.save()
    
    messages.success(request, f'"{produkt.name}" wurde zum Warenkorb hinzugefügt!')
    
    # Redirect handling
    next_url = request.GET.get('next', None)
    if next_url == 'warenkorb':
        return redirect('warenkorb')
    else:
        # Bleib auf der Produktseite wenn kein next-Parameter
        return redirect('produkt_detail', produkt_id=produkt.id)


@login_required(login_url='login')
def remove_from_cart(request, produkt_name):
    """Entfernt ein Produkt aus dem Warenkorb. Nur für eingeloggte User."""
    cart = _get_or_create_cart(request.user)
    cart.items.filter(produkt_name=produkt_name).delete()
    
    messages.success(request, f'"{produkt_name}" wurde aus dem Warenkorb entfernt.')
    return redirect('warenkorb')


@login_required(login_url='login')
def update_cart(request, produkt_name):
    """Aktualisiert die Menge eines Produkts im Warenkorb. Nur für eingeloggte User."""
    menge = int(request.POST.get('menge', 1))
    
    if menge < 1:
        return remove_from_cart(request, produkt_name)
    
    cart = _get_or_create_cart(request.user)
    item = cart.items.filter(produkt_name=produkt_name).first()
    if item:
        item.menge = menge
        item.save()
    
    return redirect('warenkorb')


@login_required(login_url='login')
def warenkorb(request):
    """Warenkorb-Seite – Nur für eingeloggte User."""
    warenkorb_items = []
    gesamt = 0
    
    cart = _get_or_create_cart(request.user)
    for item in cart.items.all():
        item_gesamt = float(item.produkt_preis) * item.menge
        warenkorb_items.append({
            'name': item.produkt_name,
            'preis': float(item.produkt_preis),
            'bild': item.produkt_bild,
            'menge': item.menge,
            'gesamt': item_gesamt,
        })
        gesamt += item_gesamt
    
    return render(request, 'shop1/warenkorb.html', {
        'warenkorb_items': warenkorb_items,
        'gesamt': gesamt,
    })


# ═══ PROFIL ═══

@login_required(login_url='login')
def profil(request):
    """Profilseite mit Möglichkeit zum Bearbeiten"""
    user = request.user
    
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil erfolgreich aktualisiert!')
            return redirect('profil')
    else:
        form = UserProfileForm(instance=profile)
    
    # Status bestimmen
    status = "Normaler Nutzer"
    if user.is_staff:
        status = "Administrator (Statistiken & System)"
    elif user.is_superuser:
        status = "Mitarbeiter (Produktverwaltung)"
        
    profil_data = {
        'username': user.username,
        'email': user.email,
        'vorname': user.first_name or 'Nicht angegeben',
        'nachname': user.last_name or 'Nicht angegeben',
        'telefon': profile.telefon or 'Nicht angegeben',
        'adresse': profile.adresse or 'Nicht angegeben',
        'postleitzahl': profile.postleitzahl or 'Nicht angegeben',
        'stadt': profile.stadt or 'Nicht angegeben',
        'land': profile.land or 'Deutschland',
        'geburtsdatum': profile.geburtsdatum or 'Nicht angegeben',
        'bestellungen': 3,  # Platzhalter
        'ist_admin': user.is_staff,
        'ist_superuser': user.is_superuser,
        'status': status,
        'email_verified': profile.email_verified,
    }
    
    return render(request, 'shop1/profil.html', {
        'profil': profil_data,
        'form': form,
        'user': user,
    })


@login_required(login_url='login')
def change_password(request):
    """View zum Ändern des Passworts"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Session-Hash updaten, damit der User nicht ausgeloggt wird
            update_session_auth_hash(request, user)
            messages.success(request, '✅ Dein Passwort wurde erfolgreich geändert!')
            return redirect('profil')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'shop1/change_password.html', {'form': form})


# ═══ EMAIL-VERIFIKATION ═══

def verify_email(request, token):
    """Verifiziert die E-Mail-Adresse eines Users anhand des Tokens."""
    print(f">>> VERIFY VIEW AUFGERUFEN MIT TOKEN: {token}")
    try:
        profile = UserProfile.objects.get(verification_token=token)
        if profile.email_verified:
            messages.info(request, 'Deine E-Mail-Adresse wurde bereits bestätigt.')
        else:
            profile.email_verified = True
            profile.save(update_fields=['email_verified'])
            messages.success(request, '✅ Deine E-Mail-Adresse wurde erfolgreich bestätigt! Du kannst dich jetzt einloggen.')
        return redirect('login')
    except (UserProfile.DoesNotExist, ValueError, ValidationError):
        messages.error(request, '❌ Ungültiger oder abgelaufener Bestätigungslink.')
        return redirect('home')


@login_required(login_url='login')
def resend_verification(request):
    """Sendet die Verifikations-Email erneut."""
    try:
        profile = request.user.profile
        if profile.email_verified:
            messages.info(request, 'Deine E-Mail-Adresse ist bereits bestätigt.')
        else:
            profile.regenerate_token()
            from .signals import send_verification_email
            send_verification_email(request.user, profile)
            messages.success(request, '📧 Neue Bestätigungs-E-Mail wurde gesendet!')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profil nicht gefunden.')
    
    return redirect('profil')


@login_required(login_url='login')
def delete_account(request):
    """Löscht das gesamte Benutzerkonto und alle dazugehörigen Daten."""
    if request.method == 'POST':
        user = request.user
        # Durch CASCADE-Deletion werden auch UserProfile, Cart und CartItems gelöscht
        user.delete()
        messages.success(request, 'Dein Account und alle dazugehörigen Daten wurden erfolgreich gelöscht. Schade, dass du gehst!')
        return redirect('home')
    
    # Falls versehentlich über GET aufgerufen, zurück zum Profil
    return redirect('profil')