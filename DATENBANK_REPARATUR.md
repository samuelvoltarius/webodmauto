# ChiliView Datenbank-Reparatur Anleitung

## Problem
Nach der Schema-Reparatur müssen alle laufenden Backend-Prozesse neu gestartet werden, damit die Änderungen wirksam werden.

## Lösung

### 1. Backend stoppen
Alle laufenden Backend-Prozesse beenden (Strg+C in den Terminals)

### 2. Schema-Reparatur ausführen
```bash
cd local_dev/backend
python fix_database_schema.py
```

### 3. Backend neu starten
```bash
cd local_dev/backend
venv\Scripts\activate
python main.py
```

### 4. Frontend neu starten (falls nötig)
```bash
cd local_dev/frontend
npm run dev
```

## Behobene Probleme

✅ **Datenbank-Schema**: Fehlende Spalten `storage_limit_gb` und `max_users` hinzugefügt
✅ **SQLAlchemy Relationships**: Audit-Log Foreign Key Probleme behoben
✅ **Windows-Kompatibilität**: Alle Windows-spezifischen Pfad- und Encoding-Probleme gelöst

## Verifikation

Nach dem Neustart sollten folgende Funktionen wieder funktionieren:
- ✅ Login ohne Serverfehler
- ✅ Reseller-Daten laden
- ✅ Reseller erstellen/bearbeiten
- ✅ Backup/Log-Löschung
- ✅ Dashboard-Statistiken

## Bei weiteren Problemen

Falls nach dem Neustart immer noch Fehler auftreten:

1. Logs überprüfen:
   - `local_dev/backend/logs/chiliview_errors.log`
   - `local_dev/backend/logs/chiliview.log`

2. Datenbank-Schema verifizieren:
   ```bash
   cd local_dev/backend
   python -c "
   import sqlite3
   conn = sqlite3.connect('data/chiliview.db')
   cursor = conn.cursor()
   cursor.execute('PRAGMA table_info(resellers)')
   print('Resellers Spalten:', [row[1] for row in cursor.fetchall()])
   conn.close()
   "
   ```

3. Komplette Datenbank-Neuerstellung (nur im Notfall):
   ```bash
   cd local_dev/backend
   python migrate_database.py