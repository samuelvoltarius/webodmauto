FROM python:3.11-slim

# Arbeitsverzeichnis setzen
WORKDIR /app

# System-Dependencies installieren
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Python-Dependencies kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Verzeichnisse für Daten erstellen
RUN mkdir -p /app/data /app/logs /app/uploads /app/temp

# Berechtigungen setzen
RUN chmod -R 755 /app

# Port freigeben
EXPOSE 8000

# Gesundheitscheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Anwendung starten
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]