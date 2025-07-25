import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export const authService = {
  async login(credentials) {
    try {
      console.log('Starting login request to:', `${API_URL}/auth/login`)
      
      const response = await axios.post(`${API_URL}/auth/login`, credentials, {
        timeout: 5000 // 5-second timeout
      })
      
      // Store token and user data
      const token = response.data.access_token
      if (token) {
        localStorage.setItem('token', token)
        localStorage.setItem('userRole', response.data.role)
        localStorage.setItem('userData', JSON.stringify(response.data.user))
        localStorage.setItem('loginTime', Date.now()) // Add this for session tracking
        
        console.log('Authentication successful, token received')
      } else {
        console.error('No token received in login response')
        throw new Error('No authentication token received')
      }
      
      return response.data
    } catch (error) {
      console.error('Login error:', error)
      
      if (error.code === 'ERR_NETWORK') {
        console.error('Network error - backend might be down')
      }
      
      throw error
    }
  },
  
  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('userRole')
    localStorage.removeItem('userData')
    localStorage.removeItem('loginTime')
    console.log('User logged out')
  },
  
  getCurrentUser() {
    const userData = localStorage.getItem('userData')
    try {
      return userData ? JSON.parse(userData) : null
    } catch (e) {
      console.error('Error parsing user data from storage:', e)
      return null
    }
  },
  
  updateUserData(userData) {
    localStorage.setItem('userData', JSON.stringify(userData))
  },
  
  isAuthenticated() {
    return this.isTokenValid()
  },
  
  getRole() {
    return localStorage.getItem('userRole')
  },

  getToken() {
    return localStorage.getItem('token')
  },
  
  isTokenValid() {
    const token = this.getToken()
    if (!token) return false
    
    // Simple expiration check for JWT tokens
    try {
      // Split the token to get the payload part
      const base64Url = token.split('.')[1]
      if (!base64Url) return false
      
      // Decode the base64 string
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const payload = JSON.parse(atob(base64))
      
      // Check if token is expired
      const currentTime = Date.now() / 1000
      return payload.exp > currentTime
    } catch (e) {
      console.error('Error checking token validity:', e)
      return false
    }
  },

  async register(userData) {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, userData)
      console.log('Registration successful:', response.data)
      return response.data
    } catch (error) {
      console.error('Registration error:', error.response?.data || error.message)
      throw error
    }
  },
  
  // Validate token with server
  async validateTokenWithServer() {
    try {
      const token = this.getToken()
      if (!token) return false
      
      const response = await axios.get(`${API_URL}/auth/validate`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      return response.data?.valid === true
    } catch (error) {
      console.error('Token validation error:', error)
      return false
    }
  }
} 