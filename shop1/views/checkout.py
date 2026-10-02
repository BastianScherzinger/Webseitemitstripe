"""Checkout und Zahlungsabwicklung (PayPal + Überweisung)."""

import os
import json
import logging
from decimal import Decimal, ROUND_HALF_UP

import requests
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils.html import escape
from django.views.decorators.http import require_http_methods

from ..models import Order, OrderItem
from ..utils import send_brevo_email
from ._helpers import _get_or_create_cart

#: Zustände einer Bestellung, die als bezahlt gelten (``paid`` und alles, was
#: danach kommt). Nur der Übergang **in** diese Menge bucht Bestand ab.
BEZAHLT_STATI = frozenset({'paid', 'processing', 'ready_for_shipping', 'shipped'})

#: Obergrenzen der Bestellfelder = Länge der Spalten in ``Order`` (EIG75).
#: PostgreSQL weist längere Werte mit einem Fehler zurück, SQLite nicht – die
#: Tests liefen deshalb nie in diesen Fehler.
BESTELL_LAENGEN = {
    'vorname': 100, 'nachname': 100, 'email': 254, 'adresse': 255,
    'stadt': 100, 'postleitzahl': 10, 'land': 100, 'telefon': 20,
}

#: Zahlarten, die der Bestellvorgang anbietet.
ZAHLARTEN = ('paypal', 'bank_transfer')

_log = logging.getLogger('shop1')


def _paypal_api_base():
    return 'https://api-m.paypal.com' if os.getenv('PAYPAL_MODE', 'sandbox') == 'live' else 'https://api-m.sandbox.paypal.com'


def _paypal_token():
    """Zugangstoken der PayPal-REST-API oder ``None`` (Zugang fehlt/Fehler)."""
    client_id = settings.PAYPAL_CLIENT_ID
    secret = os.getenv('PAYPAL_SECRET', '')
    if not secret or client_id == 'sb':
        _log.error('PayPal nicht möglich: PAYPAL_SECRET/PAYPAL_CLIENT_ID fehlt.')
        return None
    try:
        antwort = requests.post(
            f'{_paypal_api_base()}/v1/oauth2/token',
            timeout=10,
            auth=(client_id, secret),
            data={'grant_type': 'client_credentials'},
        )
        antwort.raise_for_status()
        return antwort.json()['access_token']
    except Exception as e:
        _log.error('PayPal-Zugangstoken nicht erhalten: %s', e)
        return None


def _paypal_bestellung_anlegen(order):
    """Legt die PayPal-Bestellung **auf dem Server** an (EIG63).

    Betrag und Währung kommen aus der Bestellung in der Datenbank, nicht aus
    dem Browser. Gibt die PayPal-Kennung oder ``None`` zurück."""
    token = _paypal_token()
    if not token:
        return None
    try:
        antwort = requests.post(
            f'{_paypal_api_base()}/v2/checkout/orders',
            timeout=10,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json={
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'custom_id': str(order.id),
                    'description': f'Luviq Mission #{order.id}',
                    'amount': {'currency_code': 'EUR', 'value': f'{order.gesamt_betrag:.2f}'},
                }],
            },
        )
        if antwort.status_code not in (200, 201):
            _log.error('PayPal-Bestellung nicht angelegt (HTTP %s)', antwort.status_code)
            return None
        return antwort.json().get('id')
    except Exception as e:
        _log.error('PayPal-Bestellung nicht angelegt: %s', e)
        return None


