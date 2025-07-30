<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Neues Projekt hochladen</h1>
            <p class="mt-2 text-gray-600">
              Laden Sie Ihre Drohnenbilder hoch und erstellen Sie ein 3D-Modell
            </p>
          </div>
          <router-link
            to="/user/projects"
            class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            ← Zurück zu Projekten
          </router-link>
        </div>
      </div>

      <!-- Upload Form -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form @submit.prevent="createProject" class="space-y-8">
          <!-- Projekt-Informationen -->
          <div>
            <h2 class="text-xl font-semibold text-gray-900 mb-6">Projekt-Informationen</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Projektname *</label>
                <input
                  v-model="projectForm.name"
                  type="text"
                  required
                  placeholder="z.B. Gebäude-Scan 2024"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>
              
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-2">Beschreibung</label>
                <textarea
                  v-model="projectForm.description"
                  rows="3"
                  placeholder="Beschreiben Sie Ihr Projekt..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Projekttyp</label>
                <select
                  v-model="projectForm.project_type"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="building">Gebäude</option>
                  <option value="landscape">Landschaft</option>
                  <option value="infrastructure">Infrastruktur</option>
                  <option value="agriculture">Landwirtschaft</option>
                  <option value="other">Sonstiges</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Verarbeitungsqualität</label>
                <select
                  v-model="projectForm.processing_quality"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Niedrig (schnell)</option>
                  <option value="medium">Mittel (empfohlen)</option>
                  <option value="high">Hoch (langsam)</option>
                  <option value="ultra">Ultra (sehr langsam)</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Datei-Upload -->
          <div>
            <h2 class="text-xl font-semibold text-gray-900 mb-6">Bilder hochladen</h2>
            
            <!-- Upload-Bereich -->
            <div
              @drop="handleDrop"
              @dragover.prevent
              @dragenter.prevent
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors"
              :class="{ 'border-blue-400 bg-blue-50': isDragging }"
            >
              <div class="space-y-4">
                <div class="flex justify-center">
                  <svg class="h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </div>
                <div>
                  <p class="text-lg text-gray-600">Bilder hier ablegen oder</p>
                  <label class="cursor-pointer">
                    <span class="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                      Dateien auswählen
                    </span>
                    <input
                      ref="fileInput"
                      type="file"
                      multiple
                      accept="image/*"
                      @change="handleFileSelect"
                      class="hidden"
                    >
                  </label>
                </div>
                <p class="text-sm text-gray-500">
                  Unterstützte Formate: JPG, PNG, TIFF<br>
                  Maximale Dateigröße: {{ maxUploadSizeMB }}MB pro Datei<br>
                  Empfohlen: Mindestens 20 Bilder für beste Ergebnisse
                </p>
              </div>
            </div>

            <!-- Upload-Fortschritt -->
            <div v-if="uploadProgress > 0" class="mt-4">
              <div class="flex justify-between text-sm text-gray-600 mb-2">
                <span>Upload-Fortschritt</span>
                <span>{{ uploadProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: uploadProgress + '%' }"
                ></div>
              </div>
            </div>

            <!-- Datei-Liste -->
            <div v-if="selectedFiles.length > 0" class="mt-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">
                Ausgewählte Dateien ({{ selectedFiles.length }})
              </h3>
              <div class="max-h-64 overflow-y-auto border border-gray-200 rounded-md">
                <div v-for="(file, index) in selectedFiles" :key="index" 
                     class="flex items-center justify-between p-3 border-b border-gray-100 last:border-b-0">
                  <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                      <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ file.name }}</p>
                      <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
                    </div>
                  </div>
                  <button
                    @click="removeFile(index)"
                    class="text-red-600 hover:text-red-800"
                  >
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                  </button>
                </div>
              </div>
              
              <!-- Datei-Statistiken -->
              <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div class="bg-gray-50 p-3 rounded-md">
                  <p class="text-gray-600">Gesamtgröße</p>
                  <p class="font-medium">{{ formatFileSize(totalFileSize) }}</p>
                </div>
                <div class="bg-gray-50 p-3 rounded-md">
                  <p class="text-gray-600">Durchschnittsgröße</p>
                  <p class="font-medium">{{ formatFileSize(averageFileSize) }}</p>
                </div>
                <div class="bg-gray-50 p-3 rounded-md">
                  <p class="text-gray-600">Geschätzte Verarbeitungszeit</p>
                  <p class="font-medium">{{ estimatedProcessingTime }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Erweiterte Optionen -->
          <div>
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-xl font-semibold text-gray-900">Erweiterte Optionen</h2>
              <button
                type="button"
                @click="showAdvancedOptions = !showAdvancedOptions"
                class="text-blue-600 hover:text-blue-800 text-sm"
              >
                {{ showAdvancedOptions ? 'Ausblenden' : 'Anzeigen' }}
              </button>
            </div>
            
            <div v-if="showAdvancedOptions" class="space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">GPS-Koordinaten verwenden</label>
                  <div class="flex items-center">
                    <input
                      v-model="projectForm.use_gps"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    >
                    <span class="ml-2 text-sm text-gray-600">
                      GPS-Daten aus EXIF für Georeferenzierung nutzen
                    </span>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Automatische Optimierung</label>
                  <div class="flex items-center">
                    <input
                      v-model="projectForm.auto_optimize"
                      type="checkbox"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    >
                    <span class="ml-2 text-sm text-gray-600">
                      Automatische Bildoptimierung vor Verarbeitung
                    </span>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Mesh-Auflösung</label>
                  <select
                    v-model="projectForm.mesh_resolution"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Niedrig (2M Punkte)</option>
                    <option value="medium">Mittel (5M Punkte)</option>
                    <option value="high">Hoch (10M Punkte)</option>
                    <option value="ultra">Ultra (20M+ Punkte)</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Textur-Qualität</label>
                  <select
                    v-model="projectForm.texture_quality"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="1024">1024x1024</option>
                    <option value="2048">2048x2048</option>
                    <option value="4096">4096x4096</option>
                    <option value="8192">8192x8192</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              @click="resetForm"
              class="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Zurücksetzen
            </button>
            <button
              type="submit"
              :disabled="!canSubmit || uploading"
              class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="uploading">Wird hochgeladen...</span>
              <span v-else>Projekt erstellen</span>
            </button>
          </div>
        </form>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'UserProjectUpload',
  setup() {
    const router = useRouter()
    const store = useStore()
    
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const isDragging = ref(false)
    const showAdvancedOptions = ref(false)
    const message = ref('')
    const messageType = ref('success')
    const maxUploadSizeMB = ref(1024)

    const selectedFiles = ref([])
    const fileInput = ref(null)
    
    const projectForm = ref({
      name: '',
      description: '',
      project_type: 'building',
      processing_quality: 'medium',
      use_gps: true,
      auto_optimize: true,
      mesh_resolution: 'medium',
      texture_quality: '2048'
    })

    const totalFileSize = computed(() => {
      return selectedFiles.value.reduce((total, file) => total + file.size, 0)
    })

    const averageFileSize = computed(() => {
      if (selectedFiles.value.length === 0) return 0
      return totalFileSize.value / selectedFiles.value.length
    })

    const estimatedProcessingTime = computed(() => {
      const fileCount = selectedFiles.value.length
      const quality = projectForm.value.processing_quality
      
      let baseTime = fileCount * 2 // 2 Minuten pro Bild als Basis
      
      switch (quality) {
        case 'low': baseTime *= 0.5; break
        case 'medium': baseTime *= 1; break
        case 'high': baseTime *= 2; break
        case 'ultra': baseTime *= 4; break
      }
      
      if (baseTime < 60) return `${Math.round(baseTime)} Minuten`
      return `${Math.round(baseTime / 60)} Stunden`
    })

    const canSubmit = computed(() => {
      return projectForm.value.name.trim() && selectedFiles.value.length >= 3
    })

    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files)
      addFiles(files)
    }

    const handleDrop = (event) => {
      event.preventDefault()
      isDragging.value = false
      const files = Array.from(event.dataTransfer.files)
      addFiles(files)
    }

    const addFiles = (files) => {
      const validFiles = files.filter(file => {
        // Prüfe Dateityp
        if (!file.type.startsWith('image/')) {
          showMessage(`${file.name} ist kein gültiges Bildformat`, 'error')
          return false
        }
        
        // Prüfe Dateigröße
        const maxSize = maxUploadSizeMB.value * 1024 * 1024
        if (file.size > maxSize) {
          showMessage(`${file.name} ist zu groß (max. ${maxUploadSizeMB.value}MB)`, 'error')
          return false
        }
        
        return true
      })

      // Füge nur neue Dateien hinzu (keine Duplikate)
      validFiles.forEach(file => {
        const exists = selectedFiles.value.some(existing => 
          existing.name === file.name && existing.size === file.size
        )
        if (!exists) {
          selectedFiles.value.push(file)
        }
      })

      if (validFiles.length > 0) {
        showMessage(`${validFiles.length} Datei(en) hinzugefügt`, 'success')
      }
    }

    const removeFile = (index) => {
      selectedFiles.value.splice(index, 1)
    }

    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }

    const createProject = async () => {
      if (!canSubmit.value) return

      try {
        uploading.value = true
        uploadProgress.value = 0

        // FormData für Datei-Upload erstellen
        const formData = new FormData()
        
        // Projekt-Daten hinzufügen
        formData.append('name', projectForm.value.name)
        formData.append('description', projectForm.value.description)
        formData.append('project_type', projectForm.value.project_type)
        formData.append('processing_quality', projectForm.value.processing_quality)
        formData.append('use_gps', projectForm.value.use_gps)
        formData.append('auto_optimize', projectForm.value.auto_optimize)
        formData.append('mesh_resolution', projectForm.value.mesh_resolution)
        formData.append('texture_quality', projectForm.value.texture_quality)

        // Dateien hinzufügen
        selectedFiles.value.forEach((file, index) => {
          formData.append(`files`, file)
        })

        // Upload mit Progress-Tracking
        const response = await api.post('/user/projects', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            uploadProgress.value = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
          }
        })

        showMessage('Projekt erfolgreich erstellt und Upload gestartet!', 'success')
        
        // Nach erfolgreichem Upload zur Projekt-Übersicht
        setTimeout(() => {
          router.push('/user/projects')
        }, 2000)

      } catch (err) {
        console.error('Fehler beim Erstellen des Projekts:', err)
        showMessage(
          err.response?.data?.detail || 'Fehler beim Erstellen des Projekts',
          'error'
        )
      } finally {
        uploading.value = false
        uploadProgress.value = 0
      }
    }

    const resetForm = () => {
      projectForm.value = {
        name: '',
        description: '',
        project_type: 'building',
        processing_quality: 'medium',
        use_gps: true,
        auto_optimize: true,
        mesh_resolution: 'medium',
        texture_quality: '2048'
      }
      selectedFiles.value = []
      uploadProgress.value = 0
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const showMessage = (msg, type = 'success') => {
      message.value = msg
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 5000)
    }

    const loadUserLimits = async () => {
      try {
        const user = store.getters['auth/user']
        if (user && user.max_upload_size_mb) {
          maxUploadSizeMB.value = user.max_upload_size_mb
        }
      } catch (err) {
        console.error('Fehler beim Laden der Benutzer-Limits:', err)
      }
    }

    onMounted(() => {
      loadUserLimits()
    })

    return {
      uploading,
      uploadProgress,
      isDragging,
      showAdvancedOptions,
      message,
      messageType,
      maxUploadSizeMB,
      selectedFiles,
      fileInput,
      projectForm,
      totalFileSize,
      averageFileSize,
      estimatedProcessingTime,
      canSubmit,
      handleFileSelect,
      handleDrop,
      removeFile,
      formatFileSize,
      createProject,
      resetForm
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
