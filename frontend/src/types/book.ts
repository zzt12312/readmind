export interface BookItem {
  id: number
  title: string
  author: string
  notes: number
  tags: string[]
  category?: string
  source_path?: string
  reading_date?: string
  last_read_date?: string
  progress?: string
  cover?: string
  reading_notes?: string
}

export interface BookListResponse {
  items: BookItem[]
}

export interface BookDetailResponse {
  book: BookItem
  summary: string
}

export interface BookSummaryResponse {
  book_id: number
  summary: string
  cached?: boolean
  regenerated?: boolean
  status?: 'queued' | 'processing' | 'success'
  job_id?: string
  message?: string
}
