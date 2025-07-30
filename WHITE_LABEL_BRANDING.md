# ChiliView White-Label Branding System

## 🎨 Vollständiges Branding-System für Reseller

Das ChiliView White-Label Branding System ermöglicht es Resellern, ihre ChiliView-Instanz vollständig an ihr Corporate Design anzupassen und ihren Benutzern ein nahtloses, markenkonformes Erlebnis zu bieten.

## ✅ Implementierte Features

### **1. Reseller Branding Interface**
- **Datei**: [`local_dev/frontend/src/views/reseller/Branding.vue`](local_dev/frontend/src/views/reseller/Branding.vue)
- **Zugriff**: Reseller Dashboard → Branding
- **Funktionen**:
  - ✅ Live-Vorschau der Änderungen
  - ✅ Logo-Upload und -Verwaltung
  - ✅ Farbschema-Anpassung (Primär-/Sekundärfarben)
  - ✅ Willkommensnachrichten
  - ✅ Rechtliche Angaben (Impressum/Datenschutz)
  - ✅ Benutzerdefiniertes CSS
  - ✅ Benutzerdefiniertes HTML

### **2. Datenbank-Schema**
- **Datei**: [`local_dev/backend/database/models.py`](local_dev/backend/database/models.py:49-60)
- **Branding-Felder im Reseller-Model**:
  ```python
  # Branding-Einstellungen
  logo_url = Column(String(255))
  primary_color = Column(String(7), default="#007bff")
  secondary_color = Column(String(7), default="#6c757d")
  welcome_message = Column(Text)
  custom_css = Column(Text)
  custom_html = Column(Text)
  
  # Rechtliche Angaben
  imprint = Column(Text)
  privacy_policy = Column(Text)
  homepage_url = Column(String(255))
  ```

### **3. Backend-API**
- **Datei**: [`local_dev/backend/routers/admin.py`](local_dev/backend/routers/admin.py)
- **Endpoints**:
  - `GET /admin/resellers/{reseller_id}` - Branding-Daten abrufen
  - `PUT /admin/resellers/{reseller_id}` - Branding-Daten speichern
  - Vollständige Validierung und Fehlerbehandlung

### **4. Branding-Service**
- **Datei**: [`local_dev/frontend/src/services/branding.js`](local_dev/frontend/src/services/branding.js)
- **Funktionen**:
  - ✅ Automatisches Laden der Branding-Daten
  - ✅ CSS-Variablen-Injection
  - ✅ Custom CSS/HTML-Injection
  - ✅ Seitentitel-Anpassung
  - ✅ Komponenten-Integration

## 🎯 Branding-Möglichkeiten für Reseller

### **Visuelle Anpassungen**
1. **Logo**: Eigenes Firmenlogo (PNG/SVG, empfohlen: 200x60px)
2. **Farben**: 
   - Primärfarbe für Buttons, Links, Hervorhebungen
   - Sekundärfarbe für sekundäre Elemente
3. **Willkommensnachricht**: Personalisierte Begrüßung für Benutzer

### **Rechtliche Compliance (DSGVO-konform)**
1. **Impressum**: Vollständiges Impressum nach §5 TMG
2. **Datenschutzerklärung**: DSGVO-konforme Datenschutzerklärung
3. **Homepage-URL**: Link zur Unternehmens-Website

### **Erweiterte Anpassungen**
1. **Custom CSS**: Vollständige Kontrolle über das Design
2. **Custom HTML**: Zusätzliche Elemente (z.B. Footer-Inhalte)

## 🔧 Technische Integration

### **Automatische Branding-Anwendung**
```javascript
// Branding wird automatisch geladen und angewendet
import brandingService from '@/services/branding'

// In Vue-Komponenten
const branding = brandingService.getBrandingConfig()
const styles = brandingService.getComponentStyles()
```

### **CSS-Variablen-System**
```css
/* Automatisch verfügbare CSS-Variablen */
:root {
  --primary-color: #007bff;    /* Reseller-Primärfarbe */
  --secondary-color: #6c757d;  /* Reseller-Sekundärfarbe */
  --brand-primary: #007bff;
  --brand-secondary: #6c757d;
}
```

