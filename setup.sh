#!/bin/bash

# ChiliView Standalone Setup Script
# Automatische Installation und Konfiguration mit WebODM-CLI Integration

set -e  # Exit on any error

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Globale Variablen für Port-Konfiguration
HTTP_PORT=80
API_PORT=8000

# Logging-Funktionen
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

info() {
    echo -e "${PURPLE}[INFO]${NC} $1"
}

# Banner anzeigen
show_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ChiliView Setup                          ║"
    echo "║          Mehrmandantenfähige Fotoverarbeitungsplattform     ║"
    echo "║                                                              ║"
    echo "║  Automatische Installation aller Abhängigkeiten:            ║"
    echo "║  • Docker & Docker Compose                                  ║"
    echo "║  • WebODM-CLI (Kommandozeilen-Integration)                  ║"
    echo "║  • ClamAV Virenscan                                         ║"
    echo "║  • Potree 3D-Viewer                                         ║"
    echo "║  • Nginx Reverse Proxy                                      ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Betriebssystem erkennen
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            DISTRO=$(lsb_release -si 2>/dev/null || echo "Debian")
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            DISTRO=$(cat /etc/redhat-release | awk '{print $1}')
        else
            OS="linux"
            DISTRO="Unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    else
        OS="unknown"
        DISTRO="Unknown"
    fi
    
    log "Erkanntes Betriebssystem: $DISTRO ($OS)"
}

# Systemvoraussetzungen prüfen
check_system_requirements() {
    log "Prüfe Systemvoraussetzungen..."
    
    # RAM prüfen (mindestens 4GB empfohlen)
    if command -v free &> /dev/null; then
        TOTAL_RAM=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
        if [ "$TOTAL_RAM" -lt 4 ]; then
            warning "Nur ${TOTAL_RAM}GB RAM verfügbar. Mindestens 4GB empfohlen."
        else
            success "${TOTAL_RAM}GB RAM verfügbar"
        fi
    fi
    
    # Speicherplatz prüfen (mindestens 20GB)
    AVAILABLE_SPACE=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 20 ]; then
        warning "Nur ${AVAILABLE_SPACE}GB Speicherplatz verfügbar. Mindestens 20GB empfohlen."
    else
        success "${AVAILABLE_SPACE}GB Speicherplatz verfügbar"
    fi
    
    # Internet-Verbindung prüfen
    if ping -c 1 google.com &> /dev/null; then
        success "Internet-Verbindung verfügbar"
    else
        error "Keine Internet-Verbindung - Installation nicht möglich"
        exit 1
    fi
}

# Port-Verfügbarkeit prüfen
check_port_availability() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
        return 1  # Port belegt
    else
        return 0  # Port frei
    fi
}

