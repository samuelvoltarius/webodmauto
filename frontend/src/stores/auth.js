/**
 * ChiliView Auth Store
 * Pinia Store für Authentifizierung und Benutzerverwaltung
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const impersonation = ref({
    active: false,
    originalAdmin: null
  })

  // Router und Toast
  const router = useRouter()
  const toast = useToast()

  // Computed
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const resellerId = computed(() => user.value?.reseller_id || null)
  const isAdmin = computed(() => userRole.value === 'admin')
  const isReseller = computed(() => userRole.value === 'reseller')
  const isUser = computed(() => userRole.value === 'user')
  const isImpersonating = computed(() => impersonation.value.active)

  // Actions
  const login = async (credentials) => {
    isLoading.value = true
    
    try {
      const response = await axios.post('/api/auth/login', credentials)
      
      const { access_token, user: userData, impersonation: impersonationData } = response.data
      
      // Token und User-Daten speichern
      token.value = access_token
      user.value = userData
      localStorage.setItem('auth_token', access_token)
      
      // Impersonation-Status setzen
      if (impersonationData) {
        impersonation.value = {
          active: true,
          originalAdmin: impersonationData.original_admin_id
        }
      }
      
      // Axios-Header setzen
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      toast.success('Erfolgreich angemeldet')
      
      // Weiterleitung basierend auf Rolle
      await redirectAfterLogin()
      
      return response.data
      
    } catch (error) {
      console.error('Login-Fehler:', error)
      
      const message = error.response?.data?.detail || 'Anmeldung fehlgeschlagen'
      toast.error(message)
      
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      // Logout-Request an Server
      if (token.value) {
        await axios.post('/api/auth/logout')
      }
    } catch (error) {
      console.error('Logout-Fehler:', error)
    } finally {
      // Lokale Daten löschen
      clearAuthData()
      
      toast.success('Erfolgreich abgemeldet')
      
      // Zur Login-Seite weiterleiten
      router.push('/login')
    }
  }

  const validateToken = async () => {
    if (!token.value) {
      throw new Error('Kein Token vorhanden')
    }

    try {
      // Axios-Header setzen
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      
      const response = await axios.get('/api/auth/validate-token')
      
      if (response.data.valid) {
        user.value = response.data.user
        
        // Impersonation-Status prüfen
        if (response.data.user.impersonated_by) {
          impersonation.value = {
            active: true,
            originalAdmin: response.data.user.original_admin
          }
        }
        
        return true
      } else {
        throw new Error('Token ungültig')
      }
      
    } catch (error) {
      console.error('Token-Validierung fehlgeschlagen:', error)
      clearAuthData()
      throw error
    }
  }

  const changePassword = async (passwordData) => {
    isLoading.value = true
    
    try {
      await axios.post('/api/auth/change-password', passwordData)
      toast.success('Passwort erfolgreich geändert')
      
    } catch (error) {
      console.error('Passwort-Änderung fehlgeschlagen:', error)
      
      const message = error.response?.data?.detail?.message || 
                     error.response?.data?.detail || 
                     'Passwort konnte nicht geändert werden'
      toast.error(message)
      
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const impersonateUser = async (targetUserType, targetUserId, resellerId = null) => {
    if (!isAdmin.value) {
      throw new Error('Nur Admins können Impersonation durchführen')
    }

    isLoading.value = true
    
    try {
      const response = await axios.post('/api/auth/impersonate', {
        target_user_type: targetUserType,
        target_user_id: targetUserId,
        reseller_id: resellerId
      })
      
      const { access_token, user: userData } = response.data
      
      // Token und User-Daten aktualisieren
      token.value = access_token
      user.value = userData
      localStorage.setItem('auth_token', access_token)
      
      // Impersonation-Status setzen
      impersonation.value = {
        active: true,
        originalAdmin: response.data.original_admin_id
      }
      
      // Axios-Header aktualisieren
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      toast.success(`Impersonation als ${targetUserType} gestartet`)
      
      // Weiterleitung zur entsprechenden Rolle
      await redirectAfterLogin()
      
      return response.data
      
    } catch (error) {
      console.error('Impersonation fehlgeschlagen:', error)
      
      const message = error.response?.data?.detail || 'Impersonation fehlgeschlagen'
      toast.error(message)
      
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const endImpersonation = async () => {
    if (!impersonation.value.active) {
      throw new Error('Keine aktive Impersonation')
    }

    isLoading.value = true
    
    try {
      const response = await axios.post('/api/auth/end-impersonation')
      
      const { access_token, user: userData } = response.data
      
      // Token und User-Daten aktualisieren
      token.value = access_token
      user.value = userData
      localStorage.setItem('auth_token', access_token)
      
      // Impersonation-Status zurücksetzen
      impersonation.value = {
        active: false,
        originalAdmin: null
      }
      
      // Axios-Header aktualisieren
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      toast.success('Impersonation beendet')
      
      // Zurück zum Admin-Dashboard
      router.push('/admin/dashboard')
      
      return response.data
      
    } catch (error) {
      console.error('Impersonation beenden fehlgeschlagen:', error)
      
      const message = error.response?.data?.detail || 'Impersonation konnte nicht beendet werden'
      toast.error(message)
      
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const refreshUserData = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      user.value = response.data.user
      
    } catch (error) {
      console.error('User-Daten aktualisieren fehlgeschlagen:', error)
      throw error
    }
  }

  // Helper Functions
  const clearAuthData = () => {
    user.value = null
    token.value = null
    impersonation.value = {
      active: false,
      originalAdmin: null
    }
    localStorage.removeItem('auth_token')
    delete axios.defaults.headers.common['Authorization']
  }

  const redirectAfterLogin = async () => {
    const currentRoute = router.currentRoute.value
    
    // Wenn bereits auf einer gültigen Seite, nicht weiterleiten
    if (currentRoute.meta.requiresAuth && 
        (!currentRoute.meta.roles || currentRoute.meta.roles.includes(userRole.value))) {
      return
    }
    
    // Rollenbasierte Weiterleitung
    switch (userRole.value) {
      case 'admin':
        router.push('/admin/dashboard')
        break
        
      case 'reseller':
        router.push(`/reseller/${resellerId.value}/dashboard`)
        break
        
      case 'user':
        router.push(`/reseller/${resellerId.value}/user/dashboard`)
        break
        
      default:
        router.push('/login')
    }
  }

  const hasPermission = (permission) => {
    if (!user.value) return false
    
    // Admin hat alle Rechte
    if (userRole.value === 'admin') return true
    
    // Rollenbasierte Berechtigungen
    const permissions = {
      reseller: [
        'manage_users',
        'view_projects',
        'manage_branding',
        'create_backup'
      ],
      user: [
        'view_own_projects',
        'upload_files',
        'view_profile'
      ]
    }
    
    const rolePermissions = permissions[userRole.value] || []
    return rolePermissions.includes(permission)
  }

  const canAccessReseller = (targetResellerId) => {
    if (!user.value) return false
    
    // Admin kann auf alle Reseller zugreifen
    if (userRole.value === 'admin') return true
    
    // Reseller und User können nur auf ihren eigenen Reseller zugreifen
    return resellerId.value === targetResellerId
  }

  // Initialization
  const initialize = async () => {
    if (token.value) {
      try {
        await validateToken()
      } catch (error) {
        console.error('Initialisierung fehlgeschlagen:', error)
        clearAuthData()
      }
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    impersonation,
    
    // Computed
    isAuthenticated,
    userRole,
    resellerId,
    isAdmin,
    isReseller,
    isUser,
    isImpersonating,
    
    // Actions
    login,
    logout,
    validateToken,
    changePassword,
    impersonateUser,
    endImpersonation,
    refreshUserData,
    initialize,
    
    // Helper
    hasPermission,
    canAccessReseller,
    clearAuthData
  }
})