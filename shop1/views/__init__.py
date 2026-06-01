"""Views-Package – re-exportiert alle View-Funktionen fuer urls.py Kompatibilitaet."""

from .shop import startseite, werbung_klick, kontakt, kontakte, ueber_uns, produkte, produkt_detail_slug, produkt_detail_redirect
from .auth import login, logout, register, verify_email, resend_verification, delete_account, profil, change_password
from .cart import warenkorb, add_to_cart, remove_from_cart, update_cart
from .checkout import checkout, payment, paypal_capture, payment_success, payment_cancel
from .legal import impressum, datenschutz, agb, robots_txt, sitemap_xml, newsletter_subscribe
from .gaestebuch import gaestebuch, comment_add, comment_like, comment_delete

__all__ = [
    # shop
    'startseite', 'werbung_klick', 'kontakt', 'kontakte', 'ueber_uns', 'produkte', 'produkt_detail_slug', 'produkt_detail_redirect',
    # auth
    'login', 'logout', 'register', 'verify_email', 'resend_verification', 'delete_account', 'profil', 'change_password',
    # cart
    'warenkorb', 'add_to_cart', 'remove_from_cart', 'update_cart',
    # checkout
    'checkout', 'payment', 'paypal_capture', 'payment_success', 'payment_cancel',
    # legal
    'impressum', 'datenschutz', 'agb', 'robots_txt', 'sitemap_xml', 'newsletter_subscribe',
    # gaestebuch
    'gaestebuch', 'comment_add', 'comment_like', 'comment_delete',
]
