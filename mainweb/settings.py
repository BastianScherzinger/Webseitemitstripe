"""
Django settings for mainweb project.
"""

from pathlib import Path
from dotenv import load_dotenv
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

_SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-CHANGE_THIS_IN_PRODUCTION')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

if not DEBUG and _SECRET_KEY.startswith('django-insecure-'):
    raise RuntimeError(
        'SECRET_KEY ist nicht gesetzt oder unsicher. '
        'Setze die Umgebungsvariable SECRET_KEY auf einen zufälligen Wert.'
    )
SECRET_KEY = _SECRET_KEY

# In Production nur bekannte Hosts erlauben; DEBUG erlaubt alles lokal.
# ALLOWED_HOSTS_EXTRA robust parsen: Nutzer tragen dort oft aus Versehen
# "https://domain.com" statt "domain.com" ein - das würde ALLOWED_HOSTS
# sonst wirkungslos machen. Außerdem wird automatisch die jeweils andere
# Variante (mit/ohne "www.") ergänzt, falls nur eine davon eingetragen wurde.
_extra_raw = [
    h.strip().removeprefix('https://').removeprefix('http://').rstrip('/')
    for h in os.getenv('ALLOWED_HOSTS_EXTRA', '').split(',') if h.strip()
]
_extra = set(_extra_raw)
for _h in _extra_raw:
    _extra.add(_h[4:] if _h.startswith('www.') else f'www.{_h}')
_extra = sorted(_extra)

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.up.railway.app'] + _extra

# ═══ CSRF / PROXY ═══

CSRF_TRUSTED_ORIGINS = [
    'https://*.up.railway.app',
    'https://luviq-luisa-production.up.railway.app',
    'http://localhost',
    'http://127.0.0.1',
] + [f'https://{_h}' for _h in _extra]

# Railway terminiert HTTPS am Proxy und leitet intern als HTTP weiter
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False      # False = HTMX/JS kann CSRF-Token lesen
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG

# ═══ APPS ═══

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',   # staticfiles MUSS vor cloudinary_storage kommen
    'cloudinary_storage',           # sonst überschreibt cs den collectstatic-Befehl
    'cloudinary',
    'axes',
    'shop1',
]

# ═══ MIDDLEWARE ═══

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'shop1.middleware.PageVisitMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ═══ AXES BRUTE-FORCE-SCHUTZ ═══

AXES_FAILURE_LIMIT = 10            # 10 Versuche (nicht 5) – weniger Risiko für Admin-Lockout
AXES_COOLOFF_TIME = 1              # 1 Stunde Sperrung
AXES_LOCKOUT_TEMPLATE = 'shop1/lockout.html'
AXES_RESET_ON_SUCCESS = True
# Sperre nur wenn GLEICHER Username + GLEICHE IP fehlschlägt (nicht nur IP)
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]

# ═══ URLS / TEMPLATES ═══

ROOT_URLCONF = 'mainweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop1.context_processors.shop_owner_check',
            ],
        },
    },
]

WSGI_APPLICATION = 'mainweb.wsgi.application'

# ═══ DATENBANK ═══

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600
    )
}

# ═══ PYSTORE-DATENBANK (Werbung/WerbungStat Cross-Site) ═══
# Railway-Variable: PYSTORE_DATABASE_URL
# Ohne Variable: Fallback auf lokale DB (Entwicklung)
_pystore_url = os.getenv('PYSTORE_DATABASE_URL')
if _pystore_url:
    DATABASES['pystore'] = dj_database_url.parse(_pystore_url, conn_max_age=600)
else:
    DATABASES['pystore'] = DATABASES['default']

DATABASE_ROUTERS = ['shop1.routers.WerbungRouter']

# ═══ PASSWORT-VALIDIERUNG ═══

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ═══ SPRACHE / ZEITZONE ═══

LANGUAGE_CODE = 'de-de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

# ═══ STATISCHE DATEIEN ═══

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # ManifestStaticFilesStorage: keine Threading-Komprimierung (behebt den
        # FileNotFoundError in whitenoise/compress.py), erstellt Manifest für Cache-Busting
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

# Rückwärtskompatibilität (für eventuelle ältere Pakete die das Attribut prüfen)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

if os.getenv('CLOUDINARY_URL'):
    STORAGES["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ═══ E-MAIL ═══

USE_SMTP_EMAIL = os.getenv('USE_SMTP_EMAIL', 'False') == 'True'

if USE_SMTP_EMAIL or not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp-relay.brevo.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
    EMAIL_TIMEOUT = 30
    if EMAIL_PORT == 465:
        EMAIL_USE_TLS = False
        EMAIL_USE_SSL = True
    else:
        EMAIL_USE_TLS = True
        EMAIL_USE_SSL = False
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@luviq-shop.de')
SITE_URL = os.getenv('SITE_URL', 'https://luviq-luisa-production.up.railway.app')

# ═══ SICHERHEITSEINSTELLUNGEN ═══

# Session
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600        # 2 Wochen

# CSRF
CSRF_COOKIE_SECURE = not DEBUG      # nochmal explizit (überschreibt frühere Zeile)

# Clickjacking
X_FRAME_OPTIONS = 'DENY'

# Immer aktiv (kein Grund nur in Production)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# SSL/HSTS (nur in Production)
SECURE_SSL_REDIRECT = not DEBUG
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True

APPEND_SLASH = True

# ═══ PAYPAL ═══

PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', 'sb')

# ═══ LOGIN / LOGOUT ═══

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ═══ GOOGLE MAPS ═══
GOOGLE_REVIEW_URL = os.getenv('GOOGLE_REVIEW_URL', 'https://www.google.com/maps/search/Luviq+Universe+Alsfeld')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'shop1': {'handlers': ['console'], 'level': 'INFO', 'propagate': True},
    },
}
