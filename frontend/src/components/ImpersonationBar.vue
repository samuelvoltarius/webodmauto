<template>
  <!-- 🎭 Impersonation-Banner (nur sichtbar wenn aktive Impersonation) -->
  <div v-if="isImpersonating" class="bg-orange-500 text-white px-4 py-2 shadow-md">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
      <!-- Impersonation-Info -->
      <div class="flex items-center space-x-3">
        <div class="flex items-center">
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
          </svg>
          <span class="font-medium">Admin-Impersonation aktiv</span>
        </div>
        
        <div class="text-sm opacity-90">
          <span>Sie agieren als:</span>
          <span class="font-semibold ml-1">
            {{ impersonatedUser.type === 'reseller' ? 'Reseller' : 'Benutzer' }}
            "{{ impersonatedUser.name }}"
          </span>
          <span class="ml-2 text-xs">
            (Original Admin: {{ originalAdmin.username }})
          </span>
        </div>
      </div>

      <!-- Back-Button -->
      <div class="flex items-center space-x-3">
        <div class="text-sm opacity-90">
          Seit: {{ formatTime(impersonationStarted) }}
        </div>
        
        <button
          @click="endImpersonation"
          :disabled="isEnding"
          class="bg-white text-orange-600 px-4 py-1 rounded-md text-sm font-medium hover:bg-orange-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        >
          <svg v-if="isEnding" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          {{ isEnding ? 'Beende...' : 'Zurück zu Admin' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

export default {
  name: 'ImpersonationBar',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const showMessage = inject('showMessage')
    
    // State
    const isEnding = ref(false)
    const impersonationStatus = ref(null)
    
    // Computed
    const isImpersonating = computed(() => {
      return authStore.user?.is_impersonating || false
    })
    
    const originalAdmin = computed(() => {
      if (!isImpersonating.value) return null
      return {
        id: authStore.user?.original_admin_id,
        username: authStore.user?.original_admin_username || 'Admin'
      }
    })
    
    const impersonatedUser = computed(() => {
      if (!isImpersonating.value) return null
      
      const user = authStore.user
      return {
        type: user?.impersonated_user_type || user?.role,
        name: user?.company_name || user?.full_name || user?.username,
        id: user?.impersonated_user_id || user?.sub
      }
    })
    
    const impersonationStarted = computed(() => {
      return authStore.user?.impersonation_started_at
    })
    
    // Methods
    const formatTime = (isoString) => {
      if (!isoString) return ''
      
      try {
        const date = new Date(isoString)
        const now = new Date()
        const diffMs = now - date
        const diffMins = Math.floor(diffMs / 60000)
        
        if (diffMins < 1) return 'gerade eben'
        if (diffMins < 60) return `${diffMins} Min`
        
        const diffHours = Math.floor(diffMins / 60)
        const remainingMins = diffMins % 60
        
        if (diffHours < 24) {
          return remainingMins > 0 ? `${diffHours}h ${remainingMins}m` : `${diffHours}h`
        }
        
        return date.toLocaleString('de-DE', {
          day: '2-digit',
          month: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        return ''
      }
    }
    
    const endImpersonation = async () => {
      if (isEnding.value) return
      
      try {
        isEnding.value = true
        
        // API-Call zum Beenden der Impersonation
        const response = await axios.post('/api/admin/end-impersonation')
        
        if (response.data.admin_token) {
          // Neuen Admin-Token setzen
          localStorage.setItem('auth_token', response.data.admin_token)
          
          // Auth Store aktualisieren
          await authStore.initialize()
          
          // Zur Admin-Dashboard weiterleiten
          await router.push('/admin/dashboard')
          
          showMessage('Impersonation erfolgreich beendet', 'success')
        }
        
      } catch (error) {
        console.error('Fehler beim Beenden der Impersonation:', error)
        
        let errorMessage = 'Fehler beim Beenden der Impersonation'
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail
        }
        
        showMessage(errorMessage, 'error')
      } finally {
        isEnding.value = false
      }
    }
    
    const checkImpersonationStatus = async () => {
      if (!isImpersonating.value) return
      
      try {
        const response = await axios.get('/api/admin/impersonation-status')
        impersonationStatus.value = response.data
      } catch (error) {
        console.warn('Impersonation-Status konnte nicht abgerufen werden:', error)
      }
    }
    
    // Lifecycle
    onMounted(() => {
      checkImpersonationStatus()
      
      // Status alle 30 Sekunden prüfen
      const interval = setInterval(checkImpersonationStatus, 30000)
      
      // Cleanup
      return () => {
        clearInterval(interval)
      }
    })
    
    return {
      isImpersonating,
      originalAdmin,
      impersonatedUser,
      impersonationStarted,
      isEnding,
      endImpersonation,
      formatTime
    }
  }
}
</script>

<style scoped>
/* Impersonation-Banner Animation */
.bg-orange-500 {
  background: linear-gradient(90deg, #f97316 0%, #ea580c 100%);
}

/* Pulsing Animation für aktive Impersonation */
@keyframes pulse-orange {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(249, 115, 22, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(249, 115, 22, 0);
  }
}

.bg-orange-500::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  animation: pulse-orange 2s infinite;
  pointer-events: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .max-w-7xl {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .flex.items-center.justify-between {
    align-items: flex-start;
  }
  
  .text-sm {
    font-size: 0.75rem;
  }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  .bg-orange-500 {
    background: #d97706;
    border: 2px solid #ffffff;
  }
  
  .bg-white {
    border: 1px solid #000000;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .animate-spin {
    animation: none;
  }
  
  .bg-orange-500::before {
    animation: none;
  }
  
  .transition-colors {
    transition: none;
  }
}

/* Print Styles */
@media print {
  .bg-orange-500 {
    display: none;
  }
}
</style>