def _paypal_einziehen(paypal_order_id):
    """Zieht die von der Kundin freigegebene PayPal-Zahlung **vom Server aus** ein.

    Vorher buchte das Skript im Browser ab (``actions.order.capture()``) und
    meldete es erst danach dem Server – scheiterte dessen Prüfung, war das Geld
    schon weg (EIG63). Jetzt bucht der Server und prüft danach. Eine schon
    eingezogene Bestellung (422 ``ORDER_ALREADY_CAPTURED``) gilt als Erfolg, damit
    ein wiederholter Aufruf nicht scheitert. Gibt ``True`` zurück, wenn PayPal
    die Zahlung eingezogen hat."""
    token = _paypal_token()
    if not token:
        return False
    try:
        antwort = requests.post(
            f'{_paypal_api_base()}/v2/checkout/orders/{paypal_order_id}/capture',
            timeout=10,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        )
        if antwort.status_code in (200, 201):
            return True
        if antwort.status_code == 422 and 'ORDER_ALREADY_CAPTURED' in str(antwort.json()):
            return True
        _log.error('PayPal-Einzug abgelehnt (HTTP %s)', antwort.status_code)
        return False
    except Exception as e:
        _log.error('PayPal-Einzug fehlgeschlagen: %s', e)
        return False


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
            timeout=10,
            auth=(client_id, secret),
            data={'grant_type': 'client_credentials'},
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()['access_token']

        order_resp = requests.get(
            f'{_paypal_api_base()}/v2/checkout/orders/{paypal_order_id}',
            timeout=10,
            headers={'Authorization': f'Bearer {access_token}'},
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


def _rund(betrag):
    return Decimal(betrag).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def _bank_konfiguriert():
    """Überweisung gibt es nur mit hinterlegter IBAN (EIG114): ohne sie stünde
    in der Mail ein leeres Feld, und die Kundin hätte nichts zum Überweisen."""
    return bool(os.getenv('BANK_IBAN', '').strip())


def _verfuegbarkeit(posten):
    """Meldungen zu allen Posten, die sich nicht (mehr) bestellen lassen.

    Prüft je Posten das **Stück selbst** (EIG47): vorhanden, aktiv, nicht im
    Archiv vergeben, in ausreichender Zahl vorrätig. Leere Liste = alles
    bestellbar."""
    probleme = []
    for item in posten:
        produkt = item.produkt()
        if produkt is None or not produkt.aktiv or produkt.vergeben:
            probleme.append(f'"{item.produkt_name}" ist nicht mehr verfügbar.')
        elif produkt.lagerbestand < item.menge:
            probleme.append(f'Von "{item.produkt_name}" ist nur noch {produkt.lagerbestand} verfügbar.')
    return probleme


def _eingaben_pruefen(felder):
    """Fehlermeldung zu den Adressfeldern oder ``None`` (EIG75)."""
    pflicht = ('vorname', 'nachname', 'email', 'adresse', 'stadt', 'postleitzahl', 'land')
    if not all(felder[name] for name in pflicht):
        return 'Bitte fülle alle erforderlichen Felder aus.'
    for name, grenze in BESTELL_LAENGEN.items():
        if len(felder[name]) > grenze:
            return f'Eine Eingabe ist zu lang (höchstens {grenze} Zeichen, Feld „{name}“). Bitte kürze sie.'
    try:
        validate_email(felder['email'])
    except ValidationError:
        return 'Bitte gib eine gültige E-Mail-Adresse an.'
    return None


@login_required(login_url='login')
def checkout(request):
    """Checkout-Seite mit Adressdaten."""
    # EIG56: Die Bestätigungsmail der Registrierung ist ernst gemeint – die
    # Bestellung geht an eine frei wählbare Adresse, also muss das Konto vorher
    # eine bestätigte Adresse haben.
    profil = getattr(request.user, 'profile', None)
    if profil is None or not profil.email_verified:
        messages.warning(request, 'Bitte bestätige zuerst deine E-Mail-Adresse. Den Link hast du '
                                  'per E-Mail bekommen; im Profil kannst du ihn erneut anfordern.')
        return redirect('profil')

    cart = _get_or_create_cart(request.user)
    posten = list(cart.items.order_by('id'))

    if not posten:
        messages.warning(request, 'Dein Warenkorb ist leer.')
        return redirect('warenkorb')

    # EIG47: vor Formular **und** Bestellung prüfen, ob es die Stücke noch gibt.
    probleme = _verfuegbarkeit(posten)
    if probleme:
        for meldung in probleme:
            messages.error(request, meldung)
        return redirect('warenkorb')

    gesamt_betrag_original = sum((item.produkt_preis * item.menge for item in posten), Decimal('0'))

    hat_rabatt = False
    rabatt_wert = Decimal('0')
    if hasattr(request.user, 'profile') and request.user.profile.has_welcome_discount:
        hat_rabatt = True
        rabatt_wert = _rund(gesamt_betrag_original * Decimal('0.10'))

    gesamt_betrag = gesamt_betrag_original - rabatt_wert

    if request.method == 'POST':
        felder = {
            'vorname': request.POST.get('vorname', '').strip(),
            'nachname': request.POST.get('nachname', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'adresse': request.POST.get('adresse', '').strip(),
            'stadt': request.POST.get('stadt', '').strip(),
            'postleitzahl': request.POST.get('postleitzahl', '').strip(),
            'land': request.POST.get('land', 'Deutschland').strip(),
            'telefon': request.POST.get('telefon', '').strip(),
        }

        fehler = _eingaben_pruefen(felder)
        if fehler:
            messages.error(request, fehler)
            return redirect('checkout')

        payment_method = request.POST.get('payment_method', 'paypal')
        if payment_method not in ZAHLARTEN:
            messages.error(request, 'Bitte wähle eine Zahlungsart.')
            return redirect('checkout')
        if payment_method == 'bank_transfer' and not _bank_konfiguriert():
            messages.error(request, 'Die Überweisung ist gerade nicht möglich. Bitte zahle mit PayPal.')
            return redirect('checkout')

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    status='pending',
                    payment_method=payment_method,
                    gesamt_betrag=gesamt_betrag,
                    rabatt_betrag=rabatt_wert,   # EIG16/EIG88: der Rabatt steht in der Bestellung
                    **felder,
                )
                for item in posten:
                    OrderItem.objects.create(
                        order=order,
                        produkt_name=item.produkt_name,
                        produkt_preis=item.produkt_preis,
                        produkt_ref=item.produkt_ref,   # EIG112: das Stück, nicht nur sein Name
                        menge=item.menge,
                    )

            if payment_method == 'bank_transfer':
                try:
                    send_bank_details_email(order)
                except Exception as e:
                    _log.error("Bank-details email error: %s", e)
                # Die Bestellung ist angelegt und in ``OrderItem`` festgehalten –
                # der Warenkorb hat seine Aufgabe erfüllt (EIG23). Die Bankdaten
                # stehen zusätzlich auf der Seite, falls die Mail nicht ankommt
                # (EIG114).
                cart.items.all().delete()
                messages.info(request, '🏛️ Mission gestartet! Bitte schließe die Überweisung ab.')
                return redirect('payment_success', order_id=order.id)

            return redirect('payment', order_id=order.id)

        except Exception:
            _log.exception('Bestellung konnte nicht angelegt werden (Benutzer %s)', request.user.pk)
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
        'laengen': BESTELL_LAENGEN,
        'bank_moeglich': _bank_konfiguriert(),
    })


