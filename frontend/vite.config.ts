import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
      dts: false,
    }),
    Components({
      resolvers: [ElementPlusResolver({ directives: true })],
      dts: false,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      // 本地开发默认把 /api 转发到 Flask，避免 npm run dev 时仍然去请求 5173 自己。
      '/api': {
        target: process.env.VITE_DEV_API_PROXY_TARGET ?? 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) {
            return
          }

          // 把体积较大的基础依赖拆开，避免首屏把所有第三方代码都塞进同一个大 chunk。
          if (id.includes('vue-echarts')) {
            return 'chart-vue-vendor'
          }

          if (id.includes('zrender')) {
            return 'chart-renderer-vendor'
          }

          if (id.includes('echarts')) {
            return 'chart-core-vendor'
          }

          // Element Plus is imported on demand by route/component. Keeping it
          // outside a single manual chunk lets Rollup place only the used
          // pieces next to the pages that need them.
          if (id.includes('element-plus') || id.includes('@element-plus')) {
            return
          }

          if (id.includes('vue') || id.includes('vue-router') || id.includes('pinia')) {
            return 'vue-vendor'
          }

          if (id.includes('axios')) {
            return 'network-vendor'
          }

          return 'vendor'
        },
      },
    },
  },
})
