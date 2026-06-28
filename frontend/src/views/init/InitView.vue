<!--
  CPYCMS - 初始化页面
  首次使用时创建管理员账号和站点配置
-->
<template>
  <div class="min-h-dvh flex flex-col items-center justify-center bg-[var(--cms-page-bg)] text-[var(--cms-text)] px-4 py-12 relative selection:bg-brand-500/30 selection:text-brand-600 transition-colors duration-300 overflow-x-hidden">

    <div class="absolute top-0 -left-4 w-96 h-96 bg-brand-500/10 dark:bg-brand-500/5 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute bottom-0 -right-4 w-96 h-96 bg-purple-500/10 dark:bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>

    <div class="absolute top-4 right-4 left-4 sm:left-auto flex items-center justify-end gap-3 z-50">
      <LocaleSwitcher v-model="currentLocale" @change="onLocaleChange" />

      <button
        @click="toggleTheme"
        type="button"
        class="inline-flex items-center justify-center p-2.5 rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)] text-[var(--cms-text-muted)] hover:text-brand-500 hover:border-brand-500 hover:shadow-xs transition-all cursor-pointer active:scale-95"
        :title="t('common.toggleTheme')"
      >
        <svg class="w-4 h-4 block dark:hidden" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 7a5 5 0 100 10 5 5 0 000-10z" />
        </svg>
        <svg class="w-4 h-4 hidden dark:block text-indigo-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      </button>
    </div>

    <div
      v-motion
      :initial="{ opacity: 0, y: 30, scale: 0.98 }"
      :enter="{ opacity: 1, y: 0, scale: 1, transition: { type: 'spring', damping: 25, stiffness: 120 } }"
      class="w-full max-w-xl bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-2xl p-6 sm:p-9 shadow-2xl relative z-10 transition-colors duration-300"
    >
      <div class="text-center mb-8">
        <h2 class="text-4xl font-black tracking-tight bg-gradient-to-r from-brand-600 via-indigo-500 to-purple-600 bg-clip-text text-transparent">
          {{ t('init.title') }}
        </h2>
        <p class="text-[var(--cms-text-muted)] text-sm mt-2 font-medium tracking-wide">{{ t('init.subtitle') }}</p>
      </div>

      <div v-if="checking" class="flex flex-col items-center justify-center py-14">
        <div class="relative w-10 h-10">
          <div class="absolute inset-0 rounded-full border-4 border-[var(--cms-surface-muted)]"></div>
          <div class="absolute inset-0 rounded-full border-4 border-t-brand-500 animate-spin"></div>
        </div>
        <p class="text-[var(--cms-text-muted)] text-sm mt-4 animate-pulse">{{ t('init.checking') }}</p>
      </div>

      <div v-else-if="initialized" class="text-center py-6">
        <div class="inline-flex items-center justify-center w-14 h-14 bg-emerald-500/10 text-emerald-500 dark:text-emerald-400 rounded-full mb-5 border border-emerald-500/20 shadow-inner">
          <svg class="w-7 h-7" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h5 class="text-xl font-bold text-[var(--cms-text)]">{{ t('init.alreadyInitTitle') }}</h5>
        <p class="text-[var(--cms-text-muted)] text-sm mt-2 mb-8">{{ t('init.alreadyInitDesc') }}</p>

        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <router-link to="/" class="flex items-center justify-center px-5 py-2.5 bg-[var(--cms-surface-muted)] hover:bg-[var(--cms-surface-strong)] active:scale-98 font-semibold rounded-xl transition-all border border-[var(--cms-border)] text-sm text-[var(--cms-text)]">
            {{ t('init.btnHome') }}
          </router-link>
          <router-link to="/admin/login" class="flex items-center justify-center px-5 py-2.5 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 active:scale-98 text-white font-semibold rounded-xl shadow-md shadow-brand-600/10 transition-all text-sm">
            {{ t('init.btnAdmin') }}
          </router-link>
        </div>
      </div>

      <div v-else>
        <div class="space-y-6">
          <div>
            <div class="flex items-center gap-2 mb-4 border-l-4 border-brand-500 pl-2.5">
              <h5 class="text-sm font-bold tracking-wider text-[var(--cms-text)] uppercase">{{ t('init.sectionAdmin') }}</h5>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelUsername') }} <span class="text-rose-500">*</span></label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                  </span>
                  <input v-model="form.username" type="text" autocomplete="off" class="w-full pl-10 pr-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-brand-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-brand-500/10 rounded-xl text-[var(--cms-text)] placeholder-slate-400 dark:placeholder-slate-500 text-sm outline-none transition-all" :placeholder="t('init.placeholderUser')" />
                </div>
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelPassword') }} <span class="text-rose-500">*</span></label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                  </span>
                  <input v-model="form.password" type="password" class="w-full pl-10 pr-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-brand-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-brand-500/10 rounded-xl text-[var(--cms-text)] placeholder-slate-400 dark:placeholder-slate-500 text-sm outline-none transition-all" :placeholder="t('init.placeholderPwd')" />
                </div>
              </div>
            </div>
          </div>

          <div class="w-full border-t border-[var(--cms-border)]/60 my-2"></div>

          <div>
            <div class="flex items-center gap-2 mb-4 border-l-4 border-purple-500 pl-2.5">
              <h5 class="text-sm font-bold tracking-wider text-[var(--cms-text)] uppercase">{{ t('init.sectionSite') }}</h5>
            </div>

            <div class="space-y-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelSiteName') }}</label>
                  <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                    </span>
                    <input v-model="form.site_name" type="text" class="w-full pl-10 pr-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-purple-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-purple-500/10 rounded-xl text-[var(--cms-text)] text-sm outline-none transition-all" />
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelSiteSlogan') }}</label>
                  <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/></svg>
                    </span>
                    <input v-model="form.site_slogan" type="text" class="w-full pl-10 pr-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-purple-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-purple-500/10 rounded-xl text-[var(--cms-text)] text-sm outline-none transition-all" :placeholder="t('init.placeholderSlogan')" />
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelSiteDesc') }}</label>
                <textarea v-model="form.site_description" rows="2" class="w-full px-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-purple-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-purple-500/10 rounded-xl text-[var(--cms-text)] text-sm outline-none transition-all resize-none" :placeholder="t('init.placeholderDesc')"></textarea>
              </div>

              <div>
                <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelBoundDomains') }}</label>
                <textarea v-model="form.bound_domains" rows="2" class="w-full px-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-purple-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-purple-500/10 rounded-xl text-[var(--cms-text)] text-sm outline-none transition-all resize-none" :placeholder="t('init.placeholderBoundDomains')"></textarea>
                <p class="mt-1.5 text-[11px] leading-relaxed text-[var(--cms-text-muted)]">{{ t('init.boundDomainsHelp') }}</p>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelAuthor') }}</label>
                  <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
                    </span>
                    <input v-model="form.author_name" type="text" class="w-full pl-10 pr-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-purple-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-purple-500/10 rounded-xl text-[var(--cms-text)] text-sm outline-none transition-all" :placeholder="t('init.placeholderAuthor')" />
                  </div>
                </div>

                <div>
                  <label class="block text-xs font-bold text-[var(--cms-text-muted)] mb-1.5">{{ t('init.labelEmail') }}</label>
                  <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                    </span>
                    <input v-model="form.author_email" type="email" class="w-full pl-10 pr-4 py-2.5 bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] focus:border-purple-500 focus:bg-[var(--cms-surface)] focus:ring-4 focus:ring-purple-500/10 rounded-xl text-[var(--cms-text)] text-sm outline-none transition-all" :placeholder="t('init.placeholderEmail')" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-5 space-y-3">
          <div v-if="error" class="flex items-center gap-2.5 px-4 py-3 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-500 text-xs">
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span>{{ error }}</span>
          </div>
          <div v-if="success" class="flex items-center gap-2.5 px-4 py-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-500 text-xs">
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span>{{ success }}</span>
          </div>
        </div>

        <button
          type="button"
          class="w-full mt-6 py-3 bg-gradient-to-r from-brand-600 via-indigo-600 to-purple-600 hover:from-brand-500 hover:via-indigo-500 hover:to-purple-500 disabled:from-slate-400 disabled:to-slate-400 dark:disabled:from-slate-800 dark:disabled:to-slate-800 disabled:text-slate-300 dark:disabled:text-slate-600 disabled:cursor-not-allowed text-white font-semibold text-sm rounded-xl transition-all shadow-lg shadow-brand-600/15 active:scale-[0.99] flex items-center justify-center gap-2 cursor-pointer"
          @click="handleInit"
          :disabled="submitting"
        >
          <svg v-if="submitting" class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>{{ submitting ? t('init.btnSubmitting') : t('init.btnSubmit') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { initApi } from '@/services/api'
import { useSiteStore } from '@/stores'
import LocaleSwitcher from '@/components/common/LocaleSwitcher.vue'
import { useTheme } from "@/composables/useTheme"; // 🟢 去掉后缀，让 Vite 自动解析
import { getInitialLocale, applyDocumentLocale, translate, type LanguageCode } from '@/i18n'

const route = useRoute()
const siteStore = useSiteStore()
const checking = ref(true)
const initialized = ref(false)
const submitting = ref(false)
const error = ref('')
const success = ref('')

// 🟢 1. 直接激活并解构主题控制（useTheme 内部的 immediate watch 会在组件创建时自动处理好深浅色 DOM 绑定）
const { toggleTheme } = useTheme()

// 2. 响应式绑定国际化语系
const currentLocale = ref<LanguageCode>(getInitialLocale())

// 代理本地化快捷函数
function t(key: string, vars?: any): string {
  return translate(currentLocale.value, key, vars)
}

function onLocaleChange(locale: LanguageCode) {
  applyDocumentLocale(locale)
}

function safeRedirect(value: unknown, fallback = '/'): string {
  return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//') && !value.startsWith('/init')
    ? value
    : fallback
}

const form = ref({
  username: '',
  password: '',
  site_name: t('common.siteDefaultName'),
  site_slogan: '',
  site_description: '',
  bound_domains: typeof window !== 'undefined' ? window.location.origin : '',
  author_name: '',
  author_email: ''
})

onMounted(async () => {
  // 🟢 3. 移除了多余的旧版手动主题应用命令，只保留国际化语系应用
  applyDocumentLocale(currentLocale.value)

  try {
    const res = await initApi.check()
    initialized.value = !!res.initialized
  } catch {
    /* 拦截异常 */
  } finally {
    checking.value = false
  }
})

async function handleInit() {
  error.value = ''
  success.value = ''

  if (!form.value.username || form.value.username.length < 3) {
    error.value = t('init.errUser')
    return
  }
  if (!form.value.password || form.value.password.length < 6) {
    error.value = t('init.errPwd')
    return
  }

  submitting.value = true
  try {
    const res = await initApi.setup(form.value)
    if (res.code === 200) {
      let verified = !!res.initialized
      if (!verified) {
        const check = await initApi.check()
        verified = !!check.initialized
      }
      if (!verified) {
        error.value = t('init.verifyFailed')
        return
      }
      initialized.value = true
      siteStore.resetSiteCache()
      success.value = res.msg || t('init.successMsg')
      const redirect = safeRedirect(route.query.redirect, '/')

      setTimeout(() => {
        window.location.href = redirect
      }, 800)
    } else {
      error.value = res.msg || `Error: ${res.code}`
    }
  } catch (e: any) {
    error.value = e.message || t('init.timeout')
  } finally {
    submitting.value = false
  }
}
</script>
