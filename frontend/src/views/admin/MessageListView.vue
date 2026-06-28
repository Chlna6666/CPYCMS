<!--
  CPYCMS - 后台留言管理
-->
<template>
  <div class="w-full pb-8">

    <header
      class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      v-motion
      :initial="{ opacity: 0, y: -20 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
          {{ t('admin.messages') || '留言管理' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          查看和回复来自访客的留言与反馈
        </p>
      </div>
    </header>

    <div
      class="mb-6 inline-flex rounded-xl bg-slate-100 p-1 dark:bg-slate-900"
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :enter="{ opacity: 1, y: 0, transition: { delay: 50 } }"
    >
      <button
        class="flex h-9 items-center justify-center rounded-lg px-5 text-sm font-medium transition-all"
        :class="filter === 'all' ? 'bg-white text-slate-900 shadow-sm dark:bg-slate-800 dark:text-white' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
        @click="setFilter('all')"
      >
        {{ t('adminStatus.all') || '全部留言' }}
      </button>
      <button
        class="flex h-9 items-center justify-center rounded-lg px-5 text-sm font-medium transition-all"
        :class="filter === 'pending' ? 'bg-white text-brand-600 shadow-sm dark:bg-slate-800 dark:text-brand-400' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
        @click="setFilter('pending')"
      >
        {{ t('adminStatus.pending') || '待审核' }}
      </button>
      <button
        class="flex h-9 items-center justify-center rounded-lg px-5 text-sm font-medium transition-all"
        :class="filter === 'approved' ? 'bg-white text-emerald-600 shadow-sm dark:bg-slate-800 dark:text-emerald-400' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
        @click="setFilter('approved')"
      >
        {{ t('adminStatus.approved') || '已审核' }}
      </button>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-500"></div>
    </div>

    <div v-else class="flex flex-col gap-4">
      <div
        v-for="(msg, index) in messages"
        :key="msg.id"
        class="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-950"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 100 + index * 30 } }"
      >
        <div class="mb-3 flex flex-wrap items-start justify-between gap-3">
          <div class="flex flex-col gap-1.5">
            <div class="flex items-center gap-2">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-brand-50 text-brand-600 dark:bg-brand-900/20 dark:text-brand-400">
                <User class="h-4 w-4" />
              </div>
              <span class="font-bold text-slate-900 dark:text-slate-100">{{ msg.nickname }}</span>
              <span
                class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold"
                :class="msg.is_admin_author ? 'bg-brand-50 text-brand-700 dark:bg-brand-900/30 dark:text-brand-300' : 'bg-slate-100 text-slate-500 dark:bg-slate-900 dark:text-slate-400'"
              >
                {{ msg.is_admin_author ? t('identity.admin') : t('identity.visitor') }}
              </span>
              <span class="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                <Mail class="h-3.5 w-3.5" />
                {{ msg.email || t('adminStatus.noEmail') || '未留邮箱' }}
              </span>
            </div>
            <div class="flex items-center gap-1 text-xs text-slate-400 dark:text-slate-500">
              <Clock class="h-3.5 w-3.5" />
              {{ msg.created_at }}
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span
              v-if="!msg.is_approved"
              class="inline-flex items-center gap-1 rounded-md bg-amber-50 px-2 py-1 text-xs font-medium text-amber-600 dark:bg-amber-900/20 dark:text-amber-400"
            >
              <ShieldAlert class="h-3.5 w-3.5" />
              {{ t('adminStatus.pending') || '待审核' }}
            </span>
            <span
              v-if="msg.is_replied"
              class="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400"
            >
              <CheckCircle class="h-3.5 w-3.5" />
              {{ t('adminStatus.replied') || '已回复' }}
            </span>
          </div>
        </div>

        <p class="mb-4 text-sm leading-relaxed text-slate-700 dark:text-slate-300">
          {{ msg.content }}
        </p>

        <div
          v-if="msg.reply"
          class="mb-4 rounded-xl border-l-4 border-brand-500 bg-brand-50 p-4 dark:border-brand-500 dark:bg-brand-900/10"
        >
          <div class="mb-1 flex items-center gap-1.5 text-xs font-bold text-brand-600 dark:text-brand-400">
            <MessageSquare class="h-3.5 w-3.5" />
            {{ t('adminMessage.adminReplyPrefix') || '管理员回复：' }}
          </div>
          <p class="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
            {{ msg.reply }}
          </p>
        </div>

        <div class="mt-auto flex flex-wrap items-center gap-2 pt-2">
          <button
            v-if="!msg.is_approved"
            class="inline-flex h-8 items-center justify-center gap-1.5 rounded-lg bg-emerald-500 px-3 text-xs font-semibold text-white transition-all hover:bg-emerald-600 active:scale-95"
            @click="approve(msg.id)"
          >
            <Check class="h-3.5 w-3.5" />
            {{ t('adminAction.approve') || '通过审核' }}
          </button>

          <button
            class="inline-flex h-8 items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 transition-colors hover:border-brand-500 hover:bg-brand-50 hover:text-brand-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300 dark:hover:border-brand-500 dark:hover:bg-brand-900/20 dark:hover:text-brand-400 active:scale-95"
            @click="openReply(msg)"
          >
            <Reply class="h-3.5 w-3.5" />
            {{ msg.is_replied ? t('adminAction.editReply') || '修改回复' : t('adminAction.reply') || '回复' }}
          </button>

          <button
            class="inline-flex h-8 items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 transition-colors hover:border-red-500 hover:bg-red-50 hover:text-red-600 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-300 dark:hover:border-red-500 dark:hover:bg-red-900/20 dark:hover:text-red-400 active:scale-95"
            @click="deleteMsg(msg.id)"
          >
            <Trash2 class="h-3.5 w-3.5" />
            {{ t('adminAction.delete') || '删除' }}
          </button>
        </div>
      </div>

      <div v-if="messages.length === 0" class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-white py-24 dark:border-slate-800 dark:bg-slate-950">
        <Inbox class="mb-4 h-12 w-12 text-slate-300 dark:text-slate-600" />
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ t('adminEmpty.messages') || '暂无符合条件的留言' }}</p>
      </div>
    </div>

    <div v-if="totalPages > 1 && !loading" class="mt-8 flex justify-center gap-2">
      <button
        class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 disabled:opacity-30 dark:border-slate-800 dark:hover:bg-slate-900"
        :disabled="page <= 1"
        @click="changePage(page - 1)"
      >
        <ChevronLeft class="h-4 w-4" />
      </button>
      <button
        v-for="p in totalPages"
        :key="p"
        class="h-9 min-w-[36px] rounded-xl border px-3 text-sm font-medium transition-colors"
        :class="p === page ? 'border-brand-500 bg-brand-500 text-white' : 'border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-800 dark:text-slate-400 dark:hover:bg-slate-900'"
        @click="changePage(p)"
      >
        {{ p }}
      </button>
      <button
        class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-slate-500 transition-colors hover:bg-slate-50 disabled:opacity-30 dark:border-slate-800 dark:hover:bg-slate-900"
        :disabled="page >= totalPages"
        @click="changePage(page + 1)"
      >
        <ChevronRight class="h-4 w-4" />
      </button>
    </div>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showReply" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
        <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="showReply = false"></div>

        <div class="relative flex w-full max-w-lg flex-col rounded-2xl bg-white shadow-2xl dark:bg-slate-950">
          <div class="flex items-center justify-between border-b border-slate-100 px-6 py-4 dark:border-slate-800">
            <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">{{ t('adminMessage.replyTitle') || '回复留言' }}</h3>
            <button class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800 dark:hover:text-slate-300" @click="showReply = false">
              <X class="h-5 w-5" />
            </button>
          </div>

          <div class="px-6 py-5">
            <div class="mb-4 rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm dark:border-slate-800/60 dark:bg-slate-900/50">
              <span class="font-semibold text-slate-700 dark:text-slate-300">{{ t('adminMessage.fromPrefix') || '来自' }} {{ replyTarget.nickname }}：</span>
              <span class="text-slate-600 dark:text-slate-400">{{ replyTarget.content }}</span>
            </div>

            <textarea
              v-model="replyContent"
              class="w-full custom-scrollbar resize-none rounded-xl border border-slate-200 bg-transparent p-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              rows="5"
              :placeholder="t('adminMessage.replyPlaceholder') || '请输入回复内容...'"
            ></textarea>
          </div>

          <div class="flex items-center justify-end gap-3 border-t border-slate-100 px-6 py-4 dark:border-slate-800">
            <button
              class="h-10 rounded-xl px-4 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800 active:scale-95"
              @click="showReply = false"
            >
              {{ t('adminAction.cancel') || '取消' }}
            </button>
            <button
              class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white transition-all hover:bg-brand-600 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
              @click="doReply"
              :disabled="!replyContent.trim()"
            >
              <Send class="h-4 w-4" />
              {{ t('adminAction.sendReply') || '发送回复' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { messageApi } from '@/services/api'
import type { Message } from '@/services/api'
import { useUiStore } from '@/stores'

// 引入高颜值 Lucide 图标
import {
  User, Mail, Clock, MessageSquare, Reply, Trash2,
  Check, CheckCircle, ShieldAlert, Inbox, X, Send,
  ChevronLeft, ChevronRight
} from '@lucide/vue'

const uiStore = useUiStore()
const t = uiStore.t
const messages = ref<Message[]>([])
const loading = ref<boolean>(true)
const page = ref<number>(1)
const totalPages = ref<number>(1)
const filter = ref<string>('all')

const showReply = ref<boolean>(false)
const replyTarget = ref<Message>({} as Message)
const replyContent = ref<string>('')

async function loadData(): Promise<void> {
  loading.value = true
  const params: Record<string, any> = { page: page.value }
  if (filter.value !== 'all') params.status = filter.value

  try {
    const res = await messageApi.adminGetList(params)
    messages.value = res.data?.items || []
    totalPages.value = res.data?.pages || 1
  } catch (e) {
    console.warn(e)
  }
  loading.value = false
}

function setFilter(f: string): void {
  filter.value = f
  page.value = 1
  loadData()
}

function changePage(p: number): void {
  page.value = p
  loadData()
}

async function approve(id: number): Promise<void> {
  try {
    await messageApi.approve(id)
    loadData()
  } catch (e: any) {
    alert(e.message)
  }
}

function openReply(msg: Message): void {
  replyTarget.value = msg
  replyContent.value = msg.reply || ''
  showReply.value = true
}

async function doReply(): Promise<void> {
  if (!replyContent.value.trim()) return
  try {
    await messageApi.reply(replyTarget.value.id, { reply: replyContent.value })
    showReply.value = false
    loadData()
  } catch (e: any) {
    alert(e.message)
  }
}

async function deleteMsg(id: number): Promise<void> {
  if (!confirm(t('adminMessage.deleteConfirm') || '确定要删除这条留言吗？此操作不可恢复。')) return
  try {
    await messageApi.delete(id)
    // 删空当前页跳转上一页逻辑保护
    if (messages.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    loadData()
  } catch (e: any) {
    alert(e.message)
  }
}

onMounted(loadData)
</script>

<style scoped>
/* 自定义优美滚动条 */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-200);
  border-radius: 20px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-700);
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-300);
}
.dark .custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: var(--color-slate-600);
}
</style>
