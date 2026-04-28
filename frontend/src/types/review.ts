export interface ReviewSummaryItem {
  label: string
  value: string
}

export interface ReviewCard {
  id: number
  book_id: number
  note_id: number
  question: string
  source: string
  answer: string
  review_count: number
  mastery_score: number
  last_reviewed_at: string
  next_review_at: string
}

export interface ReviewTodayResponse {
  summary: ReviewSummaryItem[]
  card: ReviewCard
  cards: ReviewCard[]
}

export type ReviewLevel = 'low' | 'medium' | 'high'

export interface ReviewProgress {
  note_id: number
  review_count: number
  mastery_score: number
  last_result: ReviewLevel
  last_reviewed_at: string
  next_review_at: string
}

export interface ReviewRateResponse {
  progress: ReviewProgress | null
  summary: ReviewSummaryItem[]
}
