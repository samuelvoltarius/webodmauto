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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                <!-- Header -->
                <div class="sm:flex sm:items-center">
                    <div class="sm:flex-auto">
                        <h1 class="text-xl font-semibold text-gray-900">Reseller-Verwaltung</h1>
                        <p class="mt-2 text-sm text-gray-700">Verwalten Sie alle Reseller-Accounts und deren Konfigurationen.</p>
                    </div>
                    <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
                        <button
                            @click="showCreateModal = true"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
                        >
                            Neuer Reseller
                        </button>
                    </div>
                </div>

                <!-- Resellers Table -->
                <div class="mt-8 flex flex-col">
                    <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                            <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                                <table class="min-w-full divide-y divide-gray-300">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Reseller
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Status
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Benutzer
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Projekte
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Erstellt
                                            </th>
                                            <th scope="col" class="relative px-6 py-3">
                                                <span class="sr-only">Aktionen</span>
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody class="bg-white divide-y divide-gray-200">
                                        <tr v-for="reseller in resellers" :key="reseller.id">
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <div class="flex items-center">
                                                    <div class="flex-shrink-0 h-10 w-10">
                                                        <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                                                            <span class="text-sm font-medium text-indigo-700">{{ reseller.name.charAt(0).toUpperCase() }}</span>
                                                        </div>
                                                    </div>
                                                    <div class="ml-4">
                                                        <div class="text-sm font-medium text-gray-900">{{ reseller.name }}</div>
                                                        <div class="text-sm text-gray-500">{{ reseller.email }}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span :class="[
                                                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                                                    reseller.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                                ]">
                                                    {{ reseller.is_active ? 'Aktiv' : 'Inaktiv' }}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {{ reseller.user_count }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {{ reseller.project_count }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {{ formatDate(reseller.created_at) }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button
                                                    @click="editReseller(reseller)"
                                                    class="text-indigo-600 hover:text-indigo-900 mr-4"
                                                >
                                                    Bearbeiten
                                                </button>
                                                <button
                                                    @click="toggleResellerStatus(reseller)"
                                                    :class="[
                                                        'mr-4',
                                                        reseller.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                                                    ]"
                                                >
                                                    {{ reseller.is_active ? 'Deaktivieren' : 'Aktivieren' }}
                                                </button>
                                                <button
                                                    @click="deleteReseller(reseller)"
                                                    class="text-red-600 hover:text-red-900"
                                                >
                                                    Löschen
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
                        {{ showCreateModal ? 'Neuer Reseller' : 'Reseller bearbeiten' }}
                    </h3>
                    <form @submit.prevent="saveReseller">
                        <div class="mb-4">
                            <label for="name" class="block text-sm font-medium text-gray-700">Name</label>
                            <input
                                type="text"
                                id="name"
                                v-model="currentReseller.name"
                                required
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div class="mb-4">
                            <label for="email" class="block text-sm font-medium text-gray-700">E-Mail</label>
                            <input
                                type="email"
                                id="email"
                                v-model="currentReseller.email"
                                required
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div class="mb-4" v-if="showCreateModal">
                            <label for="password" class="block text-sm font-medium text-gray-700">Passwort</label>
                            <input
                                type="password"
                                id="password"
                                v-model="currentReseller.password"
                                required
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                        <div class="mb-4">
                            <label for="company" class="block text-sm font-medium text-gray-700">Unternehmen</label>
                            <input
                                type="text"
                                id="company"
                                v-model="currentReseller.company"
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
                        </div>
                        <!-- Storage Limits -->
                        <div class="mb-4">
                            <h4 class="text-sm font-medium text-gray-900 mb-3">Speicherlimits</h4>
                            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                <div>
                                    <label for="storage_limit_gb" class="block text-sm font-medium text-gray-700">Speicherlimit (GB)</label>
                                    <input
                                        type="number"
                                        id="storage_limit_gb"
                                        v-model="currentReseller.storage_limit_gb"
                                        min="1"
                                        max="1000"
                                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                        placeholder="z.B. 100"
                                    />
                                </div>
                                <div>
                                    <label for="max_users" class="block text-sm font-medium text-gray-700">Max. Benutzer</label>
                                    <input
                                        type="number"
                                        id="max_users"
                                        v-model="currentReseller.max_users"
                                        min="1"
                                        max="1000"
                                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                        placeholder="z.B. 50"
                                    />
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <div class="flex items-center">
                                <input
                                    id="is_active"
                                    type="checkbox"
                                    v-model="currentReseller.is_active"
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
    name: 'AdminResellers',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const resellers = ref([])
        const showCreateModal = ref(false)
        const showEditModal = ref(false)
        const saving = ref(false)
        const loading = ref(false)
        
        const currentReseller = ref({
            id: null,
            name: '',
            email: '',
            password: '',
            company: '',
            is_active: true,
            storage_limit_gb: 50,
            max_users: 10
        })
        
        // API Configuration
        const API_BASE = 'http://localhost:8000/api'
        
        const getAuthHeaders = () => {
            const token = authStore.token
            return token ? { Authorization: `Bearer ${token}` } : {}
        }
        
        // Load resellers from API
        const loadResellers = async () => {
            loading.value = true
            try {
                const response = await axios.get(`${API_BASE}/admin/resellers`, {
                    headers: getAuthHeaders()
                })
                resellers.value = response.data
                console.log('Reseller geladen:', response.data)
            } catch (error) {
                console.error('Fehler beim Laden der Reseller:', error)
                if (error.response?.status === 401) {
                    authStore.logout()
                    router.push('/login')
                } else {
                    alert('Fehler beim Laden der Reseller-Daten!')
                }
            } finally {
                loading.value = false
            }
        }
        
        const formatDate = (dateString) => {
            return new Date(dateString).toLocaleDateString('de-DE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            })
        }
        
        const editReseller = (reseller) => {
            currentReseller.value = { ...reseller }
            showEditModal.value = true
        }
        
        const saveReseller = async () => {
            saving.value = true
            try {
                if (showCreateModal.value) {
                    // Create new reseller
                    const resellerData = {
                        name: currentReseller.value.name,
                        email: currentReseller.value.email,
                        password: currentReseller.value.password,
                        company: currentReseller.value.company,
                        is_active: currentReseller.value.is_active,
                        storage_limit_gb: parseInt(currentReseller.value.storage_limit_gb),
                        max_users: parseInt(currentReseller.value.max_users)
                    }
                    
                    const response = await axios.post(`${API_BASE}/admin/resellers`, resellerData, {
                        headers: getAuthHeaders()
                    })
                    
                    console.log('Neuer Reseller erstellt:', response.data)
                    await loadResellers() // Reload list
                    alert('Reseller erfolgreich erstellt!')
                } else {
                    // Update existing reseller
                    const resellerData = {
                        name: currentReseller.value.name,
                        email: currentReseller.value.email,
                        company: currentReseller.value.company,
                        is_active: currentReseller.value.is_active,
                        storage_limit_gb: parseInt(currentReseller.value.storage_limit_gb),
                        max_users: parseInt(currentReseller.value.max_users)
                    }
                    
                    const response = await axios.put(`${API_BASE}/admin/resellers/${currentReseller.value.id}`, resellerData, {
                        headers: getAuthHeaders()
                    })
                    
                    console.log('Reseller aktualisiert:', response.data)
                    await loadResellers() // Reload list
                    alert('Reseller erfolgreich aktualisiert!')
                }
                
                closeModal()
            } catch (error) {
                console.error('Fehler beim Speichern:', error)
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
        
        const toggleResellerStatus = async (reseller) => {
            try {
                const response = await axios.put(`${API_BASE}/admin/resellers/${reseller.id}`, {
                    ...reseller,
                    is_active: !reseller.is_active
                }, {
                    headers: getAuthHeaders()
                })
                
                console.log('Reseller Status geändert:', response.data)
                await loadResellers() // Reload list
                alert(`Reseller ${!reseller.is_active ? 'aktiviert' : 'deaktiviert'}!`)
            } catch (error) {
                console.error('Fehler beim Ändern des Status:', error)
                if (error.response?.status === 401) {
                    authStore.logout()
                    router.push('/login')
                } else {
                    alert(`Fehler beim Ändern des Status: ${error.response?.data?.detail || error.message}`)
                }
            }
        }
        
        const deleteReseller = async (reseller) => {
            if (confirm(`Möchten Sie den Reseller "${reseller.name}" wirklich löschen?`)) {
                try {
                    await axios.delete(`${API_BASE}/admin/resellers/${reseller.id}`, {
                        headers: getAuthHeaders()
                    })
                    
                    console.log('Reseller gelöscht:', reseller)
                    await loadResellers() // Reload list
                    alert('Reseller erfolgreich gelöscht!')
                } catch (error) {
                    console.error('Fehler beim Löschen:', error)
                    if (error.response?.status === 401) {
                        authStore.logout()
                        router.push('/login')
                    } else {
                        alert(`Fehler beim Löschen: ${error.response?.data?.detail || error.message}`)
                    }
                }
            }
        }
        
        const closeModal = () => {
            showCreateModal.value = false
            showEditModal.value = false
            currentReseller.value = {
                id: null,
                name: '',
                email: '',
                password: '',
                company: '',
                is_active: true,
                storage_limit_gb: 50,
                max_users: 10
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
            loadResellers()
        })
        
        return {
            resellers,
            showCreateModal,
            showEditModal,
            currentReseller,
            saving,
            loading,
            editReseller,
            saveReseller,
            toggleResellerStatus,
            deleteReseller,
            closeModal,
            formatDate,
            logout
        }
    }
}
</script>
