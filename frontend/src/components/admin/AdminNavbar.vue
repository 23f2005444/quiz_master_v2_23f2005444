<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
      <router-link class="navbar-brand d-flex align-items-center" to="/admin">
        <i class="bi bi-mortarboard-fill me-2"></i>
        <span class="fw-bold">Quiz Master</span>
      </router-link>
      
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link" to="/admin">Dashboard</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/subjects">Subjects</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/users">Users</router-link>
          </li>
        </ul>
        
        <div class="d-flex align-items-center">
          <span class="text-light me-3">
            <i class="bi bi-person-circle me-1"></i>
            Admin
          </span>
          <button @click="logout" class="btn btn-outline-light btn-sm">
            <i class="bi bi-box-arrow-right me-1"></i>
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
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
.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand {
  font-size: 1.25rem;
}

.nav-link {
  font-weight: 500;
  transition: color 0.2s ease-in-out;
}

.nav-link:hover {
  color: #5b21b6;
}

.nav-link.router-link-active {
  color: #8b5cf6;
}
</style>