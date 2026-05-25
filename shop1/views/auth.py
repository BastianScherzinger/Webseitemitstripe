"""Authentifizierung und Benutzerprofil: Login, Registrierung, Profil, E-Mail-Verifikation."""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from ..forms import CustomUserCreationForm, UserProfileForm
from ..models import UserProfile, Order
from ._helpers import _is_admin, _get_or_create_cart, _sync_session_to_db


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            _sync_session_to_db(request, user)
            try:
                if not user.profile.email_verified:
                    messages.info(
                        request,
                        f'Willkommen, {user.first_name or user.username}! '
                        f'Bitte bestätige noch deine E-Mail-Adresse.',
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
            try:
                messages.success(
                    request,
                    f'Account erfolgreich erstellt! '
                    f'Eine Bestätigungs-E-Mail wurde an {user.email} gesendet. '
                    f'Prüfe dein Postfach (auch Spam-Ordner).',
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
            from ..signals import send_verification_email
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
        if _is_admin(user):
            messages.error(request, '⛔ Der Shopbesitzer-Account kann nicht gelöscht werden.')
            return redirect('profil')
        user.delete()
        messages.success(request, 'Dein Account und alle dazugehörigen Daten wurden erfolgreich gelöscht.')
        return redirect('home')
    return redirect('profil')


@login_required(login_url='login')
def profil(request):
    """Profilseite mit Möglichkeit zum Bearbeiten."""
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

    status = "Normaler Nutzer"
    if user.is_superuser:
        status = "Superadministrator"
    elif user.is_staff:
        status = "Mitarbeiter"

    bestellungen_count = Order.objects.filter(user=user).count()
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
    """View zum Ändern des Passworts."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
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
