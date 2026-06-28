<template>
  <div class="max-w-5xl mx-auto w-full px-4 py-8 sm:py-12 min-h-screen pb-16">
    <!-- Header Banner -->
    <header class="mb-8 space-y-2">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 text-brand-600 dark:text-brand-400 text-xs font-semibold uppercase tracking-wide">
        <MessageSquare class="w-3.5 h-3.5" />
        <span>{{ t('route.guestbook') || '留言板' }}</span>
      </div>
      <h1 class="text-2xl sm:text-3xl font-black text-[var(--cms-text)] tracking-tight">
        {{ t('guestbook.title') }}
      </h1>
      <p class="text-sm text-[var(--cms-text-muted)]">
        {{ t('guestbook.intro') }}
      </p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start w-full">
      <!-- 留言表单栏 (Mobile: Full width, Desktop: 5 cols) -->
      <div class="lg:col-span-5 w-full">
        <div class="bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-3xl p-6 sm:p-8 shadow-sm space-y-5 w-full">
          <h3 class="text-lg font-bold text-[var(--cms-text)] flex items-center gap-2">
            <Send class="w-4 h-4 text-brand-500" />
            <span>{{ t('guestbook.write') }}</span>
          </h3>

          <div class="space-y-4">
            <div class="space-y-1.5">
              <label class="block text-xs font-medium text-[var(--cms-text-muted)]">{{ t('guestbook.nickname') }}</label>
              <input
                v-model="form.nickname"
                type="text"
                class="h-11 w-full rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface-muted)] px-4 text-sm text-[var(--cms-text)] outline-none transition-all focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
                :placeholder="t('guestbook.nicknamePlaceholder')"
                maxlength="50"
              />
            </div>

            <div class="space-y-1.5">
              <label class="block text-xs font-medium text-[var(--cms-text-muted)]">{{ t('guestbook.email') }}</label>
              <input
                v-model="form.email"
                type="email"
                class="h-11 w-full rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface-muted)] px-4 text-sm text-[var(--cms-text)] outline-none transition-all focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10"
                :placeholder="t('guestbook.emailPlaceholder')"
              />
            </div>

            <div class="space-y-1.5">
              <label class="block text-xs font-medium text-[var(--cms-text-muted)]">{{ t('guestbook.content') }}</label>
              <textarea
                v-model="form.content"
                rows="4"
                class="w-full rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface-muted)] p-4 text-sm text-[var(--cms-text)] outline-none transition-all focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 resize-y"
                :placeholder="t('guestbook.contentPlaceholder')"
                maxlength="1000"
              ></textarea>
              <div class="text-right text-[11px] text-[var(--cms-text-muted)]">
                {{ form.content.length }}/1000
              </div>
            </div>

            <button
              type="button"
              class="w-full py-3.5 px-4 rounded-xl bg-brand-500 hover:bg-brand-600 !text-white text-sm font-bold flex items-center justify-center gap-2 transition-all shadow-sm active:scale-98 disabled:opacity-60 disabled:cursor-not-allowed"
              @click="submitMessage"
              :disabled="submitting"
            >
              <Loader2 v-if="submitting" class="w-4 h-4 animate-spin !text-white" />
              <Send v-else class="w-4 h-4 !text-white" />
              <span class="!text-white">{{ submitting ? t('guestbook.submitting') : t('guestbook.submit') }}</span>
            </button>
          </div>

          <!-- Alert Toast -->
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 translate-y-1"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 translate-y-1"
          >
            <div
              v-if="message"
              class="p-3.5 rounded-xl text-xs font-semibold flex items-center gap-2 shadow-sm"
              :class="messageType === 'success' ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/30' : 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400 border border-red-200 dark:border-red-800/30'"
            >
              <CheckCircle v-if="messageType === 'success'" class="w-4 h-4 shrink-0" />
              <AlertCircle v-else class="w-4 h-4 shrink-0" />
              <span>{{ message }}</span>
            </div>
          </Transition>
        </div>
      </div>

      <!-- 留言列表栏 (Mobile: Full width, Desktop: 7 cols) -->
      <div class="lg:col-span-7 w-full space-y-4">
        <!-- Loading State -->
        <div v-if="loading" class="flex flex-col gap-4 w-full">
          <div v-for="i in 3" :key="i" class="h-32 w-full animate-pulse rounded-3xl border border-[var(--cms-border)] bg-[var(--cms-surface-muted)]"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="messages.length === 0" class="flex flex-col items-center justify-center rounded-3xl border border-dashed border-[var(--cms-border)] py-16 text-[var(--cms-text-muted)] w-full">
          <MessageSquare class="w-10 h-10 mb-3 opacity-20" />
          <p class="text-sm font-medium">{{ t('guestbook.empty') }}</p>
        </div>

        <!-- Message Cards List -->
        <div v-else class="space-y-4 w-full">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="bg-[var(--cms-surface)] border border-[var(--cms-border)] rounded-3xl p-5 sm:p-6 shadow-sm space-y-3 w-full hover:border-brand-500/30 transition-all"
          >
            <div class="flex items-center justify-between gap-3 pb-3 border-b border-[var(--cms-border)]/60">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-500/20 to-indigo-500/20 text-brand-600 dark:text-brand-400 font-bold text-xs flex items-center justify-center shrink-0">
                  {{ msg.nickname ? msg.nickname.charAt(0).toUpperCase() : 'V' }}
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-sm font-bold text-[var(--cms-text)]">{{ msg.nickname }}</span>
                  <span
                    class="px-2 py-0.5 rounded-md text-[11px] font-bold inline-flex items-center gap-1"
                    :class="msg.is_admin_author ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20' : 'bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-500/20'"
                  >
                    <ShieldCheck v-if="msg.is_admin_author" class="w-3 h-3" />
                    <User v-else class="w-3 h-3" />
                    {{ msg.is_admin_author ? t('identity.admin') : t('identity.visitor') }}
                  </span>
                </div>
              </div>

              <div class="text-[11px] text-[var(--cms-text-muted)] flex items-center gap-1 shrink-0">
                <Clock class="w-3 h-3" />
                <span>{{ msg.created_at }}</span>
              </div>
            </div>

            <p class="text-sm text-[var(--cms-text)] leading-relaxed whitespace-pre-wrap pt-1">
              {{ msg.content }}
            </p>

            <!-- Admin Reply Box -->
            <div v-if="msg.reply" class="bg-[var(--cms-surface-muted)] p-4 rounded-2xl border-l-4 border-amber-500 space-y-1 mt-3">
              <div class="text-xs font-bold text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
                <ShieldCheck class="w-3.5 h-3.5" />
                <span>{{ t('guestbook.replyByAdmin') }}</span>
              </div>
              <p class="text-xs text-[var(--cms-text)] leading-relaxed whitespace-pre-wrap">
                {{ msg.reply }}
              </p>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pt-4">
          <button
            class="h-9 w-9 rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)] text-[var(--cms-text)] flex items-center justify-center hover:bg-[var(--cms-surface-muted)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed active:scale-95"
            :disabled="page <= 1"
            @click="changePage(page - 1)"
          >
            <ChevronLeft class="w-4 h-4" />
          </button>

          <button
            v-for="p in totalPages"
            :key="p"
            class="h-9 min-w-9 px-3 rounded-xl border text-xs font-bold transition-all active:scale-95"
            :class="p === page ? 'bg-brand-500 border-brand-500 !text-white shadow-sm' : 'border-[var(--cms-border)] bg-[var(--cms-surface)] text-[var(--cms-text)] hover:bg-[var(--cms-surface-muted)]'"
            @click="changePage(p)"
          >
            <span :class="p === page ? '!text-white' : ''">{{ p }}</span>
          </button>

          <button
            class="h-9 w-9 rounded-xl border border-[var(--cms-border)] bg-[var(--cms-surface)] text-[var(--cms-text)] flex items-center justify-center hover:bg-[var(--cms-surface-muted)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed active:scale-95"
            :disabled="page >= totalPages"
            @click="changePage(page + 1)"
          >
            <ChevronRight class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  MessageSquare, Send, Loader2, User, ShieldCheck, Clock,
  ChevronLeft, ChevronRight, AlertCircle, CheckCircle
} from '@lucide/vue'
import { messageApi, type Message } from '@/services/api'
import { useUiStore } from '@/stores'

