#!/usr/bin/env python3
"""
ChiliView Backup Script
Erstellt ein vollständiges Backup aller Projektdateien
"""

import os
import zipfile
import shutil
from datetime import datetime
from pathlib import Path

def create_backup():
    # Backup-Name mit Zeitstempel
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"chiliview_backup_{timestamp}"
    backup_file = f"{backup_name}.zip"
    
    print(f"Erstelle Backup: {backup_file}")
    
    # Dateien und Verzeichnisse zum Backup
    items_to_backup = [
        'backend',
        'frontend', 
        'nginx',
        'scripts',
        'docker-compose.yml',
        'docker-compose.override.yml',
        'setup.sh',
        'install.sh',
        'create_backup.sh',
        'README.md',
        '.gitignore'
    ]
    
    try:
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in items_to_backup:
                if os.path.exists(item):
                    if os.path.isfile(item):
                        zipf.write(item, f"{backup_name}/{item}")
                        print(f"✓ Datei hinzugefügt: {item}")
                    elif os.path.isdir(item):
                        for root, dirs, files in os.walk(item):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_path = os.path.join(backup_name, file_path)
                                zipf.write(file_path, arc_path)
                        print(f"✓ Verzeichnis hinzugefügt: {item}")
                else:
                    print(f"⚠ Nicht gefunden: {item}")
        
        # Backup-Größe ermitteln
        backup_size = os.path.getsize(backup_file)
        backup_size_mb = backup_size / (1024 * 1024)
        
        print("\n" + "="*60)
        print(f"✅ Backup erfolgreich erstellt: {backup_file}")
        print(f"📁 Größe: {backup_size_mb:.2f} MB")
        print("\nDas Backup enthält:")
        print("  • Vollständigen Backend-Code (Python/FastAPI)")
        print("  • Vollständigen Frontend-Code (Vue.js)")
        print("  • Docker-Konfiguration")
        print("  • Setup- und Installations-Skripte")
        print("  • Nginx-Konfiguration")
        print("  • Dokumentation")
        print("\nZum Wiederherstellen:")
        print(f"  1. Entpacken Sie {backup_file}")
        print(f"  2. cd {backup_name}")
        print("  3. chmod +x install.sh && ./install.sh")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Erstellen des Backups: {e}")
        return False

if __name__ == "__main__":
    success = create_backup()
    exit(0 if success else 1)