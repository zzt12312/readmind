export interface LlmHealth {
  provider: string
  demo_mode: boolean
  base_url: string
  model: string
  api_key_loaded: boolean
  connected: boolean
  fallback_mode: boolean
  detail: string
  embedding_model: string
  embedding_provider: string
  embedding_status: 'idle' | 'loading' | 'ready' | 'fallback'
  embedding_error: string
}

export interface EmbeddingWarmupResponse {
  started: boolean
  embedding_model: string
  embedding_provider: string
  embedding_status: 'idle' | 'loading' | 'ready' | 'fallback'
  embedding_error: string
}
