/**
 * CPYCMS - 客户端风控指纹。
 * 仅用于评论防刷和重复提交判断，不存储原始可识别信息。
 */

function toHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map(byte => byte.toString(16).padStart(2, '0'))
    .join('')
}

async function digest(value: string): Promise<string> {
  if (!window.crypto?.subtle) {
    let hash = 0
    for (let index = 0; index < value.length; index += 1) {
      hash = Math.imul(31, hash) + value.charCodeAt(index) | 0
    }
    return Math.abs(hash).toString(16).padStart(32, '0')
  }
  const bytes = new TextEncoder().encode(value)
  const hash = await crypto.subtle.digest('SHA-256', bytes)
  return toHex(hash)
}

export async function buildClientFingerprint(): Promise<string> {
  const nav = window.navigator
  const screenInfo = window.screen
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || ''
  const language = nav.language || ''
  const languages = (nav.languages || []).join(',')
  const platform = nav.platform || ''
  const hardware = String(nav.hardwareConcurrency || '')
  const memory = String((nav as Navigator & { deviceMemory?: number }).deviceMemory || '')
  const depth = String(screenInfo.colorDepth || '')
  const size = `${screenInfo.width}x${screenInfo.height}`
  const ua = nav.userAgent || ''
  const payload = [ua, language, languages, platform, hardware, memory, depth, size, timezone].join('|')
  return digest(payload)
}
