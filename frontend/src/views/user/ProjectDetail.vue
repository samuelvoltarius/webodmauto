<template>
    <div class="min-h-screen bg-gray-50">
        <!-- Navigation Header -->
        <nav class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex items-center">
                        <router-link
                            :to="`/user/${$route.params.userId}/projects`"
                            class="flex items-center text-gray-500 hover:text-gray-700"
                        >
                            <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                            </svg>
                            Zurück zu Projekten
                        </router-link>
                    </div>
                    <div class="flex items-center">
                        <div class="flex-shrink-0">
                            <button
                                @click="logout"
                                class="relative inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                            >
                                Abmelden
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div class="px-4 py-6 sm:px-0">
                <!-- Project Header -->
                <div class="mb-8">
                    <div class="flex items-center justify-between">
                        <div>
                            <h1 class="text-3xl font-bold text-gray-900">{{ project.name }}</h1>
                            <p class="mt-1 text-sm text-gray-600">{{ project.description || 'Keine Beschreibung verfügbar' }}</p>
                        </div>
                        <div class="flex items-center space-x-3">
                            <span :class="[
                                'inline-flex px-3 py-1 text-sm font-semibold rounded-full',
                                getStatusColor(project.status)
                            ]">
                                {{ getStatusText(project.status) }}
                            </span>
                            <div class="flex space-x-2">
                                <button
                                    v-if="project.status === 'processing'"
                                    @click="cancelProcessing"
                                    class="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                >
                                    Abbrechen
                                </button>
                                <button
                                    @click="deleteProject"
                                    class="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                >
                                    <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                    </svg>
                                    Löschen
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Progress Bar (nur bei processing) -->
                <div v-if="project.status === 'processing'" class="mb-8">
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Verarbeitungsfortschritt</h3>
                            <div class="flex justify-between text-sm text-gray-600 mb-2">
                                <span>{{ project.current_step || 'Verarbeitung läuft...' }}</span>
                                <span>{{ project.progress_percentage }}%</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-3">
                                <div 
                                    class="bg-blue-600 h-3 rounded-full transition-all duration-300"
                                    :style="{ width: `${project.progress_percentage}%` }"
                                ></div>
                            </div>
                            <div v-if="project.estimated_completion" class="mt-2 text-sm text-gray-500">
                                Geschätzte Fertigstellung: {{ formatDate(project.estimated_completion) }}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Error Message (bei failed) -->
                <div v-if="project.status === 'failed'" class="mb-8">
                    <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="ml-3">
                                <h3 class="text-sm font-medium text-red-800">Verarbeitungsfehler</h3>
                                <div class="mt-2 text-sm text-red-700">
                                    {{ project.error_message || 'Ein unbekannter Fehler ist aufgetreten.' }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3D Viewer (nur bei completed) -->
                <div v-if="project.status === 'completed'" class="mb-8">
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="px-6 py-4 border-b border-gray-200">
                            <div class="flex items-center justify-between">
                                <h3 class="text-lg leading-6 font-medium text-gray-900">3D-Viewer</h3>
                                <div class="flex space-x-2">
                                    <button
                                        @click="toggleFullscreen"
                                        class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                                        </svg>
                                        Vollbild
                                    </button>
                                    <button
                                        @click="openInNewTab"
                                        class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                                        </svg>
                                        Neuer Tab
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="p-0">
                            <div class="bg-gray-900 relative" style="height: 600px;">
                                <iframe 
                                    ref="viewerFrame"
                                    :src="`/api/viewer/${project.reseller_id}/${project.id}/`"
                                    class="w-full h-full border-0"
                                    :title="`3D-Viewer für ${project.name}`"
                                    @load="onViewerLoad"
                                    @error="onViewerError"
                                ></iframe>
                                <div v-if="viewerLoading" class="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75">
                                    <div class="text-center text-white">
                                        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                                        <p>3D-Modell wird geladen...</p>
                                    </div>
                                </div>
                                <div v-if="viewerError" class="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75">
                                    <div class="text-center text-white">
                                        <svg class="h-12 w-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        <p>Fehler beim Laden des 3D-Viewers</p>
                                        <button
                                            @click="reloadViewer"
                                            class="mt-2 inline-flex items-center px-3 py-2 border border-white text-sm font-medium rounded-md text-white hover:bg-white hover:text-gray-900"
                                        >
                                            Neu laden
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Project Information Grid -->
                <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
                    <!-- Project Details -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="px-6 py-4 border-b border-gray-200">
                            <h3 class="text-lg leading-6 font-medium text-gray-900">Projekt-Details</h3>
                        </div>
                        <div class="px-6 py-4">
                            <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Dateien</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ project.file_count }} Bilder</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Größe</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ formatFileSize(project.file_size_bytes) }}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Erstellt</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ formatDate(project.created_at) }}</dd>
                                </div>
                                <div v-if="project.processing_completed_at">
                                    <dt class="text-sm font-medium text-gray-500">Abgeschlossen</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ formatDate(project.processing_completed_at) }}</dd>
                                </div>
                                <div v-if="project.processing_time">
                                    <dt class="text-sm font-medium text-gray-500">Verarbeitungszeit</dt>
                                    <dd class="mt-1 text-sm text-gray-900">{{ formatDuration(project.processing_time) }}</dd>
                                </div>
                                <div>
                                    <dt class="text-sm font-medium text-gray-500">Projekt-ID</dt>
                                    <dd class="mt-1 text-sm text-gray-900 font-mono">{{ project.project_uuid }}</dd>
                                </div>
                            </dl>
                        </div>
                    </div>

                    <!-- Processing Logs -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="px-6 py-4 border-b border-gray-200">
                            <h3 class="text-lg leading-6 font-medium text-gray-900">Verarbeitungsprotokoll</h3>
                        </div>
                        <div class="px-6 py-4">
                            <div class="flow-root">
                                <ul class="-mb-8">
                                    <li v-for="(log, index) in processingLogs" :key="log.id" class="relative pb-8">
                                        <div v-if="index !== processingLogs.length - 1" class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"></div>
                                        <div class="relative flex space-x-3">
                                            <div>
                                                <span :class="[
                                                    'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white',
                                                    getLogColor(log.log_level)
                                                ]">
                                                    <svg class="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                                                    </svg>
                                                </span>
                                            </div>
                                            <div class="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                                                <div>
                                                    <p class="text-sm text-gray-900">{{ log.message }}</p>
                                                    <p class="text-xs text-gray-500">{{ log.step }}</p>
                                                </div>
                                                <div class="text-right text-sm whitespace-nowrap text-gray-500">
                                                    {{ formatDate(log.timestamp) }}
                                                </div>
                                            </div>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

