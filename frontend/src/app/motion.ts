/**
 * CPYCMS - Vue Motion 动画预设
 * 使用 transform/opacity，避免触发布局重排，并尊重系统减少动态效果设置。
 */

import { MotionPlugin } from '@vueuse/motion'
import type { App } from 'vue'

const prefersReducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false

const instant = {
  initial: { opacity: 1, y: 0, scale: 1 },
  visible: { opacity: 1, y: 0, scale: 1 }
}

const presets = prefersReducedMotion
  ? {
      fadeVisible: instant,
      slideVisible: instant,
      cardVisible: instant,
      heroVisible: instant
    }
  : {
      fadeVisible: {
        initial: { opacity: 0 },
        visible: { opacity: 1, transition: { duration: 220, ease: 'easeOut' } }
      },
      slideVisible: {
        initial: { opacity: 0, y: 18 },
        visible: { opacity: 1, y: 0, transition: { duration: 260, ease: 'easeOut' } }
      },
      cardVisible: {
        initial: { opacity: 0, y: 16, scale: 0.98 },
        visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 240, ease: 'easeOut' } }
      },
      heroVisible: {
        initial: { opacity: 0, y: 24, scale: 0.99 },
        visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 320, ease: 'easeOut' } }
      }
    }

export function installMotion(app: App): void {
  app.use(MotionPlugin, { directives: presets })
}
