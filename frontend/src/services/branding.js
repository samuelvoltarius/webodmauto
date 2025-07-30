/**
 * ChiliView Branding Service
 * Lädt und verwaltet Branding-Daten für White-Label-Funktionalität
 */

import axios from 'axios'

// 🎨 Branding-Service
export const useBrandingService = () => {
  
  /**
   * Lädt Branding-Daten für den aktuellen Reseller
   * @param {string} resellerId - Optional: Spezifische Reseller-ID
   * @returns {Promise<Object>} Branding-Daten
   */
  const loadBranding = async (resellerId = null) => {
    try {
      // Reseller-ID aus verschiedenen Quellen ermitteln
      let targetResellerId = resellerId
      
      if (!targetResellerId) {
        // Aus URL-Parameter extrahieren
        const urlPath = window.location.pathname
        const resellerMatch = urlPath.match(/\/reseller\/([^\/]+)/)
        if (resellerMatch) {
          targetResellerId = resellerMatch[1]
        }
      }
      
      if (!targetResellerId) {
        // Aus localStorage (falls User eingeloggt)
        const userData = localStorage.getItem('user_data')
        if (userData) {
          const user = JSON.parse(userData)
          targetResellerId = user.reseller_id
        }
      }
      
      // API-Call für Branding-Daten
      if (targetResellerId) {
        const response = await axios.get(`/api/reseller/${targetResellerId}/branding`)
        return response.data
      }
      
      // Fallback: Standard-Branding laden
      const response = await axios.get('/api/branding/default')
      return response.data
      
    } catch (error) {
      console.warn('Branding-Daten konnten nicht geladen werden:', error)
      
      // Fallback: Standard-Branding-Daten
      return {
        company_name: 'ChiliView',
        logo_url: null,
        primary_color: '#2563eb',
        secondary_color: '#64748b',
        accent_color: '#10b981',
        font_family: 'Inter',
        custom_css: null,
        footer_text: 'Powered by ChiliView',
        contact_email: 'info@chiliview.com',
        support_url: null,
        terms_url: null,
        privacy_url: null,
        
        // Impressum-Daten
        address: 'Musterstraße 123',
        postal_code: '12345',
        city: 'Musterstadt',
        country: 'Deutschland',
        phone: '+49 (0) 123 456789',
        email: 'info@chiliview.com',
        website: 'https://chiliview.com',
        
        // Geschäftsführung
        ceo_name: 'Max Mustermann',
        commercial_register: 'HRB 123456',
        court: 'Amtsgericht Musterstadt',
        tax_number: 'DE123456789',
        vat_id: 'DE123456789',
        
        // Datenschutzbeauftragter
        dpo_name: 'Max Mustermann',
        dpo_email: 'datenschutz@chiliview.com',
        dpo_phone: '+49 (0) 123 456789',
        dpo_address: 'Musterstraße 123'
      }
    }
  }
  
  /**
   * Speichert Branding-Daten für einen Reseller
   * @param {string} resellerId - Reseller-ID
   * @param {Object} brandingData - Branding-Daten
   * @returns {Promise<Object>} Gespeicherte Branding-Daten
   */
  const saveBranding = async (resellerId, brandingData) => {
    try {
      const response = await axios.put(`/api/reseller/${resellerId}/branding`, brandingData)
      return response.data
    } catch (error) {
      console.error('Branding-Daten konnten nicht gespeichert werden:', error)
      throw error
    }
  }
  
  /**
   * Wendet Branding-Styles auf die Seite an
   * @param {Object} branding - Branding-Daten
   */
  const applyBrandingStyles = (branding) => {
    if (!branding) return
    
    try {
      // CSS-Variablen setzen
      const root = document.documentElement
      
      if (branding.primary_color) {
        root.style.setProperty('--color-primary', branding.primary_color)
      }
      
      if (branding.secondary_color) {
        root.style.setProperty('--color-secondary', branding.secondary_color)
      }
      
      if (branding.accent_color) {
        root.style.setProperty('--color-accent', branding.accent_color)
      }
      
      if (branding.font_family) {
        root.style.setProperty('--font-family', branding.font_family)
      }
      
      // Custom CSS anwenden
      if (branding.custom_css) {
        let customStyleElement = document.getElementById('custom-branding-styles')
        
        if (!customStyleElement) {
          customStyleElement = document.createElement('style')
          customStyleElement.id = 'custom-branding-styles'
          document.head.appendChild(customStyleElement)
        }
        
        customStyleElement.textContent = branding.custom_css
      }
      
      // Favicon aktualisieren
      if (branding.favicon_url) {
        let faviconElement = document.querySelector('link[rel="icon"]')
        
        if (!faviconElement) {
          faviconElement = document.createElement('link')
          faviconElement.rel = 'icon'
          document.head.appendChild(faviconElement)
        }
        
        faviconElement.href = branding.favicon_url
      }
      
      // Titel-Präfix setzen
      if (branding.company_name && branding.company_name !== 'ChiliView') {
        const currentTitle = document.title
        if (!currentTitle.startsWith(branding.company_name)) {
          document.title = currentTitle.replace('ChiliView', branding.company_name)
        }
      }
      
    } catch (error) {
      console.warn('Branding-Styles konnten nicht angewendet werden:', error)
    }
  }
  
  /**
   * Lädt und wendet Branding automatisch an
   * @param {string} resellerId - Optional: Spezifische Reseller-ID
   */
  const initializeBranding = async (resellerId = null) => {
    try {
      const branding = await loadBranding(resellerId)
      applyBrandingStyles(branding)
      return branding
    } catch (error) {
      console.warn('Branding-Initialisierung fehlgeschlagen:', error)
      return null
    }
  }
  
  /**
   * Entfernt alle Branding-Styles
   */
  const removeBrandingStyles = () => {
    try {
      // CSS-Variablen zurücksetzen
      const root = document.documentElement
      root.style.removeProperty('--color-primary')
      root.style.removeProperty('--color-secondary')
      root.style.removeProperty('--color-accent')
      root.style.removeProperty('--font-family')
      
      // Custom CSS entfernen
      const customStyleElement = document.getElementById('custom-branding-styles')
      if (customStyleElement) {
        customStyleElement.remove()
      }
      
    } catch (error) {
      console.warn('Branding-Styles konnten nicht entfernt werden:', error)
    }
  }
  
  /**
   * Validiert Branding-Daten
   * @param {Object} branding - Branding-Daten
   * @returns {Object} Validierungsergebnis
   */
  const validateBranding = (branding) => {
    const errors = []
    const warnings = []
    
    // Pflichtfelder prüfen
    if (!branding.company_name || branding.company_name.trim() === '') {
      errors.push('Firmenname ist erforderlich')
    }
    
    // Farben validieren
    const colorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/
    
    if (branding.primary_color && !colorRegex.test(branding.primary_color)) {
      errors.push('Primärfarbe muss ein gültiger Hex-Farbcode sein')
    }
    
    if (branding.secondary_color && !colorRegex.test(branding.secondary_color)) {
      errors.push('Sekundärfarbe muss ein gültiger Hex-Farbcode sein')
    }
    
    if (branding.accent_color && !colorRegex.test(branding.accent_color)) {
      errors.push('Akzentfarbe muss ein gültiger Hex-Farbcode sein')
    }
    
    // URLs validieren
    const urlRegex = /^https?:\/\/.+/
    
    if (branding.logo_url && !urlRegex.test(branding.logo_url)) {
      warnings.push('Logo-URL sollte mit http:// oder https:// beginnen')
    }
    
    if (branding.website && !urlRegex.test(branding.website)) {
      warnings.push('Website-URL sollte mit http:// oder https:// beginnen')
    }
    
    // E-Mail validieren
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    
    if (branding.email && !emailRegex.test(branding.email)) {
      errors.push('E-Mail-Adresse ist ungültig')
    }
    
    if (branding.dpo_email && !emailRegex.test(branding.dpo_email)) {
      errors.push('Datenschutzbeauftragter E-Mail-Adresse ist ungültig')
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings
    }
  }
  
  return {
    loadBranding,
    saveBranding,
    applyBrandingStyles,
    initializeBranding,
    removeBrandingStyles,
    validateBranding
  }
}

