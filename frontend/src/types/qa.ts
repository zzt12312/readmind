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

export interface QaEvidenceSummary {
  reference_count: number
  suggested_points: number
  sufficient: boolean
  message: string
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

export interface QaSavedAnswer {
  id: string
  session_id?: string | null
  message_id: string
  title: string
  question: string
  answer: string
  references: QaReference[]
  scope: 'all-books' | 'current-book'
  book_id?: number | null
  saved_at: string
}

export type QaWorkspaceStatus = 'open' | 'writing' | 'reviewing'
export type QaWorkspaceAction = 'followup' | 'writing' | 'reviewing'

export interface QaQuestionWorkspace {
  id: string
  title: string
  question: string
  latest_answer: string
  references: QaReference[]
  scope: 'all-books' | 'current-book'
  book_id?: number | null
  status: QaWorkspaceStatus
  evidence_count: number
  next_action: string
  created_at: string
  updated_at: string
}

export interface QaInsightCard {
  id: string
  title: string
  question: string
  summary: string
  references: QaReference[]
  created_at: string
}

export interface QaUnderstanding {
  id: string
  title: string
  question: string
  content: string
  references: QaReference[]
  created_at: string
  updated_at: string
}

export interface QaReviewSeed {
  id: string
  title: string
  question: string
  references: QaReference[]
  book_id?: number | null
  note_ids: number[]
  created_at: string
}

export type QaDepositType = 'insight_card' | 'understanding' | 'review_seed' | 'question'

export interface QaDepositPayload {
  deposit_type: QaDepositType
  title: string
  question: string
  content: string
  references: QaReference[]
  scope: 'all-books' | 'current-book'
  book_id?: number | null
  note_ids?: number[]
  status?: string
}

export interface QaDepositItem extends QaDepositPayload {
  id: string
  note_ids: number[]
  status: string
  created_at: string
  updated_at: string
}

export interface QaDepositResponse {
  item: QaDepositItem
  message: string
}

export interface QaResponse {
  question: string
  answer: string
  references: QaReference[]
  evidence?: QaEvidenceSummary
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
  onMeta?: (payload: { question: string; references: QaReference[]; retrieval_mode?: string; query_rewrite?: QueryRewriteSummary | null; evidence?: QaEvidenceSummary }) => void
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

export interface QaExportPayload {
  title: string
  scope: 'all-books' | 'current-book'
  book_title?: string
  messages: QaMessage[]
}

export interface QaExportResponse {
  file_name: string
  relative_path: string
  absolute_path: string
  download_url: string
  message: string
}
