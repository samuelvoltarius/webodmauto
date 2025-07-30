# ChiliView - Einfacher Start

## 🚀 Ein-Klick Start

**Einfach doppelklicken auf:**
```
ChiliView_START.bat
```

Das war's! Die Datei macht alles automatisch:
- ✅ Prüft Python & Node.js Installation
- ✅ Erstellt Virtual Environment (falls nötig)
- ✅ Installiert alle Dependencies
- ✅ Startet Backend Server (Port 8000)
- ✅ Startet Frontend Server (Port 3000)
- ✅ Öffnet Browser automatisch

## 📋 Voraussetzungen

Stellen Sie sicher, dass folgende Software installiert ist:

1. **Python 3.8+** - [Download hier](https://python.org)
2. **Node.js 16+** - [Download hier](https://nodejs.org)

## 🔐 Login-Daten

Nach dem Start können Sie sich anmelden mit:
- **Username:** `admin`
- **Password:** `admin123`

## 🌐 URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Dokumentation:** http://localhost:8000/docs

## 🛑 Stoppen

Drücken Sie eine beliebige Taste im Batch-Fenster, um beide Server zu stoppen.

## 📁 Projektstruktur

```
local_dev/
├── ChiliView_START.bat    ← Diese Datei starten!
├── backend/               ← FastAPI Backend
│   ├── main.py
│   ├── requirements.txt
│   └── venv/             ← Wird automatisch erstellt
├── frontend/             ← Vue.js Frontend
│   ├── package.json
│   └── node_modules/     ← Wird automatisch erstellt
└── data/                 ← SQLite Datenbanken
```

## 🔧 Manuelle Installation (falls nötig)

Falls die automatische Installation nicht funktioniert:

### Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## 🆘 Problembehebung

### "Python ist nicht installiert"
- Python von https://python.org herunterladen
- Bei Installation "Add to PATH" aktivieren

### "Node.js ist nicht installiert"
- Node.js von https://nodejs.org herunterladen
- LTS Version wählen

### Port bereits belegt
- Andere Anwendungen auf Port 3000/8000 beenden
- Oder Ports in den Konfigurationsdateien ändern

### Dependencies-Fehler
- Internet-Verbindung prüfen
- Antivirus-Software temporär deaktivieren
- Als Administrator ausführen

## 📞 Support

Bei Problemen prüfen Sie:
1. Python & Node.js korrekt installiert?
2. Internet-Verbindung verfügbar?
3. Ports 3000 & 8000 frei?
4. Antivirus blockiert Installation?

---

**Viel Erfolg mit ChiliView! 🌶️**