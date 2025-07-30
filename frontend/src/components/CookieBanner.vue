<template>
  <!-- Cookie Banner -->
  <div v-if="showBanner" class="fixed bottom-0 left-0 right-0 z-50 bg-gray-900 text-white shadow-2xl">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <!-- Cookie Info -->
        <div class="flex-1">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 mt-1">
              <svg class="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-medium mb-1">Cookie-Einstellungen</h3>
              <p class="text-xs text-gray-300 leading-relaxed">
                Wir verwenden Cookies, um Ihnen die bestmögliche Nutzererfahrung zu bieten. 
                Technisch notwendige Cookies sind für die Grundfunktionen der Website erforderlich. 
                Weitere Cookies helfen uns, die Website zu verbessern und Ihnen personalisierte Inhalte anzuzeigen.
              </p>
            </div>
          </div>
        </div>

        <!-- Cookie Controls -->
        <div class="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
          <!-- Settings Button -->
          <button
            @click="showSettings = true"
            class="px-4 py-2 text-xs font-medium text-gray-300 hover:text-white border border-gray-600 hover:border-gray-500 rounded-md transition-colors duration-200"
          >
            <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Einstellungen
          </button>

          <!-- Accept Essential -->
          <button
            @click="acceptEssential"
            class="px-4 py-2 text-xs font-medium text-gray-900 bg-gray-200 hover:bg-gray-100 rounded-md transition-colors duration-200"
          >
            Nur Notwendige
          </button>

          <!-- Accept All -->
          <button
            @click="acceptAll"
            class="px-4 py-2 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-200"
          >
            Alle akzeptieren
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Cookie Settings Modal -->
  <div v-if="showSettings" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="showSettings = false"></div>

      <!-- Modal -->
      <div class="inline-block w-full max-w-2xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
        <!-- Header -->
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-medium text-gray-900">Cookie-Einstellungen</h3>
          <button
            @click="showSettings = false"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Cookie Categories -->
        <div class="space-y-6">
          <!-- Essential Cookies -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="text-sm font-medium text-gray-900">Technisch notwendige Cookies</h4>
                <p class="text-xs text-gray-500 mt-1">Diese Cookies sind für die Grundfunktionen der Website erforderlich.</p>
              </div>
              <div class="flex items-center">
                <span class="text-xs text-gray-500 mr-2">Immer aktiv</span>
                <div class="w-10 h-6 bg-green-500 rounded-full relative">
                  <div class="w-4 h-4 bg-white rounded-full absolute top-1 right-1"></div>
                </div>
              </div>
            </div>
            <div class="text-xs text-gray-600">
              <p><strong>Zweck:</strong> Authentifizierung, Sitzungsverwaltung, Sicherheit</p>
              <p><strong>Cookies:</strong> session_token, csrf_token, user_preferences</p>
              <p><strong>Speicherdauer:</strong> Sitzung bis 30 Tage</p>
            </div>
          </div>

          <!-- Functional Cookies -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="text-sm font-medium text-gray-900">Funktionale Cookies</h4>
                <p class="text-xs text-gray-500 mt-1">Diese Cookies ermöglichen erweiterte Funktionen und Personalisierung.</p>
              </div>
              <div class="flex items-center">
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="cookieSettings.functional"
                    class="sr-only peer"
                  >
                  <div class="w-10 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
            <div class="text-xs text-gray-600">
              <p><strong>Zweck:</strong> Benutzereinstellungen, Sprachauswahl, Theme-Präferenzen</p>
              <p><strong>Cookies:</strong> user_theme, language_preference, ui_settings</p>
              <p><strong>Speicherdauer:</strong> 1 Jahr</p>
            </div>
          </div>

          <!-- Analytics Cookies -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="text-sm font-medium text-gray-900">Analyse-Cookies</h4>
                <p class="text-xs text-gray-500 mt-1">Diese Cookies helfen uns zu verstehen, wie Sie die Website nutzen.</p>
              </div>
              <div class="flex items-center">
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="cookieSettings.analytics"
                    class="sr-only peer"
                  >
                  <div class="w-10 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
            <div class="text-xs text-gray-600">
              <p><strong>Zweck:</strong> Nutzungsstatistiken, Performance-Monitoring, Fehleranalyse</p>
              <p><strong>Cookies:</strong> _analytics_session, _performance_data</p>
              <p><strong>Speicherdauer:</strong> 2 Jahre</p>
            </div>
          </div>

          <!-- Marketing Cookies -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-center justify-between mb-3">
              <div>
                <h4 class="text-sm font-medium text-gray-900">Marketing-Cookies</h4>
                <p class="text-xs text-gray-500 mt-1">Diese Cookies werden für personalisierte Werbung verwendet.</p>
              </div>
              <div class="flex items-center">
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="cookieSettings.marketing"
                    class="sr-only peer"
                  >
                  <div class="w-10 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-1 after:left-1 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
            <div class="text-xs text-gray-600">
              <p><strong>Zweck:</strong> Personalisierte Werbung, Remarketing, Conversion-Tracking</p>
              <p><strong>Cookies:</strong> _marketing_id, _conversion_data</p>
              <p><strong>Speicherdauer:</strong> 1 Jahr</p>
            </div>
          </div>
        </div>

        <!-- Legal Links -->
        <div class="mt-6 pt-4 border-t border-gray-200">
          <p class="text-xs text-gray-600 mb-3">
            Weitere Informationen finden Sie in unserer 
            <router-link to="/privacy" class="text-blue-600 hover:text-blue-800 underline">Datenschutzerklärung</router-link> 
            und unserem 
            <router-link to="/imprint" class="text-blue-600 hover:text-blue-800 underline">Impressum</router-link>.
          </p>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col sm:flex-row gap-3 mt-6">
          <button
            @click="acceptEssential"
            class="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200"
          >
            Nur notwendige Cookies
          </button>
          <button
            @click="saveSettings"
            class="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-200"
          >
            Auswahl speichern
          </button>
          <button
            @click="acceptAll"
            class="flex-1 px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors duration-200"
          >
            Alle akzeptieren
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'

