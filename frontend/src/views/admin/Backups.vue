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
                                class="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
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
                        <h1 class="text-xl font-semibold text-gray-900">Backup-Verwaltung</h1>
                        <p class="mt-2 text-sm text-gray-700">Erstellen und verwalten Sie System-Backups.</p>
                    </div>
                    <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
                        <button
                            @click="createBackup"
                            :disabled="creating"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto disabled:opacity-50"
                        >
                            {{ creating ? 'Erstelle Backup...' : 'Neues Backup' }}
                        </button>
                    </div>
                </div>

                <!-- Backup Statistics -->
                <div class="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    <div class="bg-white overflow-hidden shadow rounded-lg">
                        <div class="p-5">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <div class="w-8 h-8 bg-green-100 rounded-md flex items-center justify-center">
                                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Erfolgreiche Backups</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.successful }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

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
                                        <dt class="text-sm font-medium text-gray-500 truncate">Fehlgeschlagene Backups</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.failed }}</dd>
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
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.79 4 8.5 4s8.5-1.79 8.5-4V7M4 7c0 2.21 3.79 4 8.5 4s8.5-1.79 8.5-4M4 7c0-2.21 3.79-4 8.5-4s8.5 1.79 8.5 4"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Gesamtgröße</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.totalSize }}</dd>
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
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                    </div>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Letztes Backup</dt>
                                        <dd class="text-lg font-medium text-gray-900">{{ stats.lastBackup }}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Backups Table -->
                <div class="mt-8 flex flex-col">
                    <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                        <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                            <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                                <table class="min-w-full divide-y divide-gray-300">
                                    <thead class="bg-gray-50">
                                        <tr>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Backup
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Typ
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Status
                                            </th>
                                            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                                                Größe
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
                                        <tr v-for="backup in backups" :key="backup.id">
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <div class="flex items-center">
                                                    <div class="flex-shrink-0 h-10 w-10">
                                                        <div class="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center">
                                                            <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"></path>
                                                            </svg>
                                                        </div>
                                                    </div>
                                                    <div class="ml-4">
                                                        <div class="text-sm font-medium text-gray-900">{{ backup.name }}</div>
                                                        <div class="text-sm text-gray-500">{{ backup.description }}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span :class="[
                                                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                                                    backup.type === 'automatic' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                                                ]">
                                                    {{ backup.type === 'automatic' ? 'Automatisch' : 'Manuell' }}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span :class="[
                                                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                                                    backup.status === 'completed' ? 'bg-green-100 text-green-800' : 
                                                    backup.status === 'failed' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                                                ]">
                                                    {{ getStatusText(backup.status) }}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {{ backup.size }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {{ formatDate(backup.created_at) }}
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button
                                                    v-if="backup.status === 'completed'"
                                                    @click="downloadBackup(backup)"
                                                    class="text-indigo-600 hover:text-indigo-900 mr-4"
                                                >
                                                    Download
                                                </button>
                                                <button
                                                    v-if="backup.status === 'completed'"
                                                    @click="restoreBackup(backup)"
                                                    class="text-green-600 hover:text-green-900 mr-4"
                                                >
                                                    Wiederherstellen
                                                </button>
                                                <button
                                                    @click="deleteBackup(backup)"
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

        <!-- Restore Confirmation Modal -->
        <div v-if="showRestoreModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
                <div class="mt-3">
                    <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100">
                        <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                    </div>
                    <div class="mt-2 text-center">
                        <h3 class="text-lg font-medium text-gray-900">Backup wiederherstellen</h3>
                        <div class="mt-2">
                            <p class="text-sm text-gray-500">
                                Sind Sie sicher, dass Sie das Backup "{{ selectedBackup?.name }}" wiederherstellen möchten? 
                                Diese Aktion überschreibt alle aktuellen Daten und kann nicht rückgängig gemacht werden.
                            </p>
                        </div>
                    </div>
                    <div class="mt-4 flex justify-center space-x-3">
                        <button
                            @click="showRestoreModal = false"
                            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
                        >
                            Abbrechen
                        </button>
                        <button
                            @click="confirmRestore"
                            :disabled="restoring"
                            class="px-4 py-2 text-sm font-medium text-white bg-yellow-600 rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 disabled:opacity-50"
                        >
                            {{ restoring ? 'Wiederherstellen...' : 'Wiederherstellen' }}
                        </button>
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
    name: 'AdminBackups',
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()
        
        const backups = ref([])
        const creating = ref(false)
        const restoring = ref(false)
        const showRestoreModal = ref(false)
        const selectedBackup = ref(null)
        
        const stats = ref({
            successful: 15,
            failed: 2,
            totalSize: '2.4 GB',
            lastBackup: '2 Stunden'
        })
        
        // Mock data - in real app this would come from API
        const loadBackups = async () => {
            try {
                backups.value = [
                    {
                        id: 1,
                        name: 'backup_2024_01_29_daily',
                        description: 'Tägliches automatisches Backup',
                        type: 'automatic',
                        status: 'completed',
                        size: '156 MB',
                        created_at: '2024-01-29T02:00:00Z'
                    },
                    {
                        id: 2,
                        name: 'backup_2024_01_28_manual',
                        description: 'Manuelles Backup vor Update',
                        type: 'manual',
                        status: 'completed',
                        size: '148 MB',
                        created_at: '2024-01-28T14:30:00Z'
                    },
                    {
                        id: 3,
                        name: 'backup_2024_01_28_daily',
                        description: 'Tägliches automatisches Backup',
                        type: 'automatic',
                        status: 'completed',
                        size: '152 MB',
                        created_at: '2024-01-28T02:00:00Z'
                    },
                    {
                        id: 4,
                        name: 'backup_2024_01_27_daily',
                        description: 'Tägliches automatisches Backup',
                        type: 'automatic',
                        status: 'failed',
                        size: '0 MB',
                        created_at: '2024-01-27T02:00:00Z'
                    },
                    {
                        id: 5,
                        name: 'backup_2024_01_26_daily',
                        description: 'Tägliches automatisches Backup',
                        type: 'automatic',
                        status: 'completed',
                        size: '145 MB',
                        created_at: '2024-01-26T02:00:00Z'
                    }
                ]
            } catch (error) {
                console.error('Fehler beim Laden der Backups:', error)
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
        
        const getStatusText = (status) => {
            switch (status) {
                case 'completed': return 'Abgeschlossen'
                case 'failed': return 'Fehlgeschlagen'
                case 'running': return 'Läuft'
                default: return 'Unbekannt'
            }
        }
        
        const createBackup = async () => {
            creating.value = true
            try {
                // Simulate backup creation
                console.log('Erstelle neues Backup...')
                
                await new Promise(resolve => setTimeout(resolve, 3000))
                
                const newBackup = {
                    id: Date.now(),
                    name: `backup_${new Date().toISOString().split('T')[0]}_manual`,
                    description: 'Manuelles Backup',
                    type: 'manual',
                    status: 'completed',
                    size: '159 MB',
                    created_at: new Date().toISOString()
                }
                
                backups.value.unshift(newBackup)
                stats.value.successful++
                
                alert('Backup erfolgreich erstellt!')
            } catch (error) {
                console.error('Fehler beim Erstellen des Backups:', error)
                alert('Fehler beim Erstellen des Backups!')
            } finally {
                creating.value = false
            }
        }
        
        const downloadBackup = async (backup) => {
            try {
                console.log('Lade Backup herunter:', backup.name)
                // In real app, this would trigger a file download
                alert(`Download von "${backup.name}" gestartet!`)
            } catch (error) {
                console.error('Fehler beim Download:', error)
                alert('Fehler beim Download des Backups!')
            }
        }
        
        const restoreBackup = (backup) => {
            selectedBackup.value = backup
            showRestoreModal.value = true
        }
        
        const confirmRestore = async () => {
            restoring.value = true
            try {
                console.log('Stelle Backup wieder her:', selectedBackup.value.name)
                
                // Simulate restore process
                await new Promise(resolve => setTimeout(resolve, 5000))
                
                showRestoreModal.value = false
                alert(`Backup "${selectedBackup.value.name}" erfolgreich wiederhergestellt!`)
            } catch (error) {
                console.error('Fehler beim Wiederherstellen:', error)
                alert('Fehler beim Wiederherstellen des Backups!')
            } finally {
                restoring.value = false
                selectedBackup.value = null
            }
        }
        
        const deleteBackup = async (backup) => {
            if (confirm(`Möchten Sie das Backup "${backup.name}" wirklich löschen?`)) {
                try {
                    const index = backups.value.findIndex(b => b.id === backup.id)
                    if (index !== -1) {
                        backups.value.splice(index, 1)
                        if (backup.status === 'completed') {
                            stats.value.successful--
                        } else if (backup.status === 'failed') {
                            stats.value.failed--
                        }
                        console.log('Backup gelöscht:', backup)
                        alert('Backup erfolgreich gelöscht!')
                    }
                } catch (error) {
                    console.error('Fehler beim Löschen:', error)
                    alert('Fehler beim Löschen des Backups!')
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
            loadBackups()
        })
        
        return {
            backups,
            stats,
            creating,
            restoring,
            showRestoreModal,
            selectedBackup,
            createBackup,
            downloadBackup,
            restoreBackup,
            confirmRestore,
            deleteBackup,
            formatDate,
            getStatusText,
            logout
        }
    }
}
</script>
