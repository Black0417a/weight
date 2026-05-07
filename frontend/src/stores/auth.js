import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('user_token') || null,
    isAdmin: false,
    admin: null,
    adminToken: localStorage.getItem('admin_token') || null
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdminLoggedIn: (state) => !!state.adminToken
  },

  actions: {
    async login(email) {
      const res = await axios.post('/api/auth/login', { email })
      this.token = res.data.token
      this.user = res.data.user
      localStorage.setItem('user_token', res.data.token)
      localStorage.setItem('user_info', JSON.stringify(res.data.user))
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      return res.data
    },

    async adminLogin(username, password) {
      const res = await axios.post('/api/admin/auth/login', { username, password })
      this.adminToken = res.data.token
      this.admin = res.data.admin
      this.isAdmin = true
      localStorage.setItem('admin_token', res.data.token)
      localStorage.setItem('admin_info', JSON.stringify(res.data.admin))
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.adminToken}`
      return res.data
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('user_token')
      localStorage.removeItem('user_info')
      delete axios.defaults.headers.common['Authorization']
    },

    adminLogout() {
      this.adminToken = null
      this.admin = null
      this.isAdmin = false
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_info')
      delete axios.defaults.headers.common['Authorization']
    },

    restoreSession() {
      const userToken = localStorage.getItem('user_token')
      if (userToken) {
        this.token = userToken
        axios.defaults.headers.common['Authorization'] = `Bearer ${userToken}`
        const userInfo = localStorage.getItem('user_info')
        if (userInfo) {
          try { this.user = JSON.parse(userInfo) } catch {}
        }
      }

      const adminToken = localStorage.getItem('admin_token')
      if (adminToken) {
        this.adminToken = adminToken
        this.isAdmin = true
        axios.defaults.headers.common['Authorization'] = `Bearer ${adminToken}`
        const adminInfo = localStorage.getItem('admin_info')
        if (adminInfo) {
          try { this.admin = JSON.parse(adminInfo) } catch {}
        }
      }
    }
  }
})
