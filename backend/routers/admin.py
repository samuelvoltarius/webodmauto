"""
ChiliView Admin Router
API-Endpunkte für Admin-Funktionen: Reseller-/User-Verwaltung, System-Logs, Backups
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog
import os
import zipfile
import io
from pathlib import Path

from auth.auth_handler import require_admin, get_current_user
from database.database import get_database, db_manager, get_reseller_database
from database.models import Admin, Reseller, User, AuditLog, BackupRecord, SystemConfig
from auth.password_handler import password_handler

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic Models
class CreateResellerRequest(BaseModel):
    """Reseller-Erstellung"""
    reseller_id: str
    company_name: str
    contact_email: EmailStr
    contact_name: str
    password: Optional[str] = None  # Falls leer, wird automatisch generiert
    
    # Branding (optional)
    logo_url: Optional[str] = None
    primary_color: Optional[str] = "#007bff"
    secondary_color: Optional[str] = "#6c757d"
    welcome_message: Optional[str] = None
    
    # Konfiguration
    allow_self_registration: Optional[bool] = False
    max_upload_size_mb: Optional[int] = 1024
    max_projects_per_user: Optional[int] = 10

class UpdateResellerRequest(BaseModel):
    """Reseller-Update"""
    company_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    welcome_message: Optional[str] = None
    custom_css: Optional[str] = None
    custom_html: Optional[str] = None
    
    # Rechtliche Angaben
    imprint: Optional[str] = None
    privacy_policy: Optional[str] = None
    homepage_url: Optional[str] = None
    
    # Konfiguration
    allow_self_registration: Optional[bool] = None
    max_upload_size_mb: Optional[int] = None
    max_projects_per_user: Optional[int] = None
    is_active: Optional[bool] = None

class CreateUserRequest(BaseModel):
    """User-Erstellung in Reseller-DB"""
    username: str
    email: EmailStr
    full_name: str
    password: Optional[str] = None
    max_projects: Optional[int] = 10
    max_upload_size_mb: Optional[int] = 1024

class SystemConfigRequest(BaseModel):
    """System-Konfiguration"""
    key: str
    value: str
    description: Optional[str] = None

class BackupRequest(BaseModel):
    """Backup-Anfrage"""
    reseller_id: str
    backup_type: str = "full"

# Reseller-Verwaltung
@router.post("/resellers", status_code=status.HTTP_201_CREATED)
async def create_reseller(
    reseller_data: CreateResellerRequest,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Erstellt einen neuen Reseller mit eigener Datenbank
    
    Nur für Admin-Benutzer verfügbar.
    """
    try:
        db = get_database()
        
        # Prüfen ob Reseller-ID bereits existiert
        existing = db.query(Reseller).filter(Reseller.reseller_id == reseller_data.reseller_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reseller-ID '{reseller_data.reseller_id}' bereits vergeben"
            )
        
        # Passwort generieren falls nicht angegeben
        password = reseller_data.password
        if not password:
            password = password_handler.generate_secure_password(16, True)
        
        # Passwort-Stärke validieren
        validation = password_handler.validate_password_strength(password)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Passwort entspricht nicht den Sicherheitsanforderungen",
                    "errors": validation["errors"]
                }
            )
        
        # Reseller-Datenbank erstellen
        db_path = await db_manager.create_reseller_database(reseller_data.reseller_id)
        
        # Reseller in zentraler DB erstellen
        reseller = Reseller(
            reseller_id=reseller_data.reseller_id,
            company_name=reseller_data.company_name,
            contact_email=reseller_data.contact_email,
            contact_name=reseller_data.contact_name,
            password_hash=password_handler.hash_password(password),
            logo_url=reseller_data.logo_url,
            primary_color=reseller_data.primary_color,
            secondary_color=reseller_data.secondary_color,
            welcome_message=reseller_data.welcome_message,
            allow_self_registration=reseller_data.allow_self_registration,
            max_upload_size_mb=reseller_data.max_upload_size_mb,
            max_projects_per_user=reseller_data.max_projects_per_user,
            database_path=db_path,
            is_active=True
        )
        
        db.add(reseller)
        db.commit()
        db.refresh(reseller)
        
        # Audit-Log erstellen
        from auth.auth_handler import auth_handler
        await auth_handler.log_audit_action(
            db, "create_reseller", admin_id=int(current_user["sub"]),
            resource_type="reseller", resource_id=reseller_data.reseller_id,
            description=f"Reseller '{reseller_data.company_name}' erstellt",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        logger.info("Reseller erstellt", 
                   reseller_id=reseller_data.reseller_id,
                   admin_id=current_user["sub"])
        
        # Antwort (ohne Passwort-Hash)
        response_data = {
            "id": reseller.id,
            "reseller_id": reseller.reseller_id,
            "company_name": reseller.company_name,
            "contact_email": reseller.contact_email,
            "contact_name": reseller.contact_name,
            "is_active": reseller.is_active,
            "created_at": reseller.created_at.isoformat(),
            "database_path": reseller.database_path
        }
        
        # Passwort nur zurückgeben wenn automatisch generiert
        if not reseller_data.password:
            response_data["generated_password"] = password
            response_data["password_info"] = "WICHTIG: Passwort sicher speichern und an Reseller weiterleiten!"
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Resellers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reseller konnte nicht erstellt werden"
        )
    finally:
        db.close()

