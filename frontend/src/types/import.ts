export interface ImportJob {
  id: number | string
  file_name: string
  status: 'processing' | 'success' | 'failed'
  progress: number
  result: string
  source?: string
  created_at?: string
  finished_at?: string
}

export interface ImportMeta {
  demo_mode: boolean
  source_label: string
  description: string
  vault_root?: string
  vault_status?: 'ready' | 'missing' | 'invalid' | 'empty'
  vault_message?: string
  markdown_count?: number
}

export interface ImportSyncFeedback {
  status: 'idle' | 'processing' | 'success' | 'failed'
  title: string
  message: string
  book_count: number
  note_count: number
  category_count: number
}

export interface ImportJobListResponse {
  items: ImportJob[]
  meta: ImportMeta
}
