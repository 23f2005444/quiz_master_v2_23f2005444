import axios from 'axios'
import { ref } from 'vue'
import { authService } from '@/services/auth'

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  },
  // Add timeout to avoid long waits when server is down
  timeout: 10000
})

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  config => {
    // Add token to every request if available
    const token = authService.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout - server might be down')
    } else if (error.code === 'ERR_NETWORK' || !error.response) {
      console.error('Network error - backend server might not be running')
      // Don't redirect to login on network errors - this breaks the UX
      return Promise.reject(new Error('Backend server is not responding. Please check if it\'s running.'))
    }
    
    // Special handling for CORS errors
    if (error.message && error.message.includes('Network Error')) {
      console.error('CORS Error: The API server might not be configured to accept requests from this origin.')
    }
    
    // Handle 401 unauthorized (expired token)
    if (error.response?.status === 401) {
      console.log('Unauthorized request - logging out user')
      authService.logout()
      // Use window.location to force a full page reload
      window.location.href = '/login?reason=session_expired'
    }
    
    return Promise.reject(error)
  }
)

export function useApi() {
  const error = ref(null)
  const isLoading = ref(false)
  
  // Generic GET request
  const get = async (url) => {
    try {
      isLoading.value = true
      error.value = null
      return await apiClient.get(url)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // Generic POST request
  const post = async (url, data) => {
    try {
      isLoading.value = true
      error.value = null
      return await apiClient.post(url, data)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // Generic PUT request
  const put = async (url, data) => {
    try {
      isLoading.value = true
      error.value = null
      return await apiClient.put(url, data)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // Generic DELETE request
  const del = async (url) => {
    try {
      isLoading.value = true
      error.value = null
      return await apiClient.delete(url)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    error,
    isLoading,
    get,
    post,
    put,
    delete: del
  }
}