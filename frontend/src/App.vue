<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Loading Overlay -->
    <div v-if="isInitializing" class="fixed inset-0 bg-white z-50 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p class="text-gray-600">ChiliView wird geladen...</p>
      </div>
    </div>

    <!-- Main App Content -->
    <router-view v-else />

    <!-- Global Modals -->
    <Teleport to="body">
      <!-- Confirmation Modal -->
      <div v-if="showConfirmModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <h3 class="text-lg font-medium text-gray-900 mb-4">{{ confirmModal.title }}</h3>
          <p class="text-gray-600 mb-6">{{ confirmModal.message }}</p>
          <div class="flex justify-end space-x-3">
            <button
              @click="cancelConfirm"
              class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
            >
              Abbrechen
            </button>
            <button
              @click="confirmAction"
              class="px-4 py-2 text-white bg-red-600 rounded-md hover:bg-red-700"
            >
              Bestätigen
            </button>
          </div>
        </div>
      </div>

      <!-- Error Modal -->
      <div v-if="showErrorModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
        <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div class="flex items-center mb-4">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 class="ml-3 text-lg font-medium text-gray-900">Fehler</h3>
          </div>
          <p class="text-gray-600 mb-6">{{ errorModal.message }}</p>
          <div class="flex justify-end">
            <button
              @click="closeErrorModal"
              class="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              OK
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, provide } from 'vue'
import { useAuthStore } from '@stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

// Stores
const authStore = useAuthStore()
const router = useRouter()

// State
const isInitializing = ref(true)
const showConfirmModal = ref(false)
const showErrorModal = ref(false)
const confirmModal = ref({
  title: '',
  message: '',
  onConfirm: null
})
const errorModal = ref({
  message: ''
})

// Global Modal Functions
const showConfirmation = (title, message, onConfirm) => {
  confirmModal.value = { title, message, onConfirm }
  showConfirmModal.value = true
}

const confirmAction = () => {
  if (confirmModal.value.onConfirm) {
    confirmModal.value.onConfirm()
  }
  showConfirmModal.value = false
}

const cancelConfirm = () => {
  showConfirmModal.value = false
}

const showError = (message) => {
  errorModal.value.message = message
  showErrorModal.value = true
}

const closeErrorModal = () => {
  showErrorModal.value = false
}

// Provide global functions to child components
provide('showConfirmation', showConfirmation)
provide('showError', showError)

// Axios Interceptors
const setupAxiosInterceptors = () => {
  // Request Interceptor
  axios.interceptors.request.use(
    (config) => {
      // Add auth token if available
      const token = localStorage.getItem('auth_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      
      // Add request timestamp for debugging
      config.metadata = { startTime: new Date() }
      
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response Interceptor
  axios.interceptors.response.use(
    (response) => {
      // Log response time in development
      if (import.meta.env.DEV && response.config.metadata) {
        const endTime = new Date()
        const duration = endTime - response.config.metadata.startTime
        console.log(`API Call: ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`)
      }
      
      return response
    },
    (error) => {
      // Handle common errors
      if (error.response) {
        const status = error.response.status
        
        switch (status) {
          case 401:
            // Unauthorized - clear auth and redirect to login
            authStore.clearAuthData()
            if (router.currentRoute.value.name !== 'Login') {
              router.push('/login')
            }
            break
            
          case 403:
            // Forbidden - show error or redirect to unauthorized
            router.push('/unauthorized')
            break
            
          case 404:
            // Not found - could redirect to 404 page
            console.warn('Resource not found:', error.config.url)
            break
            
          case 429:
            // Rate limited
            showError('Zu viele Anfragen. Bitte versuchen Sie es später erneut.')
            break
            
          case 500:
          case 502:
          case 503:
          case 504:
            // Server errors
            showError('Ein Serverfehler ist aufgetreten. Bitte versuchen Sie es später erneut.')
            break
        }
      } else if (error.request) {
        // Network error
        showError('Netzwerkfehler. Bitte überprüfen Sie Ihre Internetverbindung.')
      }
      
      return Promise.reject(error)
    }
  )
}

// App Initialization
const initializeApp = async () => {
  try {
    // Setup axios interceptors
    setupAxiosInterceptors()
    
    // Initialize auth store
    await authStore.initialize()
    
    // Set app as initialized
    isInitializing.value = false
    
    console.log('ChiliView App erfolgreich initialisiert')
    
  } catch (error) {
    console.error('App-Initialisierung fehlgeschlagen:', error)
    
    // Still show the app even if initialization fails
    isInitializing.value = false
    
    // Show error to user
    showError('Die Anwendung konnte nicht vollständig geladen werden. Einige Funktionen sind möglicherweise nicht verfügbar.')
  }
}

// Lifecycle
onMounted(() => {
  initializeApp()
})

// Global error handling
window.addEventListener('error', (event) => {
  console.error('Global Error:', event.error)
  
  if (import.meta.env.PROD) {
    showError('Ein unerwarteter Fehler ist aufgetreten.')
  }
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
  
  if (import.meta.env.PROD) {
    showError('Ein Netzwerkfehler ist aufgetreten.')
  }
  
  event.preventDefault()
})
</script>

<style>
/* Global Styles */
#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Loading Animation */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

/* Focus Styles */
.focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

/* Print Styles */
@media print {
  .no-print {
    display: none !important;
  }
}

/* Dark Mode Support (Future Enhancement) */
@media (prefers-color-scheme: dark) {
  /* Dark mode styles would go here */
}

/* High Contrast Mode Support */
@media (prefers-contrast: high) {
  /* High contrast styles would go here */
}

/* Reduced Motion Support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>