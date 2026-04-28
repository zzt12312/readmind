export interface NoteItem {
  id: number
  book_id?: number
  book_title?: string
  chapter: string
  excerpt: string
  comment: string
  tags: string[]
  timestamp?: string
  source_path?: string
}

export interface NoteInsightReference {
  book: string
  chapter: string
  excerpt: string
}

export interface NoteInsightSections {
  core_conclusion: string
  key_themes: string[]
  review_questions: string[]
  action_suggestions: string[]
  reasoning: string
}

export interface NoteInsight {
  summary: string
  related_topics: string[]
  related_note: string
  references?: NoteInsightReference[]
  retrieval_mode?: string
  sections?: NoteInsightSections
}

export interface NoteFilters {
  categories: string[]
  tags: string[]
  chapters: string[]
}

export interface NotePagination {
  page: number
  per_page: number
  total: number
  total_pages: number
  has_more: boolean
}

export interface NoteListResponse {
  items: NoteItem[]
  insight: NoteInsight
  filters: NoteFilters
  pagination: NotePagination
}
