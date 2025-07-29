# ChiliView Plattform

Eine mehrmandantenfähige Plattform zur Verarbeitung und Präsentation von Fotodaten (z.B. aus Drohnenbefliegungen) über WebODM-CLI.

## 🎯 Überblick

ChiliView ermöglicht es Admin, Resellern und deren Endkunden (Usern), Projekte hochzuladen, automatisch verarbeiten zu lassen und anschließend in einem eingebetteten Viewer (Potree) zu betrachten.

### Hauptfunktionen

- **Mehrmandantenfähigkeit**: Separate Datenbanken und Branding pro Reseller
- **Rollenbasierte Zugriffskontrolle**: Admin, Reseller, User mit spezifischen Rechten
- **Automatische Fotoverarbeitung**: Integration mit WebODM-CLI für 3D-Modellgenerierung
- **3D-Viewer**: Potree-Integration für interaktive 3D-Modell-Anzeige
- **White-Label Branding**: Anpassbares Design pro Reseller
- **DSGVO-konform**: Datenschutz, Backup/Restore, Audit-Logs
- **Sicherheit**: Virenscan, Rate-Limiting, Impersonation-Logging

## 🏗️ Systemarchitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   WebODM-CLI    │
│   (Vue.js)      │◄──►│   (FastAPI)     │◄──►│   (Processing)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8080    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Database      │              │
         └──────────────┤   (SQLite)      │──────────────┘
                        │   Multi-Tenant  │
                        └─────────────────┘
```

### Technologie-Stack

| Komponente | Technologie | Beschreibung |
|------------|-------------|--------------|
| Frontend | Vue.js 3 + Vite | SPA mit Router, Pinia, TailwindCSS |
| Backend | FastAPI (Python) | REST API mit JWT Auth |
| Datenbank | SQLite | Pro Reseller + zentrale DB |
| Verarbeitung | WebODM-CLI | Automatische 3D-Modellgenerierung |
| Viewer | Potree | 3D-Punktwolken und Mesh-Anzeige |
| Containerisierung | Docker + Compose | Vollständiger Stack |
| Reverse Proxy | Nginx | Load Balancing, SSL, Static Files |
| Virenscan | ClamAV | Upload-Sicherheit |

## 🚀 Installation und Setup

### ⚡ Ein-Klick Installation (Empfohlen)

ChiliView kann mit einem einzigen Befehl vollständig installiert und konfiguriert werden:

```bash
chmod +x install.sh && ./install.sh
```

**Das automatische Setup:**
- ✅ Erkennt Ihr Betriebssystem (Linux, macOS, Windows)
- ✅ Installiert Docker & Docker Compose falls nötig
- ✅ Konfiguriert WebODM vollständig mit PostgreSQL & Redis
- ✅ Richtet ClamAV Virenscan ein
- ✅ Installiert Potree 3D-Viewer automatisch
- ✅ Erstellt Admin-Benutzer interaktiv
- ✅ Startet alle Services automatisch
- ✅ Führt Gesundheitschecks durch

### 🔧 Manuelle Installation

Falls Sie die Installation manuell durchführen möchten:

#### 1. Repository klonen

```bash
git clone <repository-url>
cd chiliviewapp
```

#### 2. Setup-Skript ausführen

```bash
chmod +x setup.sh
./setup.sh
```

Das Setup-Skript führt Sie interaktiv durch die Konfiguration und erstellt automatisch den Admin-Benutzer.

#### 3. Services manuell starten (nur bei manueller Installation)

```bash
# Alle Services mit erweiterter Konfiguration starten
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Logs verfolgen
docker-compose logs -f
```

### 🌐 Zugriff nach Installation

Nach der Installation ist ChiliView sofort verfügbar:

- **Hauptanwendung:** http://localhost
- **Admin-Panel:** http://localhost/admin
- **WebODM:** http://localhost:8080
- **API-Dokumentation:** http://localhost:8000/api/docs
- **Backend-API:** http://localhost:8000

**Admin-Zugangsdaten:** Werden während der Installation interaktiv erstellt

### Systemvoraussetzungen

- **Minimum:** 4GB RAM, 2 CPU Cores, 20GB Storage
- **Empfohlen:** 8GB RAM, 4 CPU Cores, 100GB SSD
- **Internet-Verbindung** für automatische Downloads

## 👥 Benutzerrollen

### 👑 Admin
- Vollständige Systemverwaltung
- Reseller erstellen, bearbeiten, löschen
- Zugriff auf alle Projekte aller Nutzer
- Impersonation (Login als jeder Reseller/User)
- System-Logs und Audit-Trails
- Backup & Restore aller Reseller-Instanzen

### 🧩 Reseller
- Eigener Zugang: `http://localhost/reseller/<reseller_id>`
- Eigene SQLite-Datenbank
- User-Verwaltung (Anlegen, Löschen, Limits setzen)
- Branding-Anpassungen (Logo, Farben, Texte)
- Selbstregistrierung aktivieren/deaktivieren
- Eigene Backups erstellen

