<template>
  <section class="space-y-6">
    <div class="flex items-center justify-between border-b border-[var(--cms-border)] pb-3">
      <h2 class="text-xl font-bold tracking-tight flex items-center gap-2">
        <span class="w-1.5 h-6 rounded-full bg-accent-500"></span>
        {{ title }}
      </h2>
      <router-link to="/portfolio" class="text-xs font-semibold text-accent-500 hover:text-accent-600 flex items-center gap-1 transition-colors">
        <span>{{ allText }}</span>
        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5"/></svg>
      </router-link>
    </div>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 2" :key="i" class="w-full aspect-video bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-2xl p-3 animate-pulse space-y-3 shadow-xs">
        <div class="w-full h-2/3 bg-[var(--cms-surface-strong)] rounded-xl"></div>
        <div class="h-5 bg-[var(--cms-surface-strong)] rounded-md w-2/3"></div>
        <div class="h-4 bg-[var(--cms-surface-strong)] rounded-md w-1/3"></div>
      </div>
    </div>

    <div v-else-if="works.length === 0" class="text-center py-12 border-2 border-dashed border-[var(--cms-border)] rounded-2xl text-[var(--cms-text-muted)] text-sm">
      {{ emptyText }}
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(work, idx) in works"
        :key="work.id"
        v-motion
        :initial="{ opacity: 0, x: 20 }"
        :enter="{ opacity: 1, x: 0, transition: { delay: idx * 100, duration: 400 } }"
        class="group bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-2xl overflow-hidden shadow-xs hover:shadow-md hover:border-accent-500/50 transition-all duration-300"
      >
        <div v-if="work.cover_image" class="relative aspect-video w-full bg-[var(--cms-surface-muted)] overflow-hidden">
          <img
            :src="work.cover_image"
            :alt="work.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-slate-950/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
            <router-link :to="`/portfolio/${work.id}`" class="px-3 py-1.5 rounded-lg bg-white text-slate-900 font-semibold text-xs shadow-sm hover:bg-slate-100 active:scale-95 transition-all">
              {{ detailText }}
            </router-link>
          </div>
        </div>

        <div class="p-4 space-y-1">
          <h3 class="font-bold text-sm text-[var(--cms-text)] truncate group-hover:text-accent-500 transition-colors">
            <router-link :to="`/portfolio/${work.id}`">{{ work.title }}</router-link>
          </h3>
          <p class="text-xs text-[var(--cms-text-muted)] truncate">
            {{ work.description || emptyDescText }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Work } from '@/services/api'

defineProps<{
  loading: boolean
  works: Work[]
  title: string
  allText: string
  emptyText: string
  emptyDescText: string
  detailText: string
}>()
</script>
