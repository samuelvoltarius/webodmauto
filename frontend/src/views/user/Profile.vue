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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                    <h1 class="text-2xl font-bold text-gray-900">Profil & Speicher</h1>
                    <p class="mt-1 text-sm text-gray-600">Verwalten Sie Ihr Profil und überwachen Sie Ihre Speichernutzung.</p>
                </div>

                <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
                    <!-- User Profile Card -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="px-4 py-5 sm:p-6">
                            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Benutzerinformationen</h3>
                            
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Name</label>
                                    <div class="mt-1 text-sm text-gray-900">{{ userInfo.name }}</div>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">E-Mail</label>
                                    <div class="mt-1 text-sm text-gray-900">{{ userInfo.email }}</div>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Rolle</label>
                                    <div class="mt-1">
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                                            Benutzer
                                        </span>
                                    </div>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Registriert seit</label>
                                    <div class="mt-1 text-sm text-gray-900">{{ formatDate(userInfo.created_at) }}</div>
                                </div>
                                
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Letzter Login</label>
                                    <div class="mt-1 text-sm text-gray-900">{{ formatDate(userInfo.last_login) }}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Storage Overview Card -->
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="px-4 py-5 sm:p-6">
                            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Speicher-Übersicht</h3>
                            
                            <!-- Storage Stats -->
                            <div class="space-y-4">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm font-medium text-gray-700">Speicherlimit</span>
                                    <span class="text-sm text-gray-900">{{ storageInfo.limit_gb }} GB</span>
                                </div>
                                
                                <div class="flex justify-between items-center">
                                    <span class="text-sm font-medium text-gray-700">Verwendet</span>
                                    <span class="text-sm text-gray-900">{{ storageInfo.used_gb }} GB</span>
                                </div>
                                
                                <div class="flex justify-between items-center">
                                    <span class="text-sm font-medium text-gray-700">Verfügbar</span>
                                    <span class="text-sm text-gray-900">{{ storageInfo.available_gb }} GB</span>
                                </div>
                                
                                <!-- Progress Bar -->
                                <div class="mt-4">
                                    <div class="flex justify-between text-sm text-gray-600 mb-2">
                                        <span>{{ storagePercentage }}% verwendet</span>
                                        <span>{{ storageInfo.used_gb }} / {{ storageInfo.limit_gb }} GB</span>
                                    </div>
                                    <div class="w-full bg-gray-200 rounded-full h-4">
                                        <div 
                                            class="h-4 rounded-full transition-all duration-300"
                                            :class="getStorageBarColor()"
                                            :style="{ width: `${Math.min(storagePercentage, 100)}%` }"
                                        ></div>
                                    </div>
                                </div>
                                
                                <!-- Storage Warning -->
                                <div v-if="storagePercentage >= 90" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                                    <div class="flex">
                                        <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                                        </svg>
                                        <div class="ml-3">
                                            <h3 class="text-sm font-medium text-red-800">Speicher fast voll</h3>
                                            <p class="mt-1 text-sm text-red-700">
                                                Ihr Speicher ist zu {{ storagePercentage }}% gefüllt. Bitte löschen Sie alte Projekte oder kontaktieren Sie Ihren Administrator für mehr Speicherplatz.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div v-else-if="storagePercentage >= 75" class="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                                    <div class="flex">
                                        <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                                        </svg>
                                        <div class="ml-3">
                                            <h3 class="text-sm font-medium text-yellow-800">Speicher wird knapp</h3>
                                            <p class="mt-1 text-sm text-yellow-700">
                                                Ihr Speicher ist zu {{ storagePercentage }}% gefüllt. Überlegen Sie, alte Projekte zu löschen.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Storage Breakdown -->
                <div class="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Speicherverbrauch nach Projekten</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">Detaillierte Aufschlüsselung Ihres Speicherverbrauchs</p>
                    </div>
                    <div class="border-t border-gray-200">
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Projekt
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Größe
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Anteil
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Erstellt
                                        </th>
                                        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Status
                                        </th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    <tr v-for="project in projectStorage" :key="project.id">
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm font-medium text-gray-900">{{ project.name }}</div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="text-sm text-gray-900">{{ project.size_gb }} GB</div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <div class="flex items-center">
                                                <div class="text-sm text-gray-900 mr-2">{{ getProjectPercentage(project.size_gb) }}%</div>
                                                <div class="w-16 bg-gray-200 rounded-full h-2">
                                                    <div 
                                                        class="bg-indigo-500 h-2 rounded-full"
                                                        :style="{ width: `${getProjectPercentage(project.size_gb)}%` }"
                                                    ></div>
                                                </div>
                                            </div>
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {{ formatDate(project.created_at) }}
                                        </td>
                                        <td class="px-6 py-4 whitespace-nowrap">
                                            <span :class="[
                                                'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                                                getStatusColor(project.status)
                                            ]">
                                                {{ getStatusText(project.status) }}
                                            </span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Account Actions -->
                <div class="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Konto-Aktionen</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">Verwalten Sie Ihr Konto und Ihre Daten</p>
                    </div>
                    <div class="border-t border-gray-200 px-4 py-5 sm:px-6">
                        <div class="space-y-4">
                            <div class="flex justify-between items-center">
                                <div>
                                    <h4 class="text-sm font-medium text-gray-900">Passwort ändern</h4>
                                    <p class="text-sm text-gray-500">Aktualisieren Sie Ihr Passwort für mehr Sicherheit</p>
                                </div>
                                <button
                                    @click="changePassword"
                                    class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    Ändern
                                </button>
                            </div>
                            
                            <div class="flex justify-between items-center">
                                <div>
                                    <h4 class="text-sm font-medium text-gray-900">Daten exportieren</h4>
                                    <p class="text-sm text-gray-500">Laden Sie eine Kopie Ihrer Daten herunter</p>
                                </div>
                                <button
                                    @click="exportData"
                                    class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                                >
                                    Exportieren
                                </button>
                            </div>
                            
                            <div class="flex justify-between items-center pt-4 border-t border-gray-200">
                                <div>
                                    <h4 class="text-sm font-medium text-red-900">Konto löschen</h4>
                                    <p class="text-sm text-red-600">Alle Ihre Daten werden unwiderruflich gelöscht</p>
                                </div>
                                <button
                                    @click="deleteAccount"
                                    class="inline-flex items-center px-3 py-2 border border-red-300 shadow-sm text-sm leading-4 font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                >
                                    Löschen
                                </button>
                            </div>
                        </div>
                    </div>
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
    name: 'UserProfile',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const userInfo = ref({
            name: 'Max Mustermann',
            email: 'max@example.com',
            created_at: '2023-06-15T10:00:00Z',
            last_login: '2024-01-21T14:30:00Z'
        })
        
        const storageInfo = ref({
            used_gb: 8.5,
            limit_gb: 15,
            available_gb: 6.5
        })
        
        const projectStorage = ref([
            {
                id: 1,
                name: 'Baustellenaufnahme Nord',
                size_gb: 2.3,
                status: 'completed',
                created_at: '2024-01-15T10:00:00Z'
            },
            {
                id: 2,
                name: 'Dachinspektion Gebäude A',
                size_gb: 1.8,
                status: 'processing',
                created_at: '2024-01-18T14:00:00Z'
            },
            {
                id: 3,
                name: 'Landvermessung Süd',
                size_gb: 4.2,
                status: 'completed',
                created_at: '2024-01-10T09:00:00Z'
            },
            {
                id: 4,
                name: 'Fassadeninspektion',
                size_gb: 0.2,
                status: 'failed',
                created_at: '2024-01-20T16:00:00Z'
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
        
        const getProjectPercentage = (sizeGb) => {
            return Math.round((sizeGb / storageInfo.value.limit_gb) * 100)
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
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            })
        }
        
        const changePassword = () => {
            alert('Passwort-Änderung würde hier implementiert werden')
        }
        
        const exportData = () => {
            alert('Datenexport würde hier implementiert werden')
        }
        
        const deleteAccount = () => {
            if (confirm('Sind Sie sicher, dass Sie Ihr Konto löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.')) {
                alert('Konto-Löschung würde hier implementiert werden')
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
        
        const loadProfileData = async () => {
            try {
                // In real app, this would load data from API
                console.log('Profil-Daten geladen')
            } catch (error) {
                console.error('Fehler beim Laden der Profil-Daten:', error)
            }
        }
        
        onMounted(() => {
            loadProfileData()
        })
        
        return {
            userInfo,
            storageInfo,
            storagePercentage,
            projectStorage,
            getStorageBarColor,
            getProjectPercentage,
            getStatusColor,
            getStatusText,
            formatDate,
            changePassword,
            exportData,
            deleteAccount,
            logout
        }
    }
}
</script>
