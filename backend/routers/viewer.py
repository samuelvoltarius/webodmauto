"""
ChiliView Viewer Router
API-Endpunkte für Potree-Viewer Integration und 3D-Modell-Anzeige
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import structlog
import os
import json
from pathlib import Path
import zipfile
import shutil

from auth.auth_handler import require_user, get_current_user
from database.database import get_reseller_database, get_database
from database.models import User, Project, Reseller

logger = structlog.get_logger(__name__)
router = APIRouter()

# Pydantic Models
class ViewerConfigResponse(BaseModel):
    """Viewer-Konfiguration"""
    viewer_url: str
    project_name: str
    project_id: int
    point_cloud_url: Optional[str]
    mesh_url: Optional[str]
    orthophoto_url: Optional[str]
    viewer_type: str

class PotreeViewer:
    """
    Potree-Viewer Integration
    Verwaltet 3D-Punktwolken und Mesh-Anzeige
    """
    
    def __init__(self):
        self.potree_path = Path("viewer/potree")
        self.ensure_potree_installation()
    
    def ensure_potree_installation(self):
        """
        Stellt sicher, dass Potree installiert ist
        """
        if not self.potree_path.exists():
            logger.info("Potree wird installiert...")
            self.install_potree()
    
    def install_potree(self):
        """
        Installiert Potree-Viewer
        """
        try:
            import urllib.request
            import tempfile
            
            # Potree von GitHub herunterladen
            potree_url = "https://github.com/potree/potree/releases/download/1.8/potree_1.8.zip"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                urllib.request.urlretrieve(potree_url, temp_file.name)
                
                # Potree extrahieren
                self.potree_path.parent.mkdir(parents=True, exist_ok=True)
                
                with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                    zip_ref.extractall(self.potree_path.parent)
                
                # Verzeichnis umbenennen falls nötig
                extracted_dirs = [d for d in self.potree_path.parent.iterdir() if d.is_dir() and 'potree' in d.name.lower()]
                if extracted_dirs and extracted_dirs[0] != self.potree_path:
                    extracted_dirs[0].rename(self.potree_path)
                
                os.unlink(temp_file.name)
                
                logger.info("Potree erfolgreich installiert")
                
        except Exception as e:
            logger.error(f"Fehler bei Potree-Installation: {str(e)}")
            
            # Fallback: Minimale Potree-Struktur erstellen
            self.create_minimal_potree()
    
    def create_minimal_potree(self):
        """
        Erstellt eine minimale Potree-Struktur
        """
        try:
            self.potree_path.mkdir(parents=True, exist_ok=True)
            
            # Basis-HTML für Potree
            potree_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="description" content="">
    <meta name="author" content="">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>ChiliView 3D Viewer</title>
    
    <link rel="stylesheet" type="text/css" href="./libs/potree/potree.css">
    <link rel="stylesheet" type="text/css" href="./libs/jquery-ui/jquery-ui.min.css">
    <link rel="stylesheet" type="text/css" href="./libs/openlayers3/ol.css">
    <link rel="stylesheet" type="text/css" href="./libs/spectrum/spectrum.css">
    <link rel="stylesheet" type="text/css" href="./libs/jstree/themes/mixed/style.css">
</head>

<body>
    <script src="./libs/jquery/jquery-3.1.1.min.js"></script>
    <script src="./libs/spectrum/spectrum.js"></script>
    <script src="./libs/jquery-ui/jquery-ui.min.js"></script>
    <script src="./libs/other/BinaryHeap.js"></script>
    <script src="./libs/tween/tween.min.js"></script>
    <script src="./libs/d3/d3.js"></script>
    <script src="./libs/proj4/proj4.js"></script>
    <script src="./libs/openlayers3/ol.js"></script>
    <script src="./libs/i18next/i18next.js"></script>
    <script src="./libs/jstree/jstree.js"></script>
    <script src="./libs/potree/potree.js"></script>
    
    <div class="potree_container" style="position: absolute; width: 100%; height: 100%; left: 0px; top: 0px; ">
        <div id="potree_render_area" style="background-image: url('./resources/images/background.jpg');"></div>
        <div id="potree_sidebar_container"> </div>
    </div>

    <script>
        window.viewer = new Potree.Viewer(document.getElementById("potree_render_area"));
        
        viewer.setEDLEnabled(true);
        viewer.setFOV(60);
        viewer.setPointBudget(1*1000*1000);
        viewer.loadSettingsFromURL();
        
        viewer.setDescription("ChiliView 3D Model");
        
        // Load point cloud if available
        if(window.pointCloudUrl) {
            Potree.loadPointCloud(window.pointCloudUrl, "pointcloud", function(e){
                let pointcloud = e.pointcloud;
                let material = pointcloud.material;
                material.size = 1;
                material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
                material.shape = Potree.PointShape.SQUARE;
                material.activeAttributeName = "rgba";
                
                viewer.scene.addPointCloud(pointcloud);
                viewer.fitToScreen();
            });
        }
        
        // Error handling
        viewer.addEventListener("error", function(e) {
            console.error("Potree error:", e);
            document.getElementById("potree_render_area").innerHTML = 
                '<div style="padding: 20px; color: white; background: rgba(0,0,0,0.8);">' +
                '<h2>3D-Viewer Fehler</h2>' +
                '<p>Das 3D-Modell konnte nicht geladen werden.</p>' +
                '<p>Mögliche Ursachen:</p>' +
                '<ul>' +
                '<li>Die Verarbeitung ist noch nicht abgeschlossen</li>' +
                '<li>Es ist ein Fehler bei der Modellgenerierung aufgetreten</li>' +
                '<li>Die Modelldateien sind beschädigt</li>' +
                '</ul>' +
                '</div>';
        });
    </script>
</body>
</html>
"""
            
            with open(self.potree_path / "viewer.html", "w", encoding="utf-8") as f:
                f.write(potree_html)
            
            # CSS-Datei erstellen
            css_content = """
body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

.potree_container {
    background: #000;
}

#potree_render_area {
    background-size: cover;
    background-position: center;
}

.error-message {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
}
"""
            
            css_dir = self.potree_path / "libs" / "potree"
            css_dir.mkdir(parents=True, exist_ok=True)
            
            with open(css_dir / "potree.css", "w") as f:
                f.write(css_content)
            
            logger.info("Minimale Potree-Struktur erstellt")
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der minimalen Potree-Struktur: {str(e)}")
    
    def prepare_project_viewer(self, project: Project, reseller_id: str) -> Dict[str, Any]:
        """
        Bereitet den Viewer für ein Projekt vor
        """
        try:
            project_viewer_dir = Path(f"data/resellers/{reseller_id}/projects/{project.id}/viewer")
            project_viewer_dir.mkdir(parents=True, exist_ok=True)
            
            # Potree-Dateien in Projekt-Verzeichnis kopieren
            if self.potree_path.exists():
                for item in self.potree_path.iterdir():
                    if item.is_file():
                        shutil.copy2(item, project_viewer_dir)
                    elif item.is_dir():
                        shutil.copytree(item, project_viewer_dir / item.name, dirs_exist_ok=True)
            
            # Projekt-spezifische Viewer-HTML erstellen
            viewer_config = self.create_project_viewer_html(project, reseller_id)
            
            with open(project_viewer_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(viewer_config["html"])
            
            return {
                "viewer_path": str(project_viewer_dir),
                "viewer_url": f"/viewer/{reseller_id}/{project.id}/",
                "config": viewer_config
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Vorbereiten des Projekt-Viewers: {str(e)}")
            raise
    
    def create_project_viewer_html(self, project: Project, reseller_id: str) -> Dict[str, Any]:
        """
        Erstellt projekt-spezifische Viewer-HTML
        """
        # Verfügbare Dateien ermitteln
        output_dir = Path(project.viewer_path) if project.viewer_path else None
        
        point_cloud_url = None
        mesh_url = None
        orthophoto_url = None
        
        if output_dir and output_dir.exists():
            # Punktwolke suchen
            for ext in ['.las', '.laz', '.ply', '.xyz']:
                pc_files = list(output_dir.glob(f"*{ext}"))
                if pc_files:
                    point_cloud_url = f"./output/{pc_files[0].name}"
                    break
            
            # Mesh suchen
            mesh_files = list(output_dir.glob("textured_model.zip"))
            if mesh_files:
                # ZIP extrahieren für Web-Zugriff
                mesh_dir = output_dir / "mesh"
                mesh_dir.mkdir(exist_ok=True)
                
                try:
                    with zipfile.ZipFile(mesh_files[0], 'r') as zip_ref:
                        zip_ref.extractall(mesh_dir)
                    
                    # OBJ-Datei suchen
                    obj_files = list(mesh_dir.glob("*.obj"))
                    if obj_files:
                        mesh_url = f"./output/mesh/{obj_files[0].name}"
                except:
                    pass
            
            # Orthophoto suchen
            ortho_files = list(output_dir.glob("orthophoto.*"))
            if ortho_files:
                orthophoto_url = f"./output/{ortho_files[0].name}"
        
        # HTML generieren
        html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChiliView - {project.name}</title>
    
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #000;
            color: white;
        }}
        
        .viewer-container {{
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        
        .viewer-header {{
            background: rgba(0, 0, 0, 0.8);
            padding: 10px 20px;
            border-bottom: 1px solid #333;
            z-index: 1000;
        }}
        
        .viewer-content {{
            flex: 1;
            position: relative;
            overflow: hidden;
        }}
        
        .viewer-frame {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .loading-message {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            background: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 5px;
        }}
        
        .error-message {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            background: rgba(139, 0, 0, 0.8);
            padding: 20px;
            border-radius: 5px;
            max-width: 500px;
        }}
        
        .controls {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0, 0, 0, 0.7);
            padding: 10px;
            border-radius: 5px;
            z-index: 1000;
        }}
        
        .control-button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            margin: 2px;
            border-radius: 3px;
            cursor: pointer;
        }}
        
        .control-button:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="viewer-container">
        <div class="viewer-header">
            <h2 style="margin: 0;">{project.name}</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.8;">
                3D-Modell | Erstellt am {project.created_at.strftime('%d.%m.%Y %H:%M')}
            </p>
        </div>
        
        <div class="viewer-content">
            <div class="controls">
                <button class="control-button" onclick="resetView()">Ansicht zurücksetzen</button>
                <button class="control-button" onclick="toggleFullscreen()">Vollbild</button>
            </div>
            
            <div id="loading" class="loading-message">
                <h3>3D-Modell wird geladen...</h3>
                <p>Bitte warten Sie einen Moment.</p>
            </div>
            
            <div id="error" class="error-message" style="display: none;">
                <h3>Fehler beim Laden des 3D-Modells</h3>
                <p>Das 3D-Modell konnte nicht geladen werden.</p>
                <p><strong>Mögliche Ursachen:</strong></p>
                <ul style="text-align: left;">
                    <li>Die Verarbeitung ist noch nicht abgeschlossen</li>
                    <li>Es ist ein Fehler bei der Modellgenerierung aufgetreten</li>
                    <li>Die Modelldateien sind beschädigt oder unvollständig</li>
                </ul>
                <button class="control-button" onclick="location.reload()">Neu laden</button>
            </div>
            
            <iframe id="viewer-frame" class="viewer-frame" src="./viewer.html" style="display: none;"></iframe>
        </div>
    </div>
    
    <script>
        // Viewer-Konfiguration
        window.projectConfig = {{
            projectId: {project.id},
            projectName: "{project.name}",
            pointCloudUrl: {json.dumps(point_cloud_url)},
            meshUrl: {json.dumps(mesh_url)},
            orthophotoUrl: {json.dumps(orthophoto_url)}
        }};
        
        // Viewer laden
        setTimeout(function() {{
            const iframe = document.getElementById('viewer-frame');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            
            iframe.onload = function() {{
                loading.style.display = 'none';
                iframe.style.display = 'block';
                
                // Konfiguration an Iframe weiterleiten
                try {{
                    iframe.contentWindow.postMessage(window.projectConfig, '*');
                }} catch(e) {{
                    console.warn('Konnte Konfiguration nicht an Viewer weiterleiten:', e);
                }}
            }};
            
            iframe.onerror = function() {{
                loading.style.display = 'none';
                error.style.display = 'block';
            }};
            
            // Timeout für Fehlerbehandlung
            setTimeout(function() {{
                if (loading.style.display !== 'none') {{
                    loading.style.display = 'none';
                    error.style.display = 'block';
                }}
            }}, 30000); // 30 Sekunden Timeout
        }}, 1000);
        
        // Steuerungsfunktionen
        function resetView() {{
            const iframe = document.getElementById('viewer-frame');
            try {{
                iframe.contentWindow.postMessage({{action: 'resetView'}}, '*');
            }} catch(e) {{
                console.warn('Konnte Ansicht nicht zurücksetzen:', e);
            }}
        }}
        
        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        }}
        
        // Tastatur-Shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'F11') {{
                e.preventDefault();
                toggleFullscreen();
            }} else if (e.key === 'r' || e.key === 'R') {{
                resetView();
            }}
        }});
    </script>
