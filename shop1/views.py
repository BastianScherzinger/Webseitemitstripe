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
from .models import UserProfile, Cart, CartItem, Produkt, Order, OrderItem

import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


# ═══ HILFSFUNKTIONEN ═══

def _setup_admin_user():
    """Synchronisiert den Admin-User aus der .env mit der Datenbank."""
    try:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@shop.de')
        admin_password = os.getenv('ADMIN_PASSWORD')

        if not admin_password:
            return  # Kein Passwort gesetzt → nichts tun (sichererer Fallback)

        user = User.objects.filter(username=admin_username).first()
        if user:
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
    return user.username == admin_username or user.is_superuser


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
    # Fetch some active products for the animated gallery
    produkte_galerie = Produkt.objects.filter(aktiv=True)[:8]
    context = {
        'titel': 'Luviq-Shop',
        'anzahl': 42,
        'produkte_galerie': produkte_galerie,
    }
    return render(request, 'shop1/index.html', context)


def kontakte(request, produkt_id):
    return redirect('kontakt')


from .utils import send_brevo_email

def kontakt(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        betreff = request.POST.get('betreff', '')
        nachricht = request.POST.get('nachricht', '')
        
        if name and email and betreff and nachricht:
            # Newlines aus Subject-Feldern entfernen (Email-Header-Injection)
            safe_betreff = betreff.replace('\r', '').replace('\n', ' ')
            safe_name = name.replace('\r', '').replace('\n', ' ')
            safe_email = email.replace('\r', '').replace('\n', ' ')
            subject = f"Kontaktformular: {safe_betreff}"
            message = f"Neue Nachricht von {safe_name} ({safe_email}):\n\n{nachricht}"
            from_email = settings.DEFAULT_FROM_EMAIL
            # E-Mail an dich (Shop-Betreiber) senden
            # Wir nutzen ADMIN_EMAIL aus der .env, sonst DEFAULT_FROM_EMAIL
            recipient = os.getenv('ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
            
            try:
                send_brevo_email(subject, message, recipient, recipient_name="Shop Admin", text_content=message)
                messages.success(request, 'Deine Nachricht wurde erfolgreich gesendet! Wir melden uns in Kürze.')
            except Exception:
                messages.error(request, 'Entschuldigung, es gab ein Problem beim Senden deiner Nachricht.')
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
    
    # Stock Check
    if produkt.lagerbestand < 1:
        messages.error(request, f'Entschuldigung, "{produkt.name}" ist leider ausverkauft.')
        return redirect('home')

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
        if item.menge < produkt.lagerbestand:
            item.menge += 1
            item.save()
            messages.success(request, f'"{produkt.name}" wurde zum Warenkorb hinzugefügt!')
        else:
            messages.warning(request, f'Du hast bereits alle verfügbaren Einheiten ({produkt.lagerbestand}) im Warenkorb.')
    else:
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
    try:
        menge = int(request.POST.get('menge', 1))
    except (ValueError, TypeError):
        menge = 1
    
    if menge < 1:
        return remove_from_cart(request, produkt_name)
    
    cart = _get_or_create_cart(request.user)
    item = cart.items.filter(produkt_name=produkt_name).first()
    if item:
        # Stock Check für Update
        db_produkt = Produkt.objects.filter(name=produkt_name).first()
        if db_produkt and menge > db_produkt.lagerbestand:
            menge = db_produkt.lagerbestand
            messages.warning(request, f'Nur {menge} Einheiten verfügbar. Menge wurde angepasst.')
        
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
        
    # Echte Bestellungszahl berechnen
    bestellungen_count = Order.objects.filter(user=user).count()
    
    # Bestellungen für Anzeige holen
    bestellungen = Order.objects.filter(user=user).prefetch_related('items').order_by('-erstellt_am')
    
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
        'bestellungen': bestellungen_count,
        'ist_admin': user.is_staff,
        'ist_superuser': user.is_superuser,
        'status': status,
        'email_verified': profile.email_verified,
        'is_main_admin': _is_admin(user),
    }
    
    return render(request, 'shop1/profil.html', {
        'profil': profil_data,
        'form': form,
        'user': user,
        'bestellungen': bestellungen,
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
        
        # SCHUTZ: Shopbesitzer/Admin darf nicht gelöscht werden
        if _is_admin(user):
            messages.error(request, '⛔ Der Shopbesitzer-Account kann nicht gelöscht werden. Kontaktiere den System-Administrator für manuelle Änderungen.')
            return redirect('profil')
            
        # Durch CASCADE-Deletion werden auch UserProfile, Cart und CartItems gelöscht
        user.delete()
        messages.success(request, 'Dein Account und alle dazugehörigen Daten wurden erfolgreich gelöscht. Schade, dass du gehst!')
        return redirect('home')
    
    # Falls versehentlich über GET aufgerufen, zurück zum Profil
    return redirect('profil')


# ═══ CHECKOUT & ZAHLUNG (PAYPAL) ═══

@login_required(login_url='login')
def checkout(request):
    """Checkout-Seite mit Adressdaten"""
    cart = _get_or_create_cart(request.user)
    
    # Warenkorb ist leer
    if not cart.items.exists():
        messages.warning(request, 'Dein Warenkorb ist leer.')
        return redirect('warenkorb')
    
    # Gesamtbetrag berechnen
    gesamt_betrag_original = sum(float(item.produkt_preis * item.menge) for item in cart.items.all())
    
    # Rabatt Check (Erste Bestellung)
    hat_rabatt = False
    rabatt_wert = 0
    if hasattr(request.user, 'profile') and request.user.profile.has_welcome_discount:
        hat_rabatt = True
        rabatt_wert = gesamt_betrag_original * 0.10
        
    gesamt_betrag = gesamt_betrag_original - rabatt_wert

    if request.method == 'POST':
        # ... (Formular Daten sammeln)
        vorname = request.POST.get('vorname', '').strip()
        nachname = request.POST.get('nachname', '').strip()
        email = request.POST.get('email', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        stadt = request.POST.get('stadt', '').strip()
        postleitzahl = request.POST.get('postleitzahl', '').strip()
        land = request.POST.get('land', 'Deutschland').strip()
        telefon = request.POST.get('telefon', '').strip()
        
        # Validierung
        if not all([vorname, nachname, email, adresse, stadt, postleitzahl, land]):
            messages.error(request, 'Bitte fülle alle erforderlichen Felder aus.')
            return redirect('checkout')
        
        # Bestellung erstellen
        try:
            payment_method = request.POST.get('payment_method', 'paypal')
            
            order = Order.objects.create(
                user=request.user,
                status='pending',
                payment_method=payment_method,
                vorname=vorname,
                nachname=nachname,
                email=email,
                adresse=adresse,
                stadt=stadt,
                postleitzahl=postleitzahl,
                land=land,
                telefon=telefon,
                gesamt_betrag=gesamt_betrag,
            )
            
            # Merke ob Rabatt genutzt wurde
            request.session['order_rabatt'] = float(rabatt_wert) if hat_rabatt else 0
            
            # Order Items erstellen
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    produkt_name=item.produkt_name,
                    produkt_preis=item.produkt_preis,
                    menge=item.menge,
                )
            
            # Spezielle Logik für Überweisung
            if payment_method == 'bank_transfer':
                # Email mit Bankverbindung senden
                try:
                    send_bank_details_email(order)
                except Exception as e:
                    print(f"Email error: {e}")
                
                messages.info(request, '🏛️ Mission gestartet! Bitte schließe die Überweisung ab.')
                return redirect('payment_success', order_id=order.id)

            # Standard: PayPal
            return redirect('payment', order_id=order.id)
            
        except Exception:
            messages.error(request, 'Ein Fehler ist aufgetreten. Bitte versuche es erneut.')
            return redirect('checkout')
    
    # GET Request - Checkout-Formular anzeigen
    profile_data = {}
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        profile_data = {
            'vorname': request.user.first_name or '',
            'nachname': request.user.last_name or '',
            'email': request.user.email,
            'adresse': profile.adresse or '',
            'stadt': profile.stadt or '',
            'postleitzahl': profile.postleitzahl or '',
            'land': profile.land or 'Deutschland',
            'telefon': profile.telefon or '',
        }
    
    context = {
        'gesamt_betrag': gesamt_betrag,
        'gesamt_betrag_original': gesamt_betrag_original,
        'hat_rabatt': hat_rabatt,
        'rabatt_wert': rabatt_wert,
        'profile_data': profile_data,
    }
    return render(request, 'shop1/checkout.html', context)


@login_required(login_url='login')
def payment(request, order_id):
    """Payment-Seite mit PayPal Smart Buttons"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Bestellung nicht gefunden.')
        return redirect('warenkorb')
    
    # Nur unbezahlte Bestellungen können bezahlt werden
    if order.status == 'paid':
        messages.info(request, 'Diese Bestellung wurde bereits bezahlt.')
        return redirect('payment_success', order_id=order.id)
    
    paypal_client_id = settings.PAYPAL_CLIENT_ID
    
    context = {
        'order': order,
        'paypal_client_id': paypal_client_id,
    }
    return render(request, 'shop1/payment.html', context)


@require_http_methods(["POST"])
@login_required(login_url='login')
def paypal_capture(request, order_id):
    """Wird nach erfolgreicher PayPal-Zahlung aufgerufen (AJAX).
    CSRF wird über X-CSRFToken Header geprüft (payment.html Zeile 145)."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Bestellung nicht gefunden'}, status=404)

    if order.status == 'paid':
        return JsonResponse({'status': 'success', 'redirect': f'/payment/success/{order.id}/'})

    try:
        data = json.loads(request.body)
        paypal_order_id = data.get('paypal_order_id', '')

        if not paypal_order_id:
            return JsonResponse({'error': 'Keine PayPal Order ID'}, status=400)

        # Replay-Schutz: paypal_order_id darf nicht bereits einer anderen Bestellung gehören
        if Order.objects.filter(paypal_order_id=paypal_order_id).exclude(id=order.id).exists():
            return JsonResponse({'error': 'Diese PayPal-Transaktion wurde bereits verwendet.'}, status=400)

        # Bestellung als bezahlt markieren
        order.paypal_order_id = paypal_order_id
        order.status = 'paid'
        order.save()
        
        # Rabatt verbrauchen
        if hasattr(request.user, 'profile'):
            request.user.profile.has_welcome_discount = False
            request.user.profile.save()

        # Lagerbestand reduzieren
        for item in order.items.all():
            db_produkt = Produkt.objects.filter(name=item.produkt_name).first()
            if db_produkt:
                db_produkt.lagerbestand = max(0, db_produkt.lagerbestand - item.menge)
                db_produkt.aktiv = False # Artikel nach Verkauf deaktivieren (1-of-1)
                db_produkt.save()
        
        # Bestätigungs-Email senden
        try:
            send_order_confirmation_email(order)
        except Exception:
            pass  # Email-Fehler sollten den Zahlungsprozess nicht blockieren
        
        return JsonResponse({'status': 'success', 'redirect': f'/payment/success/{order.id}/'})
        
    except Exception:
        return JsonResponse({'error': 'Zahlung konnte nicht verarbeitet werden.'}, status=500)


@login_required(login_url='login')
def payment_success(request, order_id):
    """Erfolgreiche Zahlung"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Bestellung nicht gefunden.')
        return redirect('warenkorb')
    
    # Warenkorb leeren nach erfolgreicher Zahlung
    cart = _get_or_create_cart(request.user)
    cart.items.all().delete()
    
    context = {
        'order': order,
    }
    return render(request, 'shop1/payment_success.html', context)


@login_required(login_url='login')
def payment_cancel(request):
    """Zahlung abgebrochen"""
    messages.warning(request, 'Die Zahlung wurde abgebrochen. Dein Warenkorb ist noch vorhanden.')
    return redirect('warenkorb')


def send_order_confirmation_email(order):
    """Sendet eine Bestellbestätigung per E-Mail via Brevo API"""
    items_text = '\n'.join([
        f"- {item.menge}x {item.produkt_name}: {float(item.produkt_preis) * item.menge:.2f} €"
        for item in order.items.all()
    ])
    
    subject = f'Bestellbestätigung #{order.id}'
    html_content = f"""
    <html>
        <body>
            <h2>Hallo {order.vorname} {order.nachname},</h2>
            <p>vielen Dank für deine Bestellung! Deine Zahlung wurde erfolgreich verarbeitet.</p>
            <h3>Bestellnummer: #{order.id}</h3>
            <p><strong>Bestellte Artikel:</strong></p>
            <pre>{items_text}</pre>
            <p><strong>Gesamtbetrag: {float(order.gesamt_betrag):.2f} €</strong></p>
            <h4>Lieferadresse:</h4>
            <p>{order.adresse}<br>{order.postleitzahl} {order.stadt}<br>{order.land}</p>
            <p>Vielen Dank für deinen Einkauf!</p>
            <p>Mit freundlichen Grüßen,<br>Dein Shop-Team</p>
        </body>
    </html>
    """
    text_content = f"Bestellbestätigung #{order.id}\n\n{items_text}\n\nGesamt: {float(order.gesamt_betrag):.2f} €"
    

    send_brevo_email(subject, html_content, order.email, recipient_name=f"{order.vorname} {order.nachname}", text_content=text_content)


def send_bank_details_email(order):
    """Sendet wunderschöne Bankverbindung & PayPal Option bei Wahl von Überweisung"""
    subject = f'Zahlungsinformationen für deine Mission #{order.id}'
    
    # Items Liste generieren
    items_html = ""
    for item in order.items.all():
        db_produkt = Produkt.objects.filter(name=item.produkt_name).first()
        bild_html = ""
        if db_produkt and db_produkt.bild:
            bild_html = f'<img src="{db_produkt.bild.url}" width="80" style="border-radius: 10px; margin-right: 15px;">'
        
        items_html += f"""
        <div style="display: flex; align-items: center; padding: 15px 0; border-bottom: 1px solid #eeeeee;">
            {bild_html}
            <div>
                <p style="margin: 0; font-weight: bold; color: #050816;">{item.produkt_name}</p>
                <p style="margin: 5px 0 0 0; color: #888888; font-size: 12px;">{item.menge}x {item.produkt_preis:.2f} €</p>
            </div>
        </div>
        """

    html_content = f"""
    <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background-color: #f9fafb; color: #111827; margin: 0; padding: 40px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 30px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.05); border: 1px solid #eeeeee;">
                
                <!-- Header -->
                <div style="background: #050816; padding: 40px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 5px;">Luviq</h1>
                    <p style="color: #ff6a00; margin-top: 10px; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;">Mission: Payment Pending</p>
                </div>

                <div style="padding: 40px;">
                    <h2 style="font-size: 20px; font-weight: 900; margin-bottom: 20px;">Hallo {order.vorname},</h2>
                    <p style="line-height: 1.6; color: #4b5563;">vielen Dank für deine Bestellung! Du hast dich für eine manuelle Zahlung entschieden. Bitte begleiche den Betrag zeitnah, damit wir dein Unikat versenden können.</p>

                    <div style="margin: 30px 0; padding: 30px; background: #fdf2f2; border-radius: 20px; border-left: 5px solid #ff6a00;">
                        <h3 style="margin-top: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #ff6a00;">Zahlungsoption A: Überweisung</h3>
                        <p style="margin: 15px 0 5px 0; font-size: 13px;"><strong>Inhaber:</strong> Luisa Brehler</p>
                        <p style="margin: 5px 0; font-size: 13px;"><strong>IBAN:</strong> DE05 51 85 0079 1028 1367 37</p>
                        <p style="margin: 5px 0; font-size: 13px;"><strong>Verwendungszweck:</strong> Mission #{order.id}</p>
                        <p style="margin: 5px 0; font-size: 13px;"><strong>Betrag:</strong> <span style="font-size: 18px; font-weight: 900;">{float(order.gesamt_betrag):.2f} €</span></p>
                    </div>

                    <div style="margin: 30px 0; padding: 30px; background: #eff6ff; border-radius: 20px; border-left: 5px solid #2563eb;">
                        <h3 style="margin-top: 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #2563eb;">Zahlungsoption B: PayPal</h3>
                        <p style="margin: 15px 0; font-size: 13px;">Sende das Geld einfach per PayPal an:</p>
                        <p style="margin: 5px 0; font-size: 16px; font-weight: bold; color: #2563eb;">brehlerluisa@gmail.com</p>
                        <p style="margin: 10px 0 0 0; font-size: 11px; color: #6b7280;">(Bitte bestelle als "Freunde & Familie" oder übernehme die Gebühren, damit der volle Betrag ankommt.)</p>
                    </div>

                    <h3 style="font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px; border-top: 1px solid #eeeeee; pt: 20px;">Deine Auswahl:</h3>
                    {items_html}

                    <div style="margin-top: 40px; text-align: center; color: #9ca3af; font-size: 12px;">
                        <p>Sobald die Zahlung eingegangen ist, erhältst du eine Bestätigung.</p>
                        <p style="margin-top: 20px;">Herzliche Grüße,<br><strong style="color: #050816;">Luisa Brehler</strong></p>
                    </div>
                </div>

                <!-- Footer -->
                <div style="background: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #eeeeee;">
                    <p style="font-size: 10px; color: #9ca3af; text-transform: uppercase; letter-spacing: 2px;">Luviq Universe &copy; 2026</p>
                </div>
            </div>
        </body>
    </html>
    """
    send_brevo_email(subject, html_content, order.email, recipient_name=f"{order.vorname} {order.nachname}")


@csrf_exempt
def newsletter_subscribe(request):
    """Abonniert den Newsletter."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
        except:
            email = request.POST.get('email', '').strip()
            
        if not email:
            return JsonResponse({'error': 'Bitte gib eine gültige Email an.'}, status=400)
            
        from .models import Subscriber
        if Subscriber.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Du bist bereits im Orbit angemeldet!'}, status=200)
            
        Subscriber.objects.create(email=email)
        return JsonResponse({'message': 'Erfolgreich zum Newsletter angemeldet!'}, status=200)
        
    return JsonResponse({'error': 'Invalid request'}, status=405)


# ═══ SEO & TECHNISCHES SEO ═══

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

def robots_txt(request):
    """Erzeugt die robots.txt Datei für Suchmaschinen."""
    lines = [
        "User-agent: *",
        "Disallow: /shop-admin/",
        "Disallow: /profil/",
        "Disallow: /warenkorb/",
        "Disallow: /checkout/",
        "Disallow: /verify/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    """Erzeugt eine dynamische sitemap.xml."""
    base_url = request.build_absolute_uri('/')[:-1]
    
    # Statische Seiten
    pages = [
        {'loc': '', 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': reverse('produkte'), 'priority': '0.9', 'changefreq': 'daily'},
        {'loc': reverse('gaestebuch'), 'priority': '0.8', 'changefreq': 'daily'},
        {'loc': reverse('kontakt'), 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': reverse('ueber_uns'), 'priority': '0.7', 'changefreq': 'monthly'},
        {'loc': reverse('impressum'), 'priority': '0.3', 'changefreq': 'yearly'},
        {'loc': reverse('datenschutz'), 'priority': '0.3', 'changefreq': 'yearly'},
        {'loc': reverse('agb'), 'priority': '0.3', 'changefreq': 'yearly'},
    ]
    
    # Dynamische Produkte
    for produkt in Produkt.objects.filter(aktiv=True):
        pages.append({
            'loc': reverse('produkt_detail', args=[produkt.id]),
            'priority': '0.8',
            'changefreq': 'weekly'
        })

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for page in pages:
        xml_content += '  <url>\n'
        xml_content += f'    <loc>{base_url}{page["loc"]}</loc>\n'
        xml_content += f'    <priority>{page["priority"]}</priority>\n'
        xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml_content += '  </url>\n'
        
    xml_content += '</urlset>'
    
    return HttpResponse(xml_content, content_type="application/xml")


# ═══ GÄSTEBUCH & KOMMENTARE ═══

from .models import Comment

def gaestebuch(request):
    """Zeigt alle Haupt-Kommentare und deren Antworten an."""
    # Nur Haupt-Kommentare (parent=None) laden
    comments = Comment.objects.filter(parent=None).select_related('user').prefetch_related('replies', 'likes').order_by('-erstellt_am')
    
    return render(request, 'shop1/gaestebuch.html', {
        'comments': comments,
    })


@login_required(login_url='login')
def comment_add(request):
    """Fügt einen neuen Kommentar oder eine Antwort hinzu."""
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if not text:
            messages.error(request, 'Bitte gib eine Nachricht ein.')
            return redirect(request.META.get('HTTP_REFERER', 'gaestebuch'))
            
        parent = None
        is_admin_reply = False
        
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
            # Prüfen ob der antwortende User ein Admin ist
            if _is_admin(request.user):
                is_admin_reply = True
        
        Comment.objects.create(
            user=request.user,
            text=text,
            parent=parent,
            is_admin_reply=is_admin_reply
        )
        
        messages.success(request, 'Dein Beitrag wurde im Orbit veröffentlicht!')
    return redirect(request.META.get('HTTP_REFERER', 'gaestebuch'))


@login_required(login_url='login')
def comment_like(request, comment_id):
    """Liked oder ent-liked einen Kommentar."""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    
    return redirect(request.META.get('HTTP_REFERER', 'gaestebuch'))


@login_required(login_url='login')
def comment_delete(request, comment_id):
    """Löscht einen Kommentar (nur Admin oder Ersteller)."""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Nur Admin oder der Verfasser dürfen löschen
    if _is_admin(request.user) or comment.user == request.user:
        comment.delete()
        messages.success(request, 'Beitrag wurde gelöscht.')
    else:
        messages.error(request, 'Keine Berechtigung zum Löschen.')
        
    return redirect(request.META.get('HTTP_REFERER', 'gaestebuch'))
