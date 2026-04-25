from . import views
from . import admin_views
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.startseite, name='home'),
    path('stripe-test/', views.stripe_webhook), # Test-Pfad
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'), # Original-Pfad
    path('produkte/', views.produkte, name='produkte'),
    path('produkt/<int:produkt_id>/', views.produkt_detail, name='produkt_detail'),
    path('kontakt/', views.kontakt, name='kontakt'),
    path('ueber_uns/', views.ueber_uns, name='ueber_uns'),
    path('kontakte/<int:produkt_id>/', views.kontakte, name='kontakte'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('warenkorb/', views.warenkorb, name='warenkorb'),
    path('warenkorb/add/<int:produkt_id>/', views.add_to_cart, name='add_to_cart'),
    path('warenkorb/remove/<str:produkt_name>/', views.remove_from_cart, name='remove_from_cart'),
    path('warenkorb/update/<str:produkt_name>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('profil/', views.profil, name='profil'),
    path('profil/change-password/', views.change_password, name='change_password'),
    path('verify/<str:token>', views.verify_email, name='verify_email_no_slash'),
    path('verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # ═══ RECHTLICHES ═══
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),
    path('agb/', views.agb, name='agb'),

    # Favicon Fix
    path('favicon.ico', RedirectView.as_view(url='/static/shop1/favicon.ico')),
    path('favicon.png', RedirectView.as_view(url='/static/shop1/favicon.png')),

    # ═══ ADMIN ROUTES ═══
    path('shop-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('shop-admin/stats/', admin_views.admin_stats, name='admin_stats'),
    path('shop-admin/users/create/', admin_views.admin_user_create, name='admin_user_create'),
    path('shop-admin/users/<int:user_id>/edit/', admin_views.admin_user_edit, name='admin_user_edit'),
    path('shop-admin/users/<int:user_id>/delete/', admin_views.admin_user_delete, name='admin_user_delete'),
    path('shop-admin/users/<int:user_id>/cart/', admin_views.admin_user_cart, name='admin_user_cart'),
    path('shop-admin/produkte/', admin_views.admin_produkte_list, name='admin_produkte_list'),
    path('shop-admin/produkte/upload/', admin_views.admin_produkt_upload, name='admin_produkt_upload'),
    path('shop-admin/produkte/<int:produkt_id>/edit/', admin_views.admin_produkt_edit, name='admin_produkt_edit'),
    path('shop-admin/produkte/<int:produkt_id>/delete/', admin_views.admin_produkt_delete, name='admin_produkt_delete'),
]