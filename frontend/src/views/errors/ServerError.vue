<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <!-- Error Icon -->
        <div class="mx-auto flex items-center justify-center h-24 w-24 rounded-full bg-red-100 mb-6">
          <svg class="h-12 w-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z">
            </path>
          </svg>
        </div>

        <!-- Error Code -->
        <h1 class="text-6xl font-bold text-gray-900 mb-4">500</h1>
        
        <!-- Error Title -->
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">
          Interner Serverfehler
        </h2>
        
        <!-- Error Description -->
        <p class="text-gray-600 mb-8 max-w-md mx-auto">
          Es ist ein unerwarteter Fehler aufgetreten. Unser Team wurde automatisch benachrichtigt 
          und arbeitet bereits an einer Lösung.
        </p>

        <!-- Error Details (if available) -->
        <div v-if="errorDetails" class="mb-8">
          <div class="bg-red-50 border border-red-200 rounded-md p-4 text-left">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Fehlerdetails</h3>
                <div class="mt-2 text-sm text-red-700">
                  <p><strong>Fehler-ID:</strong> {{ errorDetails.id }}</p>
                  <p v-if="errorDetails.message"><strong>Nachricht:</strong> {{ errorDetails.message }}</p>
                  <p><strong>Zeitstempel:</strong> {{ formatTimestamp(errorDetails.timestamp) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-4">
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              @click="goBack"
              class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              Zurück
            </button>
            
            <button
              @click="reloadPage"
              class="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              Seite neu laden
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

        <!-- Help Section -->
        <div class="mt-12 pt-8 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Benötigen Sie Hilfe?</h3>
          <div class="space-y-2 text-sm text-gray-600">
            <p>Wenn das Problem weiterhin besteht, kontaktieren Sie bitte unseren Support:</p>
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
              
              <a
                href="tel:+43123456789"
                class="inline-flex items-center text-blue-600 hover:text-blue-800"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                </svg>
                Telefon Support
              </a>
            </div>
          </div>
        </div>

        <!-- Status Information -->
        <div class="mt-8 p-4 bg-blue-50 rounded-md">
          <div class="flex items-center">
            <svg class="h-5 w-5 text-blue-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <p class="text-sm text-blue-800">
              Systemstatus: <a href="/status" class="underline hover:no-underline">Aktuelle Verfügbarkeit prüfen</a>
            </p>
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'ServerError',
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    const errorDetails = ref(null)

    const goBack = () => {
      if (window.history.length > 1) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }

    const reloadPage = () => {
      window.location.reload()
    }

    const formatTimestamp = (timestamp) => {
      return new Date(timestamp).toLocaleString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    const generateErrorId = () => {
      return 'ERR-' + Date.now().toString(36).toUpperCase() + '-' + Math.random().toString(36).substr(2, 5).toUpperCase()
    }

    const logError = () => {
      // Fehler-Details für Debugging sammeln
      const error = {
        id: generateErrorId(),
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
        referrer: document.referrer,
        message: route.query.message || null
      }

      errorDetails.value = error

      // Fehler an Backend senden (falls verfügbar)
      try {
        fetch('/api/errors/report', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(error)
        }).catch(() => {
          // Fehler beim Senden ignorieren
          console.warn('Konnte Fehler nicht an Backend senden')
        })
      } catch (err) {
        // Fehler beim Senden ignorieren
        console.warn('Konnte Fehler nicht an Backend senden:', err)
      }

      // Lokales Logging
      console.error('Server Error 500:', error)
    }

    onMounted(() => {
      logError()
      
      // Automatische Weiterleitung nach 30 Sekunden (optional)
      // setTimeout(() => {
      //   router.push('/')
      // }, 30000)
    })

    return {
      errorDetails,
      goBack,
      reloadPage,
      formatTimestamp
    }
  }
}
</script>

<style scoped>
/* Zusätzliche Animationen für bessere UX */
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
button:hover {
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
</style>
