import axios from 'axios'
import { ref } from 'vue'
import { authService } from '@/services/auth'

// Create axios instance with base URL
const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
      // Debug logging
      console.log(`API Request to ${config.url}`)
    } else {
      console.warn('No token found for request to:', config.url)
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Add response interceptor for better error handling
apiClient.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API Error:', error)
    console.error('Response data:', error.response?.data)
    
    // Handle 401 unauthorized (expired token)
    if (error.response?.status === 401) {
      authService.logout()
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export function useApi() {
  const error = ref(null)
  
  // Generic GET request
  const get = async (url) => {
    try {
      error.value = null
      return await apiClient.get(url)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    }
  }
  
  // Generic POST request
  const post = async (url, data) => {
    try {
      error.value = null
      return await apiClient.post(url, data)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    }
  }
  
  // Generic PUT request
  const put = async (url, data) => {
    try {
      error.value = null
      return await apiClient.put(url, data)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    }
  }
  
  // Generic DELETE request
  const del = async (url) => {
    try {
      error.value = null
      return await apiClient.delete(url)
    } catch (err) {
      error.value = err.response?.data?.msg || err.message || 'An error occurred'
      throw err
    }
  }
  
  return {
    error,
    get,
    post,
    put,
    delete: del
  }
}