### **Komponenten-Integration**
```vue
<template>
  <div :style="brandingStyles">
    <img v-if="branding.company.logo" :src="branding.company.logo" />
    <h1>{{ branding.company.name }}</h1>
    <p>{{ branding.company.welcome }}</p>
  </div>
</template>

<script>
import brandingService from '@/services/branding'

export default {
  computed: {
    branding() {
      return brandingService.getBrandingConfig()
    },
    brandingStyles() {
      return brandingService.getComponentStyles()
    }
  }
}
</script>
```

## 🚀 Verwendung für Reseller

### **1. Zugriff auf Branding-Einstellungen**
1. Als Reseller einloggen
2. Dashboard → "Branding" aufrufen
3. Branding-Einstellungen anpassen
4. Live-Vorschau prüfen
5. Speichern

### **2. Logo-Integration**
- Logo-URL eingeben (externe URL oder Upload)
- Empfohlene Größe: 200x60px
- Unterstützte Formate: PNG, SVG, JPG

### **3. Farbschema anpassen**
- Primärfarbe: Hauptfarbe für Buttons, Links
- Sekundärfarbe: Akzentfarbe für sekundäre Elemente
- Color-Picker oder Hex-Code-Eingabe

### **4. Rechtliche Angaben**
- **Impressum**: Vollständige Firmenangaben (Pflichtfeld)
- **Datenschutz**: DSGVO-konforme Datenschutzerklärung (Pflichtfeld)

### **5. Erweiterte Anpassungen**
- **Custom CSS**: Für fortgeschrittene Design-Anpassungen
- **Custom HTML**: Für zusätzliche Inhalte im Footer

## 🎨 Auswirkungen auf User-Experience

### **Für End-User (Kunden des Resellers)**
- ✅ Konsistentes Branding der Reseller-Marke
- ✅ Vertraute Farben und Logo
- ✅ Personalisierte Willkommensnachrichten
- ✅ Rechtssichere Impressum/Datenschutz-Links
- ✅ Nahtlose Integration in Reseller-Website

### **Für Reseller**
- ✅ Vollständige Kontrolle über das Erscheinungsbild
- ✅ White-Label-Lösung ohne ChiliView-Branding
- ✅ DSGVO-konforme rechtliche Integration
- ✅ Einfache Verwaltung über Web-Interface
- ✅ Live-Vorschau aller Änderungen

## 📱 Responsive Design

Das Branding-System ist vollständig responsive und funktioniert auf:
- ✅ Desktop-Computern
- ✅ Tablets
- ✅ Smartphones
- ✅ Verschiedenen Bildschirmgrößen

## 🔒 Sicherheit & Validierung

- ✅ Eingabe-Validierung für alle Felder
- ✅ XSS-Schutz für Custom HTML/CSS
- ✅ Sichere URL-Validierung für Logo/Homepage
- ✅ Audit-Logging aller Branding-Änderungen

## 🎯 Beispiel-Anwendungsfall

**Szenario**: Architekturbüro "Müller & Partner" nutzt ChiliView

1. **Branding-Setup**:
   - Logo: `https://mueller-partner.de/logo.png`
   - Primärfarbe: `#2C5F41` (Firmengrün)
   - Sekundärfarbe: `#8B4513` (Braun)
   - Willkommen: "Willkommen bei Müller & Partner 3D-Vermessung"

2. **Rechtliche Integration**:
   - Impressum mit vollständigen Firmenangaben
   - Datenschutzerklärung nach DSGVO
   - Homepage-Link zu `https://mueller-partner.de`

3. **Ergebnis für End-User**:
   - ChiliView erscheint als "Müller & Partner 3D-Vermessung"
   - Firmenfarben und Logo überall sichtbar
   - Rechtssichere Impressum/Datenschutz-Links
   - Nahtlose Integration in Firmen-Website

## 🔄 Aktualisierung & Wartung

- ✅ Branding-Änderungen werden sofort angewendet
- ✅ Keine Server-Neustarts erforderlich
- ✅ Versionierung aller Branding-Änderungen
- ✅ Rollback-Möglichkeit über Admin-Interface

Das White-Label Branding System ist vollständig implementiert und einsatzbereit!