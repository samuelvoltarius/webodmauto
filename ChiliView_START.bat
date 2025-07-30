@echo off
echo ========================================
echo    ChiliView - Lokale Entwicklung
echo ========================================
echo.

:: Prüfen ob wir im richtigen Verzeichnis sind
if not exist "backend\main.py" (
    echo FEHLER: Bitte diese Datei aus dem local_dev Verzeichnis starten!
    echo.
    pause
    exit /b 1
)

:: Prüfen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH!
    echo Bitte Python 3.8+ installieren: https://python.org
    echo.
    pause
    exit /b 1
)

:: Prüfen ob Node.js installiert ist
node --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Node.js ist nicht installiert oder nicht im PATH!
    echo Bitte Node.js installieren: https://nodejs.org
    echo.
    pause
    exit /b 1
)

echo [1/6] Prüfe Backend Virtual Environment...
cd backend
if not exist "venv\Scripts\activate.bat" (
    echo Virtual Environment nicht gefunden. Erstelle neues venv...
    python -m venv venv
    if errorlevel 1 (
        echo FEHLER: Konnte Virtual Environment nicht erstellen!
        pause
        exit /b 1
    )
)

echo [2/6] Aktiviere Virtual Environment und installiere Dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo WARNUNG: Einige Python-Pakete konnten nicht installiert werden.
    echo Versuche es trotzdem...
)

echo [3/6] Starte Backend Server...
start "ChiliView Backend" cmd /k "venv\Scripts\activate.bat && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

:: Warten bis Backend gestartet ist
echo Warte auf Backend-Start...
timeout /t 5 /nobreak >nul

cd ..\frontend

echo [4/6] Prüfe Frontend Dependencies...
if not exist "node_modules" (
    echo Node modules nicht gefunden. Installiere Dependencies...
    npm install
    if errorlevel 1 (
        echo FEHLER: Frontend Dependencies konnten nicht installiert werden!
        pause
        exit /b 1
    )
)

echo [5/6] Starte Frontend Development Server...
start "ChiliView Frontend" cmd /k "npm run dev"

echo [6/6] Öffne Browser...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo    ChiliView erfolgreich gestartet!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Login-Daten:
echo Username: admin
echo Password: admin123
echo.
echo Drücken Sie eine beliebige Taste zum Beenden...
echo (Dies stoppt beide Server)
pause >nul

echo.
echo Stoppe Server...
taskkill /f /im "node.exe" >nul 2>&1
taskkill /f /im "python.exe" >nul 2>&1
echo Server gestoppt.