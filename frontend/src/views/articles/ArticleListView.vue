<template>
  <div class="mx-auto w-full max-w-5xl px-4 py-8 sm:py-12">
    <header class="mb-10 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
          {{ t('articles.title') }}
        </h1>
        <p class="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
          {{ t('globalSearch.articleListHint') }}
        </p>
      </div>

      <div class="flex items-center gap-3">
        <div class="relative min-w-[160px]">
          <Filter class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
          <select
            v-model="filters.category_id"
            class="h-10 w-full appearance-none rounded-xl border border-slate-200 bg-white pl-9 pr-8 text-sm text-slate-700 outline-none transition-colors hover:border-slate-300 focus:border-brand-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300"
            @change="loadArticles"
          >
            <option :value="0">{{ t('articles.allCategories') }}</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <ChevronDown class="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        </div>
      </div>
    </header>

    <div v-if="loading" class="flex flex-col gap-4">
      <div v-for="i in 4" :key="i" class="h-36 w-full animate-pulse rounded-2xl border border-slate-100 bg-slate-50/50 dark:border-slate-800/50 dark:bg-slate-900/50"></div>
    </div>

    <div v-else-if="articles.length === 0" class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 py-24 text-slate-400 dark:border-slate-800">
      <BookOpen class="mb-3 h-10 w-10 opacity-20" aria-hidden="true" />
      <p class="text-sm">{{ t('articles.empty') }}</p>
    </div>

    <div v-else>
      <TransitionGroup name="list" tag="div" class="flex flex-col gap-4">
        <article
          v-for="(article, index) in articles"
          :key="article.id"
          class="group relative flex flex-col gap-5 rounded-2xl border border-slate-200 bg-white p-5 transition-colors duration-200 hover:border-slate-300 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:hover:border-slate-700 dark:hover:bg-slate-900/50 md:flex-row md:items-center"
          :style="{ '--delay': index }"
        >
          <div v-if="article.cover_image" class="h-44 w-full shrink-0 overflow-hidden rounded-xl border border-slate-100 dark:border-slate-800 md:h-32 md:w-48">
            <img
              :src="article.cover_image"
              class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              :alt="article.title"
            />
          </div>

          <div class="flex-1 min-w-0">
            <div class="mb-2.5 flex flex-wrap items-center gap-2">
              <span class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                <Folder class="h-3 w-3" aria-hidden="true" />
                {{ article.category_name || t('articles.untitledCategory') }}
              </span>
              <span v-if="article.is_top" class="rounded-md border border-brand-500/20 bg-brand-500/10 px-2 py-0.5 text-[11px] font-bold text-brand-600 dark:text-brand-400">
                {{ t('articles.top') }}
              </span>
            </div>

            <h2 class="mb-2 truncate text-lg font-bold text-slate-900 transition-colors group-hover:text-brand-500 dark:text-slate-100">
              <router-link :to="`/article/${article.slug}`" class="after:absolute after:inset-0">
                {{ article.title }}
              </router-link>
            </h2>

            <p class="mb-4 line-clamp-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
              {{ article.summary || t('articles.summaryFallback') }}
            </p>

            <div class="flex flex-wrap items-center gap-4 text-xs text-slate-400">
              <span class="flex items-center gap-1.5"><Calendar class="h-3.5 w-3.5" aria-hidden="true" /> {{ article.published_at || article.created_at }}</span>
              <span class="flex items-center gap-1.5"><Eye class="h-3.5 w-3.5" aria-hidden="true" /> {{ article.view_count }}</span>
              <div class="flex gap-2 border-l border-slate-200 pl-4 dark:border-slate-800">
                <span v-for="tag in article.tags" :key="tag.id">#{{ tag.name }}</span>
              </div>
            </div>
          </div>
        </article>
      </TransitionGroup>

      <nav v-if="totalPages > 1" class="mt-12 flex justify-center gap-2">
        <button
          class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 disabled:opacity-30 dark:border-slate-800 dark:hover:bg-slate-900"
          :disabled="page <= 1"
          @click="changePage(page - 1)"
        >
          <ChevronLeft class="h-4 w-4" aria-hidden="true" />
        </button>
        <button
          v-for="p in visiblePages"
          :key="p"
          class="h-9 min-w-[36px] rounded-xl border px-3 text-sm font-medium transition-colors"
          :class="p === page ? 'border-brand-500 bg-brand-500 text-white' : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-800 dark:text-slate-400 dark:hover:bg-slate-900'"
          @click="changePage(p)"
        >
          {{ p }}
        </button>
        <button
          class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 disabled:opacity-30 dark:border-slate-800 dark:hover:bg-slate-900"
          :disabled="page >= totalPages"
          @click="changePage(page + 1)"
        >
          <ChevronRight class="h-4 w-4" aria-hidden="true" />
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSiteStore, useUiStore } from '@/stores'
import { articleApi, type Article } from '@/services/api'
import {
  BookOpen, Calendar, Eye, Folder,
  Filter, ChevronDown, ChevronLeft, ChevronRight
} from '@lucide/vue'

const route = useRoute()
const siteStore = useSiteStore()
const uiStore = useUiStore()
const t = uiStore.t
const categories = computed(() => siteStore.categories)

const articles = ref<Article[]>([])
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)
const filters = ref({ category_id: 0, tag_id: 0, keyword: '' })

const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function loadArticles() {
  loading.value = true
  try {
    const params: Record<string, string | number> = { page: page.value }
    if (filters.value.category_id) params.category_id = filters.value.category_id
    if (filters.value.tag_id) params.tag_id = filters.value.tag_id
    if (filters.value.keyword) params.keyword = filters.value.keyword
    const res = await articleApi.getList(params)
    articles.value = res.data?.items || []
    totalPages.value = res.data?.pages || 1
  } catch (e) { console.warn(e) }
  loading.value = false
}

function queryStringValue(value: unknown): string {
  return Array.isArray(value) ? String(value[0] || '') : String(value || '')
}

function changePage(p: number) {
  page.value = p
  loadArticles()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(async () => {
  await siteStore.loadSiteInfo()
  if (route.query.category_id) filters.value.category_id = parseInt(queryStringValue(route.query.category_id), 10)
  if (route.query.tag_id) filters.value.tag_id = parseInt(queryStringValue(route.query.tag_id), 10)
  if (route.query.keyword) filters.value.keyword = queryStringValue(route.query.keyword)
  loadArticles()
})

watch(() => route.query, () => {
  filters.value.category_id = route.query.category_id ? parseInt(queryStringValue(route.query.category_id), 10) : 0
  filters.value.tag_id = route.query.tag_id ? parseInt(queryStringValue(route.query.tag_id), 10) : 0
  filters.value.keyword = route.query.keyword ? queryStringValue(route.query.keyword) : ''
  page.value = 1
  loadArticles()
})
</script>

<style scoped>
/* 列表阶梯入场动画 */
.list-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: calc(var(--delay) * 0.06s);
}
.list-enter-from {
  opacity: 0;
  transform: translateY(15px);
}
</style>