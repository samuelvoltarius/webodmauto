<template>
    <div class="min-h-screen bg-gray-50">
        <!-- Navigation Header -->
        <nav class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex">
                        <div class="flex-shrink-0 flex items-center">
                            <h1 class="text-xl font-semibold text-gray-900">ChiliView Reseller</h1>
                        </div>
                        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                            <router-link
                                :to="`/reseller/${$route.params.resellerId}/dashboard`"
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Dashboard
                            </router-link>
                            <router-link
                                :to="`/reseller/${$route.params.resellerId}/users`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Benutzer
                            </router-link>
                            <router-link
                                :to="`/reseller/${$route.params.resellerId}/branding`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Branding
                            </router-link>
                            <router-link
                                :to="`/reseller/${$route.params.resellerId}/settings`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Einstellungen
                            </router-link>
                            <router-link
                                :to="`/reseller/${$route.params.resellerId}/backup`"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Backup
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
                    <h1 class="text-2xl font-bold text-gray-900">Willkommen, {{ resellerInfo.name }}!</h1>
                    <p class="mt-1 text-sm text-gray-600">Hier ist eine Übersicht über Ihr Reseller-Dashboard.</p>
                </div>

                <!-- Stats Grid -->
                <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
                    <!-- Total Users -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Gesamt Benutzer</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.total_users }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Active Users -->
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
                                        <dt class="text-sm font-medium text-gray-500 truncate">Aktive Benutzer</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.active_users }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Total Projects -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

                    <!-- Storage Used -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-6 w-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7c0-2.21-1.79-4-4-4H8c-2.21 0-4 1.79-4 4z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Speicher verwendet</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.storage_used }} GB</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Storage Overview -->
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
                                ⚠️ Ihr Speicher ist fast voll. Bitte kontaktieren Sie Ihren Administrator.
                            </div>
                            <div v-else-if="storagePercentage >= 75" class="mt-2 text-sm text-yellow-600">
                                ⚠️ Ihr Speicher ist zu 75% gefüllt.
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent Activity -->
                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Letzte Aktivitäten</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">Aktuelle Benutzer- und Projektaktivitäten</p>
                    </div>
                    <ul class="divide-y divide-gray-200">
                        <li v-for="activity in recentActivities" :key="activity.id" class="px-4 py-4 sm:px-6">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 h-10 w-10">
                                        <div class="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
                                            <svg class="h-6 w-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                            </svg>
                                        </div>
                                    </div>
                                    <div class="ml-4">
                                        <div class="text-sm font-medium text-gray-900">{{ activity.user_name }}</div>
                                        <div class="text-sm text-gray-500">{{ activity.action }}</div>
                                    </div>
                                </div>
                                <div class="flex items-center">
                                    <div class="text-sm text-gray-500">{{ formatDate(activity.timestamp) }}</div>
                                </div>
                            </div>
                        </li>
                        <li v-if="recentActivities.length === 0" class="px-4 py-8 text-center">
                            <div class="text-gray-500">
                                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <p class="mt-2 text-sm">Noch keine Aktivitäten vorhanden</p>
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
import axios from 'axios'

export default {
    name: 'ResellerDashboard',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const resellerInfo = ref({
            name: 'Reseller Dashboard',
            company: 'Beispiel GmbH'
        })
        
        const stats = ref({
            total_users: 0,
            active_users: 0,
            total_projects: 0,
            storage_used: 0
        })
        
        const storageInfo = ref({
            used_gb: 0,
            limit_gb: 50,
            available_gb: 50
        })
        
        const recentActivities = ref([])
        
        const storagePercentage = computed(() => {
            return Math.round((storageInfo.value.used_gb / storageInfo.value.limit_gb) * 100)
        })
        
        // API Configuration
        const API_BASE = 'http://localhost:8000/api'
        
        const getAuthHeaders = () => {
            const token = authStore.token
            return token ? { Authorization: `Bearer ${token}` } : {}
        }
        
        const getStorageBarColor = () => {
            const percentage = storagePercentage.value
            if (percentage >= 90) return 'bg-red-500'
            if (percentage >= 75) return 'bg-yellow-500'
            return 'bg-green-500'
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
        
        const loadDashboardData = async () => {
            try {
                const resellerId = router.currentRoute.value.params.resellerId
                
                // Load reseller info
                try {
                    const resellerResponse = await axios.get(`${API_BASE}/reseller/${resellerId}/info`, {
                        headers: getAuthHeaders()
                    })
                    
                    if (resellerResponse.data) {
                        resellerInfo.value = resellerResponse.data
                    }
                } catch (error) {
                    console.error('Fehler beim Laden der Reseller-Info:', error)
                }
                
                // Load stats
                try {
                    const statsResponse = await axios.get(`${API_BASE}/reseller/${resellerId}/stats`, {
                        headers: getAuthHeaders()
                    })
                    
                    if (statsResponse.data) {
                        stats.value = statsResponse.data
                    }
                } catch (error) {
                    console.error('Fehler beim Laden der Statistiken:', error)
                }
                
                // Load activities
                try {
                    const activitiesResponse = await axios.get(`${API_BASE}/reseller/${resellerId}/activities`, {
                        headers: getAuthHeaders()
                    })
                    
                    if (activitiesResponse.data) {
                        recentActivities.value = activitiesResponse.data
                    }
                } catch (error) {
                    console.error('Fehler beim Laden der Aktivitäten:', error)
                }
                
                console.log('Dashboard-Daten geladen')
            } catch (error) {
                console.error('Fehler beim Laden der Dashboard-Daten:', error)
            }
        }
        
        const logout = async () => {
            try {
                await authStore.logout()
                router.push('/login')
            } catch (error) {
                console.error('Logout-Fehler:', error)
            }
        }
        
        onMounted(() => {
            loadDashboardData()
        })
        
        return {
            resellerInfo,
            stats,
            storageInfo,
            storagePercentage,
            recentActivities,
            getStorageBarColor,
            formatDate,
            logout
        }
    }
}
</script>
