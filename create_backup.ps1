# ChiliView Backup Script für Windows
# Erstellt ein vollständiges Backup aller Projektdateien

$BackupName = "chiliview_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$BackupFile = "$BackupName.zip"

Write-Host "Erstelle Backup: $BackupFile" -ForegroundColor Green

# Temporäres Verzeichnis für Backup erstellen
$TempPath = "$env:TEMP\$BackupName"
New-Item -ItemType Directory -Path $TempPath -Force | Out-Null

Write-Host "Kopiere Projektdateien..." -ForegroundColor Yellow

# Backend kopieren
if (Test-Path "backend") {
    Copy-Item -Path "backend" -Destination $TempPath -Recurse -Force
    Write-Host "✓ Backend kopiert" -ForegroundColor Green
}

# Frontend kopieren
if (Test-Path "frontend") {
    Copy-Item -Path "frontend" -Destination $TempPath -Recurse -Force
    Write-Host "✓ Frontend kopiert" -ForegroundColor Green
}

# Nginx Konfiguration kopieren
if (Test-Path "nginx") {
    Copy-Item -Path "nginx" -Destination $TempPath -Recurse -Force
    Write-Host "✓ Nginx Konfiguration kopiert" -ForegroundColor Green
}

# Scripts kopieren
if (Test-Path "scripts") {
    Copy-Item -Path "scripts" -Destination $TempPath -Recurse -Force
    Write-Host "✓ Scripts kopiert" -ForegroundColor Green
}

# Docker Konfiguration kopieren
$dockerFiles = @("docker-compose.yml", "docker-compose.override.yml")
foreach ($file in $dockerFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $TempPath -Force
    }
}
Write-Host "✓ Docker Konfiguration kopiert" -ForegroundColor Green

# Setup und Installation kopieren
$setupFiles = @("setup.sh", "install.sh", "create_backup.sh")
foreach ($file in $setupFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $TempPath -Force
    }
}
Write-Host "✓ Setup-Skripte kopiert" -ForegroundColor Green

# Dokumentation kopieren
if (Test-Path "README.md") {
    Copy-Item -Path "README.md" -Destination $TempPath -Force
}
Write-Host "✓ Dokumentation kopiert" -ForegroundColor Green

# Weitere Konfigurationsdateien
$configFiles = @(".gitignore", ".env.example")
foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $TempPath -Force
    }
}

# ZIP-Archiv erstellen
Write-Host "Erstelle ZIP-Archiv..." -ForegroundColor Yellow

try {
    Compress-Archive -Path "$TempPath\*" -DestinationPath $BackupFile -Force
    
    # Temporäres Verzeichnis aufräumen
    Remove-Item -Path $TempPath -Recurse -Force
    
    $BackupSize = (Get-Item $BackupFile).Length
    $BackupSizeMB = [math]::Round($BackupSize / 1MB, 2)
    
    Write-Host ""
    Write-Host "✅ Backup erfolgreich erstellt: $BackupFile" -ForegroundColor Green
    Write-Host "📁 Größe: $BackupSizeMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Das Backup enthält:" -ForegroundColor Yellow
    Write-Host "  • Vollständigen Backend-Code (Python/FastAPI)" -ForegroundColor White
    Write-Host "  • Vollständigen Frontend-Code (Vue.js)" -ForegroundColor White
    Write-Host "  • Docker-Konfiguration" -ForegroundColor White
    Write-Host "  • Setup- und Installations-Skripte" -ForegroundColor White
    Write-Host "  • Nginx-Konfiguration" -ForegroundColor White
    Write-Host "  • Dokumentation" -ForegroundColor White
    Write-Host ""
    Write-Host "Zum Wiederherstellen:" -ForegroundColor Yellow
    Write-Host "  1. Entpacken Sie $BackupFile" -ForegroundColor White
    Write-Host "  2. Führen Sie install.sh aus (Linux/macOS) oder setup.sh" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "❌ Fehler beim Erstellen des Backups: $($_.Exception.Message)" -ForegroundColor Red
    Remove-Item -Path $TempPath -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}