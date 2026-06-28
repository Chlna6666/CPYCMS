/**
 * CPYCMS - 管理员认证状态
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type ApiResponse, type UserInfo } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const isLoggedIn = ref(false)
  const checked = ref(false)
  const checking = ref(false)
  let checkingPromise: Promise<void> | null = null

  async function checkAuth(force = false): Promise<void> {
    if (!force && checked.value) return
    if (!force && checkingPromise) return checkingPromise

    checking.value = true
    checkingPromise = (async () => {
      try {
        const res = await authApi.check()
        if (res.logged_in && res.data?.is_admin !== false) {
          user.value = res.data || null
          isLoggedIn.value = true
        } else {
          user.value = null
          isLoggedIn.value = false
        }
      } catch {
        user.value = null
        isLoggedIn.value = false
      } finally {
        checked.value = true
        checking.value = false
        checkingPromise = null
      }
    })()
    return checkingPromise
  }

  async function refreshAuth(): Promise<void> {
    return checkAuth(true)
  }

  async function requireAuth(): Promise<boolean> {
    try {
      await checkAuth()
      return isLoggedIn.value
    } catch {
      return false
    }
  }

  async function login(username: string, password: string): Promise<ApiResponse<UserInfo>> {
    const res = await authApi.login({ username, password })
    if (res.code === 200) {
      user.value = res.data || null
      isLoggedIn.value = res.data?.is_admin !== false
      checked.value = true
    }
    return res
  }

  async function logout(): Promise<void> {
    try {
      await authApi.logout()
    } finally {
      clearAuth()
    }
  }

  function clearAuth(): void {
    user.value = null
    isLoggedIn.value = false
    checked.value = true
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('cpycms:auth-expired', clearAuth)
  }

  return { user, isLoggedIn, checked, checking, checkAuth, refreshAuth, requireAuth, login, logout, clearAuth }
})
