<template>
  <div class="auth-page py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card border-0 shadow-sm">
            <div class="card-body p-4 p-md-5">
              <!-- Header -->
              <div class="text-center mb-4">
                <RouterLink to="/" class="d-inline-block mb-4">
                  <div class="auth-logo">
                    <i class="bi bi-mortarboard-fill text-primary"></i>
                  </div>
                </RouterLink>
                <h4 class="fw-bold">Welcome Back!</h4>
                <p class="text-secondary">Please sign in to continue</p>
              </div>

              <!-- Alert for errors -->
              <div v-if="error" class="alert alert-danger" role="alert">
                {{ error }}
              </div>

              <!-- Login Form -->
              <form @submit.prevent="handleLogin" class="needs-validation" novalidate>
                <!-- Role Selection -->
                <div class="mb-3">
                  <label class="form-label">Login as</label>
                  <div class="d-flex gap-3">
                    <div class="form-check">
                      <input 
                        class="form-check-input" 
                        type="radio" 
                        name="role" 
                        id="userRole"
                        value="user"
                        v-model="formData.role"
                      >
                      <label class="form-check-label" for="userRole">
                        User
                      </label>
                    </div>
                    <div class="form-check">
                      <input 
                        class="form-check-input" 
                        type="radio" 
                        name="role" 
                        id="adminRole"
                        value="admin"
                        v-model="formData.role"
                      >
                      <label class="form-check-label" for="adminRole">
                        Admin
                      </label>
                    </div>
                  </div>
                </div>

                <!-- Username/Email Field -->
                <div class="mb-3">
                  <label class="form-label">
                    {{ formData.role === 'admin' ? 'Username' : 'Email' }}
                  </label>
                  <input 
                    :type="formData.role === 'admin' ? 'text' : 'email'"
                    class="form-control" 
                    :placeholder="formData.role === 'admin' ? 'Enter username' : 'Enter email'"
                    v-model="formData.username"
                    required
                  >
                </div>

                <!-- Password Field -->
                <div class="mb-4">
                  <label class="form-label">Password</label>
                  <div class="input-group">
                    <input 
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control" 
                      placeholder="Enter password"
                      v-model="formData.password"
                      required
                    >
                    <button 
                      class="btn btn-outline-secondary" 
                      type="button"
                      @click="togglePassword"
                    >
                      <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                    </button>
                  </div>
                </div>

                <!-- Submit Button -->
                <button 
                  type="submit" 
                  class="btn btn-primary w-100"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Sign In
                </button>
              </form>

              <!-- Register Link -->
              <p class="text-center mt-4 mb-0" v-if="formData.role === 'user'">
                Don't have an account? 
                <RouterLink to="/register">Register</RouterLink>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authService } from '@/services/auth'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)
const serverStatus = ref('unknown') // 'unknown', 'online', 'offline'

const formData = reactive({
  role: 'user',
  username: '',
  password: ''
})

onMounted(async () => {
  // Check if user was redirected due to session expiry
  if (route.query.reason === 'session_expired') {
    error.value = 'Your session has expired. Please log in again.'
  }
  
  // Check if server is running
  checkServerStatus()
})

const checkServerStatus = async () => {
  try {
    // Simple ping to check if backend is available
    await axios.get('http://localhost:5000/api/auth/ping', { timeout: 3000 })
    serverStatus.value = 'online'
  } catch (err) {
    if (err.code === 'ERR_NETWORK' || !err.response) {
      serverStatus.value = 'offline'
      error.value = 'Cannot connect to server. Please ensure the backend is running.'
    } else {
      // Server is up but returned an error
      serverStatus.value = 'online'
    }
  }
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async () => {
  try {
    if (serverStatus.value === 'offline') {
      error.value = 'Cannot connect to server. Please ensure the backend is running.'
      await checkServerStatus()
      return
    }
    
    loading.value = true
    error.value = ''
    
    const credentials = {
      role: formData.role,
      password: formData.password
    }

    if (formData.role === 'admin') {
      credentials.username = formData.username
    } else {
      credentials.email = formData.username
    }

    console.log('Attempting login with:', { ...credentials, password: '[HIDDEN]' })
    
    // Use the auth service to login
    const response = await authService.login(credentials)
    console.log('Login successful, response:', response)
    
    // Redirect based on role
    if (response.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  } catch (err) {
    console.error('Login error:', err)
    
    if (err.code === 'ERR_NETWORK' || !err.response) {
      error.value = 'Cannot connect to server. Please ensure the backend is running.'
      serverStatus.value = 'offline'
    } else {
      error.value = err.response?.data?.msg || 'An error occurred during login'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 76px);
  background-color: var(--bs-light);
}

.auth-logo {
  width: 48px;
  height: 48px;
  background-color: var(--bs-primary-bg-subtle);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto;
}

.form-control {
  padding: 0.75rem 1rem;
}

.form-control:focus {
  box-shadow: none;
  border-color: var(--bs-primary);
}
</style>