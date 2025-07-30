<script setup>
import { ref, onMounted } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()
const loading = ref(true)

onMounted(async () => {
  
  try {
    await auth.initAuth()
    
    console.log('Auth state initialized:', {
      isAuthenticated: auth.isAuthenticated.value,
      role: auth.role.value
    })
  } catch (error) {
    console.error('Auth initialization error:', error)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div v-if="!loading">
    <RouterView />
  </div>
  <div v-else class="loading-screen">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<style>
.loading-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>