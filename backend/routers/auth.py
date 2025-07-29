"""
ChiliView Authentication Router
API-Endpunkte für Login, Logout, Impersonation und Token-Verwaltung
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
import structlog

from auth.auth_handler import auth_handler, get_current_user
from database.database import get_database
from database.models import Admin, Reseller

logger = structlog.get_logger(__name__)
router = APIRouter()
security = HTTPBearer()

# Pydantic Models für Request/Response
class LoginRequest(BaseModel):
    """
    Login-Anfrage für alle Benutzertypen
    """
    username: str
    password: str
    reseller_id: Optional[str] = None  # Für User-Login erforderlich

class LoginResponse(BaseModel):
    """
    Login-Antwort mit Token und Benutzerinformationen
    """
    access_token: str
    token_type: str
    user: dict
    impersonation: Optional[bool] = False
    original_admin_id: Optional[int] = None

class ImpersonationRequest(BaseModel):
    """
    Impersonation-Anfrage für Admin
    """
    target_user_type: str  # "reseller" oder "user"
    target_user_id: str
    reseller_id: Optional[str] = None  # Für User-Impersonation erforderlich

class PasswordChangeRequest(BaseModel):
    """
    Passwort-Änderung-Anfrage
    """
    current_password: str
    new_password: str

class TokenValidationResponse(BaseModel):
    """
    Token-Validierung-Antwort
    """
    valid: bool
    user: Optional[dict] = None
    expires_at: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, request: Request):
    """
    Universeller Login-Endpunkt für Admin, Reseller und User
    
    - **username**: Benutzername oder E-Mail
    - **password**: Passwort
    - **reseller_id**: Erforderlich für User-Login, optional für Admin/Reseller
    """
    try:
        logger.info("Login-Versuch", username=login_data.username, reseller_id=login_data.reseller_id)
        
        result = await auth_handler.login(
            username=login_data.username,
            password=login_data.password,
            reseller_id=login_data.reseller_id,
            request=request
        )
        
        logger.info("Login erfolgreich", username=login_data.username, role=result["user"]["role"])
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim Login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login-Service nicht verfügbar"
        )

@router.post("/impersonate", response_model=LoginResponse)
async def impersonate_user(
    impersonation_data: ImpersonationRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Admin-Impersonation: Als anderer Benutzer einloggen
    
    Nur für Admin-Benutzer verfügbar.
    
    - **target_user_type**: "reseller" oder "user"
    - **target_user_id**: ID des Zielbenutzers
    - **reseller_id**: Erforderlich für User-Impersonation
    """
    try:
        # Admin-Berechtigung prüfen
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Nur Admins können Impersonation durchführen"
            )
        
        # Token aus Request extrahieren
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ungültiger Authorization Header"
            )
        
        token = auth_header.split(" ")[1]
        
        logger.info("Impersonation-Versuch", 
                   admin_id=current_user.get("sub"),
                   target_type=impersonation_data.target_user_type,
                   target_id=impersonation_data.target_user_id)
        
        result = await auth_handler.impersonate_user(
            admin_token=token,
            target_user_type=impersonation_data.target_user_type,
            target_user_id=impersonation_data.target_user_id,
            reseller_id=impersonation_data.reseller_id,
            request=request
        )
        
        logger.info("Impersonation erfolgreich",
                   admin_id=current_user.get("sub"),
                   target_type=impersonation_data.target_user_type,
                   target_id=impersonation_data.target_user_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei Impersonation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Impersonation-Service nicht verfügbar"
        )

