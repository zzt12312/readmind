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

export interface DashboardDailyBriefFeedback {
  label: string
  value: string
  hint: string
}

export interface DashboardDailyBriefAction {
  label: string
  type: 'review' | 'notes' | 'book' | 'analytics'
  path: string
}

export interface DashboardDailyBrief {
  title: string
  summary: string
  feedback_items: DashboardDailyBriefFeedback[]
  suggested_actions: DashboardDailyBriefAction[]
  highlights: {
    topics: string[]
    book: {
      id: number
      title: string
    } | null
    author: string
  }
}

export interface DashboardActionItem {
  label: string
  title: string
  hint: string
  path: string
  accent: 'primary' | 'warm' | 'calm'
}

export interface DashboardRecommendedReview {
  title: string
  reason: string
  path: string
  topics: string[]
  book: {
    id: number
    title: string
    author: string
    notes: number
    cover: string
  } | null
}

export interface DashboardOverview {
  metrics: DashboardMetric[]
  recent_books: DashboardRecentBook[]
  active_topics: string[]
  review_summary: DashboardReviewSummary
  daily_brief: DashboardDailyBrief
  action_queue: DashboardActionItem[]
  recommended_review: DashboardRecommendedReview
}
