<!--
  CPYCMS - 作品展示页（个性化功能模块1）
  展示个人作品，支持点赞、查看详情
-->
<template>
  <div class="container py-5 fade-in">
    <h2 class="section-title mb-4">{{ t('portfolio.title') }}</h2>
    <p class="text-muted mb-4">{{ t('portfolio.intro') }}</p>

    <div v-if="loading" class="cms-loading"></div>
    <div v-else-if="works.length === 0" class="cms-empty">
      <Sparkles class="empty-icon mx-auto" aria-hidden="true" />
      <p>{{ t('portfolio.empty') }}</p>
    </div>
    <div v-else class="row g-4">
      <div class="col-md-6 col-lg-4" v-for="work in works" :key="work.id">
        <div class="cms-card h-100">
          <div v-if="work.cover_image" style="height:200px;overflow:hidden">
            <img :src="work.cover_image" class="w-100 h-100" style="object-fit:cover" :alt="work.title" />
          </div>
          <div class="p-3">
            <h5 class="mb-2">{{ work.title }}</h5>
            <p class="text-muted small mb-2">{{ work.description?.substring(0, 80) || t('portfolio.descFallback') }}</p>
            <div class="d-flex flex-wrap gap-1 mb-3">
              <span v-for="tech in work.tech_stack" :key="tech" class="cms-tag small">{{ tech }}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex gap-3 text-muted small">
                <span class="inline-flex items-center gap-1"><Heart class="cms-icon-sm" aria-hidden="true" /> {{ work.like_count }}</span>
                <span class="inline-flex items-center gap-1"><Eye class="cms-icon-sm" aria-hidden="true" /> {{ work.view_count }}</span>
              </div>
              <router-link :to="`/portfolio/${work.id}`" class="cms-btn cms-btn-primary" style="padding:5px 14px;font-size:0.8rem">
                {{ t('portfolio.detail') }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="cms-pagination" v-if="totalPages > 1">
      <button :disabled="page <= 1" @click="changePage(page - 1)">&laquo;</button>
      <button v-for="p in totalPages" :key="p" :class="{ active: p === page }" @click="changePage(p)">{{ p }}</button>
      <button :disabled="page >= totalPages" @click="changePage(page + 1)">&raquo;</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { workApi, type Work } from '@/services/api'
import { useUiStore } from '@/stores'
import { Eye, Heart, Sparkles } from '@lucide/vue'

const works = ref<Work[]>([])
const uiStore = useUiStore()
const t = uiStore.t
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)

async function loadWorks() {
  loading.value = true
  try {
    const res = await workApi.getList({ page: page.value })
    works.value = res.data?.items || []
    totalPages.value = res.data?.pages || 1
  } catch (e) { console.warn(e) }
  loading.value = false
}

function changePage(p: number) {
  page.value = p
  loadWorks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(loadWorks)
</script>
