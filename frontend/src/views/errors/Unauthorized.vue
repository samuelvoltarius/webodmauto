<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <!-- Lock Icon -->
        <div class="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-red-100 mb-6">
          <svg class="h-12 w-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z">
            </path>
          </svg>
        </div>

        <!-- Error Code -->
        <h1 class="text-6xl font-bold text-gray-900 mb-4">401</h1>
        
        <!-- Error Title -->
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">
          Zugriff verweigert
        </h2>
        
        <!-- Error Description -->
        <p class="text-gray-600 mb-8 max-w-md mx-auto">
          Sie haben keine Berechtigung, auf diese Seite zuzugreifen. 
          Bitte melden Sie sich an oder wenden Sie sich an Ihren Administrator.
        </p>

        <!-- Access Details -->
        <div v-if="accessDetails" class="mb-8">
          <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4 text-left">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-yellow-800">Zugriffsinformationen</h3>
                <div class="mt-2 text-sm text-yellow-700">
                  <p><strong>Erforderliche Rolle:</strong> {{ accessDetails.requiredRole }}</p>
                  <p><strong>Ihre aktuelle Rolle:</strong> {{ accessDetails.currentRole || 'Nicht angemeldet' }}</p>
                  <p v-if="accessDetails.resource"><strong>Angeforderte Ressource:</strong> {{ accessDetails.resource }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Login Section (if not logged in) -->
        <div v-if="!isLoggedIn" class="mb-8">
          <div class="bg-blue-50 border border-blue-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-blue-800">Anmeldung erforderlich</h3>
                <p class="mt-1 text-sm text-blue-700">
                  Sie müssen sich anmelden, um auf diese Seite zugreifen zu können.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Role Upgrade Section (if logged in but insufficient role) -->
        <div v-else-if="needsRoleUpgrade" class="mb-8">
          <div class="bg-purple-50 border border-purple-200 rounded-md p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-purple-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-purple-800">Höhere Berechtigung erforderlich</h3>
                <p class="mt-1 text-sm text-purple-700">
                  Ihre aktuelle Rolle reicht nicht aus, um auf diese Ressource zuzugreifen. 
                  Kontaktieren Sie Ihren Administrator für eine Berechtigung.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-4">
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <!-- Login Button (if not logged in) -->
            <router-link
              v-if="!isLoggedIn"
              :to="{ path: '/login', query: { redirect: $route.fullPath } }"
              class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 0a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
              </svg>
              Anmelden
            </router-link>

            <!-- Dashboard Button (if logged in) -->
            <router-link
              v-else
              :to="getDashboardRoute()"
              class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              Zu meinem Dashboard
            </router-link>
            
            <button
              @click="goBack"
              class="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              Zurück
            </button>
          </div>

          <router-link
            to="/"
            class="inline-flex items-center text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
            Zur Startseite
          </router-link>
        </div>

        <!-- Contact Admin Section -->
        <div v-if="isLoggedIn && needsRoleUpgrade" class="mt-12 pt-8 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Berechtigung anfordern</h3>
          <div class="space-y-4">
            <p class="text-sm text-gray-600">
              Wenn Sie glauben, dass Sie Zugriff auf diese Seite haben sollten, 
              kontaktieren Sie bitte Ihren Administrator:
            </p>
            
            <div class="bg-gray-50 rounded-md p-4">
              <div class="text-sm">
                <p><strong>Angeforderte Seite:</strong> {{ $route.fullPath }}</p>
                <p><strong>Erforderliche Rolle:</strong> {{ accessDetails?.requiredRole }}</p>
                <p><strong>Ihre Benutzer-ID:</strong> {{ currentUser?.id }}</p>
                <p><strong>Zeitstempel:</strong> {{ new Date().toLocaleString('de-DE') }}</p>
              </div>
            </div>

            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                :href="`mailto:admin@chiliview.com?subject=Zugriffsberechtigung anfordern&body=Hallo,%0A%0AIch benötige Zugriff auf: ${$route.fullPath}%0AErforderliche Rolle: ${accessDetails?.requiredRole}%0AMeine Benutzer-ID: ${currentUser?.id}%0A%0AVielen Dank!`"
                class="inline-flex items-center text-blue-600 hover:text-blue-800"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                Administrator kontaktieren
              </a>
              
              <button
                @click="requestAccess"
                class="inline-flex items-center text-green-600 hover:text-green-800"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                Zugriff anfordern
              </button>
            </div>
          </div>
        </div>

        <!-- Help Section -->
        <div class="mt-12 pt-8 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Benötigen Sie Hilfe?</h3>
          <div class="space-y-2 text-sm text-gray-600">
            <p>Bei Fragen zu Berechtigungen und Zugriff:</p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center mt-4">
              <a
                href="mailto:support@chiliview.com"
                class="inline-flex items-center text-blue-600 hover:text-blue-800"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                E-Mail Support
              </a>
              
              <router-link
                to="/help/permissions"
                class="inline-flex items-center text-blue-600 hover:text-blue-800"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Berechtigungen verstehen
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="mt-12 text-center text-xs text-gray-500">
      <p>&copy; 2024 ChiliView Platform. Alle Rechte vorbehalten.</p>
      <div class="mt-2 space-x-4">
        <router-link to="/privacy" class="hover:text-gray-700">Datenschutz</router-link>
        <router-link to="/terms" class="hover:text-gray-700">AGB</router-link>
        <router-link to="/imprint" class="hover:text-gray-700">Impressum</router-link>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="message" class="fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg bg-green-500 text-white">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'Unauthorized',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()
    
    const message = ref('')
    const accessDetails = ref(null)

    const currentUser = computed(() => {
      return store.getters['auth/user']
    })

    const isLoggedIn = computed(() => {
      return !!currentUser.value
    })

    const needsRoleUpgrade = computed(() => {
      return isLoggedIn.value && accessDetails.value?.requiredRole && 
             accessDetails.value.currentRole !== accessDetails.value.requiredRole
    })

    const goBack = () => {
      if (window.history.length > 1) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }

    const getDashboardRoute = () => {
      const user = currentUser.value
      if (!user) return '/'
      
      switch (user.role) {
        case 'admin': return '/admin/dashboard'
        case 'reseller': return '/reseller/dashboard'
        case 'user': return '/user/projects'
        default: return '/'
      }
    }

    const requestAccess = async () => {
      try {
        const requestData = {
          requested_url: route.fullPath,
          required_role: accessDetails.value?.requiredRole,
          current_role: currentUser.value?.role,
          user_id: currentUser.value?.id,
          timestamp: new Date().toISOString()
        }

        await api.post('/auth/request-access', requestData)
        
        message.value = 'Zugriffsberechtigung wurde angefordert. Sie erhalten eine E-Mail, sobald diese bearbeitet wurde.'
        
        setTimeout(() => {
          message.value = ''
        }, 5000)

      } catch (err) {
        console.error('Fehler beim Anfordern der Berechtigung:', err)
        message.value = 'Fehler beim Senden der Anfrage. Bitte kontaktieren Sie den Administrator direkt.'
        
        setTimeout(() => {
          message.value = ''
        }, 5000)
      }
    }

    const determineAccessDetails = () => {
      const path = route.fullPath
      const user = currentUser.value
      
      // Bestimme erforderliche Rolle basierend auf dem Pfad
      let requiredRole = 'user'
      let resource = path
      
      if (path.startsWith('/admin')) {
        requiredRole = 'admin'
        resource = 'Admin-Bereich'
      } else if (path.startsWith('/reseller')) {
        requiredRole = 'reseller'
        resource = 'Reseller-Bereich'
      } else if (path.startsWith('/user')) {
        requiredRole = 'user'
        resource = 'Benutzer-Bereich'
      }

      accessDetails.value = {
        requiredRole,
        currentRole: user?.role || null,
        resource
      }
    }

    const logUnauthorizedAccess = () => {
      // Unauthorized-Zugriff für Security-Monitoring loggen
      const unauthorizedData = {
        url: route.fullPath,
        user_id: currentUser.value?.id || null,
        user_role: currentUser.value?.role || null,
        required_role: accessDetails.value?.requiredRole,
        timestamp: new Date().toISOString(),
        ip_address: null, // Wird vom Backend gesetzt
        user_agent: navigator.userAgent
      }

      // An Backend senden (falls verfügbar)
      try {
        fetch('/api/security/unauthorized', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(unauthorizedData)
        }).catch(() => {
          // Fehler beim Senden ignorieren
        })
      } catch (err) {
        // Fehler beim Senden ignorieren
      }

      console.warn('401 - Unauthorized Access:', unauthorizedData)
    }

    onMounted(() => {
      determineAccessDetails()
      logUnauthorizedAccess()
    })

    return {
      message,
      accessDetails,
      currentUser,
      isLoggedIn,
      needsRoleUpgrade,
      goBack,
      getDashboardRoute,
      requestAccess
    }
  }
}
</script>

<style scoped>
/* Animationen für bessere UX */
.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Hover-Effekte für Buttons */
button:hover, .router-link-active:hover {
  transform: translateY(-1px);
  transition: transform 0.2s ease;
}

/* Responsive Anpassungen */
@media (max-width: 640px) {
  .sm\:flex-row {
    flex-direction: column;
  }
  
  .sm\:flex-row .gap-4 {
    gap: 1rem;
  }
}

/* Alert Box Styling */
.bg-yellow-50, .bg-blue-50, .bg-purple-50 {
  border-radius: 0.375rem;
}

/* Message Animation */
.fixed {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>