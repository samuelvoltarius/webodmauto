"""
ChiliView Datenbankverbindung und -konfiguration
Verwaltet zentrale Datenbank und Reseller-spezifische SQLite-Datenbanken
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
import asyncio
from pathlib import Path
import structlog
from typing import Dict, Optional
import sqlite3

from .models import Base, Admin, Reseller, SystemConfig

logger = structlog.get_logger(__name__)

# Zentrale Datenbank-Engine
CENTRAL_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/chiliview.db")
central_engine = create_engine(
    CENTRAL_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in CENTRAL_DATABASE_URL else {},
    poolclass=StaticPool if "sqlite" in CENTRAL_DATABASE_URL else None,
    echo=False  # In Produktion auf False setzen
)

# Session Factory für zentrale Datenbank
CentralSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=central_engine)

# Cache für Reseller-Datenbank-Engines
reseller_engines: Dict[str, any] = {}
reseller_sessions: Dict[str, sessionmaker] = {}

class DatabaseManager:
    """
    Verwaltet zentrale und Reseller-spezifische Datenbankverbindungen
    Implementiert Mandantentrennung durch separate SQLite-Dateien
    """
    
    def __init__(self):
        self.central_engine = central_engine
        self.central_session = CentralSessionLocal
    
    async def init_central_database(self):
        """
        Initialisiert die zentrale Datenbank mit Admin- und Reseller-Tabellen
        """
        try:
            # Verzeichnis für zentrale DB erstellen
            db_path = Path("data")
            db_path.mkdir(exist_ok=True)
            
            # Tabellen erstellen
            Base.metadata.create_all(bind=self.central_engine)
            
            # Standard-Admin erstellen falls nicht vorhanden
            await self.create_default_admin()
            
            # System-Konfiguration initialisieren
            await self.init_system_config()
            
            logger.info("Zentrale Datenbank erfolgreich initialisiert")
            
        except Exception as e:
            logger.error(f"Fehler bei Initialisierung der zentralen Datenbank: {str(e)}")
            raise
    
    async def create_default_admin(self):
        """
        Erstellt Standard-Admin-Benutzer falls nicht vorhanden
        """
        from auth.password_handler import PasswordHandler
        
        db = self.central_session()
        try:
            # Prüfen ob bereits ein Admin existiert
            existing_admin = db.query(Admin).first()
            if existing_admin:
                logger.info("Admin-Benutzer bereits vorhanden")
                return
            
            # Standard-Admin erstellen
            password_handler = PasswordHandler()
            default_password = "ChiliView2024!"  # In Produktion ändern!
            
            admin = Admin(
                username="admin",
                email="admin@chiliview.local",
                password_hash=password_handler.hash_password(default_password),
                full_name="System Administrator",
                is_active=True
            )
            
            db.add(admin)
            db.commit()
            
            logger.info("Standard-Admin erstellt", username="admin", email="admin@chiliview.local")
            logger.warning("WICHTIG: Standard-Passwort in Produktion ändern!")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Erstellen des Standard-Admins: {str(e)}")
            raise
        finally:
            db.close()
    
    async def init_system_config(self):
        """
        Initialisiert System-Konfiguration mit Standardwerten
        """
        db = self.central_session()
        try:
            default_configs = [
                {
                    "key": "max_upload_size_global",
                    "value": "2147483648",  # 2GB
                    "description": "Maximale Upload-Größe in Bytes (global)"
                },
                {
                    "key": "webodm_cli_timeout",
                    "value": "3600",  # 1 Stunde
                    "description": "Timeout für WebODM-CLI Verarbeitung in Sekunden"
                },
                {
                    "key": "virus_scan_enabled",
                    "value": "true",
                    "description": "Virenscan für Uploads aktiviert"
                },
                {
                    "key": "backup_retention_days",
                    "value": "30",
                    "description": "Backup-Aufbewahrungszeit in Tagen"
                },
                {
                    "key": "gdpr_data_retention_days",
                    "value": "2555",  # 7 Jahre
                    "description": "DSGVO Datenaufbewahrung in Tagen"
                }
            ]
            
            for config in default_configs:
                existing = db.query(SystemConfig).filter(SystemConfig.key == config["key"]).first()
                if not existing:
                    system_config = SystemConfig(**config)
                    db.add(system_config)
            
            db.commit()
            logger.info("System-Konfiguration initialisiert")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler bei System-Konfiguration: {str(e)}")
            raise
        finally:
            db.close()
    
    def get_reseller_database_path(self, reseller_id: str) -> str:
        """
        Gibt den Pfad zur Reseller-spezifischen Datenbank zurück
        """
        return f"data/resellers/{reseller_id}/reseller.db"
    
    async def create_reseller_database(self, reseller_id: str) -> str:
        """
        Erstellt eine neue Reseller-spezifische Datenbank
        """
        try:
            # Verzeichnis für Reseller erstellen
            reseller_dir = Path(f"data/resellers/{reseller_id}")
            reseller_dir.mkdir(parents=True, exist_ok=True)
            
            # Weitere Unterverzeichnisse erstellen
            (reseller_dir / "users").mkdir(exist_ok=True)
            (reseller_dir / "projects").mkdir(exist_ok=True)
            (reseller_dir / "viewer").mkdir(exist_ok=True)
            (reseller_dir / "uploads").mkdir(exist_ok=True)
            (reseller_dir / "backups").mkdir(exist_ok=True)
            
            # Datenbank-Pfad
            db_path = self.get_reseller_database_path(reseller_id)
            
            # Engine für Reseller-DB erstellen
            engine = create_engine(
                f"sqlite:///{db_path}",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
            
            # Tabellen erstellen (nur User, Project, etc. - keine Admin/Reseller)
            from .models import User, Project, ProcessingLog, AuditLog, VirusScanResult
            
            # Metadata für Reseller-spezifische Tabellen
            reseller_metadata = MetaData()
            
            # Tabellen zur Metadata hinzufügen
            User.__table__.tometadata(reseller_metadata)
            Project.__table__.tometadata(reseller_metadata)
            ProcessingLog.__table__.tometadata(reseller_metadata)
            AuditLog.__table__.tometadata(reseller_metadata)
            VirusScanResult.__table__.tometadata(reseller_metadata)
            
            # Tabellen erstellen
            reseller_metadata.create_all(bind=engine)
            
            # Engine und Session im Cache speichern
            reseller_engines[reseller_id] = engine
            reseller_sessions[reseller_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            
            logger.info(f"Reseller-Datenbank erstellt", reseller_id=reseller_id, db_path=db_path)
            
            return db_path
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Reseller-Datenbank: {str(e)}", reseller_id=reseller_id)
            raise
    
    def get_reseller_session(self, reseller_id: str) -> sessionmaker:
        """
        Gibt eine Session für die Reseller-spezifische Datenbank zurück
        """
        if reseller_id not in reseller_sessions:
            # Lazy loading der Reseller-Datenbank
            db_path = self.get_reseller_database_path(reseller_id)
            
            if not Path(db_path).exists():
                raise ValueError(f"Reseller-Datenbank nicht gefunden: {reseller_id}")
            
            engine = create_engine(
                f"sqlite:///{db_path}",
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
            
            reseller_engines[reseller_id] = engine
            reseller_sessions[reseller_id] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        return reseller_sessions[reseller_id]
    
    async def backup_reseller_database(self, reseller_id: str, backup_path: str):
        """
        Erstellt ein Backup der Reseller-Datenbank
        """
        try:
            import shutil
            import zipfile
            from datetime import datetime
            
            source_dir = Path(f"data/resellers/{reseller_id}")
            
            if not source_dir.exists():
                raise ValueError(f"Reseller-Verzeichnis nicht gefunden: {reseller_id}")
            
            # Backup-Verzeichnis erstellen
            backup_dir = Path(backup_path).parent
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # ZIP-Backup erstellen
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(source_dir.parent)
                        zipf.write(file_path, arcname)
            
            logger.info(f"Reseller-Backup erstellt", reseller_id=reseller_id, backup_path=backup_path)
            
        except Exception as e:
            logger.error(f"Fehler beim Backup: {str(e)}", reseller_id=reseller_id)
            raise
    
    async def restore_reseller_database(self, reseller_id: str, backup_path: str):
        """
        Stellt eine Reseller-Datenbank aus einem Backup wieder her
        """
        try:
            import zipfile
            import shutil
            
            if not Path(backup_path).exists():
                raise ValueError(f"Backup-Datei nicht gefunden: {backup_path}")
            
            # Zielverzeichnis vorbereiten
            target_dir = Path(f"data/resellers/{reseller_id}")
            
            # Altes Verzeichnis sichern (falls vorhanden)
            if target_dir.exists():
                backup_old = target_dir.with_suffix('.backup_old')
                if backup_old.exists():
                    shutil.rmtree(backup_old)
                shutil.move(str(target_dir), str(backup_old))
            
            # Backup extrahieren
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall("data/resellers")
            
            # Engine-Cache leeren für diesen Reseller
            if reseller_id in reseller_engines:
                reseller_engines[reseller_id].dispose()
                del reseller_engines[reseller_id]
                del reseller_sessions[reseller_id]
            
            logger.info(f"Reseller-Backup wiederhergestellt", reseller_id=reseller_id, backup_path=backup_path)
            
        except Exception as e:
            logger.error(f"Fehler beim Wiederherstellen: {str(e)}", reseller_id=reseller_id)
            raise

# Globale Instanz des Database Managers
db_manager = DatabaseManager()

async def init_database():
    """
    Initialisiert alle Datenbanken
    """
    await db_manager.init_central_database()

def get_database() -> Session:
    """
    Dependency für zentrale Datenbank-Session
    """
    db = CentralSessionLocal()
    try:
        return db
    finally:
        pass  # Session wird vom Caller geschlossen

def get_reseller_database(reseller_id: str) -> Session:
    """
    Dependency für Reseller-spezifische Datenbank-Session
    """
    session_factory = db_manager.get_reseller_session(reseller_id)
    db = session_factory()
    try:
        return db
    finally:
        pass  # Session wird vom Caller geschlossen

def close_database_connections():
    """
    Schließt alle Datenbankverbindungen
    """
    try:
        central_engine.dispose()
        
        for engine in reseller_engines.values():
            engine.dispose()
        
        reseller_engines.clear()
        reseller_sessions.clear()
        
        logger.info("Alle Datenbankverbindungen geschlossen")
        
    except Exception as e:
        logger.error(f"Fehler beim Schließen der Datenbankverbindungen: {str(e)}")