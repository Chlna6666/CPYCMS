/**
 * CPYCMS - Vue3 应用入口 (TypeScript)
 * 初始化 Vue 实例、注册路由和状态管理
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useUiStore } from '@/stores'
import { installMotion } from '@/app/motion'
import './assets/css/main.css'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia 状态管理，并在挂载前同步 html lang 与主题标记。
const pinia = createPinia()
app.use(pinia)
useUiStore(pinia).initUi()

// 注册路由
app.use(router)
installMotion(app)

// 等待首个路由守卫完成后再挂载，避免刷新前台页面时先渲染未登录态。
void router.isReady().then(() => {
  app.mount('#app')
})
