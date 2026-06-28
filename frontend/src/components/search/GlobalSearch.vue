<template>
  <div ref="rootRef" class="relative w-full max-w-[32rem]">
    <form role="search" class="relative group flex items-center" @submit.prevent="submitSearch">
      <label class="sr-only" :for="props.inputId">{{ t('globalSearch.label') }}</label>

      <Search class="pointer-events-none absolute left-3.5 h-[18px] w-[18px] text-[var(--cms-text-muted)]/50 transition-colors group-focus-within:text-[var(--cms-text-muted)]" aria-hidden="true" />

      <input
        :id="props.inputId"
        v-model.trim="keyword"
        type="search"
        autocomplete="off"
        class="h-10 w-full rounded-full border border-[var(--cms-border)] bg-[var(--cms-surface)] pl-10 pr-[88px] text-sm text-[var(--cms-text)] outline-none transition-colors duration-200 hover:border-[var(--cms-border)]/80 focus:border-brand-500 placeholder-[var(--cms-text-muted)]/50 [&::-webkit-search-cancel-button]:appearance-none"
        :placeholder="t('globalSearch.placeholder')"
        @focus="isFocused = true"
        @keydown.esc="closePanel"
      />

      <button
        v-if="keyword"
        type="button"
        class="absolute right-[4.5rem] flex h-5 w-5 items-center justify-center rounded-full bg-transparent text-[var(--cms-text-muted)] opacity-60 transition-colors hover:bg-[var(--cms-surface-muted)] hover:opacity-100"
        :aria-label="t('globalSearch.clear')"
        @click="clearSearch"
      >
        <X class="h-3.5 w-3.5" aria-hidden="true" />
      </button>

      <button
        type="submit"
        class="absolute right-1 flex h-8 items-center justify-center rounded-full bg-[var(--cms-surface-muted)] px-4 text-sm font-medium text-[var(--cms-text-muted)] transition-colors hover:bg-[var(--cms-border)] hover:text-[var(--cms-text)] disabled:pointer-events-none disabled:opacity-50"
        :disabled="normalizedKeyword.length === 0"
      >
        <span>{{ t('common.search') }}</span>
      </button>
    </form>

    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="showPanel"
        class="absolute left-0 right-0 top-full z-50 mt-2 overflow-hidden rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)] shadow-lg"
      >
        <div v-if="searching" class="flex items-center gap-2.5 px-4 py-5 text-sm text-[var(--cms-text-muted)]">
          <LoaderCircle class="h-4.5 w-4.5 animate-spin text-[var(--cms-text-muted)]" aria-hidden="true" />
          <span>{{ t('globalSearch.searching') }}</span>
        </div>

        <div v-else-if="isEmptyResult" class="flex flex-col items-center justify-center px-4 py-8 text-sm text-[var(--cms-text-muted)]">
          <Archive class="h-8 w-8 mb-2 opacity-20" />
          <span>{{ t('globalSearch.empty') }}</span>
        </div>

        <div v-else class="max-h-[60vh] overflow-y-auto overscroll-contain custom-scrollbar">
          <SearchGroup
            v-if="articleResults.length"
            :title="t('globalSearch.articles')"
            :count="articleResults.length"
            icon="article"
          >
            <router-link
              v-for="item in articleResults"
              :key="`article-${item.id}`"
              :to="`/article/${item.slug}`"
              class="group flex items-start gap-3 px-4 py-3 transition-colors hover:bg-[var(--cms-surface-muted)]"
              @click="closePanel"
            >
              <div class="min-w-0 flex-1">
                <div class="truncate text-sm font-medium text-[var(--cms-text)] transition-colors group-hover:text-brand-500">
                  {{ item.title }}
                </div>
                <div class="mt-0.5 line-clamp-1 text-xs text-[var(--cms-text-muted)]/80">
                  {{ item.summary || t('articles.summaryFallback') }}
                </div>
              </div>
            </router-link>
          </SearchGroup>

          <SearchGroup
            v-if="workResults.length"
            :title="t('globalSearch.works')"
            :count="workResults.length"
            icon="work"
          >
            <router-link
              v-for="item in workResults"
              :key="`work-${item.id}`"
              :to="`/portfolio/${item.id}`"
              class="group flex items-start gap-3 px-4 py-3 transition-colors hover:bg-[var(--cms-surface-muted)]"
              @click="closePanel"
            >
              <div class="min-w-0 flex-1">
                <div class="truncate text-sm font-medium text-[var(--cms-text)] transition-colors group-hover:text-brand-500">
                  {{ item.title }}
                </div>
                <div class="mt-0.5 line-clamp-1 text-xs text-[var(--cms-text-muted)]/80">
                  {{ item.description || t('portfolio.descFallback') }}
                </div>
              </div>
            </router-link>
          </SearchGroup>

          <SearchGroup
            v-if="resourceResults.length"
            :title="t('globalSearch.resources')"
            :count="resourceResults.length"
            icon="resource"
          >
            <router-link
              v-for="item in resourceResults"
              :key="`resource-${item.id}`"
              :to="{ path: '/resources', query: { keyword: normalizedKeyword } }"
              class="group flex items-start gap-3 px-4 py-3 transition-colors hover:bg-[var(--cms-surface-muted)]"
              @click="closePanel"
            >
              <div class="min-w-0 flex-1">
                <div class="truncate text-sm font-medium text-[var(--cms-text)] transition-colors group-hover:text-brand-500">
                  {{ item.title }}
                </div>
                <div class="mt-0.5 line-clamp-1 text-xs text-[var(--cms-text-muted)]/80">
                  {{ item.description || t('resources.descFallback') }}
                </div>
              </div>
            </router-link>
          </SearchGroup>

          <div class="p-2 border-t border-[var(--cms-border)] bg-[var(--cms-surface)]">
            <button
              type="button"
              class="flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium text-brand-500 transition-colors hover:bg-brand-500/5"
              @click="submitSearch"
            >
              <span>{{ t('globalSearch.viewAll', { keyword: normalizedKeyword }) }}</span>
              <ArrowUpRight class="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowUpRight, Archive, FileText, LoaderCircle, Search, Sparkles, X } from '@lucide/vue'