</body>
</html>
"""
        
        return {
            "html": html_content,
            "point_cloud_url": point_cloud_url,
            "mesh_url": mesh_url,
            "orthophoto_url": orthophoto_url
        }

# Globale Instanz
potree_viewer = PotreeViewer()

@router.get("/{reseller_id}/{project_id}/")
async def serve_project_viewer(
    reseller_id: str,
    project_id: int,
    current_user: dict = Depends(require_user)
):
    """
    Serviert den 3D-Viewer für ein Projekt
    """
    try:
        user_id = int(current_user.get("sub"))
        user_reseller_id = current_user.get("reseller_id")
        
        # Berechtigung prüfen
        if user_reseller_id != reseller_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff auf fremde Projekte nicht erlaubt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # Projekt laden
            query = reseller_db.query(Project).filter(Project.id == project_id)
            
            # User-Berechtigung prüfen (außer für Admin)
            if current_user.get("role") != "admin":
                query = query.filter(Project.user_id == user_id)
            
            project = query.first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
            if project.status != "completed":
                # Spezielle Seite für nicht abgeschlossene Projekte
                return HTMLResponse(content=f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChiliView - {project.name}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 50px auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .status-icon {{
            font-size: 48px;
            margin-bottom: 20px;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: #007bff;
            transition: width 0.3s ease;
        }}
        .refresh-button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
        }}
        .refresh-button:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="status-icon">
            {'⏳' if project.status == 'processing' else '📤' if project.status == 'uploaded' else '❌'}
        </div>
        <h2>{project.name}</h2>
        <p><strong>Status:</strong> {
            'Wird verarbeitet...' if project.status == 'processing' 
            else 'Hochgeladen, wartet auf Verarbeitung' if project.status == 'uploaded'
            else 'Verarbeitung fehlgeschlagen'
        }</p>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {project.progress_percentage}%"></div>
        </div>
        <p>{project.progress_percentage:.1f}% abgeschlossen</p>
        
        {f'<p style="color: red;"><strong>Fehler:</strong> {project.error_message}</p>' if project.error_message else ''}
        
        <button class="refresh-button" onclick="location.reload()">Aktualisieren</button>
        
        <script>
            // Auto-refresh alle 30 Sekunden bei laufender Verarbeitung
            {f'setTimeout(() => location.reload(), 30000);' if project.status in ['uploaded', 'processing'] else ''}
        </script>
    </div>
</body>
</html>
                """)
            
            # Viewer vorbereiten falls noch nicht geschehen
            viewer_dir = Path(f"data/resellers/{reseller_id}/projects/{project_id}/viewer")
            if not viewer_dir.exists() or not (viewer_dir / "index.html").exists():
                viewer_config = potree_viewer.prepare_project_viewer(project, reseller_id)
                
                # Viewer-URL in Projekt speichern
                if not project.viewer_url:
                    project.viewer_url = viewer_config["viewer_url"]
                    reseller_db.commit()
            
            # Viewer-HTML servieren
            viewer_html_path = viewer_dir / "index.html"
            if viewer_html_path.exists():
                return FileResponse(str(viewer_html_path), media_type="text/html")
            else:
                raise HTTPException(status_code=404, detail="Viewer nicht verfügbar")
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Servieren des Viewers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Viewer konnte nicht geladen werden"
        )

