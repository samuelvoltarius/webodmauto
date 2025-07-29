"""
ChiliView Reseller Router
API-Endpunkte für Reseller-Funktionen: User-Verwaltung, Branding, Konfiguration
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
import os
from pathlib import Path
import shutil

from auth.auth_handler import require_reseller, get_current_user
from database.database import get_database, get_reseller_database
from database.models import Reseller, User, Project, AuditLog
from auth.password_handler import password_handler

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic Models
class CreateUserRequest(BaseModel):
    """User-Erstellung durch Reseller"""
    username: str
    email: EmailStr
    full_name: str
    password: Optional[str] = None
    max_projects: Optional[int] = None
    max_upload_size_mb: Optional[int] = None

class UpdateUserRequest(BaseModel):
    """User-Update durch Reseller"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    max_projects: Optional[int] = None
    max_upload_size_mb: Optional[int] = None
    is_active: Optional[bool] = None

class UpdateBrandingRequest(BaseModel):
    """Branding-Update"""
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    welcome_message: Optional[str] = None
    custom_css: Optional[str] = None
    custom_html: Optional[str] = None
    imprint: Optional[str] = None
    privacy_policy: Optional[str] = None
    homepage_url: Optional[str] = None

class UpdateConfigRequest(BaseModel):
    """Konfiguration-Update"""
    allow_self_registration: Optional[bool] = None
    max_upload_size_mb: Optional[int] = None
    max_projects_per_user: Optional[int] = None

class SelfRegistrationRequest(BaseModel):
    """Selbstregistrierung für User"""
    username: str
    email: EmailStr
    full_name: str
    password: str
    gdpr_consent: bool

# Reseller-Dashboard
@router.get("/dashboard")
async def get_reseller_dashboard(
    current_user: dict = Depends(require_reseller)
):
    """
    Reseller-Dashboard mit Übersicht und Statistiken
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
        # Zentrale DB für Reseller-Info
        db = get_database()
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Reseller-DB für Statistiken
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # User-Statistiken
            total_users = reseller_db.query(User).count()
            active_users = reseller_db.query(User).filter(User.is_active == True).count()
            
            # Projekt-Statistiken
            total_projects = reseller_db.query(Project).count()
            active_projects = reseller_db.query(Project).filter(
                Project.status.in_(["uploaded", "processing"])
            ).count()
            completed_projects = reseller_db.query(Project).filter(
                Project.status == "completed"
            ).count()
            failed_projects = reseller_db.query(Project).filter(
                Project.status == "failed"
            ).count()
            
            # Neueste User (letzte 7 Tage)
            from datetime import timedelta
            recent_users = reseller_db.query(User).filter(
                User.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            # Neueste Projekte
            recent_projects = reseller_db.query(Project).order_by(
                Project.created_at.desc()
            ).limit(5).all()
            
            recent_projects_data = []
            for project in recent_projects:
                user = reseller_db.query(User).filter(User.id == project.user_id).first()
                recent_projects_data.append({
                    "id": project.id,
                    "name": project.name,
                    "status": project.status,
                    "user_name": user.username if user else "Unknown",
                    "created_at": project.created_at.isoformat(),
                    "progress_percentage": project.progress_percentage
                })
            
            return {
                "reseller": {
                    "id": reseller.id,
                    "reseller_id": reseller.reseller_id,
                    "company_name": reseller.company_name,
                    "contact_email": reseller.contact_email,
                    "is_active": reseller.is_active,
                    "allow_self_registration": reseller.allow_self_registration,
                    "max_upload_size_mb": reseller.max_upload_size_mb,
                    "max_projects_per_user": reseller.max_projects_per_user
                },
                "statistics": {
                    "users": {
                        "total": total_users,
                        "active": active_users,
                        "inactive": total_users - active_users,
                        "recent_7_days": recent_users
                    },
                    "projects": {
                        "total": total_projects,
                        "active": active_projects,
                        "completed": completed_projects,
                        "failed": failed_projects
                    }
                },
                "recent_projects": recent_projects_data,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Reseller-Dashboards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard konnte nicht geladen werden"
        )
    finally:
        db.close()

# User-Verwaltung
@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUserRequest,
    request: Request,
    current_user: dict = Depends(require_reseller)
):
    """
    Erstellt einen neuen User in der Reseller-Datenbank
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
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
            
            # Reseller-Limits aus zentraler DB holen
            db = get_database()
            reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
            
            # Passwort generieren falls nicht angegeben
            password = user_data.password
            if not password:
                password = password_handler.generate_secure_password(12, True)
            
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
            
            # User erstellen
            user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                password_hash=password_handler.hash_password(password),
                max_projects=user_data.max_projects or reseller.max_projects_per_user,
                max_upload_size_mb=user_data.max_upload_size_mb or reseller.max_upload_size_mb,
                gdpr_consent=True,  # Reseller-erstellte User haben automatisch Consent
                gdpr_consent_date=datetime.utcnow(),
                is_active=True,
                email_verified=True  # Reseller-erstellte User sind automatisch verifiziert
            )
            
            reseller_db.add(user)
            reseller_db.commit()
            reseller_db.refresh(user)
            
            # Audit-Log in Reseller-DB
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                reseller_db, "create_user", reseller_id=reseller.id,
                resource_type="user", resource_id=str(user.id),
                description=f"User '{user_data.username}' erstellt",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("User erstellt durch Reseller", 
                       user_id=user.id,
                       username=user_data.username,
                       reseller_id=reseller_id)
            
            response_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "max_projects": user.max_projects,
                "max_upload_size_mb": user.max_upload_size_mb,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
            
            # Passwort nur zurückgeben wenn automatisch generiert
            if not user_data.password:
                response_data["generated_password"] = password
                response_data["password_info"] = "WICHTIG: Passwort sicher speichern und an User weiterleiten!"
            
            return response_data
            
        finally:
            reseller_db.close()
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User konnte nicht erstellt werden"
        )

