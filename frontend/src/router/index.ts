/**
 * CPYCMS - 路由入口
 */
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { installRouterGuards } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

installRouterGuards(router)

export default router
