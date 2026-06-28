<template>
  <div class="min-h-screen pb-16">
    <!-- Hero Header Banner -->
    <section class="relative overflow-hidden py-12 sm:py-16 bg-gradient-to-b from-brand-500/10 via-transparent to-transparent border-b border-[var(--cms-border)]">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-4">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 text-xs font-semibold tracking-wide uppercase">
          <Sparkles class="w-3.5 h-3.5" />
          <span>{{ t('route.about') || '关于我们' }}</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-black tracking-tight text-[var(--cms-text)]">
          {{ t('about.titlePrefix') }}
          <span class="bg-gradient-to-r from-brand-500 to-indigo-500 bg-clip-text text-transparent dark:from-brand-400 dark:to-indigo-400">
            {{ siteTitle }}
          </span>
        </h1>
        <p class="max-w-2xl mx-auto text-sm text-[var(--cms-text-muted)] leading-relaxed">
          {{ siteSubtitle }}
        </p>
      </div>
    </section>

    <!-- Main Content Area -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 pt-10">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Sidebar Info Card -->
        <div class="lg:col-span-1 space-y-6">
          <div class="bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-3xl p-6 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col items-center text-center">
            <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-brand-500 to-indigo-500 flex items-center justify-center text-white text-2xl font-black shadow-lg mb-4">
              {{ siteStore.siteInfo.author_name ? siteStore.siteInfo.author_name.charAt(0).toUpperCase() : 'A' }}
            </div>
            <h3 class="text-lg font-bold text-[var(--cms-text)]">
              {{ siteStore.siteInfo.author_name || t('common.siteDefaultName') }}
            </h3>
            <p class="text-xs text-[var(--cms-text-muted)] mt-1">
              {{ t('identity.admin') || '站长 / 管理员' }}
            </p>

            <div v-if="siteStore.siteInfo.author_email" class="w-full mt-6 pt-6 border-t border-[var(--cms-border)] flex items-center justify-center gap-2 text-xs text-[var(--cms-text-muted)]">
              <Mail class="w-4 h-4 text-brand-500 shrink-0" />
              <a :href="`mailto:${siteStore.siteInfo.author_email}`" class="hover:text-brand-500 transition-colors truncate">
                {{ siteStore.siteInfo.author_email }}
              </a>
            </div>
          </div>

          <!-- Quick Navigation Card -->
          <div class="bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-3xl p-6 shadow-sm space-y-3">
            <h4 class="text-xs font-bold text-[var(--cms-text-muted)] uppercase tracking-wider mb-2">
              {{ t('footer.quickNav') }}
            </h4>
            <router-link to="/articles" class="flex items-center justify-between p-3 rounded-2xl bg-[var(--cms-surface-muted)] hover:bg-brand-500/10 hover:text-brand-500 text-xs font-medium transition-all group">
              <span class="flex items-center gap-2">
                <FileText class="w-4 h-4 text-brand-500" />
                <span>{{ t('nav.articles') }}</span>
              </span>
              <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </router-link>
            <router-link to="/contact" class="flex items-center justify-between p-3 rounded-2xl bg-[var(--cms-surface-muted)] hover:bg-brand-500/10 hover:text-brand-500 text-xs font-medium transition-all group">
              <span class="flex items-center gap-2">
                <Mail class="w-4 h-4 text-brand-500" />
                <span>{{ t('footer.contactUs') }}</span>
              </span>
              <ArrowRight class="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </router-link>
          </div>
        </div>

        <!-- Markdown Document View -->
        <div class="lg:col-span-2">
          <div class="bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-3xl p-6 sm:p-8 shadow-sm">
            <MarkdownRenderer :content="aboutContent" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Sparkles, Mail, ArrowRight, FileText } from '@lucide/vue'
import { useSiteStore, useUiStore } from '@/stores'
import MarkdownRenderer from '@/components/common/MarkdownRenderer.vue'

const siteStore = useSiteStore()
const uiStore = useUiStore()
const t = uiStore.t
const siteTitle = computed(() => siteStore.siteInfo.site_name || t('common.siteDefaultName'))
const siteSubtitle = computed(() => siteStore.siteInfo.site_slogan || t('about.subtitle'))
const aboutContent = computed(() => siteStore.siteInfo.about_content || t('about.defaultContent'))

onMounted(() => siteStore.loadSiteInfo())
</script>
