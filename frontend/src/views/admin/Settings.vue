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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">System-Einstellungen</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">WebODM-Konfiguration und Systemparameter</p>
                    </div>
                    
                    <!-- WebODM Settings -->
                    <div class="border-t border-gray-200">
                        <div class="px-4 py-5 sm:p-6">
                            <h4 class="text-lg font-medium text-gray-900 mb-4">WebODM-Konfiguration</h4>
                            
                            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                                <div>
                                    <label for="webodm_path" class="block text-sm font-medium text-gray-700">WebODM-CLI Pfad</label>
                                    <input
                                        type="text"
                                        name="webodm_path"
                                        id="webodm_path"
                                        v-model="settings.webodm_path"
                                        class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                        placeholder="/opt/WebODM/webodm.sh"
                                    />
                                </div>
                                
                                <div>
                                    <label for="max_concurrent_jobs" class="block text-sm font-medium text-gray-700">Max. gleichzeitige Jobs</label>
                                    <input
                                        type="number"
                                        name="max_concurrent_jobs"
                                        id="max_concurrent_jobs"
                                        v-model="settings.max_concurrent_jobs"
                                        class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                        min="1"
                                        max="10"
                                    />
                                </div>
                                
                                <div>
                                    <label for="processing_timeout" class="block text-sm font-medium text-gray-700">Verarbeitungs-Timeout (Minuten)</label>
                                    <input
                                        type="number"
                                        name="processing_timeout"
                                        id="processing_timeout"
                                        v-model="settings.processing_timeout"
                                        class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                        min="30"
                                        max="1440"
                                    />
                                </div>
                                
                                <div>
                                    <label for="storage_path" class="block text-sm font-medium text-gray-700">Speicher-Pfad</label>
                                    <input
                                        type="text"
                                        name="storage_path"
                                        id="storage_path"
                                        v-model="settings.storage_path"
                                        class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                        placeholder="/var/chiliview/storage"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- System Settings -->
                    <div class="border-t border-gray-200">
                        <div class="px-4 py-5 sm:p-6">
                            <h4 class="text-lg font-medium text-gray-900 mb-4">System-Einstellungen</h4>
                            
                            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                                <div>
                                    <label for="backup_retention" class="block text-sm font-medium text-gray-700">Backup-Aufbewahrung (Tage)</label>
                                    <input
                                        type="number"
                                        name="backup_retention"
                                        id="backup_retention"
                                        v-model="settings.backup_retention"
                                        class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                        min="1"
                                        max="365"
                                    />
                                </div>
                                
                                <div>
                                    <label for="log_level" class="block text-sm font-medium text-gray-700">Log-Level</label>
                                    <select
                                        id="log_level"
                                        name="log_level"
                                        v-model="settings.log_level"
                                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                                    >
                                        <option value="DEBUG">Debug</option>
                                        <option value="INFO">Info</option>
                                        <option value="WARNING">Warning</option>
                                        <option value="ERROR">Error</option>
                                    </select>
                                </div>
                                
                                <div class="sm:col-span-2">
                                    <div class="flex items-start">
                                        <div class="flex items-center h-5">
                                            <input
                                                id="auto_backup"
                                                name="auto_backup"
                                                type="checkbox"
                                                v-model="settings.auto_backup"
                                                class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                            />
                                        </div>
                                        <div class="ml-3 text-sm">
                                            <label for="auto_backup" class="font-medium text-gray-700">Automatische Backups</label>
                                            <p class="text-gray-500">Täglich um 2:00 Uhr automatisches Backup erstellen</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="sm:col-span-2">
                                    <div class="flex items-start">
                                        <div class="flex items-center h-5">
                                            <input
                                                id="email_notifications"
                                                name="email_notifications"
                                                type="checkbox"
                                                v-model="settings.email_notifications"
                                                class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                            />
                                        </div>
                                        <div class="ml-3 text-sm">
                                            <label for="email_notifications" class="font-medium text-gray-700">E-Mail Benachrichtigungen</label>
                                            <p class="text-gray-500">Bei kritischen Systemereignissen E-Mail senden</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Hardware Settings -->
                    <div class="border-t border-gray-200">
                        <div class="px-4 py-5 sm:p-6">
                            <h4 class="text-lg font-medium text-gray-900 mb-4">Hardware-Konfiguration</h4>
                            
                            <div class="bg-gray-50 p-4 rounded-lg mb-4">
                                <h5 class="text-sm font-medium text-gray-900 mb-2">Erkannte Hardware</h5>
                                <div class="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span class="text-gray-500">CPU Kerne:</span>
                                        <span class="ml-2 font-medium">{{ hardwareInfo.cpu_cores }}</span>
                                    </div>
                                    <div>
                                        <span class="text-gray-500">RAM:</span>
                                        <span class="ml-2 font-medium">{{ hardwareInfo.ram_gb }} GB</span>
                                    </div>
                                    <div>
                                        <span class="text-gray-500">Freier Speicher:</span>
                                        <span class="ml-2 font-medium">{{ hardwareInfo.free_space_gb }} GB</span>
                                    </div>
                                    <div>
                                        <span class="text-gray-500">GPU:</span>
                                        <span class="ml-2 font-medium">{{ hardwareInfo.gpu_available ? 'Verfügbar' : 'Nicht verfügbar' }}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                                <div>
                                    <label for="cpu_limit" class="block text-sm font-medium text-gray-700">CPU-Limit (%)</label>
                                    <input
                                        type="range"
                                        name="cpu_limit"
                                        id="cpu_limit"
                                        v-model="settings.cpu_limit"
                                        min="10"
                                        max="100"
                                        step="10"
                                        class="mt-1 block w-full"
                                    />
                                    <div class="text-sm text-gray-500 mt-1">{{ settings.cpu_limit }}%</div>
                                </div>
                                
                                <div>
                                    <label for="memory_limit" class="block text-sm font-medium text-gray-700">RAM-Limit (GB)</label>
                                    <input
                                        type="range"
                                        name="memory_limit"
                                        id="memory_limit"
                                        v-model="settings.memory_limit"
                                        min="1"
                                        :max="hardwareInfo.ram_gb"
                                        step="1"
                                        class="mt-1 block w-full"
                                    />
                                    <div class="text-sm text-gray-500 mt-1">{{ settings.memory_limit }} GB</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Save Button -->
                    <div class="border-t border-gray-200 px-4 py-4 sm:px-6">
                        <div class="flex justify-end">
                            <button
                                type="button"
                                @click="saveSettings"
                                :disabled="saving"
                                class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                            >
                                {{ saving ? 'Speichern...' : 'Einstellungen speichern' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
    name: 'AdminSettings',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const saving = ref(false)
        const loading = ref(false)
        
        const settings = ref({
            webodm_path: '/opt/WebODM/webodm.sh',
            max_concurrent_jobs: 3,
            processing_timeout: 120,
            storage_path: '/var/chiliview/storage',
            backup_retention: 30,
            log_level: 'INFO',
            auto_backup: true,
            email_notifications: false,
            cpu_limit: 80,
            memory_limit: 8
        })
        
        const hardwareInfo = ref({
            cpu_cores: 0,
            ram_gb: 0,
            free_space_gb: 0,
            gpu_available: false
        })
        
        // API Configuration
        const API_BASE = 'http://localhost:8000/api'
        
        const getAuthHeaders = () => {
            const token = authStore.token
            return token ? { Authorization: `Bearer ${token}` } : {}
        }
        
        const loadSettings = async () => {
            loading.value = true
            try {
                const response = await axios.get(`${API_BASE}/admin/settings`, {
                    headers: getAuthHeaders()
                })
                settings.value = { ...settings.value, ...response.data }
                console.log('Einstellungen geladen:', response.data)
            } catch (error) {
                console.error('Fehler beim Laden der Einstellungen:', error)
                if (error.response?.status === 401) {
                    authStore.logout()
                    router.push('/login')
                } else {
                    alert('Fehler beim Laden der Einstellungen!')
                }
            } finally {
                loading.value = false
            }
        }
        
        const loadHardwareInfo = async () => {
            try {
                const response = await axios.get(`${API_BASE}/admin/hardware-info`, {
                    headers: getAuthHeaders()
                })
                hardwareInfo.value = response.data
                
                // Update memory limit max based on available RAM
                if (settings.value.memory_limit > hardwareInfo.value.ram_gb) {
                    settings.value.memory_limit = Math.floor(hardwareInfo.value.ram_gb * 0.8)
                }
                
                console.log('Hardware-Informationen geladen:', response.data)
            } catch (error) {
                console.error('Fehler beim Laden der Hardware-Informationen:', error)
                if (error.response?.status === 401) {
                    authStore.logout()
                    router.push('/login')
                } else {
                    // Fallback values if API fails
                    hardwareInfo.value = {
                        cpu_cores: 4,
                        ram_gb: 8,
                        free_space_gb: 100,
                        gpu_available: false
                    }
                }
            }
        }
        
        const saveSettings = async () => {
            saving.value = true
            try {
                const response = await axios.put(`${API_BASE}/admin/settings`, settings.value, {
                    headers: getAuthHeaders()
                })
                
                console.log('Einstellungen gespeichert:', response.data)
                alert('Einstellungen erfolgreich gespeichert!')
            } catch (error) {
                console.error('Fehler beim Speichern der Einstellungen:', error)
                if (error.response?.status === 401) {
                    authStore.logout()
                    router.push('/login')
                } else {
                    alert(`Fehler beim Speichern: ${error.response?.data?.detail || error.message}`)
                }
            } finally {
                saving.value = false
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
            loadSettings()
            loadHardwareInfo()
        })
        
        return {
            settings,
            hardwareInfo,
            saving,
            loading,
            saveSettings,
            logout
        }
    }
}
</script>