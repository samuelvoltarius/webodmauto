"""
ChiliView Datenbank-Models
SQLAlchemy Models für alle Entitäten der mehrmandantenfähigen Plattform
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class Admin(Base):
    """
    Admin-Benutzer mit vollständigen Systemrechten
    Kann alle Reseller und User verwalten, Impersonation durchführen
    """
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Beziehungen
    audit_logs = relationship("AuditLog", back_populates="admin")

class Reseller(Base):
    """
    Reseller-Entität mit eigener Datenbank und Branding
    Jeder Reseller hat eine separate SQLite-Datenbank
    """
    __tablename__ = "resellers"
    
    id = Column(Integer, primary_key=True, index=True)
    reseller_id = Column(String(50), unique=True, index=True, nullable=False)  # URL-freundliche ID
    company_name = Column(String(100), nullable=False)
    contact_email = Column(String(100), nullable=False)
    contact_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Branding-Einstellungen
    logo_url = Column(String(255))
    primary_color = Column(String(7), default="#007bff")  # Hex-Farbe
    secondary_color = Column(String(7), default="#6c757d")
    welcome_message = Column(Text)
    custom_css = Column(Text)
    custom_html = Column(Text)
    
    # Rechtliche Angaben
    imprint = Column(Text)
    privacy_policy = Column(Text)
    homepage_url = Column(String(255))
    
    # Konfiguration
    allow_self_registration = Column(Boolean, default=False)
    max_upload_size_mb = Column(Integer, default=1024)  # 1GB Standard
    max_projects_per_user = Column(Integer, default=10)
    
    # Status und Metadaten
    is_active = Column(Boolean, default=True, nullable=False)
    database_path = Column(String(255), nullable=False)  # Pfad zur Reseller-DB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Beziehungen
    audit_logs = relationship("AuditLog", back_populates="reseller")

class User(Base):
    """
    End-User innerhalb eines Resellers
    Gespeichert in der jeweiligen Reseller-Datenbank
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True, nullable=False)
    email = Column(String(100), index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    
    # Benutzer-Limits
    max_projects = Column(Integer, default=10)
    max_upload_size_mb = Column(Integer, default=1024)
    
    # DSGVO-relevante Felder
    gdpr_consent = Column(Boolean, default=False, nullable=False)
    gdpr_consent_date = Column(DateTime(timezone=True))
    data_retention_until = Column(DateTime(timezone=True))
    
    # Status und Metadaten
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Beziehungen
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")

class Project(Base):
    """
    Fotoverarbeitungsprojekt eines Users
    Enthält Upload-Daten und Verarbeitungsstatus
    """
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_uuid = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Beziehung zum User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Upload-Informationen
    original_filename = Column(String(255))
    file_size_bytes = Column(Integer)
    file_count = Column(Integer, default=0)
    upload_path = Column(String(500))
    
    # Verarbeitungsstatus
    status = Column(String(20), default="uploaded")  # uploaded, processing, completed, failed
    webodm_task_id = Column(String(100))
    progress_percentage = Column(Float, default=0.0)
    processing_started_at = Column(DateTime(timezone=True))
    processing_completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    
    # Viewer-Informationen
    viewer_path = Column(String(500))  # Pfad zum Potree-Viewer
    viewer_url = Column(String(500))   # URL zum Viewer
    
    # Metadaten
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Beziehungen
    user = relationship("User", back_populates="projects")
    processing_logs = relationship("ProcessingLog", back_populates="project", cascade="all, delete-orphan")

class ProcessingLog(Base):
    """
    Verarbeitungsprotokoll für WebODM-CLI Aufgaben
    Speichert detaillierte Logs der Modellberechnung
    """
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Log-Daten
    log_level = Column(String(10), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    step = Column(String(50))  # z.B. "feature_extraction", "meshing", "texturing"
    progress = Column(Float)
    
    # Zeitstempel
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Beziehungen
    project = relationship("Project", back_populates="processing_logs")

class AuditLog(Base):
    """
    Audit-Log für alle sicherheitsrelevanten Aktionen
    Speichert Impersonation, Uploads, Löschungen, etc.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Akteur (wer hat die Aktion durchgeführt)
    admin_id = Column(Integer, ForeignKey("admins.id"))
    reseller_id = Column(Integer, ForeignKey("resellers.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Aktion
    action = Column(String(50), nullable=False)  # login, upload, delete, impersonate, etc.
    resource_type = Column(String(50))  # user, project, reseller
    resource_id = Column(String(100))
    
    # Details
    description = Column(Text)
    ip_address = Column(String(45))  # IPv6-kompatibel
    user_agent = Column(String(500))
    
    # Impersonation-spezifisch
    original_admin_id = Column(Integer, ForeignKey("admins.id"))
    impersonated_user_type = Column(String(20))  # admin, reseller, user
    impersonated_user_id = Column(String(50))
    
    # Zeitstempel
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Beziehungen
    admin = relationship("Admin", back_populates="audit_logs", foreign_keys=[admin_id])
    reseller = relationship("Reseller", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    original_admin = relationship("Admin", foreign_keys=[original_admin_id])

class SystemConfig(Base):
    """
    Systemweite Konfigurationseinstellungen
    Speichert globale Parameter und Feature-Flags
    """
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    
    # Metadaten
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BackupRecord(Base):
    """
    Backup-Aufzeichnungen für Reseller-Datenbanken
    Verfolgt erstellte und wiederhergestellte Backups
    """
    __tablename__ = "backup_records"
    
    id = Column(Integer, primary_key=True, index=True)
    reseller_id = Column(Integer, ForeignKey("resellers.id"), nullable=False)
    
    # Backup-Details
    backup_type = Column(String(20), nullable=False)  # full, incremental
    backup_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer)
    
    # Status
    status = Column(String(20), default="created")  # created, restored, deleted, failed
    created_by_admin_id = Column(Integer, ForeignKey("admins.id"))
    
    # Zeitstempel
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    restored_at = Column(DateTime(timezone=True))
    
    # Beziehungen
    reseller = relationship("Reseller")
    created_by = relationship("Admin")

class VirusScanResult(Base):
    """
    Ergebnisse der Virenscans für hochgeladene Dateien
    Speichert ClamAV-Scan-Resultate
    """
    __tablename__ = "virus_scan_results"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256
    
    # Scan-Ergebnis
    is_clean = Column(Boolean, nullable=False)
    threat_name = Column(String(100))
    scan_engine_version = Column(String(50))
    
    # Zeitstempel
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())