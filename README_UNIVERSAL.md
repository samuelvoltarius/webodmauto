# ChiliView - Universal Start Guide 🌶️

ChiliView kann auf **allen Plattformen** gestartet werden! Wählen Sie Ihre bevorzugte Methode:

## 🚀 Schnellstart-Optionen

### 🪟 **Windows**
```bash
# Doppelklick auf:
ChiliView_START.bat
```

### 🐧 **Linux / 🍎 macOS**
```bash
# Terminal öffnen und ausführen:
chmod +x ChiliView_START.sh
./ChiliView_START.sh
```

### 🐳 **Docker (Alle Plattformen)**
```bash
# Terminal öffnen und ausführen:
chmod +x ChiliView_DOCKER.sh
./ChiliView_DOCKER.sh

# Oder manuell:
docker-compose up -d
```

---

## 📋 Voraussetzungen

### Native Installation (Windows/Linux/macOS):
- **Python 3.8+** - [Download](https://python.org)
- **Node.js 16+** - [Download](https://nodejs.org)

### Docker Installation:
- **Docker** - [Download](https://docs.docker.com/get-docker/)
- **Docker Compose** - [Download](https://docs.docker.com/compose/install/)

---

## 🎯 Nach dem Start

### 🌐 URLs:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Dokumentation:** http://localhost:8000/docs

### 🔐 Login-Daten:
- **Username:** `admin`
- **Password:** `admin123`

---

## 📁 Projektstruktur

```
local_dev/
├── 🚀 ChiliView_START.bat     ← Windows Start
├── 🚀 ChiliView_START.sh      ← Linux/macOS Start
├── 🐳 ChiliView_DOCKER.sh     ← Docker Start
├── 📄 docker-compose.yml      ← Docker Konfiguration
├── backend/                   ← FastAPI Backend
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                  ← Vue.js Frontend
│   ├── package.json
│   └── Dockerfile
└── data/                      ← SQLite Datenbanken
```

---

## 🛠️ Plattform-spezifische Anweisungen

### 🪟 **Windows**

**Automatisch:**
1. Doppelklick auf `ChiliView_START.bat`
2. Warten bis Browser öffnet
3. Mit `admin` / `admin123` anmelden

**Manuell:**
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Neues Terminal:
cd frontend
npm install
npm run dev
```

### 🐧 **Linux**

**Automatisch:**
```bash
chmod +x ChiliView_START.sh
./ChiliView_START.sh
```

**Manuell:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Neues Terminal:
cd frontend
npm install
npm run dev
```

**Abhängigkeiten installieren:**
```bash
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm

# CentOS/RHEL:
sudo yum install python3 python3-pip nodejs npm

# Arch Linux:
sudo pacman -S python python-pip nodejs npm
```

### 🍎 **macOS**

**Automatisch:**
```bash
chmod +x ChiliView_START.sh
./ChiliView_START.sh
```

**Abhängigkeiten installieren:**
```bash
# Mit Homebrew:
brew install python3 node

# Oder von den offiziellen Websites herunterladen
```

### 🐳 **Docker (Alle Plattformen)**

**Automatisch:**
```bash
chmod +x ChiliView_DOCKER.sh
./ChiliView_DOCKER.sh
```

**Manuell:**
```bash
# Container starten:
docker-compose up -d

# Logs anzeigen:
docker-compose logs -f

# Container stoppen:
docker-compose down
```

---

## 🔧 Erweiterte Konfiguration

### Ports ändern:
- **Backend:** In `backend/main.py` oder `docker-compose.yml`
- **Frontend:** In `frontend/vite.config.js` oder `docker-compose.yml`

### Datenbank-Pfad:
- **Native:** `data/chiliview.db`
- **Docker:** Volume-gemountet in Container

### Logs:
- **Native:** Terminal-Output
- **Docker:** `docker-compose logs -f`

---

## 🆘 Problembehebung

### "Python/Node.js nicht gefunden"
- Installieren Sie Python 3.8+ und Node.js 16+
- Stellen Sie sicher, dass sie im PATH sind

### "Port bereits belegt"
- Stoppen Sie andere Anwendungen auf Port 3000/8000
- Oder ändern Sie die Ports in der Konfiguration

### "Docker nicht gefunden"
- Installieren Sie Docker Desktop
- Starten Sie Docker Desktop vor dem Ausführen

### "Permission denied" (Linux/macOS)
```bash
chmod +x ChiliView_START.sh
chmod +x ChiliView_DOCKER.sh
```

### "Dependencies-Fehler"
- Prüfen Sie Ihre Internet-Verbindung
- Deaktivieren Sie temporär Antivirus/Firewall
- Führen Sie als Administrator/sudo aus

---

## 📞 Support & Features

### ✅ **Vollständig implementiert:**
- Multi-Tenant Architektur (Admin → Reseller → User)
- WebODM-CLI Integration für Photogrammetrie
- Potree Viewer für 3D-Modelle
- Speicherlimit-Management
- Hardware-Erkennung
- DSGVO-konforme Audit-Logs
- White-Label Branding
- Backup/Restore System

### 🔐 **Sicherheit:**
- JWT-basierte Authentifizierung
- Rollen-basierte Zugriffskontrolle
- Passwort-Hashing mit bcrypt
- SQL-Injection Schutz
- CORS-Konfiguration

### 🌐 **Technologie-Stack:**
- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Frontend:** Vue.js 3, Tailwind CSS, Pinia
- **3D Viewer:** Potree
- **Photogrammetrie:** WebODM-CLI
- **Containerisierung:** Docker, Docker Compose

---

**Viel Erfolg mit ChiliView! 🌶️**

Bei Fragen oder Problemen prüfen Sie die Logs oder kontaktieren Sie den Support.