<script setup>
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const { loading, initAuth } = useAuth()

onMounted(() => {
  initAuth()
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