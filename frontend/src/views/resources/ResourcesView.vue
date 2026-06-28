<!--
  CPYCMS - 资源下载页（个性化功能模块2）
  展示可下载的资源文件
-->
<template>
  <div class="container py-5 fade-in">
    <h2 class="section-title mb-4">{{ t('resources.title') }}</h2>
    <p class="text-muted mb-4">{{ t('resources.intro') }}</p>

    <div v-if="keyword" class="mb-4 rounded-2xl border border-cyan-200 bg-cyan-50 px-4 py-3 text-sm text-cyan-800 dark:border-cyan-500/20 dark:bg-cyan-500/10 dark:text-cyan-200">
      {{ t('globalSearch.filteredBy', { keyword }) }}
    </div>

    <div v-if="loading" class="cms-loading"></div>
    <div v-else-if="resources.length === 0" class="cms-empty">
      <PackageOpen class="empty-icon mx-auto" aria-hidden="true" />
      <p>{{ t('resources.empty') }}</p>
    </div>
    <div v-else>
      <div v-for="res in resources" :key="res.id" class="cms-card p-4 mb-3">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
          <div class="d-flex align-items-center gap-3">
            <div class="file-icon">
              <component :is="getFileIcon(res.file_type)" class="cms-icon" aria-hidden="true" />
            </div>
            <div>
              <h5 class="mb-1">{{ res.title }}</h5>
              <p class="text-muted small mb-1">{{ res.description || t('resources.descFallback') }}</p>
              <div class="d-flex gap-3 text-muted small flex-wrap">
                <span>{{ res.file_name }}</span>
                <span>{{ formatSize(res.file_size) }}</span>
                <span class="inline-flex items-center gap-1"><Download class="cms-icon-sm" aria-hidden="true" /> {{ t('resources.downloaded') }} {{ res.download_count }} {{ t('resources.suffix') }}</span>
                <span>{{ res.created_at }}</span>
              </div>
            </div>
          </div>
          <a :href="downloadUrl(res.id)" class="cms-btn cms-btn-accent" download>
            <Download class="cms-icon" aria-hidden="true" /> {{ t('resources.download') }}
          </a>
        </div>
      </div>
    </div>

    <div class="cms-pagination" v-if="totalPages > 1">
      <button :disabled="page <= 1" @click="changePage(page - 1)">&laquo;</button>
      <button v-for="p in totalPages" :key="p" :class="{ active: p === page }" @click="changePage(p)">{{ p }}</button>
      <button :disabled="page >= totalPages" @click="changePage(page + 1)">&raquo;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { resourceApi, type Resource } from '@/services/api'
import { useUiStore } from '@/stores'
import { Archive, Download, FileArchive, FileSpreadsheet, FileText, PackageOpen } from '@lucide/vue'

const resources = ref<Resource[]>([])
const uiStore = useUiStore()
const t = uiStore.t
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)
const route = useRoute()
const keyword = ref('')

function downloadUrl(id: number) { return resourceApi.download(id) }
function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}
function getFileIcon(type: string) {
  const icons: Record<string, unknown> = {
    zip: FileArchive,
    rar: FileArchive,
    '7z': FileArchive,
    xls: FileSpreadsheet,
    xlsx: FileSpreadsheet,
    ppt: FileSpreadsheet,
    pptx: FileSpreadsheet,
    pdf: FileText,
    doc: FileText,
    docx: FileText,
    txt: FileText,
    md: FileText
  }
  return icons[type] || Archive
}

async function loadResources() {
  loading.value = true
  try {
    const params: Record<string, string | number> = { page: page.value }
    if (keyword.value) params.keyword = keyword.value
    const res = await resourceApi.getList(params)
    resources.value = res.data?.items || []
    totalPages.value = res.data?.pages || 1
  } catch (e) { console.warn(e) }
  loading.value = false
}
function changePage(p: number) { page.value = p; loadResources(); window.scrollTo({ top: 0, behavior: 'smooth' }) }

function queryStringValue(value: unknown): string {
  return Array.isArray(value) ? String(value[0] || '') : String(value || '')
}

onMounted(() => {
  keyword.value = route.query.keyword ? queryStringValue(route.query.keyword) : ''
  loadResources()
})

watch(() => route.query.keyword, value => {
  keyword.value = value ? queryStringValue(value) : ''
  page.value = 1
  loadResources()
})
</script>

<style scoped>
.file-icon { width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; background: #e2e8f0; border-radius: 10px; font-size: 1.5rem; }
</style>
