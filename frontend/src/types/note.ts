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

export interface QueryRewriteSummary {
  original: string
  applied_rules: string[]
  expansion_terms: string[]
  variants: string[]
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
  query_rewrite?: QueryRewriteSummary | null
}

export interface NoteInsightExportPayload {
  title: string
  scope: {
    book_id?: number
    book_title?: string
    q?: string
    category?: string
    tag?: string
    chapter?: string
    sort?: string
  }
  summary: string
  sections: NoteInsightSections | null
  references: NoteInsightReference[]
}

export interface NoteInsightExportResponse {
  file_name: string
  relative_path: string
  absolute_path: string
  download_url: string
  message: string
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
