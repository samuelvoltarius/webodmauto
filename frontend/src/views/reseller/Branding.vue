<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">White-Label Branding</h1>
        <p class="mt-2 text-gray-600">
          Passen Sie das Erscheinungsbild Ihrer ChiliView-Instanz für Ihre Benutzer an
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Main Content -->
      <div v-else class="space-y-8">
        <!-- Preview Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Live-Vorschau</h2>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-6" :style="previewStyles">
            <div class="flex items-center space-x-4 mb-4">
              <img v-if="brandingData.logo_url" :src="brandingData.logo_url" alt="Logo" class="h-12 w-auto">
              <div v-else class="h-12 w-12 bg-gray-300 rounded flex items-center justify-center">
                <svg class="h-6 w-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
              </div>
              <div>
                <h3 class="text-lg font-semibold">{{ brandingData.company_name || 'Ihr Firmenname' }}</h3>
                <p class="text-sm opacity-75">{{ brandingData.welcome_message || 'Willkommen bei ChiliView' }}</p>
              </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <button class="px-4 py-2 rounded font-medium text-white" :style="{ backgroundColor: brandingData.primary_color }">
                Primäre Aktion
              </button>
              <button class="px-4 py-2 rounded font-medium text-white" :style="{ backgroundColor: brandingData.secondary_color }">
                Sekundäre Aktion
              </button>
            </div>
          </div>
        </div>

        <!-- Branding Form -->
        <form @submit.prevent="saveBranding" class="space-y-8">
          <!-- Logo & Farben -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Logo & Farben</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Logo URL -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Logo URL</label>
                <input
                  v-model="brandingData.logo_url"
                  type="url"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://example.com/logo.png"
                >
                <p class="mt-1 text-xs text-gray-500">Empfohlene Größe: 200x60px, Format: PNG/SVG</p>
              </div>

              <!-- Homepage URL -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Homepage URL</label>
                <input
                  v-model="brandingData.homepage_url"
                  type="url"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://ihre-website.de"
                >
              </div>

              <!-- Primärfarbe -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Primärfarbe</label>
                <div class="flex space-x-2">
                  <input
                    v-model="brandingData.primary_color"
                    type="color"
                    class="h-10 w-16 border border-gray-300 rounded cursor-pointer"
                  >
                  <input
                    v-model="brandingData.primary_color"
                    type="text"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="#007bff"
                  >
                </div>
              </div>

              <!-- Sekundärfarbe -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Sekundärfarbe</label>
                <div class="flex space-x-2">
                  <input
                    v-model="brandingData.secondary_color"
                    type="color"
                    class="h-10 w-16 border border-gray-300 rounded cursor-pointer"
                  >
                  <input
                    v-model="brandingData.secondary_color"
                    type="text"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="#6c757d"
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- Texte & Nachrichten -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Texte & Nachrichten</h3>
            <div class="space-y-4">
              <!-- Willkommensnachricht -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Willkommensnachricht</label>
                <textarea
                  v-model="brandingData.welcome_message"
                  rows="3"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Willkommen bei unserem 3D-Photogrammetrie Service..."
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Rechtliche Angaben -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Rechtliche Angaben (DSGVO-konform)</h3>
            <div class="space-y-6">
              <!-- Impressum -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Impressum
                  <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="brandingData.imprint"
                  rows="8"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Firmenname&#10;Geschäftsführer: Max Mustermann&#10;Adresse: Musterstraße 1, 12345 Musterstadt&#10;Telefon: +49 123 456789&#10;E-Mail: info@example.com&#10;Handelsregister: HRB 12345&#10;Umsatzsteuer-ID: DE123456789"
                  required
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">Rechtlich erforderlich nach §5 TMG</p>
              </div>

              <!-- Datenschutzerklärung -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Datenschutzerklärung
                  <span class="text-red-500">*</span>
                </label>
                <textarea
                  v-model="brandingData.privacy_policy"
                  rows="12"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="1. Datenschutz auf einen Blick&#10;&#10;Allgemeine Hinweise&#10;Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert...&#10;&#10;2. Allgemeine Hinweise und Pflichtinformationen&#10;&#10;Datenschutz&#10;Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst..."
                  required
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">Rechtlich erforderlich nach DSGVO Art. 13</p>
              </div>
            </div>
          </div>

          <!-- Erweiterte Anpassungen -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Erweiterte Anpassungen</h3>
            <div class="space-y-6">
              <!-- Custom CSS -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Benutzerdefiniertes CSS</label>
                <textarea
                  v-model="brandingData.custom_css"
                  rows="6"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder="/* Ihre benutzerdefinierten CSS-Regeln */&#10;.custom-header {&#10;  background: linear-gradient(45deg, #your-color1, #your-color2);&#10;}"
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">Erweiterte CSS-Anpassungen für Ihr Branding</p>
              </div>

              <!-- Custom HTML -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Benutzerdefiniertes HTML (Footer)</label>
                <textarea
                  v-model="brandingData.custom_html"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder="<!-- Zusätzliche HTML-Elemente für den Footer -->&#10;<div class='custom-footer'>&#10;  <p>© 2024 Ihr Firmenname. Alle Rechte vorbehalten.</p>&#10;</div>"
                ></textarea>
                <p class="mt-1 text-xs text-gray-500">HTML-Code für Footer oder zusätzliche Elemente</p>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              @click="resetToDefaults"
              class="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Zurücksetzen
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <span v-if="saving">Speichern...</span>
              <span v-else>Branding speichern</span>
            </button>
          </div>
        </form>
      </div>

      <!-- Success Message -->
      <div v-if="showSuccess" class="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg">
        ✅ Branding erfolgreich gespeichert!
      </div>

      <!-- Error Message -->
      <div v-if="error" class="fixed bottom-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg">
        ❌ {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'ResellerBranding',
  setup() {
    const store = useStore()
    const loading = ref(true)
    const saving = ref(false)
    const showSuccess = ref(false)
    const error = ref('')

    const brandingData = ref({
      company_name: '',
      logo_url: '',
      homepage_url: '',
      primary_color: '#007bff',
      secondary_color: '#6c757d',
      welcome_message: '',
      imprint: '',
      privacy_policy: '',
      custom_css: '',
      custom_html: ''
    })

    const previewStyles = computed(() => ({
      backgroundColor: brandingData.value.primary_color + '10',
      borderColor: brandingData.value.primary_color + '30'
    }))

    const loadBrandingData = async () => {
      try {
        loading.value = true
        const user = store.getters['auth/user']
        
        if (user && user.reseller_id) {
          const response = await api.get(`/admin/resellers/${user.reseller_id}`)
          
          // Branding-Daten aus der API-Antwort extrahieren
          const data = response.data
          brandingData.value = {
            company_name: data.company_name || '',
            logo_url: data.logo_url || '',
            homepage_url: data.homepage_url || '',
            primary_color: data.primary_color || '#007bff',
            secondary_color: data.secondary_color || '#6c757d',
            welcome_message: data.welcome_message || '',
            imprint: data.imprint || '',
            privacy_policy: data.privacy_policy || '',
            custom_css: data.custom_css || '',
            custom_html: data.custom_html || ''
          }
        }
      } catch (err) {
        console.error('Fehler beim Laden der Branding-Daten:', err)
        error.value = 'Fehler beim Laden der Branding-Daten'
      } finally {
        loading.value = false
      }
    }

    const saveBranding = async () => {
      try {
        saving.value = true
        error.value = ''
        
        const user = store.getters['auth/user']
        if (!user || !user.reseller_id) {
          throw new Error('Reseller-ID nicht gefunden')
        }

        // Validierung
        if (!brandingData.value.imprint.trim()) {
          throw new Error('Impressum ist erforderlich')
        }
        
        if (!brandingData.value.privacy_policy.trim()) {
          throw new Error('Datenschutzerklärung ist erforderlich')
        }

        // API-Call zum Speichern
        await api.put(`/admin/resellers/${user.reseller_id}`, {
          company: brandingData.value.company_name,
          logo_url: brandingData.value.logo_url,
          homepage_url: brandingData.value.homepage_url,
          primary_color: brandingData.value.primary_color,
          secondary_color: brandingData.value.secondary_color,
          welcome_message: brandingData.value.welcome_message,
          imprint: brandingData.value.imprint,
          privacy_policy: brandingData.value.privacy_policy,
          custom_css: brandingData.value.custom_css,
          custom_html: brandingData.value.custom_html
        })

        showSuccess.value = true
        setTimeout(() => {
          showSuccess.value = false
        }, 3000)

      } catch (err) {
        console.error('Fehler beim Speichern:', err)
        error.value = err.response?.data?.detail || err.message || 'Fehler beim Speichern'
        setTimeout(() => {
          error.value = ''
        }, 5000)
      } finally {
        saving.value = false
      }
    }

    const resetToDefaults = () => {
      brandingData.value = {
        company_name: brandingData.value.company_name, // Firmenname beibehalten
        logo_url: '',
        homepage_url: '',
        primary_color: '#007bff',
        secondary_color: '#6c757d',
        welcome_message: '',
        imprint: brandingData.value.imprint, // Rechtliche Angaben beibehalten
        privacy_policy: brandingData.value.privacy_policy,
        custom_css: '',
        custom_html: ''
      }
    }

    onMounted(() => {
      loadBrandingData()
    })

    return {
      loading,
      saving,
      showSuccess,
      error,
      brandingData,
      previewStyles,
      saveBranding,
      resetToDefaults
    }
  }
}
</script>

<style scoped>
/* Zusätzliche Styles für bessere UX */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive Anpassungen */
@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: 1fr;
  }
}
</style>
