<template>
  <header class="sticky top-0 z-40 w-full border-b border-[var(--cms-border)] bg-[var(--cms-surface)]/85 backdrop-blur-xl transition-colors duration-300">
    <div class="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">

      <router-link to="/" class="group flex shrink-0 items-center gap-2" @click="closeMobileMenu">
        <span class="bg-gradient-to-r from-brand-500 to-indigo-500 bg-clip-text text-2xl font-black tracking-tight text-transparent transition-all duration-200 group-hover:opacity-80 active:scale-95 dark:from-brand-400 dark:to-indigo-400">
          {{ siteStore.siteInfo?.site_name || 'CPYCMS' }}
        </span>
      </router-link>

      <nav class="hidden lg:flex items-center gap-1.5 ml-8 mr-auto">
        <router-link
          v-for="item in navLinks"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-xl text-[var(--cms-text-muted)] hover:text-brand-500 hover:bg-[var(--cms-surface-muted)] transition-colors cursor-pointer select-none whitespace-nowrap"
          exact-active-class="!text-brand-600 !bg-brand-500/10 dark:!text-brand-400 dark:!bg-brand-500/20 font-bold"
        >
          <component :is="item.icon" class="h-4 w-4" aria-hidden="true" />
          <span>{{ t(item.langKey) }}</span>
        </router-link>
      </nav>

      <div class="hidden lg:flex items-center gap-3 shrink-0">
        <div class="w-56 xl:w-64 transition-all duration-300 focus-within:w-72">
          <GlobalSearch />
        </div>

        <LocaleSwitcher v-model="uiStore.locale" @change="onLocaleChange" size="sm" />

        <button
          type="button"
          class="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)] text-[var(--cms-text-muted)] hover:text-brand-500 hover:border-brand-500 hover:bg-[var(--cms-surface-muted)] transition-colors active:scale-90"
          :aria-label="t('common.toggleTheme')"
          @click="uiStore.toggleTheme"
        >
          <MoonStar v-if="uiStore.theme === 'dark'" class="h-4.5 w-4.5 text-amber-500" aria-hidden="true" />
          <SunMedium v-else class="h-4.5 w-4.5 text-indigo-500" aria-hidden="true" />
        </button>
      </div>

      <button
        type="button"
        class="inline-flex lg:hidden h-10 w-10 items-center justify-center rounded-xl text-[var(--cms-text-muted)] hover:bg-[var(--cms-surface-muted)] transition-colors active:scale-95"
        :aria-label="t('admin.menu')"
        @click="toggleMobileMenu"
      >
        <Menu class="h-6 w-6" aria-hidden="true" />
      </button>
    </div>
  </header>

  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 scale-95 translate-y-2"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 translate-y-2"
    >
      <div v-if="isMobileMenuOpen" class="fixed inset-0 z-50 flex flex-col bg-[var(--cms-surface)] lg:hidden">

        <div class="flex h-16 shrink-0 items-center justify-between px-4 sm:px-6">
          <router-link to="/" class="flex items-center gap-2" @click="closeMobileMenu">
            <span class="bg-gradient-to-r from-brand-500 to-indigo-500 bg-clip-text text-2xl font-black tracking-tight text-transparent dark:from-brand-400 dark:to-indigo-400">
              {{ siteStore.siteInfo?.site_name || 'CPYCMS' }}
            </span>
          </router-link>

          <button
            type="button"
            class="inline-flex h-10 w-10 items-center justify-center rounded-full text-[var(--cms-text-muted)] hover:bg-[var(--cms-surface-muted)] transition-colors active:scale-95"
            @click="closeMobileMenu"
          >
            <X class="h-6 w-6" aria-hidden="true" />
          </button>
        </div>

        <div class="mx-auto w-full max-w-2xl shrink-0 px-4 pt-2 pb-6 sm:px-6">
          <div class="w-full">
            <GlobalSearch input-id="global-search-mobile" />
          </div>
        </div>

        <div class="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-1 overflow-y-auto px-4 sm:px-6">
          <router-link
            v-for="item in navLinks"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 rounded-2xl px-4 py-3.5 text-base font-medium text-[var(--cms-text-muted)] transition-colors hover:bg-[var(--cms-surface-muted)] hover:text-brand-500"
            exact-active-class="!text-brand-600 !bg-brand-500/10 dark:!text-brand-400 dark:!bg-brand-500/20 font-bold"
            @click="closeMobileMenu"
          >
            <component :is="item.icon" class="h-5 w-5" aria-hidden="true" />
            <span>{{ t(item.langKey) }}</span>
          </router-link>
        </div>

        <div class="mx-auto mt-auto flex w-full max-w-2xl shrink-0 items-center justify-between border-t border-[var(--cms-border)] px-4 py-5 sm:px-6 pb-safe">
          <LocaleSwitcher v-model="uiStore.locale" @change="onLocaleChange" size="md" />

          <button
            type="button"
            class="flex h-10 items-center gap-2 rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)] px-4 text-sm font-medium text-[var(--cms-text-muted)] transition-colors hover:bg-[var(--cms-surface-muted)] active:scale-95"
            @click="uiStore.toggleTheme"
          >
            <template v-if="uiStore.theme === 'dark'">
              <MoonStar class="h-4 w-4 text-amber-500" aria-hidden="true" />
              <span>{{ t('common.light') || '浅色' }}</span>
            </template>
            <template v-else>
              <SunMedium class="h-4 w-4 text-indigo-500" aria-hidden="true" />
              <span>{{ t('common.dark') || '深色' }}</span>
            </template>
          </button>
        </div>

      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import {
  Menu, MoonStar, SunMedium, X,
  Home, FileText, Briefcase, Archive, MessageSquare, User, Mail
} from '@lucide/vue'
import { useUiStore, useSiteStore } from '@/stores'
import LocaleSwitcher from '@/components/common/LocaleSwitcher.vue'
import GlobalSearch from '@/components/search/GlobalSearch.vue'

const uiStore = useUiStore()
const siteStore = useSiteStore()
const t = uiStore.t

const isMobileMenuOpen = ref(false)

const navLinks = [
  { path: '/', langKey: 'nav.home', icon: Home },
  { path: '/articles', langKey: 'nav.articles', icon: FileText },
  { path: '/portfolio', langKey: 'nav.portfolio', icon: Briefcase },
  { path: '/resources', langKey: 'nav.resources', icon: Archive },
  { path: '/guestbook', langKey: 'nav.guestbook', icon: MessageSquare },
  { path: '/about', langKey: 'nav.about', icon: User },
  { path: '/contact', langKey: 'nav.contact', icon: Mail }
]

function toggleMobileMenu() {
  isMobileMenuOpen.value = true
}

function closeMobileMenu() {
  isMobileMenuOpen.value = false
}

function onLocaleChange(locale: any) {
  uiStore.setLocale(locale)
}

// 防滚动穿透：全屏菜单打开时，禁止下层页面滚动
watch(isMobileMenuOpen, (isOpen) => {
  if (typeof document !== 'undefined') {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
})

// 组件销毁时务必重置滚动状态
onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
/* 适配苹果刘海屏等设备底部安全区 */
.pb-safe {
  padding-bottom: max(1.25rem, env(safe-area-inset-bottom));
}
</style>