@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    search: Optional[str] = None,
    current_user: dict = Depends(require_reseller)
):
    """
    Listet alle User des Resellers auf
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            query = reseller_db.query(User)
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    (User.username.like(search_filter)) |
                    (User.email.like(search_filter)) |
                    (User.full_name.like(search_filter))
                )
            
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
                "limit": limit
            }
            
        finally:
            reseller_db.close()
            
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der User: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User konnten nicht abgerufen werden"
        )

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    current_user: dict = Depends(require_reseller)
):
    """
    Gibt Details zu einem spezifischen User zurück
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            user = reseller_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            # Projekt-Details laden
            projects = []
            for project in user.projects:
                projects.append({
                    "id": project.id,
                    "name": project.name,
                    "status": project.status,
                    "progress_percentage": project.progress_percentage,
                    "created_at": project.created_at.isoformat(),
                    "file_count": project.file_count,
                    "file_size_bytes": project.file_size_bytes
                })
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "max_projects": user.max_projects,
                "max_upload_size_mb": user.max_upload_size_mb,
                "is_active": user.is_active,
                "email_verified": user.email_verified,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "gdpr_consent": user.gdpr_consent,
                "gdpr_consent_date": user.gdpr_consent_date.isoformat() if user.gdpr_consent_date else None,
                "data_retention_until": user.data_retention_until.isoformat() if user.data_retention_until else None,
                "projects": projects
            }
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User konnte nicht abgerufen werden"
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    update_data: UpdateUserRequest,
    request: Request,
    current_user: dict = Depends(require_reseller)
):
    """
    Aktualisiert einen User
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            user = reseller_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            # Felder aktualisieren (nur wenn angegeben)
            update_fields = []
            for field, value in update_data.dict(exclude_unset=True).items():
                if hasattr(user, field) and value is not None:
                    # Spezielle Validierung für Username/Email
                    if field in ["username", "email"]:
                        existing = reseller_db.query(User).filter(
                            getattr(User, field) == value,
                            User.id != user_id
                        ).first()
                        if existing:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"{field.capitalize()} bereits vergeben"
                            )
                    
                    setattr(user, field, value)
                    update_fields.append(field)
            
            if update_fields:
                user.updated_at = datetime.utcnow()
                reseller_db.commit()
                
                # Audit-Log erstellen
                from auth.auth_handler import auth_handler
                await auth_handler.log_audit_action(
                    reseller_db, "update_user", user_id=user.id,
                    resource_type="user", resource_id=str(user_id),
                    description=f"User aktualisiert: {', '.join(update_fields)}",
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent", "unknown")
                )
                
                logger.info("User aktualisiert", 
                           user_id=user_id,
                           fields=update_fields,
                           reseller_id=reseller_id)
            
            return {"message": "User erfolgreich aktualisiert", "updated_fields": update_fields}
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User konnte nicht aktualisiert werden"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_user: dict = Depends(require_reseller)
):
    """
    Löscht einen User und alle seine Projekte
    
    WARNUNG: Diese Aktion ist irreversibel!
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            user = reseller_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            username = user.username
            
            # User-Projekte und Dateien löschen
            for project in user.projects:
                # Projektdateien löschen
                if project.upload_path and os.path.exists(project.upload_path):
                    shutil.rmtree(project.upload_path, ignore_errors=True)
                
                if project.viewer_path and os.path.exists(project.viewer_path):
                    shutil.rmtree(project.viewer_path, ignore_errors=True)
            
            # User aus DB löschen (Cascade löscht auch Projekte)
            reseller_db.delete(user)
            reseller_db.commit()
            
            # Audit-Log erstellen
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                reseller_db, "delete_user", 
                resource_type="user", resource_id=str(user_id),
                description=f"User '{username}' gelöscht",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("User gelöscht", 
                       user_id=user_id,
                       username=username,
                       reseller_id=reseller_id)
            
            return {"message": "User erfolgreich gelöscht"}
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User konnte nicht gelöscht werden"
        )

