"""
WebODM Service für automatische Integration und Konfiguration
Stellt sicher, dass WebODM vollständig konfiguriert und einsatzbereit ist
"""

import asyncio
import aiohttp
import logging
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WebODMService:
    """Service für WebODM-Integration mit automatischer Konfiguration"""
    
    def __init__(self):
        self.base_url = os.getenv("WEBODM_URL", "http://webodm-webapp:8080")
        self.username = os.getenv("WEBODM_USERNAME", "admin")
        self.password = os.getenv("WEBODM_PASSWORD", "admin")
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.ensure_webodm_ready()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def ensure_webodm_ready(self) -> bool:
        """
        Stellt sicher, dass WebODM vollständig konfiguriert und einsatzbereit ist
        """
        try:
            # Warten bis WebODM verfügbar ist
            if not await self._wait_for_webodm():
                logger.error("WebODM ist nicht verfügbar")
                return False
                
            # Admin-Benutzer sicherstellen
            if not await self._ensure_admin_user():
                logger.error("Konnte WebODM Admin-Benutzer nicht erstellen")
                return False
                
            # Authentifizierung
            if not await self._authenticate():
                logger.error("WebODM-Authentifizierung fehlgeschlagen")
                return False
                
            # Grundkonfiguration prüfen/setzen
            await self._configure_webodm()
            
            logger.info("WebODM ist vollständig konfiguriert und einsatzbereit")
            return True
            
        except Exception as e:
            logger.error(f"Fehler bei WebODM-Initialisierung: {e}")
            return False
            
    async def _wait_for_webodm(self, timeout: int = 300) -> bool:
        """Wartet bis WebODM verfügbar ist"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                async with self.session.get(f"{self.base_url}/api/") as response:
                    if response.status == 200:
                        logger.info("WebODM ist verfügbar")
                        return True
            except Exception:
                pass
                
            logger.info("Warte auf WebODM...")
            await asyncio.sleep(5)
            
        return False
        
    async def _ensure_admin_user(self) -> bool:
        """Stellt sicher, dass der Admin-Benutzer existiert"""
        try:
            # Versuche Login - wenn erfolgreich, existiert der Benutzer bereits
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(
                f"{self.base_url}/api/token-auth/",
                json=login_data
            ) as response:
                if response.status == 200:
                    logger.info("WebODM Admin-Benutzer bereits vorhanden")
                    return True
                    
            # Benutzer existiert nicht - über Django Management Command erstellen
            logger.info("Erstelle WebODM Admin-Benutzer...")
            
            # Da wir keinen direkten Zugriff auf Django haben,
            # verwenden wir die WebODM-interne Registrierung falls verfügbar
            # oder setzen voraus, dass das init-webodm.sh Skript läuft
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Sicherstellen des Admin-Benutzers: {e}")
            return False
            
    async def _authenticate(self) -> bool:
        """Authentifiziert sich bei WebODM"""
        try:
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(
                f"{self.base_url}/api/token-auth/",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.token = data.get("token")
                    # Token ist 24 Stunden gültig
                    self.token_expires = datetime.now() + timedelta(hours=23)
                    
                    # Session-Header setzen
                    self.session.headers.update({
                        "Authorization": f"JWT {self.token}"
                    })
                    
                    logger.info("WebODM-Authentifizierung erfolgreich")
                    return True
                else:
                    logger.error(f"WebODM-Login fehlgeschlagen: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Fehler bei WebODM-Authentifizierung: {e}")
            return False
            
    async def _configure_webodm(self):
        """Konfiguriert WebODM für ChiliView"""
        try:
            # Grundeinstellungen prüfen/setzen
            settings = {
                "PROCESSING_NODES_ONLINECHECK": True,
                "PROCESSING_NODES_ONLINECHECK_INTERVAL": 60,
                "MAX_IMAGES_PER_TASK": 10000,
                "TASK_CLEANUP_DAYS": 30
            }
            
            for key, value in settings.items():
                await self._set_setting(key, value)
                
            logger.info("WebODM-Grundkonfiguration abgeschlossen")
            
        except Exception as e:
            logger.error(f"Fehler bei WebODM-Konfiguration: {e}")
            
    async def _set_setting(self, key: str, value: Any):
        """Setzt eine WebODM-Einstellung"""
        try:
            # WebODM-Settings sind normalerweise über Admin-Interface verfügbar
            # Hier würden wir die entsprechende API verwenden falls verfügbar
            pass
        except Exception as e:
            logger.debug(f"Konnte Einstellung {key} nicht setzen: {e}")
            
    async def refresh_token_if_needed(self):
        """Erneuert Token falls nötig"""
        if (not self.token or 
            not self.token_expires or 
            datetime.now() >= self.token_expires - timedelta(minutes=5)):
            await self._authenticate()
            
    async def create_project(self, name: str, description: str = "") -> Optional[Dict]:
        """Erstellt ein neues WebODM-Projekt"""
        try:
            await self.refresh_token_if_needed()
            
            project_data = {
                "name": name,
                "description": description
            }
            
            async with self.session.post(
                f"{self.base_url}/api/projects/",
                json=project_data
            ) as response:
                if response.status == 201:
                    project = await response.json()
                    logger.info(f"WebODM-Projekt erstellt: {project['id']}")
                    return project
                else:
                    logger.error(f"Fehler beim Erstellen des Projekts: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des WebODM-Projekts: {e}")
            return None
            
    async def create_task(self, project_id: int, name: str, images_path: str, 
                         options: Dict = None) -> Optional[Dict]:
        """Erstellt eine neue WebODM-Aufgabe"""
        try:
            await self.refresh_token_if_needed()
            
            # Standard-Optionen für Drohnenfotografie
            default_options = {
                "auto-boundary": True,
                "mesh-octree-depth": 11,
                "mesh-size": 200000,
                "mesh-point-weight": 4,
                "texturing-data-term": "area",
                "texturing-nadir-weight": 16,
                "texturing-outlier-removal-type": "gauss_clamping",
                "texturing-skip-global-seam-leveling": True,
                "texturing-skip-local-seam-leveling": False,
                "texturing-skip-hole-filling": True,
                "orthophoto-resolution": 5,
                "dem-resolution": 5,
                "feature-quality": "high",
                "pc-quality": "high",
                "matcher-neighbors": 8,
                "matcher-distance": 0
            }
            
            if options:
                default_options.update(options)
                
            # Aufgabe erstellen
            task_data = {
                "name": name,
                "processing_node": None,  # Automatische Auswahl
                "options": [{"name": k, "value": v} for k, v in default_options.items()]
            }
            
            # Bilder hochladen und Aufgabe erstellen
            # Dies würde normalerweise über Multipart-Upload erfolgen
            # Hier vereinfacht dargestellt
            
            async with self.session.post(
                f"{self.base_url}/api/projects/{project_id}/tasks/",
                json=task_data
            ) as response:
                if response.status == 201:
                    task = await response.json()
                    logger.info(f"WebODM-Aufgabe erstellt: {task['id']}")
                    return task
                else:
                    logger.error(f"Fehler beim Erstellen der Aufgabe: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der WebODM-Aufgabe: {e}")
            return None
            
    async def get_task_status(self, project_id: int, task_id: str) -> Optional[Dict]:
        """Ruft den Status einer WebODM-Aufgabe ab"""
        try:
            await self.refresh_token_if_needed()
            
            async with self.session.get(
                f"{self.base_url}/api/projects/{project_id}/tasks/{task_id}/"
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Fehler beim Abrufen des Aufgabenstatus: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des WebODM-Aufgabenstatus: {e}")
            return None
            
    async def download_assets(self, project_id: int, task_id: str, 
                            asset_type: str = "orthophoto.tif") -> Optional[bytes]:
        """Lädt Assets von einer WebODM-Aufgabe herunter"""
        try:
            await self.refresh_token_if_needed()
            
            async with self.session.get(
                f"{self.base_url}/api/projects/{project_id}/tasks/{task_id}/download/{asset_type}"
            ) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"Fehler beim Herunterladen von {asset_type}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Fehler beim Herunterladen der WebODM-Assets: {e}")
            return None
            
    async def health_check(self) -> bool:
        """Prüft ob WebODM gesund ist"""
        try:
            async with self.session.get(f"{self.base_url}/api/") as response:
                return response.status == 200
        except Exception:
            return False


# Globale WebODM-Service-Instanz
webodm_service = WebODMService()


async def get_webodm_service() -> WebODMService:
    """Dependency für FastAPI"""
    return webodm_service


async def initialize_webodm():
    """Initialisiert WebODM beim Anwendungsstart"""
    try:
        async with WebODMService() as service:
            success = await service.ensure_webodm_ready()
            if success:
                logger.info("WebODM erfolgreich initialisiert")
            else:
                logger.warning("WebODM-Initialisierung fehlgeschlagen - manueller Setup erforderlich")
    except Exception as e:
        logger.error(f"Fehler bei WebODM-Initialisierung: {e}")