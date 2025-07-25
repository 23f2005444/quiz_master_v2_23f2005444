<template>
  <div class="sidebar bg-dark text-white" :class="{ 'sidebar-collapsed': isCollapsed, 'sidebar-hidden': isMobile && !modelValue }">
    <div class="sidebar-header py-3 px-3 d-flex align-items-center justify-content-between">
      <router-link to="/dashboard" class="text-white text-decoration-none d-flex align-items-center">
        <i class="bi bi-mortarboard-fill me-2 fs-4"></i>
        <span v-if="!isCollapsed" class="fs-4">Quiz Master</span>
      </router-link>
      <button 
        class="btn btn-link text-white p-0 d-none d-lg-block" 
        @click="toggleCollapse"
      >
        <i class="bi" :class="isCollapsed ? 'bi-chevron-right' : 'bi-chevron-left'"></i>
      </button>
      <button 
        class="btn-close btn-close-white d-lg-none" 
        @click="closeSidebar"
        aria-label="Close sidebar"
      ></button>
    </div>
    
    <ul class="nav flex-column pt-3">
      <li class="nav-item">
        <router-link to="/dashboard" class="nav-link text-white d-flex align-items-center" @click="handleNavClick">
          <i class="bi bi-speedometer2 me-3"></i>
          <span v-if="!isCollapsed">Dashboard</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link to="/subjects" class="nav-link text-white d-flex align-items-center" @click="handleNavClick">
          <i class="bi bi-book me-3"></i>
          <span v-if="!isCollapsed">Subjects</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link to="/attempts" class="nav-link text-white d-flex align-items-center" @click="handleNavClick">
          <i class="bi bi-journals me-3"></i>
          <span v-if="!isCollapsed">My Attempts</span>
        </router-link>
      </li>
      <li class="nav-item">
        <router-link to="/profile" class="nav-link text-white d-flex align-items-center" @click="handleNavClick">
          <i class="bi bi-person me-3"></i>
          <span v-if="!isCollapsed">My Profile</span>
        </router-link>
      </li>
    </ul>
    
    <div class="mt-auto p-3" v-if="!isCollapsed">
      <div class="d-grid">
        <button @click="logout" class="btn btn-outline-light">
          <i class="bi bi-box-arrow-right me-2"></i> Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()
const isCollapsed = ref(false)
const isMobile = ref(false)

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const toggleCollapse = () => {
  if (isMobile.value) return
  
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebarCollapsed', isCollapsed.value.toString())
}

const closeSidebar = () => {
  emit('close')
}

const handleNavClick = () => {
  if (isMobile.value) {
    closeSidebar()
  }
}

const checkScreenSize = () => {
  isMobile.value = window.innerWidth < 992
  
  if (isMobile.value) {
    isCollapsed.value = false
  } else {
    isCollapsed.value = localStorage.getItem('sidebarCollapsed') === 'true'
  }
}

const logout = () => {
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1040;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.sidebar-collapsed {
  width: 70px;
}

.sidebar-hidden {
  transform: translateX(-100%);
}

.sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-item {
  margin-bottom: 5px;
}

.nav-link {
  padding: 10px 15px;
  border-radius: 5px;
  margin: 0 8px;
  white-space: nowrap;
}

.nav-link:hover,
.nav-link.active {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link i {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}

@media (max-width: 991.98px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar-visible {
    transform: translateX(0);
  }
}
</style>