/**
 * ChiliView Router-Konfiguration
 * Vue Router 4 mit rollenbasierter Navigation
 */

import { createRouter, createWebHistory } from 'vue-router'

// Layout-Komponenten
const DefaultLayout = () => import('@/layouts/DefaultLayout.vue')
const AuthLayout = () => import('@/layouts/AuthLayout.vue')
const ResellerLayout = () => import('@/layouts/ResellerLayout.vue')

// Auth-Views
const Login = () => import('@/views/auth/Login.vue')
const Unauthorized = () => import('@/views/auth/Unauthorized.vue')

// Admin-Views
const AdminDashboard = () => import('@/views/admin/Dashboard.vue')
const AdminResellers = () => import('@/views/admin/Resellers.vue')
const AdminResellerDetail = () => import('@/views/admin/ResellerDetail.vue')
const AdminUsers = () => import('@/views/admin/Users.vue')
const AdminSystemLogs = () => import('@/views/admin/SystemLogs.vue')
const AdminBackups = () => import('@/views/admin/Backups.vue')
const AdminSettings = () => import('@/views/admin/Settings.vue')

// Reseller-Views
const ResellerDashboard = () => import('@/views/reseller/Dashboard.vue')
const ResellerUsers = () => import('@/views/reseller/Users.vue')
const ResellerUserDetail = () => import('@/views/reseller/UserDetail.vue')
const ResellerBranding = () => import('@/views/reseller/Branding.vue')
const ResellerSettings = () => import('@/views/reseller/Settings.vue')
const ResellerBackup = () => import('@/views/reseller/Backup.vue')

// User-Views
const UserDashboard = () => import('@/views/user/Dashboard.vue')
const UserProjects = () => import('@/views/user/Projects.vue')
const UserProjectDetail = () => import('@/views/user/ProjectDetail.vue')
const UserProjectUpload = () => import('@/views/user/ProjectUpload.vue')
const UserProfile = () => import('@/views/user/Profile.vue')

// Viewer-Views
const ProjectViewer = () => import('@/views/viewer/ProjectViewer.vue')

// Error-Views
const NotFound = () => import('@/views/errors/NotFound.vue')
const ServerError = () => import('@/views/errors/ServerError.vue')

