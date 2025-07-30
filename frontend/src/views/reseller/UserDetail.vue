<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Benutzer-Details</h1>
            <p class="mt-2 text-gray-600">
              Verwalten Sie die Details und Einstellungen für diesen Benutzer
            </p>
          </div>
          <router-link
            to="/reseller/users"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            ← Zurück zur Übersicht
          </router-link>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">Fehler beim Laden</h3>
            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- User Details -->
      <div v-else-if="user" class="space-y-8">
        <!-- Benutzer-Informationen -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold text-gray-900">Benutzer-Informationen</h2>
            <div class="flex items-center space-x-2">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
              </span>
              <span v-if="user.email_verified" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                E-Mail verifiziert
              </span>
            </div>
          </div>

          <form @submit.prevent="updateUser" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Benutzername -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Benutzername</label>
                <input
                  v-model="userForm.username"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>

              <!-- E-Mail -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">E-Mail-Adresse</label>
                <input
                  v-model="userForm.email"
                  type="email"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>

              <!-- Vollständiger Name -->
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Vollständiger Name</label>
                <input
                  v-model="userForm.full_name"
                  type="text"
                  required
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>

              <!-- Maximale Projekte -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Maximale Projekte</label>
                <input
                  v-model.number="userForm.max_projects"
                  type="number"
                  min="1"
                  max="100"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>

              <!-- Upload-Limit -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Upload-Limit (MB)</label>
                <input
                  v-model.number="userForm.max_upload_size_mb"
                  type="number"
                  min="1"
                  max="10240"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>

              <!-- Speicherlimit -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Speicherlimit (GB)</label>
                <input
                  v-model.number="userForm.storage_limit_gb"
                  type="number"
                  min="1"
                  max="1000"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>

              <!-- Status -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  v-model="userForm.is_active"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option :value="true">Aktiv</option>
                  <option :value="false">Inaktiv</option>
                </select>
              </div>
            </div>

            <!-- DSGVO-Informationen -->
            <div class="border-t border-gray-200 pt-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">DSGVO-Informationen</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">DSGVO-Zustimmung</label>
                  <div class="flex items-center">
                    <input
                      v-model="userForm.gdpr_consent"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    >
                    <span class="ml-2 text-sm text-gray-600">
                      Benutzer hat der Datenverarbeitung zugestimmt
                    </span>
                  </div>
                </div>
                <div v-if="user.gdpr_consent_date">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Zustimmungsdatum</label>
                  <p class="text-sm text-gray-600">{{ formatDate(user.gdpr_consent_date) }}</p>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
              <button
                type="button"
                @click="resetPassword"
                class="px-6 py-2 border border-yellow-300 text-yellow-700 rounded-md hover:bg-yellow-50 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              >
                Passwort zurücksetzen
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <span v-if="saving">Speichern...</span>
                <span v-else>Änderungen speichern</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Benutzer-Projekte -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900">Projekte des Benutzers</h2>
          </div>
          
          <div v-if="projects.length === 0" class="p-6 text-center text-gray-500">
            Dieser Benutzer hat noch keine Projekte erstellt.
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Projekt
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dateien
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Erstellt
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Aktionen
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="project in projects" :key="project.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div class="text-sm font-medium text-gray-900">{{ project.name }}</div>
                      <div class="text-sm text-gray-500">{{ project.description || 'Keine Beschreibung' }}</div>
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getProjectStatusClass(project.status)">
                      {{ getProjectStatusText(project.status) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ project.file_count || 0 }} Dateien
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(project.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      @click="viewProject(project)"
                      class="text-blue-600 hover:text-blue-900"
                    >
                      Anzeigen
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Aktivitäts-Log -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900">Letzte Aktivitäten</h2>
          </div>
          <div class="p-6">
            <div class="space-y-4">
              <div v-for="activity in activities" :key="activity.id" class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                  <div class="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <svg class="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="flex-1">
                  <p class="text-sm text-gray-900">{{ activity.description }}</p>
                  <p class="text-xs text-gray-500">{{ formatDate(activity.timestamp) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Success/Error Messages -->
      <div v-if="message" class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg"
           :class="messageType === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'ResellerUserDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    
    const loading = ref(true)
    const saving = ref(false)
    const error = ref('')
    const message = ref('')
    const messageType = ref('success')

    const user = ref(null)
    const projects = ref([])
    const activities = ref([])
    
    const userForm = ref({
      username: '',
      email: '',
      full_name: '',
      max_projects: 10,
      max_upload_size_mb: 1024,
      storage_limit_gb: 10,
      is_active: true,
      gdpr_consent: false
    })

    const loadUserDetails = async () => {
      try {
        loading.value = true
        const userId = route.params.id
        const currentUser = store.getters['auth/user']
        
        if (!currentUser || !currentUser.reseller_id) {
          throw new Error('Reseller-ID nicht gefunden')
        }

        // User-Details laden
        const response = await api.get(`/admin/resellers/${currentUser.reseller_id}/users/${userId}`)
        user.value = response.data
        
        // Form mit User-Daten füllen
        userForm.value = {
          username: user.value.username,
          email: user.value.email,
          full_name: user.value.full_name,
          max_projects: user.value.max_projects,
          max_upload_size_mb: user.value.max_upload_size_mb,
          storage_limit_gb: user.value.storage_limit_gb || 10,
          is_active: user.value.is_active,
          gdpr_consent: user.value.gdpr_consent
        }

        // Projekte laden (Mock-Daten für Demo)
        projects.value = [
          {
            id: 1,
            name: 'Gebäude-Scan 2024',
            description: '3D-Scan eines Bürogebäudes',
            status: 'completed',
            file_count: 45,
            created_at: '2024-01-15T10:30:00Z'
          },
          {
            id: 2,
            name: 'Landschaftsaufnahme',
            description: 'Drohnenaufnahmen für Landschaftsplanung',
            status: 'processing',
            file_count: 120,
            created_at: '2024-01-20T14:15:00Z'
          }
        ]

        // Aktivitäten laden (Mock-Daten für Demo)
        activities.value = [
          {
            id: 1,
            description: 'Benutzer hat sich angemeldet',
            timestamp: '2024-01-25T09:15:00Z'
          },
          {
            id: 2,
            description: 'Neues Projekt "Gebäude-Scan 2024" erstellt',
            timestamp: '2024-01-24T16:30:00Z'
          },
          {
            id: 3,
            description: 'Profil aktualisiert',
            timestamp: '2024-01-23T11:45:00Z'
          }
        ]

      } catch (err) {
        console.error('Fehler beim Laden der Benutzer-Details:', err)
        error.value = err.response?.data?.detail || 'Fehler beim Laden der Benutzer-Details'
      } finally {
        loading.value = false
      }
    }

    const updateUser = async () => {
      try {
        saving.value = true
        const userId = route.params.id
        const currentUser = store.getters['auth/user']

        await api.put(`/admin/resellers/${currentUser.reseller_id}/users/${userId}`, userForm.value)
        
        showMessage('Benutzer erfolgreich aktualisiert', 'success')
        await loadUserDetails()
      } catch (err) {
        console.error('Fehler beim Aktualisieren:', err)
        showMessage('Fehler beim Aktualisieren', 'error')
      } finally {
        saving.value = false
      }
    }

    const resetPassword = async () => {
      if (!confirm('Möchten Sie wirklich ein neues Passwort für diesen Benutzer generieren?')) {
        return
      }

      try {
        const userId = route.params.id
        const currentUser = store.getters['auth/user']
        
        const response = await api.post(`/admin/resellers/${currentUser.reseller_id}/users/${userId}/reset-password`)
        
        alert(`Neues Passwort: ${response.data.new_password}\n\nBitte leiten Sie dieses Passwort sicher an den Benutzer weiter.`)
        showMessage('Passwort erfolgreich zurückgesetzt', 'success')
      } catch (err) {
        console.error('Fehler beim Zurücksetzen des Passworts:', err)
        showMessage('Fehler beim Zurücksetzen des Passworts', 'error')
      }
    }

    const viewProject = (project) => {
      // Navigation zum Projekt-Detail
      router.push(`/user/projects/${project.id}`)
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('de-DE')
    }

    const getProjectStatusClass = (status) => {
      switch (status) {
        case 'completed': return 'bg-green-100 text-green-800'
        case 'processing': return 'bg-yellow-100 text-yellow-800'
        case 'failed': return 'bg-red-100 text-red-800'
        default: return 'bg-gray-100 text-gray-800'
      }
    }

    const getProjectStatusText = (status) => {
      switch (status) {
        case 'completed': return 'Abgeschlossen'
        case 'processing': return 'In Bearbeitung'
        case 'failed': return 'Fehlgeschlagen'
        case 'uploaded': return 'Hochgeladen'
        default: return 'Unbekannt'
      }
    }

    const showMessage = (msg, type = 'success') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 5000)
    }

    onMounted(() => {
      loadUserDetails()
    })

    return {
      loading,
      saving,
      error,
      message,
      messageType,
      user,
      projects,
      activities,
      userForm,
      updateUser,
      resetPassword,
      viewProject,
      formatDate,
      getProjectStatusClass,
      getProjectStatusText
    }
  }
}
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
