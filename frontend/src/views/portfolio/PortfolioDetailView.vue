<!--
  CPYCMS - 作品详情页
  展示作品完整信息，支持点赞互动
-->
<template>
  <div class="container py-5 fade-in">
    <div v-if="loading" class="cms-loading"></div>
    <div v-else-if="!work" class="cms-empty">
      <CircleOff class="empty-icon mx-auto" aria-hidden="true" />
      <p>{{ t('portfolio.notFound') }}</p>
      <router-link to="/portfolio" class="cms-btn cms-btn-primary">{{ t('portfolio.backToList') }}</router-link>
    </div>
    <div v-else class="row">
      <div class="col-lg-8 mx-auto">
        <div class="cms-card p-4 p-md-5">
          <!-- 封面图 -->
          <div v-if="work.cover_image" class="mb-4" style="border-radius:12px;overflow:hidden">
            <img :src="work.cover_image" class="w-100" :alt="work.title" />
          </div>

          <header class="mb-4">
            <h1 style="font-size:2rem">{{ work.title }}</h1>
            <p class="text-muted">{{ work.description }}</p>
            <div class="d-flex flex-wrap gap-2 mb-3">
              <span v-for="tech in work.tech_stack" :key="tech" class="cms-tag">{{ tech }}</span>
            </div>
            <div class="d-flex gap-3 text-muted small">
              <span class="inline-flex items-center gap-1"><CalendarDays class="cms-icon-sm" aria-hidden="true" /> {{ work.created_at }}</span>
              <span class="inline-flex items-center gap-1"><Eye class="cms-icon-sm" aria-hidden="true" /> {{ work.view_count }} {{ t('portfolio.viewsSuffix') }}</span>
              <span class="inline-flex items-center gap-1"><Heart class="cms-icon-sm" aria-hidden="true" /> {{ work.like_count }} {{ t('portfolio.likesSuffix') }}</span>
            </div>
          </header>

          <!-- 作品详情 -->
          <MarkdownRenderer v-if="work.content" :content="work.content" />

          <!-- 链接 -->
          <div class="d-flex gap-3 mt-4" v-if="work.demo_url || work.source_url">
            <a v-if="work.demo_url" :href="work.demo_url" target="_blank" class="cms-btn cms-btn-primary">{{ t('portfolio.demo') }}</a>
            <a v-if="work.source_url" :href="work.source_url" target="_blank" class="cms-btn cms-btn-outline">{{ t('portfolio.source') }}</a>
          </div>

          <!-- 点赞按钮 -->
          <div class="text-center mt-5 pt-3 border-top">
            <button class="cms-btn cms-btn-accent" @click="handleLike" :disabled="liked">
              <Heart class="cms-icon" aria-hidden="true" />
              {{ liked ? t('portfolio.liked') : t('portfolio.likeButton') }}
            </button>
            <span class="ms-2 text-muted">{{ work.like_count }} {{ t('portfolio.peopleLiked') }}</span>
          </div>
        </div>

        <div class="text-center mt-4">
          <router-link to="/portfolio" class="cms-btn cms-btn-outline">&larr; {{ t('portfolio.title') }}</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { workApi, type Work } from '@/services/api'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'
import { useUiStore } from '@/stores'
import { buildClientFingerprint } from '@/utils/clientFingerprint'
import { CalendarDays, CircleOff, Eye, Heart } from '@lucide/vue'

const route = useRoute()
const uiStore = useUiStore()
const t = uiStore.t
const work = ref<Work | null>(null)
const loading = ref(true)
const liked = ref(false)

async function loadWork() {
  try {
    const idParam = Array.isArray(route.params.id) ? route.params.id[0] : route.params.id
    const res = await workApi.getDetail(Number(idParam))
    work.value = res.data || null
  } catch (e) { console.warn(e) }
  loading.value = false
}

async function handleLike() {
  if (liked.value || !work.value) return
  try {
    const fingerprint = await buildClientFingerprint()
    const res = await workApi.like(work.value.id, { client_fingerprint: fingerprint })
    if (res.code === 200) {
      work.value.like_count = res.like_count
      liked.value = true
    }
  } catch (e: any) {
    liked.value = true
    alert(e.message)
  }
}

onMounted(loadWork)
</script>
