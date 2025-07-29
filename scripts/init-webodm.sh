#!/bin/bash

# WebODM Initialisierungsskript
# Automatische Konfiguration von WebODM für ChiliView

set -e

echo "Initialisiere WebODM für ChiliView..."

# Warten bis WebODM verfügbar ist
echo "Warte auf WebODM..."
for i in {1..60}; do
    if curl -f http://webodm-webapp:8080/api/ &>/dev/null; then
        echo "WebODM ist verfügbar"
        break
    fi
    echo "Warte auf WebODM... ($i/60)"
    sleep 5
done

# Admin-Benutzer erstellen falls nicht vorhanden
echo "Erstelle WebODM Admin-Benutzer..."
python3 << 'EOF'
import requests
import json
import os
import sys

webodm_url = "http://webodm-webapp:8080"
admin_username = "admin"
admin_password = "admin"
admin_email = "admin@chiliview.local"

session = requests.Session()

try:
    # Prüfen ob Admin bereits existiert durch Login-Versuch
    login_response = session.post(f"{webodm_url}/api/token-auth/", {
        "username": admin_username,
        "password": admin_password
    })
    
    if login_response.status_code == 200:
        print("WebODM Admin-Benutzer bereits vorhanden")
        sys.exit(0)
    
    # CSRF Token holen
    csrf_response = session.get(f"{webodm_url}/")
    if csrf_response.status_code != 200:
        print("Fehler beim Abrufen der CSRF-Token")
        sys.exit(1)
    
    # Admin-Benutzer erstellen
    # Da WebODM keine direkte API für Benutzer-Erstellung hat,
    # verwenden wir Django Management Commands
    print("WebODM Admin wird über Django Management Command erstellt...")
    
except Exception as e:
    print(f"Fehler bei WebODM-Initialisierung: {e}")
    # Nicht kritisch - WebODM kann manuell konfiguriert werden
    print("WebODM kann nach dem Start manuell konfiguriert werden")

EOF

# WebODM Django Management Commands ausführen
echo "Führe WebODM Setup-Befehle aus..."
docker-compose exec -T webodm-webapp python manage.py migrate --noinput || true
docker-compose exec -T webodm-webapp python manage.py collectstatic --noinput || true

# Admin-Benutzer über Django erstellen
docker-compose exec -T webodm-webapp python manage.py shell << 'EOF' || true
from django.contrib.auth.models import User
import os

username = 'admin'
password = 'admin'
email = 'admin@chiliview.local'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"WebODM Admin-Benutzer '{username}' erstellt")
else:
    print(f"WebODM Admin-Benutzer '{username}' bereits vorhanden")
EOF

echo "WebODM-Initialisierung abgeschlossen"