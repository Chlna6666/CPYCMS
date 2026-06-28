<template>
  <section class="lg:col-span-2 space-y-6">
    <div class="flex items-center justify-between border-b border-[var(--cms-border)] pb-3">
      <h2 class="text-xl font-bold tracking-tight flex items-center gap-2">
        <span class="w-1.5 h-6 rounded-full bg-brand-500"></span>
        {{ title }}
      </h2>
      <router-link to="/articles" class="text-xs font-semibold text-brand-500 hover:text-brand-600 flex items-center gap-1 transition-colors">
        <span>{{ moreText }}</span>
        <svg class="w-3 h-3" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5"/></svg>
      </router-link>
    </div>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-28 w-full bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-2xl p-4 animate-pulse flex gap-4">
        <div class="w-24 h-full bg-[var(--cms-surface-strong)] rounded-xl shrink-0"></div>
        <div class="flex-1 space-y-2.5 py-1">
          <div class="h-5 bg-[var(--cms-surface-strong)] rounded-md w-3/4"></div>
          <div class="h-4 bg-[var(--cms-surface-strong)] rounded-md w-full"></div>
          <div class="h-3 bg-[var(--cms-surface-strong)] rounded-md w-1/4 mt-2"></div>
        </div>
      </div>
    </div>

    <div v-else-if="articles.length === 0" class="text-center py-12 border-2 border-dashed border-[var(--cms-border)] rounded-2xl text-[var(--cms-text-muted)] text-sm">
      {{ emptyText }}
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 items-start">
      <article
        v-for="(article, idx) in articles.slice(0, 4)"
        :key="article.id"
        class="article-enter group bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-2xl overflow-hidden shadow-xs hover:shadow-md hover:border-brand-500/50 hover:-translate-y-1 transition-all duration-300 flex flex-col"
        :style="{ animationDelay: `${idx * 80}ms` }"
      >
        <div v-if="article.cover_image" class="relative aspect-video w-full bg-[var(--cms-surface-muted)] overflow-hidden shrink-0">
          <img
            :src="article.cover_image"
            :alt="article.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            loading="lazy"
          />
          <span v-if="article.category_name" class="absolute top-3 left-3 px-2.5 py-1 text-[11px] font-bold rounded-lg bg-slate-900/80 backdrop-blur-xs text-white uppercase tracking-wider">
            {{ article.category_name }}
          </span>
        </div>

        <div class="p-4 flex flex-col space-y-2">
          <div class="space-y-1">
            <span v-if="!article.cover_image && article.category_name" class="inline-flex w-fit px-2.5 py-1 text-[11px] font-bold rounded-lg bg-brand-500/10 text-brand-600 uppercase tracking-wider">
              {{ article.category_name }}
            </span>
            <h3 class="font-bold text-base text-[var(--cms-text)] line-clamp-1 group-hover:text-brand-500 transition-colors">
              <router-link :to="`/article/${article.slug}`">{{ article.title }}</router-link>
            </h3>
            <p class="text-xs text-[var(--cms-text-muted)] line-clamp-2 leading-relaxed">
              {{ article.summary || summaryFallback }}
            </p>
          </div>

          <div class="pt-2 flex items-center justify-between text-[11px] text-[var(--cms-text-muted)] border-t border-[var(--cms-border)]/60">
            <span class="flex items-center gap-1">
              {{ formatDate(article.created_at) }}
            </span>
            <span class="flex items-center gap-1">
              {{ article.view_count || 0 }}
            </span>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Article } from '@/services/api'

defineProps<{
  loading: boolean
  articles: Article[]
  title: string
  moreText: string
  emptyText: string
  summaryFallback: string
  formatDate: (dateStr?: string) => string
}>()
</script>

<style scoped>
@keyframes articleFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.article-enter {
  opacity: 0;
  animation: articleFadeIn 0.4s ease-out forwards;
}
</style>
