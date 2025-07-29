"""
ChiliView Passwort-Handler
Sichere Passwort-Hashing und -Verifikation mit bcrypt
"""

from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import string
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

class PasswordHandler:
    """
    Verwaltet sichere Passwort-Operationen
    Verwendet bcrypt für Hashing mit konfigurierbaren Rounds
    """
    
    def __init__(self, bcrypt_rounds: int = 12):
        """
        Initialisiert den Password Handler
        
        Args:
            bcrypt_rounds: Anzahl der bcrypt Rounds (Standard: 12)
                          Höhere Werte = sicherer aber langsamer
        """
        self.bcrypt_rounds = bcrypt_rounds
        
        # Passwort-Context mit bcrypt konfigurieren
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=bcrypt_rounds
        )
        
        logger.info(f"PasswordHandler initialisiert mit {bcrypt_rounds} bcrypt rounds")
    
    def hash_password(self, password: str) -> str:
        """
        Hasht ein Passwort mit bcrypt
        
        Args:
            password: Klartext-Passwort
            
        Returns:
            Gehashtes Passwort als String
        """
        try:
            if not password:
                raise ValueError("Passwort darf nicht leer sein")
            
            hashed = self.pwd_context.hash(password)
            logger.debug("Passwort erfolgreich gehasht")
            return hashed
            
        except Exception as e:
            logger.error(f"Fehler beim Hashen des Passworts: {str(e)}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifiziert ein Passwort gegen einen Hash
        
        Args:
            plain_password: Klartext-Passwort
            hashed_password: Gehashtes Passwort aus der Datenbank
            
        Returns:
            True wenn Passwort korrekt, False sonst
        """
        try:
            if not plain_password or not hashed_password:
                return False
            
            is_valid = self.pwd_context.verify(plain_password, hashed_password)
            
            if is_valid:
                logger.debug("Passwort-Verifikation erfolgreich")
            else:
                logger.debug("Passwort-Verifikation fehlgeschlagen")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Fehler bei Passwort-Verifikation: {str(e)}")
            return False
    
    def needs_update(self, hashed_password: str) -> bool:
        """
        Prüft ob ein gehashtes Passwort aktualisiert werden muss
        (z.B. bei geänderten bcrypt rounds)
        
        Args:
            hashed_password: Gehashtes Passwort
            
        Returns:
            True wenn Update nötig, False sonst
        """
        try:
            return self.pwd_context.needs_update(hashed_password)
        except Exception as e:
            logger.error(f"Fehler bei needs_update Prüfung: {str(e)}")
            return False
    
    def generate_secure_password(self, length: int = 16, 
                                include_symbols: bool = True) -> str:
        """
        Generiert ein sicheres zufälliges Passwort
        
        Args:
            length: Länge des Passworts (Standard: 16)
            include_symbols: Ob Sonderzeichen enthalten sein sollen
            
        Returns:
            Zufälliges sicheres Passwort
        """
        try:
            if length < 8:
                raise ValueError("Passwort muss mindestens 8 Zeichen lang sein")
            
            # Zeichensatz definieren
            characters = string.ascii_letters + string.digits
            
            if include_symbols:
                # Sichere Sonderzeichen (keine problematischen für URLs/DB)
                safe_symbols = "!@#$%^&*-_=+[]{}|;:,.<>?"
                characters += safe_symbols
            
            # Sicheres zufälliges Passwort generieren
            password = ''.join(secrets.choice(characters) for _ in range(length))
            
            # Validierung: mindestens ein Buchstabe, eine Zahl
            has_letter = any(c.isalpha() for c in password)
            has_digit = any(c.isdigit() for c in password)
            
            # Falls Validierung fehlschlägt, rekursiv neues Passwort generieren
            if not (has_letter and has_digit):
                return self.generate_secure_password(length, include_symbols)
            
            logger.info(f"Sicheres Passwort generiert (Länge: {length})")
            return password
            
        except Exception as e:
            logger.error(f"Fehler bei Passwort-Generierung: {str(e)}")
            raise
    
    def validate_password_strength(self, password: str) -> dict:
        """
        Validiert die Stärke eines Passworts
        
        Args:
            password: Zu validierendes Passwort
            
        Returns:
            Dictionary mit Validierungsergebnissen
        """
        result = {
            "is_valid": False,
            "score": 0,
            "errors": [],
            "suggestions": []
        }
        
        try:
            if not password:
                result["errors"].append("Passwort darf nicht leer sein")
                return result
            
            # Länge prüfen
            if len(password) < 8:
                result["errors"].append("Passwort muss mindestens 8 Zeichen lang sein")
            elif len(password) >= 12:
                result["score"] += 2
            else:
                result["score"] += 1
                result["suggestions"].append("Längere Passwörter (12+ Zeichen) sind sicherer")
            
            # Zeichentypen prüfen
            has_lower = any(c.islower() for c in password)
            has_upper = any(c.isupper() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_symbol = any(c in "!@#$%^&*-_=+[]{}|;:,.<>?" for c in password)
            
            char_types = sum([has_lower, has_upper, has_digit, has_symbol])
            
            if not has_lower:
                result["errors"].append("Passwort muss mindestens einen Kleinbuchstaben enthalten")
            if not has_upper:
                result["errors"].append("Passwort muss mindestens einen Großbuchstaben enthalten")
            if not has_digit:
                result["errors"].append("Passwort muss mindestens eine Zahl enthalten")
            
            if char_types >= 4:
                result["score"] += 3
            elif char_types >= 3:
                result["score"] += 2
                if not has_symbol:
                    result["suggestions"].append("Sonderzeichen erhöhen die Sicherheit")
            else:
                result["score"] += 1
                result["suggestions"].append("Verwenden Sie verschiedene Zeichentypen")
            
            # Wiederholungen prüfen
            repeated_chars = len(password) - len(set(password))
            if repeated_chars > len(password) * 0.3:  # Mehr als 30% Wiederholungen
                result["score"] -= 1
                result["suggestions"].append("Vermeiden Sie zu viele wiederholte Zeichen")
            
            # Sequenzen prüfen (einfache Implementierung)
            sequences = ["123", "abc", "qwe", "asd", "zxc"]
            for seq in sequences:
                if seq in password.lower():
                    result["score"] -= 1
                    result["suggestions"].append("Vermeiden Sie einfache Sequenzen")
                    break
            
            # Häufige Passwörter prüfen (vereinfacht)
            common_passwords = [
                "password", "123456", "qwerty", "admin", "letmein",
                "welcome", "monkey", "dragon", "master", "shadow"
            ]
            
            if password.lower() in common_passwords:
                result["errors"].append("Dieses Passwort ist zu häufig verwendet")
                result["score"] = 0
            
            # Gesamtbewertung
            if len(result["errors"]) == 0 and result["score"] >= 3:
                result["is_valid"] = True
            
            # Score normalisieren (0-100)
            result["score"] = min(100, max(0, result["score"] * 20))
            
            logger.debug(f"Passwort-Stärke validiert: Score {result['score']}")
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei Passwort-Validierung: {str(e)}")
            result["errors"].append("Fehler bei der Validierung")
            return result
    
    def generate_reset_token(self, length: int = 32) -> str:
        """
        Generiert einen sicheren Token für Passwort-Reset
        
        Args:
            length: Länge des Tokens (Standard: 32)
            
        Returns:
            Sicherer zufälliger Token
        """
        try:
            # URL-sichere Zeichen verwenden
            token = secrets.token_urlsafe(length)
            logger.info(f"Reset-Token generiert (Länge: {len(token)})")
            return token
            
        except Exception as e:
            logger.error(f"Fehler bei Token-Generierung: {str(e)}")
            raise
    
    def hash_token(self, token: str) -> str:
        """
        Hasht einen Token für sichere Speicherung
        Verwendet schnelleres Hashing als für Passwörter
        
        Args:
            token: Zu hashender Token
            
        Returns:
            Gehashter Token
        """
        try:
            import hashlib
            
            # SHA-256 für Token (schneller als bcrypt)
            hashed = hashlib.sha256(token.encode()).hexdigest()
            logger.debug("Token erfolgreich gehasht")
            return hashed
            
        except Exception as e:
            logger.error(f"Fehler beim Token-Hashing: {str(e)}")
            raise
    
    def verify_token(self, token: str, hashed_token: str) -> bool:
        """
        Verifiziert einen Token gegen einen Hash
        
        Args:
            token: Klartext-Token
            hashed_token: Gehashter Token
            
        Returns:
            True wenn Token korrekt, False sonst
        """
        try:
            if not token or not hashed_token:
                return False
            
            # Token hashen und vergleichen
            token_hash = self.hash_token(token)
            is_valid = secrets.compare_digest(token_hash, hashed_token)
            
            if is_valid:
                logger.debug("Token-Verifikation erfolgreich")
            else:
                logger.debug("Token-Verifikation fehlgeschlagen")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Fehler bei Token-Verifikation: {str(e)}")
            return False

# Globale Instanz für die Anwendung
password_handler = PasswordHandler()