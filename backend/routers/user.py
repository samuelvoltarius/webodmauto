"""
ChiliView User Router
API-Endpunkte für End-User-Funktionen: Projekt-Verwaltung, Upload, Viewer
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog

from auth.auth_handler import require_user, get_current_user
from database.database import get_reseller_database
from database.models import User, Project, ProcessingLog

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic Models
class ProjectResponse(BaseModel):
    """Projekt-Antwort"""
    id: int
    project_uuid: str
    name: str
    description: Optional[str]
    status: str
    progress_percentage: float
    file_count: int
    file_size_bytes: Optional[int]
    viewer_url: Optional[str]
    created_at: str
    processing_started_at: Optional[str]
    processing_completed_at: Optional[str]
    error_message: Optional[str]

class UpdateProjectRequest(BaseModel):
    """Projekt-Update"""
    name: Optional[str] = None
    description: Optional[str] = None

class UserProfileResponse(BaseModel):
    """User-Profil-Antwort"""
    id: int
    username: str
    email: str
    full_name: str
    max_projects: int
    max_upload_size_mb: int
    is_active: bool
    email_verified: bool
    created_at: str
    last_login: Optional[str]
    project_count: int
    gdpr_consent: bool
    gdpr_consent_date: Optional[str]

# User-Dashboard
@router.get("/dashboard")
async def get_user_dashboard(
    current_user: dict = Depends(require_user)
):
    """
    User-Dashboard mit Projekt-Übersicht und Statistiken
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # User-Daten laden
            user = reseller_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            # Projekt-Statistiken
            total_projects = reseller_db.query(Project).filter(Project.user_id == user_id).count()
            
            projects_by_status = reseller_db.query(Project.status, reseller_db.func.count(Project.id)).filter(
                Project.user_id == user_id
            ).group_by(Project.status).all()
            
            status_counts = {status: count for status, count in projects_by_status}
            
            # Neueste Projekte
            recent_projects = reseller_db.query(Project).filter(
                Project.user_id == user_id
            ).order_by(Project.created_at.desc()).limit(5).all()
            
            recent_projects_data = []
            for project in recent_projects:
                recent_projects_data.append({
                    "id": project.id,
                    "project_uuid": project.project_uuid,
                    "name": project.name,
                    "status": project.status,
                    "progress_percentage": project.progress_percentage,
                    "created_at": project.created_at.isoformat(),
                    "file_count": project.file_count,
                    "viewer_url": project.viewer_url
                })
            
            # Speicherverbrauch berechnen
            total_storage_bytes = reseller_db.query(
                reseller_db.func.sum(Project.file_size_bytes)
            ).filter(Project.user_id == user_id).scalar() or 0
            
            return {
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "max_projects": user.max_projects,
                    "max_upload_size_mb": user.max_upload_size_mb,
                    "email_verified": user.email_verified
                },
                "statistics": {
                    "total_projects": total_projects,
                    "projects_by_status": {
                        "uploaded": status_counts.get("uploaded", 0),
                        "processing": status_counts.get("processing", 0),
                        "completed": status_counts.get("completed", 0),
                        "failed": status_counts.get("failed", 0)
                    },
                    "total_storage_bytes": total_storage_bytes,
                    "storage_limit_bytes": user.max_upload_size_mb * 1024 * 1024,
                    "projects_remaining": max(0, user.max_projects - total_projects)
                },
                "recent_projects": recent_projects_data,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des User-Dashboards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard konnte nicht geladen werden"
        )

# Projekt-Verwaltung
@router.get("/projects", response_model=List[ProjectResponse])
async def list_user_projects(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(require_user)
):
    """
    Listet alle Projekte des Users auf
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            query = reseller_db.query(Project).filter(Project.user_id == user_id)
            
            if status_filter:
                query = query.filter(Project.status == status_filter)
            
            projects = query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
            
            result = []
            for project in projects:
                result.append(ProjectResponse(
                    id=project.id,
                    project_uuid=project.project_uuid,
                    name=project.name,
                    description=project.description,
                    status=project.status,
                    progress_percentage=project.progress_percentage,
                    file_count=project.file_count or 0,
                    file_size_bytes=project.file_size_bytes,
                    viewer_url=project.viewer_url,
                    created_at=project.created_at.isoformat(),
                    processing_started_at=project.processing_started_at.isoformat() if project.processing_started_at else None,
                    processing_completed_at=project.processing_completed_at.isoformat() if project.processing_completed_at else None,
                    error_message=project.error_message
                ))
            
            return result
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Projekte: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Projekte konnten nicht abgerufen werden"
        )

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: dict = Depends(require_user)
):
    """
    Gibt Details zu einem spezifischen Projekt zurück
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            project = reseller_db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
            return ProjectResponse(
                id=project.id,
                project_uuid=project.project_uuid,
                name=project.name,
                description=project.description,
                status=project.status,
                progress_percentage=project.progress_percentage,
                file_count=project.file_count or 0,
                file_size_bytes=project.file_size_bytes,
                viewer_url=project.viewer_url,
                created_at=project.created_at.isoformat(),
                processing_started_at=project.processing_started_at.isoformat() if project.processing_started_at else None,
                processing_completed_at=project.processing_completed_at.isoformat() if project.processing_completed_at else None,
                error_message=project.error_message
            )
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Projekts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Projekt konnte nicht abgerufen werden"
        )

