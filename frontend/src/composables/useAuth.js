import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

const user = ref(null)
const loading = ref(true)

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isUser = computed(() => user.value?.role === 'user')

  const initAuth = async () => {
    loading.value = true
    const userData = authService.getCurrentUser()
    if (userData) {
      user.value = userData
    }
    loading.value = false
  }

  const login = async (credentials) => {
    const response = await authService.login(credentials)
    user.value = response.user
    return response
  }

  const logout = () => {
    authService.logout()
    user.value = null
  }

  return {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    isUser,
    initAuth,
    login,
    logout
  }
}