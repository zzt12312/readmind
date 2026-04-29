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
  tags: string[]
  review_count: number
  mastery_score: number
  last_reviewed_at: string
  next_review_at: string
}

export interface ReviewScope {
  tag: string
  book_id: number | null
  queue: ReviewQueue
}

export type ReviewQueue = 'due' | 'weak' | 'new'

export interface ReviewPlan {
  default_daily_goal: number
  selected_daily_goal: number
  daily_goal_options: number[]
  suggested_today: number
  due_count: number
  batch_size: number
  message: string
}

export type ReviewLevel = 'low' | 'medium' | 'high'

export interface ReviewLevelGuidance {
  level: ReviewLevel
  label: string
  hint: string
}

export interface ReviewQueueOption {
  value: ReviewQueue
  label: string
  description: string
  count: number
}

export interface ReviewTodayResponse {
  summary: ReviewSummaryItem[]
  plan: ReviewPlan
  level_guidance: ReviewLevelGuidance[]
  queue_options: ReviewQueueOption[]
  card: ReviewCard
  cards: ReviewCard[]
  weak_cards: ReviewCard[]
  scope: ReviewScope
}

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