@router.post("/end-impersonation", response_model=LoginResponse)
async def end_impersonation(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Beendet aktive Impersonation und kehrt zum ursprünglichen Admin zurück
    
    Nur verfügbar wenn eine aktive Impersonation läuft.
    """
    try:
        # Prüfen ob Impersonation aktiv ist
        if not current_user.get("original_admin"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keine aktive Impersonation gefunden"
            )
        
        # Token aus Request extrahieren
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ungültiger Authorization Header"
            )
        
        token = auth_header.split(" ")[1]
        
        logger.info("Impersonation wird beendet", 
                   current_user_id=current_user.get("sub"),
                   original_admin_id=current_user.get("original_admin"))
        
        result = await auth_handler.end_impersonation(token, request)
        
        logger.info("Impersonation beendet", 
                   admin_id=result["user"]["id"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Beenden der Impersonation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service nicht verfügbar"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Logout-Endpunkt
    
    Invalidiert den aktuellen Token (clientseitig).
    Server-seitige Token-Blacklist könnte hier implementiert werden.
    """
    try:
        logger.info("Logout", 
                   user_id=current_user.get("sub"),
                   role=current_user.get("role"))
        
        # Hier könnte eine Token-Blacklist implementiert werden
        # Für jetzt reicht clientseitiges Token-Löschen
        
        return {
            "message": "Erfolgreich abgemeldet",
            "logged_out": True
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout-Service nicht verfügbar"
        )

@router.get("/validate-token", response_model=TokenValidationResponse)
async def validate_token(current_user: dict = Depends(get_current_user)):
    """
    Validiert den aktuellen Token und gibt Benutzerinformationen zurück
    
    Nützlich für Frontend um Token-Gültigkeit zu prüfen.
    """
    try:
        from datetime import datetime
        
        # Ablaufzeit aus Token extrahieren
        exp_timestamp = current_user.get("exp")
        expires_at = None
        if exp_timestamp:
            expires_at = datetime.fromtimestamp(exp_timestamp).isoformat()
        
        return TokenValidationResponse(
            valid=True,
            user={
                "id": current_user.get("sub"),
                "username": current_user.get("username"),
                "email": current_user.get("email"),
                "role": current_user.get("role"),
                "full_name": current_user.get("full_name"),
                "reseller_id": current_user.get("reseller_id"),
                "impersonated_by": current_user.get("impersonated_by"),
                "original_admin": current_user.get("original_admin")
            },
            expires_at=expires_at
        )
        
    except Exception as e:
        logger.error(f"Fehler bei Token-Validierung: {str(e)}")
        return TokenValidationResponse(valid=False)

@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Ändert das Passwort des aktuell eingeloggten Benutzers
    
    - **current_password**: Aktuelles Passwort zur Verifikation
    - **new_password**: Neues Passwort
    """
    try:
        from auth.password_handler import password_handler
        from database.database import get_reseller_database
        
        user_role = current_user.get("role")
        user_id = current_user.get("sub")
        
        # Passwort-Stärke validieren
        validation = password_handler.validate_password_strength(password_data.new_password)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Passwort entspricht nicht den Sicherheitsanforderungen",
                    "errors": validation["errors"],
                    "suggestions": validation["suggestions"]
                }
            )
        
        db = get_database()
        
        try:
            if user_role == "admin":
                # Admin-Passwort ändern
                admin = db.query(Admin).filter(Admin.id == int(user_id)).first()
                if not admin:
                    raise HTTPException(status_code=404, detail="Admin nicht gefunden")
                
                # Aktuelles Passwort prüfen
                if not password_handler.verify_password(password_data.current_password, admin.password_hash):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Aktuelles Passwort ist falsch"
                    )
                
                # Neues Passwort setzen
                admin.password_hash = password_handler.hash_password(password_data.new_password)
                db.commit()
                
                logger.info("Admin-Passwort geändert", admin_id=admin.id)
                
            elif user_role == "reseller":
                # Reseller-Passwort ändern
                reseller = db.query(Reseller).filter(Reseller.reseller_id == user_id).first()
                if not reseller:
                    raise HTTPException(status_code=404, detail="Reseller nicht gefunden")
                
                # Aktuelles Passwort prüfen
                if not password_handler.verify_password(password_data.current_password, reseller.password_hash):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Aktuelles Passwort ist falsch"
                    )
                
                # Neues Passwort setzen
                reseller.password_hash = password_handler.hash_password(password_data.new_password)
                db.commit()
                
                logger.info("Reseller-Passwort geändert", reseller_id=reseller.reseller_id)
                
            elif user_role == "user":
                # User-Passwort ändern
                reseller_id = current_user.get("reseller_id")
                if not reseller_id:
                    raise HTTPException(status_code=400, detail="Reseller-ID fehlt")
                
                reseller_db = get_reseller_database(reseller_id)
                
                try:
                    from database.models import User
                    user = reseller_db.query(User).filter(User.id == int(user_id)).first()
                    if not user:
                        raise HTTPException(status_code=404, detail="User nicht gefunden")
                    
                    # Aktuelles Passwort prüfen
                    if not password_handler.verify_password(password_data.current_password, user.password_hash):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Aktuelles Passwort ist falsch"
                        )
                    
                    # Neues Passwort setzen
                    user.password_hash = password_handler.hash_password(password_data.new_password)
                    reseller_db.commit()
                    
                    logger.info("User-Passwort geändert", user_id=user.id, reseller_id=reseller_id)
                    
                finally:
                    reseller_db.close()
            
            else:
                raise HTTPException(status_code=400, detail="Ungültige Benutzerrolle")
            
            return {
                "message": "Passwort erfolgreich geändert",
                "changed": True
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Passwort-Ändern: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Passwort-Service nicht verfügbar"
        )

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Gibt Informationen über den aktuell eingeloggten Benutzer zurück
    """
    try:
        return {
            "user": {
                "id": current_user.get("sub"),
                "username": current_user.get("username"),
                "email": current_user.get("email"),
                "role": current_user.get("role"),
                "full_name": current_user.get("full_name"),
                "company_name": current_user.get("company_name"),
                "reseller_id": current_user.get("reseller_id"),
                "impersonated_by": current_user.get("impersonated_by"),
                "original_admin": current_user.get("original_admin")
            }
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Benutzerinformationen: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service nicht verfügbar"
        )

@router.get("/health")
async def auth_health_check():
    """
    Gesundheitscheck für den Auth-Service
    """
    return {
        "status": "healthy",
        "service": "auth",
        "version": "1.0.0"
    }