export interface AsyncJobResult {
  book_id?: number
  summary?: string
  book_count?: number
  note_count?: number
  category_count?: number
  references?: Array<{
    book: string
    chapter: string
    excerpt: string
  }>
  sections?: {
    core_conclusion: string
    key_themes: string[]
    review_questions: string[]
    action_suggestions: string[]
    reasoning: string
  }
}

export interface AsyncJob {
  id: string
  job_type: string
  status: 'queued' | 'processing' | 'success' | 'failed' | 'canceled'
  resource_type: string
  resource_id: string
  payload: Record<string, unknown>
  result: AsyncJobResult | null
  error_message: string
  progress: number
  message: string
  created_at: string
  started_at: string
  finished_at: string
}
