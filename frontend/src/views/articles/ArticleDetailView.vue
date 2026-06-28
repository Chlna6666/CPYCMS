<template>
  <div class="mx-auto w-full max-w-4xl px-4 py-8 sm:py-12">
    <div v-if="loading" class="flex flex-col items-center py-24">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-500"></div>
    </div>

    <div v-else-if="!article" class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 py-24 text-center dark:border-slate-800">
      <CircleOff class="mb-4 h-12 w-12 text-slate-300 dark:text-slate-700" aria-hidden="true" />
      <p class="mb-6 text-sm text-slate-500">{{ t('articleDetail.notFound') }}</p>
      <router-link to="/articles" class="inline-flex h-9 items-center rounded-xl bg-slate-100 px-5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300">
        {{ t('articleDetail.backToList') }}
      </router-link>
    </div>

    <Transition name="fade" appear>
      <div v-if="article">
        <article>
          <header class="mb-10 text-center">
            <div class="mb-4 flex items-center justify-center gap-2">
              <span class="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                {{ article.category_name || t('articleDetail.untitledCategory') }}
              </span>
            </div>

            <h1 class="mb-6 text-3xl font-bold leading-tight text-slate-900 dark:text-slate-50 sm:text-4xl">
              {{ article.title }}
            </h1>

            <div class="flex flex-wrap items-center justify-center gap-5 text-xs text-slate-500 dark:text-slate-400">
              <span class="flex items-center gap-1.5"><Calendar class="h-3.5 w-3.5" aria-hidden="true" /> {{ article.published_at || article.created_at }}</span>
              <span class="flex items-center gap-1.5"><Eye class="h-3.5 w-3.5" aria-hidden="true" /> {{ article.view_count }}</span>
              <span class="flex items-center gap-1.5"><Heart class="h-3.5 w-3.5" aria-hidden="true" /> {{ article.like_count }} {{ t('articleDetail.likesSuffix') }}</span>
              <span v-if="article.updated_at" class="flex items-center gap-1.5"><Clock class="h-3.5 w-3.5" aria-hidden="true" /> {{ article.updated_at }}</span>
            </div>
          </header>

          <div v-if="article.cover_image" class="mb-12 overflow-hidden rounded-2xl border border-slate-100 dark:border-slate-800">
            <img :src="article.cover_image" class="w-full object-cover" :alt="article.title" />
          </div>

          <div class="prose prose-slate prose-lg max-w-none dark:prose-invert">
            <MarkdownRenderer :content="article.content" />
          </div>

          <div class="mt-12 flex flex-col items-center gap-3 border-t border-slate-200 pt-8 dark:border-slate-800">
            <button
              type="button"
              class="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-rose-500 px-5 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:cursor-not-allowed disabled:opacity-70"
              :disabled="articleLiked || articleLiking"
              @click="handleArticleLike"
            >
              <Heart class="h-4 w-4" :class="articleLiked ? 'fill-current' : ''" aria-hidden="true" />
              {{ articleLiked ? t('articleDetail.liked') : t('articleDetail.likeButton') }}
            </button>
            <p class="text-xs text-slate-500 dark:text-slate-400">
              {{ article.like_count }} {{ t('articleDetail.peopleLiked') }}
            </p>
          </div>

          <footer class="mt-16 border-t border-slate-200 pt-8 dark:border-slate-800">
            <div class="flex flex-wrap items-center gap-2">
              <Tag class="mr-2 h-4 w-4 text-slate-400" aria-hidden="true" />
              <router-link
                v-for="tag in article.tags"
                :key="tag.id"
                :to="`/articles?tag_id=${tag.id}`"
                class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600 transition-colors hover:border-brand-500 hover:text-brand-500 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-400"
              >
                # {{ tag.name }}
              </router-link>
            </div>
          </footer>
        </article>

        <section id="comments-section" class="mt-12">
          <ArticleComments :slug="article.slug" />
        </section>

        <div class="mt-12 flex justify-center">
          <router-link to="/articles" class="group flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400 dark:hover:bg-slate-900">
            <ArrowLeft class="h-4 w-4 transition-transform group-hover:-translate-x-1" aria-hidden="true" />
            {{ t('articleDetail.backToList') }}
          </router-link>
        </div>
      </div>
    </Transition>

    <Transition name="fade-slide">
      <div v-show="showFloatingActions" class="fixed bottom-6 right-4 z-50 flex flex-col gap-2 lg:bottom-10 lg:right-10">
        <button
          @click="scrollToComments"
          class="group flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white/90 text-slate-500 backdrop-blur-md transition-colors hover:border-brand-500 hover:text-brand-500 dark:border-slate-700 dark:bg-slate-900/90 dark:text-slate-400"
          :title="t('articleComments.title')"
        >
          <MessageSquareText class="h-4.5 w-4.5" aria-hidden="true" />
        </button>

        <button
          @click="scrollToTop"
          class="group flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white/90 text-slate-500 backdrop-blur-md transition-colors hover:border-brand-500 hover:text-brand-500 dark:border-slate-700 dark:bg-slate-900/90 dark:text-slate-400"
          :title="t('common.backToTop') || '回到顶部'"
        >
          <ArrowUpToLine class="h-4.5 w-4.5" aria-hidden="true" />
        </button>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUiStore } from '@/stores'
