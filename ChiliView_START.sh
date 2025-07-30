#!/bin/bash

echo "========================================"
echo "    ChiliView - Lokale Entwicklung"
echo "========================================"
echo

# Prüfen ob wir im richtigen Verzeichnis sind
if [ ! -f "backend/main.py" ]; then
    echo "FEHLER: Bitte dieses Skript aus dem local_dev Verzeichnis starten!"
    echo
    exit 1
fi

# Prüfen ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python3 ist nicht installiert!"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "macOS: brew install python3"
    echo
    exit 1
fi

# Prüfen ob Node.js installiert ist
if ! command -v node &> /dev/null; then
    echo "FEHLER: Node.js ist nicht installiert!"
    echo "Ubuntu/Debian: sudo apt install nodejs npm"
    echo "macOS: brew install node"
    echo
    exit 1
fi

echo "[1/6] Prüfe Backend Virtual Environment..."
cd backend

if [ ! -d "venv" ]; then
    echo "Virtual Environment nicht gefunden. Erstelle neues venv..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "FEHLER: Konnte Virtual Environment nicht erstellen!"
        exit 1
    fi
fi

echo "[2/6] Aktiviere Virtual Environment und installiere Dependencies..."
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "WARNUNG: Einige Python-Pakete konnten nicht installiert werden."
    echo "Versuche es trotzdem..."
fi

echo "[3/6] Starte Backend Server..."
# Für Linux/Mac verwenden wir screen oder tmux falls verfügbar
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="ChiliView Backend" -- bash -c "cd $(pwd) && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -title "ChiliView Backend" -e "cd $(pwd) && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload; bash" &
else
    # Fallback: Background-Prozess
    echo "Starte Backend im Hintergrund..."
    nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
fi

# Warten bis Backend gestartet ist
echo "Warte auf Backend-Start..."
sleep 5

cd ../frontend

echo "[4/6] Prüfe Frontend Dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Node modules nicht gefunden. Installiere Dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "FEHLER: Frontend Dependencies konnten nicht installiert werden!"
        exit 1
    fi
fi

echo "[5/6] Starte Frontend Development Server..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="ChiliView Frontend" -- bash -c "cd $(pwd) && npm run dev; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -title "ChiliView Frontend" -e "cd $(pwd) && npm run dev; bash" &
else
    # Fallback: Background-Prozess
    echo "Starte Frontend im Hintergrund..."
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
fi

echo "[6/6] Öffne Browser..."
sleep 3

# Browser öffnen (plattformabhängig)
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
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo
echo "Login-Daten:"
echo "Username: admin"
echo "Password: admin123"
echo
echo "Logs:"
echo "Backend:  tail -f backend.log"
echo "Frontend: tail -f frontend.log"
echo
echo "Zum Stoppen: Ctrl+C oder ./stop_chiliview.sh"

# Warten auf Benutzer-Input
read -p "Drücken Sie Enter zum Beenden..."

# Cleanup
echo
echo "Stoppe Server..."
if [ ! -z "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
fi
if [ ! -z "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null
fi

# Alle Node.js und Python Prozesse stoppen (vorsichtig)
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null

echo "Server gestoppt."