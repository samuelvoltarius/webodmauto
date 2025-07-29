#!/bin/bash

# ChiliView Deployment Script
# Automatisiertes Deployment der ChiliView-Plattform

set -e  # Exit on any error

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging-Funktion
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Konfiguration
ENVIRONMENT=${1:-production}
BACKUP_DIR="backups/pre-deploy-$(date +%Y%m%d_%H%M%S)"
COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
fi

log "ChiliView Deployment gestartet (Environment: $ENVIRONMENT)"

# Voraussetzungen prüfen
check_prerequisites() {
    log "Prüfe Voraussetzungen..."
    
    # Docker prüfen
    if ! command -v docker &> /dev/null; then
        error "Docker ist nicht installiert"
        exit 1
    fi
    
    # Docker Compose prüfen
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose ist nicht installiert"
        exit 1
    fi
    
    # Git prüfen (für Updates)
    if ! command -v git &> /dev/null; then
        warning "Git ist nicht installiert - Updates nicht möglich"
    fi
    
    # Freier Speicherplatz prüfen (mindestens 5GB)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_SPACE" -lt 5242880 ]; then  # 5GB in KB
        warning "Weniger als 5GB freier Speicherplatz verfügbar"
    fi
    
    success "Voraussetzungen erfüllt"
}

# Backup erstellen
create_backup() {
    if [ -d "data" ]; then
        log "Erstelle Backup..."
        mkdir -p "$BACKUP_DIR"
        
        # Datenbank-Backup
        if [ -f "data/chiliview.db" ]; then
            cp "data/chiliview.db" "$BACKUP_DIR/"
            log "Zentrale Datenbank gesichert"
        fi
        
        # Reseller-Datenbanken
        if [ -d "data/resellers" ]; then
            cp -r "data/resellers" "$BACKUP_DIR/"
            log "Reseller-Datenbanken gesichert"
        fi
        
        # Konfigurationsdateien
        if [ -f "backend/.env" ]; then
            cp "backend/.env" "$BACKUP_DIR/"
        fi
        
        success "Backup erstellt: $BACKUP_DIR"
    else
        log "Keine bestehenden Daten gefunden - Backup übersprungen"
    fi
}

# Umgebungsvariablen prüfen
check_environment() {
    log "Prüfe Umgebungskonfiguration..."
    
    if [ ! -f "backend/.env" ]; then
        warning "backend/.env nicht gefunden - erstelle Beispiel-Konfiguration"
        
        cat > backend/.env << EOF
# ChiliView Backend Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///app/data/chiliview.db
UPLOAD_MAX_SIZE=2147483648
WEBODM_CLI_PATH=/usr/local/bin/webodm
VIRUS_SCAN_ENABLED=true
LOG_LEVEL=INFO
ENVIRONMENT=$ENVIRONMENT
EOF
        
        warning "WICHTIG: Bitte backend/.env konfigurieren und Deployment erneut starten!"
        exit 1
    fi
    
    # Kritische Variablen prüfen
    source backend/.env
    
    if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "your-super-secret-jwt-key-change-in-production" ]; then
        error "JWT_SECRET_KEY muss in backend/.env gesetzt werden!"
        exit 1
    fi
    
    success "Umgebungskonfiguration OK"
}

# Docker Images bauen
build_images() {
    log "Baue Docker Images..."
    
    # Backend bauen
    log "Baue Backend Image..."
    docker build -t chiliview-backend:latest ./backend
    
    # Frontend bauen
    log "Baue Frontend Image..."
    docker build -t chiliview-frontend:latest ./frontend
    
    success "Docker Images erfolgreich gebaut"
}

# Services starten
start_services() {
    log "Starte Services..."
    
    # Alte Container stoppen
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Neue Container starten
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Services gestartet"
}