const messages = ref<Message[]>([])
const uiStore = useUiStore()
const t = uiStore.t
const loading = ref(true)
const page = ref(1)
const totalPages = ref(1)
const form = ref({ nickname: '', email: '', content: '' })
const submitting = ref(false)
const message = ref('')
const messageType = ref('success')

async function loadMessages() {
  loading.value = true
  try {
    const res = await messageApi.getList({ page: page.value })
    messages.value = res.data?.items || []
    totalPages.value = res.data?.pages || 1
  } catch (e) {
    console.warn('加载留言失败:', e)
  }
  loading.value = false
}

async function submitMessage() {
  if (!form.value.nickname.trim()) {
    message.value = t('guestbook.validationNickname')
    messageType.value = 'danger'
    return
  }
  if (!form.value.content.trim()) {
    message.value = t('guestbook.validationContent')
    messageType.value = 'danger'
    return
  }
  submitting.value = true
  message.value = ''
  try {
    const res = await messageApi.create(form.value)
    message.value = res.msg || t('guestbook.success')
    messageType.value = 'success'
    form.value = { nickname: '', email: '', content: '' }
    loadMessages()
  } catch (e: any) {
    message.value = e.message || '提交失败'
    messageType.value = 'danger'
  }
  submitting.value = false
}

function changePage(p: number) {
  page.value = p
  loadMessages()
}

onMounted(loadMessages)
</script>
