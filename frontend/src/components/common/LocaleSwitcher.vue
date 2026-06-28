<template>
  <div class="relative inline-block text-left select-none" ref="dropdownRef">
    <button
      type="button"
      @click.stop="toggleDropdown"
      class="inline-flex items-center justify-between font-medium rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)] text-[var(--cms-text)] hover:border-brand-500 hover:text-brand-500 hover:shadow-md transition-all duration-200 cursor-pointer active:scale-95 group"
      :class="sizeClasses.button"
    >
      <span class="truncate tracking-wide">{{ currentItem ? t(currentItem.labelKey) : '' }}</span>

      <svg
        class="text-[var(--cms-text-muted)] group-hover:text-brand-500 transition-transform duration-300 shrink-0"
        :class="[{ 'rotate-180': isOpen }, sizeClasses.icon]"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform scale-95 opacity-0 -translate-y-2"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 -translate-y-2"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)]/90 backdrop-blur-md shadow-xl z-50 overflow-hidden p-1 min-w-[120px]"
        :class="sizeClasses.menu"
      >
        <button
          v-for="item in AVAILABLE_LOCALES"
          :key="item.code"
          type="button"
          @click="selectLocale(item.code)"
          class="w-full flex items-center justify-between text-left rounded-lg transition-colors duration-150 cursor-pointer"
          :class="[
            modelValue === item.code
              ? 'bg-brand-500/10 text-brand-500 font-semibold'
              : 'text-[var(--cms-text-muted)] hover:bg-[var(--cms-surface-muted)] hover:text-[var(--cms-text)]',
            sizeClasses.item
          ]"
        >
          <span class="truncate">{{ t(item.labelKey) }}</span>

          <svg
            v-if="modelValue === item.code"
            class="text-brand-500 shrink-0"
            :class="sizeClasses.checkIcon"
            fill="none"
            stroke="currentColor"
            stroke-width="3"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { AVAILABLE_LOCALES } from '@/i18n'
import type { LanguageCode } from '@/i18n'
import { useUiStore } from '@/stores'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'md',
    validator: (value: string) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'change'])
const uiStore = useUiStore()
const t = uiStore.t

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

// 动态匹配语言项
const currentItem = computed(() => AVAILABLE_LOCALES.find(l => l.code === props.modelValue) || AVAILABLE_LOCALES[0])

// 核心多规格尺寸控制样式映射表
const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return {
        button: 'px-2.5 py-1.5 text-xs rounded-lg min-w-[95px] gap-1.5 shadow-xs',
        icon: 'w-3 h-3',
        menu: 'min-w-[105px]',
        item: 'px-2 py-1.5 text-xs',
        checkIcon: 'w-3.5 h-3.5'
      }
    case 'lg':
      return {
        button: 'px-4.5 py-2.5 text-base rounded-2xl min-w-[135px] gap-3.5 shadow-md',
        icon: 'w-4 h-4',
        menu: 'min-w-[140px]',
        item: 'px-4 py-2.5 text-base',
        checkIcon: 'w-5 h-5'
      }
    case 'md':
    default:
      return {
        button: 'px-3.5 py-2 text-sm rounded-xl min-w-[115px] gap-2.5 shadow-sm',
        icon: 'w-3.5 h-3.5',
        menu: 'min-w-[125px]',
        item: 'px-3 py-2 text-sm',
        checkIcon: 'w-4 h-4'
      }
  }
})

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const selectLocale = (code: LanguageCode) => {
  emit('update:modelValue', code)
  emit('change', code)
  isOpen.value = false
}

// 点击外部区域自动收起下拉框
const closeDropdown = (e: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  window.removeEventListener('click', closeDropdown)
})
</script>
