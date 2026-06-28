/// <reference types="vite/client" />
/// <reference types="@vitejs/plugin-vue-jsx" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module '@vueuse/motion' {
  import type { App } from 'vue'
  export const MotionPlugin: { install(app: App, options?: unknown): void }
}
