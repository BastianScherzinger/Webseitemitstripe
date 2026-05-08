from . import views
from . import admin_views
from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.startseite, name='home'),
    path('paypal/capture/<int:order_id>/', views.paypal_capture, name='paypal_capture'),
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
    
    # ═══ PASSWORD RESET ═══
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='shop1/password_reset_form.html',
        email_template_name='shop1/password_reset_email.html',
        html_email_template_name='shop1/password_reset_email.html',
        subject_template_name='shop1/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='shop1/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='shop1/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='shop1/password_reset_complete.html'
    ), name='password_reset_complete'),
    # ═══ RECHTLICHES ═══
    path('impressum/', views.impressum, name='impressum'),
    path('datenschutz/', views.datenschutz, name='datenschutz'),
    path('agb/', views.agb, name='agb'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    
    # ═══ SEO ═══
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),

    # ═══ GÄSTEBUCH & KOMMENTARE ═══
    path('gaestebuch/', views.gaestebuch, name='gaestebuch'),
    path('comment/add/', views.comment_add, name='comment_add'),
    path('comment/<int:comment_id>/like/', views.comment_like, name='comment_like'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),

    # Favicon Fix
    path('favicon.ico', RedirectView.as_view(url='/static/shop1/favicon.ico')),
    path('favicon.png', RedirectView.as_view(url='/static/shop1/favicon.png')),

    # ═══ ADMIN ROUTES ═══
    path('shop-admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('shop-admin/stats/', admin_views.admin_stats, name='admin_stats'),
    path('shop-admin/stats/reset-visits/', admin_views.admin_reset_visits, name='admin_reset_visits'),
    path('shop-admin/stats/reset-orders/', admin_views.admin_reset_orders, name='admin_reset_orders'),
    path('shop-admin/users/create/', admin_views.admin_user_create, name='admin_user_create'),
    path('shop-admin/users/<int:user_id>/edit/', admin_views.admin_user_edit, name='admin_user_edit'),
    path('shop-admin/users/<int:user_id>/delete/', admin_views.admin_user_delete, name='admin_user_delete'),
    path('shop-admin/users/<int:user_id>/cart/', admin_views.admin_user_cart, name='admin_user_cart'),
    path('shop-admin/produkte/', admin_views.admin_produkte_list, name='admin_produkte_list'),
    path('shop-admin/produkte/upload/', admin_views.admin_produkt_upload, name='admin_produkt_upload'),
    path('shop-admin/produkte/<int:produkt_id>/edit/', admin_views.admin_produkt_edit, name='admin_produkt_edit'),
    path('shop-admin/produkte/<int:produkt_id>/delete/', admin_views.admin_produkt_delete, name='admin_produkt_delete'),
    path('shop-admin/produkte/<int:produkt_id>/resend-newsletter/', admin_views.admin_resend_newsletter, name='admin_resend_newsletter'),
    path('shop-admin/produkte/<int:produkt_id>/reset-newsletter/', admin_views.admin_newsletter_reset, name='admin_newsletter_reset'),
    path('shop-admin/produkte/<int:produkt_id>/toggle/', admin_views.admin_produkt_toggle, name='admin_produkt_toggle'),
    path('shop-admin/orders/', admin_views.admin_orders_list, name='admin_orders_list'),
    path('shop-admin/orders/<int:order_id>/', admin_views.admin_order_detail, name='admin_order_detail'),
    path('shop-admin/orders/<int:order_id>/delete/', admin_views.admin_order_delete, name='admin_order_delete'),
]