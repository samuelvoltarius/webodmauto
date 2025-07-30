"""
ChiliView Upload Router
API-Endpunkte für Datei-Upload, Virenscan und WebODM-CLI Integration
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
import os
import uuid
import shutil
import asyncio
from pathlib import Path
# Windows-kompatible magic-Implementierung
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    # Fallback für Windows ohne libmagic
    class MockMagic:
        @staticmethod
        def from_file(path, mime=True):
            return "image/jpeg"  # Fallback für Bilder
    magic = MockMagic()
import hashlib

from auth.auth_handler import require_user, get_current_user
from database.database import get_reseller_database
from database.models import User, Project, ProcessingLog, VirusScanResult

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic Models
class UploadResponse(BaseModel):
    """Upload-Antwort"""
    project_id: int
    project_uuid: str
    message: str
    file_count: int
    total_size_bytes: int
    status: str

class ProcessingStatusResponse(BaseModel):
    """Verarbeitungsstatus-Antwort"""
    project_id: int
    status: str
    progress_percentage: float
    current_step: Optional[str]
    estimated_completion: Optional[str]
    error_message: Optional[str]

# Konfiguration
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.raw', '.dng'}
MAX_FILES_PER_UPLOAD = 1000
CHUNK_SIZE = 8192  # 8KB Chunks für Streaming

class VirusScanner:
    """
    Virus-Scanner Integration mit ClamAV
    """
    
    def __init__(self):
        self.enabled = os.getenv("VIRUS_SCAN_ENABLED", "true").lower() == "true"
        
    async def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Scannt eine Datei auf Viren
        """
        if not self.enabled:
            return {
                "is_clean": True,
                "threat_name": None,
                "scan_engine_version": "disabled"
            }
        
        try:
            import pyclamd
            
            # ClamAV-Daemon verbinden
            cd = pyclamd.ClamdUnixSocket()
            
            # Ping-Test
            if not cd.ping():
                logger.warning("ClamAV-Daemon nicht erreichbar")
                return {
                    "is_clean": True,  # Bei Fehler durchlassen
                    "threat_name": None,
                    "scan_engine_version": "unavailable"
                }
            
            # Datei scannen
            scan_result = cd.scan_file(file_path)
            
            if scan_result is None:
                # Datei ist sauber
                return {
                    "is_clean": True,
                    "threat_name": None,
                    "scan_engine_version": cd.version()
                }
            else:
                # Bedrohung gefunden
                threat_name = scan_result[file_path][1] if file_path in scan_result else "Unknown"
                return {
                    "is_clean": False,
                    "threat_name": threat_name,
                    "scan_engine_version": cd.version()
                }
                
        except Exception as e:
            logger.error(f"Fehler beim Virenscan: {str(e)}")
            # Bei Fehler durchlassen (fail-open)
            return {
                "is_clean": True,
                "threat_name": None,
                "scan_engine_version": "error"
            }