# Hardware-Analyse und WebODM-Instanzen-Konfiguration
configure_webodm_instances() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║              Hardware-Analyse & WebODM-Konfiguration         ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log "Analysiere Hardware-Konfiguration..."
    
    # CPU-Informationen ermitteln
    if command -v nproc &> /dev/null; then
        CPU_CORES=$(nproc)
    elif command -v sysctl &> /dev/null && [[ "$OS" == "macos" ]]; then
        CPU_CORES=$(sysctl -n hw.ncpu)
    else
        CPU_CORES=4  # Fallback
    fi
    
    # CPU-Frequenz ermitteln (Linux)
    CPU_FREQ="Unbekannt"
    if [ -f /proc/cpuinfo ]; then
        CPU_FREQ=$(grep "cpu MHz" /proc/cpuinfo | head -1 | awk '{print $4}' | cut -d'.' -f1)
        if [ -n "$CPU_FREQ" ]; then
            CPU_FREQ="${CPU_FREQ} MHz"
        else
            CPU_FREQ="Unbekannt"
        fi
    elif command -v sysctl &> /dev/null && [[ "$OS" == "macos" ]]; then
        CPU_FREQ=$(sysctl -n hw.cpufrequency_max 2>/dev/null)
        if [ -n "$CPU_FREQ" ]; then
            CPU_FREQ="$((CPU_FREQ / 1000000)) MHz"
        else
            CPU_FREQ="Unbekannt"
        fi
    fi
    
    # RAM-Informationen ermitteln
    if command -v free &> /dev/null; then
        TOTAL_RAM_MB=$(free -m | awk 'NR==2{print $2}')
        TOTAL_RAM_GB=$((TOTAL_RAM_MB / 1024))
    elif command -v sysctl &> /dev/null && [[ "$OS" == "macos" ]]; then
        TOTAL_RAM_BYTES=$(sysctl -n hw.memsize)
        TOTAL_RAM_GB=$((TOTAL_RAM_BYTES / 1024 / 1024 / 1024))
    else
        TOTAL_RAM_GB=8  # Fallback
    fi
    
    # CPU-Modell ermitteln (falls verfügbar)
    CPU_MODEL="Unbekannt"
    if [ -f /proc/cpuinfo ]; then
        CPU_MODEL=$(grep "model name" /proc/cpuinfo | head -1 | cut -d':' -f2 | sed 's/^ *//' | cut -c1-50)
    elif command -v sysctl &> /dev/null && [[ "$OS" == "macos" ]]; then
        CPU_MODEL=$(sysctl -n machdep.cpu.brand_string 2>/dev/null | cut -c1-50)
    fi
    
    # Hardware-Informationen anzeigen
    echo -e "${BLUE}📊 Hardware-Analyse:${NC}"
    echo "   CPU: $CPU_MODEL"
    echo "   Kerne: $CPU_CORES"
    echo "   Frequenz: $CPU_FREQ"
    echo "   RAM: ${TOTAL_RAM_GB}GB"
    echo ""
    
    # WebODM-Instanzen-Empfehlung berechnen
    calculate_webodm_recommendation() {
        local cores=$1
        local ram_gb=$2
        
        # Basis-Empfehlung: 1 Instanz pro 2 CPU-Kerne
        local cpu_based=$((cores / 2))
        
        # RAM-basierte Begrenzung: 1 Instanz pro 2GB RAM (WebODM braucht ~1.5GB pro Instanz)
        local ram_based=$((ram_gb / 2))
        
        # Minimum von beiden nehmen
        local recommended=$(( cpu_based < ram_based ? cpu_based : ram_based ))
        
        # Mindestens 1, maximal 12
        if [ $recommended -lt 1 ]; then
            recommended=1
        elif [ $recommended -gt 12 ]; then
            recommended=12
        fi
        
        echo $recommended
    }
    
    RECOMMENDED_INSTANCES=$(calculate_webodm_recommendation $CPU_CORES $TOTAL_RAM_GB)
    
    # Empfehlung mit Begründung anzeigen
    echo -e "${GREEN}💡 Empfohlene WebODM-CLI Instanzen: $RECOMMENDED_INSTANCES${NC}"
    echo ""
    echo -e "${BLUE}Begründung:${NC}"
    
    if [ $CPU_CORES -ge 8 ] && [ $TOTAL_RAM_GB -ge 16 ]; then
        echo "   ✅ Leistungsstarker Server - Mehrere parallele Instanzen möglich"
    elif [ $CPU_CORES -ge 4 ] && [ $TOTAL_RAM_GB -ge 8 ]; then
        echo "   ✅ Mittlere Leistung - Moderate Parallelisierung empfohlen"
    else
        echo "   ⚠️  Begrenzte Ressourcen - Wenige Instanzen für Stabilität"
    fi
    
    echo "   • CPU-Kerne: $CPU_CORES → max. $((CPU_CORES / 2)) Instanzen"
    echo "   • RAM: ${TOTAL_RAM_GB}GB → max. $((TOTAL_RAM_GB / 2)) Instanzen"
    echo "   • WebODM benötigt ~1.5GB RAM + 2 CPU-Kerne pro Instanz"
    echo ""
    
    # Benutzer-Auswahl
    while true; do
        echo -e "${YELLOW}Wie viele WebODM-CLI Instanzen sollen maximal gleichzeitig laufen?${NC}"
        echo "   Empfohlen: $RECOMMENDED_INSTANCES"
        echo "   Minimum: 1"
        echo "   Maximum: 12"
        echo ""
        read -p "Anzahl WebODM-Instanzen [$RECOMMENDED_INSTANCES]: " MAX_WEBODM_INSTANCES
        MAX_WEBODM_INSTANCES=${MAX_WEBODM_INSTANCES:-$RECOMMENDED_INSTANCES}
        
        if [[ "$MAX_WEBODM_INSTANCES" =~ ^[0-9]+$ ]] && [ "$MAX_WEBODM_INSTANCES" -ge 1 ] && [ "$MAX_WEBODM_INSTANCES" -le 12 ]; then
            break
        else
            error "Bitte geben Sie eine Zahl zwischen 1 und 12 ein"
        fi
    done
    
    # Warnung bei hoher Anzahl auf schwacher Hardware
    if [ $MAX_WEBODM_INSTANCES -gt $RECOMMENDED_INSTANCES ]; then
        warning "Sie haben mehr Instanzen gewählt als empfohlen!"
        echo "   Dies kann zu Leistungsproblemen oder Speichermangel führen."
        echo "   Empfohlen für Ihre Hardware: $RECOMMENDED_INSTANCES"
        echo ""
        read -p "Trotzdem fortfahren? (j/N): " CONFIRM_HIGH_INSTANCES
        if [[ ! "$CONFIRM_HIGH_INSTANCES" =~ ^[jJ]$ ]]; then
            MAX_WEBODM_INSTANCES=$RECOMMENDED_INSTANCES
            info "Auf empfohlenen Wert zurückgesetzt: $RECOMMENDED_INSTANCES"
        fi
    fi
    
    success "WebODM-Konfiguration: $MAX_WEBODM_INSTANCES parallele Instanzen"
    
    # Geschätzte Performance anzeigen
    echo ""
    echo -e "${BLUE}📈 Geschätzte Performance:${NC}"
    echo "   • $MAX_WEBODM_INSTANCES User können gleichzeitig verarbeiten"
    echo "   • Durchschnittliche Verarbeitungszeit: 10-15 Minuten pro Projekt"
    echo "   • Maximaler Durchsatz: ~$((MAX_WEBODM_INSTANCES * 4)) Projekte pro Stunde"
    
    if [ $MAX_WEBODM_INSTANCES -gt 1 ]; then
        echo "   • Wartezeit bei Überlastung: ~$((15 / MAX_WEBODM_INSTANCES)) Minuten"
    fi
    echo ""
}

