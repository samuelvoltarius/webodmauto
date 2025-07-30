<template>
    <div class="min-h-screen bg-gray-50">
        <!-- Navigation Header -->
        <nav class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex">
                        <div class="flex-shrink-0 flex items-center">
                            <h1 class="text-xl font-semibold text-gray-900">ChiliView</h1>
                        </div>
                        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                            <router-link
                                :to="`/user/${$route.params.userId}/dashboard`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Dashboard
                            </router-link>
                            <router-link
                                :to="`/user/${$route.params.userId}/projects`"
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Projekte
                            </router-link>
                            <router-link
                                :to="`/user/${$route.params.userId}/upload`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Upload
                            </router-link>
                            <router-link
                                :to="`/user/${$route.params.userId}/profile`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Profil
                            </router-link>
                        </div>
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
                <!-- Header -->
                <div class="mb-8">
                    <h1 class="text-2xl font-bold text-gray-900">Meine Projekte</h1>
                    <p class="mt-1 text-sm text-gray-600">Verwalten Sie Ihre 3D-Modellierungsprojekte</p>
                </div>

                <!-- Loading State -->
                <div v-if="loading" class="flex justify-center items-center py-12">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>

                <!-- Error State -->
                <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">Fehler beim Laden</h3>
                            <p class="mt-1 text-sm text-red-700">{{ error }}</p>
                            <div class="mt-4">
                                <button
                                    @click="refreshProjects"
                                    class="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200"
                                >
                                    Erneut versuchen
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Projects Grid -->
                <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                    <div v-for="project in projects" :key="project.id" class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="h-12 w-12 rounded-lg bg-indigo-100 flex items-center justify-center">
                                        <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">{{ project.name }}</dt>
                                        <dd class="flex items-baseline">
                                            <div class="text-lg font-semibold text-gray-900">
                                                {{ project.file_count }} Dateien
                                            </div>
                                            <div class="ml-2 text-sm text-gray-500">
                                                {{ formatFileSize(project.file_size_bytes) }}
                                            </div>
                                        </dd>
                                    </dl>
                                </div>
                            </div>
                            
                            <!-- Status Badge -->
                            <div class="mt-4">
                                <span :class="[
                                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                                    getStatusColor(project.status)
                                ]">
                                    {{ getStatusText(project.status) }}
                                </span>
                            </div>

                            <!-- Progress Bar (nur bei processing) -->
                            <div v-if="project.status === 'processing'" class="mt-4">
                                <div class="flex justify-between text-sm text-gray-600 mb-1">
                                    <span>Fortschritt</span>
                                    <span>{{ project.progress_percentage }}%</span>
                                </div>
                                <div class="w-full bg-gray-200 rounded-full h-2">
                                    <div 
                                        class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                        :style="{ width: `${project.progress_percentage}%` }"
                                    ></div>
                                </div>
                            </div>

                            <!-- 3D Viewer Preview (nur bei completed) -->
                            <div v-if="project.status === 'completed'" class="mt-4">
                                <div class="bg-gray-900 rounded-lg overflow-hidden" style="height: 200px;">
                                    <iframe 
                                        :src="`/api/viewer/${project.reseller_id}/${project.id}/`"
                                        class="w-full h-full border-0"
                                        :title="`3D-Viewer für ${project.name}`"
                                        loading="lazy"
                                        @load="onViewerLoad(project.id)"
                                        @error="onViewerError(project.id)"
                                    ></iframe>
                                </div>
                            </div>

                            <!-- Action Buttons -->
                            <div class="mt-6 flex justify-between">
                                <div class="flex space-x-2">
                                    <button
                                        v-if="project.status === 'completed'"
                                        @click="openFullViewer(project)"
                                        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                                        </svg>
                                        3D-Viewer
                                    </button>
                                    <button
                                        @click="viewDetails(project)"
                                        class="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                    >
                                        Details
                                    </button>
                                </div>
                                <div class="flex space-x-2">
                                    <button
                                        v-if="project.status === 'processing'"
                                        @click="cancelProcessing(project)"
                                        class="inline-flex items-center px-3 py-2 border border-red-300 text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                    >
                                        Abbrechen
                                    </button>
                                    <button
                                        @click="deleteProject(project)"
                                        class="inline-flex items-center px-3 py-2 border border-red-300 text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                    >
                                        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                        </svg>
                                        Löschen
                                    </button>
                                </div>
                            </div>

                            <!-- Created Date -->
                            <div class="mt-4 text-xs text-gray-500">
                                Erstellt am {{ formatDate(project.created_at) }}
                            </div>
                        </div>
                    </div>

                    <!-- Empty State -->
                    <div v-if="projects.length === 0" class="col-span-full">
                        <div class="text-center py-12">
                            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                            </svg>
                            <h3 class="mt-2 text-sm font-medium text-gray-900">Keine Projekte</h3>
                            <p class="mt-1 text-sm text-gray-500">Erstellen Sie Ihr erstes 3D-Modellierungsprojekt.</p>
                            <div class="mt-6">
                                <router-link
                                    :to="`/user/${$route.params.userId}/upload`"
                                    class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                                    </svg>
                                    Neues Projekt
                                </router-link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Full Screen Viewer Modal -->
        <div v-if="showFullViewer" class="fixed inset-0 z-50 overflow-hidden">
            <div class="absolute inset-0 bg-black bg-opacity-75" @click="closeFullViewer"></div>
            <div class="relative w-full h-full">
                <div class="absolute top-4 right-4 z-10">
                    <button
                        @click="closeFullViewer"
                        class="bg-white bg-opacity-20 hover:bg-opacity-30 text-white p-2 rounded-full"
                    >
                        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <iframe 
                    v-if="selectedProject"
                    :src="`/api/viewer/${selectedProject.reseller_id}/${selectedProject.id}/`"
                    class="w-full h-full border-0"
                    :title="`3D-Viewer für ${selectedProject.name}`"
                ></iframe>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/services/api'