@login_required(login_url='login')
def payment(request, order_id):
    """Payment-Seite mit PayPal Smart Buttons."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Bestellung nicht gefunden.')
        return redirect('warenkorb')

    if order.status in BEZAHLT_STATI:
        messages.info(request, 'Diese Bestellung wurde bereits bezahlt.')
        return redirect('payment_success', order_id=order.id)

    return render(request, 'shop1/payment.html', {
        'order': order,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    })


@require_http_methods(["POST"])
@login_required(login_url='login')
def paypal_create(request, order_id):
    """Legt die PayPal-Bestellung für eine eigene, offene Bestellung an (AJAX).

    Betrag und Währung bestimmt der Server aus der Bestellung (EIG63); das
    Skript der Bezahlseite bekommt nur die PayPal-Kennung zurück."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Bestellung nicht gefunden'}, status=404)
    if order.status != 'pending' or order.payment_method != 'paypal':
        return JsonResponse({'error': 'Diese Bestellung lässt sich nicht mit PayPal bezahlen.'}, status=400)
    probleme = _verfuegbarkeit(list(order.items.all()))
    if probleme:
        return JsonResponse({'error': ' '.join(probleme)}, status=409)
    kennung = _paypal_bestellung_anlegen(order)
    if not kennung:
        return JsonResponse({'error': 'PayPal ist gerade nicht erreichbar. Es wurde nichts abgebucht.'}, status=502)
    return JsonResponse({'id': kennung})


