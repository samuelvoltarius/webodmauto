# DSGVO-Compliance Dokumentation - ChiliView Platform

## 📋 Übersicht

Die ChiliView Platform ist vollständig DSGVO-konform implementiert und erfüllt alle Anforderungen der Datenschutz-Grundverordnung (EU-DSGVO) für den deutschen und europäischen Markt.

## 🛡️ Implementierte DSGVO-Features

### 1. Rechtliche Seiten

#### Impressum (`/imprint`)
- **Datei**: `local_dev/frontend/src/views/legal/Imprint.vue`
- **Features**:
  - Vollständige Anbieterkennzeichnung nach § 5 TMG
  - Geschäftsführung und Handelsregisterdaten
  - Kontaktdaten und Verantwortlichkeiten
  - Umsatzsteuer-ID und Steuernummer
  - Aufsichtsbehörde und Berufsbezeichnung
  - White-Label Branding-Integration
  - Responsive Design für alle Geräte

#### Datenschutzerklärung (`/privacy`)
- **Datei**: `local_dev/frontend/src/views/legal/Privacy.vue`
- **Features**:
  - Umfassende Datenschutzerklärung nach Art. 13/14 DSGVO
  - Detaillierte Beschreibung der Datenverarbeitung
  - Rechtsgrundlagen für alle Verarbeitungszwecke
  - Betroffenenrechte (Auskunft, Berichtigung, Löschung, etc.)
  - Speicherdauern und Aufbewahrungsfristen
  - Datensicherheitsmaßnahmen
  - Cookie-Informationen
  - 3D-Modell Upload und Verarbeitung
  - Kontaktdaten des Datenschutzbeauftragten
  - White-Label Branding-Integration

### 2. Cookie-Management

#### Cookie-Banner
- **Datei**: `local_dev/frontend/src/components/CookieBanner.vue`
- **Features**:
  - DSGVO-konformer Cookie-Consent-Banner
  - Granulare Cookie-Kategorien:
    - Technisch notwendige Cookies (immer aktiv)
    - Funktionale Cookies (optional)
    - Analyse-Cookies (optional)
    - Marketing-Cookies (optional)
  - Detaillierte Cookie-Einstellungen mit Modal
  - Automatische Cookie-Verwaltung und -Löschung
  - Consent-Speicherung mit Ablaufdatum (1 Jahr)
  - Integration mit Analytics und Marketing-Tools
  - Responsive Design und Accessibility

#### Cookie-Funktionalität
- **Consent-Management**: Automatische Speicherung und Verwaltung der Benutzereinwilligung
- **Cookie-Kategorisierung**: Klare Trennung zwischen notwendigen und optionalen Cookies
- **Automatische Löschung**: Deaktivierte Cookies werden automatisch gelöscht
- **Consent-Erneuerung**: Automatische Aufforderung zur Erneuerung nach einem Jahr
- **Integration**: Nahtlose Integration mit Google Analytics und anderen Tools

### 3. Branding-Service Integration

#### White-Label DSGVO-Compliance
- **Datei**: `local_dev/frontend/src/services/branding.js`
- **Features**:
  - Automatische Anpassung der rechtlichen Seiten an Reseller-Branding
  - Dynamische Kontaktdaten und Firmeninformationen
  - Reseller-spezifische Datenschutzbeauftragte
  - Anpassbare Impressum-Daten
  - Branding-Integration in Cookie-Banner

### 4. Router-Integration

#### Öffentliche Rechtliche Seiten
- **Datei**: `local_dev/frontend/src/router/index.js`
- **Features**:
  - Öffentlich zugängliche Legal-Seiten ohne Authentifizierung
  - SEO-optimierte URLs (`/imprint`, `/privacy`)
  - Korrekte Meta-Tags und Titel
  - AuthLayout für konsistente Darstellung

### 5. App-Integration

#### Globale DSGVO-Integration
- **Datei**: `local_dev/frontend/src/App.vue`
- **Features**:
  - Cookie-Banner in der Hauptanwendung integriert
  - Automatische Initialisierung nach App-Start
  - Keine Beeinträchtigung der Anwendungsperformance

## 🔒 Datenschutz-Maßnahmen

### Technische Maßnahmen
1. **Verschlüsselung**: Alle Datenübertragungen erfolgen über HTTPS/TLS
2. **Passwort-Sicherheit**: Verschlüsselte Speicherung mit bcrypt
3. **Session-Management**: Sichere JWT-Token mit Ablaufzeiten
4. **Zugriffskontrolle**: Rollenbasierte Berechtigungen
5. **Audit-Logging**: Vollständige Protokollierung aller Systemzugriffe
6. **Datensparsamkeit**: Minimale Datenerhebung nach Zweckbindung

### Organisatorische Maßnahmen
1. **Datenschutzbeauftragter**: Kontaktdaten in allen rechtlichen Dokumenten
2. **Aufbewahrungsfristen**: Klare Regelungen für alle Datentypen
3. **Löschkonzept**: Automatische und manuelle Datenlöschung
4. **Backup-Sicherheit**: Verschlüsselte Backups mit begrenzter Aufbewahrung
5. **Mitarbeiterschulung**: Dokumentierte Datenschutz-Richtlinien

