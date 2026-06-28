<!--
  CPYCMS - 后台个人信息管理
  修改昵称、邮箱、简介、密码
-->
<template>
  <div class="w-full pb-12">
    <header
      class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      v-motion
      :initial="{ opacity: 0, y: -20 }"
      :enter="{ opacity: 1, y: 0 }"
    >
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-50">
          {{ t('admin.profile') || '个人信息' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          管理您的账户基础信息与安全凭证
        </p>
      </div>
    </header>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">

      <section
        class="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 100 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <User class="h-5 w-5 text-brand-500" />
          {{ t('adminProfile.basicInfo') || '基本资料' }}
        </h2>

        <div class="flex flex-1 flex-col space-y-5">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminProfile.username') || '登录账号' }}
            </label>
            <div class="relative">
              <input
                :value="authStore.user?.username"
                class="h-11 w-full cursor-not-allowed rounded-xl border border-slate-200 bg-slate-50 pl-4 pr-10 text-sm text-slate-500 outline-none dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-400"
                disabled
              />
              <Lock class="absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            </div>
            <p class="mt-1.5 flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
              <Info class="h-3.5 w-3.5" />
              {{ t('adminProfile.usernameLocked') || '账号名称作为唯一凭证，不可修改' }}
            </p>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminProfile.nickname') || '显示昵称' }}
            </label>
            <input
              v-model="profile.nickname"
              class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              placeholder="怎么称呼您？"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminProfile.email') || '联系邮箱' }}
            </label>
            <input
              v-model="profile.email"
              type="email"
              class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              placeholder="admin@example.com"
            />
          </div>

          <div class="flex-1">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminProfile.bio') || '个人简介' }}
            </label>
            <textarea
              v-model="profile.bio"
              class="min-h-[100px] w-full custom-scrollbar resize-y rounded-xl border border-slate-200 bg-transparent p-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              rows="3"
              placeholder="简单介绍一下自己吧..."
            ></textarea>
          </div>

          <div
            v-if="profileMsg"
            class="flex items-center gap-2 rounded-lg p-3 text-sm font-medium"
            :class="profileOk ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400'"
          >
            <CheckCircle v-if="profileOk" class="h-4.5 w-4.5 shrink-0" />
            <AlertCircle v-else class="h-4.5 w-4.5 shrink-0" />
            {{ profileMsg }}
          </div>

          <div class="mt-2 flex justify-end">
            <button
              class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-600 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
              @click="saveProfile"
              :disabled="saving"
            >
              <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
              <Save v-else class="h-4 w-4" />
              {{ saving ? t('adminAction.saving') || '保存中...' : t('adminAction.saveProfile') || '保存基本信息' }}
            </button>
          </div>
        </div>
      </section>

      <section
        class="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 150 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <ShieldAlert class="h-5 w-5 text-indigo-500" />
          {{ t('adminProfile.passwordTitle') || '安全设置' }}
        </h2>

        <div class="flex flex-1 flex-col space-y-5">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminProfile.currentPassword') || '当前密码' }}
            </label>
            <input
              v-model="pwdForm.old_password"
              type="password"
              class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminProfile.newPassword') || '新密码' }}
            </label>
            <input
              v-model="pwdForm.new_password"
              type="password"
              class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
              :placeholder="t('adminProfile.newPasswordPlaceholder') || '最少 6 个字符'"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('adminProfile.confirmPassword') || '确认新密码' }}
            </label>
            <input
              v-model="pwdConfirm"
              type="password"
              class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100"
            />
          </div>

          <div
            v-if="pwdMsg"
            class="flex items-center gap-2 rounded-lg p-3 text-sm font-medium"
            :class="pwdOk ? 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-red-50 text-red-600 dark:bg-red-900/20 dark:text-red-400'"
          >
            <CheckCircle v-if="pwdOk" class="h-4.5 w-4.5 shrink-0" />
            <AlertCircle v-else class="h-4.5 w-4.5 shrink-0" />
            {{ pwdMsg }}
          </div>

          <div class="mt-auto pt-4 flex justify-end">
            <button
              class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 text-sm font-semibold text-white transition-all hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-slate-200 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60"
              @click="changePassword"
              :disabled="changing"
            >
              <Loader2 v-if="changing" class="h-4 w-4 animate-spin" />
              <ShieldCheck v-else class="h-4 w-4" />
              {{ changing ? t('adminAction.changing') || '提交中...' : t('adminAction.changePassword') || '更新密码' }}
            </button>
          </div>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores'
import { authApi } from '@/services/api'
import { useUiStore } from '@/stores'

// 引入全套高颜值 Lucide 图标
import {
  User, Lock, Save, ShieldAlert, ShieldCheck,
  Info, CheckCircle, AlertCircle, Loader2
} from '@lucide/vue'

const authStore = useAuthStore()
const uiStore = useUiStore()
const t = uiStore.t

const saving = ref<boolean>(false)
const changing = ref<boolean>(false)
const profileMsg = ref<string>('')
const profileOk = ref<boolean>(true)
const pwdMsg = ref<string>('')
const pwdOk = ref<boolean>(true)

const profile = ref<{ nickname: string; email: string; bio: string }>({ nickname: '', email: '', bio: '' })
const pwdForm = ref<{ old_password: string; new_password: string }>({ old_password: '', new_password: '' })
const pwdConfirm = ref<string>('')

onMounted(async () => {
  await authStore.checkAuth()
  if (authStore.user) {
    profile.value.nickname = authStore.user.nickname || ''
    profile.value.email = authStore.user.email || ''
    profile.value.bio = authStore.user.bio || ''
  }
})

async function saveProfile(): Promise<void> {
  saving.value = true
  profileMsg.value = ''
  try {
    const res = await authApi.updateProfile(profile.value)
    profileMsg.value = res.msg || t('adminProfile.saved') || '基本信息更新成功'
    profileOk.value = true
  } catch (e: any) {
    profileMsg.value = e.message
    profileOk.value = false
  }
  saving.value = false
}

async function changePassword(): Promise<void> {
  pwdMsg.value = ''

  if (!pwdForm.value.old_password || !pwdForm.value.new_password) {
    pwdMsg.value = t('adminProfile.passwordRequired') || '请填写当前密码和新密码'
    pwdOk.value = false
    return
  }
  if (pwdForm.value.new_password.length < 6) {
    pwdMsg.value = t('adminProfile.passwordTooShort') || '新密码长度至少需要 6 个字符'
    pwdOk.value = false
    return
  }
  if (pwdForm.value.new_password !== pwdConfirm.value) {
    pwdMsg.value = t('adminProfile.passwordMismatch') || '两次输入的新密码不一致'
    pwdOk.value = false
    return
  }

  changing.value = true
  try {
    const res = await authApi.changePassword(pwdForm.value)
    pwdMsg.value = res.msg || t('adminProfile.passwordChanged') || '密码更新成功，请牢记新密码'
    pwdOk.value = true
    pwdForm.value = { old_password: '', new_password: '' }
    pwdConfirm.value = ''
  } catch (e: any) {
    pwdMsg.value = e.message
    pwdOk.value = false
  }
  changing.value = false
}
</script>

<style scoped>
/* 自定义优美滚动条 (供 textarea 使用) */
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