@router.get("/resellers")
async def list_resellers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: dict = Depends(require_admin)
):
    """
    Listet alle Reseller auf
    """
    try:
        db = get_database()
        
        query = db.query(Reseller)
        
        if active_only:
            query = query.filter(Reseller.is_active == True)
        
        resellers = query.offset(skip).limit(limit).all()
        
        result = []
        for reseller in resellers:
            result.append({
                "id": reseller.id,
                "reseller_id": reseller.reseller_id,
                "company_name": reseller.company_name,
                "contact_email": reseller.contact_email,
                "contact_name": reseller.contact_name,
                "is_active": reseller.is_active,
                "created_at": reseller.created_at.isoformat(),
                "last_login": reseller.last_login.isoformat() if reseller.last_login else None,
                "allow_self_registration": reseller.allow_self_registration,
                "max_upload_size_mb": reseller.max_upload_size_mb,
                "max_projects_per_user": reseller.max_projects_per_user
            })
        
        return {
            "resellers": result,
            "total": len(result),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Reseller: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reseller konnten nicht abgerufen werden"
        )
    finally:
        db.close()

@router.get("/resellers/{reseller_id}")
async def get_reseller(
    reseller_id: str,
    current_user: dict = Depends(require_admin)
):
    """
    Gibt Details zu einem spezifischen Reseller zurück
    """
    try:
        db = get_database()
        
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # User-Anzahl aus Reseller-DB ermitteln
        user_count = 0
        try:
            reseller_db = get_reseller_database(reseller_id)
            user_count = reseller_db.query(User).count()
            reseller_db.close()
        except:
            pass  # Falls Reseller-DB nicht verfügbar
        
        return {
            "id": reseller.id,
            "reseller_id": reseller.reseller_id,
            "company_name": reseller.company_name,
            "contact_email": reseller.contact_email,
            "contact_name": reseller.contact_name,
            "logo_url": reseller.logo_url,
            "primary_color": reseller.primary_color,
            "secondary_color": reseller.secondary_color,
            "welcome_message": reseller.welcome_message,
            "custom_css": reseller.custom_css,
            "custom_html": reseller.custom_html,
            "imprint": reseller.imprint,
            "privacy_policy": reseller.privacy_policy,
            "homepage_url": reseller.homepage_url,
            "allow_self_registration": reseller.allow_self_registration,
            "max_upload_size_mb": reseller.max_upload_size_mb,
            "max_projects_per_user": reseller.max_projects_per_user,
            "is_active": reseller.is_active,
            "created_at": reseller.created_at.isoformat(),
            "updated_at": reseller.updated_at.isoformat() if reseller.updated_at else None,
            "last_login": reseller.last_login.isoformat() if reseller.last_login else None,
            "database_path": reseller.database_path,
            "user_count": user_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Resellers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reseller konnte nicht abgerufen werden"
        )
    finally:
        db.close()

