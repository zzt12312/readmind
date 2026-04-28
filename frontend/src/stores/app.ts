import { defineStore } from 'pinia'
import { fetchLlmHealth, warmupEmbedding } from '@/api/modules/llm'
import type { LlmHealth } from '@/types/llm'

export const useAppStore = defineStore('app', {
  state: () => ({
    appName: 'ReadMind',
    llmHealth: null as LlmHealth | null,
    llmLoading: false,
    embeddingWarming: false,
  }),
  actions: {
    async loadLlmHealth() {
      this.llmLoading = true
      try {
        this.llmHealth = await fetchLlmHealth()
      } finally {
        this.llmLoading = false
      }
    },
    // embedding 预热会触发后端后台加载真实模型，前端只需要轮询最新状态即可。
    async startEmbeddingWarmup() {
      this.embeddingWarming = true
      try {
        await warmupEmbedding()
        await this.loadLlmHealth()
      } finally {
        this.embeddingWarming = false
      }
    },
  },
})
