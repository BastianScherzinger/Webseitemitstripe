#!/bin/sh

# ═══ MIGRATIONEN ═══
echo "Running migrations..."
python manage.py migrate --noinput

# ═══ SUPERUSER ANLEGEN ═══
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "Creating superuser $ADMIN_USERNAME..."
    python manage.py shell -c "
import os
from django.contrib.auth.models import User
username = os.environ.get('ADMIN_USERNAME')
email    = os.environ.get('ADMIN_EMAIL', 'admin@shop.de')
password = os.environ.get('ADMIN_PASSWORD')
if username and password:
    user, created = User.objects.get_or_create(username=username)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    print('Superuser', username, 'created' if created else 'updated')
"
fi

# ═══ FIXTURES LADEN ═══
python manage.py loaddata initial_data.json 2>/dev/null || true

# ═══ PYSTORE SCHEMA FIX ═══
echo "Fixing pystore schema (seite column)..."
python manage.py fix_pystore_schema

# ═══ STATISCHE DATEIEN SAMMELN ═══
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "WARNING: collectstatic failed"

# ═══ UMGEBUNG UND AUSGELIEFERTE SEITE PRUEFEN ═══
# Nach collectstatic (die Seiten brauchen das Manifest), vor Gunicorn.
# Bewusst NICHT blockierend: ein Fehler steht im Log, die Seite geht
# trotzdem online - ein Abbruch wegen einer fehlenden Variablen naehme
# den Shop offline, das waere schlechter als heute. Blockierend waere
# "python manage.py pruefe_seite --streng" ohne "|| ...".
echo "Checking environment and delivered pages..."
python manage.py pruefe_seite || echo "WARNING: pruefe_seite reported errors (see above), starting anyway"

# ═══ GUNICORN STARTEN ═══
# Die Anwendung ist E/A-gebunden (Datenbank, Cloudinary, ip-api): deshalb
# gthread mit mehreren Threads je Worker statt nur zwei gleichzeitiger
# Anfragen fuer den ganzen Shop. Jeder Thread haelt eine eigene
# Datenbankverbindung (CONN_MAX_AGE=600): 2 x 4 = 8, dazu bis zu 4 je
# Worker aus dem Geo-Pool der Middleware. --timeout 30 statt 120: die
# langsamste gemessene Seite lag bei 11 s (Befund PF10); eine haengende
# Anfrage blockiert so keinen halben Pool mehr fuer zwei Minuten.
# --max-requests erneuert Worker regelmaessig, der Jitter verhindert,
# dass beide gleichzeitig neu starten. Kein --preload: es teilte die
# Datenbankverbindungen ueber den Fork (zwei Datenbanken, ein Router).
# Die drei Werte lassen sich per Railway-Variable ohne Deploy zuruecknehmen.
echo "Starting Gunicorn on port $PORT..."
exec gunicorn mainweb.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --worker-class gthread \
    --workers "${GUNICORN_WORKERS:-2}" \
    --threads "${GUNICORN_THREADS:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-30}" \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile -
