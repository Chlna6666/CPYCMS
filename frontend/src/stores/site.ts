/**
 * CPYCMS - 站点信息状态
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { siteApi, type Category, type SiteSettings, type Tag } from '@/services/api'

const SITE_BOOTSTRAP_CACHE_MS = 60_000

export const useSiteStore = defineStore('site', () => {
  const siteInfo = ref<SiteSettings>({} as SiteSettings)
  const categories = ref<Category[]>([])
  const tags = ref<Tag[]>([])
  const loaded = ref(false)
  const loadedAt = ref(0)
  let loadingPromise: Promise<void> | null = null

  function applySiteTheme(info: Partial<SiteSettings>): void {
    const root = document.documentElement
    if (info.theme_primary_color) root.style.setProperty('--site-primary', info.theme_primary_color)
    if (info.theme_accent_color) root.style.setProperty('--site-accent', info.theme_accent_color)
  }

  async function loadSiteInfo(force = false): Promise<void> {
    const cacheFresh = loaded.value && Date.now() - loadedAt.value < SITE_BOOTSTRAP_CACHE_MS
    if (!force && cacheFresh) return
    if (!force && loadingPromise) return loadingPromise

    loadingPromise = (async () => {
      try {
        const res = await siteApi.getBootstrap()
        siteInfo.value = (res.data?.info || {}) as SiteSettings
        applySiteTheme(siteInfo.value)
        categories.value = res.data?.categories || []
        tags.value = res.data?.tags || []
        loaded.value = true
        loadedAt.value = Date.now()
      } catch (e) {
        console.warn('站点信息加载失败:', e)
      } finally {
        loadingPromise = null
      }
    })()
    return loadingPromise
  }

  function resetSiteCache(): void {
    loaded.value = false
    loadedAt.value = 0
    loadingPromise = null
  }

  return { siteInfo, categories, tags, loaded, loadSiteInfo, applySiteTheme, resetSiteCache }
})
