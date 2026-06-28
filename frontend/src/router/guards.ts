import { initApi } from '@/services/api'
import { useAuthStore, useUiStore } from '@/stores'
import type { Router } from 'vue-router'

export function installRouterGuards(router: Router): void {
  router.beforeEach(async (to, _from, next) => {
    const uiStore = useUiStore()
    const titleKey = to.meta.titleKey as string | undefined
    const title = titleKey ? uiStore.t(titleKey) : undefined
    document.title = title ? `${title} - CPYCMS` : 'CPYCMS'
    const authStore = useAuthStore()
    const safeRedirect = (value: unknown, fallback = '/') => {
      return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//') && !value.startsWith('/init') ? value : fallback
    }

    try {
      const initRes = await initApi.check()
      const initialized = !!initRes.initialized
      if (to.name === 'Init') {
        if (initialized) {
          next(safeRedirect(to.query.redirect, '/'))
          return
        }
      } else if (!initialized) {
        next({ name: 'Init', query: { redirect: to.fullPath } })
        return
      }
    } catch {
      if (to.name !== 'Init') {
        next({ name: 'Init', query: { redirect: to.fullPath } })
        return
      }
    }

    if (to.name !== 'Init') {
      await authStore.checkAuth()
    }

    if (to.matched.some(record => record.meta.requiresAuth)) {
      if (!authStore.isLoggedIn) {
        next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
        return
      }
      if (authStore.user?.is_admin === false) {
        authStore.clearAuth()
        next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
        return
      }
    }

    next()
  })
}
