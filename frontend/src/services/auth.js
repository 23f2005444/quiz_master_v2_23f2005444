import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export const authService = {
  async login(credentials) {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, credentials)
      
      // Store token from the response
      const token = response.data.access_token
      if (token) {
        console.log('Got token:', token.substring(0, 20) + '...')
        localStorage.setItem('token', token)
        localStorage.setItem('userRole', response.data.role)
        localStorage.setItem('userData', JSON.stringify(response.data.user))
      } else {
        console.error('No token received in login response')
      }
      
      return response.data
    } catch (error) {
      console.error('Login error:', error.response?.data || error.message)
      throw error
    }
  },
  
  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('userRole')
    localStorage.removeItem('userData')
  },
  
  getCurrentUser() {
    const userData = localStorage.getItem('userData')
    return userData ? JSON.parse(userData) : null
  },
  
  isAuthenticated() {
    return !!localStorage.getItem('token')
  },
  
  getRole() {
    return localStorage.getItem('userRole')
  },

  getToken() {
    return localStorage.getItem('token')
  }
}