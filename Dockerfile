# Basis-Image
FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Umgebungsvariablen setzen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Start-Skript ausführbar machen
RUN chmod +x /app/start.sh

# Port freigeben (für Railway informativ)
EXPOSE 8000

# Start-Skript ausführen
CMD ["/app/start.sh"]
