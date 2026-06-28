<template>
  <div class="min-h-screen bg-slate-50 transition-colors duration-300 pb-12 dark:bg-[#020617]">

    <HeroBanner
      :loading="loading"
      :slides="slides"
      :active-slide="activeSlide"
      :site-name="siteInfo.site_name || uiStore.t('common.siteDefaultName')"
      @change-slide="activeSlide = $event"
    />

    <main class="mx-auto max-w-7xl px-4 mt-8 sm:px-6 lg:px-8 lg:mt-12">
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-12 lg:gap-10 xl:gap-12">

        <div
          class="lg:col-span-8"
          v-motion
          :initial="{ opacity: 0, x: -20 }"
          :enter="{ opacity: 1, x: 0, transition: { delay: 100, duration: 400, ease: 'easeOut' } }"
        >
          <HomeArticles
            :articles="articles"
            :loading="loading"
            :title="uiStore.t('nav.articles')"
            :more-text="uiStore.t('common.explore')"
            :empty-text="uiStore.t('home.emptyArticles')"
            :summary-fallback="uiStore.t('articles.summaryFallback')"
            :format-date="formatDate"
          />
        </div>

        <div
          class="lg:col-span-4"
          v-motion
          :initial="{ opacity: 0, x: 20 }"
          :enter="{ opacity: 1, x: 0, transition: { delay: 200, duration: 400, ease: 'easeOut' } }"
        >
          <HomeWorks
            :works="works"
            :loading="loading"
            :title="uiStore.t('nav.portfolio')"
            :all-text="uiStore.t('common.explore')"
            :empty-text="uiStore.t('home.emptyWorks')"
            :empty-desc-text="uiStore.t('home.emptyWorkDesc')"
            :detail-text="uiStore.t('common.detail')"
          />
        </div>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSiteStore, useUiStore } from '@/stores'
import { articleApi, workApi } from '@/services/api'

// 首页专属组件统一放在当前页面目录，页面文件只负责数据编排和路由级展示。
import HeroBanner from '@/views/home/components/HeroBanner.vue'
import HomeArticles from '@/views/home/components/HomeArticles.vue'
import HomeWorks from '@/views/home/components/HomeWorks.vue'

type HeroSlide = {
  badge?: string
  title: string
  subtitle: string
  link?: string
  btnText: string
  image?: string
}

const siteStore = useSiteStore()
const uiStore = useUiStore()

const articles = ref<any[]>([])
const works = ref<any[]>([])
const loading = ref(true)
const activeSlide = ref(0)

const siteInfo = computed(() => siteStore.siteInfo || {})

// 轮播图幻灯片数据计算 (优先级：后台配置幻灯片 > 最新文章抽取 > 默认占位)
const slides = computed<HeroSlide[]>(() => {
  if (siteInfo.value.hero_slides && Array.isArray(siteInfo.value.hero_slides) && siteInfo.value.hero_slides.length > 0) {
    return siteInfo.value.hero_slides
  }

  if (articles.value.length > 0) {
    return articles.value.slice(0, 3).map(article => ({
      badge: article.category_name || uiStore.t('articleDetail.untitledCategory'),
      title: article.title,
      subtitle: article.summary || uiStore.t('articles.summaryFallback'),
      link: `/article/${article.slug}`,
      btnText: uiStore.t('common.detail'),
      image: article.cover_image
    }))
  }

  return [
    {
      badge: siteInfo.value.site_name || uiStore.t('common.siteDefaultName'),
      title: siteInfo.value.site_slogan || uiStore.t('home.defaultSlogan'),
      subtitle: siteInfo.value.site_description || uiStore.t('home.defaultDesc'),
      link: '/articles',
      btnText: uiStore.t('common.explore')
    }
  ]
})

/** 将后端时间字符串格式化成当前语言对应的短日期，避免首页卡片直接暴露原始时间。 */
function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  const normalized = dateStr.includes('T') ? dateStr : dateStr.replace(' ', 'T')
  const date = new Date(normalized)

  if (Number.isNaN(date.getTime())) return dateStr

  return new Intl.DateTimeFormat(uiStore.locale, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(date)
}

onMounted(async () => {
  try {
    // 聚合并发请求，大幅缩短首页弱网环境下的加载白屏时间
    const [artRes, workRes] = await Promise.all([
      articleApi.getList({ page: 1 }),
      workApi.getList({ page: 1 })
    ])

    articles.value = artRes.data?.items || []

    // 提取高赞作品排行前 3 项展示
    works.value = (workRes.data?.items || [])
      .sort((a: any, b: any) => b.like_count - a.like_count)
      .slice(0, 3)

  } catch (e) {
    console.warn('首页公共业务流水加载失败:', e)
  } finally {
    loading.value = false
  }
})
</script>