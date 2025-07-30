<template>
  <div class="not-found-container">
    <div class="text-center">
      <div class="error-badge">
        <span>404</span>
      </div>
      
      <div class="mt-4">
        <h1 class="display-5 fw-bold text-primary mb-3">Page Not Found</h1>
        <p class="lead mb-4">Oops! We couldn't find the page you're looking for.</p>
        
        <div class="illustration mb-5">
          <i class="bi bi-search"></i>
          <div class="question-marks">
            <i class="bi bi-question-circle"></i>
            <i class="bi bi-question-circle"></i>
            <i class="bi bi-question-circle"></i>
          </div>
        </div>
        
        <div class="d-flex justify-content-center gap-3">
          <button @click="goBack" class="btn btn-outline-primary btn-lg">
            <i class="bi bi-arrow-left me-2"></i>
            Go Back
          </button>
          
          <router-link :to="homeRoute" class="btn btn-primary btn-lg">
            <i class="bi bi-house-door me-2"></i>
            {{ buttonText }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const auth = useAuth()

// Initialize with safe default values
const isAdmin = ref(false)
const isAuthenticated = ref(false)
const buttonText = ref('Home')

onMounted(() => {
  try {
    if (auth && typeof auth.isAdmin !== 'undefined') {
      isAdmin.value = auth.isAdmin
    }
    
    if (auth && typeof auth.isAuthenticated !== 'undefined') {
      isAuthenticated.value = auth.isAuthenticated
    }
    
    buttonText.value = isAdmin.value ? 'Admin Dashboard' : 
                       isAuthenticated.value ? 'Dashboard' : 'Home'
  } catch (error) {
    console.error('Error accessing authentication state:', error)
  }
})

const homeRoute = computed(() => {
  if (isAdmin.value) {
    return '/admin'
  } else if (isAuthenticated.value) {
    return '/dashboard'
  } else {
    return '/'
  }
})

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background-color: #f8f9fa;
}

.error-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  font-weight: 700;
  color: #fff;
  background-color: #4f46e5;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.2);
}

.illustration {
  position: relative;
  height: 120px;
}

.illustration .bi-search {
  font-size: 5rem;
  color: #4f46e5;
  opacity: 0.7;
}

.question-marks {
  position: absolute;
  top: 0;
  right: 50%;
  transform: translateX(100%);
  display: flex;
  gap: 10px;
}

.question-marks .bi-question-circle {
  font-size: 1.5rem;
  color: #4f46e5;
  opacity: 0.7;
  animation: float 3s infinite ease-in-out;
}

.question-marks .bi-question-circle:nth-child(1) {
  animation-delay: 0s;
}

.question-marks .bi-question-circle:nth-child(2) {
  font-size: 2rem;
  animation-delay: 0.5s;
}

.question-marks .bi-question-circle:nth-child(3) {
  font-size: 1.2rem;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

@media (max-width: 576px) {
  .error-badge {
    width: 120px;
    height: 120px;
    font-size: 3rem;
  }
  
  .display-5 {
    font-size: 1.8rem;
  }
  
  .illustration .bi-search {
    font-size: 4rem;
  }
  
  .d-flex {
    flex-direction: column;
  }
  
  .btn-lg {
    width: 100%;
  }
}
</style>