# Branding-Verwaltung
@router.get("/branding")
async def get_branding(
    current_user: dict = Depends(require_reseller)
):
    """
    Ruft die aktuellen Branding-Einstellungen ab
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
        db = get_database()
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        return {
            "logo_url": reseller.logo_url,
            "primary_color": reseller.primary_color,
            "secondary_color": reseller.secondary_color,
            "welcome_message": reseller.welcome_message,
            "custom_css": reseller.custom_css,
            "custom_html": reseller.custom_html,
            "imprint": reseller.imprint,
            "privacy_policy": reseller.privacy_policy,
            "homepage_url": reseller.homepage_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Brandings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Branding konnte nicht abgerufen werden"
        )
    finally:
        db.close()

@router.put("/branding")
async def update_branding(
    branding_data: UpdateBrandingRequest,
    request: Request,
    current_user: dict = Depends(require_reseller)
):
    """
    Aktualisiert die Branding-Einstellungen
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
        db = get_database()
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Felder aktualisieren (nur wenn angegeben)
        update_fields = []
        for field, value in branding_data.dict(exclude_unset=True).items():
            if hasattr(reseller, field) and value is not None:
                setattr(reseller, field, value)
                update_fields.append(field)
        
        if update_fields:
            reseller.updated_at = datetime.utcnow()
            db.commit()
            
            # Audit-Log erstellen
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                db, "update_branding", reseller_id=reseller.id,
                resource_type="branding", resource_id=reseller_id,
                description=f"Branding aktualisiert: {', '.join(update_fields)}",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("Branding aktualisiert", 
                       reseller_id=reseller_id,
                       fields=update_fields)
        
        return {"message": "Branding erfolgreich aktualisiert", "updated_fields": update_fields}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Brandings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Branding konnte nicht aktualisiert werden"
        )
    finally:
        db.close()

# Konfiguration
@router.get("/config")
async def get_config(
    current_user: dict = Depends(require_reseller)
):
    """
    Ruft die Reseller-Konfiguration ab
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
        db = get_database()
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        return {
            "allow_self_registration": reseller.allow_self_registration,
            "max_upload_size_mb": reseller.max_upload_size_mb,
            "max_projects_per_user": reseller.max_projects_per_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Konfiguration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konfiguration konnte nicht abgerufen werden"
        )
    finally:
        db.close()

@router.put("/config")
async def update_config(
    config_data: UpdateConfigRequest,
    request: Request,
    current_user: dict = Depends(require_reseller)
):
    """
    Aktualisiert die Reseller-Konfiguration
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
        db = get_database()
        reseller = db.query(Reseller).filter(Reseller.reseller_id == reseller_id).first()
        
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        # Felder aktualisieren (nur wenn angegeben)
        update_fields = []
        for field, value in config_data.dict(exclude_unset=True).items():
            if hasattr(reseller, field) and value is not None:
                setattr(reseller, field, value)
                update_fields.append(field)
        
        if update_fields:
            reseller.updated_at = datetime.utcnow()
            db.commit()
            
            # Audit-Log erstellen
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                db, "update_config", reseller_id=reseller.id,
                resource_type="config", resource_id=reseller_id,
                description=f"Konfiguration aktualisiert: {', '.join(update_fields)}",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("Konfiguration aktualisiert", 
                       reseller_id=reseller_id,
                       fields=update_fields)
        
        return {"message": "Konfiguration erfolgreich aktualisiert", "updated_fields": update_fields}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Konfiguration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Konfiguration konnte nicht aktualisiert werden"
        )
    finally:
        db.close()