### 👤 User
- Upload und Verwaltung eigener Projekte
- 3D-Modell-Viewer nach Verarbeitung
- Projekt-Fortschritt verfolgen
- DSGVO-konformer Datenexport
- Profil-Verwaltung

## 📂 Projektworkflow

### 1. Upload
```
User lädt Bilder hoch (JPG, PNG, TIFF)
    ↓
Virenscan (ClamAV)
    ↓
Validierung (Größe, Format, Limits)
    ↓
Speicherung in Reseller-spezifischem Verzeichnis
```

### 2. Verarbeitung
```
WebODM-CLI wird automatisch aufgerufen
    ↓
Fortschrittsanzeige (Polling) im Dashboard
    ↓
3D-Modell-Generierung (Punktwolke, Mesh, Orthophoto)
    ↓
Ergebnisse in Viewer-Format konvertieren
```

### 3. Anzeige
```
Potree-Viewer wird vorbereitet
    ↓
3D-Modell eingebettet
    ↓
Rohdaten werden gelöscht (Speicherplatz)
    ↓
Viewer-URL für User verfügbar
```

## 🔐 Sicherheitsfeatures

### Authentifizierung
- JWT-basierte Token-Authentifizierung
- Sichere Passwort-Hashing (bcrypt)
- Session-Management mit Ablaufzeiten
- Impersonation mit vollständigem Audit-Trail

### Datenschutz (DSGVO)
- Cookie-Banner mit Zustimmung
- Einwilligung bei Registrierung
- Vollständiger Datenexport (ZIP)
- Soft-Delete mit konfigurierbarer Aufbewahrungszeit
- Audit-Logs für alle Aktionen

### Upload-Sicherheit
- Virenscan mit ClamAV
- Dateityp-Validierung
- Größenlimits pro User/Reseller
- Sichere Dateinamen-Bereinigung

### System-Sicherheit
- Rate-Limiting pro IP
- Security Headers (CSP, HSTS, etc.)
- IP-Whitelisting
- Verdächtige Aktivitäten-Erkennung

## 🎨 White-Label Branding

Jeder Reseller kann sein eigenes Branding konfigurieren:

### Anpassbare Elemente
- **Logo**: Upload oder URL
- **Farben**: Primär- und Sekundärfarben
- **Texte**: Willkommensnachricht, Impressum, Datenschutz
- **Custom CSS/HTML**: Erweiterte Anpassungen (mit Haftungsausschluss)
- **Homepage-Link**: Rücklink zur eigenen Website

### Branding-Zugriff
```
http://localhost/reseller/<reseller_id>/
```

## 💾 Backup & Restore

### Automatische Backups
- Tägliche Backups aller Reseller-Datenbanken
- Komprimierte ZIP-Archive
- Konfigurierbare Aufbewahrungszeit

### Manuelle Backups
```bash
# Reseller-Backup erstellen
curl -X POST "http://localhost/api/admin/backups" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"reseller_id": "example_reseller", "backup_type": "full"}'

# Backup herunterladen
curl -X GET "http://localhost/api/admin/backups/<backup_id>/download" \
  -H "Authorization: Bearer <admin_token>" \
  -o backup.zip
```

### Restore
```bash
# Backup wiederherstellen
curl -X POST "http://localhost/api/admin/backups/<backup_id>/restore" \
  -H "Authorization: Bearer <admin_token>"
```

## 📊 Monitoring und Logs

### Log-Dateien
```
logs/
├── chiliview.log          # Allgemeine Anwendungslogs
├── chiliview_errors.log   # Fehler-spezifische Logs
└── chiliview_audit.log    # Audit-Trail (Sicherheit)
```

