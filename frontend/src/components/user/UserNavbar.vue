<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white py-2 py-lg-3 shadow-sm">
    <div class="container-fluid">
      <button 
        class="btn btn-link text-dark d-lg-none me-2" 
        type="button"
        @click="toggleSidebar"
        aria-label="Toggle sidebar"
      >
        <i class="bi bi-list fs-4"></i>
      </button>

      <a class="navbar-brand center" href="#">Quiz Master</a>

    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()

const emit = defineEmits(['toggle-sidebar'])

const toggleSidebar = () => {
  emit('toggle-sidebar')
}

const notifications = ref([
  {
    id: 1,
    icon: 'bi-lightning',
    title: 'New Quiz Available',
    message: 'Python Programming Basics quiz is now available',
    time: '10 minutes ago'
  },
  {
    id: 2,
    icon: 'bi-trophy',
    title: 'Congratulations!',
    message: 'You scored 85% on Database Systems quiz',
    time: '1 hour ago'
  }
])

const userName = computed(() => {
  return auth.user?.full_name || 'User'
})

const userAvatar = computed(() => {
  return auth.user?.avatar || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(userName.value) + '&background=random'
})

const logout = () => {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 1030;
}

.dropdown-item:active {
  background-color: #6366f1;
}

/* Touch-friendly dropdowns on mobile */
@media (max-width: 767.98px) {
  .dropdown-item {
    padding: 0.5rem 1rem;
  }
  
  .dropdown-menu {
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  }
}
</style>