# Port-Konfiguration
configure_ports() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    Port-Konfiguration                       ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    info "Prüfe Port-Verfügbarkeit und konfiguriere Services..."
    
    # HTTP Port (Standard: 80)
    while true; do
        if check_port_availability 80; then
            read -p "HTTP Port [80]: " HTTP_PORT
            HTTP_PORT=${HTTP_PORT:-80}
        else
            warning "Port 80 ist bereits belegt"
            read -p "HTTP Port [8080]: " HTTP_PORT
            HTTP_PORT=${HTTP_PORT:-8080}
        fi
        
        if [[ "$HTTP_PORT" =~ ^[0-9]+$ ]] && [ "$HTTP_PORT" -ge 1 ] && [ "$HTTP_PORT" -le 65535 ]; then
            if check_port_availability "$HTTP_PORT"; then
                break
            else
                error "Port $HTTP_PORT ist bereits belegt"
            fi
        else
            error "Bitte geben Sie eine gültige Portnummer ein (1-65535)"
        fi
    done
    
    # Backend API Port (Standard: 8000)
    while true; do
        if check_port_availability 8000; then
            read -p "Backend API Port [8000]: " API_PORT
            API_PORT=${API_PORT:-8000}
        else
            warning "Port 8000 ist bereits belegt"
            read -p "Backend API Port [8001]: " API_PORT
            API_PORT=${API_PORT:-8001}
        fi
        
        if [[ "$API_PORT" =~ ^[0-9]+$ ]] && [ "$API_PORT" -ge 1 ] && [ "$API_PORT" -le 65535 ]; then
            if check_port_availability "$API_PORT"; then
                break
            else
                error "Port $API_PORT ist bereits belegt"
            fi
        else
            error "Bitte geben Sie eine gültige Portnummer ein (1-65535)"
        fi
    done
    
    success "Port-Konfiguration abgeschlossen:"
    info "  HTTP: $HTTP_PORT"
    info "  HTTPS: $HTTPS_PORT" 
    info "  Backend API: $API_PORT"
    info "  WebODM-CLI: Direkte Integration (kein Port erforderlich)"
}

