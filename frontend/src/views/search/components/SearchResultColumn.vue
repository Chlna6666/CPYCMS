<template>
  <section class="flex flex-col">
    <div class="mb-3 flex items-center justify-between px-1">
      <h2 class="text-sm font-semibold text-slate-800 dark:text-slate-200">{{ title }}</h2>
      <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500 dark:bg-slate-800 dark:text-slate-400">
        {{ count }}
      </span>
    </div>

    <div v-if="loading" class="flex flex-col gap-3">
      <div class="h-24 w-full animate-pulse rounded-xl border border-slate-100 bg-slate-50/50 dark:border-slate-800/50 dark:bg-slate-900/50"></div>
      <div class="h-24 w-full animate-pulse rounded-xl border border-slate-100 bg-slate-50/50 dark:border-slate-800/50 dark:bg-slate-900/50"></div>
    </div>

    <div v-else-if="count === 0" class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 py-12 dark:border-slate-800">
      <span class="text-sm text-slate-400 dark:text-slate-500">{{ emptyText }}</span>
    </div>

    <div v-else class="flex flex-col gap-3">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  count: number
  loading: boolean
  emptyText: string
}>()
</script>