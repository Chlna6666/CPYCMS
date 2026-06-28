<template>
  <section class="mt-5">
    <div class="mb-4 flex items-center justify-between gap-3">
      <div>
        <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100">{{ t('articleComments.title') }}</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ authStore.isLoggedIn ? t('articleComments.adminSubtitle') : t('articleComments.subtitle') }}
        </p>
      </div>
      <span class="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-400">
        {{ comments.length }} {{ t('articleComments.countSuffix') }}
      </span>
    </div>

    <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
      <div class="space-y-4">
        <article
          v-for="comment in comments"
          :key="comment.id"
          class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950"
        >
          <div class="flex flex-wrap items-center gap-2">
            <strong class="text-sm text-slate-900 dark:text-slate-100">{{ comment.nickname }}</strong>
            <span
              class="rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="comment.is_admin_author ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-900 dark:text-slate-400'"
            >
              {{ comment.is_admin_author ? t('identity.admin') : t('identity.visitor') }}
            </span>
            <span v-if="comment.email_masked" class="text-xs text-slate-500 dark:text-slate-400">{{ comment.email_masked }}</span>
            <span v-if="comment.email && authStore.isLoggedIn" class="text-xs text-slate-500 dark:text-slate-400">{{ comment.email }}</span>
            <span class="text-xs text-slate-400">{{ comment.created_at }}</span>
            <span
              v-if="authStore.isLoggedIn"
              class="rounded-full px-2 py-0.5 text-xs"
              :class="comment.is_approved ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300' : 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'"
            >
              {{ comment.is_approved ? t('adminStatus.approved') : t('adminStatus.pending') }}
            </span>
          </div>

          <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700 dark:text-slate-300">
            {{ comment.content }}
          </p>

          <div v-if="comment.reply" class="mt-4 rounded-xl border-l-4 border-brand-500 bg-brand-50 p-3 dark:bg-brand-900/10">
            <div class="mb-1 text-xs font-semibold text-brand-600 dark:text-brand-300">{{ t('articleComments.adminReply') }}</div>
            <p class="whitespace-pre-wrap text-sm leading-6 text-slate-700 dark:text-slate-300">{{ comment.reply }}</p>
          </div>

          <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-500 dark:text-slate-400">
            <span class="rounded-full bg-slate-100 px-2 py-1 dark:bg-slate-900">{{ comment.browser }}</span>
            <span class="rounded-full bg-slate-100 px-2 py-1 dark:bg-slate-900">{{ comment.os_name }}</span>
            <span class="rounded-full bg-slate-100 px-2 py-1 dark:bg-slate-900">{{ comment.device_type }}</span>
          </div>

          <div v-if="authStore.isLoggedIn" class="mt-4 flex flex-wrap items-center gap-2">
            <button
              v-if="!comment.is_approved"
              type="button"
              class="inline-flex h-8 items-center justify-center rounded-lg bg-emerald-500 px-3 text-xs font-semibold text-white transition hover:bg-emerald-600"
              @click="approveComment(comment.id)"
            >
              {{ t('adminAction.approve') }}
            </button>
            <button
              type="button"
              class="inline-flex h-8 items-center justify-center rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 transition hover:border-brand-500 hover:text-brand-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300"
              @click="openReply(comment)"
            >
              {{ comment.is_replied ? t('adminAction.editReply') : t('adminAction.reply') }}
            </button>
            <button
              type="button"
              class="inline-flex h-8 items-center justify-center rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 transition hover:border-rose-500 hover:text-rose-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300"
              @click="deleteComment(comment.id)"
            >
              {{ t('adminAction.delete') }}
            </button>
          </div>
        </article>

        <div v-if="!comments.length" class="rounded-2xl border border-dashed border-slate-300 px-4 py-10 text-center text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
          {{ t('articleComments.empty') }}
        </div>
      </div>

      <aside class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-950">
        <h4 class="text-base font-semibold text-slate-900 dark:text-slate-100">
          {{ authStore.isLoggedIn ? t('articleComments.adminFormTitle') : t('articleComments.formTitle') }}
        </h4>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ authStore.isLoggedIn ? t('articleComments.adminFormHint') : t('articleComments.formHint') }}
        </p>

        <form class="mt-4 space-y-3" @submit.prevent="submitComment">
          <div v-if="!authStore.isLoggedIn">
            <label class="mb-1 block text-sm text-slate-600 dark:text-slate-300">{{ t('articleComments.nickname') }}</label>
            <input v-model="form.nickname" type="text" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-cyan-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100" :placeholder="t('articleComments.nicknamePlaceholder')" />
          </div>
          <div v-if="!authStore.isLoggedIn">
            <label class="mb-1 block text-sm text-slate-600 dark:text-slate-300">{{ t('articleComments.email') }}</label>
            <input v-model="form.email" type="email" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-cyan-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100" :placeholder="t('articleComments.emailPlaceholder')" />
          </div>
          <div>
            <label class="mb-1 block text-sm text-slate-600 dark:text-slate-300">{{ t('articleComments.content') }}</label>
            <textarea v-model="form.content" rows="5" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-cyan-500 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100" :placeholder="t('articleComments.contentPlaceholder')" />
          </div>

          <button
            type="submit"
            class="inline-flex h-11 items-center justify-center rounded-xl bg-cyan-600 px-4 text-sm font-semibold text-white transition hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="submitting"
          >
            {{ submitting ? t('articleComments.submitting') : (authStore.isLoggedIn ? t('articleComments.adminSubmit') : t('articleComments.submit')) }}
          </button>
        </form>

        <div v-if="message" class="mt-4 rounded-xl px-3 py-2 text-sm" :class="messageType === 'success' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300' : 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'">
          {{ message }}
        </div>
      </aside>
    </div>

    <Transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition duration-150 ease-in" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="showReply" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showReply = false"></div>
        <div class="relative flex w-full max-w-lg flex-col rounded-2xl bg-white shadow-2xl dark:bg-slate-950">
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
            <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">{{ t('articleComments.replyTitle') }}</h3>
            <button class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300" @click="showReply = false">
              <X class="h-5 w-5" />
            </button>
          </div>
          <div class="px-6 py-5">
            <div class="mb-4 rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm dark:border-slate-800/60 dark:bg-slate-900/50">
              <span class="font-semibold text-slate-700 dark:text-slate-300">{{ replyTarget.nickname }}：</span>
              <span class="text-slate-600 dark:text-slate-400">{{ replyTarget.content }}</span>
            </div>
            <textarea
              v-model="replyContent"
              class="w-full resize-none rounded-xl border border-slate-200 bg-transparent p-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              rows="5"
              :placeholder="t('articleComments.replyPlaceholder')"
            ></textarea>
          </div>
          <div class="flex items-center justify-end gap-3 border-t border-slate-100 px-6 py-4 dark:border-slate-800">
            <button class="h-10 rounded-xl px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" @click="showReply = false">
              {{ t('adminAction.cancel') }}
            </button>
            <button
              class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white transition-all hover:bg-brand-600 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="!replyContent.trim()"
              @click="saveReply"
            >
              {{ t('adminAction.sendReply') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { commentApi, type ArticleComment } from '@/services/api'
import { useAuthStore, useUiStore } from '@/stores'
import { buildClientFingerprint } from '@/utils/clientFingerprint'
import { X } from '@lucide/vue'

const props = defineProps<{ slug: string }>()

const authStore = useAuthStore()
const uiStore = useUiStore()
const t = uiStore.t

const comments = ref<ArticleComment[]>([])
const submitting = ref(false)
const showReply = ref(false)
const replyTarget = ref<ArticleComment>({} as ArticleComment)
const replyContent = ref('')
const message = ref('')
const messageType = ref<'success' | 'danger'>('success')
const form = reactive({
  nickname: '',
  email: '',
  content: ''
})

async function loadComments() {
  try {
    const res = await commentApi.getList(props.slug, { page: 1 })
    comments.value = res.data?.items || []
  } catch (error) {
    console.warn(error)
  }
}

function setMessage(type: 'success' | 'danger', text: string) {
  messageType.value = type
  message.value = text
}

async function approveComment(id: number) {
  try {
    await commentApi.approve(id)
    await loadComments()
  } catch (error: any) {
    setMessage('danger', error?.message || t('common.networkError'))
  }
}

function openReply(comment: ArticleComment) {
  replyTarget.value = comment
  replyContent.value = comment.reply || ''
  showReply.value = true
}

async function saveReply() {
  if (!replyContent.value.trim()) return
  try {
    await commentApi.reply(replyTarget.value.id, { reply: replyContent.value.trim() })
    showReply.value = false
    setMessage('success', t('articleComments.replySaved'))
    await loadComments()
  } catch (error: any) {
    setMessage('danger', error?.message || t('common.networkError'))
  }
}

async function deleteComment(id: number) {
  if (!confirm(t('adminComment.deleteConfirm'))) return
  try {
    await commentApi.delete(id)
    await loadComments()
  } catch (error: any) {
    setMessage('danger', error?.message || t('common.networkError'))
  }
}

async function submitComment() {
  const adminComment = authStore.isLoggedIn

  if (!adminComment && !form.nickname.trim()) {
    setMessage('danger', t('articleComments.validationNickname'))
    return
  }
  if (!adminComment && !form.email.trim()) {
    setMessage('danger', t('articleComments.validationEmail'))
    return
  }
  if (!form.content.trim()) {
    setMessage('danger', t('articleComments.validationContent'))
    return
  }

  submitting.value = true
  message.value = ''
  try {
    const payload = adminComment
      ? { content: form.content.trim() }
      : {
          nickname: form.nickname.trim(),
          email: form.email.trim(),
          content: form.content.trim(),
          client_fingerprint: await buildClientFingerprint()
        }
    const res = await commentApi.create(props.slug, payload)
    setMessage('success', res.msg || (adminComment ? t('articleComments.adminSuccess') : t('articleComments.success')))
    form.content = ''
    await loadComments()
  } catch (error: any) {
    setMessage('danger', error?.message || t('common.networkError'))
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await authStore.checkAuth()
  await loadComments()
})
</script>
