<template>
  <div class="mx-auto w-full max-w-7xl px-4 py-8 sm:py-10">
    <header class="mb-10 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div class="max-w-2xl">
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
          {{ t('globalSearch.title') }}
        </h1>
        <p class="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
          {{ t('globalSearch.subtitle') }}
        </p>
      </div>
      <div class="inline-flex h-9 items-center rounded-full bg-slate-100 px-4 text-sm font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
        {{ keyword ? t('globalSearch.currentKeyword', { keyword }) : t('globalSearch.useHeaderSearch') }}
      </div>
    </header>

    <section class="grid gap-6 xl:grid-cols-[1.2fr_0.9fr_0.9fr]">

      <SearchResultColumn
        :title="t('globalSearch.articles')"
        :count="articleResults.length"
        :loading="loading"
        :empty-text="t('globalSearch.emptyArticles')"
      >
        <router-link
          v-for="item in articleResults"
          :key="`article-${item.id}`"
          :to="`/article/${item.slug}`"
          class="group block rounded-xl border border-slate-200 bg-white p-4 transition-colors duration-200 hover:border-slate-300 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:hover:border-slate-700 dark:hover:bg-slate-900/50"
        >
          <div class="text-sm font-medium text-slate-900 transition-colors group-hover:text-cyan-600 dark:text-slate-100 dark:group-hover:text-cyan-500">
            {{ item.title }}
          </div>
          <div class="mt-1.5 line-clamp-2 text-xs leading-5 text-slate-500 dark:text-slate-400">
            {{ item.summary || t('articles.summaryFallback') }}
          </div>
        </router-link>
      </SearchResultColumn>

      <SearchResultColumn
        :title="t('globalSearch.works')"
        :count="workResults.length"
        :loading="loading"
        :empty-text="t('globalSearch.emptyWorks')"
      >
        <router-link
          v-for="item in workResults"
          :key="`work-${item.id}`"
          :to="`/portfolio/${item.id}`"
          class="group block rounded-xl border border-slate-200 bg-white p-4 transition-colors duration-200 hover:border-slate-300 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:hover:border-slate-700 dark:hover:bg-slate-900/50"
        >
          <div class="text-sm font-medium text-slate-900 transition-colors group-hover:text-cyan-600 dark:text-slate-100 dark:group-hover:text-cyan-500">
            {{ item.title }}
          </div>
          <div class="mt-1.5 line-clamp-2 text-xs leading-5 text-slate-500 dark:text-slate-400">
            {{ item.description || t('portfolio.descFallback') }}
          </div>
          <div class="mt-3 flex flex-wrap gap-1.5">
            <span v-for="tech in item.tech_stack.slice(0, 4)" :key="tech" class="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {{ tech }}
            </span>
          </div>
        </router-link>
      </SearchResultColumn>

      <SearchResultColumn
        :title="t('globalSearch.resources')"
        :count="resourceResults.length"
        :loading="loading"
        :empty-text="t('globalSearch.emptyResources')"
      >
        <div
          v-for="item in resourceResults"
          :key="`resource-${item.id}`"
          class="group rounded-xl border border-slate-200 bg-white p-4 transition-colors duration-200 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-950 dark:hover:border-slate-700"
        >
          <div class="text-sm font-medium text-slate-900 dark:text-slate-100">
            {{ item.title }}
          </div>
          <div class="mt-1.5 line-clamp-2 text-xs leading-5 text-slate-500 dark:text-slate-400">
            {{ item.description || t('resources.descFallback') }}
          </div>
          <div class="mt-4 flex items-center justify-between gap-3 border-t border-slate-100 pt-3 dark:border-slate-800">
            <div class="min-w-0 flex-1 text-[11px] text-slate-400">
              <span class="block truncate">{{ item.file_name }}</span>
            </div>
            <a
              :href="resourceApi.download(item.id)"
              class="inline-flex h-7 items-center justify-center rounded-lg bg-slate-100 px-3 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            >
              {{ t('resources.download') }}
            </a>
          </div>
        </div>
      </SearchResultColumn>

    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { articleApi, resourceApi, workApi, type Article, type Resource, type Work } from '@/services/api'
import { useUiStore } from '@/stores'
import SearchResultColumn from '@/views/search/components/SearchResultColumn.vue'

const route = useRoute()
const uiStore = useUiStore()
const t = uiStore.t

const keyword = ref('')
const articleResults = ref<Article[]>([])
const resourceResults = ref<Resource[]>([])
const workResults = ref<Work[]>([])
const loading = ref(true)

function queryStringValue(value: unknown): string {
  return Array.isArray(value) ? String(value[0] || '') : String(value || '')
}

async function loadResults() {
  loading.value = true
  try {
    const value = keyword.value.trim()
    if (!value) {
      articleResults.value = []
      resourceResults.value = []
      workResults.value = []
      return
    }
    const [articleRes, resourceRes, workRes] = await Promise.all([
      articleApi.search(value, 8),
      resourceApi.search(value, 8),
      workApi.search(value, 8)
    ])
    articleResults.value = articleRes.data?.items || []
    resourceResults.value = resourceRes.data?.items || []
    workResults.value = workRes.data?.items || []
  } catch (error) {
    console.warn('搜索结果加载失败:', error)
    articleResults.value = []
    resourceResults.value = []
    workResults.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  keyword.value = route.query.keyword ? queryStringValue(route.query.keyword) : ''
  void loadResults()
})

watch(() => route.query.keyword, value => {
  keyword.value = value ? queryStringValue(value) : ''
  void loadResults()
})
</script>