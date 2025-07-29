"""
WebODM-CLI Service für direkte Kommandozeilen-Integration
Keine Weboberfläche, nur CLI-Befehle für Photogrammetrie-Verarbeitung
"""

import asyncio
import subprocess
import logging
import os
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class WebODMCLIService:
    """Service für direkte WebODM-CLI Integration ohne Webinterface"""
    
    def __init__(self):
        self.webodm_cli_path = self._find_webodm_cli()
        self.projects_base_path = Path("data/webodm_projects")
        self.projects_base_path.mkdir(parents=True, exist_ok=True)
        
    def _find_webodm_cli(self) -> Optional[str]:
        """Findet WebODM-CLI Installation"""
        possible_paths = [
            "/usr/local/bin/webodm.sh",
            "/opt/webodm/webodm.sh", 
            "./webodm/webodm.sh",
            "webodm.sh"
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                logger.info(f"WebODM-CLI gefunden: {path}")
                return path
                
        logger.warning("WebODM-CLI nicht gefunden - wird bei Bedarf installiert")
        return None
        
    async def install_webodm_cli(self) -> bool:
        """Installiert WebODM-CLI falls nicht vorhanden"""
        try:
            logger.info("Installiere WebODM-CLI...")
            
            # WebODM-CLI von GitHub herunterladen
            install_dir = Path("/opt/webodm")
            install_dir.mkdir(parents=True, exist_ok=True)
            
            # Git clone WebODM
            process = await asyncio.create_subprocess_exec(
                "git", "clone", "https://github.com/OpenDroneMap/WebODM.git", 
                str(install_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # WebODM-CLI ausführbar machen
                cli_path = install_dir / "webodm.sh"
                if cli_path.exists():
                    os.chmod(cli_path, 0o755)
                    self.webodm_cli_path = str(cli_path)
                    logger.info("WebODM-CLI erfolgreich installiert")
                    return True
                    
            logger.error(f"WebODM-CLI Installation fehlgeschlagen: {stderr.decode()}")
            return False
            
        except Exception as e:
            logger.error(f"Fehler bei WebODM-CLI Installation: {e}")
            return False
            
    async def create_project(self, project_name: str, reseller_id: str) -> str:
        """Erstellt ein neues WebODM-CLI Projekt"""
        try:
            # Projekt-Verzeichnis erstellen
            project_path = self.projects_base_path / reseller_id / project_name
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Unterverzeichnisse erstellen
            (project_path / "images").mkdir(exist_ok=True)
            (project_path / "output").mkdir(exist_ok=True)
            (project_path / "logs").mkdir(exist_ok=True)
            
            logger.info(f"WebODM-CLI Projekt erstellt: {project_path}")
            return str(project_path)
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des WebODM-CLI Projekts: {e}")
            raise
            
    async def process_images(self, project_path: str, images_path: str,
                           options: Dict[str, Any] = None, instance_id: str = None) -> Dict[str, Any]:
        """
        Verarbeitet Bilder mit WebODM-CLI (parallele Instanzen möglich)
        
        Args:
            project_path: Pfad zum Projekt-Verzeichnis
            images_path: Pfad zu den Eingabebildern
            options: Verarbeitungsoptionen
            instance_id: Eindeutige Instanz-ID für parallele Verarbeitung
            
        Returns:
            Dict mit Verarbeitungsstatus und Ergebnissen
        """
        if not self.webodm_cli_path:
            if not await self.install_webodm_cli():
                raise Exception("WebODM-CLI nicht verfügbar und Installation fehlgeschlagen")
                
        try:
            project_path = Path(project_path)
            
            # Eindeutige Verzeichnisse für parallele Instanzen
            instance_suffix = f"_{instance_id}" if instance_id else ""
            output_path = project_path / f"output{instance_suffix}"
            temp_path = project_path / f"temp{instance_suffix}"
            log_path = project_path / "logs" / f"processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}{instance_suffix}.log"
            
            # Verzeichnisse erstellen
            output_path.mkdir(parents=True, exist_ok=True)
            temp_path.mkdir(parents=True, exist_ok=True)
            
            # Standard-Optionen für Drohnenfotografie
            default_options = {
                "dem": True,
                "orthophoto": True,
                "dsm": True,
                "dtm": True,
                "mesh-octree-depth": 11,
                "mesh-size": 200000,
                "orthophoto-resolution": 5,
                "dem-resolution": 5,
                "feature-quality": "high",
                "pc-quality": "high",
                "texturing-data-term": "area",
                "auto-boundary": True,
                # Parallele Verarbeitung optimieren
                "max-concurrency": "auto",  # WebODM nutzt verfügbare CPU-Kerne
                "rerun-all": False,  # Keine Neuverarbeitung bei Restart
                "fast-orthophoto": False  # Qualität vor Geschwindigkeit
            }
            
            if options:
                default_options.update(options)
                
            # Eindeutiger Projekt-Name für parallele Instanzen
            project_name = f"{project_path.name}{instance_suffix}"
            
            # WebODM-CLI Befehl zusammenstellen
            cmd = [
                self.webodm_cli_path,
                "process",
                "--project", project_name,
                "--images", images_path,
                "--output", str(output_path),
                "--temp", str(temp_path)  # Separates Temp-Verzeichnis
            ]
            
            # Optionen hinzufügen
            for key, value in default_options.items():
                if value is True:
                    cmd.append(f"--{key}")
                elif value is not False and value is not None:
                    cmd.extend([f"--{key}", str(value)])
                    
            logger.info(f"Starte WebODM-CLI Instanz {instance_id}: {' '.join(cmd)}")
            
            # Status-Datei erstellen (instanz-spezifisch)
            status_file = project_path / f"processing_status{instance_suffix}.json"
            await self._update_status(status_file, "running", f"Verarbeitung gestartet (Instanz {instance_id})", 0)
            
            # Prozess starten mit separatem Working Directory
            working_dir = temp_path
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(working_dir),
                env={**os.environ, "TMPDIR": str(temp_path)}  # Separate Temp-Verzeichnisse
            )
            
            # Log-Datei für Output
            with open(log_path, 'w') as log_file:
                # Output in Echtzeit lesen und Status aktualisieren
                async for line in self._read_process_output(process):
                    log_file.write(line + '\n')
                    log_file.flush()
                    
                    # Fortschritt aus Log parsen
                    progress = self._parse_progress(line)
                    if progress is not None:
                        await self._update_status(status_file, "running", line.strip(), progress)
                        
            # Auf Prozess-Ende warten
            return_code = await process.wait()
            
            if return_code == 0:
                # Erfolgreiche Verarbeitung
                results = await self._collect_results(output_path)
                await self._update_status(status_file, "completed", f"Verarbeitung erfolgreich abgeschlossen (Instanz {instance_id})", 100)
                
                # Potree-Viewer vorbereiten falls Punktwolke vorhanden
                if results.get("point_cloud"):
                    await self._prepare_potree_viewer(project_path, results["point_cloud"])
                
                # Temp-Verzeichnis aufräumen
                if temp_path.exists():
                    import shutil
                    shutil.rmtree(temp_path)
                    
                return {
                    "status": "completed",
                    "message": f"Verarbeitung erfolgreich abgeschlossen (Instanz {instance_id})",
                    "results": results,
                    "log_file": str(log_path),
                    "instance_id": instance_id
                }
            else:
                # Fehler bei Verarbeitung
                await self._update_status(status_file, "failed", f"Verarbeitung fehlgeschlagen (Instanz {instance_id})", 0)
                return {
                    "status": "failed",
                    "message": f"WebODM-CLI Verarbeitung fehlgeschlagen (Instanz {instance_id})",
                    "return_code": return_code,
                    "log_file": str(log_path),
                    "instance_id": instance_id
                }
                
        except Exception as e:
            logger.error(f"Fehler bei WebODM-CLI Verarbeitung (Instanz {instance_id}): {e}")
            if 'status_file' in locals():
                await self._update_status(status_file, "failed", f"Fehler: {str(e)}", 0)
            raise
            
    async def _read_process_output(self, process):
        """Liest Prozess-Output zeilenweise"""
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            yield line.decode().strip()
            
    def _parse_progress(self, line: str) -> Optional[int]:
        """Parst Fortschritt aus WebODM-CLI Output"""
        # Verschiedene Progress-Patterns
        patterns = [
            r'(\d+)%',  # Direkte Prozentangabe
            r'(\d+)/(\d+)',  # Schritt x von y
            r'Progress: (\d+)',  # Progress: x
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                if '/' in pattern:
                    # x/y Format
                    current, total = map(int, match.groups())
                    return int((current / total) * 100)
                else:
                    # Direkte Prozentangabe
                    return int(match.group(1))
                    
        return None
        
    async def _update_status(self, status_file: Path, status: str, message: str, progress: int):
        """Aktualisiert Status-Datei"""
        status_data = {
            "status": status,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
            
    async def _collect_results(self, output_path: Path) -> Dict[str, Any]:
        """Sammelt Verarbeitungsergebnisse"""
        results = {}
        
        # Suche nach generierten Dateien
        file_patterns = {
            "orthophoto": ["orthophoto.tif", "orthophoto.jpg"],
            "dem": ["dem.tif"],
            "dsm": ["dsm.tif"], 
            "dtm": ["dtm.tif"],
            "point_cloud": ["point_cloud.ply", "point_cloud.las"],
            "mesh": ["mesh.ply", "mesh.obj"],
            "texture": ["texture.jpg", "texture.png"]
        }
        
        for result_type, patterns in file_patterns.items():
            for pattern in patterns:
                result_file = output_path / pattern
                if result_file.exists():
                    results[result_type] = str(result_file)
                    break
                    
        return results
        
    async def _prepare_potree_viewer(self, project_path: Path, point_cloud_path: str):
        """Bereitet Potree-Viewer für Punktwolke vor"""
        try:
            viewer_path = project_path / "viewer"
            viewer_path.mkdir(exist_ok=True)
            
            # Potree-Konverter aufrufen (falls verfügbar)
            potree_converter = shutil.which("PotreeConverter")
            if potree_converter:
                cmd = [
                    potree_converter,
                    "-i", point_cloud_path,
                    "-o", str(viewer_path),
                    "--generate-page", "index.html"
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.wait()
                
                if process.returncode == 0:
                    logger.info("Potree-Viewer erfolgreich vorbereitet")
                else:
                    logger.warning("Potree-Konvertierung fehlgeschlagen")
            else:
                logger.warning("PotreeConverter nicht gefunden - Viewer-Vorbereitung übersprungen")
                
        except Exception as e:
            logger.error(f"Fehler bei Potree-Viewer Vorbereitung: {e}")
            
    async def get_processing_status(self, project_path: str) -> Dict[str, Any]:
        """Ruft aktuellen Verarbeitungsstatus ab"""
        try:
            status_file = Path(project_path) / "processing_status.json"
            
            if status_file.exists():
                with open(status_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "status": "not_started",
                    "message": "Verarbeitung noch nicht gestartet",
                    "progress": 0
                }
                
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Verarbeitungsstatus: {e}")
            return {
                "status": "error",
                "message": f"Fehler beim Statusabruf: {str(e)}",
                "progress": 0
            }
            
    async def cleanup_project(self, project_path: str, keep_results: bool = True):
        """Räumt Projekt-Verzeichnis auf"""
        try:
            project_path = Path(project_path)
            
            # Eingabebilder löschen (Speicherplatz sparen)
            images_path = project_path / "images"
            if images_path.exists():
                shutil.rmtree(images_path)
                logger.info(f"Eingabebilder gelöscht: {images_path}")
                
            # Temporäre Dateien löschen
            temp_files = project_path.glob("*.tmp")
            for temp_file in temp_files:
                temp_file.unlink()
                
            if not keep_results:
                # Komplettes Projekt löschen
                shutil.rmtree(project_path)
                logger.info(f"Projekt komplett gelöscht: {project_path}")
            else:
                logger.info(f"Projekt aufgeräumt, Ergebnisse behalten: {project_path}")
                
        except Exception as e:
            logger.error(f"Fehler beim Aufräumen des Projekts: {e}")
            
    async def list_available_options(self) -> Dict[str, Any]:
        """Listet verfügbare WebODM-CLI Optionen auf"""
        if not self.webodm_cli_path:
            return {}
            
        try:
            # WebODM-CLI Help aufrufen
            process = await asyncio.create_subprocess_exec(
                self.webodm_cli_path, "process", "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            help_text = stdout.decode()
            
            # Optionen aus Help-Text parsen
            options = {}
            for line in help_text.split('\n'):
                if line.strip().startswith('--'):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        option_name = parts[0][2:]  # Remove --
                        description = ' '.join(parts[1:])
                        options[option_name] = description
                        
            return options
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der WebODM-CLI Optionen: {e}")
            return {}


# Globale Service-Instanz
webodm_cli_service = WebODMCLIService()


async def get_webodm_cli_service() -> WebODMCLIService:
    """Dependency für FastAPI"""
    return webodm_cli_service