class WebODMProcessor:
    """
    WebODM-CLI Integration für Fotogrammetrie-Verarbeitung
    """
    
    def __init__(self):
        self.webodm_url = os.getenv("WEBODM_URL", "http://webodm-cli:8080")
        self.webodm_username = os.getenv("WEBODM_USERNAME", "admin")
        self.webodm_password = os.getenv("WEBODM_PASSWORD", "admin")
        
    async def create_task(self, project_id: int, images_path: str, reseller_db) -> str:
        """
        Erstellt eine neue WebODM-Aufgabe
        """
        try:
            import httpx
            
            # WebODM-API Client
            async with httpx.AsyncClient(timeout=30.0) as client:
                
                # Login
                login_data = {
                    "username": self.webodm_username,
                    "password": self.webodm_password
                }
                
                login_response = await client.post(
                    f"{self.webodm_url}/api/token-auth/",
                    data=login_data
                )
                
                if login_response.status_code != 200:
                    raise Exception(f"WebODM Login fehlgeschlagen: {login_response.status_code}")
                
                token = login_response.json()["token"]
                headers = {"Authorization": f"Token {token}"}
                
                # Projekt erstellen
                project_data = {
                    "name": f"ChiliView_Project_{project_id}",
                    "description": f"Automatisch erstellt für Projekt {project_id}"
                }
                
                project_response = await client.post(
                    f"{self.webodm_url}/api/projects/",
                    json=project_data,
                    headers=headers
                )
                
                if project_response.status_code != 201:
                    raise Exception(f"WebODM Projekt-Erstellung fehlgeschlagen: {project_response.status_code}")
                
                webodm_project_id = project_response.json()["id"]
                
                # Task erstellen
                task_data = {
                    "project": webodm_project_id,
                    "name": f"Task_{project_id}",
                    "processing_node": None,  # Auto-select
                    "auto_boundary": True,
                    "options": [
                        {"name": "mesh-octree-depth", "value": "11"},
                        {"name": "mesh-size", "value": "200000"},
                        {"name": "texturing-data-term", "value": "area"},
                        {"name": "texturing-nadir-weight", "value": "16"}
                    ]
                }
                
                # Bilder als Multipart-Upload vorbereiten
                files = []
                image_files = list(Path(images_path).glob("*"))
                
                for image_file in image_files:
                    if image_file.suffix.lower() in ALLOWED_EXTENSIONS:
                        files.append(
                            ("images", (image_file.name, open(image_file, "rb"), "image/jpeg"))
                        )
                
                # Task mit Bildern erstellen
                task_response = await client.post(
                    f"{self.webodm_url}/api/projects/{webodm_project_id}/tasks/",
                    data=task_data,
                    files=files,
                    headers=headers
                )
                
                # Dateien schließen
                for _, (_, file_obj, _) in files:
                    file_obj.close()
                
                if task_response.status_code != 201:
                    raise Exception(f"WebODM Task-Erstellung fehlgeschlagen: {task_response.status_code}")
                
                task_id = task_response.json()["id"]
                webodm_task_id = f"{webodm_project_id}_{task_id}"
                
                logger.info("WebODM Task erstellt", 
                           project_id=project_id,
                           webodm_task_id=webodm_task_id)
                
                return webodm_task_id
                
        except Exception as e:
            logger.error(f"Fehler bei WebODM Task-Erstellung: {str(e)}")
            
            # Processing-Log erstellen
            await self.log_processing_error(reseller_db, project_id, str(e))
            raise
    
    async def get_task_status(self, webodm_task_id: str) -> Dict[str, Any]:
        """
        Ruft den Status einer WebODM-Aufgabe ab
        """
        try:
            import httpx
            
            project_id, task_id = webodm_task_id.split("_")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                
                # Login
                login_data = {
                    "username": self.webodm_username,
                    "password": self.webodm_password
                }
                
                login_response = await client.post(
                    f"{self.webodm_url}/api/token-auth/",
                    data=login_data
                )
                
                if login_response.status_code != 200:
                    raise Exception(f"WebODM Login fehlgeschlagen: {login_response.status_code}")
                
                token = login_response.json()["token"]
                headers = {"Authorization": f"Token {token}"}
                
                # Task-Status abrufen
                task_response = await client.get(
                    f"{self.webodm_url}/api/projects/{project_id}/tasks/{task_id}/",
                    headers=headers
                )
                
                if task_response.status_code != 200:
                    raise Exception(f"WebODM Task-Status abrufen fehlgeschlagen: {task_response.status_code}")
                
                task_data = task_response.json()
                
                # Status mapping
                status_mapping = {
                    10: "queued",      # QUEUED
                    20: "processing",  # RUNNING
                    30: "completed",   # COMPLETED
                    40: "failed",      # FAILED
                    50: "canceled"     # CANCELED
                }
                
                status = status_mapping.get(task_data["status"], "unknown")
                progress = task_data.get("running_progress", 0)
                
                return {
                    "status": status,
                    "progress_percentage": progress,
                    "current_step": task_data.get("last_error", ""),
                    "processing_time": task_data.get("processing_time", 0),
                    "output_available": task_data.get("available_assets", [])
                }
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des WebODM Task-Status: {str(e)}")
            return {
                "status": "error",
                "progress_percentage": 0,
                "current_step": f"Fehler: {str(e)}",
                "processing_time": 0,
                "output_available": []
            }
    
    async def download_results(self, webodm_task_id: str, output_path: str) -> bool:
        """
        Lädt die Ergebnisse einer WebODM-Aufgabe herunter
        """
        try:
            import httpx
            
            project_id, task_id = webodm_task_id.split("_")
            
            async with httpx.AsyncClient(timeout=300.0) as client:  # 5 Minuten Timeout
                
                # Login
                login_data = {
                    "username": self.webodm_username,
                    "password": self.webodm_password
                }
                
                login_response = await client.post(
                    f"{self.webodm_url}/api/token-auth/",
                    data=login_data
                )
                
                if login_response.status_code != 200:
                    raise Exception(f"WebODM Login fehlgeschlagen: {login_response.status_code}")
                
                token = login_response.json()["token"]
                headers = {"Authorization": f"Token {token}"}
                
                # Verfügbare Assets abrufen
                assets_response = await client.get(
                    f"{self.webodm_url}/api/projects/{project_id}/tasks/{task_id}/",
                    headers=headers
                )
                
                if assets_response.status_code != 200:
                    raise Exception("Konnte verfügbare Assets nicht abrufen")
                
                available_assets = assets_response.json().get("available_assets", [])
                
                # Wichtige Assets herunterladen
                important_assets = ["textured_model.zip", "orthophoto.tif", "dsm.tif"]
                
                Path(output_path).mkdir(parents=True, exist_ok=True)
                
                for asset in important_assets:
                    if asset in available_assets:
                        
                        download_response = await client.get(
                            f"{self.webodm_url}/api/projects/{project_id}/tasks/{task_id}/download/{asset}",
                            headers=headers
                        )
                        
                        if download_response.status_code == 200:
                            asset_path = Path(output_path) / asset
                            with open(asset_path, "wb") as f:
                                f.write(download_response.content)
                            
                            logger.info(f"Asset heruntergeladen: {asset}")
                
                return True
                
        except Exception as e:
            logger.error(f"Fehler beim Herunterladen der WebODM-Ergebnisse: {str(e)}")
            return False
    
    async def log_processing_error(self, reseller_db, project_id: int, error_message: str):
        """
        Loggt einen Verarbeitungsfehler
        """
        try:
            processing_log = ProcessingLog(
                project_id=project_id,
                log_level="ERROR",
                message=error_message,
                step="webodm_processing",
                progress=0.0
            )
            
            reseller_db.add(processing_log)
            reseller_db.commit()
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Processing-Logs: {str(e)}")

