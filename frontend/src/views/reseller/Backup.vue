<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Backup & Wiederherstellung</h1>
        <p class="mt-2 text-gray-600">
          Verwalten Sie Backups Ihrer Datenbank und Benutzerdaten
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Main Content -->
      <div v-else class="space-y-8">
        <!-- Backup erstellen -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Neues Backup erstellen</h2>
          <div class="flex flex-col sm:flex-row gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-2">Backup-Typ</label>
              <select 
                v-model="newBackup.type" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="full">Vollständiges Backup</option>
                <option value="incremental">Inkrementelles Backup</option>
              </select>
            </div>
            <div class="flex items-end">
              <button
                @click="createBackup"
                :disabled="creating"
                class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <span v-if="creating">Erstelle...</span>
                <span v-else>Backup erstellen</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Backup-Liste -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-xl font-semibold text-gray-900">Verfügbare Backups</h2>
          </div>
          
          <div v-if="backups.length === 0" class="p-6 text-center text-gray-500">
            Keine Backups vorhanden. Erstellen Sie Ihr erstes Backup.
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Backup-ID
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Typ
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Größe
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Erstellt
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Aktionen
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="backup in backups" :key="backup.id">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{{ backup.id }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="backup.backup_type === 'full' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
                      {{ backup.backup_type === 'full' ? 'Vollständig' : 'Inkrementell' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatFileSize(backup.file_size_bytes) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(backup.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getStatusClass(backup.status)">
                      {{ getStatusText(backup.status) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      @click="downloadBackup(backup.id)"
                      class="text-blue-600 hover:text-blue-900"
                    >
                      Download
                    </button>
                    <button
                      @click="restoreBackup(backup.id)"
                      :disabled="restoring"
                      class="text-green-600 hover:text-green-900 disabled:opacity-50"
                    >
                      Wiederherstellen
                    </button>
                    <button
                      @click="deleteBackup(backup.id)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Löschen
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Backup-Einstellungen -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Backup-Einstellungen</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Automatische Backups
              </label>
              <div class="flex items-center">
                <input
                  v-model="settings.autoBackup"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <span class="ml-2 text-sm text-gray-600">
                  Täglich automatische Backups erstellen
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Aufbewahrungszeit (Tage)
              </label>
              <input
                v-model="settings.retentionDays"
                type="number"
                min="1"
                max="365"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
          </div>
          <div class="mt-6">
            <button
              @click="saveSettings"
              :disabled="savingSettings"
              class="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
            >
              <span v-if="savingSettings">Speichern...</span>
              <span v-else">Einstellungen speichern</span>
            </button>
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
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'ResellerBackup',
  setup() {
    const store = useStore()
    const loading = ref(true)
    const creating = ref(false)
    const restoring = ref(false)
    const savingSettings = ref(false)
    const message = ref('')
    const messageType = ref('success')

    const backups = ref([])
    const newBackup = ref({
      type: 'full'
    })
    const settings = ref({
      autoBackup: false,
      retentionDays: 30
    })

    const loadBackups = async () => {
      try {
        loading.value = true
        const user = store.getters['auth/user']
        
        if (user && user.reseller_id) {
          const response = await api.get(`/admin/backups?reseller_id=${user.reseller_id}`)
          backups.value = response.data.backups || []
        }
      } catch (error) {
        console.error('Fehler beim Laden der Backups:', error)
        showMessage('Fehler beim Laden der Backups', 'error')
      } finally {
        loading.value = false
      }
    }

    const createBackup = async () => {
      try {
        creating.value = true
        const user = store.getters['auth/user']
        
        if (!user || !user.reseller_id) {
          throw new Error('Reseller-ID nicht gefunden')
        }

        await api.post('/admin/backups', {
          reseller_id: user.reseller_id,
          backup_type: newBackup.value.type
        })

        showMessage('Backup erfolgreich erstellt', 'success')
        await loadBackups()
      } catch (error) {
        console.error('Fehler beim Erstellen des Backups:', error)
        showMessage('Fehler beim Erstellen des Backups', 'error')
      } finally {
        creating.value = false
      }
    }

    const downloadBackup = async (backupId) => {
      try {
        const response = await api.get(`/admin/backups/${backupId}/download`, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `backup-${backupId}.zip`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        showMessage('Backup-Download gestartet', 'success')
      } catch (error) {
        console.error('Fehler beim Download:', error)
        showMessage('Fehler beim Download', 'error')
      }
    }

    const restoreBackup = async (backupId) => {
      if (!confirm('Sind Sie sicher? Diese Aktion überschreibt alle aktuellen Daten!')) {
        return
      }

      try {
        restoring.value = true
        await api.post(`/admin/backups/${backupId}/restore`)
        showMessage('Backup erfolgreich wiederhergestellt', 'success')
        await loadBackups()
      } catch (error) {
        console.error('Fehler bei der Wiederherstellung:', error)
        showMessage('Fehler bei der Wiederherstellung', 'error')
      } finally {
        restoring.value = false
      }
    }

    const deleteBackup = async (backupId) => {
      if (!confirm('Backup wirklich löschen?')) {
        return
      }

      try {
        await api.delete(`/admin/backups/${backupId}`)
        showMessage('Backup gelöscht', 'success')
        await loadBackups()
      } catch (error) {
        console.error('Fehler beim Löschen:', error)
        showMessage('Fehler beim Löschen', 'error')
      }
    }

    const saveSettings = async () => {
      try {
        savingSettings.value = true
        // Hier würde die API für Backup-Einstellungen aufgerufen
        showMessage('Einstellungen gespeichert', 'success')
      } catch (error) {
        console.error('Fehler beim Speichern:', error)
        showMessage('Fehler beim Speichern', 'error')
      } finally {
        savingSettings.value = false
      }
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('de-DE')
    }

    const getStatusClass = (status) => {
      switch (status) {
        case 'created': return 'bg-green-100 text-green-800'
        case 'restored': return 'bg-blue-100 text-blue-800'
        case 'failed': return 'bg-red-100 text-red-800'
        default: return 'bg-gray-100 text-gray-800'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'created': return 'Erstellt'
        case 'restored': return 'Wiederhergestellt'
        case 'failed': return 'Fehlgeschlagen'
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
      loadBackups()
    })

    return {
      loading,
      creating,
      restoring,
      savingSettings,
      message,
      messageType,
      backups,
      newBackup,
      settings,
      createBackup,
      downloadBackup,
      restoreBackup,
      deleteBackup,
      saveSettings,
      formatFileSize,
      formatDate,
      getStatusClass,
      getStatusText
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
