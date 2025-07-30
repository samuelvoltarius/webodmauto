#!/bin/bash

echo "========================================"
echo "    ChiliView - Docker Setup"
echo "========================================"
echo

# Prüfen ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    echo "FEHLER: Docker ist nicht installiert!"
    echo "Installation: https://docs.docker.com/get-docker/"
    echo
    exit 1
fi

# Prüfen ob Docker Compose installiert ist
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "FEHLER: Docker Compose ist nicht installiert!"
    echo "Installation: https://docs.docker.com/compose/install/"
    echo
    exit 1
fi

# Prüfen ob wir im richtigen Verzeichnis sind
if [ ! -f "docker-compose.yml" ]; then
    echo "FEHLER: Bitte dieses Skript aus dem local_dev Verzeichnis starten!"
    echo
    exit 1
fi

echo "[1/5] Erstelle notwendige Verzeichnisse..."
mkdir -p data logs uploads temp backups viewer

echo "[2/5] Stoppe eventuell laufende Container..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null

echo "[3/5] Baue Docker Images..."
if command -v docker-compose &> /dev/null; then
    docker-compose build
else
    docker compose build
fi

if [ $? -ne 0 ]; then
    echo "FEHLER: Docker Build fehlgeschlagen!"
    exit 1
fi

echo "[4/5] Starte ChiliView Container..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
else
    docker compose up -d
fi

if [ $? -ne 0 ]; then
    echo "FEHLER: Container konnten nicht gestartet werden!"
    exit 1
fi

echo "[5/5] Warte auf Container-Start..."
echo "Prüfe Backend..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend ist bereit!"
        break
    fi
    echo "Warte auf Backend... ($i/30)"
    sleep 2
done

echo "Prüfe Frontend..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend ist bereit!"
        break
    fi
    echo "Warte auf Frontend... ($i/30)"
    sleep 2
done

# Browser öffnen (plattformabhängig)
echo "Öffne Browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
else
    echo "Bitte öffnen Sie manuell: http://localhost:3000"
fi

echo
echo "========================================"
echo "    ChiliView erfolgreich gestartet!"
echo "========================================"
echo
echo "🌐 URLs:"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "🔐 Login-Daten:"
echo "Username: admin"
echo "Password: admin123"
echo
echo "📊 Container Status:"
if command -v docker-compose &> /dev/null; then
    docker-compose ps
else
    docker compose ps
fi
echo
echo "📝 Logs anzeigen:"
echo "Alle Logs:     docker-compose logs -f"
echo "Backend Logs:  docker-compose logs -f backend"
echo "Frontend Logs: docker-compose logs -f frontend"
echo
echo "🛑 Stoppen:"
echo "docker-compose down"
echo
echo "Drücken Sie Ctrl+C zum Beenden des Skripts..."

# Warten auf Benutzer-Input
trap 'echo -e "\n\nStoppe Container..."; docker-compose down 2>/dev/null || docker compose down 2>/dev/null; echo "Container gestoppt."; exit 0' INT

# Endlos-Schleife um das Skript am Leben zu halten
while true; do
    sleep 1
done