const routes = [
  // Redirect root to login
  {
    path: '/',
    redirect: '/login'
  },

  // Authentication Routes
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      layout: 'auth',
      requiresAuth: false,
      title: 'Anmelden - ChiliView'
    }
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: Unauthorized,
    meta: {
      layout: 'auth',
      requiresAuth: false,
      title: 'Nicht autorisiert - ChiliView'
    }
  },

  // Admin Routes
  {
    path: '/admin',
    component: DefaultLayout,
    meta: {
      requiresAuth: true,
      roles: ['admin']
    },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: {
          title: 'Admin Dashboard - ChiliView',
          breadcrumb: 'Dashboard'
        }
      },
      {
        path: 'resellers',
        name: 'AdminResellers',
        component: AdminResellers,
        meta: {
          title: 'Reseller-Verwaltung - ChiliView',
          breadcrumb: 'Reseller'
        }
      },
      {
        path: 'resellers/:resellerId',
        name: 'AdminResellerDetail',
        component: AdminResellerDetail,
        meta: {
          title: 'Reseller-Details - ChiliView',
          breadcrumb: 'Reseller-Details'
        }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers,
        meta: {
          title: 'Benutzer-Verwaltung - ChiliView',
          breadcrumb: 'Benutzer'
        }
      },
      {
        path: 'logs',
        name: 'AdminSystemLogs',
        component: AdminSystemLogs,
        meta: {
          title: 'System-Logs - ChiliView',
          breadcrumb: 'System-Logs'
        }
      },
      {
        path: 'backups',
        name: 'AdminBackups',
        component: AdminBackups,
        meta: {
          title: 'Backup-Verwaltung - ChiliView',
          breadcrumb: 'Backups'
        }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: AdminSettings,
        meta: {
          title: 'System-Einstellungen - ChiliView',
          breadcrumb: 'Einstellungen'
        }
      }
    ]
  },

  // Reseller Routes
  {
    path: '/reseller/:resellerId',
    component: ResellerLayout,
    meta: {
      requiresAuth: true,
      roles: ['admin', 'reseller']
    },
    children: [
      {
        path: '',
        redirect: 'dashboard'
      },
      {
        path: 'dashboard',
        name: 'ResellerDashboard',
        component: ResellerDashboard,
        meta: {
          title: 'Reseller Dashboard - ChiliView',
          breadcrumb: 'Dashboard'
        }
      },
      {
        path: 'users',
        name: 'ResellerUsers',
        component: ResellerUsers,
        meta: {
          title: 'Benutzer-Verwaltung - ChiliView',
          breadcrumb: 'Benutzer'
        }
      },
      {
        path: 'users/:userId',
        name: 'ResellerUserDetail',
        component: ResellerUserDetail,
        meta: {
          title: 'Benutzer-Details - ChiliView',
          breadcrumb: 'Benutzer-Details'
        }
      },
      {
        path: 'branding',
        name: 'ResellerBranding',
        component: ResellerBranding,
        meta: {
          title: 'Branding - ChiliView',
          breadcrumb: 'Branding'
        }
      },
      {
        path: 'settings',
        name: 'ResellerSettings',
        component: ResellerSettings,
        meta: {
          title: 'Einstellungen - ChiliView',
          breadcrumb: 'Einstellungen'
        }
      },
      {
        path: 'backup',
        name: 'ResellerBackup',
        component: ResellerBackup,
        meta: {
          title: 'Backup - ChiliView',
          breadcrumb: 'Backup'
        }
      }
    ]
  },

  // User Routes (Reseller-spezifisch)
  {
    path: '/reseller/:resellerId/user',
    component: DefaultLayout,
    meta: {
      requiresAuth: true,
      roles: ['admin', 'reseller', 'user']
    },
    children: [
      {
        path: '',
        redirect: 'dashboard'
      },
      {
        path: 'dashboard',
        name: 'UserDashboard',
        component: UserDashboard,
        meta: {
          title: 'Dashboard - ChiliView',
          breadcrumb: 'Dashboard'
        }
      },
      {
        path: 'projects',
        name: 'UserProjects',
        component: UserProjects,
        meta: {
          title: 'Meine Projekte - ChiliView',
          breadcrumb: 'Projekte'
        }
      },
      {
        path: 'projects/upload',
        name: 'UserProjectUpload',
        component: UserProjectUpload,
        meta: {
          title: 'Projekt hochladen - ChiliView',
          breadcrumb: 'Upload'
        }
      },
      {
        path: 'projects/:projectId',
        name: 'UserProjectDetail',
        component: UserProjectDetail,
        meta: {
          title: 'Projekt-Details - ChiliView',
          breadcrumb: 'Projekt-Details'
        }
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: UserProfile,
        meta: {
          title: 'Mein Profil - ChiliView',
          breadcrumb: 'Profil'
        }
      }
    ]
  },

  // Viewer Routes (öffentlich für authentifizierte Benutzer)
  {
    path: '/viewer/:resellerId/:projectId',
    name: 'ProjectViewer',
    component: ProjectViewer,
    meta: {
      requiresAuth: true,
      title: '3D-Viewer - ChiliView',
      hideNavigation: true
    }
  },

  // Error Routes
  {
    path: '/500',
    name: 'ServerError',
    component: ServerError,
    meta: {
      layout: 'auth',
      requiresAuth: false,
      title: 'Serverfehler - ChiliView'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      layout: 'auth',
      requiresAuth: false,
      title: 'Seite nicht gefunden - ChiliView'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation Guards
router.beforeEach((to, from, next) => {
  // Titel setzen
  if (to.meta.title) {
    document.title = to.meta.title
  }

  next()
})

// Error Handling
router.onError((error) => {
  console.error('Router Error:', error)
  
  // Bei Chunk-Load-Fehlern Seite neu laden
  if (error.message.includes('Loading chunk')) {
    window.location.reload()
  }
})

export default router

// Route Helper Functions
export const getRoutesByRole = (role) => {
  const roleRoutes = {
    admin: [
      { name: 'AdminDashboard', path: '/admin/dashboard', icon: 'HomeIcon', label: 'Dashboard' },
      { name: 'AdminResellers', path: '/admin/resellers', icon: 'BuildingOfficeIcon', label: 'Reseller' },
      { name: 'AdminUsers', path: '/admin/users', icon: 'UsersIcon', label: 'Benutzer' },
      { name: 'AdminSystemLogs', path: '/admin/logs', icon: 'DocumentTextIcon', label: 'System-Logs' },
      { name: 'AdminBackups', path: '/admin/backups', icon: 'ArchiveBoxIcon', label: 'Backups' },
      { name: 'AdminSettings', path: '/admin/settings', icon: 'CogIcon', label: 'Einstellungen' }
    ],
    reseller: [
      { name: 'ResellerDashboard', path: '/reseller/:resellerId/dashboard', icon: 'HomeIcon', label: 'Dashboard' },
      { name: 'ResellerUsers', path: '/reseller/:resellerId/users', icon: 'UsersIcon', label: 'Benutzer' },
      { name: 'ResellerBranding', path: '/reseller/:resellerId/branding', icon: 'PaintBrushIcon', label: 'Branding' },
      { name: 'ResellerSettings', path: '/reseller/:resellerId/settings', icon: 'CogIcon', label: 'Einstellungen' },
      { name: 'ResellerBackup', path: '/reseller/:resellerId/backup', icon: 'ArchiveBoxIcon', label: 'Backup' }
    ],
    user: [
      { name: 'UserDashboard', path: '/reseller/:resellerId/user/dashboard', icon: 'HomeIcon', label: 'Dashboard' },
      { name: 'UserProjects', path: '/reseller/:resellerId/user/projects', icon: 'FolderIcon', label: 'Projekte' },
      { name: 'UserProjectUpload', path: '/reseller/:resellerId/user/projects/upload', icon: 'CloudArrowUpIcon', label: 'Upload' },
      { name: 'UserProfile', path: '/reseller/:resellerId/user/profile', icon: 'UserIcon', label: 'Profil' }
    ]
  }

  return roleRoutes[role] || []
}

export const buildRoutePath = (path, params = {}) => {
  let builtPath = path
  
  Object.keys(params).forEach(key => {
    builtPath = builtPath.replace(`:${key}`, params[key])
  })
  
  return builtPath
}