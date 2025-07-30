# ChiliView - Lokale Entwicklung

Dieses Verzeichnis enthält eine lokale Entwicklungsversion von ChiliView, die ohne Docker läuft.

## Systemanforderungen

- Python 3.8+ (https://python.org/)
- Node.js 16+ (https://nodejs.org/)
- npm (wird mit Node.js installiert)

## Schnellstart

### Windows
```bash
start_local.bat
```

### Linux/Mac
```bash
python start_local.py
```

## Was passiert beim Start?

1. **Systemprüfung**: Python und Node.js werden geprüft
2. **Backend-Setup**: Virtual Environment wird erstellt und Python-Abhängigkeiten installiert
3. **Frontend-Setup**: Node.js-Abhängigkeiten werden installiert
4. **Services starten**: Backend (Port 8000) und Frontend (Port 3000) werden gestartet
5. **Browser öffnet**: Automatisch auf http://localhost:3000

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Dokumentation**: http://localhost:8000/docs

## Beenden

Drücken Sie `Ctrl+C` im Terminal um beide Services zu beenden.

## Hinweise

- Beim ersten Start werden alle Abhängigkeiten installiert (kann einige Minuten dauern)
- Das Backend läuft im Development-Modus mit Auto-Reload
- Das Frontend läuft im Development-Modus mit Hot-Reload
- Daten werden in `backend/data/` gespeichert
- Logs werden in `backend/logs/` gespeichert

## Troubleshooting

### Python nicht gefunden
Installieren Sie Python von https://python.org/ und stellen Sie sicher, dass es im PATH ist.

### Node.js nicht gefunden
Installieren Sie Node.js von https://nodejs.org/ und stellen Sie sicher, dass es im PATH ist.

### Port bereits belegt
Falls Port 8000 oder 3000 bereits belegt sind, beenden Sie andere Services oder ändern Sie die Ports in den Konfigurationsdateien.

### Abhängigkeiten-Fehler
Löschen Sie `backend/venv/` und `frontend/node_modules/` und starten Sie erneut.