### Audit-Events
- Login/Logout-Versuche
- Impersonation-Aktionen
- Datei-Uploads
- Admin-Aktionen
- Backup/Restore-Operationen
- DSGVO-Datenexporte

### System-Monitoring
```bash
# Container-Status prüfen
docker-compose ps

# Logs anzeigen
docker-compose logs -f chiliview-backend
docker-compose logs -f chiliview-frontend

# Ressourcen-Verbrauch
docker stats
```

## 🔧 Konfiguration

### Backend-Konfiguration (`backend/.env`)
```env
# Datenbank
DATABASE_URL=sqlite:///app/data/chiliview.db

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Upload-Limits
UPLOAD_MAX_SIZE=2147483648  # 2GB
MAX_FILES_PER_UPLOAD=1000

# WebODM
WEBODM_URL=http://webodm-cli:8080
WEBODM_USERNAME=admin
WEBODM_PASSWORD=admin

# Sicherheit
VIRUS_SCAN_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Reseller-spezifische Konfiguration
Jeder Reseller kann folgende Einstellungen anpassen:
- Maximale Upload-Größe pro User
- Maximale Anzahl Projekte pro User
- Selbstregistrierung aktivieren/deaktivieren
- Branding-Einstellungen

## 🚨 Troubleshooting

### Häufige Probleme

#### 1. WebODM-CLI nicht erreichbar
```bash
# WebODM-Container prüfen
docker-compose logs webodm-cli

# Neustart
docker-compose restart webodm-cli
```

#### 2. Upload-Fehler
```bash
# Berechtigungen prüfen
ls -la data/resellers/

# Speicherplatz prüfen
df -h

# ClamAV-Status prüfen
docker-compose logs clamav
```

#### 3. Frontend lädt nicht
```bash
# Nginx-Konfiguration prüfen
docker-compose exec nginx nginx -t

# Frontend-Build prüfen
docker-compose logs chiliview-frontend
```

#### 4. Datenbank-Probleme
```bash
# Datenbank-Integrität prüfen
sqlite3 data/chiliview.db "PRAGMA integrity_check;"

# Backup wiederherstellen
cp backups/latest_backup.zip data/
```

### Debug-Modus aktivieren
```bash
# Backend im Debug-Modus starten
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up -d

# Frontend im Development-Modus
cd frontend
npm run dev
```

## 📈 Performance-Optimierung

### Empfohlene Systemressourcen
- **Minimum**: 4GB RAM, 2 CPU Cores, 20GB Storage
- **Empfohlen**: 8GB RAM, 4 CPU Cores, 100GB SSD
- **Produktion**: 16GB RAM, 8 CPU Cores, 500GB SSD

### Optimierungen
1. **Nginx-Caching** für statische Dateien aktivieren
2. **Database-Indexing** für häufige Abfragen
3. **File-Cleanup** für alte Upload-Dateien
4. **Log-Rotation** konfigurieren
5. **CDN** für Frontend-Assets (Produktion)

## 🔄 Updates und Wartung

### Update-Prozess
```bash
# 1. Backup erstellen
docker-compose exec chiliview-backend python -c "
from database.database import db_manager
import asyncio
asyncio.run(db_manager.backup_all_resellers())
"

# 2. Container stoppen
docker-compose down

# 3. Code aktualisieren
git pull origin main

# 4. Container neu bauen und starten
docker-compose build
docker-compose up -d

# 5. Datenbank-Migration (falls nötig)
docker-compose exec chiliview-backend alembic upgrade head
```

### Wartungsaufgaben
```bash
# Log-Dateien rotieren
docker-compose exec chiliview-backend logrotate /etc/logrotate.conf

# Alte Backups löschen (älter als 30 Tage)
find backups/ -name "*.zip" -mtime +30 -delete

# Datenbank-Optimierung
sqlite3 data/chiliview.db "VACUUM;"
```

## 📞 Support und Entwicklung

### Entwicklung
```bash
# Development-Setup
git clone <repository-url>
cd chiliviewapp

# Backend-Development
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend-Development
cd frontend
npm install
npm run dev
```

### Beitragen
1. Fork des Repositories erstellen
2. Feature-Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request erstellen

### Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe `LICENSE` Datei für Details.

---

**ChiliView v1.0.0** - Mehrmandantenfähige Fotoverarbeitungsplattform