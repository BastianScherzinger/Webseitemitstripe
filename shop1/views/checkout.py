"""Checkout und Zahlungsabwicklung (PayPal + Überweisung)."""

import os
import json
import logging

import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..models import Produkt, Order, OrderItem
from ..utils import send_brevo_email
from ._helpers import _get_or_create_cart

_log = logging.getLogger('shop1')


def _paypal_api_base():
    return 'https://api-m.paypal.com' if os.getenv('PAYPAL_MODE', 'sandbox') == 'live' else 'https://api-m.sandbox.paypal.com'


def _verify_paypal_order(paypal_order_id, expected_amount):
    """Verifiziert eine PayPal-Zahlung serverseitig ueber die PayPal Orders API.

    Ohne diese Pruefung wuerde der vom Client per AJAX gesendete
    paypal_order_id-String ungeprueft uebernommen: jeder eingeloggte Nutzer
    haette so jede eigene Bestellung ohne echte Zahlung als bezahlt markieren
    koennen (siehe frueherer Code: nur Replay-Check, keine Verifikation).
    """
    client_id = settings.PAYPAL_CLIENT_ID
    secret = os.getenv('PAYPAL_SECRET', '')
    if not secret or client_id == 'sb':
        _log.error('PayPal Verifikation nicht moeglich: PAYPAL_SECRET/PAYPAL_CLIENT_ID fehlt.')
        return False
    try:
        token_resp = requests.post(
            f'{_paypal_api_base()}/v1/oauth2/token',
            auth=(client_id, secret),
            data={'grant_type': 'client_credentials'},
            timeout=10,
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()['access_token']

        order_resp = requests.get(
            f'{_paypal_api_base()}/v2/checkout/orders/{paypal_order_id}',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        if order_resp.status_code != 200:
            return False
        data = order_resp.json()
        if data.get('status') != 'COMPLETED':
            return False

        paid_total = sum(
            float(capture['amount']['value'])
            for unit in data.get('purchase_units', [])
            for capture in unit.get('payments', {}).get('captures', [])
            if capture.get('amount', {}).get('currency_code') == 'EUR'
        )
        return abs(paid_total - float(expected_amount)) < 0.01
    except Exception as e:
        _log.error('PayPal Verifikation fehlgeschlagen: %s', e)
        return False


@login_required(login_url='login')
def checkout(request):
    """Checkout-Seite mit Adressdaten."""
    cart = _get_or_create_cart(request.user)

    if not cart.items.exists():
        messages.warning(request, 'Dein Warenkorb ist leer.')
        return redirect('warenkorb')

    gesamt_betrag_original = sum(float(item.produkt_preis * item.menge) for item in cart.items.all())

    hat_rabatt = False
    rabatt_wert = 0
    if hasattr(request.user, 'profile') and request.user.profile.has_welcome_discount:
        hat_rabatt = True
        rabatt_wert = gesamt_betrag_original * 0.10

    gesamt_betrag = gesamt_betrag_original - rabatt_wert

    if request.method == 'POST':
        vorname = request.POST.get('vorname', '').strip()
        nachname = request.POST.get('nachname', '').strip()
        email = request.POST.get('email', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        stadt = request.POST.get('stadt', '').strip()
        postleitzahl = request.POST.get('postleitzahl', '').strip()
        land = request.POST.get('land', 'Deutschland').strip()
        telefon = request.POST.get('telefon', '').strip()

        if not all([vorname, nachname, email, adresse, stadt, postleitzahl, land]):
            messages.error(request, 'Bitte fülle alle erforderlichen Felder aus.')
            return redirect('checkout')

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

            request.session['order_rabatt'] = float(rabatt_wert) if hat_rabatt else 0

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    produkt_name=item.produkt_name,
                    produkt_preis=item.produkt_preis,
                    menge=item.menge,
                )

            if payment_method == 'bank_transfer':
                try:
                    send_bank_details_email(order)
                except Exception as e:
                    _log.error("Bank-details email error: %s", e)
                messages.info(request, '🏛️ Mission gestartet! Bitte schließe die Überweisung ab.')
                return redirect('payment_success', order_id=order.id)

            return redirect('payment', order_id=order.id)

        except Exception:
            messages.error(request, 'Ein Fehler ist aufgetreten. Bitte versuche es erneut.')
            return redirect('checkout')

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

    return render(request, 'shop1/checkout.html', {
        'gesamt_betrag': gesamt_betrag,
        'gesamt_betrag_original': gesamt_betrag_original,
        'hat_rabatt': hat_rabatt,
        'rabatt_wert': rabatt_wert,
        'profile_data': profile_data,
    })


@login_required(login_url='login')
def payment(request, order_id):
    """Payment-Seite mit PayPal Smart Buttons."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Bestellung nicht gefunden.')
        return redirect('warenkorb')

    if order.status == 'paid':
        messages.info(request, 'Diese Bestellung wurde bereits bezahlt.')
        return redirect('payment_success', order_id=order.id)

    return render(request, 'shop1/payment.html', {
        'order': order,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    })


@require_http_methods(["POST"])
@login_required(login_url='login')
def paypal_capture(request, order_id):
    """Wird nach erfolgreicher PayPal-Zahlung aufgerufen (AJAX)."""
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

        # Replay-Schutz
        if Order.objects.filter(paypal_order_id=paypal_order_id).exclude(id=order.id).exists():
            return JsonResponse({'error': 'Diese PayPal-Transaktion wurde bereits verwendet.'}, status=400)

        # Serverseitige Verifikation gegen die PayPal Orders API (Status + Betrag)
        if not _verify_paypal_order(paypal_order_id, order.gesamt_betrag):
            return JsonResponse({'error': 'Zahlung konnte nicht verifiziert werden.'}, status=400)

        order.paypal_order_id = paypal_order_id
        order.status = 'paid'
        order.save()

        if hasattr(request.user, 'profile'):
            request.user.profile.has_welcome_discount = False
            request.user.profile.save()

        # Lagerbestand reduzieren – Bulk-Fetch statt N+1
        order_items = list(order.items.all())
        produkt_namen = [i.produkt_name for i in order_items]
        produkts_by_name = {p.name: p for p in Produkt.objects.filter(name__in=produkt_namen)}
        for item in order_items:
            db_produkt = produkts_by_name.get(item.produkt_name)
            if db_produkt:
                db_produkt.lagerbestand = max(0, db_produkt.lagerbestand - item.menge)
                db_produkt.aktiv = False
                db_produkt.save()

        try:
            send_order_confirmation_email(order)
        except Exception:
            pass

        return JsonResponse({'status': 'success', 'redirect': f'/payment/success/{order.id}/'})

    except Exception:
        return JsonResponse({'error': 'Zahlung konnte nicht verarbeitet werden.'}, status=500)


@login_required(login_url='login')
def payment_success(request, order_id):
    """Erfolgreiche Zahlung."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Bestellung nicht gefunden.')
        return redirect('warenkorb')

    cart = _get_or_create_cart(request.user)
    cart.items.all().delete()

    return render(request, 'shop1/payment_success.html', {'order': order})


@login_required(login_url='login')
def payment_cancel(request):
    """Zahlung abgebrochen."""
    messages.warning(request, 'Die Zahlung wurde abgebrochen. Dein Warenkorb ist noch vorhanden.')
    return redirect('warenkorb')


def send_order_confirmation_email(order):
    """Sendet eine Bestellbestätigung per E-Mail."""
    items_text = '\n'.join([
        f"- {item.menge}x {item.produkt_name}: {float(item.produkt_preis) * item.menge:.2f} €"
        for item in order.items.all()
    ])
    subject = f'Bestellbestätigung #{order.id}'
    html_content = f"""
    <html><body>
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
    </body></html>
    """
    text_content = f"Bestellbestätigung #{order.id}\n\n{items_text}\n\nGesamt: {float(order.gesamt_betrag):.2f} €"
    send_brevo_email(subject, html_content, order.email, recipient_name=f"{order.vorname} {order.nachname}", text_content=text_content)


def send_bank_details_email(order):
    """Sendet Bankverbindung & PayPal Option bei Wahl von Überweisung."""
    subject = f'Zahlungsinformationen für deine Mission #{order.id}'

    bank_items = list(order.items.all())
    bank_produkt_namen = [i.produkt_name for i in bank_items]
    bank_produkts = {p.name: p for p in Produkt.objects.filter(name__in=bank_produkt_namen)}
    items_html = ""
    for item in bank_items:
        db_produkt = bank_produkts.get(item.produkt_name)
        bild_html = ""
        if db_produkt and db_produkt.bild:
            bild_html = f'<img src="{db_produkt.bild.url}" width="80" style="border-radius: 10px; margin-right: 15px;">'
        items_html += f"""
        <div style="display:flex;align-items:center;padding:15px 0;border-bottom:1px solid #eee;">
            {bild_html}
            <div>
                <p style="margin:0;font-weight:bold;color:#050816;">{item.produkt_name}</p>
                <p style="margin:5px 0 0;color:#888;font-size:12px;">{item.menge}x {item.produkt_preis:.2f} €</p>
            </div>
        </div>"""

    html_content = f"""
    <html><body style="font-family:'Inter',Arial,sans-serif;background:#f9fafb;color:#111827;margin:0;padding:40px;">
        <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:30px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.05);border:1px solid #eee;">
            <div style="background:#050816;padding:40px;text-align:center;">
                <h1 style="color:#fff;margin:0;font-size:24px;text-transform:uppercase;letter-spacing:5px;">Luviq</h1>
                <p style="color:#ff6a00;margin-top:10px;font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:2px;">Mission: Payment Pending</p>
            </div>
            <div style="padding:40px;">
                <h2 style="font-size:20px;font-weight:900;margin-bottom:20px;">Hallo {order.vorname},</h2>
                <p style="line-height:1.6;color:#4b5563;">vielen Dank für deine Bestellung! Bitte begleiche den Betrag zeitnah.</p>
                <div style="margin:30px 0;padding:30px;background:#fdf2f2;border-radius:20px;border-left:5px solid #ff6a00;">
                    <h3 style="margin-top:0;font-size:14px;text-transform:uppercase;letter-spacing:1px;color:#ff6a00;">Zahlungsoption A: Überweisung</h3>
                    <p style="margin:15px 0 5px;font-size:13px;"><strong>Inhaber:</strong> {os.getenv('BANK_INHABER','Luisa Brehler')}</p>
                    <p style="margin:5px 0;font-size:13px;"><strong>IBAN:</strong> {os.getenv('BANK_IBAN','')}</p>
                    <p style="margin:5px 0;font-size:13px;"><strong>Verwendungszweck:</strong> Mission #{order.id}</p>
                    <p style="margin:5px 0;font-size:13px;"><strong>Betrag:</strong> <span style="font-size:18px;font-weight:900;">{float(order.gesamt_betrag):.2f} €</span></p>
                </div>
                <div style="margin:30px 0;padding:30px;background:#eff6ff;border-radius:20px;border-left:5px solid #2563eb;">
                    <h3 style="margin-top:0;font-size:14px;text-transform:uppercase;letter-spacing:1px;color:#2563eb;">Zahlungsoption B: PayPal</h3>
                    <p style="margin:15px 0;font-size:13px;">Sende das Geld an:</p>
                    <p style="margin:5px 0;font-size:16px;font-weight:bold;color:#2563eb;">{os.getenv('PAYPAL_EMAIL','')}</p>
                </div>
                <h3 style="font-size:14px;text-transform:uppercase;letter-spacing:1px;margin-bottom:20px;">Deine Auswahl:</h3>
                {items_html}
                <div style="margin-top:40px;text-align:center;color:#9ca3af;font-size:12px;">
                    <p>Sobald die Zahlung eingegangen ist, erhältst du eine Bestätigung.</p>
                    <p style="margin-top:20px;">Herzliche Grüße,<br><strong style="color:#050816;">Luisa Brehler</strong></p>
                </div>
            </div>
            <div style="background:#f9fafb;padding:30px;text-align:center;border-top:1px solid #eee;">
                <p style="font-size:10px;color:#9ca3af;text-transform:uppercase;letter-spacing:2px;">Luviq Universe © 2026</p>
            </div>
        </div>
    </body></html>
    """
    send_brevo_email(subject, html_content, order.email, recipient_name=f"{order.vorname} {order.nachname}")
