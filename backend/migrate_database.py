"""
ChiliView Datenbank-Migration
Erstellt alle Tabellen neu mit dem korrekten Schema
"""

import os
import sys
import shutil
from pathlib import Path

# Backend-Pfad zum Python-Path hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import central_engine, db_manager
from database.models import Base
import asyncio

async def migrate_database():
    """
    Migriert die Datenbank mit dem aktuellen Schema
    """
    try:
        print("🔄 Starte Datenbank-Migration...")
        
        # Backup der alten Datenbank erstellen
        old_db_path = Path("data/chiliview.db")
        if old_db_path.exists():
            backup_path = Path("data/chiliview_backup.db")
            shutil.copy2(old_db_path, backup_path)
            print(f"✅ Backup erstellt: {backup_path}")
        
        # Alte Datenbank löschen
        if old_db_path.exists():
            old_db_path.unlink()
            print("🗑️ Alte Datenbank gelöscht")
        
        # Neue Datenbank mit korrektem Schema erstellen
        print("🏗️ Erstelle neue Datenbank mit aktuellem Schema...")
        Base.metadata.create_all(bind=central_engine)
        
        # Standard-Admin und System-Konfiguration erstellen
        print("👤 Erstelle Standard-Admin und System-Konfiguration...")
        await db_manager.init_central_database()
        
        print("✅ Datenbank-Migration erfolgreich abgeschlossen!")
        print("📋 Standard-Admin: admin / ChiliView2024!")
        
    except Exception as e:
        print(f"❌ Migration fehlgeschlagen: {str(e)}")
        
        # Backup wiederherstellen falls vorhanden
        backup_path = Path("data/chiliview_backup.db")
        if backup_path.exists():
            shutil.copy2(backup_path, old_db_path)
            print("🔄 Backup wiederhergestellt")
        
        raise

if __name__ == "__main__":
    asyncio.run(migrate_database())