@router.put("/projects/{project_id}")
async def update_project(
    project_id: int,
    update_data: UpdateProjectRequest,
    request: Request,
    current_user: dict = Depends(require_user)
):
    """
    Aktualisiert ein Projekt (nur Name und Beschreibung)
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            project = reseller_db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
            # Felder aktualisieren (nur wenn angegeben)
            update_fields = []
            for field, value in update_data.dict(exclude_unset=True).items():
                if hasattr(project, field) and value is not None:
                    setattr(project, field, value)
                    update_fields.append(field)
            
            if update_fields:
                project.updated_at = datetime.utcnow()
                reseller_db.commit()
                
                # Audit-Log erstellen
                from auth.auth_handler import auth_handler
                await auth_handler.log_audit_action(
                    reseller_db, "update_project", user_id=user_id,
                    resource_type="project", resource_id=str(project_id),
                    description=f"Projekt aktualisiert: {', '.join(update_fields)}",
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent", "unknown")
                )
                
                logger.info("Projekt aktualisiert", 
                           project_id=project_id,
                           fields=update_fields,
                           user_id=user_id)
            
            return {"message": "Projekt erfolgreich aktualisiert", "updated_fields": update_fields}
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Projekts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Projekt konnte nicht aktualisiert werden"
        )

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    request: Request,
    current_user: dict = Depends(require_user)
):
    """
    Löscht ein Projekt und alle zugehörigen Dateien
    
    WARNUNG: Diese Aktion ist irreversibel!
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            project = reseller_db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
            project_name = project.name
            
            # Projektdateien löschen
            import shutil
            if project.upload_path and os.path.exists(project.upload_path):
                shutil.rmtree(project.upload_path, ignore_errors=True)
            
            if project.viewer_path and os.path.exists(project.viewer_path):
                shutil.rmtree(project.viewer_path, ignore_errors=True)
            
            # Projekt aus DB löschen (Cascade löscht auch ProcessingLogs)
            reseller_db.delete(project)
            reseller_db.commit()
            
            # Audit-Log erstellen
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                reseller_db, "delete_project", user_id=user_id,
                resource_type="project", resource_id=str(project_id),
                description=f"Projekt '{project_name}' gelöscht",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("Projekt gelöscht", 
                       project_id=project_id,
                       project_name=project_name,
                       user_id=user_id)
            
            return {"message": "Projekt erfolgreich gelöscht"}
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Projekts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Projekt konnte nicht gelöscht werden"
        )

@router.get("/projects/{project_id}/logs")
async def get_project_logs(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_user)
):
    """
    Ruft Verarbeitungslogs für ein Projekt ab
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # Projekt-Berechtigung prüfen
            project = reseller_db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
            # Logs abrufen
            logs = reseller_db.query(ProcessingLog).filter(
                ProcessingLog.project_id == project_id
            ).order_by(ProcessingLog.timestamp.desc()).offset(skip).limit(limit).all()
            
            result = []
            for log in logs:
                result.append({
                    "id": log.id,
                    "log_level": log.log_level,
                    "message": log.message,
                    "step": log.step,
                    "progress": log.progress,
                    "timestamp": log.timestamp.isoformat()
                })
            
            return {
                "logs": result,
                "total": len(result),
                "skip": skip,
                "limit": limit,
                "project_id": project_id
            }
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Projekt-Logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Projekt-Logs konnten nicht abgerufen werden"
        )

# User-Profil
@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(require_user)
):
    """
    Ruft das User-Profil ab
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            user = reseller_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            # Projekt-Anzahl ermitteln
            project_count = reseller_db.query(Project).filter(Project.user_id == user_id).count()
            
            return UserProfileResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                max_projects=user.max_projects,
                max_upload_size_mb=user.max_upload_size_mb,
                is_active=user.is_active,
                email_verified=user.email_verified,
                created_at=user.created_at.isoformat(),
                last_login=user.last_login.isoformat() if user.last_login else None,
                project_count=project_count,
                gdpr_consent=user.gdpr_consent,
                gdpr_consent_date=user.gdpr_consent_date.isoformat() if user.gdpr_consent_date else None
            )
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des User-Profils: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User-Profil konnte nicht abgerufen werden"
        )