export default {
    name: 'UserProjectDetail',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        const route = useRoute()
        
        const viewerFrame = ref(null)
        const viewerLoading = ref(true)
        const viewerError = ref(false)
        const refreshInterval = ref(null)
        const loading = ref(true)
        const error = ref('')
        
        // 🔄 Echte Projekt-Daten vom Backend laden
        const project = ref({})
        const processingLogs = ref([])
        
        const getStatusColor = (status) => {
            switch (status) {
                case 'completed':
                    return 'bg-green-100 text-green-800'
                case 'processing':
                    return 'bg-yellow-100 text-yellow-800'
                case 'failed':
                    return 'bg-red-100 text-red-800'
                case 'uploaded':
                    return 'bg-blue-100 text-blue-800'
                default:
                    return 'bg-gray-100 text-gray-800'
            }
        }
        
        const getStatusText = (status) => {
            switch (status) {
                case 'completed':
                    return 'Abgeschlossen'
                case 'processing':
                    return 'In Bearbeitung'
                case 'failed':
                    return 'Fehler'
                case 'uploaded':
                    return 'Hochgeladen'
                default:
                    return 'Unbekannt'
            }
        }
        
        const getLogColor = (level) => {
            switch (level) {
                case 'ERROR':
                    return 'bg-red-500'
                case 'WARNING':
                    return 'bg-yellow-500'
                case 'INFO':
                    return 'bg-green-500'
                default:
                    return 'bg-gray-500'
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
            return new Date(dateString).toLocaleDateString('de-DE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            })
        }
        
        const formatDuration = (seconds) => {
            const hours = Math.floor(seconds / 3600)
            const minutes = Math.floor((seconds % 3600) / 60)
            const secs = seconds % 60
            
            if (hours > 0) {
                return `${hours}h ${minutes}m ${secs}s`
            } else if (minutes > 0) {
                return `${minutes}m ${secs}s`
            } else {
                return `${secs}s`
            }
        }
        
        const onViewerLoad = () => {
            viewerLoading.value = false
            viewerError.value = false
        }
        
        const onViewerError = () => {
            viewerLoading.value = false
            viewerError.value = true
        }
        
        const reloadViewer = () => {
            viewerLoading.value = true
            viewerError.value = false
            if (viewerFrame.value) {
                viewerFrame.value.src = viewerFrame.value.src
            }
        }
        
        const toggleFullscreen = () => {
            if (viewerFrame.value) {
                if (!document.fullscreenElement) {
                    viewerFrame.value.parentElement.requestFullscreen()
                } else {
                    document.exitFullscreen()
                }
            }
        }
        
        const openInNewTab = () => {
            const url = `/api/viewer/${project.value.reseller_id}/${project.value.id}/`
            window.open(url, '_blank')
        }
        
        // 🛑 Verarbeitung abbrechen
        const cancelProcessing = async () => {
            if (confirm(`Möchten Sie die Verarbeitung von "${project.value.name}" wirklich abbrechen?`)) {
                try {
                    await api.post(`/user/projects/${project.value.id}/cancel`)
                    await refreshProject()
                } catch (error) {
                    console.error('Fehler beim Abbrechen:', error)
                    alert('Fehler beim Abbrechen der Verarbeitung')
                }
            }
        }
        
        // 🗑️ Projekt löschen
        const deleteProject = async () => {
            if (confirm(`Möchten Sie das Projekt "${project.value.name}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`)) {
                try {
                    await api.delete(`/user/projects/${project.value.id}`)
                    router.push(`/user/${route.params.userId}/projects`)
                } catch (error) {
                    console.error('Fehler beim Löschen:', error)
                    alert('Fehler beim Löschen des Projekts')
                }
            }
        }
        
        // 🔄 Projekt-Details vom Backend laden
        const loadProject = async () => {
            try {
                loading.value = true
                error.value = ''
                
                const projectId = route.params.projectId
                const response = await api.get(`/user/projects/${projectId}`)
                project.value = response.data
                
                // Processing-Logs laden
                const logsResponse = await api.get(`/user/projects/${projectId}/logs`)
                processingLogs.value = logsResponse.data.logs || []
                
            } catch (err) {
                console.error('Fehler beim Laden des Projekts:', err)
                error.value = 'Projekt konnte nicht geladen werden'
                
                // Zurück zur Projektliste wenn Projekt nicht gefunden
                if (err.response?.status === 404) {
                    router.push(`/user/${route.params.userId}/projects`)
                }
            } finally {
                loading.value = false
            }
        }

        // 🔄 Projekt aktualisieren
        const refreshProject = async () => {
            await loadProject()
        }
        
        const logout = async () => {
            try {
                await authStore.logout()
                router.push('/login')
            } catch (error) {
                console.error('Logout-Fehler:', error)
            }
        }
        
        // 🚀 Komponente initialisieren
        onMounted(async () => {
            await loadProject()
            
            // Auto-refresh für processing projects
            if (project.value.status === 'processing') {
                refreshInterval.value = setInterval(() => {
                    refreshProject()
                }, 10000) // Alle 10 Sekunden
            }
        })
        
        onUnmounted(() => {
            if (refreshInterval.value) {
                clearInterval(refreshInterval.value)
            }
        })
        
        return {
            project,
            processingLogs,
            loading,
            error,
            viewerFrame,
            viewerLoading,
            viewerError,
            getStatusColor,
            getStatusText,
            getLogColor,
            formatFileSize,
            formatDate,
            formatDuration,
            onViewerLoad,
            onViewerError,
            reloadViewer,
            toggleFullscreen,
            openInNewTab,
            cancelProcessing,
            deleteProject,
            refreshProject,
            logout
        }
    }
}
</script>
