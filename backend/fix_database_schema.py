"""
ChiliView Datenbank-Schema-Reparatur
Fügt fehlende Spalten zur bestehenden Datenbank hinzu
"""

import os
import sys
import sqlite3
from pathlib import Path

# Backend-Pfad zum Python-Path hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def fix_database_schema():
    """
    Repariert das Datenbank-Schema durch Hinzufügen fehlender Spalten
    """
    try:
        print("🔧 Starte Datenbank-Schema-Reparatur...")
        
        db_path = Path("data/chiliview.db")
        if not db_path.exists():
            print("❌ Datenbank nicht gefunden!")
            return False
        
        # Direkte SQLite-Verbindung
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Prüfen welche Spalten in der resellers-Tabelle existieren
        cursor.execute("PRAGMA table_info(resellers)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 Vorhandene Spalten in resellers: {columns}")
        
        # Fehlende Spalten hinzufügen
        missing_columns = []
        
        if 'storage_limit_gb' not in columns:
            cursor.execute("ALTER TABLE resellers ADD COLUMN storage_limit_gb INTEGER DEFAULT 50")
            missing_columns.append('storage_limit_gb')
            print("✅ Spalte 'storage_limit_gb' hinzugefügt")
        
        if 'max_users' not in columns:
            cursor.execute("ALTER TABLE resellers ADD COLUMN max_users INTEGER DEFAULT 10")
            missing_columns.append('max_users')
            print("✅ Spalte 'max_users' hinzugefügt")
        
        # Users-Tabelle prüfen (falls sie in der zentralen DB existiert)
        try:
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [row[1] for row in cursor.fetchall()]
            
            if 'storage_limit_gb' not in user_columns and user_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN storage_limit_gb INTEGER DEFAULT 10")
                missing_columns.append('users.storage_limit_gb')
                print("✅ Spalte 'storage_limit_gb' zu users hinzugefügt")
        except sqlite3.OperationalError:
            # Users-Tabelle existiert nicht in zentraler DB (normal)
            pass
        
        # Änderungen speichern
        conn.commit()
        conn.close()
        
        if missing_columns:
            print(f"✅ Schema-Reparatur erfolgreich! Hinzugefügte Spalten: {', '.join(missing_columns)}")
        else:
            print("✅ Schema ist bereits korrekt - keine Änderungen erforderlich")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema-Reparatur fehlgeschlagen: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        print("🎉 Datenbank-Schema erfolgreich repariert!")
        print("💡 Sie können jetzt das Backend neu starten")
    else:
        print("❌ Schema-Reparatur fehlgeschlagen")
        sys.exit(1)