# Globale Instanzen
virus_scanner = VirusScanner()
webodm_processor = WebODMProcessor()

@router.post("/", response_model=UploadResponse)
async def upload_files(
    project_name: str = Form(...),
    project_description: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    request: Request = None,
    current_user: dict = Depends(require_user)
):
    """
    Lädt Dateien hoch und startet die Verarbeitung
    
    - **project_name**: Name des Projekts
    - **project_description**: Optionale Beschreibung
    - **files**: Liste der hochzuladenden Bilddateien
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
            # User-Daten und Limits laden
            user = reseller_db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User nicht gefunden")
            
            # Projekt-Limit prüfen
            current_projects = reseller_db.query(Project).filter(Project.user_id == user_id).count()
            if current_projects >= user.max_projects:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Projekt-Limit erreicht ({user.max_projects})"
                )
            
            # Datei-Validierung
            if len(files) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Keine Dateien hochgeladen"
                )
            
            if len(files) > MAX_FILES_PER_UPLOAD:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Zu viele Dateien (Maximum: {MAX_FILES_PER_UPLOAD})"
                )
            
            # Gesamtgröße prüfen
            total_size = 0
            for file in files:
                if hasattr(file, 'size') and file.size:
                    total_size += file.size
            
            max_size_bytes = user.max_upload_size_mb * 1024 * 1024
            if total_size > max_size_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Upload zu groß ({total_size} bytes, Maximum: {max_size_bytes} bytes)"
                )
            
            # Projekt erstellen
            project_uuid = str(uuid.uuid4())
            project = Project(
                project_uuid=project_uuid,
                name=project_name,
                description=project_description,
                user_id=user_id,
                status="uploading",
                file_count=len(files),
                file_size_bytes=total_size,
                progress_percentage=0.0
            )
            
            reseller_db.add(project)
            reseller_db.commit()
            reseller_db.refresh(project)
            
            # Upload-Verzeichnis erstellen
            upload_dir = Path(f"data/resellers/{reseller_id}/projects/{project.id}/upload")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            project.upload_path = str(upload_dir)
            reseller_db.commit()
            
            # Dateien hochladen und validieren
            uploaded_files = []
            virus_scan_results = []
            
            for i, file in enumerate(files):
                # Dateiname validieren
                if not file.filename:
                    continue
                
                # Dateierweiterung prüfen
                file_ext = Path(file.filename).suffix.lower()
                if file_ext not in ALLOWED_EXTENSIONS:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Dateityp nicht unterstützt: {file_ext}"
                    )
                
                # Sichere Dateinamen generieren
                safe_filename = f"{i:04d}_{file.filename}"
                file_path = upload_dir / safe_filename
                
                # Datei speichern
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # Dateityp mit python-magic verifizieren (Windows-kompatibel)
                if MAGIC_AVAILABLE:
                    try:
                        file_type = magic.from_file(str(file_path), mime=True)
                        if not file_type.startswith('image/'):
                            os.remove(file_path)
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Datei ist kein gültiges Bild: {file.filename}"
                            )
                    except Exception as e:
                        logger.warning(f"Magic-Dateityp-Prüfung fehlgeschlagen: {str(e)}")
                        # Fallback: Dateierweiterung vertrauen
                        pass
                else:
                    # Windows-Fallback: Nur Dateierweiterung prüfen
                    logger.debug("Magic nicht verfügbar, verwende Dateierweiterung für Validierung")
                
                # Datei-Hash berechnen
                file_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        file_hash.update(chunk)
                
                # Virenscan
                scan_result = await virus_scanner.scan_file(str(file_path))
                
                if not scan_result["is_clean"]:
                    # Infizierte Datei löschen
                    os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Virus gefunden in {file.filename}: {scan_result['threat_name']}"
                    )
                
                # Scan-Ergebnis speichern
                virus_scan_record = VirusScanResult(
                    file_path=str(file_path),
                    file_hash=file_hash.hexdigest(),
                    is_clean=scan_result["is_clean"],
                    threat_name=scan_result["threat_name"],
                    scan_engine_version=scan_result["scan_engine_version"]
                )
                
                reseller_db.add(virus_scan_record)
                virus_scan_results.append(scan_result)
                uploaded_files.append(str(file_path))
                
                # Progress aktualisieren
                progress = ((i + 1) / len(files)) * 50  # Upload = 50% des Gesamtfortschritts
                project.progress_percentage = progress
                reseller_db.commit()
            
            # Upload abgeschlossen
            project.status = "uploaded"
            project.progress_percentage = 50.0
            reseller_db.commit()
            
            # Audit-Log erstellen
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                reseller_db, "upload_files", user_id=user_id,
                resource_type="project", resource_id=str(project.id),
                description=f"Dateien hochgeladen: {len(uploaded_files)} Dateien, {total_size} bytes",
                ip_address=request.client.host if request else "unknown",
                user_agent=request.headers.get("user-agent", "unknown") if request else "unknown"
            )
            
            logger.info("Upload abgeschlossen", 
                       project_id=project.id,
                       file_count=len(uploaded_files),
                       total_size=total_size,
                       user_id=user_id)
            
            # WebODM-Verarbeitung im Hintergrund starten
            asyncio.create_task(start_processing(project.id, reseller_id))
            
            return UploadResponse(
                project_id=project.id,
                project_uuid=project.project_uuid,
                message="Upload erfolgreich, Verarbeitung gestartet",
                file_count=len(uploaded_files),
                total_size_bytes=total_size,
                status="uploaded"
            )
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Upload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload konnte nicht abgeschlossen werden"
        )

async def start_processing(project_id: int, reseller_id: str):
    """
    Startet die WebODM-Verarbeitung im Hintergrund
    """
    reseller_db = get_reseller_database(reseller_id)
    
    try:
        project = reseller_db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Projekt {project_id} nicht gefunden für Verarbeitung")
            return
        
        # Status auf "processing" setzen
        project.status = "processing"
        project.processing_started_at = datetime.utcnow()
        project.progress_percentage = 60.0
        reseller_db.commit()
        
        # Processing-Log erstellen
        processing_log = ProcessingLog(
            project_id=project_id,
            log_level="INFO",
            message="WebODM-Verarbeitung gestartet",
            step="webodm_start",
            progress=60.0
        )
        reseller_db.add(processing_log)
        reseller_db.commit()
        
        # WebODM-Task erstellen
        webodm_task_id = await webodm_processor.create_task(
            project_id, project.upload_path, reseller_db
        )
        
        project.webodm_task_id = webodm_task_id
        project.progress_percentage = 70.0
        reseller_db.commit()
        
        # Status-Polling starten
        await poll_processing_status(project_id, reseller_id)
        
    except Exception as e:
        logger.error(f"Fehler bei Verarbeitungsstart: {str(e)}")
        
        # Projekt als fehlgeschlagen markieren
        project = reseller_db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "failed"
            project.error_message = str(e)
            reseller_db.commit()
        
    finally:
        reseller_db.close()

async def poll_processing_status(project_id: int, reseller_id: str):
    """
    Überwacht den Verarbeitungsstatus
    """
    reseller_db = get_reseller_database(reseller_id)
    
    try:
        project = reseller_db.query(Project).filter(Project.id == project_id).first()
        if not project or not project.webodm_task_id:
            return
        
        max_polls = 360  # 6 Stunden bei 60s Intervall
        poll_count = 0
        
        while poll_count < max_polls:
            await asyncio.sleep(60)  # 1 Minute warten
            poll_count += 1
            
            # Status von WebODM abrufen
            status_data = await webodm_processor.get_task_status(project.webodm_task_id)
            
            # Projekt aktualisieren
            project = reseller_db.query(Project).filter(Project.id == project_id).first()
            if not project:
                break
            
            old_progress = project.progress_percentage
            new_progress = 70.0 + (status_data["progress_percentage"] * 0.25)  # 70-95%
            
            project.progress_percentage = new_progress
            
            # Processing-Log nur bei Fortschritt
            if new_progress > old_progress:
                processing_log = ProcessingLog(
                    project_id=project_id,
                    log_level="INFO",
                    message=f"Verarbeitung: {status_data['progress_percentage']:.1f}%",
                    step=status_data.get("current_step", "processing"),
                    progress=new_progress
                )
                reseller_db.add(processing_log)
            
            if status_data["status"] == "completed":
                # Ergebnisse herunterladen
                output_dir = Path(f"data/resellers/{reseller_id}/projects/{project_id}/output")
                
                success = await webodm_processor.download_results(
                    project.webodm_task_id, str(output_dir)
                )
                
                if success:
                    project.status = "completed"
                    project.progress_percentage = 100.0
                    project.processing_completed_at = datetime.utcnow()
                    project.viewer_path = str(output_dir)
                    project.viewer_url = f"/viewer/{reseller_id}/{project_id}/"
                    
                    # Upload-Dateien löschen (Speicherplatz sparen)
                    if project.upload_path and Path(project.upload_path).exists():
                        shutil.rmtree(project.upload_path, ignore_errors=True)
                    
                    processing_log = ProcessingLog(
                        project_id=project_id,
                        log_level="INFO",
                        message="Verarbeitung erfolgreich abgeschlossen",
                        step="completed",
                        progress=100.0
                    )
                    reseller_db.add(processing_log)
                    
                    logger.info("Verarbeitung abgeschlossen", project_id=project_id)
                else:
                    project.status = "failed"
                    project.error_message = "Ergebnisse konnten nicht heruntergeladen werden"
                
                reseller_db.commit()
                break
                
            elif status_data["status"] == "failed":
                project.status = "failed"
                project.error_message = status_data.get("current_step", "Unbekannter Fehler")
                
                processing_log = ProcessingLog(
                    project_id=project_id,
                    log_level="ERROR",
                    message=f"Verarbeitung fehlgeschlagen: {project.error_message}",
                    step="failed",
                    progress=project.progress_percentage
                )
                reseller_db.add(processing_log)
                
                reseller_db.commit()
                logger.error("Verarbeitung fehlgeschlagen", 
                           project_id=project_id, 
                           error=project.error_message)
                break
            
            reseller_db.commit()
        
        # Timeout erreicht
        if poll_count >= max_polls:
            project = reseller_db.query(Project).filter(Project.id == project_id).first()
            if project and project.status == "processing":
                project.status = "failed"
                project.error_message = "Verarbeitung-Timeout erreicht"
                reseller_db.commit()
                
                logger.warning("Verarbeitung-Timeout", project_id=project_id)
        
    except Exception as e:
        logger.error(f"Fehler beim Status-Polling: {str(e)}")
    finally:
        reseller_db.close()

@router.get("/status/{project_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    project_id: int,
    current_user: dict = Depends(require_user)
):
    """
    Ruft den aktuellen Verarbeitungsstatus ab
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
            
            # Geschätzte Fertigstellung berechnen
            estimated_completion = None
            if project.status == "processing" and project.processing_started_at:
                # Einfache Schätzung basierend auf bisherigem Fortschritt
                from datetime import timedelta
                elapsed = datetime.utcnow() - project.processing_started_at
                if project.progress_percentage > 70:
                    remaining_progress = 100 - project.progress_percentage
                    progress_rate = (project.progress_percentage - 70) / elapsed.total_seconds()
                    if progress_rate > 0:
                        remaining_seconds = remaining_progress / progress_rate
                        estimated_completion = (datetime.utcnow() +
                                              timedelta(seconds=remaining_seconds)).isoformat()
            
            # Aktuellen Schritt aus letztem Log ermitteln
            current_step = None
            latest_log = reseller_db.query(ProcessingLog).filter(
                ProcessingLog.project_id == project_id
            ).order_by(ProcessingLog.timestamp.desc()).first()
            
            if latest_log:
                current_step = latest_log.step
            
            return ProcessingStatusResponse(
                project_id=project.id,
                status=project.status,
                progress_percentage=project.progress_percentage,
                current_step=current_step,
                estimated_completion=estimated_completion,
                error_message=project.error_message
            )
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Verarbeitungsstatus: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verarbeitungsstatus konnte nicht abgerufen werden"
        )

