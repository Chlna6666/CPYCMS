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
          {{ t('admin.resources') || '资源管理' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          管理和分享站点内的文件、文档与附件
        </p>
      </div>
      <button
        class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 text-sm font-semibold text-white transition-colors hover:bg-brand-600 active:scale-95"
        @click="openUpload"
      >
        <Upload class="h-4.5 w-4.5" aria-hidden="true" />
        {{ t('adminAction.uploadResource') || '上传资源' }}
      </button>
    </header>

    <transition name="toast">
      <div
        v-if="errorMsg"
        class="mb-6 flex items-center gap-3 rounded-xl border border-red-100 bg-red-50 p-4 text-sm font-medium text-red-600 shadow-sm dark:border-red-900/30 dark:bg-red-900/20 dark:text-red-400"
      >
        <AlertCircle class="h-5 w-5 shrink-0" />
        {{ errorMsg }}
      </div>
    </transition>

    <form
      class="mb-6 grid grid-cols-1 gap-3 md:grid-cols-12"
      @submit.prevent="submitSearch"
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 50 } }"
    >
      <div class="relative md:col-span-5">
        <label class="sr-only" for="admin-resource-keyword">{{ t('adminResource.searchPlaceholder') || '搜索资源...' }}</label>
        <Search class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        <input
          id="admin-resource-keyword"
          v-model.trim="keyword"
          type="search"
          class="h-10 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
          :placeholder="t('adminResource.searchPlaceholder') || '输入资源名称或描述...'"
        />
      </div>

      <div class="relative md:col-span-4">
        <label class="sr-only" for="admin-resource-status">{{ t('adminResource.statusFilter') || '状态筛选' }}</label>
        <Filter class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
        <select
          id="admin-resource-status"
          v-model="status"
          class="h-10 w-full appearance-none rounded-xl border border-slate-200 bg-white pl-10 pr-10 text-sm text-slate-700 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300"
          @change="submitSearch"
        >
          <option value="">{{ t('adminStatus.allStatus') || '全部状态' }}</option>
          <option value="published">{{ t('adminStatus.published') || '已发布' }}</option>
          <option value="draft">{{ t('adminStatus.draft') || '草稿/隐藏' }}</option>
        </select>
        <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
      </div>

      <div class="flex gap-2 md:col-span-3">
        <button
          class="flex h-10 flex-1 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 text-sm font-medium text-white transition-colors hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200 active:scale-95"
          type="submit"
        >
          {{ t('common.search') || '搜索' }}
        </button>
        <button
          class="flex h-10 flex-1 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300 dark:hover:bg-slate-900 active:scale-95"
          type="button"
          @click="resetFilters"
        >
          <RefreshCcw class="h-4 w-4" aria-hidden="true" />
          {{ t('common.all') || '重置' }}
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
              <th class="px-5 py-4 font-medium">{{ t('adminTable.name') || '资源名称' }}</th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><File class="h-4 w-4" /> {{ t('adminTable.fileName') || '文件名' }}</div></th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><HardDrive class="h-4 w-4" /> {{ t('adminTable.size') || '大小' }}</div></th>
              <th class="px-5 py-4 font-medium">{{ t('adminTable.type') || '类型' }}</th>
              <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Download class="h-4 w-4" /> {{ t('adminTable.downloads') || '下载次数' }}</div></th>
              <th class="px-5 py-4 font-medium">{{ t('adminTable.status') || '状态' }}</th>
              <th class="px-5 py-4 font-medium text-right">{{ t('adminTable.actions') || '操作' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <tr
              v-for="r in resources"
              :key="r.id"
              class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-900/40"
            >
              <td class="px-5 py-4">
                <div class="flex flex-col">
                  <span class="font-semibold text-slate-900 dark:text-slate-100">{{ r.title }}</span>
                  <span class="mt-0.5 max-w-[200px] truncate text-xs text-slate-500 dark:text-slate-400" :title="r.description">{{ r.description || '-' }}</span>
                </div>
              </td>
              <td class="px-5 py-4">
                <span class="font-mono text-xs text-slate-600 dark:text-slate-400">{{ r.file_name }}</span>
              </td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400">
                {{ formatSize(r.file_size) }}
              </td>
              <td class="px-5 py-4">
                <span class="inline-flex items-center rounded-md border border-indigo-200 bg-indigo-50 px-2 py-0.5 text-[11px] font-bold uppercase text-indigo-600 dark:border-indigo-800/50 dark:bg-indigo-900/20 dark:text-indigo-400">
                  {{ r.file_type || 'UNK' }}
                </span>
              </td>
              <td class="px-5 py-4 text-slate-500 dark:text-slate-400">
                {{ r.download_count }}
              </td>
              <td class="px-5 py-4">
                <span
                  class="inline-flex items-center rounded-md px-2 py-1 text-[11px] font-medium"
                  :class="r.status === 'published' ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
                >
                  {{ r.status === 'published' ? (t('adminStatus.publish') || '已发布') : (t('adminStatus.draft') || '已隐藏') }}
                </span>
              </td>
              <td class="px-5 py-4 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-brand-50 hover:text-brand-600 dark:hover:bg-brand-900/20 dark:hover:text-brand-400"
                    :title="t('adminAction.edit') || '编辑'"
                    @click="editResource(r)"
                  >
                    <Edit class="h-4 w-4" />
                  </button>
                  <button
                    class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                    :title="t('adminAction.delete') || '删除'"
                    @click="deleteResource(r.id)"
                  >
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="resources.length === 0">
              <td colspan="7" class="py-16 text-center text-sm text-slate-400">
                <div class="flex flex-col items-center justify-center">
                  <FileBox class="mb-3 h-10 w-10 opacity-20" />
                  {{ t('adminEmpty.resources') || '暂无资源数据，点击上方按钮上传' }}
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
      <div v-if="showUpload" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showUpload = false"></div>
        <div class="relative flex w-full max-w-lg flex-col rounded-2xl bg-white shadow-2xl dark:bg-slate-950">
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
            <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">{{ t('adminResource.uploadTitle') || '上传新资源' }}</h3>
            <button class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300" @click="showUpload = false">
              <X class="h-5 w-5" />
            </button>
          </div>

          <div class="px-6 py-5">
            <div class="space-y-4">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminResource.resourceNameRequired') || '资源显示名称' }} *</label>
                <input v-model="uploadForm.title" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.description') || '简短说明' }}</label>
                <textarea v-model="uploadForm.description" class="w-full resize-none rounded-xl border border-slate-200 bg-transparent p-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" rows="3"></textarea>
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminResource.selectFileRequired') || '选择文件' }} *</label>
                <input
                  ref="uploadInput"
                  type="file"
                  class="block w-full text-sm text-slate-500 file:mr-4 file:rounded-full file:border-0 file:bg-brand-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-brand-600 hover:file:bg-brand-100 dark:text-slate-400 dark:file:bg-brand-900/20 dark:file:text-brand-400"
                  @change="selectUploadFile"
                />
                <p class="mt-2 text-xs text-slate-500 dark:text-slate-400">{{ t('adminResource.uploadHelp') || '支持各种常见文件格式，注意服务器上传大小限制。' }}</p>
              </div>

              <div v-if="uploadMsg" class="mt-2 rounded-lg p-3 text-sm font-medium" :class="uploadOk ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400'">
                {{ uploadMsg }}
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 border-t border-slate-100 px-6 py-4 dark:border-slate-800">
            <button class="h-10 rounded-xl px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" @click="showUpload = false">
              {{ t('adminAction.cancel') || '取消' }}
            </button>
            <button class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white transition-all hover:bg-brand-600 disabled:opacity-60 active:scale-95" @click="doUpload" :disabled="uploading">
              <Loader2 v-if="uploading" class="h-4 w-4 animate-spin" />
              {{ uploading ? t('adminAction.uploading') || '上传中...' : t('adminAction.upload') || '开始上传' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showEdit" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showEdit = false"></div>
        <div class="relative flex w-full max-w-lg flex-col rounded-2xl bg-white shadow-2xl dark:bg-slate-950">
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
            <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">{{ t('adminResource.editTitle') || '编辑资源信息' }}</h3>
            <button class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300" @click="showEdit = false">
              <X class="h-5 w-5" />
            </button>
          </div>

          <div class="px-6 py-5">
            <div class="space-y-4">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.name') || '资源名称' }}</label>
                <input v-model="editForm.title" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.description') || '简短说明' }}</label>
                <textarea v-model="editForm.description" class="w-full resize-none rounded-xl border border-slate-200 bg-transparent p-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" rows="3"></textarea>
              </div>
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.status') || '发布状态' }}</label>
                <div class="relative">
                  <select v-model="editForm.status" class="h-10 w-full appearance-none rounded-xl border border-slate-200 bg-transparent px-3 pr-10 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100">
                    <option value="published">{{ t('adminStatus.publish') || '正常显示' }}</option>
                    <option value="draft">{{ t('adminStatus.draft') || '隐藏(草稿)' }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 border-t border-slate-100 px-6 py-4 dark:border-slate-800">
            <button class="h-10 rounded-xl px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" @click="showEdit = false">
              {{ t('adminAction.cancel') || '取消' }}
            </button>
            <button class="h-10 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white transition-all hover:bg-brand-600 active:scale-95" @click="doUpdate">
              {{ t('adminAction.save') || '保存更改' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { resourceApi } from '@/services/api'
import type { Resource } from '@/services/api'
import { useUiStore } from '@/stores'

// 引入高颜值 Lucide 图标
import {
  Upload, Search, Filter, ChevronDown, RefreshCcw,
  File, HardDrive, Download, Edit, Trash2, Inbox as FileBox,
  AlertCircle, ChevronLeft, ChevronRight, X, Loader2
} from '@lucide/vue'

const uiStore = useUiStore()
const t = uiStore.t
const resources = ref<Resource[]>([])
const loading = ref<boolean>(true)
const page = ref<number>(1)
const totalPages = ref<number>(1)
const keyword = ref<string>('')
const status = ref<string>('')
const errorMsg = ref<string>('')

// 上传状态管理
const showUpload = ref<boolean>(false)
const uploading = ref<boolean>(false)
const uploadMsg = ref<string>('')
const uploadOk = ref<boolean>(true)
const uploadForm = ref<{ title: string; description: string; file: File | null }>({ title: '', description: '', file: null })
const uploadInput = ref<HTMLInputElement | null>(null)

// 编辑状态管理
const showEdit = ref<boolean>(false)
const editForm = ref<{ id: number | null; title: string; description: string; status: 'draft' | 'published' }>({
  id: null, title: '', description: '', status: 'published'
})

function formatSize(b: number): string {
  if (b < 1024) return b + ' B'
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB'
  return (b / 1048576).toFixed(1) + ' MB'
}

async function loadData(): Promise<void> {
  loading.value = true
  errorMsg.value = ''
  try {
    const params: Record<string, string | number> = { page: page.value }
    if (keyword.value) params.keyword = keyword.value
    if (status.value) params.status = status.value
    const res = await resourceApi.adminGetList(params)
    resources.value = res.data?.items || []
    totalPages.value = res.data?.pages || 1
  } catch (e: any) {
    errorMsg.value = e.message || t('common.networkError')
    resources.value = []
    totalPages.value = 1
  }
  loading.value = false
}

function openUpload(): void {
  uploadMsg.value = ''
  uploadOk.value = true
  uploadForm.value = { title: '', description: '', file: null }
  showUpload.value = true
}

async function doUpload(): Promise<void> {
  if (!uploadForm.value.title || !uploadForm.value.file) {
    uploadMsg.value = t('adminResource.uploadRequired') || '资源名称和文件必须填写'
    uploadOk.value = false
    return
  }
  uploading.value = true
  uploadMsg.value = ''

  const fd = new FormData()
  fd.append('title', uploadForm.value.title)
  fd.append('description', uploadForm.value.description)
  fd.append('file', uploadForm.value.file)

  try {
    await resourceApi.upload(fd)
    showUpload.value = false
    uploadForm.value = { title: '', description: '', file: null }
    if (uploadInput.value) uploadInput.value.value = ''
    loadData()
  } catch (e: any) {
    uploadMsg.value = e.message || t('common.networkError')
    uploadOk.value = false
  }
  uploading.value = false
}

function selectUploadFile(e: Event): void {
  const input = e.target as HTMLInputElement
  uploadForm.value.file = input.files?.[0] || null
}

function editResource(r: Resource): void {
  editForm.value = { id: r.id, title: r.title, description: r.description || '', status: r.status }
  showEdit.value = true
}

async function doUpdate(): Promise<void> {
  try {
    const { id, ...payload } = editForm.value
    await resourceApi.update(id!, payload)
    showEdit.value = false
    loadData()
  } catch (e: any) {
    alert(e.message)
  }
}

async function deleteResource(id: number): Promise<void> {
  if (!confirm(t('adminResource.deleteConfirm') || '确定要彻底删除该资源及其文件吗？此操作不可撤销。')) return
  try {
    await resourceApi.delete(id)
    if (resources.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    loadData()
  } catch (e: any) {
    alert(e.message)
  }
}

function changePage(p: number): void {
  page.value = p
  loadData()
}

function submitSearch(): void {
  page.value = 1
  loadData()
}

function resetFilters(): void {
  keyword.value = ''
  status.value = ''
  page.value = 1
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