export default {
    name: 'UserProjects',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        // 🔄 Echte Projekte vom Backend laden
        const projects = ref([])
        const loading = ref(true)
        const error = ref('')
        
        const showFullViewer = ref(false)
        const selectedProject = ref(null)
        const refreshInterval = ref(null)
        
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
        
        const openFullViewer = (project) => {
            selectedProject.value = project
            showFullViewer.value = true
        }
        
        const closeFullViewer = () => {
            showFullViewer.value = false
            selectedProject.value = null
        }
        
        const viewDetails = (project) => {
            router.push(`/user/${router.currentRoute.value.params.userId}/projects/${project.id}`)
        }
        
        // 🛑 Verarbeitung abbrechen
        const cancelProcessing = async (project) => {
            if (confirm(`Möchten Sie die Verarbeitung von "${project.name}" wirklich abbrechen?`)) {
                try {
                    await api.post(`/user/projects/${project.id}/cancel`)
                    await refreshProjects()
                } catch (error) {
                    console.error('Fehler beim Abbrechen:', error)
                    alert('Fehler beim Abbrechen der Verarbeitung')
                }
            }
        }
        
        // 🗑️ Projekt löschen
        const deleteProject = async (project) => {
            if (confirm(`Möchten Sie das Projekt "${project.name}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.`)) {
                try {
                    await api.delete(`/user/projects/${project.id}`)
                    await refreshProjects()
                } catch (error) {
                    console.error('Fehler beim Löschen:', error)
                    alert('Fehler beim Löschen des Projekts')
                }
            }
        }
        
        const onViewerLoad = (projectId) => {
            console.log('Viewer geladen für Projekt:', projectId)
        }
        
        const onViewerError = (projectId) => {
            console.error('Viewer-Fehler für Projekt:', projectId)
        }
        
        // 🔄 Projekte vom Backend laden
        const loadProjects = async () => {
            try {
                loading.value = true
                error.value = ''
                
                const response = await api.get('/user/projects')
                projects.value = response.data.projects || []
                
            } catch (err) {
                console.error('Fehler beim Laden der Projekte:', err)
                error.value = 'Projekte konnten nicht geladen werden'
                projects.value = []
            } finally {
                loading.value = false
            }
        }

        // 🔄 Projekte aktualisieren
        const refreshProjects = async () => {
            await loadProjects()
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
            await loadProjects()
            
            // Auto-refresh für processing projects
            refreshInterval.value = setInterval(() => {
                const hasProcessing = projects.value.some(p => p.status === 'processing')
                if (hasProcessing) {
                    refreshProjects()
                }
            }, 30000) // Alle 30 Sekunden
        })
        
        onUnmounted(() => {
            if (refreshInterval.value) {
                clearInterval(refreshInterval.value)
            }
        })
        
        return {
            projects,
            loading,
            error,
            showFullViewer,
            selectedProject,
            getStatusColor,
            getStatusText,
            formatFileSize,
            formatDate,
            openFullViewer,
            closeFullViewer,
            viewDetails,
            cancelProcessing,
            deleteProject,
            onViewerLoad,
            onViewerError,
            refreshProjects,
            logout
        }
    }
}
</script>
