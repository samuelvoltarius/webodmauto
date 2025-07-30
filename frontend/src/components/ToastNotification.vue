<template>
  <!-- Toast Container -->
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <TransitionGroup name="toast" tag="div">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'max-w-sm w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden',
            getToastClasses(toast.type)
          ]"
        >
          <div class="p-4">
            <div class="flex items-start">
              <!-- Icon -->
              <div class="flex-shrink-0">
                <component :is="getIcon(toast.type)" :class="getIconClasses(toast.type)" />
              </div>
              
              <!-- Content -->
              <div class="ml-3 w-0 flex-1 pt-0.5">
                <p v-if="toast.title" class="text-sm font-medium text-gray-900">
                  {{ toast.title }}
                </p>
                <p :class="[
                  'text-sm',
                  toast.title ? 'text-gray-500 mt-1' : 'text-gray-900'
                ]">
                  {{ toast.message }}
                </p>
              </div>
              
              <!-- Close Button -->
              <div class="ml-4 flex-shrink-0 flex">
                <button
                  @click="removeToast(toast.id)"
                  class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  <span class="sr-only">Schließen</span>
                  <XMarkIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
          
          <!-- Progress Bar -->
          <div
            v-if="toast.duration > 0"
            class="h-1 bg-gray-200"
          >
            <div
              :class="[
                'h-full transition-all ease-linear',
                getProgressBarClasses(toast.type)
              ]"
              :style="{
                width: `${toast.progress}%`,
                transitionDuration: `${toast.duration}ms`
              }"
            ></div>
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

export default {
  name: 'ToastNotification',
  components: {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    XCircleIcon,
    XMarkIcon
  },
  setup() {
    const toasts = ref([])
    let toastId = 0

    // 🍞 Toast hinzufügen
    const addToast = (message, type = 'info', title = null, duration = 5000) => {
      const id = ++toastId
      const toast = {
        id,
        message,
        type,
        title,
        duration,
        progress: 0,
        timer: null
      }

      toasts.value.push(toast)

      // Auto-remove nach duration
      if (duration > 0) {
        // Progress animation
        setTimeout(() => {
          toast.progress = 100
        }, 50)

        // Remove toast
        toast.timer = setTimeout(() => {
          removeToast(id)
        }, duration)
      }

      return id
    }

    // 🗑️ Toast entfernen
    const removeToast = (id) => {
      const index = toasts.value.findIndex(t => t.id === id)
      if (index > -1) {
        const toast = toasts.value[index]
        if (toast.timer) {
          clearTimeout(toast.timer)
        }
        toasts.value.splice(index, 1)
      }
    }

    // 🧹 Alle Toasts entfernen
    const clearToasts = () => {
      toasts.value.forEach(toast => {
        if (toast.timer) {
          clearTimeout(toast.timer)
        }
      })
      toasts.value = []
    }

    // 🎨 Toast-Styling
    const getToastClasses = (type) => {
      const classes = {
        success: 'border-l-4 border-green-400',
        error: 'border-l-4 border-red-400',
        warning: 'border-l-4 border-yellow-400',
        info: 'border-l-4 border-blue-400'
      }
      return classes[type] || classes.info
    }

    const getIcon = (type) => {
      const icons = {
        success: CheckCircleIcon,
        error: XCircleIcon,
        warning: ExclamationTriangleIcon,
        info: InformationCircleIcon
      }
      return icons[type] || icons.info
    }

    const getIconClasses = (type) => {
      const classes = {
        success: 'h-6 w-6 text-green-400',
        error: 'h-6 w-6 text-red-400',
        warning: 'h-6 w-6 text-yellow-400',
        info: 'h-6 w-6 text-blue-400'
      }
      return classes[type] || classes.info
    }

    const getProgressBarClasses = (type) => {
      const classes = {
        success: 'bg-green-400',
        error: 'bg-red-400',
        warning: 'bg-yellow-400',
        info: 'bg-blue-400'
      }
      return classes[type] || classes.info
    }

    // 🌐 Globale Toast-Funktionen bereitstellen
    const setupGlobalToast = () => {
      // Success Toast
      window.showSuccess = (message, title = null, duration = 5000) => {
        return addToast(message, 'success', title, duration)
      }

      // Error Toast
      window.showError = (message, title = null, duration = 8000) => {
        return addToast(message, 'error', title, duration)
      }

      // Warning Toast
      window.showWarning = (message, title = null, duration = 6000) => {
        return addToast(message, 'warning', title, duration)
      }

      // Info Toast
      window.showInfo = (message, title = null, duration = 5000) => {
        return addToast(message, 'info', title, duration)
      }

      // Generic Toast
      window.showToast = addToast

      // Clear all toasts
      window.clearToasts = clearToasts
    }

    // 🔄 Lifecycle
    onMounted(() => {
      setupGlobalToast()
    })

    onUnmounted(() => {
      clearToasts()
      // Cleanup global functions
      delete window.showSuccess
      delete window.showError
      delete window.showWarning
      delete window.showInfo
      delete window.showToast
      delete window.clearToasts
    })

    return {
      toasts,
      addToast,
      removeToast,
      clearToasts,
      getToastClasses,
      getIcon,
      getIconClasses,
      getProgressBarClasses
    }
  }
}
</script>

<style scoped>
/* Toast Transitions */
.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.3s ease-in;
}

.toast-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.toast-move {
  transition: transform 0.3s ease;
}

/* Progress Bar Animation */
.toast-progress {
  animation: toast-progress linear;
}

@keyframes toast-progress {
  from {
    width: 0%;
  }
  to {
    width: 100%;
  }
}

/* Responsive Design */
@media (max-width: 640px) {
  .toast-container {
    left: 1rem;
    right: 1rem;
    top: 1rem;
  }
  
  .toast-container > div {
    max-width: none;
  }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  .toast-container > div {
    background-color: #1f2937;
    color: #f9fafb;
  }
  
  .toast-container .text-gray-900 {
    color: #f9fafb;
  }
  
  .toast-container .text-gray-500 {
    color: #9ca3af;
  }
  
  .toast-container .text-gray-400 {
    color: #6b7280;
  }
}

/* High Contrast Mode */
@media (prefers-contrast: high) {
  .toast-container > div {
    border: 2px solid;
  }
  
  .toast-container .border-green-400 {
    border-color: #10b981;
  }
  
  .toast-container .border-red-400 {
    border-color: #ef4444;
  }
  
  .toast-container .border-yellow-400 {
    border-color: #f59e0b;
  }
  
  .toast-container .border-blue-400 {
    border-color: #3b82f6;
  }
}

/* Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .toast-enter-active,
  .toast-leave-active,
  .toast-move {
    transition: none;
  }
  
  .toast-progress {
    animation: none;
  }
}
</style>