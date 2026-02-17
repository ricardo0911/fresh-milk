import { defineStore } from 'pinia'
import { login, getUserInfo } from '@/api/user'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || '{}')
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo.is_admin || state.userInfo.is_staff
  },

  actions: {
    async login(username, password) {
      const res = await login({ username, password })
      this.token = res.access
      localStorage.setItem('token', res.access)
      if (res.refresh) {
        localStorage.setItem('refreshToken', res.refresh)
      }
      await this.fetchUserInfo()
      return res
    },

    async fetchUserInfo() {
      const userInfo = await getUserInfo()
      this.userInfo = userInfo
      localStorage.setItem('userInfo', JSON.stringify(userInfo))
      return userInfo
    },

    logout() {
      this.token = ''
      this.userInfo = {}
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userInfo')
    }
  }
})