@router.delete("/{project_id}")
async def cancel_processing(
    project_id: int,
    request: Request,
    current_user: dict = Depends(require_user)
):
    """
    Bricht die Verarbeitung eines Projekts ab
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
            
            if project.status not in ["uploaded", "processing"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Projekt kann nicht abgebrochen werden"
                )
            
            # Status auf "canceled" setzen
            project.status = "failed"
            project.error_message = "Verarbeitung vom Benutzer abgebrochen"
            reseller_db.commit()
            
            # Processing-Log erstellen
            processing_log = ProcessingLog(
                project_id=project_id,
                log_level="INFO",
                message="Verarbeitung vom Benutzer abgebrochen",
                step="canceled",
                progress=project.progress_percentage
            )
            reseller_db.add(processing_log)
            reseller_db.commit()
            
            # Audit-Log erstellen
            from auth.auth_handler import auth_handler
            await auth_handler.log_audit_action(
                reseller_db, "cancel_processing", user_id=user_id,
                resource_type="project", resource_id=str(project_id),
                description="Verarbeitung abgebrochen",
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown")
            )
            
            logger.info("Verarbeitung abgebrochen",
                       project_id=project_id,
                       user_id=user_id)
            
            return {"message": "Verarbeitung erfolgreich abgebrochen"}
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abbrechen der Verarbeitung: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verarbeitung konnte nicht abgebrochen werden"
        )

@router.get("/health")
async def upload_health_check():
    """
    Gesundheitscheck für den Upload-Service
    """
    return {
        "status": "healthy",
        "service": "upload",
        "version": "1.0.0",
        "virus_scanner_enabled": virus_scanner.enabled,
        "webodm_url": webodm_processor.webodm_url
    }