def bestellung_abschliessen(order, neuer_status='paid'):
    """Bucht eine Bestellung als bezahlt: Status, Bestand, Willkommensrabatt.

    Eine Stelle für beide Wege – PayPal (``paypal_capture``) und das Setzen auf
    „bezahlt" im Panel (``admin_views``). Bestand und Rabatt wirken nur beim
    Übergang **in** einen bezahlten Zustand, ein erneutes „bezahlt" bucht nichts
    ein zweites Mal ab. Die Stücke werden über ihre Kennung gefunden, nicht über
    den Namen (EIG08). Gibt ``True`` zurück, wenn dieser Übergang stattfand."""
    # Eine Sperre auf die Bestellzeile: zwei gleichzeitige Abschlüsse (Doppelklick,
    # zweiter Tab) buchen Bestand und Rabatt nur einmal ab; der zweite sieht den
    # schon bezahlten Zustand und meldet ``False``. (SQLite kennt die Sperre nicht,
    # PostgreSQL schon.)
    with transaction.atomic():
        in_db = Order.objects.select_for_update().values_list('status', flat=True).get(pk=order.pk)
        war_bezahlt = in_db in BEZAHLT_STATI or order.status in BEZAHLT_STATI
        if in_db in BEZAHLT_STATI:
            order.status = in_db
        elif not war_bezahlt:
            order.status = neuer_status
        order.save()
        if war_bezahlt:
            return False

        # EIG15: der Rabatt verfällt mit der ersten bezahlten Bestellung – gleich,
        # wie bezahlt wurde (vorher nur bei PayPal).
        if order.user_id and order.rabatt_betrag > 0 and hasattr(order.user, 'profile'):
            order.user.profile.has_welcome_discount = False
            order.user.profile.save()

        for item in order.items.all():
            db_produkt = item.produkt()
            if db_produkt:
                db_produkt.lagerbestand = max(0, db_produkt.lagerbestand - item.menge)
                # EIG57: das Stück bleibt als vergebenes Archivstück erreichbar, statt
                # seine indexierte Seite in den 404 mitzunehmen; kaufbar ist es nicht mehr.
                db_produkt.vergeben = True
                db_produkt.save()
    return True


@require_http_methods(["POST"])
@login_required(login_url='login')
def paypal_capture(request, order_id):
    """Wird nach der Freigabe bei PayPal aufgerufen (AJAX): zieht ein, prüft, bucht."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Bestellung nicht gefunden'}, status=404)

    if order.status in BEZAHLT_STATI:
        return JsonResponse({'status': 'success', 'redirect': f'/payment/success/{order.id}/'})

    try:
        data = json.loads(request.body)
        paypal_order_id = data.get('paypal_order_id', '')

        if not paypal_order_id:
            return JsonResponse({'error': 'Keine PayPal Order ID'}, status=400)

        # Replay-Schutz
        if Order.objects.filter(paypal_order_id=paypal_order_id).exclude(id=order.id).exists():
            return JsonResponse({'error': 'Diese PayPal-Transaktion wurde bereits verwendet.'}, status=400)

        # EIG63: erst der Server zieht ein, dann prüft er – nicht umgekehrt.
        eingezogen = _paypal_einziehen(paypal_order_id)

        # Serverseitige Verifikation gegen die PayPal Orders API (Status + Betrag)
        if not _verify_paypal_order(paypal_order_id, order.gesamt_betrag):
            if eingezogen:
                _log.error('PayPal hat eingezogen, die Prüfung scheiterte: Bestellung %s, PayPal-Kennung %s '
                           '– Zahlung von Hand klären', order.id, paypal_order_id)
            return JsonResponse({
                'error': f'Zahlung konnte nicht verifiziert werden. Bitte melde dich mit der '
                         f'Bestellnummer #{order.id} bei uns, falls PayPal dein Konto belastet hat.',
            }, status=400)

        order.paypal_order_id = paypal_order_id
        neu_bezahlt = bestellung_abschliessen(order)
        # Bezahlt: der Warenkorb ist erledigt (EIG113 – nicht erst auf der
        # Erfolgsseite, die nur noch anzeigt).
        _get_or_create_cart(request.user).items.all().delete()

        # Nur wer den Übergang in „bezahlt" ausgelöst hat, schickt die Bestätigung –
        # ein gleichzeitiger zweiter Aufruf verschickt sie nicht noch einmal.
        if neu_bezahlt:
            try:
                send_order_confirmation_email(order)
            except Exception:
                _log.exception('Bestellbestätigung konnte nicht versendet werden (Bestellung %s)', order.id)

        return JsonResponse({'status': 'success', 'redirect': f'/payment/success/{order.id}/'})

    except Exception:
        _log.exception('PayPal-Abschluss für Bestellung %s fehlgeschlagen', order.id)
        return JsonResponse({'error': 'Zahlung konnte nicht verarbeitet werden.'}, status=500)


@login_required(login_url='login')
def payment_success(request, order_id):
    """Erfolgsseite: zeigt nur an, ändert nichts (EIG54, EIG113).

    Bezahlte Bestellungen und angelegte Überweisungen bekommen ihre Seite;
    eine offene PayPal-Bestellung geht zurück zur Zahlung – wer die Zahlung
    abgebrochen hat, bekommt keine Bestätigung und verliert seinen Warenkorb
    nicht."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Bestellung nicht gefunden.')
        return redirect('warenkorb')

    ueberweisung_offen = order.status == 'pending' and order.payment_method == 'bank_transfer'
    if order.status not in BEZAHLT_STATI and not ueberweisung_offen:
        messages.warning(request, 'Diese Bestellung ist noch nicht bezahlt.')
        if order.status == 'pending':
            return redirect('payment', order_id=order.id)
        return redirect('warenkorb')

    bank = None
    if ueberweisung_offen and _bank_konfiguriert():
        bank = {
            'inhaber': os.getenv('BANK_INHABER', 'Luisa Brehler'),
            'iban': os.getenv('BANK_IBAN', ''),
            'zweck': f'Mission #{order.id}',
        }
    return render(request, 'shop1/payment_success.html', {'order': order, 'bank': bank})


