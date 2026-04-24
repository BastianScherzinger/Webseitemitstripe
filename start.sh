#!/bin/sh

# Migrations ausführen
echo "Running migrations..."
python manage.py migrate --noinput

# Superuser automatisch erstellen (falls Variablen gesetzt sind)
if [ "$ADMIN_USERNAME" ]; then
    echo "Creating superuser $ADMIN_USERNAME..."
    python manage.py shell -c "from django.contrib.auth.models import User; import os; \
        username=os.getenv('ADMIN_USERNAME'); \
        email=os.getenv('ADMIN_EMAIL'); \
        password=os.getenv('ADMIN_PASSWORD'); \
        not User.objects.filter(username=username).exists() and User.objects.create_superuser(username, email, password)"
fi

# Statische Dateien sammeln
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Server mit Gunicorn starten (für Production)
# Railway setzt automatisch die Umgebungsvariable PORT
echo "Starting Gunicorn on port $PORT..."
exec gunicorn mainweb.wsgi:application --bind 0.0.0.0:$PORT
