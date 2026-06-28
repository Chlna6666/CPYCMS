<!--
  CPYCMS - 备案信息展示
  从站点设置读取 ICP 备案号和公网安备号，并统一挂载到前台页脚与后台登录页。
-->
<template>
  <div v-if="hasRecords" class="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs text-[var(--cms-text-muted)]">
    <a
      v-if="icpNumber"
      :href="icpUrl"
      target="_blank"
      rel="noopener noreferrer nofollow"
      class="hover:text-brand-500 transition-colors"
      :aria-label="translate(uiStore.locale, 'footer.icpBeian')"
    >
      {{ icpNumber }}
    </a>
    <span v-if="icpNumber && policeNumber" aria-hidden="true" class="text-[var(--cms-text-muted)]/50">/</span>
    <a
      v-if="policeNumber"
      :href="policeUrl"
      target="_blank"
      rel="noopener noreferrer nofollow"
      class="hover:text-brand-500 transition-colors"
      :aria-label="translate(uiStore.locale, 'footer.policeBeian')"
    >
      {{ policeNumber }}
    </a>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { translate } from '@/i18n'
import { useSiteStore, useUiStore } from '@/stores'

const siteStore = useSiteStore()
const uiStore = useUiStore()

const icpUrl = 'https://beian.miit.gov.cn/#/Integrated/index'
const policeBaseUrl = 'https://beian.mps.gov.cn/#/query/webSearch'

const icpNumber = computed(() => (siteStore.siteInfo.icp_beian_number || '').trim())
const policeNumber = computed(() => (siteStore.siteInfo.police_beian_number || '').trim())
const policeCode = computed(() => {
  const matches = policeNumber.value.match(/\d{5,}/g) || []
  return matches.length ? matches[matches.length - 1] : ''
})
const policeUrl = computed(() => (
  policeCode.value ? `${policeBaseUrl}?code=${encodeURIComponent(policeCode.value)}` : policeBaseUrl
))
const hasRecords = computed(() => Boolean(icpNumber.value || policeNumber.value))

onMounted(() => {
  siteStore.loadSiteInfo()
})
</script>
