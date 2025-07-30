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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Dashboard
                            </router-link>
                            <router-link
                                :to="`/user/${$route.params.userId}/projects`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                <!-- Welcome Header -->
                <div class="mb-8">
                    <h1 class="text-2xl font-bold text-gray-900">Willkommen, {{ userInfo.name }}!</h1>
                    <p class="mt-1 text-sm text-gray-600">Hier ist eine Übersicht über Ihre Projekte und Speichernutzung.</p>
                </div>

                <!-- Storage Overview Card -->
                <div class="bg-white overflow-hidden shadow rounded-lg mb-8">
                    <div class="p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7c0-2.21-1.79-4-4-4H8c-2.21 0-4 1.79-4 4z"></path>
                                </svg>
                            </div>
                            <div class="ml-5 w-0 flex-1">
                                <dl>
                                    <dt class="text-sm font-medium text-gray-500 truncate">Speichernutzung</dt>
                                    <dd class="flex items-baseline">
                                        <div class="text-2xl font-semibold text-gray-900">
                                            {{ storageInfo.used_gb }} GB
                                        </div>
                                        <div class="ml-2 text-sm text-gray-500">
                                            von {{ storageInfo.limit_gb }} GB
                                        </div>
                                    </dd>
                                </dl>
                            </div>
                        </div>
                        
                        <!-- Storage Progress Bar -->
                        <div class="mt-4">
                            <div class="flex justify-between text-sm text-gray-600 mb-1">
                                <span>{{ storagePercentage }}% verwendet</span>
                                <span>{{ storageInfo.available_gb }} GB verfügbar</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-3">
                                <div 
                                    class="h-3 rounded-full transition-all duration-300"
                                    :class="getStorageBarColor()"
                                    :style="{ width: `${Math.min(storagePercentage, 100)}%` }"
                                ></div>
                            </div>
                            <div v-if="storagePercentage >= 90" class="mt-2 text-sm text-red-600">
                                ⚠️ Ihr Speicher ist fast voll. Bitte löschen Sie alte Projekte oder kontaktieren Sie Ihren Administrator.
                            </div>
                            <div v-else-if="storagePercentage >= 75" class="mt-2 text-sm text-yellow-600">
                                ⚠️ Ihr Speicher ist zu 75% gefüllt.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Stats Grid -->
                <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                    <!-- Total Projects -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Gesamt Projekte</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.total_projects }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Active Projects -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-6 w-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Aktive Projekte</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.active_projects }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Processing -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-6 w-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">In Bearbeitung</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.processing_projects }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Completed -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Abgeschlossen</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.completed_projects }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Projects -->
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Aktuelle Projekte</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">Ihre zuletzt bearbeiteten Projekte</p>
                    </div>
                    <ul class="divide-y divide-gray-200">
                        <li v-for="project in recentProjects" :key="project.id" class="px-4 py-4 sm:px-6">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 h-10 w-10">
                                        <div class="h-10 w-10 rounded-lg bg-gray-100 flex items-center justify-center">
                                            <svg class="h-6 w-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                            </svg>
                                        </div>
                                    </div>
                                    <div class="ml-4">
                                        <div class="text-sm font-medium text-gray-900">{{ project.name }}</div>
                                        <div class="text-sm text-gray-500">
                                            {{ project.size_gb }} GB • {{ formatDate(project.updated_at) }}
                                        </div>
                                    </div>
                                </div>
                                <div class="flex items-center">
                                    <span :class="[
                                        'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                                        getStatusColor(project.status)
                                    ]">
                                        {{ getStatusText(project.status) }}
                                    </span>
                                    <div class="ml-4 flex-shrink-0">
                                        <button
                                            @click="viewProject(project)"
                                            class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
                                        >
                                            Anzeigen
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </li>
                        <li v-if="recentProjects.length === 0" class="px-4 py-8 text-center">
                            <div class="text-gray-500">
                                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                                </svg>
                                <p class="mt-2 text-sm">Noch keine Projekte vorhanden</p>
                                <router-link
                                    :to="`/user/${$route.params.userId}/upload`"
                                    class="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200"
                                >
                                    Erstes Projekt erstellen
                                </router-link>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
    name: 'UserDashboard',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const userInfo = ref({
            name: 'Max Mustermann',
            email: 'max@example.com'
        })
        
        const storageInfo = ref({
            used_gb: 8.5,
            limit_gb: 15,
            available_gb: 6.5
        })
        
        const stats = ref({
            total_projects: 5,
            active_projects: 3,
            processing_projects: 1,
            completed_projects: 4
        })
        
        const recentProjects = ref([
            {
                id: 1,
                name: 'Baustellenaufnahme Nord',
                status: 'completed',
                size_gb: 2.3,
                updated_at: '2024-01-20T10:30:00Z'
            },
            {
                id: 2,
                name: 'Dachinspektion Gebäude A',
                status: 'processing',
                size_gb: 1.8,
                updated_at: '2024-01-21T14:15:00Z'
            },
            {
                id: 3,
                name: 'Landvermessung Süd',
                status: 'completed',
                size_gb: 4.2,
                updated_at: '2024-01-19T09:45:00Z'
            }
        ])
        
        const storagePercentage = computed(() => {
            return Math.round((storageInfo.value.used_gb / storageInfo.value.limit_gb) * 100)
        })
        
        const getStorageBarColor = () => {
            const percentage = storagePercentage.value
            if (percentage >= 90) return 'bg-red-500'
            if (percentage >= 75) return 'bg-yellow-500'
            return 'bg-green-500'
        }
        
        const getStatusColor = (status) => {
            switch (status) {
                case 'completed':
                    return 'bg-green-100 text-green-800'
                case 'processing':
                    return 'bg-yellow-100 text-yellow-800'
                case 'failed':
                    return 'bg-red-100 text-red-800'
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
                default:
                    return 'Unbekannt'
            }
        }
        
        const formatDate = (dateString) => {
            return new Date(dateString).toLocaleDateString('de-DE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            })
        }
        
        const viewProject = (project) => {
            router.push(`/user/${router.currentRoute.value.params.userId}/projects/${project.id}`)
        }
        
        const logout = async () => {
            try {
                await authStore.logout()
                router.push('/login')
            } catch (error) {
                console.error('Logout-Fehler:', error)
            }
        }
        
        const loadDashboardData = async () => {
            try {
                // In real app, this would load data from API
                console.log('Dashboard-Daten geladen')
            } catch (error) {
                console.error('Fehler beim Laden der Dashboard-Daten:', error)
            }
        }
        
        onMounted(() => {
            loadDashboardData()
        })
        
        return {
            userInfo,
            storageInfo,
            storagePercentage,
            stats,
            recentProjects,
            getStorageBarColor,
            getStatusColor,
            getStatusText,
            formatDate,
            viewProject,
            logout
        }
    }
}
</script>