export default {
  name: 'CookieBanner',
  setup() {
    const showBanner = ref(false)
    const showSettings = ref(false)
    const cookieSettings = ref({
      essential: true, // Immer aktiv
      functional: false,
      analytics: false,
      marketing: false
    })

    // 🍪 Cookie-Einstellungen laden
    const loadCookieSettings = () => {
      try {
        const saved = localStorage.getItem('cookie_settings')
        if (saved) {
          const settings = JSON.parse(saved)
          cookieSettings.value = { ...cookieSettings.value, ...settings }
          return true // Einstellungen gefunden
        }
      } catch (error) {
        console.warn('Cookie-Einstellungen konnten nicht geladen werden:', error)
      }
      return false // Keine Einstellungen gefunden
    }

    // 🍪 Cookie-Einstellungen speichern
    const saveCookieSettings = (settings) => {
      try {
        localStorage.setItem('cookie_settings', JSON.stringify(settings))
        localStorage.setItem('cookie_consent_date', new Date().toISOString())
        
        // 🔄 Cookie-Management anwenden
        applyCookieSettings(settings)
        
        console.log('Cookie-Einstellungen gespeichert:', settings)
      } catch (error) {
        console.error('Cookie-Einstellungen konnten nicht gespeichert werden:', error)
      }
    }

    // 🍪 Cookie-Management anwenden
    const applyCookieSettings = (settings) => {
      // Funktionale Cookies
      if (!settings.functional) {
        // Funktionale Cookies löschen
        document.cookie = 'user_theme=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
        document.cookie = 'language_preference=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
        document.cookie = 'ui_settings=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
      }

      // Analytics Cookies
      if (!settings.analytics) {
        // Analytics Cookies löschen
        document.cookie = '_analytics_session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
        document.cookie = '_performance_data=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
        
        // Analytics-Scripts deaktivieren
        if (window.gtag) {
          window.gtag('consent', 'update', {
            'analytics_storage': 'denied'
          })
        }
      } else {
        // Analytics aktivieren
        if (window.gtag) {
          window.gtag('consent', 'update', {
            'analytics_storage': 'granted'
          })
        }
      }

      // Marketing Cookies
      if (!settings.marketing) {
        // Marketing Cookies löschen
        document.cookie = '_marketing_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
        document.cookie = '_conversion_data=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
        
        // Marketing-Scripts deaktivieren
        if (window.gtag) {
          window.gtag('consent', 'update', {
            'ad_storage': 'denied',
            'ad_user_data': 'denied',
            'ad_personalization': 'denied'
          })
        }
      } else {
        // Marketing aktivieren
        if (window.gtag) {
          window.gtag('consent', 'update', {
            'ad_storage': 'granted',
            'ad_user_data': 'granted',
            'ad_personalization': 'granted'
          })
        }
      }
    }

    // ✅ Nur notwendige Cookies akzeptieren
    const acceptEssential = () => {
      const settings = {
        essential: true,
        functional: false,
        analytics: false,
        marketing: false
      }
      
      cookieSettings.value = settings
      saveCookieSettings(settings)
      showBanner.value = false
      showSettings.value = false
    }

    // ✅ Alle Cookies akzeptieren
    const acceptAll = () => {
      const settings = {
        essential: true,
        functional: true,
        analytics: true,
        marketing: true
      }
      
      cookieSettings.value = settings
      saveCookieSettings(settings)
      showBanner.value = false
      showSettings.value = false
    }

    // 💾 Benutzerdefinierte Einstellungen speichern
    const saveSettings = () => {
      saveCookieSettings(cookieSettings.value)
      showBanner.value = false
      showSettings.value = false
    }

    // 🔄 Cookie-Consent prüfen
    const checkCookieConsent = () => {
      const hasSettings = loadCookieSettings()
      
      if (!hasSettings) {
        // Kein Consent vorhanden - Banner anzeigen
        showBanner.value = true
      } else {
        // Consent vorhanden - Einstellungen anwenden
        applyCookieSettings(cookieSettings.value)
        
        // Prüfen ob Consent älter als 1 Jahr ist
        try {
          const consentDate = localStorage.getItem('cookie_consent_date')
          if (consentDate) {
            const oneYearAgo = new Date()
            oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1)
            
            if (new Date(consentDate) < oneYearAgo) {
              // Consent ist abgelaufen - Banner erneut anzeigen
              showBanner.value = true
            }
          }
        } catch (error) {
          console.warn('Cookie-Consent-Datum konnte nicht geprüft werden:', error)
        }
      }
    }

    // 🎯 Component Lifecycle
    onMounted(() => {
      // Kurze Verzögerung für bessere UX
      setTimeout(() => {
        checkCookieConsent()
      }, 1000)
    })

    // 👀 Cookie-Einstellungen überwachen
    watch(cookieSettings, (newSettings) => {
      // Automatisch anwenden wenn sich Einstellungen ändern
      if (!showBanner.value) {
        applyCookieSettings(newSettings)
      }
    }, { deep: true })

    return {
      showBanner,
      showSettings,
      cookieSettings,
      acceptEssential,
      acceptAll,
      saveSettings
    }
  }
}
</script>

<style scoped>
/* Custom Toggle Switch Styles */
.peer:checked ~ .peer-checked\:bg-blue-600 {
  background-color: #2563eb;
}

.peer:checked ~ .peer-checked\:after\:translate-x-full::after {
  transform: translateX(100%);
}

/* Animation für Banner */
.fixed.bottom-0 {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

/* Modal Animation */
.inline-block {
  animation: modalFadeIn 0.2s ease-out;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>