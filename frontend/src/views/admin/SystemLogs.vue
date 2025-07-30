<template>
    <div class="min-h-screen bg-gray-50">
        <!-- Navigation Header -->
        <nav class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex">
                        <div class="flex-shrink-0 flex items-center">
                            <h1 class="text-xl font-semibold text-gray-900">ChiliView Admin</h1>
                        </div>
                        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                            <router-link
                                to="/admin/dashboard"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Dashboard
                            </router-link>
                            <router-link
                                to="/admin/resellers"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Reseller
                            </router-link>
                            <router-link
                                to="/admin/users"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Benutzer
                            </router-link>
                            <router-link
                                to="/admin/settings"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Einstellungen
                            </router-link>
                            <router-link
                                to="/admin/backups"
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                Backups
                            </router-link>
                            <router-link
                                to="/admin/logs"
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                            >
                                System Logs
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
                <div class="sm:flex sm:items-center">
                    <div class="sm:flex-auto">
                        <h1 class="text-xl font-semibold text-gray-900">System Logs</h1>
                        <p class="mt-2 text-sm text-gray-700">Überwachen Sie Systemereignisse und Fehler.</p>
                    </div>
                    <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none space-x-3">
                        <button
                            @click="refreshLogs"
                            :disabled="loading"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
                        >
                            {{ loading ? 'Laden...' : 'Aktualisieren' }}
                        </button>
                        <button
                            @click="clearLogs"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                        >
                            Logs löschen
                        </button>
                    </div>
                </div>

                <!-- Log Statistics -->
                <div class="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-red-100 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Fehler</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.errors }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-yellow-100 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Warnungen</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.warnings }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Info</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.info }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-gray-100 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Gesamt</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.total }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Filters -->
                <div class="mt-6 bg-white p-4 rounded-lg shadow">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
                        <div>
                            <label for="level-filter" class="block text-sm font-medium text-gray-700">Log Level</label>
                            <select
                                id="level-filter"
                                v-model="selectedLevel"
                                @change="filterLogs"
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                <option value="">Alle Level</option>
                                <option value="ERROR">Error</option>
                                <option value="WARNING">Warning</option>
                                <option value="INFO">Info</option>
                                <option value="DEBUG">Debug</option>
                            </select>
                        </div>
                        <div>
                            <label for="component-filter" class="block text-sm font-medium text-gray-700">Komponente</label>
                            <select
                                id="component-filter"
                                v-model="selectedComponent"
                                @change="filterLogs"
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                <option value="">Alle Komponenten</option>
                                <option value="auth">Authentication</option>
                                <option value="webodm">WebODM</option>
                                <option value="database">Database</option>
                                <option value="api">API</option>
                                <option value="system">System</option>
                            </select>
                        </div>
                        <div>
                            <label for="date-filter" class="block text-sm font-medium text-gray-700">Zeitraum</label>
                            <select
                                id="date-filter"
                                v-model="selectedTimeRange"
                                @change="filterLogs"
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                <option value="1h">Letzte Stunde</option>
                                <option value="24h">Letzte 24 Stunden</option>
                                <option value="7d">Letzte 7 Tage</option>
                                <option value="30d">Letzte 30 Tage</option>
                            </select>
                        </div>
                        <div>
                            <label for="search" class="block text-sm font-medium text-gray-700">Suche</label>
                            <input
                                type="text"
                                id="search"
                                v-model="searchTerm"
                                @input="filterLogs"
                                placeholder="Nachricht durchsuchen..."
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                    </div>
                </div>

                <!-- Logs Table -->
                <div class="mt-8 flex flex-col">
                    <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                            <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                                <table class="min-w-full divide-y divide-gray-300">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Zeit
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Level
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Komponente
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Nachricht
                                            </th>
                                            <th scope="col" class="relative px-6 py-3">
                                                <span class="sr-only">Details</span>
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-gray-200">
                                        <tr v-for="log in filteredLogs" :key="log.id" :class="getRowClass(log.level)">
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {{ formatDateTime(log.timestamp) }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span :class="getLevelClass(log.level)">
                                                    {{ log.level }}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {{ log.component }}
                                            </td>
                                            <td class="px-6 py-4 text-sm text-gray-900">
                                                <div class="max-w-xs truncate">{{ log.message }}</div>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button
                                                    @click="showLogDetails(log)"
                                                    class="text-indigo-600 hover:text-indigo-900"
                                                >
                                                    Details
                                                </button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Log Details Modal -->
        <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-3/4 max-w-4xl shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-lg font-medium text-gray-900">Log Details</h3>
                        <button
                            @click="showDetailsModal = false"
                            class="text-gray-400 hover:text-gray-600"
                        >
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div v-if="selectedLog" class="space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Zeitstempel</label>
                                <p class="mt-1 text-sm text-gray-900">{{ formatDateTime(selectedLog.timestamp) }}</p>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Level</label>
                                <span :class="getLevelClass(selectedLog.level)" class="mt-1 inline-block">
                                    {{ selectedLog.level }}
                                </span>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Komponente</label>
                                <p class="mt-1 text-sm text-gray-900">{{ selectedLog.component }}</p>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-gray-700">Benutzer</label>
                                <p class="mt-1 text-sm text-gray-900">{{ selectedLog.user || 'System' }}</p>
                            </div>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700">Nachricht</label>
                            <p class="mt-1 text-sm text-gray-900 bg-gray-50 p-3 rounded-md">{{ selectedLog.message }}</p>
                        </div>
                        <div v-if="selectedLog.details">
                            <label class="block text-sm font-medium text-gray-700">Details</label>
                            <pre class="mt-1 text-xs text-gray-900 bg-gray-50 p-3 rounded-md overflow-auto max-h-64">{{ selectedLog.details }}</pre>
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
    name: 'AdminSystemLogs',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const logs = ref([])
        const loading = ref(false)
        const showDetailsModal = ref(false)
        const selectedLog = ref(null)
        
        const selectedLevel = ref('')
        const selectedComponent = ref('')
        const selectedTimeRange = ref('24h')
        const searchTerm = ref('')
        
        const stats = ref({
            errors: 3,
            warnings: 12,
            info: 156,
            total: 171
        })
        
        // Mock data - in real app this would come from API
        const loadLogs = async () => {
            loading.value = true
            try {
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 1000))
                
                logs.value = [
                    {
                        id: 1,
                        timestamp: '2024-01-29T21:45:32Z',
                        level: 'ERROR',
                        component: 'webodm',
                        message: 'WebODM processing failed for project ID 123',
                        user: 'john@example.com',
                        details: 'Stack trace:\nFile "/app/webodm.py", line 45, in process\n  result = run_webodm_cli()\nWebODMError: Insufficient memory'
                    },
                    {
                        id: 2,
                        timestamp: '2024-01-29T21:44:15Z',
                        level: 'WARNING',
                        component: 'auth',
                        message: 'Multiple failed login attempts detected',
                        user: null,
                        details: 'IP: 192.168.1.100\nAttempts: 5\nTime window: 10 minutes'
                    },
                    {
                        id: 3,
                        timestamp: '2024-01-29T21:43:22Z',
                        level: 'INFO',
                        component: 'api',
                        message: 'New user registered successfully',
                        user: 'admin@example.com',
                        details: 'User: jane@example.com\nReseller: Max Mustermann\nRole: user'
                    },
                    {
                        id: 4,
                        timestamp: '2024-01-29T21:42:10Z',
                        level: 'INFO',
                        component: 'system',
                        message: 'Backup completed successfully',
                        user: null,
                        details: 'Backup file: backup_2024_01_29_daily.tar.gz\nSize: 156 MB\nDuration: 2m 34s'
                    },
                    {
                        id: 5,
                        timestamp: '2024-01-29T21:41:05Z',
                        level: 'WARNING',
                        component: 'database',
                        message: 'Database connection pool near capacity',
                        user: null,
                        details: 'Current connections: 18/20\nRecommendation: Consider increasing pool size'
                    },
                    {
                        id: 6,
                        timestamp: '2024-01-29T21:40:33Z',
                        level: 'INFO',
                        component: 'webodm',
                        message: 'WebODM processing started for project ID 124',
                        user: 'alice@example.com',
                        details: 'Project: Drone Survey Site A\nImages: 45\nEstimated time: 15 minutes'
                    },
                    {
                        id: 7,
                        timestamp: '2024-01-29T21:39:18Z',
                        level: 'ERROR',
                        component: 'api',
                        message: 'File upload failed - invalid format',
                        user: 'bob@example.com',
                        details: 'File: invalid_file.txt\nExpected: .jpg, .png, .tiff\nReceived: .txt'
                    },
                    {
                        id: 8,
                        timestamp: '2024-01-29T21:38:45Z',
                        level: 'INFO',
                        component: 'auth',
                        message: 'User logged in successfully',
                        user: 'alice@example.com',
                        details: 'Session ID: sess_abc123\nIP: 192.168.1.50\nUser Agent: Mozilla/5.0...'
                    }
                ]
            } catch (error) {
                console.error('Fehler beim Laden der Logs:', error)
            } finally {
                loading.value = false
            }
        }
        
        const filteredLogs = computed(() => {
            let filtered = logs.value
            
            if (selectedLevel.value) {
                filtered = filtered.filter(log => log.level === selectedLevel.value)
            }
            
            if (selectedComponent.value) {
                filtered = filtered.filter(log => log.component === selectedComponent.value)
            }
            
            if (searchTerm.value) {
                const term = searchTerm.value.toLowerCase()
                filtered = filtered.filter(log => 
                    log.message.toLowerCase().includes(term) ||
                    log.component.toLowerCase().includes(term)
                )
            }
            
            // Time range filtering would be implemented here
            
            return filtered
        })
        
        const filterLogs = () => {
            // Trigger reactivity - computed will handle the actual filtering
        }
        
        const formatDateTime = (dateString) => {
            return new Date(dateString).toLocaleString('de-DE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            })
        }
        
        const getLevelClass = (level) => {
            const classes = 'inline-flex px-2 py-1 text-xs font-semibold rounded-full'
            switch (level) {
                case 'ERROR':
                    return `${classes} bg-red-100 text-red-800`
                case 'WARNING':
                    return `${classes} bg-yellow-100 text-yellow-800`
                case 'INFO':
                    return `${classes} bg-blue-100 text-blue-800`
                case 'DEBUG':
                    return `${classes} bg-gray-100 text-gray-800`
                default:
                    return `${classes} bg-gray-100 text-gray-800`
            }
        }
        
        const getRowClass = (level) => {
            switch (level) {
                case 'ERROR':
                    return 'bg-red-50'
                case 'WARNING':
                    return 'bg-yellow-50'
                default:
                    return ''
            }
        }
        
        const showLogDetails = (log) => {
            selectedLog.value = log
            showDetailsModal.value = true
        }
        
        const refreshLogs = async () => {
            await loadLogs()
        }
        
        const clearLogs = async () => {
            if (confirm('Möchten Sie wirklich alle Logs löschen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
                try {
                    console.log('Lösche alle Logs...')
                    logs.value = []
                    stats.value = { errors: 0, warnings: 0, info: 0, total: 0 }
                    alert('Logs erfolgreich gelöscht!')
                } catch (error) {
                    console.error('Fehler beim Löschen der Logs:', error)
                    alert('Fehler beim Löschen der Logs!')
                }
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
            loadLogs()
        })
        
        return {
            logs,
            filteredLogs,
            stats,
            loading,
            showDetailsModal,
            selectedLog,
            selectedLevel,
            selectedComponent,
            selectedTimeRange,
            searchTerm,
            refreshLogs,
            clearLogs,
            showLogDetails,
            filterLogs,
            formatDateTime,
            getLevelClass,
            getRowClass,
            logout
        }
    }
}
</script>
