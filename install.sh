#!/bin/bash

# ChiliView Vollständiges Installationsskript
# Automatische Installation und Konfiguration für sofortige Nutzung

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ChiliView Installer                      ║"
echo "║          Vollständige Standalone-Installation               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Berechtigungen für Skripte setzen
echo -e "${BLUE}[INFO]${NC} Setze Berechtigungen für Installationsskripte..."
chmod +x setup.sh
chmod +x scripts/init-webodm.sh
chmod +x scripts/deploy.sh

# Verzeichnisse mit korrekten Berechtigungen erstellen
echo -e "${BLUE}[INFO]${NC} Erstelle Verzeichnisstruktur..."
mkdir -p {data/{resellers,webodm,postgres,redis,clamav},logs,uploads,temp,backups,viewer,ssl}

# Berechtigungen setzen
chmod 755 data logs uploads temp backups viewer
chmod 700 ssl
chmod 777 data/webodm data/postgres data/redis data/clamav  # Docker braucht Schreibrechte

# .gitkeep Dateien für leere Verzeichnisse
touch data/.gitkeep logs/.gitkeep uploads/.gitkeep temp/.gitkeep

echo -e "${GREEN}[SUCCESS]${NC} Verzeichnisstruktur erstellt"

# Setup-Skript ausführen
echo -e "${BLUE}[INFO]${NC} Starte Hauptinstallation..."
./setup.sh

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                Installation abgeschlossen!                  ║"
echo "║                                                              ║"
echo "║  ChiliView ist jetzt vollständig installiert und            ║"
echo "║  konfiguriert. Alle Services laufen automatisch.            ║"
echo "║                                                              ║"
echo "║  🌐 Anwendung: http://localhost                             ║"
echo "║  📊 Admin-Panel: http://localhost/admin                     ║"
echo "║  🔧 WebODM: http://localhost:8080                           ║"
echo "║  📖 API-Docs: http://localhost:8000/api/docs               ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"