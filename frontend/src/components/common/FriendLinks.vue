<template>
  <div v-if="parsedLinks.length > 0" class="space-y-3">
    <h3 v-if="title" class="text-xs font-bold text-[var(--cms-text-muted)] uppercase tracking-wider flex items-center gap-1.5">
      <Link2 class="w-3.5 h-3.5 text-brand-500" />
      <span>{{ title }}</span>
    </h3>
    <div class="flex flex-wrap gap-2">
      <a
        v-for="(item, idx) in parsedLinks"
        :key="idx"
        :href="item.url"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[var(--cms-surface-muted)] hover:bg-brand-500/10 hover:text-brand-500 border border-[var(--cms-border)] text-xs font-medium text-[var(--cms-text-muted)] transition-all duration-200 group active:scale-95"
      >
        <span>{{ item.name }}</span>
        <ExternalLink class="w-3 h-3 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Link2, ExternalLink } from '@lucide/vue'
import { useSiteStore } from '@/stores'

defineProps<{
  title?: string
}>()

const siteStore = useSiteStore()

interface FriendLink {
  name: string
  url: string
}

const parsedLinks = computed<FriendLink[]>(() => {
  const raw = siteStore.siteInfo?.friend_links
  if (!raw) return []
  if (Array.isArray(raw)) {
    return raw.filter(item => item && item.name && item.url)
  }
  if (typeof raw === 'string' && raw.trim()) {
    try {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        return parsed.filter(item => item && item.name && item.url)
      }
    } catch (e) {
      console.warn('友情链接解析失败:', e)
    }
  }
  return []
})
</script>
