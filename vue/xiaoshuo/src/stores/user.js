import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')

  const isLoggedIn = computed(() => !!token.value)

  const login = async (user, pwd) => {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pwd })
      })
      const data = await res.json()

      if (data.code === 200) {
        token.value = data.data.token
        username.value = data.data.username
        localStorage.setItem('token', data.data.token)
        localStorage.setItem('username', data.data.username)
        return { success: true }
      } else {
        return { success: false, message: data.msg }
      }
    } catch (error) {
      return { success: false, message: '网络错误：' + error.message }
    }
  }

  const register = async (user, pwd) => {
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pwd })
      })
      const data = await res.json()

      if (data.code === 200) {
        return { success: true }
      } else {
        return { success: false, message: data.msg }
      }
    } catch (error) {
      return { success: false, message: '网络错误：' + error.message }
    }
  }

  const logout = () => {
    token.value = ''
    username.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('username')
  }

  const checkAuth = async () => {
    if (!token.value) return false

    try {
      const res = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token.value}` }
      })
      const data = await res.json()
      if (data.code === 200) {
        username.value = data.data.username
        return true
      } else {
        logout()
        return false
      }
    } catch (error) {
      return false
    }
  }

  return {
    token,
    username,
    isLoggedIn,
    login,
    register,
    logout,
    checkAuth
  }
})