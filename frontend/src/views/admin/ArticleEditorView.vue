<template>
  <div class="w-full pb-12">
    <header
      class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      v-motion
      :initial="{ opacity: 0, y: -20 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
          {{ isEdit ? t('route.articleEdit') || '编辑文章' : t('route.articleCreate') || '撰写新文章' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ isEdit ? '更新现有的文章内容和元数据' : '创建一篇引人入胜的新文章' }}
        </p>
      </div>
      <router-link
        to="/admin/articles"
        class="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-50 hover:text-slate-900 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400 dark:hover:bg-slate-900 dark:hover:text-slate-100 active:scale-95"
      >
        <ArrowLeft class="h-4 w-4" />
        {{ t('adminAction.backList') || '返回列表' }}
      </router-link>
    </header>

    <transition name="toast">
      <div
        v-if="message"
        class="mb-6 flex items-center gap-3 rounded-xl p-4 text-sm font-medium shadow-sm"
        :class="msgType === 'success' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800/30 dark:text-emerald-400' : 'bg-red-50 text-red-600 border border-red-100 dark:bg-red-900/20 dark:border-red-800/30 dark:text-red-400'"
      >
        <CheckCircle v-if="msgType === 'success'" class="h-5 w-5 shrink-0" />
        <AlertCircle v-else class="h-5 w-5 shrink-0" />
        {{ message }}
      </div>
    </transition>

    <div class="flex flex-col gap-6">

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 100 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <Info class="h-5 w-5 text-brand-500" />
          基础信息
        </h2>

        <div class="grid grid-cols-1 gap-5 md:grid-cols-12">

          <div class="md:col-span-8">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminArticle.articleTitle') || '文章标题' }} *
            </label>
            <input
              v-model="form.title"
              type="text"
              class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              :placeholder="t('adminArticle.articleTitlePlaceholder') || '输入一个吸引人的标题...'"
            />
          </div>
          <div class="md:col-span-4">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminArticle.slug') || 'URL 别名 (Slug)' }}
            </label>
            <input
              v-model="form.slug"
              type="text"
              class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              :placeholder="t('adminArticle.slugPlaceholder') || 'my-awesome-post'"
            />
          </div>

          <div class="md:col-span-6 lg:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminArticle.selectCategory') || '选择分类' }}
            </label>
            <div class="relative">
              <select
                v-model="form.category_id"
                class="h-11 w-full appearance-none rounded-xl border border-slate-200 bg-transparent px-4 pr-10 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              >
                <option :value="null">{{ t('adminArticle.selectCategory') || '选择分类' }}</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
              <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            </div>
          </div>
          <div class="md:col-span-6 lg:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminTable.status') || '发布状态' }}
            </label>
            <div class="relative">
              <select
                v-model="form.status"
                class="h-11 w-full appearance-none rounded-xl border border-slate-200 bg-transparent px-4 pr-10 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              >
                <option value="draft">{{ t('adminStatus.draft') || '草稿' }}</option>
                <option value="published">{{ t('adminStatus.publish') || '直接发布' }}</option>
                <option value="archived">{{ t('adminStatus.archive') || '归档' }}</option>
              </select>
              <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            </div>
          </div>

          <div class="md:col-span-12">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminArticle.tags') || '标签' }}
            </label>
            <div class="flex flex-wrap gap-2 pt-1">
              <label
                v-for="tag in allTags"
                :key="tag.id"
                class="relative flex cursor-pointer items-center justify-center whitespace-nowrap rounded-lg border px-3 py-1.5 text-xs font-medium transition-all active:scale-95"
                :class="form.tag_ids.includes(tag.id) ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 shadow-sm' : 'border-slate-200 bg-slate-50 hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900/50 dark:hover:bg-slate-800'"
              >
                <input type="checkbox" :value="tag.id" v-model="form.tag_ids" class="sr-only" />
                <span :style="{ color: tag.color || 'inherit' }" :class="!tag.color ? 'text-slate-600 dark:text-slate-400' : ''">
                  # {{ tag.name }}
                </span>
              </label>
              <span v-if="allTags.length === 0" class="text-xs text-slate-400 py-2">暂无可用标签</span>
            </div>
          </div>
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 150 } }"
      >
        <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div>
            <h2 class="mb-4 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
              <FileText class="h-5 w-5 text-brand-500" />
              {{ t('adminArticle.summary') || '文章摘要' }}
            </h2>
            <textarea
              v-model="form.summary"
              class="h-32 w-full custom-scrollbar resize-none rounded-xl border border-slate-200 bg-transparent p-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              :placeholder="t('adminArticle.summaryPlaceholder') || '简短描述这篇文章的核心内容...'"
            ></textarea>
          </div>

          <div>
            <h2 class="mb-4 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
              <Image class="h-5 w-5 text-brand-500" />
              {{ t('adminArticle.cover') || '封面图' }}
            </h2>
            <div class="flex items-start gap-4">
              <label
                class="group flex h-32 w-full max-w-[200px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 transition-colors hover:border-brand-500 hover:bg-brand-50/50 dark:border-slate-800 dark:bg-slate-900 dark:hover:border-brand-500"
              >
                <input type="file" class="sr-only" accept="image/*" @change="uploadCover" />
                <UploadCloud class="mb-2 h-6 w-6 text-slate-400 group-hover:text-brand-500" />
                <span class="text-xs font-medium text-slate-500 group-hover:text-brand-600 dark:text-slate-400">点击上传封面</span>
              </label>

              <div
                v-if="form.cover_image"
                class="relative h-32 w-full max-w-[240px] overflow-hidden rounded-xl border border-slate-200 shadow-sm dark:border-slate-800"
              >
                <img :src="form.cover_image" alt="Cover preview" class="h-full w-full object-cover" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        class="flex flex-col rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 200 } }"
      >
        <div class="flex flex-wrap items-center justify-between border-b border-slate-100 px-5 py-3.5 dark:border-slate-800">
          <h2 class="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
            <PenTool class="h-5 w-5 text-brand-500" />
            {{ t('adminArticle.content') || '正文编辑' }}
          </h2>
          <div class="flex items-center gap-2">
            <label class="inline-flex h-9 cursor-pointer items-center justify-center gap-2 rounded-lg bg-slate-100 px-3 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 active:scale-95">
              <ImageIcon class="h-4 w-4" />
              {{ t('adminAction.insertImage') || '插入图片' }}
              <input type="file" accept="image/*" @change="uploadImage" hidden />
            </label>
            <button
              class="inline-flex h-9 items-center justify-center gap-2 rounded-lg px-3 text-xs font-medium transition-colors active:scale-95"
              :class="showPreview ? 'bg-brand-50 text-brand-600 dark:bg-brand-900/20 dark:text-brand-400' : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800'"
              @click="showPreview = !showPreview"
            >
              <Eye v-if="!showPreview" class="h-4 w-4" />
              <EyeOff v-else class="h-4 w-4" />
              {{ showPreview ? t('adminAction.edit') || '关闭预览' : t('adminAction.preview') || '实时预览' }}
            </button>
          </div>
        </div>

        <div class="flex flex-col md:flex-row">
          <div
            class="flex-1 transition-all duration-300 ease-in-out"
            :class="showPreview ? 'border-r border-slate-100 dark:border-slate-800' : ''"
          >
            <textarea
              v-model="form.content"
              class="min-h-[500px] w-full custom-scrollbar resize-none bg-slate-50/50 p-5 font-mono text-sm leading-relaxed text-slate-800 outline-none dark:bg-slate-950/50 dark:text-slate-200"
              :placeholder="t('adminArticle.markdownPlaceholder') || '开始使用 Markdown 编写您的内容...'"
            ></textarea>
          </div>

          <div
            v-if="showPreview"
            class="flex-1 overflow-hidden bg-white dark:bg-slate-950"
          >
            <div class="h-[500px] w-full overflow-y-auto p-6 custom-scrollbar">
              <div v-if="!form.content" class="flex h-full flex-col items-center justify-center text-slate-400">
                <FileText class="mb-3 h-12 w-12 opacity-20" />
                <p class="text-sm">预览区将实时显示渲染后的内容</p>
              </div>
              <MarkdownRenderer v-else :content="form.content" />
            </div>
          </div>
        </div>
      </section>

      <div
        class="mt-4 flex flex-wrap items-center gap-3"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 250 } }"
      >
        <button
          class="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-600 hover:shadow disabled:cursor-not-allowed disabled:opacity-60 active:scale-95"
          @click="saveArticle"
          :disabled="saving"
        >
          <Loader2 v-if="saving" class="h-4.5 w-4.5 animate-spin" />
          <Save v-else class="h-4.5 w-4.5" />
          {{ saving ? t('adminAction.saving') || '保存中...' : (isEdit ? t('adminAction.updateArticle') || '更新文章' : t('adminAction.createArticle') || '发布文章') }}
        </button>
        <button
          class="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-6 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-60 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 dark:hover:text-white active:scale-95"
          @click="saveDraft"
          :disabled="saving"
        >
          <Archive class="h-4 w-4" />
          {{ t('adminAction.saveDraft') || '存为草稿' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { articleApi, categoryApi, tagApi, uploadApi } from '@/services/api'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { useUiStore } from '@/stores'

// 引入全套高颜值 Lucide 图标
import {
  ArrowLeft, CheckCircle, AlertCircle, Info, ChevronDown,
  FileText, Image, UploadCloud, PenTool, Image as ImageIcon,
  Eye, EyeOff, Save, Archive, Loader2
} from '@lucide/vue'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const t = uiStore.t
const isEdit = computed(() => !!route.params.id)

const categories = ref<any[]>([])
const allTags = ref<any[]>([])
const showPreview = ref(false)
const saving = ref(false)
const message = ref('')
const msgType = ref('success')

const form = ref({
  title: '', slug: '', content: '', summary: '',
  category_id: null as number | null, status: 'draft', cover_image: '',
  tag_ids: [] as number[], is_top: false
})

const articleId = computed(() => Number(route.params.id))

async function loadData() {
  const [catRes, tagRes] = await Promise.all([categoryApi.adminGetList(), tagApi.adminGetList()])
  categories.value = catRes.data || []
  allTags.value = tagRes.data || []

  if (isEdit.value) {
    try {
      const detailRes = await articleApi.adminGetDetail(articleId.value)
      const d = detailRes.data
      if (d) {
        form.value = {
          title: d.title || '', slug: d.slug || '', content: d.content || '', summary: d.summary || '',
          category_id: d.category_id || null, status: d.status || 'draft', cover_image: d.cover_image || '',
          tag_ids: (d.tags || []).map((t: any) => t.id), is_top: !!d.is_top
        }
      }
    } catch (e) { console.warn(e) }
  }
}

async function uploadImage(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('image', file)
  try {
    const res = await uploadApi.image(fd)
    if (res.data?.url) {
      form.value.content += `\n![${file.name}](${res.data.url})\n`
    }
  } catch (e: any) { alert(e.message) }
  input.value = ''
}

async function uploadCover(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('image', file)
  try {
    const res = await uploadApi.articleCover(fd)
    if (res.data?.url) form.value.cover_image = res.data.url
  } catch (e: any) { alert(e.message) }
  input.value = ''
}

async function saveArticle() {
  if (!form.value.title.trim()) { message.value = t('adminArticle.titleRequired') || '标题不能为空'; msgType.value = 'danger'; scrollToTop(); return }
  if (!form.value.content.trim()) { message.value = t('adminArticle.contentRequired') || '文章内容不能为空'; msgType.value = 'danger'; scrollToTop(); return }

  saving.value = true
  message.value = ''

  try {
    if (isEdit.value) {
      await articleApi.update(articleId.value, form.value)
    } else {
      await articleApi.create(form.value)
    }
    message.value = t('adminArticle.saved') || '文章保存成功！'
    msgType.value = 'success'
    scrollToTop()
    setTimeout(() => router.push('/admin/articles'), 1500)
  } catch (e: any) {
    message.value = e.message
    msgType.value = 'danger'
    scrollToTop()
  }
  saving.value = false
}

function saveDraft() {
  form.value.status = 'draft'
  saveArticle()
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(loadData)
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

/* 顶部通知横幅过渡动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.98);
}
</style>