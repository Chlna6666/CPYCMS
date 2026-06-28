<template>
  <div class="min-h-screen pb-16">
    <!-- Hero Header Banner -->
    <section class="relative overflow-hidden py-12 sm:py-16 bg-gradient-to-b from-brand-500/10 via-transparent to-transparent border-b border-[var(--cms-border)]">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 text-center space-y-4">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 text-xs font-semibold tracking-wide uppercase">
          <Mail class="w-3.5 h-3.5" />
          <span>{{ t('route.contact') || '联系我们' }}</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-black tracking-tight text-[var(--cms-text)]">
          {{ t('contact.title') }}
        </h1>
        <p class="max-w-2xl mx-auto text-sm text-[var(--cms-text-muted)] leading-relaxed">
          {{ siteInfo.site_slogan || t('contact.subtitle') }}
        </p>
      </div>
    </section>

    <!-- Content Grid -->
    <div class="max-w-5xl mx-auto px-4 sm:px-6 pt-10">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Left Card: Direct Contact Channels -->
        <div class="bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-3xl p-6 sm:p-8 shadow-sm flex flex-col justify-between space-y-6">
          <div class="space-y-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl bg-brand-500/10 text-brand-500 flex items-center justify-center font-bold">
                <Send class="w-5 h-5 text-brand-500" />
              </div>
              <div>
                <h3 class="text-lg font-bold text-[var(--cms-text)]">{{ t('contact.sectionContact') }}</h3>
                <p class="text-xs text-[var(--cms-text-muted)]">{{ t('contact.subtitle') }}</p>
              </div>
            </div>

            <div class="space-y-4 pt-2">
              <!-- Email Row -->
              <div v-if="siteInfo.author_email" class="p-4 rounded-2xl bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] flex items-center justify-between gap-4">
                <div class="space-y-1 min-w-0">
                  <div class="text-xs font-medium text-[var(--cms-text-muted)]">{{ t('contact.email') }}</div>
                  <div class="text-sm font-bold text-[var(--cms-text)] truncate">{{ siteInfo.author_email }}</div>
                </div>
                <a
                  :href="`mailto:${siteInfo.author_email}`"
                  class="px-3.5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 !text-white flex items-center gap-1.5 text-xs font-semibold shadow-sm transition-all shrink-0 active:scale-95"
                >
                  <Mail class="w-4 h-4 shrink-0 !text-white" />
                  <span class="!text-white">写邮件</span>
                </a>
              </div>

              <!-- Author Row -->
              <div v-if="siteInfo.author_name" class="p-4 rounded-2xl bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] flex items-center justify-between gap-4">
                <div class="space-y-1 min-w-0">
                  <div class="text-xs font-medium text-[var(--cms-text-muted)]">{{ t('contact.author') }}</div>
                  <div class="text-sm font-bold text-[var(--cms-text)] truncate">{{ siteInfo.author_name }}</div>
                </div>
                <div class="px-3.5 py-2.5 rounded-xl bg-brand-500/10 text-brand-500 flex items-center gap-1.5 text-xs font-semibold shrink-0 border border-brand-500/20">
                  <User class="w-4 h-4 shrink-0 text-brand-500" />
                  <span>{{ t('identity.admin') || '站长' }}</span>
                </div>
              </div>

              <!-- Contact Info Note -->
              <div class="p-4 rounded-2xl bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] space-y-1.5">
                <div class="text-xs font-medium text-[var(--cms-text-muted)]">{{ t('contact.contactInfo') }}</div>
                <p class="text-xs text-[var(--cms-text)] leading-relaxed">
                  {{ siteInfo.contact_info || t('contact.contactFallback') }}
                </p>
              </div>
            </div>
          </div>

          <!-- Guestbook Button CTA -->
          <div class="pt-4 border-t border-[var(--cms-border)]">
            <router-link
              to="/guestbook"
              class="w-full py-3.5 px-5 rounded-2xl bg-brand-500 hover:bg-brand-600 !text-white text-sm font-bold flex items-center justify-center gap-2 transition-all shadow-md active:scale-98"
            >
              <MessageSquare class="w-4 h-4 !text-white" />
              <span class="!text-white">{{ t('contact.goGuestbook') }}</span>
              <ArrowRight class="w-4 h-4 ml-auto !text-white" />
            </router-link>
          </div>
        </div>

        <!-- Right Card: Site Info & Friend Links -->
        <div class="bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-3xl p-6 sm:p-8 shadow-sm flex flex-col justify-between space-y-6">
          <div class="space-y-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center font-bold">
                <Globe class="w-5 h-5 text-indigo-500" />
              </div>
              <div>
                <h3 class="text-lg font-bold text-[var(--cms-text)]">{{ t('contact.sectionSite') }}</h3>
                <p class="text-xs text-[var(--cms-text-muted)]">{{ t('common.siteDefaultDesc') }}</p>
              </div>
            </div>

            <div class="space-y-3 pt-2">
              <div class="p-4 rounded-2xl bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] space-y-1">
                <span class="text-xs font-medium text-[var(--cms-text-muted)]">{{ t('contact.siteName') }}</span>
                <div class="text-sm font-bold text-[var(--cms-text)]">{{ siteInfo.site_name || t('common.siteDefaultName') }}</div>
              </div>

              <div class="p-4 rounded-2xl bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] space-y-1">
                <span class="text-xs font-medium text-[var(--cms-text-muted)]">{{ t('contact.siteSlogan') }}</span>
                <div class="text-sm font-medium text-[var(--cms-text)] leading-relaxed">
                  {{ siteInfo.site_slogan || t('home.defaultSlogan') }}
                </div>
              </div>

              <div v-if="keywordsList.length > 0" class="p-4 rounded-2xl bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] space-y-2">
                <span class="text-xs font-medium text-[var(--cms-text-muted)]">{{ t('contact.keywords') }}</span>
                <div class="flex flex-wrap gap-1.5">
                  <span v-for="(kw, idx) in keywordsList" :key="idx" class="px-2.5 py-1 rounded-lg bg-brand-500/10 text-brand-600 dark:text-brand-400 text-xs font-semibold">
                    {{ kw }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Friend Links Component integrated inside Contact page -->
          <FriendLinks :title="t('footer.friendLinks')" class="pt-4 border-t border-[var(--cms-border)]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Mail, User, Send, MessageSquare, ArrowRight, Globe } from '@lucide/vue'
import { useSiteStore, useUiStore } from '@/stores'
import FriendLinks from '@/components/common/FriendLinks.vue'

const siteStore = useSiteStore()
const uiStore = useUiStore()
const t = uiStore.t
const siteInfo = computed(() => siteStore.siteInfo)
const keywordsList = computed(() => {
  const kw = siteInfo.value.site_keywords || ''
  return kw.split(/[,，]/).map(s => s.trim()).filter(Boolean)
})

onMounted(() => siteStore.loadSiteInfo())
</script>