@router.get("/{reseller_id}/{project_id}/config", response_model=ViewerConfigResponse)
async def get_viewer_config(
    reseller_id: str,
    project_id: int,
    current_user: dict = Depends(require_user)
):
    """
    Ruft die Viewer-Konfiguration für ein Projekt ab
    """
    try:
        user_id = int(current_user.get("sub"))
        user_reseller_id = current_user.get("reseller_id")
        
        # Berechtigung prüfen
        if user_reseller_id != reseller_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff auf fremde Projekte nicht erlaubt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # Projekt laden
            query = reseller_db.query(Project).filter(Project.id == project_id)
            
            # User-Berechtigung prüfen (außer für Admin)
            if current_user.get("role") != "admin":
                query = query.filter(Project.user_id == user_id)
            
            project = query.first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
            if project.status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Projekt noch nicht abgeschlossen"
                )
            
            # Verfügbare Dateien ermitteln
            output_dir = Path(project.viewer_path) if project.viewer_path else None
            
            point_cloud_url = None
            mesh_url = None
            orthophoto_url = None
            
            if output_dir and output_dir.exists():
                # URLs für verfügbare Assets generieren
                base_url = f"/viewer/{reseller_id}/{project_id}/output/"
                
                # Punktwolke
                for ext in ['.las', '.laz', '.ply', '.xyz']:
                    pc_files = list(output_dir.glob(f"*{ext}"))
                    if pc_files:
                        point_cloud_url = base_url + pc_files[0].name
                        break
                
                # Mesh
                mesh_files = list(output_dir.glob("mesh/*.obj"))
                if mesh_files:
                    mesh_url = base_url + f"mesh/{mesh_files[0].name}"
                
                # Orthophoto
                ortho_files = list(output_dir.glob("orthophoto.*"))
                if ortho_files:
                    orthophoto_url = base_url + ortho_files[0].name
            
            return ViewerConfigResponse(
                viewer_url=project.viewer_url or f"/viewer/{reseller_id}/{project_id}/",
                project_name=project.name,
                project_id=project.id,
                point_cloud_url=point_cloud_url,
                mesh_url=mesh_url,
                orthophoto_url=orthophoto_url,
                viewer_type="potree"
            )
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Viewer-Konfiguration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Viewer-Konfiguration konnte nicht abgerufen werden"
        )

