"""
ChiliView Sicherheits-Utilities
Middleware und Funktionen für Anwendungssicherheit
"""

from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import hashlib
import secrets
from typing import Dict, Set, Optional
from datetime import datetime, timedelta
import structlog
from collections import defaultdict, deque
import re
import ipaddress

logger = structlog.get_logger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Sicherheits-Middleware für FastAPI
    Implementiert Rate-Limiting, Security Headers, IP-Blocking
    """
    
    def __init__(self, app):
        super().__init__(app)
        
        # Rate-Limiting-Speicher
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Dict[str, int] = defaultdict(int)
        
        # Konfiguration
        self.rate_limit_requests = 100  # Requests pro Minute
        self.rate_limit_window = 60     # Sekunden
        self.max_suspicious_score = 10  # Automatisches Blocking
        
        # Erlaubte IPs (Whitelist)
        self.whitelisted_ips = {
            "127.0.0.1",
            "::1",
            "localhost"
        }
        
        # Gefährliche User-Agents
        self.suspicious_user_agents = [
            r".*bot.*",
            r".*crawler.*",
            r".*spider.*",
            r".*scraper.*",
            r".*scanner.*",
            r".*hack.*",
            r".*exploit.*",
            r".*injection.*"
        ]
        
        # Gefährliche Pfade
        self.suspicious_paths = [
            r".*/admin.*",
            r".*/wp-admin.*",
            r".*/phpmyadmin.*",
            r".*\.php$",
            r".*\.asp$",
            r".*\.jsp$",
            r".*\.cgi$",
            r".*\.\./.*",  # Directory traversal
            r".*<script.*",  # XSS attempts
            r".*union.*select.*",  # SQL injection
            r".*drop.*table.*",  # SQL injection
        ]
    
    async def dispatch(self, request: Request, call_next):
        """
        Hauptmiddleware-Funktion
        """
        start_time = time.time()
        client_ip = self.get_client_ip(request)
        
        try:
            # IP-Blocking prüfen
            if self.is_ip_blocked(client_ip):
                logger.warning("Blockierte IP versucht Zugriff", ip=client_ip)
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "IP-Adresse blockiert"}
                )
            
            # Rate-Limiting prüfen
            if not self.check_rate_limit(client_ip):
                self.increase_suspicious_score(client_ip, 2)
                logger.warning("Rate-Limit überschritten", ip=client_ip)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"error": "Zu viele Anfragen"}
                )
            
            # Verdächtige Aktivitäten prüfen
            suspicious_score = self.check_suspicious_activity(request)
            if suspicious_score > 0:
                self.increase_suspicious_score(client_ip, suspicious_score)
            
            # Request verarbeiten
            response = await call_next(request)
            
            # Security Headers hinzufügen
            self.add_security_headers(response)
            
            # Performance-Logging
            process_time = time.time() - start_time
            if process_time > 5.0:  # Langsame Requests loggen
                logger.warning(
                    "Langsamer Request",
                    path=request.url.path,
                    method=request.method,
                    duration=process_time,
                    ip=client_ip
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Fehler in SecurityMiddleware: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Interner Serverfehler"}
            )
    
    def get_client_ip(self, request: Request) -> str:
        """
        Ermittelt die echte Client-IP-Adresse
        """
        # X-Forwarded-For Header (Proxy/Load Balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Erste IP in der Liste ist meist die echte Client-IP
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP Header (Nginx)
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback auf direkte Verbindung
        return request.client.host if request.client else "unknown"
    
    def is_ip_blocked(self, ip: str) -> bool:
        """
        Prüft ob eine IP-Adresse blockiert ist
        """
        if ip in self.whitelisted_ips:
            return False
        
        return ip in self.blocked_ips
    
    def check_rate_limit(self, ip: str) -> bool:
        """
        Prüft Rate-Limiting für eine IP
        """
        if ip in self.whitelisted_ips:
            return True
        
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # Alte Einträge entfernen
        ip_requests = self.rate_limits[ip]
        while ip_requests and ip_requests[0] < window_start:
            ip_requests.popleft()
        
        # Aktuellen Request hinzufügen
        ip_requests.append(now)
        
        # Limit prüfen
        return len(ip_requests) <= self.rate_limit_requests
    
    def check_suspicious_activity(self, request: Request) -> int:
        """
        Prüft auf verdächtige Aktivitäten
        Gibt Suspicious-Score zurück (0 = normal, höher = verdächtiger)
        """
        score = 0
        
        # User-Agent prüfen
        user_agent = request.headers.get("User-Agent", "").lower()
        for pattern in self.suspicious_user_agents:
            if re.match(pattern, user_agent, re.IGNORECASE):
                score += 3
                logger.info("Verdächtiger User-Agent", user_agent=user_agent)
                break
        
        # Pfad prüfen
        path = request.url.path.lower()
        for pattern in self.suspicious_paths:
            if re.match(pattern, path, re.IGNORECASE):
                score += 5
                logger.warning("Verdächtiger Pfad-Zugriff", path=path)
                break
        
        # Query-Parameter prüfen
        query_string = str(request.url.query).lower()
        if any(keyword in query_string for keyword in ["<script", "javascript:", "union select", "drop table", "../"]):
            score += 4
            logger.warning("Verdächtige Query-Parameter", query=query_string)
        
        # HTTP-Method prüfen
        if request.method in ["TRACE", "TRACK", "DEBUG"]:
            score += 2
            logger.info("Ungewöhnliche HTTP-Methode", method=request.method)
        
        # Fehlende Standard-Header
        if not request.headers.get("User-Agent"):
            score += 1
        
        if not request.headers.get("Accept"):
            score += 1
        
        return score
    
    def increase_suspicious_score(self, ip: str, points: int):
        """
        Erhöht den Suspicious-Score für eine IP
        """
        if ip in self.whitelisted_ips:
            return
        
        self.suspicious_ips[ip] += points
        
        if self.suspicious_ips[ip] >= self.max_suspicious_score:
            self.block_ip(ip)
            logger.warning(
                "IP automatisch blockiert",
                ip=ip,
                score=self.suspicious_ips[ip]
            )
    
    def block_ip(self, ip: str):
        """
        Blockiert eine IP-Adresse
        """
        if ip not in self.whitelisted_ips:
            self.blocked_ips.add(ip)
            
            # Security-Event loggen
            from utils.logging_config import security_logger
            security_logger.log_suspicious_activity(
                user_id="system",
                activity="ip_blocked",
                ip_address=ip,
                details={"reason": "suspicious_score_exceeded"}
            )
    
    def add_security_headers(self, response: Response):
        """
        Fügt Sicherheits-Header zur Response hinzu
        """
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        # Weitere Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (nur bei HTTPS)
        if hasattr(response, 'url') and str(response.url).startswith('https'):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Server-Header entfernen/ändern
        response.headers["Server"] = "ChiliView/1.0"

class InputValidator:
    """
    Eingabe-Validierung und Sanitization
    """
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Bereinigt Dateinamen von gefährlichen Zeichen
        """
        if not filename:
            return "unnamed_file"
        
        # Gefährliche Zeichen entfernen
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(dangerous_chars, '_', filename)
        
        # Reservierte Namen vermeiden (Windows)
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_without_ext = sanitized.rsplit('.', 1)[0].upper()
        if name_without_ext in reserved_names:
            sanitized = f"file_{sanitized}"
        
        # Länge begrenzen
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            max_name_length = 255 - len(ext) - 1 if ext else 255
            sanitized = f"{name[:max_name_length]}.{ext}" if ext else name[:255]
        
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validiert E-Mail-Adressen
        """
        if not email or len(email) > 254:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validiert Benutzernamen
        """
        if not username or len(username) < 3 or len(username) > 50:
            return False
        
        # Nur alphanumerische Zeichen, Unterstriche und Bindestriche
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Entfernt/escaped HTML-Tags aus Text
        """
        if not text:
            return ""
        
        # HTML-Tags entfernen
        html_pattern = r'<[^>]+>'
        sanitized = re.sub(html_pattern, '', text)
        
        # Gefährliche Zeichen escapen
        sanitized = sanitized.replace('&', '&amp;')
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        
        return sanitized
    
    @staticmethod
    def validate_project_name(name: str) -> bool:
        """
        Validiert Projektnamen
        """
        if not name or len(name) < 1 or len(name) > 100:
            return False
        
        # Keine gefährlichen Zeichen
        dangerous_pattern = r'[<>:"/\\|?*\x00-\x1f]'
        return not re.search(dangerous_pattern, name)

class CSRFProtection:
    """
    CSRF-Schutz für State-changing Operations
    """
    
    def __init__(self):
        self.tokens: Dict[str, datetime] = {}
        self.token_lifetime = timedelta(hours=1)
    
    def generate_token(self, user_id: str) -> str:
        """
        Generiert einen CSRF-Token für einen User
        """
        token = secrets.token_urlsafe(32)
        self.tokens[token] = datetime.utcnow()
        
        # Alte Tokens aufräumen
        self.cleanup_expired_tokens()
        
        return token
    
    def validate_token(self, token: str) -> bool:
        """
        Validiert einen CSRF-Token
        """
        if not token or token not in self.tokens:
            return False
        
        token_time = self.tokens[token]
        if datetime.utcnow() - token_time > self.token_lifetime:
            del self.tokens[token]
            return False
        
        return True
    
    def cleanup_expired_tokens(self):
        """
        Entfernt abgelaufene Tokens
        """
        now = datetime.utcnow()
        expired_tokens = [
            token for token, created_time in self.tokens.items()
            if now - created_time > self.token_lifetime
        ]
        
        for token in expired_tokens:
            del self.tokens[token]

class IPWhitelist:
    """
    IP-Whitelist-Verwaltung
    """
    
    def __init__(self):
        self.whitelisted_networks = [
            ipaddress.ip_network('127.0.0.0/8'),    # Localhost
            ipaddress.ip_network('::1/128'),         # IPv6 Localhost
            ipaddress.ip_network('10.0.0.0/8'),     # Private Class A
            ipaddress.ip_network('172.16.0.0/12'),  # Private Class B
            ipaddress.ip_network('192.168.0.0/16'), # Private Class C
        ]
    
    def is_whitelisted(self, ip_str: str) -> bool:
        """
        Prüft ob eine IP in der Whitelist ist
        """
        try:
            ip = ipaddress.ip_address(ip_str)
            return any(ip in network for network in self.whitelisted_networks)
        except ValueError:
            return False
    
    def add_network(self, network_str: str):
        """
        Fügt ein Netzwerk zur Whitelist hinzu
        """
        try:
            network = ipaddress.ip_network(network_str)
            self.whitelisted_networks.append(network)
            logger.info("Netzwerk zur Whitelist hinzugefügt", network=network_str)
        except ValueError as e:
            logger.error(f"Ungültiges Netzwerk: {network_str} - {str(e)}")

# Globale Instanzen
input_validator = InputValidator()
csrf_protection = CSRFProtection()
ip_whitelist = IPWhitelist()

def generate_secure_token(length: int = 32) -> str:
    """
    Generiert einen sicheren zufälligen Token
    """
    return secrets.token_urlsafe(length)

def hash_password_secure(password: str, salt: str = None) -> tuple:
    """
    Hasht ein Passwort sicher mit Salt
    """
    if not salt:
        salt = secrets.token_hex(16)
    
    # PBKDF2 mit SHA-256
    import hashlib
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100k Iterationen
    )
    
    return password_hash.hex(), salt

def verify_password_secure(password: str, password_hash: str, salt: str) -> bool:
    """
    Verifiziert ein Passwort gegen einen Hash
    """
    computed_hash, _ = hash_password_secure(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)

def constant_time_compare(a: str, b: str) -> bool:
    """
    Zeitkonstanter String-Vergleich
    """
    return secrets.compare_digest(a.encode('utf-8'), b.encode('utf-8'))