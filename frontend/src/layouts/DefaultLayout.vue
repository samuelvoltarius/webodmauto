<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold">ChiliView</h1>
          </div>
          <div class="flex items-center space-x-4">
            <button @click="logout" class="text-gray-500 hover:text-gray-700">
              Abmelden
            </button>
          </div>
        </div>
      </div>
    </nav>
    <main class="py-6">
      <router-view />
    </main>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'DefaultLayout',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      logout
    }
  }
}
</script>