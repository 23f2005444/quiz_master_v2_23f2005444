import { ref, computed } from 'vue'
import { authService } from '@/services/auth'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export function useAuth() {
  const userData = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Load user data from localStorage on creation
  const loadUserData = () => {
    const storedUser = authService.getCurrentUser()
    if (storedUser) {
      userData.value = storedUser
    }
    return userData.value
  }
  
  loadUserData()

  const user = computed(() => userData.value || {})
  
  const isAuthenticated = computed(() => {
    return authService.isAuthenticated()
  })
  
  const role = computed(() => {
    return authService.getRole()
  })

  const initAuth = async () => {
    loading.value = true
    try {
      const token = authService.getToken()
      if (!token) {
        loading.value = false
        return false
      }


      const isValid = await validateToken()
      
      if (!isValid) {
        authService.logout()
        loading.value = false
        return false
      }

  loadUserData()
      return true
    } catch (e) {
      return false
    } finally {
      loading.value = false
    }
  }

  const validateToken = async () => {
    try {
      const token = authService.getToken()
      if (!token) return false

      // Send request to validation endpoint
      try {
        await axios.get(`${API_URL}/auth/validate`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        return true
      } catch (err) {
        
        return authService.isTokenValid()
      }
    } catch (e) {
      return false
    }
  }

  // Login method
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await authService.login(credentials)
      userData.value = response.user
      return response
    } catch (e) {
      error.value = e.response?.data?.message || 'Login failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  // Logout method
  const logout = () => {
    authService.logout()
    userData.value = null
  }

  // Get user ID helper
  const getUserId = () => {
    return userData.value?.id
  }

  // Update user data
  const updateUserData = (newData) => {
    userData.value = { ...userData.value, ...newData }
    authService.updateUserData(userData.value)
  }

  return {
    user,
    isAuthenticated,
    role,
    loading,
    error,
    initAuth,
    login,
    logout,
    getUserId,
    updateUserData
  }
}