@router.put("/resellers/{reseller_id}")
async def update_reseller(
    reseller_id: str,
    update_data: UpdateResellerRequest,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Aktualisiert einen Reseller
    """
    try:
        db = get_database()
        
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Felder aktualisieren (nur wenn angegeben)
        update_fields = []
        for field, value in update_data.dict(exclude_unset=True).items():
            if hasattr(reseller, field) and value is not None:
                setattr(reseller, field, value)
                update_fields.append(field)
        
        if update_fields:
            reseller.updated_at = datetime.utcnow()
            db.commit()
            
            # Audit-Log erstellen
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                db, "update_reseller", admin_id=int(current_user["sub"]),
                resource_type="reseller", resource_id=reseller_id,
                description=f"Reseller aktualisiert: {', '.join(update_fields)}",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("Reseller aktualisiert", 
                       reseller_id=reseller_id,
                       fields=update_fields,
                       admin_id=current_user["sub"])
        
        return {"message": "Reseller erfolgreich aktualisiert", "updated_fields": update_fields}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Resellers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reseller konnte nicht aktualisiert werden"
        )
    finally:
        db.close()

@router.delete("/resellers/{reseller_id}")
async def delete_reseller(
    reseller_id: str,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Löscht einen Reseller und seine Datenbank
    
    WARNUNG: Diese Aktion ist irreversibel!
    """
    try:
        db = get_database()
        
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Backup vor Löschung erstellen
        backup_path = f"backups/pre_delete_{reseller_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        try:
            await db_manager.backup_reseller_database(reseller_id, backup_path)
            logger.info(f"Backup vor Löschung erstellt: {backup_path}")
        except Exception as e:
            logger.warning(f"Backup vor Löschung fehlgeschlagen: {str(e)}")
        
        # Reseller aus zentraler DB löschen
        db.delete(reseller)
        db.commit()
        
        # Reseller-Verzeichnis löschen
        import shutil
        reseller_dir = Path(f"data/resellers/{reseller_id}")
        if reseller_dir.exists():
            shutil.rmtree(reseller_dir)
        
        # Audit-Log erstellen
        from auth.auth_handler import auth_handler
        await auth_handler.log_audit_action(
            db, "delete_reseller", admin_id=int(current_user["sub"]),
            resource_type="reseller", resource_id=reseller_id,
            description=f"Reseller '{reseller.company_name}' gelöscht",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        logger.info("Reseller gelöscht", 
                   reseller_id=reseller_id,
                   admin_id=current_user["sub"])
        
        return {
            "message": "Reseller erfolgreich gelöscht",
            "backup_created": backup_path if 'backup_path' in locals() else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Resellers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reseller konnte nicht gelöscht werden"
        )
    finally:
        db.close()

# User-Verwaltung (in Reseller-DBs)
@router.post("/resellers/{reseller_id}/users", status_code=status.HTTP_201_CREATED)
async def create_user_for_reseller(
    reseller_id: str,
    user_data: CreateUserRequest,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Erstellt einen neuen User in der Reseller-Datenbank
    """
    try:
        # Reseller existiert prüfen
        db = get_database()
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Reseller-DB Session
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # Prüfen ob Username/Email bereits existiert
            existing_user = reseller_db.query(User).filter(
                (User.username == user_data.username) | (User.email == user_data.email)
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username oder E-Mail bereits vergeben"
                )
            
            # Passwort generieren falls nicht angegeben
            password = user_data.password
            if not password:
                password = password_handler.generate_secure_password(12, True)
            
            # User erstellen
            user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                password_hash=password_handler.hash_password(password),
                max_projects=user_data.max_projects,
                max_upload_size_mb=user_data.max_upload_size_mb,
                gdpr_consent=True,  # Admin-erstellte User haben automatisch Consent
                gdpr_consent_date=datetime.utcnow(),
                is_active=True,
                email_verified=True  # Admin-erstellte User sind automatisch verifiziert
            )
            
            reseller_db.add(user)
            reseller_db.commit()
            reseller_db.refresh(user)
            
            # Audit-Log in zentraler DB
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                db, "create_user", admin_id=int(current_user["sub"]),
                resource_type="user", resource_id=str(user.id),
                description=f"User '{user_data.username}' für Reseller '{reseller_id}' erstellt",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("User erstellt", 
                       user_id=user.id,
                       username=user_data.username,
                       reseller_id=reseller_id,
                       admin_id=current_user["sub"])
            
            response_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "max_projects": user.max_projects,
                "max_upload_size_mb": user.max_upload_size_mb,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "reseller_id": reseller_id
            }
            
            # Passwort nur zurückgeben wenn automatisch generiert
            if not user_data.password:
                response_data["generated_password"] = password
                response_data["password_info"] = "WICHTIG: Passwort sicher speichern und an User weiterleiten!"
            
            return response_data
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User konnte nicht erstellt werden"
        )
    finally:
        db.close()

@router.get("/resellers/{reseller_id}/users")
async def list_users_for_reseller(
    reseller_id: str,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    current_user: dict = Depends(require_admin)
):
    """
    Listet alle User eines Resellers auf
    """
    try:
        # Reseller existiert prüfen
        db = get_database()
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Reseller-DB Session
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            query = reseller_db.query(User)
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            users = query.offset(skip).limit(limit).all()
            
            result = []
            for user in users:
                # Projekt-Anzahl ermitteln
                project_count = len(user.projects) if user.projects else 0
                
                result.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "max_projects": user.max_projects,
                    "max_upload_size_mb": user.max_upload_size_mb,
                    "is_active": user.is_active,
                    "email_verified": user.email_verified,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "project_count": project_count,
                    "gdpr_consent": user.gdpr_consent,
                    "gdpr_consent_date": user.gdpr_consent_date.isoformat() if user.gdpr_consent_date else None
                })
            
            return {
                "users": result,
                "total": len(result),
                "skip": skip,
                "limit": limit,
                "reseller_id": reseller_id
            }
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der User: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User konnten nicht abgerufen werden"
        )
    finally:
        db.close()

# System-Logs und Audit
@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    user_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """
    Ruft System-Audit-Logs ab
    """
    try:
        db = get_database()
        
        query = db.query(AuditLog)
        
        # Filter anwenden
        if action:
            query = query.filter(AuditLog.action == action)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query = query.filter(AuditLog.timestamp <= end_dt)
        
        # Nach Zeitstempel sortieren (neueste zuerst)
        query = query.order_by(AuditLog.timestamp.desc())
        
        logs = query.offset(skip).limit(limit).all()
        
        result = []
        for log in logs:
            result.append({
                "id": log.id,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "description": log.description,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "admin_id": log.admin_id,
                "reseller_id": log.reseller_id,
                "user_id": log.user_id,
                "original_admin_id": log.original_admin_id,
                "impersonated_user_type": log.impersonated_user_type,
                "impersonated_user_id": log.impersonated_user_id,
                "timestamp": log.timestamp.isoformat()
            })
        
        return {
            "logs": result,
            "total": len(result),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Audit-Logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audit-Logs konnten nicht abgerufen werden"
        )
    finally:
        db.close()

# Backup und Restore
@router.post("/backups")
async def create_backup(
    backup_data: BackupRequest,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Erstellt ein Backup einer Reseller-Datenbank
    """
    try:
        db = get_database()
        
        # Reseller existiert prüfen
        reseller = db.query(Reseller).filter(Reseller.reseller_id == backup_data.reseller_id).first()
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Backup-Pfad generieren
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{backup_data.reseller_id}_{backup_data.backup_type}_{timestamp}.zip"
        backup_path = f"backups/{backup_filename}"
        
        # Backup erstellen
        await db_manager.backup_reseller_database(backup_data.reseller_id, backup_path)
        
        # Backup-Record erstellen
        backup_record = BackupRecord(
            reseller_id=reseller.id,
            backup_type=backup_data.backup_type,
            backup_path=backup_path,
            file_size_bytes=os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
            status="created",
            created_by_admin_id=int(current_user["sub"])
        )
        
        db.add(backup_record)
        db.commit()
        
        # Audit-Log erstellen
        from auth.auth_handler import auth_handler
        await auth_handler.log_audit_action(
            db, "create_backup", admin_id=int(current_user["sub"]),
            resource_type="backup", resource_id=str(backup_record.id),
            description=f"Backup für Reseller '{backup_data.reseller_id}' erstellt",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        logger.info("Backup erstellt", 
                   reseller_id=backup_data.reseller_id,
                   backup_path=backup_path,
                   admin_id=current_user["sub"])
        
        return {
            "message": "Backup erfolgreich erstellt",
            "backup_id": backup_record.id,
            "backup_path": backup_path,
            "file_size_bytes": backup_record.file_size_bytes,
            "created_at": backup_record.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Backups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup konnte nicht erstellt werden"
        )
    finally:
        db.close()

@router.get("/backups")
async def list_backups(
    reseller_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_admin)
):
    """
    Listet alle Backups auf
    """
    try:
        db = get_database()
        
        query = db.query(BackupRecord)
        
        if reseller_id:
            reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
            if reseller:
                query = query.filter(BackupRecord.reseller_id == reseller.id)
        
        query = query.order_by(BackupRecord.created_at.desc())
        backups = query.offset(skip).limit(limit).all()
        
        result = []
        for backup in backups:
            # Reseller-Info laden
            reseller = db.query(Reseller).filter(Reseller.id == backup.reseller_id).first()
            
            result.append({
                "id": backup.id,
                "reseller_id": reseller.reseller_id if reseller else "unknown",
                "reseller_name": reseller.company_name if reseller else "Unknown",
                "backup_type": backup.backup_type,
                "backup_path": backup.backup_path,
                "file_size_bytes": backup.file_size_bytes,
                "status": backup.status,
                "created_at": backup.created_at.isoformat(),
                "restored_at": backup.restored_at.isoformat() if backup.restored_at else None,
                "created_by_admin_id": backup.created_by_admin_id
            })
        
        return {
            "backups": result,
            "total": len(result),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Backups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backups konnten nicht abgerufen werden"
        )
    finally:
        db.close()

@router.get("/backups/{backup_id}/download")
async def download_backup(
    backup_id: int,
    current_user: dict = Depends(require_admin)
):
    """
    Lädt ein Backup herunter
    """
    try:
        db = get_database()
        
        backup = db.query(BackupRecord).filter(BackupRecord.id == backup_id).first()
        if not backup:
            raise HTTPException(status_code=404, detail="Backup nicht gefunden")
        
        backup_path = Path(backup.backup_path)
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup-Datei nicht gefunden")
        
        logger.info("Backup-Download",
                   backup_id=backup_id,
                   admin_id=current_user["sub"])
        
        return FileResponse(
            path=str(backup_path),
            filename=backup_path.name,
            media_type='application/zip'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Backup-Download: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup konnte nicht heruntergeladen werden"
        )
    finally:
        db.close()

@router.post("/backups/{backup_id}/restore")
async def restore_backup(
    backup_id: int,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Stellt ein Backup wieder her
    
    WARNUNG: Überschreibt die aktuelle Reseller-Datenbank!
    """
    try:
        db = get_database()
        
        backup = db.query(BackupRecord).filter(BackupRecord.id == backup_id).first()
        if not backup:
            raise HTTPException(status_code=404, detail="Backup nicht gefunden")
        
        # Reseller-Info laden
        reseller = db.query(Reseller).filter(Reseller.id == backup.reseller_id).first()
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller für Backup nicht gefunden")
        
        # Backup wiederherstellen
        await db_manager.restore_reseller_database(reseller.reseller_id, backup.backup_path)
        
        # Backup-Status aktualisieren
        backup.status = "restored"
        backup.restored_at = datetime.utcnow()
        db.commit()
        
        # Audit-Log erstellen
        from auth.auth_handler import auth_handler
        await auth_handler.log_audit_action(
            db, "restore_backup", admin_id=int(current_user["sub"]),
            resource_type="backup", resource_id=str(backup_id),
            description=f"Backup {backup_id} für Reseller '{reseller.reseller_id}' wiederhergestellt",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        logger.info("Backup wiederhergestellt",
                   backup_id=backup_id,
                   reseller_id=reseller.reseller_id,
                   admin_id=current_user["sub"])
        
        return {
            "message": "Backup erfolgreich wiederhergestellt",
            "backup_id": backup_id,
            "reseller_id": reseller.reseller_id,
            "restored_at": backup.restored_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Wiederherstellen des Backups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup konnte nicht wiederhergestellt werden"
        )
    finally:
        db.close()

# System-Konfiguration
@router.get("/system-config")
async def get_system_config(
    current_user: dict = Depends(require_admin)
):
    """
    Ruft die System-Konfiguration ab
    """
    try:
        db = get_database()
        
        configs = db.query(SystemConfig).all()
        
        result = {}
        for config in configs:
            result[config.key] = {
                "value": config.value,
                "description": config.description,
                "is_encrypted": config.is_encrypted,
                "updated_at": config.updated_at.isoformat() if config.updated_at else None
            }
        
        return {"config": result}
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der System-Konfiguration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System-Konfiguration konnte nicht abgerufen werden"
        )
    finally:
        db.close()

@router.put("/system-config")
async def update_system_config(
    config_data: SystemConfigRequest,
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Aktualisiert eine System-Konfiguration
    """
    try:
        db = get_database()
        
        config = db.query(SystemConfig).filter(SystemConfig.key == config_data.key).first()
        
        if config:
            # Bestehende Konfiguration aktualisieren
            config.value = config_data.value
            if config_data.description:
                config.description = config_data.description
            config.updated_at = datetime.utcnow()
        else:
            # Neue Konfiguration erstellen
            config = SystemConfig(
                key=config_data.key,
                value=config_data.value,
                description=config_data.description
            )
            db.add(config)
        
        db.commit()
        
        # Audit-Log erstellen
        from auth.auth_handler import auth_handler
        await auth_handler.log_audit_action(
            db, "update_system_config", admin_id=int(current_user["sub"]),
            resource_type="system_config", resource_id=config_data.key,
            description=f"System-Konfiguration '{config_data.key}' aktualisiert",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        logger.info("System-Konfiguration aktualisiert",
                   key=config_data.key,
                   admin_id=current_user["sub"])
        
        return {
            "message": "System-Konfiguration erfolgreich aktualisiert",
            "key": config_data.key,
            "value": config_data.value
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der System-Konfiguration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System-Konfiguration konnte nicht aktualisiert werden"
        )
    finally:
        db.close()

@router.get("/statistics")
async def get_system_statistics(
    current_user: dict = Depends(require_admin)
):
    """
    Ruft System-Statistiken ab
    """
    try:
        db = get_database()
        
        # Reseller-Statistiken
        total_resellers = db.query(Reseller).count()
        active_resellers = db.query(Reseller).filter(Reseller.is_active == True).count()
        
        # User-Statistiken (über alle Reseller)
        total_users = 0
        active_users = 0
        total_projects = 0
        
        resellers = db.query(Reseller).filter(Reseller.is_active == True).all()
        for reseller in resellers:
            try:
                reseller_db = get_reseller_database(reseller.reseller_id)
                reseller_users = reseller_db.query(User).count()
                reseller_active_users = reseller_db.query(User).filter(User.is_active == True).count()
                
                from database.models import Project
                reseller_projects = reseller_db.query(Project).count()
                
                total_users += reseller_users
                active_users += reseller_active_users
                total_projects += reseller_projects
                
                reseller_db.close()
            except:
                continue  # Reseller-DB nicht verfügbar
        
        # Backup-Statistiken
        total_backups = db.query(BackupRecord).count()
        recent_backups = db.query(BackupRecord).filter(
            BackupRecord.created_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Audit-Log-Statistiken
        total_audit_logs = db.query(AuditLog).count()
        recent_logins = db.query(AuditLog).filter(
            AuditLog.action == "login",
            AuditLog.timestamp >= datetime.utcnow() - timedelta(days=1)
        ).count()
        
        return {
            "resellers": {
                "total": total_resellers,
                "active": active_resellers,
                "inactive": total_resellers - active_resellers
            },
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "projects": {
                "total": total_projects
            },
            "backups": {
                "total": total_backups,
                "recent_7_days": recent_backups
            },
            "activity": {
                "total_audit_logs": total_audit_logs,
                "recent_logins_24h": recent_logins
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Statistiken: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Statistiken konnten nicht abgerufen werden"
        )
    finally:
        db.close()

@router.get("/health")
async def admin_health_check():
    """
    Gesundheitscheck für den Admin-Service
    """
    return {
        "status": "healthy",
        "service": "admin",
        "version": "1.0.0"
    }
            