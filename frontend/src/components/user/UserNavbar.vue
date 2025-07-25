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

      <a class="navbar-brand d-lg-none" href="#">Quiz Master</a>

      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#userNavbar"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="userNavbar">
        <div class="d-flex align-items-center ms-auto">
          <!-- Notifications -->
          <div class="dropdown me-2 me-md-3">
            <button 
              class="btn btn-link text-dark position-relative p-1" 
              type="button" 
              id="dropdownNotification" 
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-bell fs-5"></i>
              <span v-if="notifications.length > 0" 
                    class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                {{ notifications.length > 9 ? '9+' : notifications.length }}
              </span>
            </button>
            <div class="dropdown-menu dropdown-menu-end shadow-sm" aria-labelledby="dropdownNotification" style="width: 300px; max-width: 90vw;">
              <div class="dropdown-header d-flex justify-content-between align-items-center">
                <span>Notifications</span>
                <a href="#" class="text-decoration-none">Mark all as read</a>
              </div>
              <div v-if="notifications.length === 0" class="text-center p-3 text-muted">
                <i class="bi bi-bell-slash mb-2 d-block"></i>
                No new notifications
              </div>
              <a v-for="notification in notifications" :key="notification.id" href="#" class="dropdown-item border-bottom py-2">
                <div class="d-flex">
                  <div class="me-3">
                    <div class="bg-primary text-white rounded-circle p-2">
                      <i class="bi" :class="notification.icon"></i>
                    </div>
                  </div>
                  <div>
                    <p class="mb-1 fw-bold">{{ notification.title }}</p>
                    <p class="small text-muted mb-1">{{ notification.message }}</p>
                    <p class="small text-muted mb-0">{{ notification.time }}</p>
                  </div>
                </div>
              </a>
              <div class="dropdown-footer text-center p-2 border-top">
                <a href="#" class="text-decoration-none">View All Notifications</a>
              </div>
            </div>
          </div>

          <!-- User Menu -->
          <div class="dropdown">
            <button 
              class="btn btn-link text-dark d-flex align-items-center text-decoration-none dropdown-toggle" 
              type="button" 
              id="dropdownUser" 
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <img
                :src="userAvatar"
                class="rounded-circle me-2"
                alt="User"
                width="32"
                height="32"
              />
              <span class="d-none d-sm-inline">{{ userName }}</span>
            </button>
            <ul class="dropdown-menu dropdown-menu-end shadow-sm" aria-labelledby="dropdownUser">
              <li><router-link to="/profile" class="dropdown-item">My Profile</router-link></li>
              <li><router-link to="/attempts" class="dropdown-item">My Quiz Attempts</router-link></li>
              <li><hr class="dropdown-divider" /></li>
              <li><a @click.prevent="logout" class="dropdown-item" href="#">Logout</a></li>
            </ul>
          </div>
        </div>
      </div>
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