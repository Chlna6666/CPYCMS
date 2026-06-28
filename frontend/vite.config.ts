/**
 * CPYCMS - Vite 配置
 * 集成 Vue3 + JSX + Tailwind CSS v4
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

const devHost = process.env.VITE_DEV_HOST || '127.0.0.1'
const devPort = Number(process.env.VITE_DEV_PORT || '3000')
const backendUrl = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:5000'

export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    tailwindcss()
  ],
  root: path.resolve(__dirname),
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    host: devHost,
    port: devPort,
    strictPort: true,
    hmr: {
      host: devHost,
      clientPort: devPort,
      protocol: 'ws'
    },
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true
      },
      '/uploads': {
        target: backendUrl,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        chunkFileNames: 'assets/[name]-[hash].js',
        manualChunks(id) {
          const normalizedId = id.replace(/\\/g, '/')

          // 后台管理端仅在访问 /admin 时按需加载，避免普通前台页面下载管理代码。
          if (normalizedId.includes('/src/views/admin/LoginView.vue')) return 'admin-auth'
          if (normalizedId.includes('/src/components/layout/AdminLayout.vue')) return 'admin-layout'

          if (normalizedId.includes('/node_modules/')) {
            if (normalizedId.includes('/echarts/') || normalizedId.includes('/zrender/')) return 'vendor-charts'
            if (normalizedId.includes('/katex/')) return 'markdown-math'
            if (normalizedId.includes('/marked/') || normalizedId.includes('/highlight.js/')) return 'markdown-core'
            if (
              normalizedId.includes('/vue/') ||
              normalizedId.includes('/vue-router/') ||
              normalizedId.includes('/pinia/')
            ) {
              return 'vendor-vue'
            }
            if (normalizedId.includes('/axios/')) return 'vendor-http'
            if (normalizedId.includes('/@lucide/') || normalizedId.includes('/lucide-vue')) return 'vendor-icons'
            if (normalizedId.includes('/@vueuse/')) return 'vendor-motion'
          }
        }
      }
    }
  }
})
