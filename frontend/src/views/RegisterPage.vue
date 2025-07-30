<template>
  <div class="auth-page py-5">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body p-4 p-md-5">
              <!-- Header -->
              <div class="text-center mb-4">
                <RouterLink to="/" class="d-inline-block mb-4">
                  <div class="auth-logo">
                    <i class="bi bi-mortarboard-fill text-primary"></i>
                  </div>
                </RouterLink>
                <h4 class="fw-bold">Create Account</h4>
                <p class="text-secondary">Join QuizMaster to start learning</p>
              </div>

              <!-- Alert for errors -->
              <div v-if="error" class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                {{ error }}
              </div>

              <!-- Registration Form -->
              <form @submit.prevent="handleRegister" class="needs-validation" novalidate>
                <!-- Email -->
                <div class="mb-3">
                  <label for="email" class="form-label">Email address</label>
                  <input 
                    type="email" 
                    class="form-control"
                    id="email"
                    v-model="formData.email"
                    required
                    placeholder="Enter your email"
                    autocomplete="email"
                  >
                  <div class="invalid-feedback">
                    Please provide a valid email address.
                  </div>
                </div>

                <!-- Full Name -->
                <div class="mb-3">
                  <label for="fullName" class="form-label">Full Name</label>
                  <input 
                    type="text" 
                    class="form-control"
                    id="fullName"
                    v-model="formData.full_name"
                    required
                    placeholder="Enter your full name"
                    autocomplete="name"
                  >
                  <div class="invalid-feedback">
                    Please provide your full name.
                  </div>
                </div>

                <!-- Password -->
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <div class="input-group">
                    <input 
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control"
                      id="password"
                      v-model="formData.password"
                      required
                      placeholder="Create a password"
                      autocomplete="new-password"
                      minlength="8"
                    >
                    <button 
                      class="btn btn-outline-secondary" 
                      type="button"
                      @click="togglePassword"
                    >
                      <i class="bi" :class="showPassword ? 'bi-eye-slash' : 'bi-eye'"></i>
                    </button>
                  </div>
                  <div class="form-text text-muted">
                    Password must be at least 8 characters long.
                  </div>
                </div>

                <!-- Qualification -->
                <div class="mb-3">
                  <label for="qualification" class="form-label">Qualification</label>
                  <input 
                    type="text" 
                    class="form-control"
                    id="qualification"
                    v-model="formData.qualification"
                    required
                    placeholder="Enter your qualification"
                  >
                  <div class="invalid-feedback">
                    Please provide your qualification.
                  </div>
                </div>

                <!-- Date of Birth -->
                <div class="mb-4">
                  <label for="dob" class="form-label">Date of Birth</label>
                  <input 
                    type="date" 
                    class="form-control"
                    id="dob"
                    v-model="formData.date_of_birth"
                    required
                    autocomplete="bday"
                  >
                  <div class="invalid-feedback">
                    Please provide your date of birth.
                  </div>
                </div>

                <!-- Submit Button -->
                <button 
                  type="submit" 
                  class="btn btn-primary w-100"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Create Account
                </button>
              </form>

              <!-- Login Link -->
              <p class="text-center mt-4 mb-0">
                Already have an account? 
                <RouterLink to="/login">Sign In</RouterLink>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/auth'

const router = useRouter()
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

const formData = reactive({
  email: '',
  full_name: '',
  password: '',
  qualification: '',
  date_of_birth: ''
})

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleRegister = async () => {
  try {
    // Form validation
    const form = document.querySelector('form')
    if (!form.checkValidity()) {
      form.classList.add('was-validated')
      return
    }
    
    loading.value = true
    error.value = ''
    
    if (!formData.date_of_birth) {
      error.value = 'Please enter your date of birth'
      return
    }
    
    if (formData.password.length < 8) {
      error.value = 'Password must be at least 8 characters long'
      return
    }
    
    await authService.register(formData)
    
    router.push({
      path: '/login',
      query: { registered: 'success' }
    })
  } catch (err) {
    console.error('Registration error:', err)
    
    if (err.response) {
      console.error('Error response:', err.response.data)
      error.value = err.response?.data?.msg || 'Registration failed. Please try again.'
    } else if (err.request) {
      error.value = 'Network error. Please check your internet connection.'
    } else {
      error.value = 'An error occurred during registration'
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

/* Add subtle shadow effect on form controls when focused */
.form-control:focus {
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.1);
}
</style>