@login_required(login_url='login')
def payment_cancel(request):
    """Zahlung abgebrochen."""
    messages.warning(request, 'Die Zahlung wurde abgebrochen. Dein Warenkorb ist noch vorhanden.')
    return redirect('warenkorb')


def send_order_confirmation_email(order):
    """Sendet eine Bestellbestätigung per E-Mail.

    Alles, was Kundin oder Betreiberin getippt haben, läuft durch ``escape``
    (EIG65): die Adresse ist frei wählbar, ein eingeschmuggelter Link käme sonst
    vom Absender des Shops bei Dritten an. Die Einzelpreise werden um Zwischen-
    summe und Rabatt ergänzt, damit sie zum Gesamtbetrag passen (EIG16)."""
    posten = list(order.items.all())
    zwischensumme = sum((i.produkt_preis * i.menge for i in posten), Decimal('0'))
    zeilen = [f"- {item.menge}x {{}}: {float(item.produkt_preis) * item.menge:.2f} €" for item in posten]
    items_text = '\n'.join(z.format(item.produkt_name) for z, item in zip(zeilen, posten))
    items_html = '\n'.join(z.format(escape(item.produkt_name)) for z, item in zip(zeilen, posten))
    rabatt_zeile = ''
    rabatt_text = ''
    if order.rabatt_betrag and order.rabatt_betrag > 0:
        rabatt_zeile = (f'\n- Zwischensumme: {float(zwischensumme):.2f} €'
                        f'\n- Willkommensrabatt: -{float(order.rabatt_betrag):.2f} €')
        rabatt_text = (f'\nZwischensumme: {float(zwischensumme):.2f} €'
                       f'\nWillkommensrabatt: -{float(order.rabatt_betrag):.2f} €')
    subject = f'Bestellbestätigung #{order.id}'
    html_content = f"""
    <html><body>
        <h2>Hallo {escape(order.vorname)} {escape(order.nachname)},</h2>
        <p>vielen Dank für deine Bestellung! Deine Zahlung wurde erfolgreich verarbeitet.</p>
        <h3>Bestellnummer: #{order.id}</h3>
        <p><strong>Bestellte Artikel:</strong></p>
        <pre>{items_html}{rabatt_zeile}</pre>
        <p><strong>Gesamtbetrag: {float(order.gesamt_betrag):.2f} €</strong></p>
        <h4>Lieferadresse:</h4>
        <p>{escape(order.adresse)}<br>{escape(order.postleitzahl)} {escape(order.stadt)}<br>{escape(order.land)}</p>
        <p>Vielen Dank für deinen Einkauf!</p>
        <p>Herzliche Grüße,<br>Luisa Brehler</p>
    </body></html>
    """
    text_content = (f"Bestellbestätigung #{order.id}\n\n{items_text}{rabatt_text}"
                    f"\n\nGesamt: {float(order.gesamt_betrag):.2f} €")
    send_brevo_email(subject, html_content, order.email, recipient_name=f"{order.vorname} {order.nachname}", text_content=text_content)