@router.get("/{reseller_id}/{project_id}/output/{file_path:path}")
async def serve_output_file(
    reseller_id: str,
    project_id: int,
    file_path: str,
    current_user: dict = Depends(require_user)
):
    """
    Serviert Output-Dateien für den Viewer
    """
    try:
        user_id = int(current_user.get("sub"))
        user_reseller_id = current_user.get("reseller_id")
        
        # Berechtigung prüfen
        if user_reseller_id != reseller_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Zugriff auf fremde Projekte nicht erlaubt"
            )
        
        reseller_db = get_reseller_database(reseller_id)
        
        try:
            # Projekt laden
            query = reseller_db.query(Project).filter(Project.id == project_id)
            
            # User-Berechtigung prüfen (außer für Admin)
            if current_user.get("role") != "admin":
                query = query.filter(Project.user_id == user_id)
            
            project = query.first()
            
            if not project:
                raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
            
            # Sicherheitsprüfung: Nur Dateien im Output-Verzeichnis
            if ".." in file_path or file_path.startswith("/"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Ungültiger Dateipfad"
                )
            
            # Datei-Pfad konstruieren
            output_dir = Path(project.viewer_path) if project.viewer_path else None
            if not output_dir or not output_dir.exists():
                raise HTTPException(status_code=404, detail="Output-Verzeichnis nicht gefunden")
            
            file_full_path = output_dir / file_path
            
            # Prüfen ob Datei existiert und im erlaubten Verzeichnis liegt
            if not file_full_path.exists():
                raise HTTPException(status_code=404, detail="Datei nicht gefunden")
            
            # Sicherheitsprüfung: Datei muss im Output-Verzeichnis liegen
            try:
                file_full_path.resolve().relative_to(output_dir.resolve())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Zugriff außerhalb des Projektverzeichnisses nicht erlaubt"
                )
            
            # MIME-Type bestimmen
            import mimetypes
            mime_type, _ = mimetypes.guess_type(str(file_full_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            logger.info("Output-Datei serviert",
                       project_id=project_id,
                       file_path=file_path,
                       user_id=user_id)
            
            return FileResponse(
                path=str(file_full_path),
                media_type=mime_type,
                filename=file_full_path.name
            )
            
        finally:
            reseller_db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Servieren der Output-Datei: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Datei konnte nicht geladen werden"
        )

@router.get("/branding/{reseller_id}")
async def get_reseller_branding(reseller_id: str):
    """
    Ruft das Branding für einen Reseller ab (öffentlich zugänglich)
    """
    try:
        db = get_database()
        
        reseller = db.query(Reseller).filter(
            Reseller.reseller_id == reseller_id,
            Reseller.is_active == True
        ).first()
        
        if not reseller:
            raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
        
        return {
            "reseller_id": reseller.reseller_id,
            "company_name": reseller.company_name,
            "logo_url": reseller.logo_url,
            "primary_color": reseller.primary_color,
            "secondary_color": reseller.secondary_color,
            "welcome_message": reseller.welcome_message,
            "homepage_url": reseller.homepage_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Reseller-Brandings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Branding konnte nicht abgerufen werden"
        )
    finally:
        db.close()

@router.get("/health")
async def viewer_health_check():
    """
    Gesundheitscheck für den Viewer-Service
    """
    potree_available = potree_viewer.potree_path.exists()
    
    return {
        "status": "healthy",
        "service": "viewer",
        "version": "1.0.0",
        "potree_available": potree_available,
        "potree_path": str(potree_viewer.potree_path)
    }