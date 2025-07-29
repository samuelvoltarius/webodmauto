"""
ChiliView Authentifizierungs-Handler
JWT-basierte Authentifizierung mit Impersonation-Funktionalität
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
import os
from enum import Enum

from database.database import get_database, get_reseller_database, db_manager
from database.models import Admin, Reseller, User, AuditLog
from .password_handler import PasswordHandler

logger = structlog.get_logger(__name__)

# JWT Konfiguration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 Stunden

security = HTTPBearer()

class UserRole(str, Enum):
    """
    Benutzerrollen im System
    """
    ADMIN = "admin"
    RESELLER = "reseller"
    USER = "user"

class AuthHandler:
    """
    Hauptklasse für Authentifizierung und Autorisierung
    Verwaltet JWT-Tokens, Login, Logout und Impersonation
    """
    
    def __init__(self):
        self.password_handler = PasswordHandler()
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Erstellt einen JWT Access Token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            logger.info("JWT Token erstellt", user_id=data.get("sub"), role=data.get("role"))
            return encoded_jwt
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des JWT Tokens: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token-Erstellung fehlgeschlagen"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verifiziert und dekodiert einen JWT Token
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Token-Gültigkeit prüfen
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token abgelaufen"
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT Verifikation fehlgeschlagen: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ungültiger Token"
            )
    
    async def authenticate_admin(self, username: str, password: str, db) -> Optional[Admin]:
        """
        Authentifiziert einen Admin-Benutzer
        """
        try:
            # Admin in zentraler DB suchen
            admin = db.query(Admin).filter(
                (Admin.username == username) | (Admin.email == username)
            ).first()
            
            if not admin:
                logger.warning("Admin-Login fehlgeschlagen: Benutzer nicht gefunden", username=username)
                return None
            
            if not admin.is_active:
                logger.warning("Admin-Login fehlgeschlagen: Benutzer deaktiviert", username=username)
                return None
            
            # Passwort prüfen
            if not self.password_handler.verify_password(password, admin.password_hash):
                logger.warning("Admin-Login fehlgeschlagen: Falsches Passwort", username=username)
                return None
            
            # Last login aktualisieren
            admin.last_login = datetime.utcnow()
            db.commit()
            
            logger.info("Admin erfolgreich authentifiziert", admin_id=admin.id, username=admin.username)
            return admin
            
        except Exception as e:
            logger.error(f"Fehler bei Admin-Authentifizierung: {str(e)}")
            return None
    
    async def authenticate_reseller(self, username: str, password: str, db) -> Optional[Reseller]:
        """
        Authentifiziert einen Reseller-Benutzer
        """
        try:
            # Reseller in zentraler DB suchen
            reseller = db.query(Reseller).filter(
                (Reseller.reseller_id == username) | (Reseller.contact_email == username)
            ).first()
            
            if not reseller:
                logger.warning("Reseller-Login fehlgeschlagen: Benutzer nicht gefunden", username=username)
                return None
            
            if not reseller.is_active:
                logger.warning("Reseller-Login fehlgeschlagen: Benutzer deaktiviert", username=username)
                return None
            
            # Passwort prüfen
            if not self.password_handler.verify_password(password, reseller.password_hash):
                logger.warning("Reseller-Login fehlgeschlagen: Falsches Passwort", username=username)
                return None
            
            # Last login aktualisieren
            reseller.last_login = datetime.utcnow()
            db.commit()
            
            logger.info("Reseller erfolgreich authentifiziert", reseller_id=reseller.reseller_id)
            return reseller
            
        except Exception as e:
            logger.error(f"Fehler bei Reseller-Authentifizierung: {str(e)}")
            return None
    
    async def authenticate_user(self, username: str, password: str, reseller_id: str) -> Optional[User]:
        """
        Authentifiziert einen End-User in der Reseller-Datenbank
        """
        try:
            # Reseller-DB Session holen
            reseller_db = get_reseller_database(reseller_id)
            
            # User in Reseller-DB suchen
            user = reseller_db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                logger.warning("User-Login fehlgeschlagen: Benutzer nicht gefunden", 
                             username=username, reseller_id=reseller_id)
                reseller_db.close()
                return None
            
            if not user.is_active:
                logger.warning("User-Login fehlgeschlagen: Benutzer deaktiviert", 
                             username=username, reseller_id=reseller_id)
                reseller_db.close()
                return None
            
            # Passwort prüfen
            if not self.password_handler.verify_password(password, user.password_hash):
                logger.warning("User-Login fehlgeschlagen: Falsches Passwort", 
                             username=username, reseller_id=reseller_id)
                reseller_db.close()
                return None
            
            # Last login aktualisieren
            user.last_login = datetime.utcnow()
            reseller_db.commit()
            reseller_db.close()
            
            logger.info("User erfolgreich authentifiziert", 
                       user_id=user.id, username=user.username, reseller_id=reseller_id)
            return user
            
        except Exception as e:
            logger.error(f"Fehler bei User-Authentifizierung: {str(e)}")
            return None
    
    async def login(self, username: str, password: str, reseller_id: Optional[str] = None, 
                   request: Optional[Request] = None) -> Dict[str, Any]:
        """
        Universelle Login-Funktion für alle Benutzertypen
        """
        db = get_database()
        
        try:
            # Audit-Log Daten sammeln
            ip_address = request.client.host if request else "unknown"
            user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"
            
            # 1. Admin-Login versuchen (nur wenn kein reseller_id angegeben)
            if not reseller_id:
                admin = await self.authenticate_admin(username, password, db)
                if admin:
                    # JWT Token erstellen
                    token_data = {
                        "sub": str(admin.id),
                        "username": admin.username,
                        "email": admin.email,
                        "role": UserRole.ADMIN,
                        "full_name": admin.full_name
                    }
                    
                    access_token = self.create_access_token(token_data)
                    
                    # Audit-Log erstellen
                    await self.log_audit_action(
                        db, "login", admin_id=admin.id, 
                        description=f"Admin-Login erfolgreich",
                        ip_address=ip_address, user_agent=user_agent
                    )
                    
                    return {
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": {
                            "id": admin.id,
                            "username": admin.username,
                            "email": admin.email,
                            "full_name": admin.full_name,
                            "role": UserRole.ADMIN
                        }
                    }
                
                # 2. Reseller-Login versuchen
                reseller = await self.authenticate_reseller(username, password, db)
                if reseller:
                    # JWT Token erstellen
                    token_data = {
                        "sub": reseller.reseller_id,
                        "username": reseller.reseller_id,
                        "email": reseller.contact_email,
                        "role": UserRole.RESELLER,
                        "company_name": reseller.company_name,
                        "reseller_id": reseller.reseller_id
                    }
                    
                    access_token = self.create_access_token(token_data)
                    
                    # Audit-Log erstellen
                    await self.log_audit_action(
                        db, "login", reseller_id=reseller.id,
                        description=f"Reseller-Login erfolgreich",
                        ip_address=ip_address, user_agent=user_agent
                    )
                    
                    return {
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": {
                            "id": reseller.id,
                            "username": reseller.reseller_id,
                            "email": reseller.contact_email,
                            "company_name": reseller.company_name,
                            "role": UserRole.RESELLER,
                            "reseller_id": reseller.reseller_id
                        }
                    }
            
            # 3. User-Login (nur mit reseller_id)
            if reseller_id:
                user = await self.authenticate_user(username, password, reseller_id)
                if user:
                    # JWT Token erstellen
                    token_data = {
                        "sub": str(user.id),
                        "username": user.username,
                        "email": user.email,
                        "role": UserRole.USER,
                        "full_name": user.full_name,
                        "reseller_id": reseller_id
                    }
                    
                    access_token = self.create_access_token(token_data)
                    
                    # Audit-Log in Reseller-DB erstellen
                    reseller_db = get_reseller_database(reseller_id)
                    await self.log_audit_action(
                        reseller_db, "login", user_id=user.id,
                        description=f"User-Login erfolgreich",
                        ip_address=ip_address, user_agent=user_agent
                    )
                    reseller_db.close()
                    
                    return {
                        "access_token": access_token,
                        "token_type": "bearer",
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "full_name": user.full_name,
                            "role": UserRole.USER,
                            "reseller_id": reseller_id
                        }
                    }
            
            # Login fehlgeschlagen
            logger.warning("Login fehlgeschlagen", username=username, reseller_id=reseller_id)
            
            # Fehlgeschlagenen Login loggen
            await self.log_audit_action(
                db, "login_failed", 
                description=f"Login fehlgeschlagen für {username}",
                ip_address=ip_address, user_agent=user_agent
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ungültige Anmeldedaten"
            )
            
        finally:
            db.close()
    
    async def impersonate_user(self, admin_token: str, target_user_type: str, 
                              target_user_id: str, reseller_id: Optional[str] = None,
                              request: Optional[Request] = None) -> Dict[str, Any]:
        """
        Admin-Impersonation: Als anderer Benutzer einloggen
        """
        # Admin-Token verifizieren
        admin_payload = self.verify_token(admin_token)
        
        if admin_payload.get("role") != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nur Admins können Impersonation durchführen"
            )
        
        db = get_database()
        
        try:
            admin_id = int(admin_payload.get("sub"))
            admin = db.query(Admin).filter(Admin.id == admin_id).first()
            
            if not admin or not admin.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Admin-Benutzer nicht gefunden oder deaktiviert"
                )
            
            # Audit-Log Daten
            ip_address = request.client.host if request else "unknown"
            user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"
            
            # Je nach Zielbenutzer-Typ impersonieren
            if target_user_type == "reseller":
                reseller = db.query(Reseller).filter(Reseller.reseller_id == target_user_id).first()
                if not reseller:
                    raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
                
                # Impersonation-Token erstellen
                token_data = {
                    "sub": reseller.reseller_id,
                    "username": reseller.reseller_id,
                    "email": reseller.contact_email,
                    "role": UserRole.RESELLER,
                    "company_name": reseller.company_name,
                    "reseller_id": reseller.reseller_id,
                    "impersonated_by": admin_id,
                    "original_admin": admin_id
                }
                
                access_token = self.create_access_token(token_data)
                
                # Impersonation loggen
                await self.log_audit_action(
                    db, "impersonate", admin_id=admin_id,
                    description=f"Admin impersoniert Reseller {target_user_id}",
                    ip_address=ip_address, user_agent=user_agent,
                    original_admin_id=admin_id,
                    impersonated_user_type="reseller",
                    impersonated_user_id=target_user_id
                )
                
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "impersonation": True,
                    "original_admin_id": admin_id,
                    "user": {
                        "id": reseller.id,
                        "username": reseller.reseller_id,
                        "email": reseller.contact_email,
                        "company_name": reseller.company_name,
                        "role": UserRole.RESELLER,
                        "reseller_id": reseller.reseller_id
                    }
                }
            
            elif target_user_type == "user" and reseller_id:
                reseller_db = get_reseller_database(reseller_id)
                user = reseller_db.query(User).filter(User.id == int(target_user_id)).first()
                
                if not user:
                    reseller_db.close()
                    raise HTTPException(status_code=404, detail="User nicht gefunden")
                
                # Impersonation-Token erstellen
                token_data = {
                    "sub": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "role": UserRole.USER,
                    "full_name": user.full_name,
                    "reseller_id": reseller_id,
                    "impersonated_by": admin_id,
                    "original_admin": admin_id
                }
                
                access_token = self.create_access_token(token_data)
                
                # Impersonation loggen (in beiden DBs)
                await self.log_audit_action(
                    db, "impersonate", admin_id=admin_id,
                    description=f"Admin impersoniert User {target_user_id} in Reseller {reseller_id}",
                    ip_address=ip_address, user_agent=user_agent,
                    original_admin_id=admin_id,
                    impersonated_user_type="user",
                    impersonated_user_id=target_user_id
                )
                
                await self.log_audit_action(
                    reseller_db, "impersonate", user_id=user.id,
                    description=f"Admin {admin_id} impersoniert User",
                    ip_address=ip_address, user_agent=user_agent,
                    original_admin_id=admin_id
                )
                
                reseller_db.close()
                
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "impersonation": True,
                    "original_admin_id": admin_id,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": UserRole.USER,
                        "reseller_id": reseller_id
                    }
                }
            
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ungültiger Benutzertyp für Impersonation"
                )
                
        finally:
            db.close()
    
    async def end_impersonation(self, token: str, request: Optional[Request] = None) -> Dict[str, Any]:
        """
        Beendet Impersonation und kehrt zum ursprünglichen Admin zurück
        """
        payload = self.verify_token(token)
        
        original_admin_id = payload.get("original_admin")
        if not original_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keine aktive Impersonation gefunden"
            )
        
        db = get_database()
        
        try:
            admin = db.query(Admin).filter(Admin.id == original_admin_id).first()
            if not admin:
                raise HTTPException(status_code=404, detail="Ursprünglicher Admin nicht gefunden")
            
            # Neuen Admin-Token erstellen
            token_data = {
                "sub": str(admin.id),
                "username": admin.username,
                "email": admin.email,
                "role": UserRole.ADMIN,
                "full_name": admin.full_name
            }
            
            access_token = self.create_access_token(token_data)
            
            # Impersonation-Ende loggen
            ip_address = request.client.host if request else "unknown"
            user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"
            
            await self.log_audit_action(
                db, "end_impersonation", admin_id=admin.id,
                description="Impersonation beendet, zurück zu Admin",
                ip_address=ip_address, user_agent=user_agent
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "impersonation": False,
                "user": {
                    "id": admin.id,
                    "username": admin.username,
                    "email": admin.email,
                    "full_name": admin.full_name,
                    "role": UserRole.ADMIN
                }
            }
            
        finally:
            db.close()
    
    async def log_audit_action(self, db, action: str, admin_id: Optional[int] = None,
                              reseller_id: Optional[int] = None, user_id: Optional[int] = None,
                              description: Optional[str] = None, ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None, resource_type: Optional[str] = None,
                              resource_id: Optional[str] = None, original_admin_id: Optional[int] = None,
                              impersonated_user_type: Optional[str] = None,
                              impersonated_user_id: Optional[str] = None):
        """
        Erstellt einen Audit-Log-Eintrag
        """
        try:
            audit_log = AuditLog(
                admin_id=admin_id,
                reseller_id=reseller_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                original_admin_id=original_admin_id,
                impersonated_user_type=impersonated_user_type,
                impersonated_user_id=impersonated_user_id
            )
            
            db.add(audit_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Audit-Logs: {str(e)}")
            db.rollback()

# Globale Instanz
auth_handler = AuthHandler()

# Dependency für geschützte Routen
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency zur Benutzer-Authentifizierung
    Extrahiert und verifiziert JWT Token aus Authorization Header
    """
    try:
        payload = auth_handler.verify_token(credentials.credentials)
        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Benutzer-Authentifizierung: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentifizierung fehlgeschlagen"
        )

# Role-basierte Dependencies
async def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency die Admin-Rechte erfordert
    """
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin-Rechte erforderlich"
        )
    return current_user

async def require_reseller(current_user: dict = Depends(get_current_user)):
    """
    Dependency die Reseller-Rechte erfordert
    """
    if current_user.get("role") not in [UserRole.ADMIN, UserRole.RESELLER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reseller-Rechte erforderlich"
        )
    return current_user

async def require_user(current_user: dict = Depends(get_current_user)):
    """
    Dependency die User-Rechte erfordert (alle authentifizierten Benutzer)
    """
    return current_user