def send_bank_details_email(order):
    """Sendet Bankverbindung & PayPal Option bei Wahl von Überweisung."""
    subject = f'Zahlungsinformationen für deine Mission #{order.id}'

    bank_items = list(order.items.all())
    items_html = ""
    for item in bank_items:
        db_produkt = item.produkt()
        bild_html = ""
        if db_produkt and db_produkt.bild:
            bild_html = f'<img src="{escape(db_produkt.bild.url)}" width="80" style="border-radius: 10px; margin-right: 15px;">'
        items_html += f"""
        <div style="display:flex;align-items:center;padding:15px 0;border-bottom:1px solid #eee;">
            {bild_html}
            <div>
                <p style="margin:0;font-weight:bold;color:#050816;">{escape(item.produkt_name)}</p>
                <p style="margin:5px 0 0;color:#888;font-size:12px;">{item.menge}x {item.produkt_preis:.2f} €</p>
            </div>
        </div>"""
    if order.rabatt_betrag and order.rabatt_betrag > 0:
        items_html += f"""
        <p style="margin:15px 0 0;color:#888;font-size:12px;">Willkommensrabatt: -{float(order.rabatt_betrag):.2f} €</p>"""

    # Option B nur, wenn eine PayPal-Adresse hinterlegt ist – sonst stünde ein
    # leeres Feld in der Mail (EIG114).
    paypal_adresse = os.getenv('PAYPAL_EMAIL', '').strip()
    paypal_block = ''
    if paypal_adresse:
        paypal_block = f"""
                <div style="margin:30px 0;padding:30px;background:#eff6ff;border-radius:20px;border-left:5px solid #2563eb;">
                    <h3 style="margin-top:0;font-size:14px;text-transform:uppercase;letter-spacing:1px;color:#2563eb;">Zahlungsoption B: PayPal</h3>
                    <p style="margin:15px 0;font-size:13px;">Sende das Geld an:</p>
                    <p style="margin:5px 0;font-size:16px;font-weight:bold;color:#2563eb;">{escape(paypal_adresse)}</p>
                </div>"""

    html_content = f"""
    <html><body style="font-family:'Inter',Arial,sans-serif;background:#f9fafb;color:#111827;margin:0;padding:40px;">
        <div style="max-width:600px;margin:0 auto;background:#fff;border-radius:30px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.05);border:1px solid #eee;">
            <div style="background:#050816;padding:40px;text-align:center;">
                <h1 style="color:#fff;margin:0;font-size:24px;text-transform:uppercase;letter-spacing:5px;">Luviq</h1>
                <p style="color:#ff6a00;margin-top:10px;font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:2px;">Mission: Payment Pending</p>
            </div>
            <div style="padding:40px;">
                <h2 style="font-size:20px;font-weight:900;margin-bottom:20px;">Hallo {escape(order.vorname)},</h2>
                <p style="line-height:1.6;color:#4b5563;">vielen Dank für deine Bestellung! Bitte begleiche den Betrag zeitnah.</p>
                <div style="margin:30px 0;padding:30px;background:#fdf2f2;border-radius:20px;border-left:5px solid #ff6a00;">
                    <h3 style="margin-top:0;font-size:14px;text-transform:uppercase;letter-spacing:1px;color:#ff6a00;">Zahlungsoption A: Überweisung</h3>
                    <p style="margin:15px 0 5px;font-size:13px;"><strong>Inhaber:</strong> {escape(os.getenv('BANK_INHABER','Luisa Brehler'))}</p>
                    <p style="margin:5px 0;font-size:13px;"><strong>IBAN:</strong> {escape(os.getenv('BANK_IBAN',''))}</p>
                    <p style="margin:5px 0;font-size:13px;"><strong>Verwendungszweck:</strong> Mission #{order.id}</p>
                    <p style="margin:5px 0;font-size:13px;"><strong>Betrag:</strong> <span style="font-size:18px;font-weight:900;">{float(order.gesamt_betrag):.2f} €</span></p>
                </div>
                {paypal_block}
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
