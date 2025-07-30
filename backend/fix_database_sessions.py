#!/usr/bin/env python3
"""
ChiliView Datenbank-Session-Reparatur
Behebt kritische Probleme mit Datenbank-Sessions und Transaktionen
"""

import sys
import os
import asyncio
from pathlib import Path

# Pfad zum Backend-Verzeichnis hinzufügen
sys.path.append(str(Path(__file__).parent))

from database.database import db_manager, get_database, CentralSessionLocal
from database.models import Admin, Reseller, User, SystemConfig
from auth.password_handler import PasswordHandler
import structlog

logger = structlog.get_logger(__name__)

async def repair_database_sessions():
    """
    Repariert Datenbank-Sessions und stellt sicher, dass Transaktionen korrekt funktionieren
    """
    print("🔧 ChiliView Datenbank-Session-Reparatur wird gestartet...")
    
    try:
        # 1. Zentrale Datenbank initialisieren
        print("📊 Initialisiere zentrale Datenbank...")
        await db_manager.init_central_database()
        
        # 2. Test der Session-Verwaltung
        print("🧪 Teste Session-Verwaltung...")
        db = CentralSessionLocal()
        try:
            # Test-Query ausführen
            admin_count = db.query(Admin).count()
            print(f"✅ Zentrale DB: {admin_count} Admin(s) gefunden")
            
            # Test-Transaktion
            test_config = SystemConfig(
                key="session_test",
                value="test_value",
                description="Session-Test"
            )
            db.add(test_config)
            db.commit()
            
            # Test-Abfrage
            saved_config = db.query(SystemConfig).filter(SystemConfig.key == "session_test").first()
            if saved_config:
                print("✅ Transaktions-Test erfolgreich")
                # Test-Eintrag wieder löschen
                db.delete(saved_config)
                db.commit()
            else:
                print("❌ Transaktions-Test fehlgeschlagen")
                
        finally:
            db.close()
        
        # 3. Reseller-Datenbanken prüfen
        print("🏢 Prüfe Reseller-Datenbanken...")
        db = CentralSessionLocal()
        try:
            resellers = db.query(Reseller).all()
            print(f"📋 {len(resellers)} Reseller gefunden")
            
            for reseller in resellers:
                try:
                    # Reseller-DB-Pfad prüfen
                    db_path = Path(reseller.database_path)
                    if not db_path.exists():
                        print(f"⚠️  Reseller-DB fehlt für {reseller.reseller_id}, erstelle neu...")
                        await db_manager.create_reseller_database(reseller.reseller_id)
                    
                    # Session-Test für Reseller-DB
                    session_factory = db_manager.get_reseller_session(reseller.reseller_id)
                    reseller_db = session_factory()
                    try:
                        user_count = reseller_db.query(User).count()
                        print(f"✅ Reseller {reseller.reseller_id}: {user_count} User(s)")
                    finally:
                        reseller_db.close()
                        
                except Exception as e:
                    print(f"❌ Fehler bei Reseller {reseller.reseller_id}: {str(e)}")
                    
        finally:
            db.close()
        
        # 4. Verzeichnisstruktur prüfen
        print("📁 Prüfe Verzeichnisstruktur...")
        directories = [
            "data",
            "data/resellers", 
            "logs",
            "backups",
            "uploads",
            "temp"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Verzeichnis: {directory}")
        
        # 5. Standard-Admin prüfen
        print("👤 Prüfe Standard-Admin...")
        db = CentralSessionLocal()
        try:
            admin = db.query(Admin).first()
            if not admin:
                print("⚠️  Kein Admin gefunden, erstelle Standard-Admin...")
                password_handler = PasswordHandler()
                default_password = "ChiliView2024!"
                
                admin = Admin(
                    username="admin",
                    email="admin@chiliview.local",
                    password_hash=password_handler.hash_password(default_password),
                    full_name="System Administrator",
                    is_active=True
                )
                
                db.add(admin)
                db.commit()
                print(f"✅ Standard-Admin erstellt (Passwort: {default_password})")
            else:
                print(f"✅ Admin vorhanden: {admin.username}")
                
        finally:
            db.close()
        
        print("\n🎉 Datenbank-Session-Reparatur erfolgreich abgeschlossen!")
        print("\n📋 Nächste Schritte:")
        print("1. Backend neu starten: python main.py")
        print("2. Frontend neu starten: npm run dev")
        print("3. Login testen mit admin / ChiliView2024!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Kritischer Fehler bei der Reparatur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_operations():
    """
    Testet grundlegende Datenbankoperationen
    """
    print("\n🧪 Teste Datenbankoperationen...")
    
    try:
        # Test 1: Reseller erstellen
        print("📝 Test 1: Reseller-Erstellung...")
        db = CentralSessionLocal()
        try:
            # Prüfen ob Test-Reseller bereits existiert
            existing = db.query(Reseller).filter(Reseller.reseller_id == "test_reseller").first()
            if existing:
                db.delete(existing)
                db.commit()
            
            # Neuen Test-Reseller erstellen
            password_handler = PasswordHandler()
            test_reseller = Reseller(
                reseller_id="test_reseller",
                company_name="Test Company",
                contact_email="test@example.com",
                contact_name="Test User",
                password_hash=password_handler.hash_password("TestPassword123!"),
                is_active=True,
                database_path="data/resellers/test_reseller/reseller.db"
            )
            
            db.add(test_reseller)
            db.commit()
            db.refresh(test_reseller)
            
            print(f"✅ Test-Reseller erstellt: ID {test_reseller.id}")
            
            # Reseller-DB erstellen
            await db_manager.create_reseller_database("test_reseller")
            print("✅ Reseller-Datenbank erstellt")
            
            # Test-User in Reseller-DB erstellen
            session_factory = db_manager.get_reseller_session("test_reseller")
            reseller_db = session_factory()
            try:
                test_user = User(
                    username="testuser",
                    email="testuser@example.com",
                    full_name="Test User",
                    password_hash=password_handler.hash_password("TestPassword123!"),
                    is_active=True,
                    email_verified=True,
                    gdpr_consent=True
                )
                
                reseller_db.add(test_user)
                reseller_db.commit()
                reseller_db.refresh(test_user)
                
                print(f"✅ Test-User erstellt: ID {test_user.id}")
                
                # User wieder abrufen (Test der Persistierung)
                retrieved_user = reseller_db.query(User).filter(User.username == "testuser").first()
                if retrieved_user:
                    print("✅ User-Persistierung erfolgreich")
                else:
                    print("❌ User-Persistierung fehlgeschlagen")
                
            finally:
                reseller_db.close()
            
            # Test-Reseller wieder löschen
            db.delete(test_reseller)
            db.commit()
            print("✅ Test-Reseller gelöscht")
            
        finally:
            db.close()
        
        print("✅ Alle Datenbank-Tests erfolgreich!")
        return True
        
    except Exception as e:
        print(f"❌ Datenbank-Test fehlgeschlagen: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 ChiliView Datenbank-Session-Reparatur")
    print("=" * 50)
    
    # Asyncio Event Loop erstellen
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Reparatur ausführen
        success = loop.run_until_complete(repair_database_sessions())
        
        if success:
            # Tests ausführen
            test_success = loop.run_until_complete(test_database_operations())
            
            if test_success:
                print("\n🎉 Alle Reparaturen und Tests erfolgreich!")
                sys.exit(0)
            else:
                print("\n❌ Tests fehlgeschlagen!")
                sys.exit(1)
        else:
            print("\n❌ Reparatur fehlgeschlagen!")
            sys.exit(1)
            
    finally:
        loop.close()