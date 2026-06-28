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
          {{ t('admin.works') || '作品管理' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          管理你的所有项目和展示作品
        </p>
      </div>
      <button
        class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 text-sm font-semibold text-white transition-colors hover:bg-brand-600 active:scale-95"
        @click="openModal()"
      >
        <Plus class="h-4.5 w-4.5" aria-hidden="true" />
        {{ t('adminAction.addWork') || '添加作品' }}
      </button>
    </header>

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
              <th class="px-5 py-4 font-medium">{{ t('adminTable.workName') || '作品名称' }}</th>
              <th class="px-5 py-4 font-medium">{{ t('adminTable.category') || '分类' }}</th>
              <th class="px-5 py-4 font-medium">{{ t('adminTable.techStack') || '技术栈' }}</th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Heart class="h-4 w-4" /> {{ t('adminTable.likes') || '点赞' }}</div></th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Eye class="h-4 w-4" /> {{ t('adminTable.views') || '浏览' }}</div></th>
              <th class="px-5 py-4 font-medium">{{ t('adminTable.status') || '状态' }}</th>
              <th class="px-5 py-4 font-medium text-right">{{ t('adminTable.actions') || '操作' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <tr
              v-for="w in works"
              :key="w.id"
              class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-900/40"
            >
              <td class="px-5 py-4">
                <span class="font-semibold text-slate-900 dark:text-slate-100">{{ w.title }}</span>
              </td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400">
                <div class="flex items-center gap-1.5">
                  <FolderTree class="h-3.5 w-3.5 text-slate-400" />
                  {{ w.category_name || t('adminStatus.none') || '无' }}
                </div>
              </td>
              <td class="px-5 py-4">
                <div class="flex flex-wrap gap-1.5 max-w-[200px]">
                  <span
                    v-for="(tech, i) in (w.tech_stack || [])"
                    :key="i"
                    class="inline-flex rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
                  >
                    {{ tech }}
                  </span>
                  <span v-if="!w.tech_stack || w.tech_stack.length === 0" class="text-xs text-slate-400">-</span>
                </div>
              </td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400">{{ w.like_count }}</td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400">{{ w.view_count }}</td>
              <td class="px-5 py-4">
                <span
                  class="inline-flex items-center rounded-md px-2 py-1 text-[11px] font-medium"
                  :class="w.status === 'published' ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
                >
                  {{ w.status === 'published' ? (t('adminStatus.published') || '已发布') : (t('adminStatus.draft') || '草稿') }}
                </span>
              </td>
              <td class="px-5 py-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-brand-50 hover:text-brand-600 dark:hover:bg-brand-900/20 dark:hover:text-brand-400"
                    :title="t('adminAction.edit') || '编辑'"
                    @click="openModal(w)"
                  >
                    <Edit class="h-4 w-4" />
                  </button>
                  <button
                    class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                    :title="t('adminAction.delete') || '删除'"
                    @click="deleteWork(w.id)"
                  >
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="works.length === 0">
              <td colspan="7" class="py-16 text-center text-sm text-slate-400">
                <div class="flex flex-col items-center justify-center">
                  <Monitor class="mb-3 h-10 w-10 opacity-20" />
                  {{ t('adminEmpty.works') || '暂无作品数据' }}
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
        v-for="p in totalPages"
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

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showModal = false"></div>

        <div class="relative flex w-full max-w-3xl flex-col rounded-2xl bg-white shadow-2xl dark:bg-slate-950">
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
            <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">
              {{ editingId ? (t('adminWork.editTitle') || '编辑作品') : (t('adminWork.createTitle') || '添加新作品') }}
            </h3>
            <button class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300" @click="showModal = false">
              <X class="h-5 w-5" />
            </button>
          </div>

          <div class="max-h-[70vh] overflow-y-auto px-6 py-5 custom-scrollbar">
            <div class="grid grid-cols-1 gap-5 md:grid-cols-12">

              <div class="md:col-span-6">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminWork.nameRequired') || '作品名称' }} *</label>
                <input v-model="editForm.title" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>

              <div class="md:col-span-6">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.category') || '所属分类' }}</label>
                <div class="relative">
                  <select v-model="editForm.category_id" class="h-10 w-full appearance-none rounded-xl border border-slate-200 bg-transparent px-3 pr-10 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100">
                    <option :value="null">{{ t('adminStatus.none') || '无分类' }}</option>
                    <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <div class="md:col-span-12">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.description') || '简短描述' }}</label>
                <textarea v-model="editForm.description" class="w-full resize-none rounded-xl border border-slate-200 bg-transparent p-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" rows="2"></textarea>
              </div>

              <div class="md:col-span-12">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminWork.detailMarkdown') || '详细介绍 (Markdown)' }}</label>
                <textarea v-model="editForm.content" class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50/50 p-3 font-mono text-sm leading-relaxed text-slate-800 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-200" rows="6"></textarea>
              </div>

              <div class="md:col-span-6">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminWork.techStackLabel') || '技术栈 (用逗号分隔)' }}</label>
                <input v-model="editForm.tech_stack_str" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" :placeholder="t('adminWork.techStackPlaceholder') || 'Vue, TailwindCSS, Node.js'" />
              </div>

              <div class="md:col-span-3">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminWork.demoUrl') || '预览地址' }}</label>
                <input v-model="editForm.demo_url" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" placeholder="https://" />
              </div>

              <div class="md:col-span-3">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminWork.sourceUrl') || '源码地址' }}</label>
                <input v-model="editForm.source_url" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" placeholder="https://" />
              </div>

              <div class="md:col-span-4">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.status') || '发布状态' }}</label>
                <div class="relative">
                  <select v-model="editForm.status" class="h-10 w-full appearance-none rounded-xl border border-slate-200 bg-transparent px-3 pr-10 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100">
                    <option value="published">{{ t('adminStatus.publish') || '发布' }}</option>
                    <option value="draft">{{ t('adminStatus.draft') || '草稿' }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>

              <div class="md:col-span-4">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.sort') || '排序' }}</label>
                <input v-model.number="editForm.sort_order" type="number" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>

              <div class="md:col-span-4">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminWork.cover') || '封面图上传' }}</label>
                <label class="flex h-10 w-full cursor-pointer items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 active:scale-95">
                  <Image class="h-4 w-4" />
                  <span class="truncate">{{ editForm.cover_image ? '重新上传封面' : '选择图片' }}</span>
                  <input type="file" class="sr-only" accept="image/*" @change="uploadCover" />
                </label>
                <div v-if="editForm.cover_image" class="mt-2 h-16 w-full overflow-hidden rounded-lg border border-slate-200 dark:border-slate-800">
                  <img :src="editForm.cover_image" class="h-full w-full object-cover" />
                </div>
              </div>

            </div>

            <div v-if="error" class="mt-4 flex items-center gap-2 rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-600 dark:border-red-900/30 dark:bg-red-900/20 dark:text-red-400">
              <AlertCircle class="h-4 w-4 shrink-0" />
              {{ error }}
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 border-t border-slate-100 px-6 py-4 dark:border-slate-800">
            <button
              class="h-10 rounded-xl px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 active:scale-95"
              @click="showModal = false"
            >
              {{ t('adminAction.cancel') || '取消' }}
            </button>
            <button
              class="h-10 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white transition-all hover:bg-brand-600 hover:shadow-sm active:scale-95"
              @click="saveWork"
            >
              {{ t('adminAction.save') || '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { workApi, categoryApi, uploadApi } from '@/services/api'
import type { Work, Category } from '@/services/api'
import { useUiStore } from '@/stores'
import {
  Plus, Edit, Trash2, FolderTree, Eye, Heart,
  ChevronLeft, ChevronRight, Monitor, X, Image,
  ChevronDown, AlertCircle
} from '@lucide/vue'

const uiStore = useUiStore()
const t = uiStore.t
const works = ref<Work[]>([])
const categories = ref<Category[]>([])
const loading = ref<boolean>(true)
const showModal = ref<boolean>(false)
const editingId = ref<number | null>(null)
const error = ref<string>('')
const page = ref<number>(1)
const totalPages = ref<number>(1)

const editForm = ref<Record<string, any>>({
  title: '', description: '', content: '', category_id: null,
  tech_stack_str: '', demo_url: '', source_url: '',
  status: 'published', sort_order: 0, cover_image: ''
})

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const [wRes, cRes] = await Promise.all([
      workApi.adminGetList({ page: page.value }),
      categoryApi.adminGetList()
    ])
    works.value = wRes.data?.items || []
    totalPages.value = wRes.data?.pages || 1
    categories.value = cRes.data || []
  } catch (e) { console.warn(e) }
  loading.value = false
}

function openModal(w: Work | null = null): void {
  editingId.value = w ? w.id : null
  editForm.value = w
    ? { ...w, tech_stack_str: (w.tech_stack || []).join(', ') }
    : { title: '', description: '', content: '', category_id: null, tech_stack_str: '', demo_url: '', source_url: '', status: 'published', sort_order: 0, cover_image: '' }
  error.value = ''
  showModal.value = true
}

async function uploadCover(e: Event): Promise<void> {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('image', file)
  try {
    const res = await uploadApi.workCover(fd)
    if (res.data?.url) editForm.value.cover_image = res.data.url
  } catch (err: any) { alert(err.message) }
  target.value = '' // 清除 input 状态
}

async function saveWork(): Promise<void> {
  if (!editForm.value.title.trim()) { error.value = t('adminWork.nameRequiredMessage') || '作品名称不能为空'; return }
  try {
    const data = {
      ...editForm.value,
      tech_stack: (editForm.value.tech_stack_str as string)
        .split(',')
        .map((s: string) => s.trim())
        .filter(Boolean)
    }
    if (editingId.value) {
      await workApi.update(editingId.value, data)
    } else {
      await workApi.create(data)
    }
    showModal.value = false
    loadData()
  } catch (e: any) { error.value = e.message }
}

async function deleteWork(id: number): Promise<void> {
  if (!confirm(t('adminWork.deleteConfirm') || '确定要删除这个作品吗？')) return
  try {
    await workApi.delete(id)
    if (works.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    loadData()
  } catch (e: any) { alert(e.message) }
}

function changePage(p: number): void {
  page.value = p
  loadData()
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
</style>