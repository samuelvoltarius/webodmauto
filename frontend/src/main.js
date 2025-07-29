/**
 * ChiliView Frontend - Hauptanwendung
 * Vue.js 3 SPA mit Router, State Management und Internationalisierung
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import Toast from 'vue-toastification'
import NProgress from 'nprogress'

import App from './App.vue'
import router from './router'
import { useAuthStore } from '@stores/auth'

// Styles
import './assets/css/main.css'
import 'vue-toastification/dist/index.css'
import 'nprogress/nprogress.css'

// Internationalisierung
const i18n = createI18n({
  locale: 'de',
  fallbackLocale: 'en',
  messages: {
    de: {
      // Deutsche Übersetzungen
      nav: {
        dashboard: 'Dashboard',
        projects: 'Projekte',
        users: 'Benutzer',
        resellers: 'Reseller',
        settings: 'Einstellungen',
        logout: 'Abmelden'
      },
      auth: {
        login: 'Anmelden',
        logout: 'Abmelden',
        username: 'Benutzername',
        password: 'Passwort',
        email: 'E-Mail',
        loginFailed: 'Anmeldung fehlgeschlagen',
        loginSuccess: 'Erfolgreich angemeldet',
        logoutSuccess: 'Erfolgreich abgemeldet'
      },
      common: {
        save: 'Speichern',
        cancel: 'Abbrechen',
        delete: 'Löschen',
        edit: 'Bearbeiten',
        create: 'Erstellen',
        loading: 'Lädt...',
        error: 'Fehler',
        success: 'Erfolgreich',
        confirm: 'Bestätigen',
        yes: 'Ja',
        no: 'Nein'
      },
      dashboard: {
        welcome: 'Willkommen bei ChiliView',
        statistics: 'Statistiken',
        recentProjects: 'Neueste Projekte',
        systemStatus: 'Systemstatus'
      },
      projects: {
        title: 'Projekte',
        create: 'Neues Projekt',
        upload: 'Dateien hochladen',
        processing: 'Verarbeitung läuft',
        completed: 'Abgeschlossen',
        failed: 'Fehlgeschlagen',
        viewModel: '3D-Modell anzeigen'
      },
      users: {
        title: 'Benutzer',
        create: 'Neuer Benutzer',
        active: 'Aktiv',
        inactive: 'Inaktiv',
        lastLogin: 'Letzter Login'
      },
      resellers: {
        title: 'Reseller',
        create: 'Neuer Reseller',
        branding: 'Branding',
        configuration: 'Konfiguration'
      }
    },
    en: {
      // English translations
      nav: {
        dashboard: 'Dashboard',
        projects: 'Projects',
        users: 'Users',
        resellers: 'Resellers',
        settings: 'Settings',
        logout: 'Logout'
      },
      auth: {
        login: 'Login',
        logout: 'Logout',
        username: 'Username',
        password: 'Password',
        email: 'Email',
        loginFailed: 'Login failed',
        loginSuccess: 'Successfully logged in',
        logoutSuccess: 'Successfully logged out'
      },
      common: {
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        create: 'Create',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        confirm: 'Confirm',
        yes: 'Yes',
        no: 'No'
      },
      dashboard: {
        welcome: 'Welcome to ChiliView',
        statistics: 'Statistics',
        recentProjects: 'Recent Projects',
        systemStatus: 'System Status'
      },
      projects: {
        title: 'Projects',
        create: 'New Project',
        upload: 'Upload Files',
        processing: 'Processing',
        completed: 'Completed',
        failed: 'Failed',
        viewModel: 'View 3D Model'
      },
      users: {
        title: 'Users',
        create: 'New User',
        active: 'Active',
        inactive: 'Inactive',
        lastLogin: 'Last Login'
      },
      resellers: {
        title: 'Resellers',
        create: 'New Reseller',
        branding: 'Branding',
        configuration: 'Configuration'
      }
    }
  }
})

// Toast-Konfiguration
const toastOptions = {
  position: 'top-right',
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
}

// NProgress-Konfiguration
NProgress.configure({
  showSpinner: false,
  speed: 500,
  minimum: 0.1
})

// App erstellen
const app = createApp(App)
const pinia = createPinia()

// Plugins registrieren
app.use(pinia)
app.use(router)
app.use(i18n)
app.use(Toast, toastOptions)

// Globale Properties
app.config.globalProperties.$filters = {
  formatDate(date) {
    if (!date) return '-'
    return new Date(date).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  },
  formatFileSize(bytes) {
    if (!bytes) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },
  truncate(text, length = 50) {
    if (!text) return ''
    return text.length > length ? text.substring(0, length) + '...' : text
  }
}

// Router Guards
router.beforeEach(async (to, from, next) => {
  NProgress.start()
  
  const authStore = useAuthStore()
  
  // Authentifizierung prüfen
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Token aus localStorage prüfen
    const token = localStorage.getItem('auth_token')
    if (token) {
      try {
        await authStore.validateToken()
        if (authStore.isAuthenticated) {
          next()
          return
        }
      } catch (error) {
        console.error('Token-Validierung fehlgeschlagen:', error)
        localStorage.removeItem('auth_token')
      }
    }
    
    next('/login')
    return
  }
  
  // Rollen-basierte Zugriffskontrolle
  if (to.meta.roles && to.meta.roles.length > 0) {
    if (!authStore.user || !to.meta.roles.includes(authStore.user.role)) {
      next('/unauthorized')
      return
    }
  }
  
  // Reseller-spezifische Routen
  if (to.params.resellerId && authStore.user?.role === 'user') {
    if (authStore.user.reseller_id !== to.params.resellerId) {
      next('/unauthorized')
      return
    }
  }
  
  next()
})

router.afterEach(() => {
  NProgress.done()
})

// Error Handler
app.config.errorHandler = (error, instance, info) => {
  console.error('Vue Error:', error, info)
  
  // Toast-Benachrichtigung für Benutzer
  if (app.config.globalProperties.$toast) {
    app.config.globalProperties.$toast.error(
      'Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es erneut.'
    )
  }
  
  // Error-Reporting (in Produktion)
  if (import.meta.env.PROD) {
    // Hier könnte ein Error-Reporting-Service integriert werden
    console.error('Production Error:', {
      error: error.message,
      stack: error.stack,
      info,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    })
  }
}

// Unhandled Promise Rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
  
  if (app.config.globalProperties.$toast) {
    app.config.globalProperties.$toast.error(
      'Ein Netzwerkfehler ist aufgetreten. Bitte überprüfen Sie Ihre Verbindung.'
    )
  }
  
  event.preventDefault()
})

// App mounten
app.mount('#app')

// Development-Tools
if (import.meta.env.DEV) {
  window.__VUE_APP__ = app
  console.log('ChiliView Frontend gestartet im Development-Modus')
}