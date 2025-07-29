"""
ChiliView Logging-Konfiguration
Strukturiertes Logging mit structlog für bessere Nachverfolgbarkeit
"""

import logging
import structlog
import sys
from pathlib import Path
from datetime import datetime
import os

def setup_logging():
    """
    Konfiguriert strukturiertes Logging für die gesamte Anwendung
    """
    
    # Log-Verzeichnis erstellen
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Log-Level aus Umgebungsvariable
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Timestamper für strukturierte Logs
    timestamper = structlog.processors.TimeStamper(fmt="ISO")
    
    # Shared processors für alle Logger
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Entwicklungsumgebung: Farbige Konsolen-Ausgabe
    if os.getenv("ENVIRONMENT", "development") == "development":
        shared_processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
    else:
        # Produktion: JSON-Format
        shared_processors.append(
            structlog.processors.JSONRenderer()
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
    
    # File Handler für alle Logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "chiliview.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Error-spezifischer File Handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "chiliview_errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    
    # Audit-spezifischer File Handler
    audit_handler = logging.handlers.RotatingFileHandler(
        log_dir / "chiliview_audit.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=20,
        encoding="utf-8"
    )
    audit_handler.setLevel(logging.INFO)
    
    # Formatter für File Handler
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    error_handler.setFormatter(file_formatter)
    audit_handler.setFormatter(file_formatter)
    
    # Root Logger konfigurieren
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
        handlers=[console_handler, file_handler, error_handler]
    )
    
    # Audit Logger separat konfigurieren
    audit_logger = logging.getLogger("audit")
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)
    
    # Externe Libraries auf WARNING setzen
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Structlog konfigurieren
    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Startup-Log
    logger = structlog.get_logger("chiliview.startup")
    logger.info(
        "Logging konfiguriert",
        log_level=log_level,
        log_dir=str(log_dir),
        environment=os.getenv("ENVIRONMENT", "development")
    )

