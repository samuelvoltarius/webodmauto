<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="text-center">
        <!-- 404 Illustration -->
        <div class="mx-auto mb-8">
          <svg class="h-32 w-32 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
                  d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.007-5.824-2.448M15 12a3 3 0 11-6 0 3 3 0 016 0z">
            </path>
          </svg>
        </div>

        <!-- Error Code -->
        <h1 class="text-6xl font-bold text-gray-900 mb-4">404</h1>
        
        <!-- Error Title -->
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">
          Seite nicht gefunden
        </h2>
        
        <!-- Error Description -->
        <p class="text-gray-600 mb-8 max-w-md mx-auto">
          Die angeforderte Seite konnte nicht gefunden werden. Möglicherweise wurde sie verschoben, 
          gelöscht oder Sie haben eine falsche URL eingegeben.
        </p>

        <!-- Search Box -->
        <div class="mb-8">
          <div class="max-w-sm mx-auto">
            <label for="search" class="sr-only">Suchen</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
              <input
                v-model="searchQuery"
                @keyup.enter="performSearch"
                type="text"
                id="search"
                placeholder="Nach Seiten suchen..."
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
            </div>
            <button
              @click="performSearch"
              class="mt-2 w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Suchen
            </button>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="mb-8">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Beliebte Seiten</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg mx-auto">
            <router-link
              to="/"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
              </svg>
              Startseite
            </router-link>

            <router-link
              v-if="userRole === 'admin'"
              to="/admin/dashboard"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              Admin Dashboard
            </router-link>

            <router-link
              v-if="userRole === 'reseller'"
              to="/reseller/dashboard"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
              Reseller Dashboard
            </router-link>

            <router-link
              v-if="userRole === 'user'"
              to="/user/projects"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
              </svg>
              Meine Projekte
            </router-link>

            <router-link
              to="/help"
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Hilfe
            </router-link>
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
            
            <router-link
              to="/"
              class="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg class="mr-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
              </svg>
              Zur Startseite
            </router-link>
          </div>
        </div>

        <!-- Recent Pages -->
        <div v-if="recentPages.length > 0" class="mt-12 pt-8 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Zuletzt besuchte Seiten</h3>
          <div class="space-y-2">
            <router-link
              v-for="page in recentPages"
              :key="page.path"
              :to="page.path"
              class="block text-sm text-blue-600 hover:text-blue-800 hover:underline"
            >
              {{ page.name }}
            </router-link>
          </div>
        </div>

        <!-- Help Section -->
        <div class="mt-12 pt-8 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Benötigen Sie Hilfe?</h3>
          <div class="space-y-2 text-sm text-gray-600">
            <p>Wenn Sie die gesuchte Seite nicht finden können:</p>
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
                to="/help"
                class="inline-flex items-center text-blue-600 hover:text-blue-800"
              >
                <svg class="mr-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Hilfe-Center
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
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'

export default {
  name: 'NotFound',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const store = useStore()
    
    const searchQuery = ref('')
    const recentPages = ref([])

    const userRole = computed(() => {
      const user = store.getters['auth/user']
      return user?.role || null
    })

    const goBack = () => {
      if (window.history.length > 1) {
        router.go(-1)
      } else {
        router.push('/')
      }
    }

    const performSearch = () => {
      if (searchQuery.value.trim()) {
        // Einfache Suche - könnte erweitert werden
        const query = searchQuery.value.toLowerCase().trim()
        
        // Bekannte Routen durchsuchen
        const routes = [
          { path: '/', name: 'Startseite', keywords: ['start', 'home', 'dashboard'] },
          { path: '/admin/dashboard', name: 'Admin Dashboard', keywords: ['admin', 'verwaltung'] },
          { path: '/admin/resellers', name: 'Reseller verwalten', keywords: ['reseller', 'händler'] },
          { path: '/admin/users', name: 'Benutzer verwalten', keywords: ['benutzer', 'user'] },
          { path: '/admin/settings', name: 'Einstellungen', keywords: ['einstellungen', 'settings', 'konfiguration'] },
          { path: '/reseller/dashboard', name: 'Reseller Dashboard', keywords: ['reseller', 'dashboard'] },
          { path: '/reseller/users', name: 'Meine Benutzer', keywords: ['benutzer', 'kunden'] },
          { path: '/reseller/branding', name: 'Branding', keywords: ['branding', 'design', 'logo'] },
          { path: '/user/projects', name: 'Meine Projekte', keywords: ['projekte', 'projects'] },
          { path: '/user/upload', name: 'Projekt hochladen', keywords: ['upload', 'hochladen', 'neu'] },
          { path: '/help', name: 'Hilfe', keywords: ['hilfe', 'help', 'support'] }
        ]

        const matchingRoute = routes.find(route => 
          route.name.toLowerCase().includes(query) ||
          route.keywords.some(keyword => keyword.includes(query))
        )

        if (matchingRoute) {
          router.push(matchingRoute.path)
        } else {
          // Zur Hilfe-Seite mit Suchbegriff
          router.push(`/help?search=${encodeURIComponent(searchQuery.value)}`)
        }
      }
    }

    const loadRecentPages = () => {
      // Aus localStorage laden (falls vorhanden)
      try {
        const stored = localStorage.getItem('chiliview_recent_pages')
        if (stored) {
          recentPages.value = JSON.parse(stored).slice(0, 5) // Nur die letzten 5
        }
      } catch (err) {
        console.warn('Konnte zuletzt besuchte Seiten nicht laden:', err)
      }
    }

    const logPageNotFound = () => {
      // 404-Ereignis für Analytics/Debugging loggen
      const notFoundData = {
        url: route.fullPath,
        referrer: document.referrer,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      }

      // An Backend senden (falls verfügbar)
      try {
        fetch('/api/analytics/404', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(notFoundData)
        }).catch(() => {
          // Fehler beim Senden ignorieren
        })
      } catch (err) {
        // Fehler beim Senden ignorieren
      }

      console.warn('404 - Seite nicht gefunden:', notFoundData)
    }

    onMounted(() => {
      loadRecentPages()
      logPageNotFound()
    })

    return {
      searchQuery,
      recentPages,
      userRole,
      goBack,
      performSearch
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

/* Hover-Effekte */
button:hover, .router-link-active:hover {
  transform: translateY(-1px);
  transition: transform 0.2s ease;
}

/* Responsive Grid */
@media (max-width: 640px) {
  .sm\:grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .sm\:flex-row {
    flex-direction: column;
  }
}

/* Search Box Styling */
input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Quick Links Hover */
.grid a:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
</style>
