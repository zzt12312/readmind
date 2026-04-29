export interface DashboardMetric {
  label: string
  value: number
  hint: string
}

export interface DashboardRecentBook {
  id: number
  title: string
  notes: number
  updated: string
  cover: string
}

export interface DashboardReviewSummary {
  suggested_count: number
  due_count: number
  streak_days: number
  mastery_rate: string
}

export interface DashboardOverview {
  metrics: DashboardMetric[]
  recent_books: DashboardRecentBook[]
  active_topics: string[]
  review_summary: DashboardReviewSummary
}
