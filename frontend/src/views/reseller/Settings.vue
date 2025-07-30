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
                                class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                <div class="bg-white shadow overflow-hidden sm:rounded-lg">
                    <div class="px-4 py-5 sm:px-6">
                        <h3 class="text-lg leading-6 font-medium text-gray-900">Reseller-Einstellungen</h3>
                        <p class="mt-1 max-w-2xl text-sm text-gray-500">Verwalten Sie Ihre Benutzer-Limits und Einstellungen</p>
                    </div>
                    
                    <!-- Current Limits Display -->
                    <div class="border-t border-gray-200">
                        <div class="px-4 py-5 sm:p-6">
                            <h4 class="text-lg font-medium text-gray-900 mb-4">Ihre aktuellen Limits</h4>
                            
                            <div class="bg-gray-50 p-4 rounded-lg mb-6">
                                <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-indigo-600">{{ resellerLimits.storage_limit_gb }} GB</div>
                                        <div class="text-sm text-gray-500">Speicherlimit</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-indigo-600">{{ resellerLimits.max_users }}</div>
                                        <div class="text-sm text-gray-500">Max. Benutzer</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-2xl font-bold text-green-600">{{ resellerLimits.current_users }}</div>
                                        <div class="text-sm text-gray-500">Aktuelle Benutzer</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- User Storage Management -->
                    <div class="border-t border-gray-200">
                        <div class="px-4 py-5 sm:p-6">
                            <h4 class="text-lg font-medium text-gray-900 mb-4">Standard-Speicherlimit für neue Benutzer</h4>
                            
                            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                                <div>
                                    <label for="default_user_storage" class="block text-sm font-medium text-gray-700">Standard-Speicherlimit (GB)</label>
                                    <input
                                        type="number"
                                        id="default_user_storage"
                                        v-model="settings.default_user_storage_gb"
                                        :max="resellerLimits.storage_limit_gb"
                                        min="1"
                                        class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                    />
                                    <p class="mt-1 text-xs text-gray-500">Max: {{ resellerLimits.storage_limit_gb }} GB (Ihr Limit)</p>
                                </div>
                                
                                <div>
                                    <label for="max_projects_per_user" class="block text-sm font-medium text-gray-700">Max. Projekte pro Benutzer</label>
                                    <input
                                        type="number"
                                        id="max_projects_per_user"
                                        v-model="settings.max_projects_per_user"
                                        min="1"
                                        max="100"
                                        class="mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Notification Settings -->
                    <div class="border-t border-gray-200">
                        <div class="px-4 py-5 sm:p-6">
                            <h4 class="text-lg font-medium text-gray-900 mb-4">Benachrichtigungen</h4>
                            
                            <div class="space-y-4">
                                <div class="flex items-start">
                                    <div class="flex items-center h-5">
                                        <input
                                            id="notify_storage_limit"
                                            type="checkbox"
                                            v-model="settings.notify_storage_limit"
                                            class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                        />
                                    </div>
                                    <div class="ml-3 text-sm">
                                        <label for="notify_storage_limit" class="font-medium text-gray-700">Speicherlimit-Benachrichtigungen</label>
                                        <p class="text-gray-500">Benachrichtigung erhalten, wenn Benutzer 80% ihres Speicherlimits erreichen</p>
                                    </div>
                                </div>
                                
                                <div class="flex items-start">
                                    <div class="flex items-center h-5">
                                        <input
                                            id="notify_new_users"
                                            type="checkbox"
                                            v-model="settings.notify_new_users"
                                            class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                        />
                                    </div>
                                    <div class="ml-3 text-sm">
                                        <label for="notify_new_users" class="font-medium text-gray-700">Neue Benutzer-Benachrichtigungen</label>
                                        <p class="text-gray-500">Benachrichtigung erhalten, wenn sich neue Benutzer registrieren</p>
                                    </div>
                                </div>
                                
                                <div class="flex items-start">
                                    <div class="flex items-center h-5">
                                        <input
                                            id="notify_project_completion"
                                            type="checkbox"
                                            v-model="settings.notify_project_completion"
                                            class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                                        />
                                    </div>
                                    <div class="ml-3 text-sm">
                                        <label for="notify_project_completion" class="font-medium text-gray-700">Projekt-Abschluss-Benachrichtigungen</label>
                                        <p class="text-gray-500">Benachrichtigung erhalten, wenn Projekte erfolgreich verarbeitet wurden</p>
                                    </div>
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

export default {
    name: 'ResellerSettings',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const saving = ref(false)
        
        const resellerLimits = ref({
            storage_limit_gb: 100,
            max_users: 20,
            current_users: 5
        })
        
        const settings = ref({
            default_user_storage_gb: 10,
            max_projects_per_user: 10,
            notify_storage_limit: true,
            notify_new_users: true,
            notify_project_completion: false
        })
        
        const loadSettings = async () => {
            try {
                // Hier würden normalerweise die Einstellungen vom Backend geladen
                console.log('Lade Reseller-Einstellungen...')
            } catch (error) {
                console.error('Fehler beim Laden der Einstellungen:', error)
            }
        }
        
        const saveSettings = async () => {
            saving.value = true
            try {
                // Validierung: Standard-Speicherlimit darf nicht größer als Reseller-Limit sein
                if (settings.value.default_user_storage_gb > resellerLimits.value.storage_limit_gb) {
                    alert(`Das Standard-Speicherlimit darf nicht größer als Ihr Limit (${resellerLimits.value.storage_limit_gb} GB) sein!`)
                    return
                }
                
                console.log('Speichere Reseller-Einstellungen:', settings.value)
                
                // Simuliere API-Call
                await new Promise(resolve => setTimeout(resolve, 1000))
                
                alert('Einstellungen erfolgreich gespeichert!')
            } catch (error) {
                console.error('Fehler beim Speichern der Einstellungen:', error)
                alert('Fehler beim Speichern der Einstellungen!')
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
        })
        
        return {
            resellerLimits,
            settings,
            saving,
            saveSettings,
            logout
        }
    }
}
</script>
