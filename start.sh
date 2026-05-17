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

# ═══ GUNICORN STARTEN ═══
echo "Starting Gunicorn on port $PORT..."
exec gunicorn mainweb.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
