#!/bin/sh

# Migrations ausführen
echo "Running migrations..."
python manage.py migrate --noinput

# Statische Dateien sammeln
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Server mit Gunicorn starten (für Production)
# Railway setzt automatisch die Umgebungsvariable PORT
echo "Starting Gunicorn on port $PORT..."
exec gunicorn mainweb.wsgi:application --bind 0.0.0.0:$PORT
