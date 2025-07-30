# ChiliView iFrame Integration & 3D-Viewer Dokumentation

## Übersicht

ChiliView bietet eine vollständige iFrame-Integration für 3D-Viewer, die es ermöglicht, verarbeitete Photogrammetrie-Projekte nahtlos in Dashboards und externe Anwendungen einzubetten.

## 3D-Viewer Integration

### Backend-Implementierung

#### Viewer Router (`backend/routers/viewer.py`)

Der Viewer-Router stellt die Hauptfunktionalität für die 3D-Viewer-Integration bereit:

```python
@router.get("/{reseller_id}/{project_id}/")
async def serve_viewer(reseller_id: str, project_id: int)
```

**Funktionen:**
- Automatische Erkennung von 3D-Assets (Potree, Punktwolken, Orthophotos)
- Sichere Dateizugriffskontrolle mit Pfad-Traversal-Schutz
- Dynamische HTML-Generierung für verschiedene Viewer-Typen
- Unterstützung für Potree, Three.js und Cesium

**Unterstützte Formate:**
- **Potree**: `.js` Dateien (automatische Erkennung)
- **Punktwolken**: `.las`, `.laz`, `.ply`, `.xyz`
- **Orthophotos**: `.tif`, `.tiff`, `.jpg`, `.png`
- **Textured Models**: `textured_model.zip` (automatische Extraktion)

#### Asset-Verarbeitung

```python
def detect_3d_assets(project_path: Path) -> Dict[str, Any]
```

Diese Funktion erkennt automatisch verfügbare 3D-Assets:

1. **Potree-Erkennung**: Sucht nach `.js` Dateien im Projektverzeichnis
2. **Punktwolken-Erkennung**: Findet alle unterstützten Punktwolken-Formate
3. **Orthophoto-Erkennung**: Lokalisiert Orthophotos und Luftbilder
4. **Textured Model**: Extrahiert und verarbeitet 3D-Modelle

### Frontend-Implementierung

#### Projects View (`frontend/src/views/user/Projects.vue`)

Die Projekt-Übersicht zeigt eingebettete 3D-Viewer für abgeschlossene Projekte:

```vue
<iframe 
    :src="`/api/viewer/${project.reseller_id}/${project.id}/`"
    class="w-full h-64 border-0 rounded-lg"
    :title="`3D-Viewer für ${project.name}`"
    @load="onViewerLoad(project.id)"
    @error="onViewerError(project.id)"
></iframe>
```

**Features:**
- Eingebettete iFrame-Viewer für alle abgeschlossenen Projekte
- Automatisches Laden und Fehlerbehandlung
- Responsive Design mit Tailwind CSS
- Vollbild-Modus verfügbar

#### Project Detail View (`frontend/src/views/user/ProjectDetail.vue`)

Die Detail-Ansicht bietet erweiterte Viewer-Funktionalität:

```vue
<div class="bg-gray-900 relative" style="height: 600px;">
    <iframe 
        ref="viewerFrame"
        :src="`/api/viewer/${project.reseller_id}/${project.id}/`"
        class="w-full h-full border-0"
        :title="`3D-Viewer für ${project.name}`"
        @load="onViewerLoad"
        @error="onViewerError"
    ></iframe>
</div>
```

**Erweiterte Features:**
- Größerer Viewer (600px Höhe)
- Vollbild-Funktionalität
- Neuer Tab öffnen
- Lade- und Fehler-Overlays
- Viewer-Neustart-Funktion

## iFrame-Anzeige Standorte

### 1. Projekt-Übersicht (`/user/:userId/projects`)

**Wo:** Hauptprojekt-Dashboard
**Größe:** 256px Höhe (h-64)
**Zweck:** Schnelle Vorschau aller abgeschlossenen Projekte
**Features:**
- Grid-Layout mit mehreren Projekten
- Kompakte Darstellung
- Direkte Navigation zu Detail-Ansicht

### 2. Projekt-Details (`/user/:userId/projects/:projectId`)

**Wo:** Dedizierte Projekt-Detail-Seite
**Größe:** 600px Höhe
**Zweck:** Vollständige 3D-Analyse und Interaktion
**Features:**
- Vollbild-Modus
- Neuer Tab öffnen
- Erweiterte Viewer-Kontrollen
- Projekt-Informationen und Logs

### 3. Dashboard-Integration (geplant)

**Wo:** User/Reseller Dashboards
**Größe:** Konfigurierbar
**Zweck:** Schnellzugriff auf aktuelle Projekte

## Technische Details

### URL-Struktur

```
/api/viewer/{reseller_id}/{project_id}/
```

**Parameter:**
- `reseller_id`: Eindeutige Reseller-Kennung
- `project_id`: Numerische Projekt-ID

### Sicherheit

1. **Authentifizierung**: Alle Viewer-Zugriffe erfordern gültige JWT-Token
2. **Autorisierung**: Benutzer können nur eigene Projekte anzeigen
3. **Pfad-Schutz**: Verhindert Directory-Traversal-Angriffe
4. **CORS**: Konfiguriert für sichere Cross-Origin-Requests

### Asset-Pfade

```
/data/resellers/{reseller_id}/projects/{project_id}/results/
├── potree/           # Potree-Viewer Dateien
├── pointclouds/      # Punktwolken (.las, .laz, .ply)
├── orthophotos/      # Orthophotos und Luftbilder
└── textured_model/   # 3D-Modelle (extrahiert)
```

