import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '127.0.0.1'
  },
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // 新增构建配置
  build: {
    rollupOptions: {
      output: {
        // 关键配置：确保基于内容生成确定性的哈希
        // [name] 是原始文件名，[hash] 是基于文件内容的哈希
        // 使用相对较短的8位hash足以避免冲突，且更整洁
        entryFileNames: `assets/entry-[name]-[hash:8].js`,
        chunkFileNames: `assets/chunk-[name]-[hash:8].js`,
        assetFileNames: `assets/asset-[name]-[hash:8].[ext]`
      }
    }
  }
})