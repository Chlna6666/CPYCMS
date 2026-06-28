<template>
  <div class="flex h-screen w-full overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100">

    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm md:hidden"
      v-motion
      :initial="{ opacity: 0 }"
      :enter="{ opacity: 1 }"
      :leave="{ opacity: 0 }"
      @click="sidebarOpen = false"
    ></div>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-64 flex-col bg-white border-r border-slate-200 transition-transform duration-300 ease-in-out dark:bg-slate-950 dark:border-slate-800 md:relative md:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div
        class="flex h-16 shrink-0 items-center px-6"
        v-motion
        :initial="{ opacity: 0, y: -20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 100 } }"
      >
        <div class="flex flex-col">
          <h3 class="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-50">CPYCMS</h3>
          <span class="text-xs text-slate-500 dark:text-slate-400">{{ t('admin.brandSub') }}</span>
        </div>
      </div>

      <nav class="flex-1 space-y-1.5 overflow-y-auto px-4 py-6 custom-scrollbar">
        <router-link
          v-for="(item, index) in navItems"
          :key="item.path"
          :to="item.path"
          class="group flex items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-colors hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-slate-50"
          :class="isExactActive(item.path) ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' : 'text-slate-600 dark:text-slate-400'"
          v-motion
          :initial="{ opacity: 0, x: -20 }"
          :enter="{ opacity: 1, x: 0, transition: { delay: 150 + index * 40 } }"
          @click="closeSidebarOnMobile"
        >
          <div class="flex items-center gap-3">
            <component
              :is="item.icon"
              class="h-5 w-5 transition-transform group-hover:scale-110"
              :class="isExactActive(item.path) ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 dark:text-slate-500'"
              aria-hidden="true"
            />
            {{ item.name }}
          </div>
          <span
            v-if="item.badge && item.badge > 0"
            class="flex h-5 items-center justify-center rounded-full bg-red-500 px-2 text-[10px] font-bold text-white shadow-sm"
          >
            {{ item.badge > 99 ? '99+' : item.badge }}
          </span>
        </router-link>
      </nav>

      <div
        class="shrink-0 border-t border-slate-200 p-4 dark:border-slate-800"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 400 } }"
      >
        <button
          class="group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 transition-colors hover:bg-red-50 hover:text-red-600 dark:text-slate-400 dark:hover:bg-red-500/10 dark:hover:text-red-400"
          @click="handleLogout"
        >
          <LogOut class="h-5 w-5 text-slate-400 transition-transform group-hover:-translate-x-1 group-hover:text-red-600 dark:text-slate-500 dark:group-hover:text-red-400" aria-hidden="true" />
          {{ t('admin.logout') }}
        </button>
      </div>
    </aside>

    <div class="flex flex-1 flex-col min-w-0 overflow-hidden">
      <header
        class="sticky top-0 z-30 flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white/80 px-4 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/80 sm:px-6"
        v-motion
        :initial="{ opacity: 0, y: -10 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 50 } }"
      >
        <button
          class="inline-flex items-center justify-center rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 focus:outline-none dark:text-slate-400 dark:hover:bg-slate-800 md:hidden"
          @click="sidebarOpen = !sidebarOpen"
        >
          <Menu class="h-5 w-5" aria-hidden="true" />
          <span class="sr-only">{{ t('admin.menu') }}</span>
        </button>

        <div class="flex flex-1 items-center justify-end gap-3 sm:gap-4">

          <LocaleSwitcher v-model="localeValue" size="md" />

          <button
            type="button"
            class="flex h-9 items-center justify-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm font-medium text-slate-600 transition-all hover:bg-white hover:shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
            :aria-label="t('common.toggleTheme')"
            :title="t('common.toggleTheme')"
            @click="toggleTheme"
          >
            <Sun v-if="theme === 'dark'" class="h-4 w-4 text-amber-500" aria-hidden="true" />
            <Moon v-else class="h-4 w-4 text-indigo-500" aria-hidden="true" />
            <span class="hidden sm:inline-block">{{ themeLabel }}</span>
          </button>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto bg-slate-50 p-4 dark:bg-slate-900 sm:p-6 lg:p-8 custom-scrollbar">
        <router-view v-slot="{ Component }">
          <transition
            name="fade-slide"
            mode="out-in"
          >
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore, useUiStore } from '@/stores'
import { commentApi, messageApi } from '@/services/api'
import type { LanguageCode } from '@/i18n'
import LocaleSwitcher from '@/components/common/LocaleSwitcher.vue'
import { useTheme } from '@/composables/useTheme'

import {
  Archive,
  FolderTree,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquare,
  MessagesSquare,
  Moon,
  PenLine,
  Settings,
  Sparkles,
  Sun,
  UserRound // <-- 补上这个导入
} from '@lucide/vue'
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUiStore()

// 初始化真正的 Theme 逻辑，用来同步操控 DOM
const { theme, toggleTheme } = useTheme()

const sidebarOpen = ref(false)
const pendingCount = ref(0)
const pendingCommentCount = ref(0)

const t = uiStore.t

// ================= 数据初始化 =================
const localeValue = computed({
  get: () => uiStore.locale,
  set: (value: LanguageCode) => uiStore.setLocale(value)
})

const themeLabel = computed(() => theme.value === 'dark' ? t('common.light') : t('common.dark'))

// ================= 导航栏数据化 =================
const navItems = computed(() => [
  { name: t('admin.dashboard'), path: '/admin', icon: LayoutDashboard },
  { name: t('admin.articles'), path: '/admin/articles', icon: PenLine },
  { name: t('admin.categories'), path: '/admin/categories', icon: FolderTree },
  { name: t('admin.works'), path: '/admin/works', icon: Sparkles },
  { name: t('admin.resources'), path: '/admin/resources', icon: Archive },
  { name: t('admin.messages'), path: '/admin/messages', icon: MessageSquare, badge: pendingCount.value },
  { name: t('admin.comments'), path: '/admin/comments', icon: MessagesSquare, badge: pendingCommentCount.value },
  { name: t('admin.settings'), path: '/admin/settings', icon: Settings },
  { name: t('admin.profile'), path: '/admin/profile', icon: UserRound },
])

// ================= 方法 =================
function isExactActive(path: string) {
  if (path === '/admin') {
    return route.path === '/admin' || route.path === '/admin/'
  }
  return route.path.startsWith(path)
}

function closeSidebarOnMobile() {
  if (window.innerWidth < 768) {
    sidebarOpen.value = false
  }
}

async function handleLogout() {
  if (confirm(t('admin.logoutConfirm'))) {
    await authStore.logout()
    router.push('/admin/login')
  }
}

async function loadPendingCount() {
  try {
    const res = await messageApi.adminGetList({ page: 1, status: 'pending' })
    pendingCount.value = res.data?.total || 0
  } catch { /* 忽略 */ }
}

async function loadPendingCommentCount() {
  try {
    const res = await commentApi.adminGetList({ page: 1, status: 'pending' })
    pendingCommentCount.value = res.data?.total || 0
  } catch { /* 忽略 */ }
}

onMounted(() => {
  authStore.checkAuth()
  loadPendingCount()
  loadPendingCommentCount()
})
</script>

<style scoped>
/* 路由切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease-out;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(15px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-15px);
}

/* 自定义优美滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
  height: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-300);
  border-radius: 20px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-700);
}
</style>