class AuditLogger:
    """
    Spezieller Logger für Audit-Events
    Protokolliert sicherheitsrelevante Aktionen
    """
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_login(self, user_id: str, user_type: str, success: bool, 
                  ip_address: str = None, user_agent: str = None, 
                  additional_info: dict = None):
        """
        Loggt Login-Versuche
        """
        self.logger.info(
            "Login-Versuch",
            event_type="login",
            user_id=user_id,
            user_type=user_type,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_info=additional_info or {}
        )
    
    def log_impersonation(self, admin_id: str, target_user_id: str, 
                         target_user_type: str, action: str,
                         ip_address: str = None, user_agent: str = None):
        """
        Loggt Impersonation-Aktionen
        """
        self.logger.info(
            "Impersonation",
            event_type="impersonation",
            admin_id=admin_id,
            target_user_id=target_user_id,
            target_user_type=target_user_type,
            action=action,  # start, end
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def log_data_access(self, user_id: str, user_type: str, resource_type: str,
                       resource_id: str, action: str, ip_address: str = None):
        """
        Loggt Datenzugriffe
        """
        self.logger.info(
            "Datenzugriff",
            event_type="data_access",
            user_id=user_id,
            user_type=user_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,  # read, write, delete
            ip_address=ip_address
        )
    
    def log_file_upload(self, user_id: str, project_id: str, file_count: int,
                       total_size: int, ip_address: str = None):
        """
        Loggt Datei-Uploads
        """
        self.logger.info(
            "Datei-Upload",
            event_type="file_upload",
            user_id=user_id,
            project_id=project_id,
            file_count=file_count,
            total_size_bytes=total_size,
            ip_address=ip_address
        )
    
    def log_admin_action(self, admin_id: str, action: str, target_type: str,
                        target_id: str, details: dict = None,
                        ip_address: str = None):
        """
        Loggt Admin-Aktionen
        """
        self.logger.info(
            "Admin-Aktion",
            event_type="admin_action",
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip_address
        )
    
    def log_security_event(self, event_type: str, severity: str, description: str,
                          user_id: str = None, ip_address: str = None,
                          additional_data: dict = None):
        """
        Loggt Sicherheitsereignisse
        """
        self.logger.warning(
            "Sicherheitsereignis",
            event_type="security",
            security_event_type=event_type,
            severity=severity,  # low, medium, high, critical
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            additional_data=additional_data or {}
        )
    
    def log_system_event(self, event_type: str, description: str,
                        component: str = None, additional_data: dict = None):
        """
        Loggt System-Events
        """
        self.logger.info(
            "System-Event",
            event_type="system",
            system_event_type=event_type,
            description=description,
            component=component,
            additional_data=additional_data or {}
        )

class PerformanceLogger:
    """
    Logger für Performance-Metriken
    """
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_request_timing(self, method: str, path: str, duration_ms: float,
                          status_code: int, user_id: str = None):
        """
        Loggt Request-Timing
        """
        self.logger.info(
            "Request-Timing",
            method=method,
            path=path,
            duration_ms=duration_ms,
            status_code=status_code,
            user_id=user_id
        )
    
    def log_database_query(self, query_type: str, table: str, duration_ms: float,
                          rows_affected: int = None):
        """
        Loggt Datenbank-Query-Performance
        """
        self.logger.debug(
            "Database-Query",
            query_type=query_type,
            table=table,
            duration_ms=duration_ms,
            rows_affected=rows_affected
        )
    
    def log_file_operation(self, operation: str, file_path: str, 
                          file_size_bytes: int, duration_ms: float):
        """
        Loggt Datei-Operationen
        """
        self.logger.debug(
            "File-Operation",
            operation=operation,
            file_path=file_path,
            file_size_bytes=file_size_bytes,
            duration_ms=duration_ms
        )
    
    def log_webodm_processing(self, project_id: str, stage: str, 
                             duration_ms: float, success: bool):
        """
        Loggt WebODM-Verarbeitungszeiten
        """
        self.logger.info(
            "WebODM-Processing",
            project_id=project_id,
            stage=stage,
            duration_ms=duration_ms,
            success=success
        )

class SecurityLogger:
    """
    Spezieller Logger für Sicherheitsereignisse
    """
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_failed_login(self, username: str, ip_address: str, 
                        user_agent: str = None, reason: str = None):
        """
        Loggt fehlgeschlagene Login-Versuche
        """
        self.logger.warning(
            "Fehlgeschlagener Login",
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            reason=reason,
            severity="medium"
        )
    
    def log_suspicious_activity(self, user_id: str, activity: str, 
                               ip_address: str, details: dict = None):
        """
        Loggt verdächtige Aktivitäten
        """
        self.logger.warning(
            "Verdächtige Aktivität",
            user_id=user_id,
            activity=activity,
            ip_address=ip_address,
            details=details or {},
            severity="high"
        )
    
    def log_virus_detection(self, file_path: str, threat_name: str,
                           user_id: str = None, ip_address: str = None):
        """
        Loggt Virus-Erkennungen
        """
        self.logger.error(
            "Virus erkannt",
            file_path=file_path,
            threat_name=threat_name,
            user_id=user_id,
            ip_address=ip_address,
            severity="critical"
        )
    
    def log_unauthorized_access(self, user_id: str, resource: str,
                               ip_address: str, attempted_action: str):
        """
        Loggt unbefugte Zugriffe
        """
        self.logger.warning(
            "Unbefugter Zugriff",
            user_id=user_id,
            resource=resource,
            ip_address=ip_address,
            attempted_action=attempted_action,
            severity="high"
        )
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str,
                               limit: int, window_seconds: int):
        """
        Loggt Rate-Limit-Überschreitungen
        """
        self.logger.warning(
            "Rate-Limit überschritten",
            ip_address=ip_address,
            endpoint=endpoint,
            limit=limit,
            window_seconds=window_seconds,
            severity="medium"
        )

# Globale Logger-Instanzen
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()

def get_request_logger(request_id: str = None):
    """
    Erstellt einen Request-spezifischen Logger
    """
    logger = structlog.get_logger("chiliview.request")
    if request_id:
        logger = logger.bind(request_id=request_id)
    return logger

def log_startup_info():
    """
    Loggt Startup-Informationen
    """
    logger = structlog.get_logger("chiliview.startup")
    
    logger.info(
        "ChiliView Backend gestartet",
        version="1.0.0",
        python_version=sys.version,
        environment=os.getenv("ENVIRONMENT", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )

def log_shutdown_info():
    """
    Loggt Shutdown-Informationen
    """
    logger = structlog.get_logger("chiliview.shutdown")
    
    logger.info(
        "ChiliView Backend wird heruntergefahren",
        timestamp=datetime.utcnow().isoformat()
    )