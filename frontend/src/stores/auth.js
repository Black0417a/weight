import { defineStore } from 'pinia'
import request from '../utils/request'

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
      const res = await request.post('/auth/login', { email })
      this.token = res.token
      this.user = res.user
      localStorage.setItem('user_token', res.token)
      localStorage.setItem('user_info', JSON.stringify(res.user))
      request.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
      return res
    },

    async adminLogin(username, password) {
      const res = await request.post('/admin/auth/login', { username, password })
      this.adminToken = res.token
      this.admin = res.admin
      this.isAdmin = true
      localStorage.setItem('admin_token', res.token)
      localStorage.setItem('admin_info', JSON.stringify(res.admin))
      request.defaults.headers.common['Authorization'] = `Bearer ${this.adminToken}`
      return res
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('user_token')
      localStorage.removeItem('user_info')
      delete request.defaults.headers.common['Authorization']
    },

    adminLogout() {
      this.adminToken = null
      this.admin = null
      this.isAdmin = false
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_info')
      delete request.defaults.headers.common['Authorization']
    },

    restoreSession() {
      const userToken = localStorage.getItem('user_token')
      if (userToken) {
        this.token = userToken
        request.defaults.headers.common['Authorization'] = `Bearer ${userToken}`
        const userInfo = localStorage.getItem('user_info')
        if (userInfo) {
          try { this.user = JSON.parse(userInfo) } catch {}
        }
      }

      const adminToken = localStorage.getItem('admin_token')
      if (adminToken) {
        this.adminToken = adminToken
        this.isAdmin = true
        request.defaults.headers.common['Authorization'] = `Bearer ${adminToken}`
        const adminInfo = localStorage.getItem('admin_info')
        if (adminInfo) {
          try { this.admin = JSON.parse(adminInfo) } catch {}
        }
      }
    }
  }
})