## 📊 Cookie-Kategorien im Detail

### Technisch Notwendige Cookies
- **Zweck**: Grundfunktionen der Website
- **Cookies**: `session_token`, `csrf_token`, `user_preferences`
- **Speicherdauer**: Sitzung bis 30 Tage
- **Rechtsgrundlage**: Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse)

### Funktionale Cookies
- **Zweck**: Erweiterte Funktionen und Personalisierung
- **Cookies**: `user_theme`, `language_preference`, `ui_settings`
- **Speicherdauer**: 1 Jahr
- **Rechtsgrundlage**: Art. 6 Abs. 1 lit. a DSGVO (Einwilligung)

### Analyse-Cookies
- **Zweck**: Nutzungsstatistiken und Performance-Monitoring
- **Cookies**: `_analytics_session`, `_performance_data`
- **Speicherdauer**: 2 Jahre
- **Rechtsgrundlage**: Art. 6 Abs. 1 lit. a DSGVO (Einwilligung)

### Marketing-Cookies
- **Zweck**: Personalisierte Werbung und Remarketing
- **Cookies**: `_marketing_id`, `_conversion_data`
- **Speicherdauer**: 1 Jahr
- **Rechtsgrundlage**: Art. 6 Abs. 1 lit. a DSGVO (Einwilligung)

## 🎯 Betroffenenrechte

### Implementierte Rechte
1. **Auskunftsrecht** (Art. 15 DSGVO): Vollständige Datenauskunft über API
2. **Berichtigungsrecht** (Art. 16 DSGVO): Profil-Bearbeitung und Datenkorrektur
3. **Löschungsrecht** (Art. 17 DSGVO): Account- und Projektlöschung
4. **Einschränkungsrecht** (Art. 18 DSGVO): Datenverarbeitung pausieren
5. **Datenübertragbarkeit** (Art. 20 DSGVO): Export aller Benutzerdaten
6. **Widerspruchsrecht** (Art. 21 DSGVO): Widerspruch gegen Verarbeitung
7. **Beschwerderecht** (Art. 77 DSGVO): Kontakt zur Aufsichtsbehörde

### Umsetzung in der Anwendung
- **Profil-Seite**: Direkte Bearbeitung persönlicher Daten
- **Projekt-Verwaltung**: Einzelne oder komplette Projektlöschung
- **Account-Löschung**: Vollständige Entfernung aller Benutzerdaten
- **Datenexport**: JSON-Export aller gespeicherten Daten
- **Kontaktformulare**: Direkte Kommunikation für Betroffenenrechte

## 🔄 Datenverarbeitung

### Verarbeitungszwecke
1. **Vertragserfüllung** (Art. 6 Abs. 1 lit. b DSGVO):
   - Benutzerregistrierung und -verwaltung
   - 3D-Modell-Upload und -Verarbeitung
   - Projekt-Management und -Speicherung

2. **Berechtigtes Interesse** (Art. 6 Abs. 1 lit. f DSGVO):
   - System-Sicherheit und -Stabilität
   - Fehleranalyse und Performance-Optimierung
   - Backup und Disaster Recovery

3. **Einwilligung** (Art. 6 Abs. 1 lit. a DSGVO):
   - Marketing und Newsletter
   - Erweiterte Analytics
   - Personalisierte Funktionen

### Aufbewahrungsfristen
- **Account-Daten**: Bis zur Löschung des Accounts
- **Projektdaten**: Bis zur manuellen Löschung durch den Nutzer
- **Log-Dateien**: Maximal 30 Tage
- **Backup-Daten**: Maximal 90 Tage
- **Rechnungsdaten**: 10 Jahre (§ 147 AO)

## 🌍 Internationale Compliance

### EU-DSGVO Compliance
- Vollständige Umsetzung aller DSGVO-Anforderungen
- Deutsche und europäische Rechtsprechung berücksichtigt
- Keine Datenübertragung in Drittländer ohne Angemessenheitsbeschluss

### Zusätzliche Standards
- **ISO 27001**: Informationssicherheits-Management
- **BSI Grundschutz**: Deutsche IT-Sicherheitsstandards
- **OWASP**: Web Application Security Standards

## 🚀 Deployment und Wartung

### Automatische Updates
- Cookie-Consent wird automatisch nach einem Jahr erneuert
- Rechtliche Dokumente können über Branding-System aktualisiert werden
- Automatische Backup-Rotation und -Löschung

### Monitoring
- Kontinuierliche Überwachung der Datenschutz-Compliance
- Automatische Benachrichtigungen bei Consent-Änderungen
- Audit-Logs für alle datenschutzrelevanten Aktionen

## 📞 Kontakt und Support

### Datenschutzbeauftragter
- **Standard**: datenschutz@chiliview.com
- **Reseller-spezifisch**: Über Branding-System konfigurierbar
- **Telefon**: Über Branding-System konfigurierbar

### Technischer Support
- **E-Mail**: support@chiliview.com
- **Dokumentation**: Vollständige API- und Implementierungsdokumentation
- **Updates**: Regelmäßige Sicherheits- und Compliance-Updates

---

**Letzte Aktualisierung**: 29. Januar 2025  
**Version**: 1.0  
**Status**: Produktionsbereit und DSGVO-konform