<template>
  <div class="w-full pb-8">
    <header class="mb-8">
      <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
        {{ t('admin.dashboard') }}
      </h1>
      <p class="mt-1 text-sm text-slate-500">{{ t('adminDashboard.subtitle') || '实时掌握站点的核心运营数据与趋势' }}</p>
    </header>

    <section class="mb-10 grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-5">
      <div
        v-for="(item, index) in statConfig"
        :key="index"
        class="group flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-4 transition-colors hover:border-brand-500/50 dark:border-slate-800 dark:bg-slate-950"
      >
        <div :class="[item.colorClass, 'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl transition-transform group-hover:scale-110']">
          <component :is="item.icon" class="h-5 w-5" />
        </div>
        <div class="min-w-0 flex-1">
          <div class="text-xs font-medium text-slate-500 dark:text-slate-400">{{ item.label }}</div>
          <div class="mt-0.5 truncate text-xl font-bold text-slate-900 dark:text-slate-50">
            {{ item.value }}
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 lg:grid-cols-12">
      <div class="lg:col-span-8">
        <div class="h-full rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-950">
          <div class="mb-2 flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-slate-100">
              <TrendingUp class="h-4 w-4 text-brand-500" />
              {{ t('adminDashboard.sevenDayTrend') || '近7天文章发布趋势' }}
            </h3>
          </div>
          <div ref="chartContainer" style="width: 100%; height: 260px;"></div>
        </div>
      </div>

      <div class="lg:col-span-4">
        <div class="h-full rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-950">
          <h3 class="mb-6 flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-slate-100">
            <PieChart class="h-4 w-4 text-indigo-500" />
            {{ t('adminDashboard.categoryDistribution') || '分类文章分布' }}
          </h3>

          <div class="space-y-5">
            <div v-for="cat in stats.category_distribution" :key="cat.name">
              <div class="mb-2 flex justify-between text-xs font-medium">
                <span class="text-slate-700 dark:text-slate-300">{{ cat.name }}</span>
                <span class="text-slate-500">{{ cat.count }}</span>
              </div>
              <div class="h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-800">
                <div
                  class="h-full rounded-full bg-indigo-500 transition-all duration-1000"
                  :style="{ width: (cat.count / maxCatCount * 100) + '%' }"
                ></div>
              </div>
            </div>
            <div v-if="!stats.category_distribution?.length" class="py-10 text-center text-sm text-slate-400">
              {{ t('adminEmpty.data') || '暂无数据' }}
            </div>
          </div>
        </div>
      </div>

      <div class="lg:col-span-6">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-950">
          <h3 class="mb-5 flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-slate-100">
            <Trophy class="h-4 w-4 text-brand-500" />
            {{ t('adminDashboard.topArticles') || '热门文章 TOP5' }}
          </h3>

          <div class="divide-y divide-slate-100 dark:divide-slate-800">
            <div
              v-for="(article, idx) in stats.top_articles"
              :key="idx"
              class="flex items-center justify-between py-3"
            >
              <div class="flex min-w-0 items-center gap-3">
                <span
                  class="flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-[10px] font-bold"
                  :class="idx < 3 ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/30 dark:text-brand-500' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
                >
                  {{ idx + 1 }}
                </span>
                <span class="truncate text-sm text-slate-700 dark:text-slate-300">{{ article.title }}</span>
              </div>
              <span class="ml-4 shrink-0 text-xs font-medium text-slate-400">
                {{ article.views }} <span class="hidden sm:inline">{{ t('adminDashboard.viewsSuffix') || '次' }}</span>
              </span>
            </div>
          </div>
          <div v-if="!stats.top_articles?.length" class="py-10 text-center text-sm text-slate-400">
            {{ t('adminEmpty.data') || '暂无数据' }}
          </div>
        </div>
      </div>

      <div class="lg:col-span-6">
        <div class="h-full rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-950">
          <h3 class="mb-5 flex items-center gap-2 text-sm font-bold text-slate-900 dark:text-slate-100">
            <Zap class="h-4 w-4 text-brand-500" />
            {{ t('adminDashboard.quickActions') || '快捷操作' }}
          </h3>

          <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
            <router-link
              v-for="action in quickActions"
              :key="action.path"
              :to="action.path"
              class="flex flex-col items-center justify-center gap-2 rounded-xl border border-slate-100 bg-slate-50/50 py-4 transition-all hover:border-brand-500/30 hover:bg-white hover:text-brand-600 dark:border-slate-800 dark:bg-slate-900/50 dark:hover:border-brand-500/50 dark:hover:text-brand-400"
            >
              <component :is="action.icon" class="h-5 w-5" />
              <span class="text-xs font-medium">{{ t(action.langKey) || action.fallbackName }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, shallowRef, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { ECharts, EChartsOption } from 'echarts'
import { statsApi, type StatsData } from '@/services/api'
import { useUiStore } from '@/stores'
import {
  FileText, CheckCircle, Briefcase, Eye, Package,
  Heart, Download, MessageSquare, MessagesSquare,
  TrendingUp, PieChart, Trophy, Zap,
  PenLine, LayoutGrid, Bell, MessageCircle, Upload, Settings
} from '@lucide/vue'

const uiStore = useUiStore()
const t = uiStore.t

echarts.use([BarChart, GridComponent, TooltipComponent, CanvasRenderer])

const chartContainer = ref<HTMLElement | null>(null)
const chartInstance = shallowRef<ECharts | null>(null)

const stats = ref<StatsData>({
  article_count: 0, published_count: 0, draft_count: 0,
  work_count: 0, resource_count: 0, message_count: 0,
  pending_messages: 0, comment_count: 0, pending_comments: 0,
  category_count: 0, total_views: 0, total_likes: 0, total_downloads: 0,
  daily_articles: [], category_distribution: [], top_articles: []
})

// 【重构】彻底移除所有红色(rose)、橙色(orange)、黄色(amber)，全替换为科技感冷色调
const statConfig = computed(() => [
  { label: t('adminDashboard.articlesTotal') || '文章总数', value: stats.value.article_count, icon: FileText, colorClass: 'bg-brand-50 text-brand-600 dark:bg-brand-900/20 dark:text-brand-400' },
  { label: t('adminDashboard.published') || '已发布', value: stats.value.published_count, icon: CheckCircle, colorClass: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' },
  { label: t('adminDashboard.worksTotal') || '作品数', value: stats.value.work_count, icon: Briefcase, colorClass: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/20 dark:text-indigo-400' },
  { label: t('adminDashboard.totalViews') || '总浏览', value: stats.value.total_views, icon: Eye, colorClass: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400' },
  { label: t('adminDashboard.resourcesTotal') || '资源数', value: stats.value.resource_count, icon: Package, colorClass: 'bg-cyan-50 text-cyan-600 dark:bg-cyan-900/20 dark:text-cyan-400' },
  { label: t('adminDashboard.totalLikes') || '总点赞', value: stats.value.total_likes, icon: Heart, colorClass: 'bg-sky-50 text-sky-600 dark:bg-sky-900/20 dark:text-sky-400' },
  { label: t('adminDashboard.totalDownloads') || '总下载', value: stats.value.total_downloads, icon: Download, colorClass: 'bg-teal-50 text-teal-600 dark:bg-teal-900/20 dark:text-teal-400' },
  // 待处理采用品牌蓝色高亮，无待处理则为冷灰色
  { label: t('adminDashboard.pendingMessages') || '待审留言', value: stats.value.pending_messages, icon: MessageSquare, colorClass: stats.value.pending_messages > 0 ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/20 dark:text-brand-400' : 'bg-slate-50 text-slate-400 dark:bg-slate-800' },
  { label: t('adminDashboard.pendingComments') || '待审评论', value: stats.value.pending_comments, icon: MessagesSquare, colorClass: stats.value.pending_comments > 0 ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/20 dark:text-brand-400' : 'bg-slate-50 text-slate-400 dark:bg-slate-800' },
  { label: t('adminDashboard.categories') || '分类数', value: stats.value.category_count, icon: LayoutGrid, colorClass: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400' }
])

const quickActions = [
  { langKey: 'adminDashboard.writeArticle', fallbackName: '写新文章', path: '/admin/articles/create', icon: PenLine },
  { langKey: 'adminDashboard.manageWorks', fallbackName: '管理作品', path: '/admin/works', icon: Briefcase },
  { langKey: 'adminDashboard.reviewMessages', fallbackName: '审核留言', path: '/admin/messages', icon: Bell },
  { langKey: 'admin.comments', fallbackName: '文章评论', path: '/admin/comments', icon: MessageCircle },
  { langKey: 'adminDashboard.uploadResource', fallbackName: '上传资源', path: '/admin/resources', icon: Upload },
  { langKey: 'admin.settings', fallbackName: '站点设置', path: '/admin/settings', icon: Settings }
]

const maxCatCount = computed(() => Math.max(1, ...stats.value.category_distribution.map(c => c.count)))

const formatDate = (dateStr: string) => dateStr.split('-').slice(1).join('/')

// 初始化 ECharts 并修正宽度挤压问题
const initChart = () => {
  if (!chartContainer.value) return

  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartContainer.value)
  }

  const isDark = uiStore.theme === 'dark'
  const textColor = isDark ? '#94a3b8' : '#64748b'
  const splitLineColor = isDark ? '#1e293b' : '#f1f5f9'
  const tooltipBg = isDark ? '#0f172a' : '#ffffff'
  const tooltipBorder = isDark ? '#1e293b' : '#e2e8f0'
  const tooltipText = isDark ? '#f8fafc' : '#0f172a'

  const dates = stats.value.daily_articles.map(d => formatDate(d.date))
  const counts = stats.value.daily_articles.map(d => d.count)

  const option: EChartsOption = {
    grid: {
      top: 30,
      right: 10, // 稍微留白防止挤压
      bottom: 0,
      left: 10,
      containLabel: true
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'none' },
      backgroundColor: tooltipBg,
      borderColor: tooltipBorder,
      padding: [8, 12],
      textStyle: { color: tooltipText, fontSize: 13 },
      extraCssText: 'border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);'
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: textColor,
        fontSize: 11,
        margin: 12,
        interval: 0 // 强制显示所有日期，防止自适应时跳过标签
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: {
        lineStyle: { color: splitLineColor, type: 'dashed' }
      },
      axisLabel: { show: false }
    },
    series: [
      {
        name: t('adminDashboard.articlesTotal') || '发布数量',
        type: 'bar',
        data: counts,
        barMaxWidth: 32, // 使用MaxWidth防止柱子在宽屏下变巨无霸，同时窄屏下能自动缩窄
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#3b82f6' }, // brand-500
            { offset: 1, color: '#93c5fd' }  // brand-300
          ])
        },
        label: {
          show: true,
          position: 'top',
          color: isDark ? '#60a5fa' : '#3b82f6',
          fontSize: 11,
          fontWeight: 'bold',
          formatter: (params: any) => params.value > 0 ? params.value : ''
        }
      }
    ]
  }

  chartInstance.value.setOption(option)
}

watch(() => uiStore.theme, () => initChart())

const handleResize = () => {
  chartInstance.value?.resize()
}

onMounted(async () => {
  try {
    const res = await statsApi.get()
    if (res.data) {
      stats.value = res.data
      initChart()
    }
  } catch (e) { console.warn(e) }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance.value?.dispose()
})
</script>
