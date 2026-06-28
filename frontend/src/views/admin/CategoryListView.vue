<!--
  CPYCMS - 后台分类与标签管理
-->
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
          {{ t('adminCategory.pageTitle') || '分类与标签' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ t('adminCategory.pageDesc') || '统一维护文章分类、作品分类和文章标签' }}
        </p>
      </div>

      <div class="flex flex-wrap gap-2">
        <button
          class="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200 dark:hover:bg-slate-900 active:scale-95"
          @click="openTagModal()"
        >
          <Tag class="h-4.5 w-4.5" aria-hidden="true" />
          {{ t('adminAction.addTag') || '添加标签' }}
        </button>
        <button
          class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-4 text-sm font-semibold text-white transition-colors hover:bg-brand-600 active:scale-95"
          @click="openCategoryModal()"
        >
          <Plus class="h-4.5 w-4.5" aria-hidden="true" />
          {{ t('adminAction.addCategory') || '添加分类' }}
        </button>
      </div>
    </header>

    <div class="grid gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.85fr)]">
      <section
        class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 100 } }"
      >
        <div class="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-4 dark:border-slate-800">
          <div class="min-w-0">
            <h2 class="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
              <FolderTree class="h-4.5 w-4.5 text-brand-500" aria-hidden="true" />
              {{ t('adminCategory.categoriesTitle') || '分类目录' }}
            </h2>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {{ t('adminCategory.categoriesDesc') || '用于文章、作品、列表筛选和导航归档' }}
            </p>
          </div>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500 dark:bg-slate-900 dark:text-slate-400">
            {{ categories.length }}
          </span>
        </div>

        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
          <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-500"></div>
        </div>

        <div v-else class="overflow-x-auto custom-scrollbar">
          <table class="w-full whitespace-nowrap text-left text-sm">
            <thead class="border-b border-slate-100 bg-slate-50/50 text-slate-500 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-400">
              <tr>
                <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><FolderTree class="h-4 w-4" /> {{ t('adminTable.name') || '分类名称' }}</div></th>
                <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Hash class="h-4 w-4" /> {{ t('adminTable.alias') || '别名' }}</div></th>
                <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><AlignLeft class="h-4 w-4" /> {{ t('adminTable.description') || '描述' }}</div></th>
                <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><ListOrdered class="h-4 w-4" /> {{ t('adminTable.sort') || '排序' }}</div></th>
                <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><FileText class="h-4 w-4" /> {{ t('adminTable.articleCount') || '文章数' }}</div></th>
                <th class="px-5 py-4 font-medium"><div class="flex items-center gap-1.5"><Eye class="h-4 w-4" /> {{ t('adminTable.visible') || '可见' }}</div></th>
                <th class="px-5 py-4 font-medium text-right">{{ t('adminTable.actions') || '操作' }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
              <tr
                v-for="cat in categories"
                :key="cat.id"
                class="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-900/40"
              >
                <td class="px-5 py-4">
                  <span class="font-semibold text-slate-900 dark:text-slate-100">{{ cat.name }}</span>
                </td>
                <td class="px-5 py-4">
                  <span class="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[11px] text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                    {{ cat.slug }}
                  </span>
                </td>
                <td class="px-5 py-4 text-slate-500 dark:text-slate-400">
                  <span class="block max-w-[220px] truncate" :title="cat.description">{{ cat.description || t('adminStatus.none') || '无' }}</span>
                </td>
                <td class="px-5 py-4 text-slate-500 dark:text-slate-400">{{ cat.sort_order }}</td>
                <td class="px-5 py-4 font-medium text-slate-600 dark:text-slate-300">{{ cat.article_count }}</td>
                <td class="px-5 py-4">
                  <span
                    class="inline-flex items-center rounded-md px-2 py-1 text-[11px] font-medium"
                    :class="cat.is_visible ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'"
                  >
                    {{ cat.is_visible ? (t('adminStatus.visible') || '可见') : (t('adminStatus.hidden') || '隐藏') }}
                  </span>
                </td>
                <td class="px-5 py-4 text-right">
                  <div class="flex items-center justify-end gap-1">
                    <button
                      class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-brand-50 hover:text-brand-600 dark:hover:bg-brand-900/20 dark:hover:text-brand-400"
                      :title="t('adminAction.edit') || '编辑'"
                      @click="openCategoryModal(cat)"
                    >
                      <Edit class="h-4 w-4" aria-hidden="true" />
                    </button>
                    <button
                      class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                      :title="t('adminAction.delete') || '删除'"
                      @click="deleteCategory(cat.id)"
                    >
                      <Trash2 class="h-4 w-4" aria-hidden="true" />
                    </button>
                  </div>
                </td>
              </tr>

              <tr v-if="categories.length === 0">
                <td colspan="7" class="py-16 text-center text-sm text-slate-400">
                  <div class="flex flex-col items-center justify-center">
                    <FolderOpen class="mb-3 h-10 w-10 opacity-20" aria-hidden="true" />
                    {{ t('adminEmpty.categories') || '暂无分类数据' }}
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section
        class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-950"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 160 } }"
      >
        <div class="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-4 dark:border-slate-800">
          <div class="min-w-0">
            <h2 class="flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
              <Tag class="h-4.5 w-4.5 text-accent-500" aria-hidden="true" />
              {{ t('adminCategory.tagsTitle') || '文章标签' }}
            </h2>
            <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {{ t('adminCategory.tagsDesc') || '用于文章标记、主题聚合和前台标签云' }}
            </p>
          </div>
          <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500 dark:bg-slate-900 dark:text-slate-400">
            {{ tags.length }}
          </span>
        </div>

        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
          <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-accent-500"></div>
        </div>

        <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
          <article
            v-for="tag in tags"
            :key="tag.id"
            class="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-slate-50/60 dark:hover:bg-slate-900/40"
          >
            <div class="flex min-w-0 items-center gap-3">
              <span
                class="h-3.5 w-3.5 shrink-0 rounded-full ring-4 ring-slate-100 dark:ring-slate-800"
                :style="{ backgroundColor: tag.color }"
                aria-hidden="true"
              ></span>
              <div class="min-w-0">
                <h3 class="truncate text-sm font-semibold text-slate-900 dark:text-slate-100">{{ tag.name }}</h3>
                <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                  {{ tag.article_count }} {{ t('adminTable.articleCount') || '文章数' }}
                </p>
              </div>
            </div>
            <div class="flex shrink-0 items-center gap-1">
              <button
                class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-brand-50 hover:text-brand-600 dark:hover:bg-brand-900/20 dark:hover:text-brand-400"
                :title="t('adminAction.edit') || '编辑'"
                @click="openTagModal(tag)"
              >
                <Edit class="h-4 w-4" aria-hidden="true" />
              </button>
              <button
                class="inline-flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-800 dark:hover:bg-slate-800 dark:hover:text-slate-200"
                :title="t('adminAction.delete') || '删除'"
                @click="deleteTag(tag.id)"
              >
                <Trash2 class="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          </article>

          <div v-if="tags.length === 0" class="flex flex-col items-center justify-center px-5 py-16 text-center text-sm text-slate-400">
            <Tags class="mb-3 h-10 w-10 opacity-20" aria-hidden="true" />
            {{ t('adminEmpty.tags') || '暂无标签数据' }}
          </div>
        </div>
      </section>
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
        <div class="relative flex w-full max-w-md flex-col rounded-2xl bg-white shadow-2xl dark:bg-slate-950">
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
            <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">
              {{ modalTitle }}
            </h3>
            <button
              class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300"
              :aria-label="t('adminAction.cancel') || '取消'"
              @click="showModal = false"
            >
              <X class="h-5 w-5" aria-hidden="true" />
            </button>
          </div>

          <div class="px-6 py-5">
            <div v-if="modalMode === 'category'" class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="md:col-span-2">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminCategory.nameRequired') || '名称' }} *</label>
                <input v-model="categoryForm.name" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>

              <div class="md:col-span-2">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.alias') || '别名' }}</label>
                <input v-model="categoryForm.slug" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" :placeholder="t('adminArticle.slugPlaceholder') || '留空自动生成'" />
              </div>

              <div class="md:col-span-2">
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.description') || '描述' }}</label>
                <input v-model="categoryForm.description" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminTable.sort') || '排序' }}</label>
                <input v-model.number="categoryForm.sort_order" type="number" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminCategory.frontendVisible') || '前台可见' }}</label>
                <div class="relative">
                  <select v-model="categoryForm.is_visible" class="h-10 w-full appearance-none rounded-xl border border-slate-200 bg-transparent px-3 pr-10 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100">
                    <option :value="true">{{ t('adminStatus.visible') || '可见' }}</option>
                    <option :value="false">{{ t('adminStatus.hidden') || '隐藏' }}</option>
                  </select>
                  <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
                </div>
              </div>
            </div>

            <div v-else class="grid grid-cols-1 gap-4">
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminCategory.tagNameRequired') || '标签名称' }} *</label>
                <input v-model="tagForm.name" class="h-10 w-full rounded-xl border border-slate-200 bg-transparent px-3 text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminCategory.tagColor') || '标签颜色' }}</label>
                <div class="flex items-center gap-3">
                  <input v-model="tagForm.color" type="color" class="h-10 w-14 cursor-pointer rounded-xl border border-slate-200 bg-transparent p-1 dark:border-slate-800" />
                  <input v-model="tagForm.color" class="h-10 flex-1 rounded-xl border border-slate-200 bg-transparent px-3 font-mono text-sm text-slate-900 outline-none focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" placeholder="#2563eb" maxlength="20" />
                </div>
              </div>
            </div>

            <div v-if="error" class="mt-4 flex items-center gap-2 rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-600 dark:border-red-900/30 dark:bg-red-900/20 dark:text-red-400">
              <AlertCircle class="h-4 w-4 shrink-0" aria-hidden="true" />
              {{ error }}
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 border-t border-slate-100 px-6 py-4 dark:border-slate-800">
            <button class="h-10 rounded-xl px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 active:scale-95" @click="showModal = false">
              {{ t('adminAction.cancel') || '取消' }}
            </button>
            <button class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white transition-all hover:bg-brand-600 active:scale-95" @click="saveCurrent">
              {{ t('adminAction.save') || '保存' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { categoryApi, tagApi } from '@/services/api'
import type { Category, Tag as TagModel } from '@/services/api'
import { useUiStore } from '@/stores'
import {
  AlignLeft,
  AlertCircle,
  ChevronDown,
  Edit,
  Eye,
  FileText,
  FolderOpen,
  FolderTree,
  Hash,
  ListOrdered,
  Plus,
  Tag,
  Tags,
  Trash2,
  X
} from '@lucide/vue'

type ModalMode = 'category' | 'tag'

const uiStore = useUiStore()
const t = uiStore.t

const categories = ref<Category[]>([])
const tags = ref<TagModel[]>([])
const loading = ref<boolean>(true)
const showModal = ref<boolean>(false)
const modalMode = ref<ModalMode>('category')
const editingId = ref<number | null>(null)
const error = ref<string>('')

const categoryForm = ref({
  name: '',
  slug: '',
  description: '',
  sort_order: 0,
  is_visible: true
})

const tagForm = ref({
  name: '',
  color: '#2563eb'
})

const modalTitle = computed(() => {
  if (modalMode.value === 'tag') {
    return editingId.value ? (t('adminCategory.editTagTitle') || '编辑标签') : (t('adminCategory.createTagTitle') || '新建标签')
  }
  return editingId.value ? (t('adminCategory.editTitle') || '编辑分类') : (t('adminCategory.createTitle') || '新建分类')
})

async function loadData(): Promise<void> {
  loading.value = true
  try {
    const [categoryRes, tagRes] = await Promise.all([
      categoryApi.adminGetList(),
      tagApi.adminGetList()
    ])
    categories.value = categoryRes.data || []
    tags.value = tagRes.data || []
  } catch (e) {
    console.warn(e)
  } finally {
    loading.value = false
  }
}

function openCategoryModal(cat: Category | null = null): void {
  modalMode.value = 'category'
  editingId.value = cat ? cat.id : null
  categoryForm.value = cat
    ? {
        name: cat.name,
        slug: cat.slug,
        description: cat.description || '',
        sort_order: cat.sort_order,
        is_visible: cat.is_visible
      }
    : { name: '', slug: '', description: '', sort_order: 0, is_visible: true }
  error.value = ''
  showModal.value = true
}

function openTagModal(tag: TagModel | null = null): void {
  modalMode.value = 'tag'
  editingId.value = tag ? tag.id : null
  tagForm.value = tag
    ? { name: tag.name, color: tag.color || '#2563eb' }
    : { name: '', color: '#2563eb' }
  error.value = ''
  showModal.value = true
}

async function saveCurrent(): Promise<void> {
  if (modalMode.value === 'tag') {
    await saveTag()
    return
  }
  await saveCategory()
}

async function saveCategory(): Promise<void> {
  if (!categoryForm.value.name.trim()) {
    error.value = t('adminCategory.nameRequiredMessage') || '名称不能为空'
    return
  }
  try {
    if (editingId.value) {
      await categoryApi.update(editingId.value, categoryForm.value)
    } else {
      await categoryApi.create(categoryForm.value)
    }
    showModal.value = false
    await loadData()
  } catch (e: any) {
    error.value = e.message
  }
}

async function saveTag(): Promise<void> {
  if (!tagForm.value.name.trim()) {
    error.value = t('adminCategory.tagNameRequiredMessage') || '标签名称不能为空'
    return
  }
  try {
    if (editingId.value) {
      await tagApi.update(editingId.value, tagForm.value)
    } else {
      await tagApi.create(tagForm.value)
    }
    showModal.value = false
    await loadData()
  } catch (e: any) {
    error.value = e.message
  }
}

async function deleteCategory(id: number): Promise<void> {
  if (!confirm(t('adminCategory.deleteConfirm') || '确定要删除此分类吗？')) return
  try {
    await categoryApi.delete(id)
    await loadData()
  } catch (e: any) {
    alert(e.message)
  }
}

async function deleteTag(id: number): Promise<void> {
  if (!confirm(t('adminCategory.deleteTagConfirm') || '确定要删除此标签吗？')) return
  try {
    await tagApi.delete(id)
    await loadData()
  } catch (e: any) {
    alert(e.message)
  }
}

onMounted(loadData)
</script>

<style scoped>
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
