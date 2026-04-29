import { defineStore } from 'pinia'
import { fetchLlmHealth, warmupEmbedding } from '@/api/modules/llm'
import type { LlmHealth } from '@/types/llm'

export const useAppStore = defineStore('app', {
  state: () => ({
    appName: 'ReadMind',
    llmHealth: null as LlmHealth | null,
    llmLoading: false,
    embeddingWarming: false,
    sidebarCollapsed: localStorage.getItem('readmind.sidebarCollapsed') === 'true',
  }),
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
      localStorage.setItem('readmind.sidebarCollapsed', String(this.sidebarCollapsed))
    },
    async loadLlmHealth() {
      this.llmLoading = true
      try {
        this.llmHealth = await fetchLlmHealth()
      } finally {
        this.llmLoading = false
      }
    },
    // 自动预热只在真实检索模式下触发一次后台加载，用户不需要理解或手动点击这个技术动作。
    async ensureEmbeddingWarmup() {
      if (this.embeddingWarming) return false
      if (!this.llmHealth) {
        await this.loadLlmHealth()
      }
      if (!this.llmHealth || this.llmHealth.demo_mode) return false
      if (['ready', 'loading', 'fallback'].includes(this.llmHealth.embedding_status)) return false

      this.embeddingWarming = true
      try {
        await warmupEmbedding()
        await this.loadLlmHealth()
        return true
      } finally {
        this.embeddingWarming = false
      }
    },
  },
})