## Viewer-Typen

### 1. Potree Viewer

**Verwendung:** Große Punktwolken (>1M Punkte)
**Format:** Potree-Octree-Struktur
**Features:**
- Level-of-Detail (LOD)
- Messtools
- Schnitte und Filter
- Annotations

### 2. Three.js Viewer

**Verwendung:** Kleinere Punktwolken und 3D-Modelle
**Format:** PLY, XYZ, OBJ
**Features:**
- WebGL-Rendering
- Orbit-Controls
- Material-Darstellung

### 3. Orthophoto Viewer

**Verwendung:** 2D-Orthophotos
**Format:** TIFF, JPEG, PNG
**Features:**
- Zoom und Pan
- Overlay-Funktionen
- Messtools

## Deployment-Konfiguration

### Nginx-Konfiguration

```nginx
location /api/viewer/ {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Erhöhte Timeouts für große 3D-Dateien
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}
```

### Docker-Volumes

```yaml
volumes:
  - ./data:/app/data  # Projekt-Daten und 3D-Assets
  - ./uploads:/app/uploads  # Upload-Verzeichnis
```

## Performance-Optimierung

### 1. Asset-Caching

- Browser-Caching für statische 3D-Assets
- CDN-Integration möglich
- Komprimierung für große Dateien

### 2. Lazy Loading

- iFrames laden nur bei Sichtbarkeit
- Progressive Asset-Loading
- Thumbnail-Generierung

### 3. Responsive Design

- Automatische Größenanpassung
- Mobile-optimierte Viewer
- Touch-Gesten-Unterstützung

## Fehlerbehandlung

### 1. Asset-Fehler

```javascript
const onViewerError = (projectId) => {
    console.error(`Viewer-Fehler für Projekt ${projectId}`)
    // Fallback auf Thumbnail oder Fehlermeldung
}
```

### 2. Lade-Timeouts

```javascript
const viewerTimeout = setTimeout(() => {
    if (viewerLoading.value) {
        viewerError.value = true
        viewerLoading.value = false
    }
}, 30000) // 30 Sekunden Timeout
```

### 3. Netzwerk-Probleme

- Automatische Wiederholung
- Offline-Modus mit Thumbnails
- Benutzerfreundliche Fehlermeldungen

## API-Endpoints

### Viewer-Endpoints

```python
GET /api/viewer/{reseller_id}/{project_id}/
# Hauptviewer-HTML

GET /api/viewer/{reseller_id}/{project_id}/assets/{asset_path}
# Statische 3D-Assets

GET /api/viewer/{reseller_id}/{project_id}/info
# Projekt-Metadaten und Asset-Informationen
```

### Projekt-Endpoints

```python
GET /api/projects/{project_id}
# Projekt-Details mit Viewer-Status

GET /api/projects/{project_id}/thumbnail
# Projekt-Thumbnail für Vorschau
```

## Entwicklung und Testing

### Lokale Entwicklung

```bash
# Backend starten
cd local_dev
python -m uvicorn backend.main:app --reload --port 8000

# Frontend starten
cd frontend
npm run dev
```

### Testing

```bash
# Viewer-Integration testen
curl http://localhost:8000/api/viewer/demo/1/

# Asset-Verfügbarkeit prüfen
curl http://localhost:8000/api/viewer/demo/1/info
```

## Zukünftige Erweiterungen

### 1. Erweiterte Viewer-Features

- VR/AR-Unterstützung
- Kollaborative Annotations
- Echtzeit-Messungen
- Export-Funktionen

### 2. Dashboard-Integration

- Widget-basierte Viewer
- Drag-and-Drop-Layout
- Benutzerdefinierte Dashboards

### 3. API-Erweiterungen

- Viewer-Konfiguration per API
- Benutzerdefinierte Viewer-Themes
- Plugin-System für Viewer-Erweiterungen

## Troubleshooting

### Häufige Probleme

1. **iFrame lädt nicht:**
   - JWT-Token prüfen
   - Netzwerk-Konnektivität testen
   - Browser-Konsole auf Fehler prüfen

2. **3D-Assets nicht gefunden:**
   - Projekt-Verarbeitung abgeschlossen?
   - Asset-Pfade korrekt?
   - Dateiberechtigungen prüfen

3. **Performance-Probleme:**
   - Asset-Größe reduzieren
   - Browser-Cache leeren
   - Hardware-Beschleunigung aktivieren

### Debug-Modus

```javascript
// Frontend Debug
localStorage.setItem('chiliview_debug', 'true')

// Backend Debug
export CHILIVIEW_DEBUG=true
```

## Fazit

Die ChiliView iFrame-Integration bietet eine vollständige Lösung für die Einbettung von 3D-Viewern in Web-Anwendungen. Mit automatischer Asset-Erkennung, sicherer Authentifizierung und responsivem Design ist sie ideal für professionelle Photogrammetrie-Workflows geeignet.

Die iFrames werden an zwei Hauptstandorten angezeigt:
1. **Projekt-Übersicht**: Kompakte Vorschau aller Projekte
2. **Projekt-Details**: Vollständiger Viewer mit erweiterten Funktionen

Die Implementierung ist skalierbar, sicher und benutzerfreundlich, mit umfassender Fehlerbehandlung und Performance-Optimierung.