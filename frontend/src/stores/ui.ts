/**
 * CPYCMS - 界面偏好状态
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { applyDocumentLocale, getInitialLocale, translate, type LanguageCode } from '@/i18n'
import { useTheme } from '@/composables/useTheme'

export const useUiStore = defineStore('ui', () => {
  const locale = ref<LanguageCode>(getInitialLocale())
  const { theme, toggleTheme } = useTheme()

  function initUi(): void {
    applyDocumentLocale(locale.value)
  }

  function setLocale(nextLocale: LanguageCode): void {
    locale.value = nextLocale
    applyDocumentLocale(nextLocale)
  }

  function setTheme(nextTheme: 'light' | 'dark'): void {
    theme.value = nextTheme
  }

  function t(key: string, vars: Record<string, string | number> = {}): string {
    return translate(locale.value, key, vars)
  }

  return { locale, theme, initUi, setLocale, setTheme, toggleTheme, t }
})
