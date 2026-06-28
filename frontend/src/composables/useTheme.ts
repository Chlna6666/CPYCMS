/**
 * CPYCMS - 全局主题色响应式状态管理
 * 规范路径：src/composables/useTheme.ts
 */
import { computed, ref, watch } from 'vue'

export type ThemeMode = 'light' | 'dark'

const STORAGE_KEY = 'cpycms.theme'

const theme = ref<ThemeMode>(getInitialTheme())
const isDark = computed(() => theme.value === 'dark')
let watcherReady = false

function getInitialTheme(): ThemeMode {
  if (typeof window === 'undefined') return 'light'
  const stored = window.localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyTheme(nextTheme: ThemeMode): void {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.dataset.theme = nextTheme
  root.dataset.bsTheme = nextTheme
  root.classList.toggle('dark', nextTheme === 'dark')
  root.style.colorScheme = nextTheme
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, nextTheme)
  }
}

function ensureThemeWatcher(): void {
  if (watcherReady) return
  watcherReady = true
  watch(theme, applyTheme, { immediate: true })
}

export function useTheme() {
  ensureThemeWatcher()

  function setTheme(nextTheme: ThemeMode): void {
    theme.value = nextTheme
  }

  function toggleTheme(): void {
    setTheme(theme.value === 'light' ? 'dark' : 'light')
  }

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme
  }
}