import { articleApi, resourceApi, workApi, type Article, type Resource, type Work } from '@/services/api'
import { useUiStore } from '@/stores'

const props = withDefaults(defineProps<{ inputId?: string }>(), {
  inputId: 'global-search'
})

// 分组标题组件也进行了视觉降噪处理
const SearchGroup = defineComponent({
  name: 'SearchGroup',
  props: {
    title: { type: String, required: true },
    count: { type: Number, required: true },
    icon: { type: String, required: true }
  },
  setup(groupProps, { slots }) {
    const iconMap = {
      article: FileText,
      work: Sparkles,
      resource: Archive
    } as const

    return () => {
      const Icon = iconMap[groupProps.icon as keyof typeof iconMap] || FileText
      return h('section', { class: 'border-b border-[var(--cms-border)] last:border-0' }, [
        h('div', { class: 'flex items-center justify-between px-4 py-2.5 bg-[var(--cms-surface)]' }, [
          h('div', { class: 'flex items-center gap-2 text-xs font-medium text-[var(--cms-text-muted)]' }, [
            h(Icon, { class: 'h-3.5 w-3.5', 'aria-hidden': 'true' }),
            h('span', groupProps.title)
          ]),
          h('span', { class: 'text-xs text-[var(--cms-text-muted)]/60' }, String(groupProps.count))
        ]),
        slots.default?.()
      ])
    }
  }
})

const router = useRouter()
const uiStore = useUiStore()
const t = uiStore.t

const keyword = ref('')
const articleResults = ref<Article[]>([])
const resourceResults = ref<Resource[]>([])
const workResults = ref<Work[]>([])
const searching = ref(false)
const isFocused = ref(false)
let searchTimer: number | undefined
let requestSeq = 0
const rootRef = ref<HTMLElement | null>(null)

const normalizedKeyword = computed(() => keyword.value.trim())
const showPanel = computed(() => isFocused.value && normalizedKeyword.value.length > 0)
const isEmptyResult = computed(() => !searching.value && articleResults.value.length === 0 && resourceResults.value.length === 0 && workResults.value.length === 0)

watch(normalizedKeyword, value => {
  if (searchTimer) window.clearTimeout(searchTimer)
  if (!value) {
    articleResults.value = []
    resourceResults.value = []
    workResults.value = []
    searching.value = false
    return
  }
  searching.value = true
  searchTimer = window.setTimeout(() => {
    void runSearch(value)
  }, 300)
})

async function runSearch(value: string): Promise<void> {
  const seq = ++requestSeq
  try {
    const [articleRes, resourceRes, workRes] = await Promise.all([
      articleApi.search(value, 4),
      resourceApi.search(value, 4),
      workApi.search(value, 4)
    ])
    if (seq !== requestSeq) return
    articleResults.value = articleRes.data?.items || []
    resourceResults.value = resourceRes.data?.items || []
    workResults.value = workRes.data?.items || []
  } catch (error) {
    if (seq !== requestSeq) return
    console.warn('统一搜索失败:', error)
    articleResults.value = []
    resourceResults.value = []
    workResults.value = []
  } finally {
    if (seq === requestSeq) {
      searching.value = false
    }
  }
}

function submitSearch(): void {
  const value = normalizedKeyword.value
  if (!value) return
  isFocused.value = false
  router.push({ path: '/search', query: { keyword: value } })
}

function clearSearch(): void {
  keyword.value = ''
  articleResults.value = []
  resourceResults.value = []
  workResults.value = []
  document.getElementById(props.inputId)?.focus()
}

function closePanel(): void {
  isFocused.value = false
}

function handleDocumentClick(event: MouseEvent): void {
  if (!rootRef.value) return
  if (!rootRef.value.contains(event.target as Node)) {
    closePanel()
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick, true)
  if (searchTimer) window.clearTimeout(searchTimer)
})
</script>

<style scoped>
/* 为了确保其他浏览器不出现原生清除按钮，在样式里再兜个底 */
input[type="search"]::-webkit-search-decoration,
input[type="search"]::-webkit-search-cancel-button,
input[type="search"]::-webkit-search-results-button,
input[type="search"]::-webkit-search-results-decoration {
  -webkit-appearance: none;
  appearance: none;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: var(--cms-border);
  border-radius: 10px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background: var(--cms-text-muted);
}
</style>