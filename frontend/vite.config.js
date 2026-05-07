import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: '/weight/',   // ⭐⭐⭐ 关键修复
  plugins: [vue()],
  server: {
    port: 3000,
    allowedHosts: [
      'www.rxaoknjn0.nyat.app'
    ],
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:6000',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})