# Basis-Image
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Abhängigkeiten für PostgreSQL und Pillow installieren
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Abhängigkeiten installieren (requirements.lock: Constraint-Datei, die
# requirements.txt selbst einbindet – ohne sie bricht pip ab)
COPY requirements.txt requirements.lock ./
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Umgebungsvariablen setzen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Start-Skript ausführbar machen
RUN chmod +x /app/start.sh

# Port freigeben
EXPOSE 8000

# Start-Skript ausführen
CMD ["/app/start.sh"]
