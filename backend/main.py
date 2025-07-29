"""
ChiliView Backend API
Hauptanwendung mit FastAPI für mehrmandantenfähige Fotoverarbeitung
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import structlog
import time
from pathlib import Path
import os

# Import der eigenen Module
from database.database import init_database, get_database
from auth.auth_handler import AuthHandler
from routers import admin, reseller, user, auth, upload, viewer, queue
from utils.logging_config import setup_logging
from utils.security import SecurityMiddleware
from services.webodm_cli_service import webodm_cli_service
from services.processing_queue import processing_queue

# Logging konfigurieren
setup_logging()
logger = structlog.get_logger(__name__)

# Sicherheitsschema für JWT
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Anwendungslebenszyklus verwalten
    Initialisiert Datenbank und andere Services beim Start
    """
    logger.info("ChiliView Backend wird gestartet...")
    
    # Datenbank initialisieren
    await init_database()
    
    # Verzeichnisstruktur erstellen
    create_directory_structure()
    
    # WebODM-CLI prüfen
    logger.info("Prüfe WebODM-CLI Verfügbarkeit...")
    if not webodm_cli_service.webodm_cli_path:
        logger.info("WebODM-CLI wird bei Bedarf automatisch installiert")
    else:
        logger.info(f"WebODM-CLI gefunden: {webodm_cli_service.webodm_cli_path}")
    
    # Processing Queue starten
    logger.info("Starte Processing Queue Manager...")
    await processing_queue.start()
    
    logger.info("ChiliView Backend erfolgreich gestartet")
    yield
    
    # Shutdown
    logger.info("ChiliView Backend wird heruntergefahren...")
    
    # Processing Queue stoppen
    await processing_queue.stop()

def create_directory_structure():
    """
    Erstellt die notwendige Verzeichnisstruktur für die Anwendung
    """
    directories = [
        "data",
        "data/resellers",
        "data/webodm_cli",
        "data/redis",
        "data/clamav",
        "logs",
        "uploads",
        "temp",
        "backups",
        "viewer"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Verzeichnis erstellt/überprüft: {directory}")

# FastAPI Anwendung erstellen
app = FastAPI(
    title="ChiliView API",
    description="Mehrmandantenfähige Plattform für Fotoverarbeitung mit WebODM-CLI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Middleware - Produktionsumgebung anpassen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host Middleware für Sicherheit
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*"]  # In Produktion spezifische Hosts
)

# Custom Security Middleware
app.add_middleware(SecurityMiddleware)

# Router einbinden
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(reseller.router, prefix="/api/reseller", tags=["Reseller"])
app.include_router(user.router, prefix="/api/user", tags=["User"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(viewer.router, prefix="/api/viewer", tags=["Viewer"])
app.include_router(queue.router, prefix="/api/queue", tags=["Queue"])

@app.get("/health")
async def health_check():
    """
    Gesundheitscheck für Load Balancer und Monitoring
    """
    return {
        "status": "healthy",
        "service": "chiliview-backend",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def api_health_check():
    """
    API-spezifischer Gesundheitscheck
    """
    try:
        # Datenbankverbindung testen
        db = await get_database()
        
        return {
            "status": "healthy",
            "database": "connected",
            "service": "chiliview-api",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Gesundheitscheck fehlgeschlagen: {str(e)}")
        raise HTTPException(status_code=503, detail="Service nicht verfügbar")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware für Request-Logging
    Protokolliert alle eingehenden Anfragen für Audit-Zwecke
    """
    start_time = time.time()
    
    # Request-Details loggen
    logger.info(
        "HTTP Request",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host,
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    response = await call_next(request)
    
    # Response-Details loggen
    process_time = time.time() - start_time
    logger.info(
        "HTTP Response",
        status_code=response.status_code,
        process_time=f"{process_time:.4f}s"
    )
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Globaler Exception Handler für HTTP-Fehler
    """
    logger.error(
        "HTTP Exception",
        status_code=exc.status_code,
        detail=exc.detail,
        url=str(request.url),
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Globaler Exception Handler für unerwartete Fehler
    """
    logger.error(
        "Unerwarteter Fehler",
        error=str(exc),
        url=str(request.url),
        method=request.method,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Interner Serverfehler",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )