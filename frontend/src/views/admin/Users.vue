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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                        <h1 class="text-xl font-semibold text-gray-900">Benutzer-Verwaltung</h1>
                        <p class="mt-2 text-sm text-gray-700">Verwalten Sie alle Benutzer über alle Reseller hinweg.</p>
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

                <!-- Filters -->
                <div class="mt-6 bg-white p-4 rounded-lg shadow">
                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div>
                            <label for="reseller-filter" class="block text-sm font-medium text-gray-700">Reseller</label>
                            <select
                                id="reseller-filter"
                                v-model="selectedReseller"
                                @change="filterUsers"
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                <option value="">Alle Reseller</option>
                                <option v-for="reseller in resellers" :key="reseller.id" :value="reseller.id">
                                    {{ reseller.name }}
                                </option>
                            </select>
                        </div>
                        <div>
                            <label for="status-filter" class="block text-sm font-medium text-gray-700">Status</label>
                            <select
                                id="status-filter"
                                v-model="selectedStatus"
                                @change="filterUsers"
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                <option value="">Alle Status</option>
                                <option value="active">Aktiv</option>
                                <option value="inactive">Inaktiv</option>
                            </select>
                        </div>
                        <div>
                            <label for="search" class="block text-sm font-medium text-gray-700">Suche</label>
                            <input
                                type="text"
                                id="search"
                                v-model="searchTerm"
                                @input="filterUsers"
                                placeholder="Name oder E-Mail..."
                                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            />
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
                                                Reseller
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Status
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Projekte
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Letzter Login
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
                                        <tr v-for="user in filteredUsers" :key="user.id">
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
                                                <div class="text-sm text-gray-900">{{ user.reseller_name }}</div>
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
                                                {{ user.project_count }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {{ user.last_login ? formatDate(user.last_login) : 'Nie' }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {{ formatDate(user.created_at) }}
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
                                                <button
                                                    @click="deleteUser(user)"
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
                        <div class="mb-4">
                            <label for="reseller" class="block text-sm font-medium text-gray-700">Reseller</label>
                            <select
                                id="reseller"
                                v-model="currentUser.reseller_id"
                                required
                                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                            >
                                <option value="">Reseller auswählen</option>
                                <option v-for="reseller in resellers" :key="reseller.id" :value="reseller.id">
                                    {{ reseller.name }}
                                </option>
                            </select>
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
    name: 'AdminUsers',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const users = ref([])
        const resellers = ref([])
        const showCreateModal = ref(false)
        const showEditModal = ref(false)
        const saving = ref(false)
        
        const selectedReseller = ref('')
        const selectedStatus = ref('')
        const searchTerm = ref('')
        
        const currentUser = ref({
            id: null,
            name: '',
            email: '',
            password: '',
            reseller_id: '',
            is_active: true
        })
        
        // Mock data - in real app this would come from API
        const loadUsers = async () => {
            try {
                users.value = [
                    {
                        id: 1,
                        name: 'John Doe',
                        email: 'john@example.com',
                        reseller_id: 1,
                        reseller_name: 'Max Mustermann',
                        is_active: true,
                        project_count: 3,
                        last_login: '2024-01-20T10:30:00Z',
                        created_at: '2024-01-15T10:30:00Z'
                    },
                    {
                        id: 2,
                        name: 'Jane Smith',
                        email: 'jane@example.com',
                        reseller_id: 1,
                        reseller_name: 'Max Mustermann',
                        is_active: true,
                        project_count: 5,
                        last_login: '2024-01-21T14:15:00Z',
                        created_at: '2024-01-16T14:15:00Z'
                    },
                    {
                        id: 3,
                        name: 'Bob Wilson',
                        email: 'bob@example.com',
                        reseller_id: 2,
                        reseller_name: 'Anna Schmidt',
                        is_active: false,
                        project_count: 1,
                        last_login: null,
                        created_at: '2024-01-17T09:45:00Z'
                    },
                    {
                        id: 4,
                        name: 'Alice Brown',
                        email: 'alice@example.com',
                        reseller_id: 2,
                        reseller_name: 'Anna Schmidt',
                        is_active: true,
                        project_count: 7,
                        last_login: '2024-01-22T16:20:00Z',
                        created_at: '2024-01-18T16:20:00Z'
                    }
                ]
            } catch (error) {
                console.error('Fehler beim Laden der Benutzer:', error)
            }
        }
        
        const loadResellers = async () => {
            try {
                resellers.value = [
                    { id: 1, name: 'Max Mustermann' },
                    { id: 2, name: 'Anna Schmidt' },
                    { id: 3, name: 'Peter Weber' }
                ]
            } catch (error) {
                console.error('Fehler beim Laden der Reseller:', error)
            }
        }
        
        const filteredUsers = computed(() => {
            let filtered = users.value
            
            if (selectedReseller.value) {
                filtered = filtered.filter(user => user.reseller_id === parseInt(selectedReseller.value))
            }
            
            if (selectedStatus.value) {
                const isActive = selectedStatus.value === 'active'
                filtered = filtered.filter(user => user.is_active === isActive)
            }
            
            if (searchTerm.value) {
                const term = searchTerm.value.toLowerCase()
                filtered = filtered.filter(user => 
                    user.name.toLowerCase().includes(term) || 
                    user.email.toLowerCase().includes(term)
                )
            }
            
            return filtered
        })
        
        const filterUsers = () => {
            // Trigger reactivity - computed will handle the actual filtering
        }
        
        const formatDate = (dateString) => {
            return new Date(dateString).toLocaleDateString('de-DE', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            })
        }
        
        const editUser = (user) => {
            currentUser.value = { ...user }
            showEditModal.value = true
        }
        
        const saveUser = async () => {
            saving.value = true
            try {
                if (showCreateModal.value) {
                    // Create new user
                    const reseller = resellers.value.find(r => r.id === parseInt(currentUser.value.reseller_id))
                    const newUser = {
                        ...currentUser.value,
                        id: Date.now(), // Mock ID
                        reseller_name: reseller ? reseller.name : '',
                        project_count: 0,
                        last_login: null,
                        created_at: new Date().toISOString()
                    }
                    users.value.push(newUser)
                    console.log('Neuer Benutzer erstellt:', newUser)
                } else {
                    // Update existing user
                    const index = users.value.findIndex(u => u.id === currentUser.value.id)
                    if (index !== -1) {
                        const reseller = resellers.value.find(r => r.id === parseInt(currentUser.value.reseller_id))
                        users.value[index] = { 
                            ...currentUser.value,
                            reseller_name: reseller ? reseller.name : users.value[index].reseller_name
                        }
                        console.log('Benutzer aktualisiert:', currentUser.value)
                    }
                }
                
                closeModal()
                alert(showCreateModal.value ? 'Benutzer erfolgreich erstellt!' : 'Benutzer erfolgreich aktualisiert!')
            } catch (error) {
                showMessage('Fehler beim Speichern des Benutzers!', 'error')
            } finally {
                saving.value = false
            }
        }
        
        const toggleUserStatus = async (user) => {
            try {
                user.is_active = !user.is_active
                showMessage(`Benutzer ${user.is_active ? 'aktiviert' : 'deaktiviert'}!`, 'success')
            } catch (error) {
                showMessage('Fehler beim Ändern des Status!', 'error')
            }
        }
        
        const deleteUser = async (user) => {
            showConfirmation(
                'Benutzer löschen',
                `Möchten Sie den Benutzer "${user.name}" wirklich löschen?`,
                async () => {
                    try {
                        const index = users.value.findIndex(u => u.id === user.id)
                        if (index !== -1) {
                            users.value.splice(index, 1)
                            showMessage('Benutzer erfolgreich gelöscht!', 'success')
                        }
                    } catch (error) {
                        showMessage('Fehler beim Löschen des Benutzers!', 'error')
                    }
                }
            )
        }
        
        const closeModal = () => {
            showCreateModal.value = false
            showEditModal.value = false
            currentUser.value = {
                id: null,
                name: '',
                email: '',
                password: '',
                reseller_id: '',
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
            loadResellers()
        })
        
        return {
            users,
            resellers,
            filteredUsers,
            showCreateModal,
            showEditModal,
            currentUser,
            saving,
            selectedReseller,
            selectedStatus,
            searchTerm,
            editUser,
            saveUser,
            toggleUserStatus,
            deleteUser,
            closeModal,
            filterUsers,
            formatDate,
            logout
        }
    }
}
</script>