# Docker installieren
install_docker() {
    if command -v docker &> /dev/null; then
        success "Docker bereits installiert: $(docker --version)"
        return
    fi
    
    log "Installiere Docker..."
    
    case $OS in
        "debian")
            # Docker für Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            
            # Docker GPG Key
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            
            # Docker Repository
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # Docker installieren
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io
            ;;
            
        "redhat")
            # Docker für CentOS/RHEL/Fedora
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            sudo systemctl start docker
            sudo systemctl enable docker
            ;;
            
        "macos")
            # Docker für macOS
            if command -v brew &> /dev/null; then
                brew install --cask docker
                warning "Docker Desktop für macOS installiert. Bitte starten Sie Docker Desktop manuell."
            else
                error "Homebrew nicht gefunden. Bitte installieren Sie Docker Desktop manuell von https://docker.com"
                exit 1
            fi
            ;;
            
        *)
            error "Automatische Docker-Installation für $OS nicht unterstützt"
            error "Bitte installieren Sie Docker manuell: https://docs.docker.com/get-docker/"
            exit 1
            ;;
    esac
    
    # Docker-Gruppe für aktuellen User
    if [ "$OS" != "macos" ]; then
        sudo usermod -aG docker $USER
        warning "Sie müssen sich ab- und wieder anmelden, damit Docker ohne sudo funktioniert"
    fi
    
    success "Docker erfolgreich installiert"
}

# Docker Compose installieren
install_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        success "Docker Compose bereits installiert: $(docker-compose --version)"
        return
    fi
    
    log "Installiere Docker Compose..."
    
    # Neueste Version ermitteln
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    case $OS in
        "linux"|"debian"|"redhat")
            # Docker Compose für Linux
            sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
            
        "macos")
            # Docker Compose ist in Docker Desktop enthalten
            if ! command -v docker-compose &> /dev/null; then
                warning "Docker Compose nicht gefunden. Stellen Sie sicher, dass Docker Desktop läuft."
            fi
            ;;
    esac
    
    success "Docker Compose erfolgreich installiert"
}

# Zusätzliche Tools installieren
install_additional_tools() {
    log "Installiere zusätzliche Tools..."
    
    case $OS in
        "debian")
            sudo apt-get update
            sudo apt-get install -y curl wget unzip git openssl netstat-nat
            ;;
        "redhat")
            sudo yum install -y curl wget unzip git openssl net-tools
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install curl wget unzip git openssl
            fi
            ;;
    esac
    
    success "Zusätzliche Tools installiert"
}

