<!--
  CPYCMS - Markdown 渲染组件
  支持 Markdown、Mermaid 图表、KaTeX 数学公式、代码高亮
-->
<template>
  <div class="markdown-body" ref="contentRef" v-html="renderedHtml"></div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import bash from 'highlight.js/lib/languages/bash'
import css from 'highlight.js/lib/languages/css'
import java from 'highlight.js/lib/languages/java'
import javascript from 'highlight.js/lib/languages/javascript'
import json from 'highlight.js/lib/languages/json'
import markdown from 'highlight.js/lib/languages/markdown'
import python from 'highlight.js/lib/languages/python'
import shell from 'highlight.js/lib/languages/shell'
import sql from 'highlight.js/lib/languages/sql'
import typescript from 'highlight.js/lib/languages/typescript'
import xml from 'highlight.js/lib/languages/xml'
import yaml from 'highlight.js/lib/languages/yaml'
import { useUiStore } from '@/stores'
import 'katex/dist/katex.min.css'
import 'highlight.js/styles/github-dark.min.css'

const props = defineProps({
  content: { type: String, default: '' }
})

const contentRef = ref<HTMLElement | null>(null)
const renderedHtml = ref('')
const uiStore = useUiStore()

/**
 * 只注册课程 CMS 常用语言，避免把 highlight.js 的全部语言包打入 Markdown chunk。
 * HTML/Vue 代码块在 highlight.js 中使用 xml 语言解析。
 */
const commonLanguages = {
  bash,
  css,
  html: xml,
  java,
  javascript,
  js: javascript,
  json,
  markdown,
  md: markdown,
  python,
  py: python,
  shell,
  sh: shell,
  sql,
  typescript,
  ts: typescript,
  vue: xml,
  xml,
  yaml,
  yml: yaml
}
const commonLanguageNames = Object.keys(commonLanguages)

Object.entries(commonLanguages).forEach(([name, language]) => {
  hljs.registerLanguage(name, language)
})

type MermaidRuntime = {
  initialize(config: Record<string, unknown>): void
  render(id: string, code: string): Promise<{ svg: string }>
}

/** 通过 public 本地资源加载 Mermaid，避免把 3MB 图表引擎打进业务 chunk。 */
async function loadMermaidRuntime(): Promise<MermaidRuntime> {
  const importMermaid = new Function('path', 'return import(path)') as (path: string) => Promise<{ default: MermaidRuntime }>
  const mod = await importMermaid('/vendor/mermaid/mermaid.esm.min.mjs')
  return mod.default
}

/** 配置 marked 解析器，使用 renderer 接入 highlight.js 适配 marked v15。 */
const renderer = new marked.Renderer()
renderer.code = ((token: any) => {
  const code = String(token.text || '')
  const lang = String(token.lang || '').trim()
  let highlighted = ''
  if (lang && hljs.getLanguage(lang)) {
    try {
      highlighted = hljs.highlight(code, { language: lang }).value
    } catch {
      highlighted = hljs.highlightAuto(code, commonLanguageNames).value
    }
  } else {
    highlighted = hljs.highlightAuto(code, commonLanguageNames).value
  }
  return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
}) as any

marked.setOptions({
  breaks: true,
  gfm: true,
  renderer
})

/** 渲染 Markdown 内容 */
async function renderContent() {
  if (!props.content) {
    renderedHtml.value = ''
    return
  }

  let text = props.content

  // 提取 Mermaid 代码块，替换为占位符
  const mermaidBlocks: string[] = []
  text = text.replace(/```mermaid\n([\s\S]*?)```/g, (_: string, code: string) => {
    const idx = mermaidBlocks.length
    mermaidBlocks.push(code.trim())
    return `<div class="mermaid" data-idx="${idx}"></div>`
  })

  // 提取 KaTeX 块级公式 $$...$$
  const katexBlocks: string[] = []
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, (_: string, formula: string) => {
    const idx = katexBlocks.length
    katexBlocks.push(formula.trim())
    return `<div class="katex-block" data-idx="${idx}"></div>`
  })

  // 提取 KaTeX 行内公式 $...$
  const katexInlines: string[] = []
  text = text.replace(/\$([^\$\n]+?)\$/g, (_: string, formula: string) => {
    const idx = katexInlines.length
    katexInlines.push(formula.trim())
    return `<span class="katex-inline" data-idx="${idx}"></span>`
  })

  // 解析 Markdown
  const html = await marked.parse(text)

  renderedHtml.value = html

  // 异步渲染 Mermaid 和 KaTeX
  await nextTick()
  if (!contentRef.value) return

  // 渲染 Mermaid 图表
  if (mermaidBlocks.length > 0) {
    try {
      const mermaid = await loadMermaidRuntime()
      mermaid.initialize({
        startOnLoad: false,
        theme: 'neutral',
        securityLevel: 'loose'
      })
      const mermaidEls = contentRef.value.querySelectorAll<HTMLElement>('.mermaid')
      for (const el of mermaidEls) {
        const idx = parseInt(el.dataset.idx || '0', 10)
        const code = mermaidBlocks[idx]
        if (code) {
          try {
            const { svg } = await mermaid.render(`mermaid-${idx}-${Date.now()}`, code)
            el.innerHTML = svg
          } catch (e: any) {
            el.innerHTML = `<pre class="text-danger">${uiStore.t('markdown.mermaidFailed')}: ${e.message}</pre>`
          }
        }
      }
    } catch { /* mermaid 未加载则跳过 */ }
  }

  // 渲染 KaTeX 公式
  if (katexBlocks.length > 0 || katexInlines.length > 0) {
    try {
      const katex = (await import('katex')).default
      // 块级公式
      const blockEls = contentRef.value.querySelectorAll<HTMLElement>('.katex-block')
      for (const el of blockEls) {
        const idx = parseInt(el.dataset.idx || '0', 10)
        const formula = katexBlocks[idx]
        if (formula) {
          try {
            katex.render(formula, el, { displayMode: true, throwOnError: false })
          } catch (e) { el.textContent = formula }
        }
      }
      // 行内公式
      const inlineEls = contentRef.value.querySelectorAll<HTMLElement>('.katex-inline')
      for (const el of inlineEls) {
        const idx = parseInt(el.dataset.idx || '0', 10)
        const formula = katexInlines[idx]
        if (formula) {
          try {
            katex.render(formula, el, { displayMode: false, throwOnError: false })
          } catch (e) { el.textContent = formula }
        }
      }
    } catch { /* katex 未加载则跳过 */ }
  }
}

watch(() => props.content, renderContent)
onMounted(renderContent)
</script>
