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
          {{ t('admin.settings') || '站点设置' }}
        </h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          管理站点的全局配置、外观主题和核心元数据
        </p>
      </div>

      <button
        class="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-brand-500 px-6 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-600 hover:shadow disabled:cursor-not-allowed disabled:opacity-60 active:scale-95"
        @click="saveSettings"
        :disabled="saving"
      >
        <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
        <Save v-else class="h-4 w-4" />
        {{ saving ? t('adminAction.saving') || '保存中...' : t('adminAction.saveSettings') || '保存所有设置' }}
      </button>
    </header>

    <transition name="toast">
      <div
        v-if="message"
        class="mb-6 flex items-center gap-3 rounded-xl p-4 text-sm font-medium shadow-sm"
        :class="msgType === 'success' ? 'bg-emerald-50 text-emerald-600 border border-emerald-100 dark:bg-emerald-900/20 dark:border-emerald-800/30 dark:text-emerald-400' : 'bg-red-50 text-red-600 border border-red-100 dark:bg-red-900/20 dark:border-red-800/30 dark:text-red-400'"
      >
        <CheckCircle v-if="msgType === 'success'" class="h-5 w-5 shrink-0" />
        <AlertCircle v-else class="h-5 w-5 shrink-0" />
        {{ message }}
      </div>
    </transition>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-brand-500"></div>
    </div>

    <div v-else class="flex flex-col gap-6">

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 50 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <Settings class="h-5 w-5 text-brand-500" />
          {{ t('adminSettings.basicInfo') || '基础信息' }}
        </h2>
        <div class="grid grid-cols-1 gap-5 md:grid-cols-12">
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.siteName') || '站点名称' }}</label>
            <input v-model="form.site_name" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.siteSlogan') || '站点标语 (Slogan)' }}</label>
            <input v-model="form.site_slogan" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>

          <div class="md:col-span-8">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.siteLogo') || 'Logo 地址' }}</label>
            <input v-model="form.site_logo" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" :placeholder="t('adminSettings.siteLogoPlaceholder') || '输入 Logo URL 或右侧上传'" />
          </div>
          <div class="md:col-span-4">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.uploadLogo') || '上传新 Logo' }}</label>
            <label class="flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 active:scale-95">
              <ImageIcon class="h-4 w-4" />
              <span>选择图片</span>
              <input type="file" class="sr-only" accept="image/png,image/jpeg,image/gif,image/webp" @change="uploadLogo" />
            </label>
          </div>
          <div class="md:col-span-12" v-if="form.site_logo">
            <div class="inline-flex rounded-xl border border-slate-200 bg-slate-50 p-2 dark:border-slate-800 dark:bg-slate-900">
              <img :src="form.site_logo" :alt="t('adminSettings.logoPreviewAlt') || 'Logo 预览'" class="h-12 w-auto object-contain" />
            </div>
          </div>

          <div class="md:col-span-12">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.siteDescription') || '站点描述 (SEO)' }}</label>
            <textarea v-model="form.site_description" class="w-full resize-none rounded-xl border border-slate-200 bg-transparent p-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" rows="2"></textarea>
          </div>
          <div class="md:col-span-12">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.keywords') || '关键词 (Keywords)' }}</label>
            <input v-model="form.site_keywords" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
          <div class="md:col-span-12">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.boundDomains') || '绑定域名' }}</label>
            <textarea v-model="form.bound_domains" rows="3" class="w-full resize-none rounded-xl border border-slate-200 bg-transparent p-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" :placeholder="t('adminSettings.boundDomainsPlaceholder') || 'https://cms.example.com'"></textarea>
            <p class="mt-1.5 text-xs leading-relaxed text-slate-500 dark:text-slate-400">{{ t('adminSettings.boundDomainsHelp') || '每行一个域名，会用于后台写接口的 CSRF Origin 校验。' }}</p>
          </div>
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 100 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <Layout class="h-5 w-5 text-brand-500" />
          {{ t('adminSettings.homeBanner') || '首页横幅与幻灯片' }}
        </h2>

        <div class="grid grid-cols-1 gap-5 md:grid-cols-12 mb-6">
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.bannerTitle') || '横幅主标题' }}</label>
            <input v-model="form.banner_title" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.bannerSubtitle') || '横幅副标题' }}</label>
            <input v-model="form.banner_subtitle" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
        </div>

        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-semibold text-slate-800 dark:text-slate-200">{{ t('adminSettings.heroSlides') || '幻灯片配置 (最多5个)' }}</h3>
          <button
            type="button"
            class="inline-flex h-8 items-center justify-center gap-1.5 rounded-lg border border-brand-200 bg-brand-50 px-3 text-xs font-medium text-brand-600 transition-colors hover:bg-brand-100 dark:border-brand-800/30 dark:bg-brand-900/20 dark:text-brand-400 dark:hover:bg-brand-900/40 active:scale-95"
            @click="addHeroSlide"
          >
            <Plus class="h-3.5 w-3.5" />
            {{ t('adminSettings.addHeroSlide') || '添加幻灯片' }}
          </button>
        </div>

        <div v-if="heroSlides.length === 0" class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 py-8 text-slate-400 dark:border-slate-800">
          <Layout class="mb-2 h-8 w-8 opacity-20" />
          <span class="text-sm">{{ t('adminSettings.emptyHeroSlides') || '暂无幻灯片数据，点击右上角添加' }}</span>
        </div>

        <div class="space-y-4">
          <div
            v-for="(slide, index) in heroSlides"
            :key="index"
            class="relative rounded-xl border border-slate-100 bg-slate-50 p-4 transition-colors dark:border-slate-800/60 dark:bg-slate-900/50"
          >
            <div class="mb-4 flex items-center justify-between">
              <span class="inline-flex items-center rounded-md bg-slate-200 px-2 py-0.5 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                # {{ index + 1 }}
              </span>
              <button
                type="button"
                class="inline-flex h-7 w-7 items-center justify-center rounded-md text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10 dark:hover:text-red-400"
                @click="removeHeroSlide(index)"
                :title="t('adminAction.delete') || '删除'"
              >
                <Trash2 class="h-4 w-4" />
              </button>
            </div>

            <div class="grid grid-cols-1 gap-4 md:grid-cols-12">
              <div class="md:col-span-6">
                <label class="mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400">{{ t('adminTable.title') || '标题' }}</label>
                <input v-model="slide.title" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" maxlength="100" />
              </div>
              <div class="md:col-span-6">
                <label class="mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400">{{ t('adminSettings.badge') || '徽章(Badge)' }}</label>
                <input v-model="slide.badge" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" maxlength="40" />
              </div>
              <div class="md:col-span-12">
                <label class="mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400">{{ t('adminSettings.bannerSubtitle') || '副标题' }}</label>
                <input v-model="slide.subtitle" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" maxlength="200" />
              </div>
              <div class="md:col-span-6">
                <label class="mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400">{{ t('adminSettings.buttonText') || '按钮文字' }}</label>
                <input v-model="slide.ctaText" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" maxlength="30" :placeholder="t('adminSettings.buttonTextPlaceholder') || '了解更多'" />
              </div>
              <div class="md:col-span-6">
                <label class="mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400">{{ t('adminSettings.buttonPath') || '按钮链接' }}</label>
                <input v-model="slide.ctaLink" class="h-9 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100" maxlength="120" :placeholder="t('adminSettings.buttonPathPlaceholder') || '/works'" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 150 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <User class="h-5 w-5 text-brand-500" />
          {{ t('adminSettings.authorInfo') || '作者与关于信息' }}
        </h2>

        <div class="grid grid-cols-1 gap-5 md:grid-cols-12 mb-5">
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.authorName') || '作者名称' }}</label>
            <input v-model="form.author_name" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.authorEmail') || '作者邮箱' }}</label>
            <input v-model="form.author_email" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
        </div>

        <div>
          <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.aboutMarkdown') || '关于页面内容 (Markdown)' }}</label>
          <textarea v-model="form.about_content" class="min-h-[200px] w-full custom-scrollbar resize-y rounded-xl border border-slate-200 bg-slate-50/50 p-4 font-mono text-sm leading-relaxed text-slate-800 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:bg-slate-900/50 dark:text-slate-200" rows="8"></textarea>
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 200 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <Palette class="h-5 w-5 text-brand-500" />
          {{ t('adminSettings.theme') || '外观与布局' }}
        </h2>

        <div class="grid grid-cols-1 gap-5 md:grid-cols-12">
          <div class="md:col-span-4">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.primaryColor') || '主色调' }}</label>
            <div class="flex items-center gap-3">
              <input v-model="form.theme_primary_color" type="color" class="h-11 w-14 cursor-pointer appearance-none rounded-xl border border-slate-200 bg-transparent p-1 outline-none dark:border-slate-800" />
              <span class="font-mono text-sm text-slate-500">{{ form.theme_primary_color }}</span>
            </div>
          </div>
          <div class="md:col-span-4">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.accentColor') || '强调色' }}</label>
            <div class="flex items-center gap-3">
              <input v-model="form.theme_accent_color" type="color" class="h-11 w-14 cursor-pointer appearance-none rounded-xl border border-slate-200 bg-transparent p-1 outline-none dark:border-slate-800" />
              <span class="font-mono text-sm text-slate-500">{{ form.theme_accent_color }}</span>
            </div>
          </div>

          <div class="md:col-span-4">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.footerHeight') || '页脚尺寸' }}</label>
            <div class="relative">
              <select v-model="form.footer_height" class="h-11 w-full appearance-none rounded-xl border border-slate-200 bg-transparent px-4 pr-10 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100">
                <option value="compact">{{ t('adminSettings.compact') || '紧凑' }}</option>
                <option value="normal">{{ t('adminSettings.normal') || '正常' }}</option>
                <option value="large">{{ t('adminSettings.large') || '大型' }}</option>
              </select>
              <ChevronDown class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            </div>
          </div>
        </div>
      </section>

      <section
        class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-950 sm:p-6"
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0, transition: { delay: 250 } }"
      >
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-slate-100">
          <Globe class="h-5 w-5 text-brand-500" />
          {{ t('adminSettings.other') || '页脚、备案与友情链接' }}
        </h2>

        <div class="grid grid-cols-1 gap-5 md:grid-cols-12 mb-8">
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.contactInfo') || '联系方式文本' }}</label>
            <input v-model="form.contact_info" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.footerText') || '版权文本' }}</label>
            <input v-model="form.footer_text" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" />
          </div>
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.icpBeianNumber') || 'ICP 备案号' }}</label>
            <input v-model="form.icp_beian_number" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" :placeholder="t('adminSettings.icpBeianPlaceholder')" maxlength="80" />
          </div>
          <div class="md:col-span-6">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.policeBeianNumber') || '公安备案号' }}</label>
            <input v-model="form.police_beian_number" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" :placeholder="t('adminSettings.policeBeianPlaceholder')" maxlength="120" />
          </div>
          <div class="md:col-span-12">
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('adminSettings.footerNote') || '页脚附加说明' }}</label>
            <input v-model="form.footer_note" class="h-11 w-full rounded-xl border border-slate-200 bg-transparent px-4 text-sm text-slate-900 outline-none transition-colors focus:border-brand-500 focus:ring-4 focus:ring-brand-500/10 dark:border-slate-800 dark:text-slate-100" :placeholder="t('adminSettings.footerNotePlaceholder')" />
          </div>
        </div>

        <div class="flex items-center justify-between mb-4 border-t border-slate-100 pt-6 dark:border-slate-800">
          <h3 class="text-sm font-semibold text-slate-800 dark:text-slate-200">{{ t('adminSettings.friendLinks') || '友情链接 (最多12个)' }}</h3>
          <button
            type="button"
            class="inline-flex h-8 items-center justify-center gap-1.5 rounded-lg border border-brand-200 bg-brand-50 px-3 text-xs font-medium text-brand-600 transition-colors hover:bg-brand-100 dark:border-brand-800/30 dark:bg-brand-900/20 dark:text-brand-400 dark:hover:bg-brand-900/40 active:scale-95"
            @click="addFriendLink"
          >
            <Plus class="h-3.5 w-3.5" />
            {{ t('adminSettings.addLink') || '添加链接' }}
          </button>
        </div>

        <div v-if="friendLinks.length === 0" class="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 py-6 text-slate-400 dark:border-slate-800">
          <LinkIcon class="mb-2 h-6 w-6 opacity-20" />
          <span class="text-xs">{{ t('adminSettings.emptyFriendLinks') || '暂无友情链接' }}</span>
        </div>

        <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="(link, index) in friendLinks"
            :key="index"
            class="flex items-center gap-2 rounded-xl border border-slate-100 bg-slate-50 p-2 dark:border-slate-800/60 dark:bg-slate-900/50"
          >
            <div class="flex flex-1 flex-col gap-2">
              <input v-model="link.name" class="h-8 w-full rounded-lg border border-transparent bg-white px-2 text-xs outline-none focus:border-brand-500 dark:bg-slate-950 dark:text-slate-100" maxlength="40" :placeholder="t('adminSettings.friendLinkNamePlaceholder') || '网站名称'" />
              <input v-model="link.url" class="h-8 w-full rounded-lg border border-transparent bg-white px-2 text-xs outline-none focus:border-brand-500 dark:bg-slate-950 dark:text-slate-100" maxlength="300" :placeholder="t('adminSettings.friendLinkUrlPlaceholder') || 'https://'" />
            </div>
            <button
              type="button"
              class="inline-flex h-full w-8 shrink-0 items-center justify-center rounded-lg text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-500/10 dark:hover:text-red-400"
              @click="removeFriendLink(index)"
            >
              <Trash2 class="h-4 w-4" />
            </button>
          </div>
        </div>

      </section>

      <div class="mt-2 flex justify-end">
        <button
          class="inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-brand-500 px-8 text-sm font-semibold text-white shadow-sm transition-all hover:bg-brand-600 hover:shadow disabled:cursor-not-allowed disabled:opacity-60 active:scale-95"
          @click="saveSettings"
          :disabled="saving"
        >
          <Loader2 v-if="saving" class="h-5 w-5 animate-spin" />
          <Save v-else class="h-5 w-5" />
          {{ saving ? t('adminAction.saving') || '保存中...' : t('adminAction.saveSettings') || '保存所有设置' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { settingsApi, uploadApi } from '@/services/api'
import type { SiteSettings } from '@/services/api'
import { useUiStore } from '@/stores'

// 引入高颜值图标
import {
  Settings, Layout, User, Palette, Globe,
  Image as ImageIcon, Plus, Trash2, Link as LinkIcon,
  Save, Loader2, CheckCircle, AlertCircle, ChevronDown
} from '@lucide/vue'

type HeroSlideForm = { title: string; subtitle: string; badge: string; ctaText: string; ctaLink: string }
type FriendLinkForm = { name: string; url: string }

const uiStore = useUiStore()
const t = uiStore.t
const loading = ref<boolean>(true)
const saving = ref<boolean>(false)
const message = ref<string>('')
const msgType = ref<string>('success')

const heroSlides = ref<HeroSlideForm[]>([])
const friendLinks = ref<FriendLinkForm[]>([])
const form = ref<Record<string, string>>({
  site_name: '', site_slogan: '', site_description: '', site_keywords: '', site_logo: '',
  bound_domains: '',
  banner_title: '', banner_subtitle: '',
  author_name: '', author_email: '', about_content: '',
  contact_info: '', footer_text: '',
  footer_note: '', footer_height: 'normal',
  icp_beian_number: '', police_beian_number: '',
  friend_links: '', hero_slides: '',
  theme_primary_color: '#2563eb', theme_accent_color: '#f97316'
})

onMounted(async () => {
  try {
    const res = await settingsApi.get()
    Object.keys(form.value).forEach(k => {
      if (res.data && (res.data as any)[k] !== undefined) form.value[k] = (res.data as any)[k]
    })
    heroSlides.value = parseHeroSlides(form.value.hero_slides)
    friendLinks.value = parseFriendLinks(form.value.friend_links)
  } catch (e) { console.warn(e) }
  loading.value = false
})

async function saveSettings(): Promise<void> {
  saving.value = true
  message.value = ''
  try {
    form.value.hero_slides = serializeHeroSlides()
    form.value.friend_links = serializeFriendLinks()
    await settingsApi.update(form.value as Partial<SiteSettings>)
    message.value = t('adminSettings.saved') || '站点设置已成功保存！'
    msgType.value = 'success'
    scrollToTop()
  } catch (e: any) {
    message.value = e.message
    msgType.value = 'danger'
    scrollToTop()
  }
  saving.value = false
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function parseJsonArray(value: string, label: string): any[] {
  if (!value.trim()) return []
  const parsed = JSON.parse(value)
  if (!Array.isArray(parsed)) throw new Error(t('adminSettings.jsonArrayError', { label }) || `${label} 解析失败`)
  return parsed
}

function parseHeroSlides(value: string): HeroSlideForm[] {
  try {
    const parsed = parseJsonArray(value, t('adminSettings.heroLabel') || '幻灯片') || []
    return parsed.slice(0, 5).map((item: any) => ({
      title: String(item?.title || ''),
      subtitle: String(item?.subtitle || ''),
      badge: String(item?.badge || ''),
      ctaText: String(item?.ctaText || ''),
      ctaLink: String(item?.ctaLink || '')
    }))
  } catch {
    return []
  }
}

function parseFriendLinks(value: string): FriendLinkForm[] {
  try {
    const parsed = parseJsonArray(value, t('adminSettings.friendLinkLabel') || '友情链接') || []
    return parsed.slice(0, 12).map((item: any) => ({
      name: String(item?.name || ''),
      url: String(item?.url || '')
    }))
  } catch {
    return []
  }
}

function addHeroSlide(): void {
  if (heroSlides.value.length >= 5) {
    throwMessage(t('adminSettings.maxHeroSlides') || '最多只能添加 5 个幻灯片')
    return
  }
  heroSlides.value.push({ title: '', subtitle: '', badge: '', ctaText: t('adminSettings.buttonTextPlaceholder') || '了解更多', ctaLink: '/articles' })
}

function removeHeroSlide(index: number): void {
  heroSlides.value.splice(index, 1)
}

function addFriendLink(): void {
  if (friendLinks.value.length >= 12) {
    throwMessage(t('adminSettings.maxFriendLinks') || '最多只能添加 12 个友情链接')
    return
  }
  friendLinks.value.push({ name: '', url: 'https://' })
}

function removeFriendLink(index: number): void {
  friendLinks.value.splice(index, 1)
}

function throwMessage(text: string): void {
  message.value = text
  msgType.value = 'danger'
  scrollToTop()
}

function serializeHeroSlides(): string {
  const slides = heroSlides.value
    .map(slide => ({
      title: slide.title.trim(),
      subtitle: slide.subtitle.trim(),
      badge: slide.badge.trim(),
      ctaText: slide.ctaText.trim(),
      ctaLink: slide.ctaLink.trim()
    }))
    .filter(slide => slide.title || slide.subtitle)
    .map(slide => {
      if (slide.ctaLink && (!slide.ctaLink.startsWith('/') || slide.ctaLink.startsWith('//'))) {
        throw new Error(t('adminSettings.invalidHeroLink') || '幻灯片链接必须以 / 开头')
      }
      return removeEmptyFields(slide)
    })
  return slides.length ? JSON.stringify(slides) : ''
}

function serializeFriendLinks(): string {
  const links = friendLinks.value
    .map(link => ({ name: link.name.trim(), url: link.url.trim() }))
    .filter(link => link.name || link.url)
    .map(link => {
      if (!link.name || !/^https?:\/\//i.test(link.url)) {
        throw new Error(t('adminSettings.invalidFriendLink') || '友情链接名称必填，且 URL 必须以 http 或 https 开头')
      }
      return link
    })
  return links.length ? JSON.stringify(links) : ''
}

function removeEmptyFields<T extends Record<string, string>>(item: T): Partial<T> {
  return Object.fromEntries(Object.entries(item).filter(([, value]) => value)) as Partial<T>
}

async function uploadLogo(e: Event): Promise<void> {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const fd = new FormData()
  fd.append('image', file)
  try {
    const res = await uploadApi.siteLogo(fd)
    if (res.data?.url) form.value.site_logo = res.data.url
  } catch (err: any) {
    message.value = err.message
    msgType.value = 'danger'
    scrollToTop()
  } finally {
    input.value = ''
  }
}
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

/* Color Picker 原生样式重置修复 */
input[type="color"]::-webkit-color-swatch-wrapper {
  padding: 0;
}
input[type="color"]::-webkit-color-swatch {
  border: none;
  border-radius: 6px;
}

/* 顶部通知横幅过渡动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.98);
}
</style>
