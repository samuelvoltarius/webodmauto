#!/bin/bash

# ChiliView Backup Script
# Erstellt ein vollständiges Backup aller Projektdateien

BACKUP_NAME="chiliview_backup_$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_NAME}.zip"

echo "Erstelle Backup: $BACKUP_FILE"

# Temporäres Verzeichnis für Backup erstellen
mkdir -p "/tmp/$BACKUP_NAME"

# Alle wichtigen Dateien kopieren
echo "Kopiere Projektdateien..."

# Backend
cp -r backend "/tmp/$BACKUP_NAME/"
echo "✓ Backend kopiert"

# Frontend
cp -r frontend "/tmp/$BACKUP_NAME/"
echo "✓ Frontend kopiert"

# Nginx Konfiguration
mkdir -p "/tmp/$BACKUP_NAME/nginx"
cp nginx/nginx.conf "/tmp/$BACKUP_NAME/nginx/" 2>/dev/null || echo "nginx.conf nicht gefunden"
echo "✓ Nginx Konfiguration kopiert"

# Scripts
mkdir -p "/tmp/$BACKUP_NAME/scripts"
cp scripts/*.sh "/tmp/$BACKUP_NAME/scripts/" 2>/dev/null || echo "Scripts nicht gefunden"
echo "✓ Scripts kopiert"

# Docker Konfiguration
cp docker-compose.yml "/tmp/$BACKUP_NAME/" 2>/dev/null || echo "docker-compose.yml nicht gefunden"
cp docker-compose.override.yml "/tmp/$BACKUP_NAME/" 2>/dev/null || echo "docker-compose.override.yml nicht gefunden"
echo "✓ Docker Konfiguration kopiert"

# Setup und Installation
cp setup.sh "/tmp/$BACKUP_NAME/" 2>/dev/null || echo "setup.sh nicht gefunden"
cp install.sh "/tmp/$BACKUP_NAME/" 2>/dev/null || echo "install.sh nicht gefunden"
echo "✓ Setup-Skripte kopiert"

# Dokumentation
cp README.md "/tmp/$BACKUP_NAME/" 2>/dev/null || echo "README.md nicht gefunden"
echo "✓ Dokumentation kopiert"

# .gitignore und andere Konfigurationsdateien
cp .gitignore "/tmp/$BACKUP_NAME/" 2>/dev/null || echo ".gitignore nicht gefunden"

# ZIP-Archiv erstellen
echo "Erstelle ZIP-Archiv..."
cd /tmp
zip -r "$BACKUP_FILE" "$BACKUP_NAME" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # Backup ins Projektverzeichnis verschieben
    mv "/tmp/$BACKUP_FILE" "./"
    
    # Temporäres Verzeichnis aufräumen
    rm -rf "/tmp/$BACKUP_NAME"
    
    echo ""
    echo "✅ Backup erfolgreich erstellt: $BACKUP_FILE"
    echo "📁 Größe: $(du -h "$BACKUP_FILE" | cut -f1)"
    echo ""
    echo "Das Backup enthält:"
    echo "  • Vollständigen Backend-Code (Python/FastAPI)"
    echo "  • Vollständigen Frontend-Code (Vue.js)"
    echo "  • Docker-Konfiguration"
    echo "  • Setup- und Installations-Skripte"
    echo "  • Nginx-Konfiguration"
    echo "  • Dokumentation"
    echo ""
    echo "Zum Wiederherstellen:"
    echo "  unzip $BACKUP_FILE"
    echo "  cd $BACKUP_NAME"
    echo "  chmod +x install.sh && ./install.sh"
else
    echo "❌ Fehler beim Erstellen des Backups"
    rm -rf "/tmp/$BACKUP_NAME"
    exit 1
fi