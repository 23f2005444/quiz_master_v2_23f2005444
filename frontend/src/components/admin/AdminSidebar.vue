<template>
  <div class="sidebar bg-light border-end">
    <div class="d-flex flex-column h-100">
      <div class="p-3 border-bottom">
        <h5 class="fw-bold text-primary">
          <i class="bi bi-speedometer2 me-2"></i>
          Admin Panel
        </h5>
      </div>
      
      <ul class="nav flex-column p-3">
        <li class="nav-item mb-2">
          <router-link 
            to="/admin" 
            class="nav-link d-flex align-items-center"
            active-class="active"
            exact
          >
            <i class="bi bi-house-door me-2"></i>
            Dashboard
          </router-link>
        </li>
        
        <li class="nav-item mb-2">
          <router-link 
            to="/admin/subjects" 
            class="nav-link d-flex align-items-center"
            active-class="active"
          >
            <i class="bi bi-book me-2"></i>
            Subjects
          </router-link>
        </li>
        
        <li class="nav-item mb-2">
          <router-link 
            to="/admin/users" 
            class="nav-link d-flex align-items-center"
            active-class="active"
          >
            <i class="bi bi-people me-2"></i>
            Users
          </router-link>
        </li>
        
        <!-- Add this new nav item -->
        <li class="nav-item mb-2">
          <router-link 
            to="/admin/email-tasks" 
            class="nav-link d-flex align-items-center"
            active-class="active"
          >
            <i class="bi bi-envelope-paper me-2"></i>
            Email Tasks
          </router-link>
        </li>
      </ul>
      
      <div class="mt-auto p-3 border-top">
        <div class="d-grid">
          <button @click="logout" class="btn btn-outline-danger btn-sm d-flex align-items-center justify-content-center">
            <i class="bi bi-box-arrow-left me-2"></i>
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { logout: authLogout } = useAuth()

const logout = async () => {
  await authLogout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: calc(100vh - 56px);
  position: sticky;
  top: 56px;
}

.nav-link {
  color: #4b5563;
  border-radius: 0.25rem;
  padding: 0.5rem 0.75rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background-color: #f3f4f6;
  color: #1f2937;
}

.nav-link.active {
  background-color: #e5edff;
  color: #3b82f6;
  font-weight: 600;
}

@media (max-width: 992px) {
  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
    top: 0;
  }
}
</style>