# Admin-Benutzer konfigurieren
configure_admin_user() {
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                 Admin-Benutzer konfigurieren                 ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Admin-Benutzername
    while true; do
        read -p "Admin-Benutzername [admin]: " ADMIN_USERNAME
        ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
        
        if [[ "$ADMIN_USERNAME" =~ ^[a-zA-Z0-9_-]+$ ]] && [ ${#ADMIN_USERNAME} -ge 3 ]; then
            break
        else
            error "Benutzername muss mindestens 3 Zeichen lang sein und nur Buchstaben, Zahlen, _ und - enthalten"
        fi
    done
    
    # Admin-E-Mail
    while true; do
        read -p "Admin-E-Mail: " ADMIN_EMAIL
        
        if [[ "$ADMIN_EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
            break
        else
            error "Bitte geben Sie eine gültige E-Mail-Adresse ein"
        fi
    done
    
    # Admin-Passwort
    while true; do
        read -s -p "Admin-Passwort (mindestens 8 Zeichen): " ADMIN_PASSWORD
        echo ""
        
        if [ ${#ADMIN_PASSWORD} -ge 8 ]; then
            read -s -p "Passwort bestätigen: " ADMIN_PASSWORD_CONFIRM
            echo ""
            
            if [ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD_CONFIRM" ]; then
                break
            else
                error "Passwörter stimmen nicht überein"
            fi
        else
            error "Passwort muss mindestens 8 Zeichen lang sein"
        fi
    done
    
    # Admin-Vollname
    read -p "Admin-Vollname [System Administrator]: " ADMIN_FULLNAME
    ADMIN_FULLNAME=${ADMIN_FULLNAME:-"System Administrator"}
    
    success "Admin-Benutzer konfiguriert: $ADMIN_USERNAME ($ADMIN_EMAIL)"
}

# Umgebungskonfiguration erstellen
create_environment_config() {
    log "Erstelle Umgebungskonfiguration..."
    
    # JWT Secret generieren
    JWT_SECRET=$(openssl rand -hex 32)
    
    # Backend .env erstellen
    cat > backend/.env << EOF
# ChiliView Backend Configuration
# Generiert am $(date)

# JWT Configuration
JWT_SECRET_KEY=$JWT_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Database Configuration
DATABASE_URL=sqlite:///app/data/chiliview.db

# Upload Configuration
UPLOAD_MAX_SIZE=2147483648
MAX_FILES_PER_UPLOAD=1000

# WebODM-CLI Configuration
WEBODM_CLI_PATH=/opt/webodm/webodm.sh

# Security Configuration
VIRUS_SCAN_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging Configuration
LOG_LEVEL=INFO
ENVIRONMENT=production

# Port Configuration
HTTP_PORT=$HTTP_PORT
HTTPS_PORT=$HTTPS_PORT
API_PORT=$API_PORT

# Admin User Configuration
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_FULLNAME=$ADMIN_FULLNAME
EOF

    success "Backend-Konfiguration erstellt"
}

# Erweiterte Docker Compose Konfiguration
create_docker_compose_config() {
    log "Erstelle erweiterte Docker Compose Konfiguration..."
    
    cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  # Backend mit konfigurierbarem Port
  chiliview-backend:
    ports:
      - "$API_PORT:8000"

  # Nginx mit konfigurierbaren Ports
  nginx:
    ports:
      - "$HTTP_PORT:80"
      - "$HTTPS_PORT:443"
    environment:
      - HTTP_PORT=$HTTP_PORT
      - HTTPS_PORT=$HTTPS_PORT
      - API_PORT=$API_PORT
EOF

    success "Docker Compose Override-Konfiguration mit konfigurierbaren Ports erstellt"
}

# Verzeichnisstruktur erstellen
create_directory_structure() {
    log "Erstelle Verzeichnisstruktur..."
    
    # Hauptverzeichnisse
    mkdir -p data/{resellers,webodm_cli,redis,clamav,backups}
    mkdir -p logs
    mkdir -p uploads
    mkdir -p temp
    mkdir -p viewer
    mkdir -p ssl
    
    # Berechtigungen setzen
    chmod 755 data logs uploads temp viewer
    chmod 700 ssl  # SSL-Verzeichnis sicherer
    chmod 777 data/webodm_cli data/redis data/clamav  # Docker braucht Schreibrechte
    
    # .gitkeep Dateien für leere Verzeichnisse
    touch data/.gitkeep
    touch logs/.gitkeep
    touch uploads/.gitkeep
    touch temp/.gitkeep
    
    success "Verzeichnisstruktur erstellt"
}

# Potree Viewer installieren
install_potree_viewer() {
    log "Installiere Potree 3D-Viewer..."
    
    # Potree-Verzeichnis erstellen
    mkdir -p viewer/potree
    
    # Potree von GitHub herunterladen
    POTREE_VERSION="1.8"
    POTREE_URL="https://github.com/potree/potree/releases/download/${POTREE_VERSION}/potree_${POTREE_VERSION}.zip"
    
    if command -v wget &> /dev/null; then
        wget -q "$POTREE_URL" -O potree.zip
    elif command -v curl &> /dev/null; then
        curl -sL "$POTREE_URL" -o potree.zip
    else
        error "Weder wget noch curl verfügbar"
        exit 1
    fi
    
    # Potree extrahieren
    unzip -q potree.zip -d viewer/
    
    # Verzeichnis umbenennen falls nötig
    if [ -d "viewer/potree_${POTREE_VERSION}" ]; then
        mv "viewer/potree_${POTREE_VERSION}"/* viewer/potree/
        rmdir "viewer/potree_${POTREE_VERSION}"
    fi
    
    # Aufräumen
    rm -f potree.zip
    
    success "Potree 3D-Viewer installiert"
}

# SSL-Zertifikate erstellen
setup_ssl_certificates() {
    log "Erstelle SSL-Zertifikate für Entwicklung..."
    
    # Selbstsignierte Zertifikate für Entwicklung
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=DE/ST=State/L=City/O=ChiliView/CN=localhost" \
        2>/dev/null
    
    success "SSL-Zertifikate erstellt (selbstsigniert für Entwicklung)"
}

# Docker Images bauen
build_docker_images() {
    log "Baue Docker Images..."
    
    # Backend Image bauen
    log "Baue Backend Image..."
    docker build -t chiliview-backend:latest ./backend
    
    # Frontend Image bauen
    log "Baue Frontend Image..."
    docker build -t chiliview-frontend:latest ./frontend
    
    success "Docker Images erfolgreich gebaut"
}

# Services starten
start_services() {
    log "Starte ChiliView Services..."
    
    # Services mit Override-Konfiguration starten
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
    
    success "Services gestartet"
}

# Auf Services warten
wait_for_services() {
    log "Warte auf Services..."
    
    # Backend
    log "Warte auf Backend..."
    for i in {1..30}; do
        if curl -f http://localhost:$API_PORT/health &>/dev/null; then
            success "Backend ist bereit"
            break
        fi
        sleep 2
    done
    
    # WebODM-CLI Installation prüfen
    log "Prüfe WebODM-CLI Installation..."
    if [ -f "./data/webodm_cli/webodm.sh" ]; then
        success "WebODM-CLI ist verfügbar"
    else
        info "WebODM-CLI wird beim ersten Start automatisch installiert"
    fi
}

# Gesundheitscheck
perform_health_check() {
    log "Führe Gesundheitscheck durch..."
    
    local all_healthy=true
    
    # Backend
    if curl -f http://localhost:$API_PORT/health &>/dev/null; then
        success "✓ Backend (http://localhost:$API_PORT)"
    else
        error "✗ Backend nicht erreichbar"
        all_healthy=false
    fi
    
    # Frontend/Nginx
    if curl -f http://localhost:$HTTP_PORT &>/dev/null; then
        success "✓ Frontend (http://localhost:$HTTP_PORT)"
    else
        error "✗ Frontend nicht erreichbar"
        all_healthy=false
    fi
    
    # WebODM-CLI
    if [ -f "./data/webodm_cli/webodm.sh" ]; then
        success "✓ WebODM-CLI (Kommandozeilen-Integration)"
    else
        info "ℹ WebODM-CLI wird bei Bedarf automatisch installiert"
    fi
    
    if [ "$all_healthy" = true ]; then
        success "Alle Services sind gesund"
    else
        warning "Einige Services sind nicht verfügbar - prüfen Sie die Logs"
    fi
}

# Abschlussinformationen anzeigen
show_completion_info() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                 ChiliView Setup abgeschlossen!              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}🌐 Anwendung verfügbar unter:${NC}"
    echo "   http://localhost:$HTTP_PORT              (Hauptanwendung)"
    echo "   http://localhost:$API_PORT         (Backend API)"
    echo "   WebODM-CLI: Direkte Integration im Backend"
    echo ""
    echo -e "${BLUE}👤 Admin-Zugangsdaten:${NC}"
    echo "   Benutzername: $ADMIN_USERNAME"
    echo "   E-Mail: $ADMIN_EMAIL"
    echo "   Passwort: [wie eingegeben]"
    echo ""
    echo -e "${BLUE}📁 Wichtige Verzeichnisse:${NC}"
    echo "   data/          - Datenbanken und Benutzerdaten"
    echo "   logs/          - Anwendungslogs"
    echo "   uploads/       - Hochgeladene Dateien"
    echo "   backups/       - Backup-Dateien"
    echo "   viewer/        - 3D-Viewer-Dateien"
    echo ""
    echo -e "${BLUE}🔧 Nützliche Befehle:${NC}"
    echo "   docker-compose logs -f                    # Logs anzeigen"
    echo "   docker-compose ps                         # Container-Status"
    echo "   docker-compose restart chiliview-backend  # Backend neustarten"
    echo "   docker-compose down                       # Services stoppen"
    echo "   docker-compose up -d                      # Services starten"
    echo ""
    echo -e "${GREEN}🎉 ChiliView ist jetzt einsatzbereit!${NC}"
    echo ""
}

# Hauptfunktion
main() {
    show_banner
    
    # System-Checks
    detect_os
    check_system_requirements
    
    # Software installieren
    install_docker
    install_docker_compose
    install_additional_tools
    
    # Konfiguration
    configure_ports
    configure_admin_user
    create_environment_config
    create_docker_compose_config
    
    # Setup
    create_directory_structure
    setup_ssl_certificates
    install_potree_viewer
    
    # Deployment
    build_docker_images
    start_services
    wait_for_services
    
    # Verifikation
    perform_health_check
    show_completion_info
    
    success "ChiliView Setup erfolgreich abgeschlossen!"
}

# Fehlerbehandlung
trap 'error "Setup fehlgeschlagen in Zeile $LINENO. Prüfen Sie die Logs."; exit 1' ERR

# Script ausführen
main "$@"