# Selbstregistrierung
@router.post("/self-register", status_code=status.HTTP_201_CREATED)
async def self_register(
    registration_data: SelfRegistrationRequest,
    request: Request,
    reseller_id: str
):
    """
    Selbstregistrierung für User (ohne Authentifizierung)
    """
    try:
        # Reseller und Selbstregistrierung prüfen
        db = get_database()
        reseller = db.query(Reseller).filter(
            Reseller.reseller_id == reseller_id,
            Reseller.is_active == True,
            Reseller.allow_self_registration == True
        ).first()
        
        if not reseller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Selbstregistrierung für diesen Reseller nicht verfügbar"
            )
        
        # DSGVO-Consent prüfen
        if not registration_data.gdpr_consent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DSGVO-Einwilligung ist erforderlich"
            )
        
        # Reseller-DB Session
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # Prüfen ob Username/Email bereits existiert
            existing_user = reseller_db.query(User).filter(
                (User.username == registration_data.username) |
                (User.email == registration_data.email)
            ).first()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username oder E-Mail bereits vergeben"
                )
            
            # Passwort-Stärke validieren
            validation = password_handler.validate_password_strength(registration_data.password)
            if not validation["is_valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "message": "Passwort entspricht nicht den Sicherheitsanforderungen",
                        "errors": validation["errors"],
                        "suggestions": validation["suggestions"]
                    }
                )
            
            # User erstellen
            user = User(
                username=registration_data.username,
                email=registration_data.email,
                full_name=registration_data.full_name,
                password_hash=password_handler.hash_password(registration_data.password),
                max_projects=reseller.max_projects_per_user,
                max_upload_size_mb=reseller.max_upload_size_mb,
                gdpr_consent=True,
                gdpr_consent_date=datetime.utcnow(),
                is_active=True,
                email_verified=False  # Selbstregistrierte User müssen E-Mail verifizieren
            )
            
            reseller_db.add(user)
            reseller_db.commit()
            reseller_db.refresh(user)
            
            # Audit-Log in Reseller-DB
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                reseller_db, "self_register", user_id=user.id,
                resource_type="user", resource_id=str(user.id),
                description=f"Selbstregistrierung: User '{registration_data.username}'",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("Selbstregistrierung erfolgreich",
                       user_id=user.id,
                       username=registration_data.username,
                       reseller_id=reseller_id)
            
            return {
                "message": "Registrierung erfolgreich",
                "user_id": user.id,
                "username": user.username,
                "email_verification_required": True,
                "created_at": user.created_at.isoformat()
            }
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Selbstregistrierung: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registrierung konnte nicht abgeschlossen werden"
        )
    finally:
        db.close()

# Backup und Export
@router.post("/backup")
async def create_reseller_backup(
    request: Request,
    current_user: dict = Depends(require_reseller)
):
    """
    Erstellt ein Backup der eigenen Reseller-Datenbank
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
        # Backup-Pfad generieren
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"{reseller_id}_self_backup_{timestamp}.zip"
        backup_path = f"data/resellers/{reseller_id}/backups/{backup_filename}"
        
        # Verzeichnis erstellen
        Path(f"data/resellers/{reseller_id}/backups").mkdir(parents=True, exist_ok=True)
        
        # Backup erstellen
        from database.database import db_manager
        await db_manager.backup_reseller_database(reseller_id, backup_path)
        
        # Audit-Log in Reseller-DB
        reseller_db = get_reseller_database(reseller_id)
        try:
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                reseller_db, "create_backup",
                resource_type="backup", resource_id=backup_filename,
                description=f"Reseller-Backup erstellt",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
        finally:
            reseller_db.close()
        
        logger.info("Reseller-Backup erstellt",
                   reseller_id=reseller_id,
                   backup_path=backup_path)
        
        return {
            "message": "Backup erfolgreich erstellt",
            "backup_filename": backup_filename,
            "backup_path": backup_path,
            "file_size_bytes": os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
            "created_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Reseller-Backups: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Backup konnte nicht erstellt werden"
        )

@router.get("/backup/download/{backup_filename}")
async def download_reseller_backup(
    backup_filename: str,
    current_user: dict = Depends(require_reseller)
):
    """
    Lädt ein eigenes Backup herunter
    """
    try:
        reseller_id = current_user.get("reseller_id") or current_user.get("sub")
        
        # Sicherheitsprüfung: Nur eigene Backups
        if not backup_filename.startswith(f"{reseller_id}_"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff auf fremde Backups nicht erlaubt"
            )
        
        backup_path = Path(f"data/resellers/{reseller_id}/backups/{backup_filename}")
        
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail="Backup-Datei nicht gefunden")
        
        logger.info("Reseller-Backup-Download",
                   reseller_id=reseller_id,
                   backup_filename=backup_filename)
        
        return FileResponse(
            path=str(backup_path),
            filename=backup_filename,
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

@router.get("/health")
async def reseller_health_check():
    """
    Gesundheitscheck für den Reseller-Service
    """
    return {
        "status": "healthy",
        "service": "reseller",
        "version": "1.0.0"
    }