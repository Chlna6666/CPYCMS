<template>
  <div class="min-h-screen flex flex-col bg-[var(--cms-page-bg)] transition-colors duration-300">
    <FrontHeader />

    <main class="flex-1 w-full">
      <router-view v-slot="{ Component, route }">
        <Transition name="route-motion" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </router-view>
    </main>

    <footer class="mt-auto border-t border-[var(--cms-border)] bg-[var(--cms-surface)] transition-colors duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 py-10 lg:py-12 space-y-8">
        <!-- Main 3-Column Grid -->
        <div class="grid grid-cols-1 md:grid-cols-12 gap-8 lg:gap-12">
          <!-- Col 1: Brand & Bio (md:col-span-4) -->
          <div class="md:col-span-4 space-y-3.5">
            <div class="flex items-center gap-2">
              <span class="bg-gradient-to-r from-brand-500 to-indigo-500 bg-clip-text text-xl font-black tracking-tight text-transparent dark:from-brand-400 dark:to-indigo-400">
                {{ siteStore.siteInfo?.site_name || 'CPYCMS' }}
              </span>
            </div>
            <p class="text-xs text-[var(--cms-text-muted)] leading-relaxed line-clamp-3">
              {{ siteStore.siteInfo?.site_slogan || siteStore.siteInfo?.site_description || translate(uiStore.locale, 'home.defaultSlogan') }}
            </p>
            <div v-if="siteStore.siteInfo?.author_name" class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[var(--cms-surface-muted)] border border-[var(--cms-border)] text-xs text-[var(--cms-text-muted)]">
              <User class="w-3.5 h-3.5 text-brand-500 shrink-0" />
              <span>{{ translate(uiStore.locale, 'contact.author') }}{{ siteStore.siteInfo.author_name }}</span>
            </div>
          </div>

          <!-- Col 2: Consolidated Navigation (md:col-span-4) -->
          <div class="md:col-span-4">
            <h3 class="text-sm font-bold text-[var(--cms-text)] mb-4 tracking-wider uppercase">
              {{ translate(uiStore.locale, 'footer.quickNav') }}
            </h3>
            <ul class="grid grid-cols-2 gap-x-4 gap-y-2.5 text-xs text-[var(--cms-text-muted)]">
              <li><router-link to="/" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1.5"><ChevronRight class="w-3 h-3 text-brand-500/70" /> {{ translate(uiStore.locale, 'nav.home') }}</router-link></li>
              <li><router-link to="/articles" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1.5"><ChevronRight class="w-3 h-3 text-brand-500/70" /> {{ translate(uiStore.locale, 'nav.articles') }}</router-link></li>
              <li><router-link to="/portfolio" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1.5"><ChevronRight class="w-3 h-3 text-brand-500/70" /> {{ translate(uiStore.locale, 'nav.portfolio') }}</router-link></li>
              <li><router-link to="/resources" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1.5"><ChevronRight class="w-3 h-3 text-brand-500/70" /> {{ translate(uiStore.locale, 'nav.resources') }}</router-link></li>
              <li><router-link to="/guestbook" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1.5"><ChevronRight class="w-3 h-3 text-brand-500/70" /> {{ translate(uiStore.locale, 'nav.guestbook') }}</router-link></li>
              <li><router-link to="/about" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1.5"><ChevronRight class="w-3 h-3 text-brand-500/70" /> {{ translate(uiStore.locale, 'footer.about') }}</router-link></li>
              <li><router-link to="/contact" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1.5"><ChevronRight class="w-3 h-3 text-brand-500/70" /> {{ translate(uiStore.locale, 'footer.contactUs') }}</router-link></li>
            </ul>
          </div>

          <!-- Col 3: Contact & Support (md:col-span-4) -->
          <div class="md:col-span-4 space-y-3">
            <h3 class="text-sm font-bold text-[var(--cms-text)] mb-4 tracking-wider uppercase">
              {{ translate(uiStore.locale, 'footer.contact') }}
            </h3>
            <div v-if="siteStore.siteInfo?.author_email" class="flex items-center gap-2 text-xs text-[var(--cms-text-muted)]">
              <Mail class="w-4 h-4 text-brand-500 shrink-0" />
              <a :href="`mailto:${siteStore.siteInfo.author_email}`" class="hover:text-brand-500 transition-colors truncate">
                {{ siteStore.siteInfo.author_email }}
              </a>
            </div>
            <p v-if="siteStore.siteInfo?.contact_info || siteStore.siteInfo?.footer_note" class="text-xs text-[var(--cms-text-muted)] leading-relaxed bg-[var(--cms-surface-muted)] p-3 rounded-xl border border-[var(--cms-border)]">
              {{ siteStore.siteInfo?.footer_note || siteStore.siteInfo?.contact_info || translate(uiStore.locale, 'footer.contactFallback') }}
            </p>
          </div>
        </div>

        <!-- Friend Links Section inside Footer -->
        <FriendLinks :title="translate(uiStore.locale, 'footer.friendLinks')" class="pt-4 border-t border-[var(--cms-border)]/60" />
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-[var(--cms-border)] py-5 text-xs text-[var(--cms-text-muted)] bg-[var(--cms-surface)]">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div class="flex flex-col sm:flex-row items-center gap-3">
            <div>{{ translate(uiStore.locale, 'footer.copyright', { year: new Date().getFullYear() }) }}</div>
            <BeianLinks />
          </div>
          <div class="flex items-center gap-4">
            <a href="/admin/login" target="_blank" class="hover:text-brand-500 transition-colors inline-flex items-center gap-1">
              <Lock class="w-3.5 h-3.5" />
              <span>{{ translate(uiStore.locale, 'footer.admin') }}</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { User, Mail, ChevronRight, Lock } from '@lucide/vue'
import { useSiteStore, useUiStore } from '@/stores'
import { translate } from '@/i18n'
import BeianLinks from '@/components/common/BeianLinks.vue'
import FriendLinks from '@/components/common/FriendLinks.vue'
import FrontHeader from './FrontHeader.vue'

const siteStore = useSiteStore()
const uiStore = useUiStore()

onMounted(() => {
  siteStore.loadSiteInfo()
})
</script>

<style>
/* 路由视图切场柔和缓动动画 */
.route-motion-enter-active,
.route-motion-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.route-motion-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.route-motion-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