# Gesundheitscheck
health_check() {
    log "Führe Gesundheitscheck durch..."
    
    # Warten auf Services
    sleep 30
    
    # Backend-Health prüfen
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Backend ist erreichbar"
    else
        error "Backend-Gesundheitscheck fehlgeschlagen"
        return 1
    fi
    
    # Frontend-Health prüfen
    if curl -f http://localhost:3000/health > /dev/null 2>&1; then
        success "Frontend ist erreichbar"
    else
        error "Frontend-Gesundheitscheck fehlgeschlagen"
        return 1
    fi
    
    # WebODM-Health prüfen
    if curl -f http://localhost:8080 > /dev/null 2>&1; then
        success "WebODM ist erreichbar"
    else
        warning "WebODM-Gesundheitscheck fehlgeschlagen (möglicherweise noch am Starten)"
    fi
    
    success "Gesundheitscheck abgeschlossen"
}

# Datenbank initialisieren
init_database() {
    log "Initialisiere Datenbank..."
    
    # Warten bis Backend bereit ist
    sleep 10
    
    # Datenbank-Migration (falls nötig)
    docker-compose -f "$COMPOSE_FILE" exec -T chiliview-backend python -c "
from database.database import init_database
import asyncio
asyncio.run(init_database())
print('Datenbank erfolgreich initialisiert')
"
    
    success "Datenbank initialisiert"
}

# Cleanup alte Images
cleanup() {
    log "Räume alte Docker Images auf..."
    
    # Ungenutzte Images entfernen
    docker image prune -f
    
    # Ungenutzte Volumes entfernen
    docker volume prune -f
    
    success "Cleanup abgeschlossen"
}

# Post-Deployment Informationen
show_info() {
    echo ""
    echo "======================================"
    echo "ChiliView Deployment abgeschlossen!"
    echo "======================================"
    echo ""
    echo "🌐 Anwendung verfügbar unter:"
    echo "   http://localhost (Frontend)"
    echo "   http://localhost:8000 (Backend API)"
    echo "   http://localhost:8080 (WebODM)"
    echo ""
    echo "👤 Standard-Admin-Zugangsdaten:"
    echo "   Benutzername: admin"
    echo "   Passwort: ChiliView2024!"
    echo "   ⚠️  WICHTIG: Passwort nach erstem Login ändern!"
    echo ""
    echo "📁 Wichtige Verzeichnisse:"
    echo "   data/          - Datenbanken und Uploads"
    echo "   logs/          - Anwendungslogs"
    echo "   backups/       - Backup-Dateien"
    echo ""
    echo "🔧 Nützliche Befehle:"
    echo "   docker-compose logs -f                    # Logs anzeigen"
    echo "   docker-compose ps                         # Container-Status"
    echo "   docker-compose restart chiliview-backend  # Backend neustarten"
    echo "   ./scripts/backup.sh                       # Manuelles Backup"
    echo ""
    echo "📖 Dokumentation: README.md"
    echo ""
}

# Rollback-Funktion
rollback() {
    error "Deployment fehlgeschlagen - führe Rollback durch..."
    
    # Services stoppen
    docker-compose -f "$COMPOSE_FILE" down
    
    # Backup wiederherstellen (falls vorhanden)
    if [ -d "$BACKUP_DIR" ]; then
        log "Stelle Backup wieder her..."
        
        if [ -f "$BACKUP_DIR/chiliview.db" ]; then
            mkdir -p data
            cp "$BACKUP_DIR/chiliview.db" "data/"
        fi
        
        if [ -d "$BACKUP_DIR/resellers" ]; then
            mkdir -p data
            cp -r "$BACKUP_DIR/resellers" "data/"
        fi
        
        success "Backup wiederhergestellt"
    fi
    
    error "Rollback abgeschlossen - bitte Logs prüfen"
    exit 1
}

# Hauptfunktion
main() {
    # Trap für Fehlerbehandlung
    trap rollback ERR
    
    check_prerequisites
    create_backup
    check_environment
    build_images
    start_services
    init_database
    
    # Gesundheitscheck mit Retry
    if ! health_check; then
        log "Erster Gesundheitscheck fehlgeschlagen - warte und versuche erneut..."
        sleep 60
        if ! health_check; then
            error "Gesundheitscheck endgültig fehlgeschlagen"
            exit 1
        fi
    fi
    
    cleanup
    show_info
    
    success "ChiliView erfolgreich deployed!"
}

# Script ausführen
main "$@"