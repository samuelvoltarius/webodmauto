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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                <!-- Header -->
                <div class="sm:flex sm:items-center">
                    <div class="sm:flex-auto">
                        <h1 class="text-xl font-semibold text-gray-900">Benutzer-Verwaltung</h1>
                        <p class="mt-2 text-sm text-gray-700">Verwalten Sie Ihre Benutzer und deren Speicherlimits.</p>
                    </div>
                    <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
                        <button
                            @click="showCreateModal = true"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
                        >
                            Neuer Benutzer
                        </button>
                    </div>
                </div>

                <!-- Storage Overview -->
                <div class="mt-6 bg-white p-4 rounded-lg shadow">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">Speicher-Übersicht</h3>
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
                        <div class="text-center">
                            <div class="text-2xl font-bold text-indigo-600">{{ storageStats.total_limit }} GB</div>
                            <div class="text-sm text-gray-500">Gesamt-Limit</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-green-600">{{ storageStats.used }} GB</div>
                            <div class="text-sm text-gray-500">Verwendet</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-yellow-600">{{ storageStats.available }} GB</div>
                            <div class="text-sm text-gray-500">Verfügbar</div>
                        </div>
                        <div class="text-center">
                            <div class="text-2xl font-bold text-gray-600">{{ users.length }}</div>
                            <div class="text-sm text-gray-500">Benutzer</div>
                        </div>
                    </div>
                </div>

                <!-- Users Table -->
                <div class="mt-8 flex flex-col">
                    <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                            <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                                <table class="min-w-full divide-y divide-gray-300">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Benutzer
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Status
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Speicherlimit
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Verwendet
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Projekte
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Letzter Login
                                            </th>
                                            <th scope="col" class="relative px-6 py-3">
                                                <span class="sr-only">Aktionen</span>
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-gray-200">
                                        <tr v-for="user in users" :key="user.id">
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <div class="flex items-center">
                                                    <div class="flex-shrink-0 h-10 w-10">
                                                        <div class="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
                                                            <span class="text-sm font-medium text-gray-700">{{ user.name.charAt(0).toUpperCase() }}</span>
                                                        </div>
                                                    </div>
                                                    <div class="ml-4">
                                                        <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                                                        <div class="text-sm text-gray-500">{{ user.email }}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span :class="[
                                                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                                                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                ]">
                                                    {{ user.is_active ? 'Aktiv' : 'Inaktiv' }}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {{ user.storage_limit_gb }} GB
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <div class="flex items-center">
                                                    <div class="text-sm text-gray-900">{{ user.storage_used_gb }} GB</div>
                                                    <div class="ml-2 w-16 bg-gray-200 rounded-full h-2">
                                                        <div 
                                                            class="h-2 rounded-full"
                                                            :class="getStorageBarColor(user.storage_used_gb, user.storage_limit_gb)"
                                                            :style="{ width: `${Math.min((user.storage_used_gb / user.storage_limit_gb) * 100, 100)}%` }"
                                                        ></div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {{ user.project_count }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {{ user.last_login ? formatDate(user.last_login) : 'Nie' }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button
                                                    @click="editUser(user)"
                                                    class="text-indigo-600 hover:text-indigo-900 mr-4"
                                                >
                                                    Bearbeiten
                                                </button>
                                                <button
                                                    @click="toggleUserStatus(user)"
                                                    :class="[
                                                        'mr-4',
                                                        user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                                                    ]"
                                                >
                                                    {{ user.is_active ? 'Deaktivieren' : 'Aktivieren' }}
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

        <!-- Create/Edit Modal -->
        <div v-if="showCreateModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">
                        {{ showCreateModal ? 'Neuer Benutzer' : 'Benutzer bearbeiten' }}
                    </h3>
                    <form @submit.prevent="saveUser">
                        <div class="mb-4">
                            <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                            <input
                                type="text"
                                id="name"
                                v-model="currentUser.name"
                                required
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div class="mb-4">
                            <label for="email" class="block text-sm font-medium text-gray-700">E-Mail</label>
                            <input
                                type="email"
                                id="email"
                                v-model="currentUser.email"
                                required
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div class="mb-4" v-if="showCreateModal">
                            <label for="password" class="block text-sm font-medium text-gray-700">Passwort</label>
                            <input
                                type="password"
                                id="password"
                                v-model="currentUser.password"
                                required
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                        
                        <!-- Storage Limit -->
                        <div class="mb-4">
                            <label for="storage_limit_gb" class="block text-sm font-medium text-gray-700">Speicherlimit (GB)</label>
                            <input
                                type="number"
                                id="storage_limit_gb"
                                v-model="currentUser.storage_limit_gb"
                                :max="resellerLimits.available_storage"
                                min="1"
                                required
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                            <p class="mt-1 text-xs text-gray-500">Max verfügbar: {{ resellerLimits.available_storage }} GB</p>
                        </div>
                        
                        <div class="mb-4">
                            <div class="flex items-center">
                                <input
                                    id="is_active"
                                    type="checkbox"
                                    v-model="currentUser.is_active"
                                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                />
                                <label for="is_active" class="ml-2 block text-sm text-gray-900">
                                    Aktiv
                                </label>
                            </div>
                        </div>
                        
                        <div class="flex justify-end space-x-3">
                            <button
                                type="button"
                                @click="closeModal"
                                class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
                            >
                                Abbrechen
                            </button>
                            <button
                                type="submit"
                                :disabled="saving"
                                class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                            >
                                {{ saving ? 'Speichern...' : 'Speichern' }}
                            </button>
                        </div>
                    </form>
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
    name: 'ResellerUsers',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const users = ref([])
        const showCreateModal = ref(false)
        const showEditModal = ref(false)
        const saving = ref(false)
        
        const resellerLimits = ref({
            total_storage: 100,
            available_storage: 75
        })
        
        const currentUser = ref({
            id: null,
            name: '',
            email: '',
            password: '',
            storage_limit_gb: 10,
            is_active: true
        })
        
        const storageStats = computed(() => {
            const totalLimit = resellerLimits.value.total_storage
            const used = users.value.reduce((sum, user) => sum + user.storage_used_gb, 0)
            const available = totalLimit - used
            
            return {
                total_limit: totalLimit,
                used: used.toFixed(1),
                available: available.toFixed(1)
            }
        })
        
        // Mock data - in real app this would come from API
        const loadUsers = async () => {
            try {
                users.value = [
                    {
                        id: 1,
                        name: 'John Doe',
                        email: 'john@example.com',
                        is_active: true,
                        storage_limit_gb: 15,
                        storage_used_gb: 8.5,
                        project_count: 3,
                        last_login: '2024-01-20T10:30:00Z'
                    },
                    {
                        id: 2,
                        name: 'Jane Smith',
                        email: 'jane@example.com',
                        is_active: true,
                        storage_limit_gb: 20,
                        storage_used_gb: 12.3,
                        project_count: 5,
                        last_login: '2024-01-21T14:15:00Z'
                    },
                    {
                        id: 3,
                        name: 'Bob Wilson',
                        email: 'bob@example.com',
                        is_active: false,
                        storage_limit_gb: 10,
                        storage_used_gb: 2.1,
                        project_count: 1,
                        last_login: null
                    }
                ]
            } catch (error) {
                console.error('Fehler beim Laden der Benutzer:', error)
            }
        }
        
        const formatDate = (dateString) => {
            return new Date(dateString).toLocaleDateString('de-DE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            })
        }
        
        const getStorageBarColor = (used, limit) => {
            const percentage = (used / limit) * 100
            if (percentage >= 90) return 'bg-red-500'
            if (percentage >= 75) return 'bg-yellow-500'
            return 'bg-green-500'
        }
        
        const editUser = (user) => {
            currentUser.value = { ...user }
            showEditModal.value = true
        }
        
        const saveUser = async () => {
            saving.value = true
            try {
                // Validierung: Speicherlimit darf verfügbaren Speicher nicht überschreiten
                if (currentUser.value.storage_limit_gb > resellerLimits.value.available_storage) {
                    alert(`Das Speicherlimit darf nicht größer als der verfügbare Speicher (${resellerLimits.value.available_storage} GB) sein!`)
                    return
                }
                
                if (showCreateModal.value) {
                    // Create new user
                    const newUser = {
                        ...currentUser.value,
                        id: Date.now(), // Mock ID
                        storage_used_gb: 0,
                        project_count: 0,
                        last_login: null
                    }
                    users.value.push(newUser)
                    console.log('Neuer Benutzer erstellt:', newUser)
                } else {
                    // Update existing user
                    const index = users.value.findIndex(u => u.id === currentUser.value.id)
                    if (index !== -1) {
                        users.value[index] = { ...currentUser.value }
                        console.log('Benutzer aktualisiert:', currentUser.value)
                    }
                }
                
                closeModal()
                alert(showCreateModal.value ? 'Benutzer erfolgreich erstellt!' : 'Benutzer erfolgreich aktualisiert!')
            } catch (error) {
                console.error('Fehler beim Speichern:', error)
                alert('Fehler beim Speichern des Benutzers!')
            } finally {
                saving.value = false
            }
        }
        
        const toggleUserStatus = async (user) => {
            try {
                user.is_active = !user.is_active
                console.log('Benutzer Status geändert:', user)
                alert(`Benutzer ${user.is_active ? 'aktiviert' : 'deaktiviert'}!`)
            } catch (error) {
                console.error('Fehler beim Ändern des Status:', error)
                alert('Fehler beim Ändern des Status!')
            }
        }
        
        const closeModal = () => {
            showCreateModal.value = false
            showEditModal.value = false
            currentUser.value = {
                id: null,
                name: '',
                email: '',
                password: '',
                storage_limit_gb: 10,
                is_active: true
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
            loadUsers()
        })
        
        return {
            users,
            storageStats,
            resellerLimits,
            showCreateModal,
            showEditModal,
            currentUser,
            saving,
            editUser,
            saveUser,
            toggleUserStatus,
            closeModal,
            formatDate,
            getStorageBarColor,
            logout
        }
    }
}
</script>
