<template>
  <div class="relative w-full h-[70dvh] overflow-hidden bg-slate-50 transition-colors duration-300 dark:bg-[#020617]">

    <div class="absolute inset-x-0 bottom-0 top-12 h-full bg-gradient-to-t from-brand-100/40 via-indigo-50/20 to-transparent dark:from-brand-900/20 dark:via-transparent dark:to-transparent"></div>

    <div v-if="loading" class="absolute inset-0 flex flex-col items-center justify-center py-20">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-500"></div>
    </div>

    <div v-else class="h-full relative">
      <Transition name="fade-slide" mode="out-in">
        <div
          v-if="currentSlide"
          :key="activeSlide"
          class="absolute inset-0 z-10 h-full w-full px-4 flex flex-col items-center justify-center space-y-6 sm:space-y-8"
        >
          <div v-if="currentSlide.image" class="absolute inset-0 -z-10 h-full w-full overflow-hidden">
            <img
              :src="currentSlide.image"
              :alt="currentSlide.title"
              class="h-full w-full object-cover opacity-20 dark:opacity-30 scale-105"
            />
            <div class="absolute inset-0 bg-slate-50/50 dark:bg-slate-900/50 mix-blend-overlay"></div>
          </div>
          <div class="space-y-6 text-center max-w-4xl mx-auto">
            <h2 class="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-slate-50 md:text-5xl lg:text-6xl leading-tight drop-shadow-sm">
              {{ currentSlide.title }}
            </h2>
            
            <div v-if="currentSlide.badge" class="flex justify-center">
              <span class="inline-flex items-center rounded-full border border-brand-500/20 bg-white/60 px-4 py-1.5 text-sm font-bold text-brand-600 backdrop-blur-md shadow-sm transition-colors dark:border-brand-400/20 dark:bg-slate-900/50 dark:text-brand-400">
                {{ currentSlide.badge || siteName }}
              </span>
            </div>
            
            <p class="text-lg text-slate-700 dark:text-slate-300 max-w-2xl mx-auto leading-relaxed drop-shadow-sm">
              {{ currentSlide.subtitle }}
            </p>
          </div>

          <div class="flex flex-col gap-3 pt-4 sm:flex-row sm:items-center sm:justify-center sm:gap-4">
            <button
              v-if="currentSlide.link"
              @click="router.push(currentSlide.link)"
              class="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-brand-500 px-8 text-sm font-semibold text-white transition-colors hover:bg-brand-600 disabled:opacity-60 disabled:pointer-events-none active:scale-95 dark:text-white"
            >
              {{ currentSlide.btnText }}
            </button>

          </div>
        </div>
      </Transition>
    </div>

    <div v-if="slides.length > 1" class="absolute inset-x-0 bottom-8 z-20 flex justify-center">
      <div class="inline-flex items-center gap-2 rounded-full bg-white/40 p-1.5 backdrop-blur-md shadow-sm border border-slate-200/50 dark:bg-slate-900/40 dark:border-slate-800/50">
        <button
          v-for="(_, index) in slides"
          :key="index"
          class="h-2 rounded-full transition-all duration-300"
          :class="index === activeSlide ? 'w-6 bg-brand-500 shadow-sm' : 'w-2 bg-slate-400/60 hover:bg-slate-500 dark:bg-slate-600 dark:hover:bg-slate-500'"
          @click="$emit('change-slide', index)"
          :aria-label="'切换到第 ' + (index + 1) + ' 张幻灯片'"
        />
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '@/stores'

type HeroSlide = {
  badge?: string
  title: string
  subtitle: string
  link?: string
  btnText: string
  image?: string
}

const props = defineProps<{
  loading?: boolean
  slides: HeroSlide[]
  activeSlide: number
  siteName: string
}>()

defineEmits(['change-slide'])

const router = useRouter()
const uiStore = useUiStore()
const t = uiStore.t

// 直接计算当前需要展示的幻灯片，配合 Transition mode="out-in" 使用
const currentSlide = computed(() => props.slides[props.activeSlide])
</script>

<style scoped>
/* 更加平滑的进场淡入淡出动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(15px) scale(0.98);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-15px) scale(1.02);
}
</style>