import { articleApi, type Article } from '@/services/api'
import { buildClientFingerprint } from '@/utils/clientFingerprint'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import ArticleComments from '@/views/articles/components/ArticleComments.vue'
import {
  Calendar, CircleOff, Eye, Clock, Tag, ArrowLeft,
  ArrowUpToLine, MessageSquareText, Heart
} from '@lucide/vue'

const route = useRoute()
const uiStore = useUiStore()
const t = uiStore.t
const article = ref<Article | null>(null)
const loading = ref(true)
const articleLiked = ref(false)
const articleLiking = ref(false)

// 控制悬浮按钮显示隐藏
const showFloatingActions = ref(false)

function handleScroll() {
  // 滚动超过 300px 显示按钮
  showFloatingActions.value = window.scrollY > 300
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function scrollToComments() {
  const el = document.getElementById('comments-section')
  if (el) {
    // 预留 80px 偏移量，避免被顶部吸顶导航栏遮挡
    const y = el.getBoundingClientRect().top + window.scrollY - 80
    window.scrollTo({ top: y, behavior: 'smooth' })
  }
}

async function handleArticleLike() {
  if (!article.value || articleLiked.value || articleLiking.value) return
  articleLiking.value = true
  try {
    const fingerprint = await buildClientFingerprint()
    const res = await articleApi.like(article.value.slug, { client_fingerprint: fingerprint })
    article.value.like_count = res.like_count
    articleLiked.value = true
  } catch (e: any) {
    articleLiked.value = true
    alert(e?.message || t('common.networkError'))
  } finally {
    articleLiking.value = false
  }
}

onMounted(async () => {
  // 监听滚动事件
  window.addEventListener('scroll', handleScroll, { passive: true })

  try {
    const slug = Array.isArray(route.params.slug) ? route.params.slug[0] : route.params.slug
    const res = await articleApi.getDetail(String(slug || ''))
    article.value = res.data || null
  } catch (e) { console.warn(e) }
  loading.value = false
})

onUnmounted(() => {
  // 移除事件监听，防止内存泄漏
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

/* 侧边悬浮按钮划入动画 */
.fade-slide-enter-active, .fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.fade-slide-enter-from, .fade-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

/* 适配 Markdown 渲染后的媒体与代码块，统一切角与边框 */
:deep(.prose img) {
  border-radius: 0.75rem;
  border: 1px solid var(--cms-border);
}
:deep(.prose pre) {
  border-radius: 0.75rem;
  border: 1px solid var(--cms-border);
}
</style>