// 🎨 Branding-Utilities
export const brandingUtils = {
  /**
   * Generiert CSS-Variablen aus Branding-Daten
   * @param {Object} branding - Branding-Daten
   * @returns {string} CSS-String
   */
  generateCSSVariables: (branding) => {
    const variables = []
    
    if (branding.primary_color) {
      variables.push(`--color-primary: ${branding.primary_color};`)
    }
    
    if (branding.secondary_color) {
      variables.push(`--color-secondary: ${branding.secondary_color};`)
    }
    
    if (branding.accent_color) {
      variables.push(`--color-accent: ${branding.accent_color};`)
    }
    
    if (branding.font_family) {
      variables.push(`--font-family: ${branding.font_family};`)
    }
    
    return variables.length > 0 ? `:root { ${variables.join(' ')} }` : ''
  },
  
  /**
   * Konvertiert Hex-Farbe zu RGB
   * @param {string} hex - Hex-Farbcode
   * @returns {Object} RGB-Werte
   */
  hexToRgb: (hex) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  },
  
  /**
   * Berechnet Kontrast zwischen zwei Farben
   * @param {string} color1 - Erste Farbe (Hex)
   * @param {string} color2 - Zweite Farbe (Hex)
   * @returns {number} Kontrastverhältnis
   */
  calculateContrast: (color1, color2) => {
    const rgb1 = brandingUtils.hexToRgb(color1)
    const rgb2 = brandingUtils.hexToRgb(color2)
    
    if (!rgb1 || !rgb2) return 0
    
    const luminance1 = (0.299 * rgb1.r + 0.587 * rgb1.g + 0.114 * rgb1.b) / 255
    const luminance2 = (0.299 * rgb2.r + 0.587 * rgb2.g + 0.114 * rgb2.b) / 255
    
    const brightest = Math.max(luminance1, luminance2)
    const darkest = Math.min(luminance1, luminance2)
    
    return (brightest + 0.05) / (darkest + 0.05)
  }
}

export default useBrandingService