@router.get("/data-export")
async def export_user_data(
    current_user: dict = Depends(require_user)
):
    """
    DSGVO-konformer Datenexport für User
    Exportiert alle Benutzerdaten als ZIP-Datei
    """
    try:
        user_id = int(current_user.get("sub"))
        reseller_id = current_user.get("reseller_id")
        
        if not reseller_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reseller-ID fehlt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            user = reseller_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            import zipfile
            import json
            import tempfile
            from pathlib import Path
            
            # Temporäre ZIP-Datei erstellen
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    
                    # User-Daten als JSON
                    user_data = {
                        "user_profile": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "full_name": user.full_name,
                            "created_at": user.created_at.isoformat(),
                            "last_login": user.last_login.isoformat() if user.last_login else None,
                            "gdpr_consent": user.gdpr_consent,
                            "gdpr_consent_date": user.gdpr_consent_date.isoformat() if user.gdpr_consent_date else None
                        },
                        "projects": [],
                        "processing_logs": [],
                        "export_date": datetime.utcnow().isoformat()
                    }
                    
                    # Projekte hinzufügen
                    projects = reseller_db.query(Project).filter(Project.user_id == user_id).all()
                    for project in projects:
                        project_data = {
                            "id": project.id,
                            "project_uuid": project.project_uuid,
                            "name": project.name,
                            "description": project.description,
                            "status": project.status,
                            "created_at": project.created_at.isoformat(),
                            "file_count": project.file_count,
                            "file_size_bytes": project.file_size_bytes
                        }
                        user_data["projects"].append(project_data)
                        
                        # Processing-Logs für dieses Projekt
                        logs = reseller_db.query(ProcessingLog).filter(
                            ProcessingLog.project_id == project.id
                        ).all()
                        
                        for log in logs:
                            log_data = {
                                "project_id": project.id,
                                "project_name": project.name,
                                "log_level": log.log_level,
                                "message": log.message,
                                "step": log.step,
                                "timestamp": log.timestamp.isoformat()
                            }
                            user_data["processing_logs"].append(log_data)
                    
                    # JSON-Daten zur ZIP hinzufügen
                    zipf.writestr("user_data.json", json.dumps(user_data, indent=2, ensure_ascii=False))
                    
                    # README hinzufügen
                    readme_content = f"""
ChiliView Datenexport für {user.username}
========================================

Dieser Export enthält alle Ihre persönlichen Daten aus der ChiliView-Plattform.

Inhalt:
- user_data.json: Alle Ihre Profil- und Projektdaten in strukturierter Form

Export erstellt am: {datetime.utcnow().isoformat()}
Reseller: {reseller_id}

Für Fragen zu diesem Export wenden Sie sich bitte an den Support.
"""
                    zipf.writestr("README.txt", readme_content)
                
                # Audit-Log erstellen
                from auth.auth_handler import auth_handler
                await auth_handler.log_audit_action(
                    reseller_db, "data_export", user_id=user_id,
                    resource_type="user", resource_id=str(user_id),
                    description="DSGVO-Datenexport erstellt",
                    ip_address="system",
                    user_agent="system"
                )
                
                logger.info("Datenexport erstellt", 
                           user_id=user_id,
                           username=user.username,
                           reseller_id=reseller_id)
                
                # ZIP-Datei als Response zurückgeben
                from fastapi.responses import FileResponse
                return FileResponse(
                    path=temp_file.name,
                    filename=f"chiliview_export_{user.username}_{datetime.now().strftime('%Y%m%d')}.zip",
                    media_type='application/zip'
                )
                
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Datenexport: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Datenexport konnte nicht erstellt werden"
        )

@router.get("/health")
async def user_health_check():
    """
    Gesundheitscheck für den User-Service
    """
    return {
        "status": "healthy",
        "service": "user",
        "version": "1.0.0"
    }