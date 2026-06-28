<template>
  <div class="min-h-dvh flex flex-col items-center justify-center bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100 px-4 py-12 relative selection:bg-brand-500/30 selection:text-brand-600 transition-colors duration-300 overflow-x-hidden">

    <div class="absolute -top-20 -left-20 w-96 h-96 bg-brand-500/20 dark:bg-brand-500/10 rounded-full blur-[100px] pointer-events-none animate-pulse duration-[6000ms]"></div>
    <div class="absolute -bottom-20 -right-20 w-96 h-96 bg-indigo-500/20 dark:bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none animate-pulse duration-[8000ms]"></div>

    <div class="absolute top-4 right-4 sm:top-6 sm:right-6 flex items-center justify-end gap-3 z-50">
      <LocaleSwitcher v-model="localeValue" size="sm" />

      <button
        @click="toggleTheme"
        type="button"
        class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-white/80 backdrop-blur-sm text-slate-600 transition-all hover:bg-slate-50 hover:text-brand-500 hover:shadow-sm dark:border-slate-800 dark:bg-slate-950/80 dark:text-slate-400 dark:hover:bg-slate-900 dark:hover:text-brand-400 active:scale-95"
        :title="t('common.toggleTheme') || '切换主题'"
      >
        <Sun v-if="theme === 'dark'" class="h-4.5 w-4.5 text-amber-500" />
        <Moon v-else class="h-4.5 w-4.5 text-indigo-500" />
      </button>
    </div>

    <div
      v-motion
      :initial="{ opacity: 0, y: 30, scale: 0.98 }"
      :enter="{ opacity: 1, y: 0, scale: 1, transition: { type: 'spring', damping: 22, stiffness: 120 } }"
      class="w-full max-w-md bg-white/80 backdrop-blur-xl border border-slate-200/80 rounded-2xl p-6 sm:p-10 shadow-xl dark:bg-slate-950/80 dark:border-slate-800/80 relative z-10"
    >
      <div class="text-center mb-8">
        <h2 class="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-brand-500 via-indigo-500 to-purple-500 dark:from-brand-400 dark:via-indigo-400 dark:to-purple-400 bg-clip-text text-transparent mb-2">
          CPYCMS
        </h2>
        <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">
          {{ t('adminLogin.subtitle') || '欢迎回来，请登录您的账户' }}
        </p>
      </div>

      <div class="space-y-5">
        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {{ t('adminLogin.username') || '账号' }}
          </label>
          <div class="relative">
            <User class="absolute left-3.5 top-1/2 h-4.5 w-4.5 -translate-y-1/2 text-slate-400" aria-hidden="true" />
            <input
              v-model="username"
              type="text"
              class="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-200 bg-white/50 text-slate-900 placeholder-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 transition-all outline-none dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-100"
              :placeholder="t('adminLogin.usernamePlaceholder') || '请输入管理员账号'"
              @keyup.enter="handleLogin"
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            {{ t('adminLogin.password') || '密码' }}
          </label>
          <div class="relative">
            <Lock class="absolute left-3.5 top-1/2 h-4.5 w-4.5 -translate-y-1/2 text-slate-400" aria-hidden="true" />
            <input
              v-model="password"
              type="password"
              class="w-full pl-10 pr-4 py-2.5 text-sm rounded-xl border border-slate-200 bg-white/50 text-slate-900 placeholder-slate-400 focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 transition-all outline-none dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-100"
              :placeholder="t('adminLogin.passwordPlaceholder') || '请输入您的密码'"
              @keyup.enter="handleLogin"
            />
          </div>
        </div>

        <Transition name="fade">
          <div v-if="error" class="p-3 text-xs font-medium text-red-600 bg-red-50 border border-red-100 rounded-xl flex items-center gap-2 dark:bg-red-900/20 dark:border-red-900/30 dark:text-red-400">
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>{{ error }}</span>
          </div>
        </Transition>

        <button
          class="w-full h-11 text-sm font-semibold rounded-xl text-white bg-brand-500 hover:bg-brand-600 active:scale-[0.98] transition-all cursor-pointer disabled:opacity-60 disabled:pointer-events-none flex items-center justify-center gap-2 shadow-md shadow-brand-500/20"
          @click="handleLogin"
          :disabled="loading"
        >
          <Loader2 v-if="loading" class="animate-spin h-4.5 w-4.5" />
          <span>{{ loading ? (t('adminLogin.submitting') || '正在登录...') : (t('adminLogin.submit') || '登 录') }}</span>
        </button>
      </div>

      <div class="text-center mt-8 border-t border-slate-100 dark:border-slate-800 pt-5">
        <router-link to="/" class="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-brand-500 transition-colors dark:text-slate-400 dark:hover:text-brand-400">
          <Home class="w-3.5 h-3.5" />
          {{ t('adminLogin.backHome') || '返回网站首页' }}
        </router-link>
        <div class="mt-3 opacity-80">
          <BeianLinks />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore, useUiStore } from '@/stores'
import { useTheme } from '@/composables/useTheme'
import type { LanguageCode } from '@/i18n'

import BeianLinks from '@/components/common/BeianLinks.vue'
import LocaleSwitcher from '@/components/common/LocaleSwitcher.vue'

// 引入高颜值 Lucide 图标
import { Sun, Moon, User, Lock, AlertCircle, Loader2, Home } from '@lucide/vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUiStore()
const t = uiStore.t

// 初始化真正的 Theme 逻辑，用来同步操控 DOM (修复深色模式切换Bug)
const { theme, toggleTheme } = useTheme()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

// 双向绑定语系切换
const localeValue = computed({
  get: () => uiStore.locale,
  set: (value: LanguageCode) => uiStore.setLocale(value)
})

async function handleLogin() {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = t('adminLogin.required') || '请输入账号和密码'
    return
  }
  loading.value = true
  try {
    const res = await authStore.login(username.value, password.value)
    if (res.code === 200 && authStore.isLoggedIn) {
      const queryRedirect = Array.isArray(route.query.redirect) ? route.query.redirect[0] : route.query.redirect
      const redirect = queryRedirect || '/admin'
      router.push(redirect)
    } else {
      error.value = res.msg || t('adminLogin.failed') || '登录失败'
    }
  } catch (err: any) {
    error.value = err?.message || '网络连接异常，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
