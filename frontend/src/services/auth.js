import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export const authService = {
  async login(credentials) {
    try {
      
      const response = await axios.post(`${API_URL}/auth/login`, credentials, {
        timeout: 5000 
      })
      
      const token = response.data.access_token
      if (token) {
        localStorage.setItem('token', token)
        localStorage.setItem('userRole', response.data.role)
        localStorage.setItem('userData', JSON.stringify(response.data.user))
        localStorage.setItem('loginTime', Date.now()) // Add this for session tracking
        
      } else {
        throw new Error('No authentication token received')
      }
      
      return response.data
    } catch (error) {
      
      if (error.code === 'ERR_NETWORK') {
      }
      
      throw error
    }
  },
  
  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('userRole')
    localStorage.removeItem('userData')
    localStorage.removeItem('loginTime')
  },
  
  getCurrentUser() {
    const userData = localStorage.getItem('userData')
    try {
      return userData ? JSON.parse(userData) : null
    } catch (e) {
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
    
    try {
      const base64Url = token.split('.')[1]
      if (!base64Url) return false
      
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const payload = JSON.parse(atob(base64))
      
      // Check if token is expired
      const currentTime = Date.now() / 1000
      return payload.exp > currentTime
    } catch (e) {
      return false
    }
  },

  async register(userData) {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, userData)
      return response.data
    } catch (error) {
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
      return false
    }
  }
} 