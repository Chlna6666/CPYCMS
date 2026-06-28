/**
 * CPYCMS - JSON i18n messages.
 * 轻量级国际化实现，只负责读取 JSON 语言包并同步 document.lang。
 */

import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'

export type LanguageCode = 'zh-CN' | 'en-US'

type MessageTree = Record<string, unknown>

export const DEFAULT_LOCALE: LanguageCode = 'zh-CN'
export const SUPPORTED_LOCALES: LanguageCode[] = ['zh-CN', 'en-US']

// 统一管理的可选语系元数据（不含 flag 纯文本）
export const AVAILABLE_LOCALES = [
  { code: 'zh-CN', labelKey: 'common.localeZh' },
  { code: 'en-US', labelKey: 'common.localeEn' }
] as const

export const messages: Record<LanguageCode, MessageTree> = {
  'zh-CN': zhCN,
  'en-US': enUS
}

function isLanguageCode(value: string | null): value is LanguageCode {
  return value === 'zh-CN' || value === 'en-US'
}

export function getInitialLocale(): LanguageCode {
  const stored = window.localStorage.getItem('cpycms.locale')
  return isLanguageCode(stored) ? stored : DEFAULT_LOCALE
}

export function applyDocumentLocale(locale: LanguageCode): void {
  document.documentElement.lang = locale
  window.localStorage.setItem('cpycms.locale', locale)
}

function resolveMessage(locale: LanguageCode, key: string): string | undefined {
  const value = key.split('.').reduce<unknown>((current, segment) => {
    if (current && typeof current === 'object' && segment in current) {
      return (current as Record<string, unknown>)[segment]
    }
    return undefined
  }, messages[locale])
  return typeof value === 'string' ? value : undefined
}

export function translate(locale: LanguageCode, key: string, vars: Record<string, string | number> = {}): string {
  const template = resolveMessage(locale, key) ?? resolveMessage(DEFAULT_LOCALE, key) ?? key
  return Object.entries(vars).reduce(
    (text, [name, value]) => text.split(`{${name}}`).join(String(value)),
    template
  )
}
