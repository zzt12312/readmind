import { apiClient } from '@/api/client'
import type { EmbeddingWarmupResponse, LlmHealth } from '@/types/llm'

export async function fetchLlmHealth() {
  const { data } = await apiClient.get<LlmHealth>('/llm/health')
  return data
}

export async function warmupEmbedding() {
  const { data } = await apiClient.post<EmbeddingWarmupResponse>('/llm/embedding/warmup')
  return data
}
