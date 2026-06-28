<template>
  <div class="w-full pb-8">
<header
      class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      v-motion
      :initial="{ opacity: 0, y: -20 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
          {{ t('admin.articles') || '文章管理' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          管理站点的所有博客文章与内容发布
        </p>
      </div>

      <button
        @click="router.push('/admin/articles/create')"
        class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-600 hover:shadow active:scale-95"
      >
        <Plus class="h-4 w-4" aria-hidden="true" />
        {{ t('adminAction.addArticle') || '新建文章' }}
      </button>
    </header>

    <form
      class="mb-6 grid grid-cols-1 gap-3 md:grid-cols-12"
      @submit.prevent="submitSearch"
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 50 } }"
    >
      <div class="relative md:col-span-5">
        <label class="sr-only" for="admin-article-keyword">{{ t('adminArticle.searchPlaceholder') || '搜索文章标题...' }}</label>
        <Search class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        <input
          id="admin-article-keyword"
          v-model.trim="keyword"
          type="search"
          class="h-10 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
          :placeholder="t('adminArticle.searchPlaceholder') || '搜索文章标题...'"
        />
      </div>

      <div class="relative md:col-span-4">
        <label class="sr-only" for="admin-article-status">{{ t('adminTable.status') || '状态筛选' }}</label>
        <Filter class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        <select
          id="admin-article-status"
          v-model="statusFilter"
          class="h-10 w-full appearance-none rounded-xl border border-slate-200 bg-white pl-10 pr-10 text-sm text-slate-700 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300"
          @change="submitSearch"
        >
          <option value="">{{ t('adminStatus.allStatus') || '全部状态' }}</option>
          <option value="published">{{ t('adminStatus.published') || '已发布' }}</option>
          <option value="draft">{{ t('adminStatus.draft') || '草稿' }}</option>
          <option value="archived">{{ t('adminStatus.archived') || '已归档' }}</option>
        </select>
        <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
      </div>

      <div class="flex gap-2 md:col-span-3">
        <button
          class="flex h-10 flex-1 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 text-sm font-medium text-white transition-colors hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200 active:scale-95"
          type="submit"
        >
          <Search class="h-4 w-4" aria-hidden="true" />
          <span class="hidden xl:inline-block">{{ t('common.search') || '搜索' }}</span>
        </button>
        <button
          class="flex h-10 flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 active:scale-95"
          type="button"
          @click="resetFilters"
        >
          <RefreshCcw class="h-4 w-4" aria-hidden="true" />
          <span class="hidden xl:inline-block">{{ t('common.all') || '重置' }}</span>
        </button>
      </div>
    </form>

    <div
      class="rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm dark:border-slate-800 dark:bg-slate-950"
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 100 } }"
    >
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-500"></div>
      </div>

      <div v-else class="overflow-x-auto custom-scrollbar">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="border-b border-slate-100 bg-slate-50/50 text-slate-500 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-400">
            <tr>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><PenTool class="h-4 w-4" /> {{ t('adminTable.title') || '标题' }}</div></th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><FolderTree class="h-4 w-4" /> {{ t('adminTable.category') || '分类' }}</div></th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Activity class="h-4 w-4" /> {{ t('adminTable.status') || '状态' }}</div></th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Eye class="h-4 w-4" /> {{ t('adminTable.views') || '浏览' }}</div></th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Calendar class="h-4 w-4" /> {{ t('adminTable.publishedAt') || '发布时间' }}</div></th>
              <th class="px-5 py-4 font-medium text-right">{{ t('adminTable.actions') || '操作' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <tr
              v-for="article in articles"
              :key="article.id"
              class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-900/40"
            >
              <td class="px-5 py-4">
                <div class="flex items-center gap-2">
                  <span class="font-semibold text-slate-900 dark:text-slate-100 truncate max-w-[200px] lg:max-w-[300px] xl:max-w-[400px]" :title="article.title">
                    {{ article.title }}
                  </span>
                  <span v-if="article.is_top" class="inline-flex shrink-0 items-center rounded-md border border-amber-200 bg-amber-50 px-1.5 py-0.5 text-[10px] font-bold text-amber-600 dark:border-amber-800/50 dark:bg-amber-900/20 dark:text-amber-400">
                    TOP
                  </span>
                </div>
              </td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400">
                <div class="flex items-center gap-1.5">
                  <Folder class="h-3.5 w-3.5 text-slate-400" />
                  {{ article.category_name || t('adminStatus.none') || '无' }}
                </div>
              </td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center rounded-md px-2 py-1 text-[11px] font-medium" :class="statusTheme(article.status)">
                  {{ statusText(article.status) }}
                </span>
              </td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400 font-medium">
                {{ article.view_count }}
              </td>
              <td class="px-5 py-4 text-xs text-slate-400 dark:text-slate-500">
                {{ article.published_at || t('adminStatus.none') || '无' }}
              </td>
              <td class="px-5 py-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-brand-50 hover:text-brand-600 dark:hover:bg-brand-900/20 dark:hover:text-brand-400"
                    :title="t('adminAction.edit') || '编辑'"
                    @click="editArticle(article.id)"
                  >
                    <Edit class="h-4 w-4" />
                  </button>
                  <button
                    class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400"
                    :title="t('adminAction.delete') || '删除'"
                    @click="deleteArticle(article.id)"
                  >
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="articles.length === 0">
              <td colspan="6" class="py-16 text-center text-sm text-slate-400">
                <div class="flex flex-col items-center justify-center">
                  <FileText class="mb-3 h-12 w-12 opacity-20" />
                  {{ t('adminEmpty.articles') || '暂无符合条件的文章数据' }}
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="totalPages > 1 && !loading" class="mt-8 flex justify-center gap-2">
      <button
        class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 disabled:opacity-30 dark:border-slate-800 dark:hover:bg-slate-900"
        :disabled="page <= 1"
        @click="changePage(page - 1)"
      >
        <ChevronLeft class="h-4 w-4" />
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
        <ChevronRight class="h-4 w-4" />
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { articleApi, type Article } from '@/services/api'
import { useUiStore } from '@/stores'

// 引入高颜值 Lucide 图标
import {
  Plus, Search, Filter, ChevronDown, ChevronLeft, ChevronRight,
  Eye, Calendar, Folder, Edit, Trash2, FileText, PenTool, FolderTree, Activity, RefreshCcw
} from '@lucide/vue'

const router = useRouter()
const uiStore = useUiStore()
const t = uiStore.t
const articles = ref<Article[]>([])
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)
const keyword = ref('')
const statusFilter = ref('')

const visiblePages = computed(() => {
  const pages: number[] = []
  const start = Math.max(1, page.value - 2)
  const end = Math.min(totalPages.value, page.value + 2)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

function statusTheme(s: Article['status']): string {
  switch (s) {
    case 'published':
      return 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400'
    case 'draft':
      return 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
    case 'archived':
      return 'bg-indigo-50 text-indigo-500 dark:bg-indigo-900/20 dark:text-indigo-400'
    default:
      return 'bg-slate-100 text-slate-500'
  }
}

function statusText(s: Article['status']): string {
  return {
    published: t('adminStatus.published') || '已发布',
    draft: t('adminStatus.draft') || '草稿',
    archived: t('adminStatus.archived') || '已归档'
  }[s] || s
}

async function loadArticles() {
  loading.value = true
  try {
    const params: Record<string, string | number> = { page: page.value }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value) params.status = statusFilter.value
    const res = await articleApi.adminGetList(params)
    articles.value = res.data?.items || []
    totalPages.value = res.data?.pages || 1
  } catch (e) {
    console.warn(e)
  }
  loading.value = false
}

function submitSearch() {
  page.value = 1
  loadArticles()
}

function resetFilters() {
  keyword.value = ''
  statusFilter.value = ''
  page.value = 1
  loadArticles()
}

function editArticle(id: number) {
  router.push(`/admin/articles/edit/${id}`)
}

async function deleteArticle(id: number) {
  if (!confirm(t('adminArticle.deleteConfirm') || '确认要删除这篇文章吗？')) return
  try {
    await articleApi.delete(id)
    if (articles.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    loadArticles()
  } catch (e: any) {
    alert(e.message)
  }
}

function changePage(p: number) {
  page.value = p
  loadArticles()
}

onMounted(loadArticles)
</script>

<style scoped>
/* 自定义优美滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-200);
  border-radius: 20px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-700);
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-300);
}
.dark .custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-600);
}
</style>