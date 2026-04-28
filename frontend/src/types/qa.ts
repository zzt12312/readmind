export interface QueryRewriteSummary {
  original: string
  applied_rules: string[]
  expansion_terms: string[]
  variants: string[]
}

export interface QaReference {
  book: string
  book_id: number
  note_id: number
  chapter: string
  excerpt: string
  source_path: string
}

export interface QaMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  references?: QaReference[]
  feedback?: 'up' | 'down' | null
}

export interface QaSession {
  id: string
  title: string
  scope: 'all-books' | 'current-book'
  book_id?: number
  updated_at: string
  pinned?: boolean
  messages: QaMessage[]
}

export interface QaResponse {
  question: string
  answer: string
  references: QaReference[]
  generation_mode?: 'llm' | 'fallback'
  retrieval_mode?: string
  fallback_reason?: string
  query_rewrite?: QueryRewriteSummary | null
}

export interface QaStatusPayload {
  phase: 'idle' | 'retrieving' | 'generating' | 'fallback' | 'success' | 'failed'
  label: string
  detail: string
}

export interface QaStreamEventHandlers {
  onMeta?: (payload: { question: string; references: QaReference[]; retrieval_mode?: string; query_rewrite?: QueryRewriteSummary | null }) => void
  onStatus?: (payload: QaStatusPayload) => void
  onDelta?: (payload: { content: string }) => void
  onDone?: (payload: QaResponse) => void
  onError?: (error: Error) => void
}

export interface QaAskPayload {
  question: string
  scope?: 'all-books' | 'current-book'
  book_id?: number
  history?: QaMessage[]
}
