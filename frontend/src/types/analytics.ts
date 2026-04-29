export interface AnalyticsMetric {
  label: string
  value: string | number
  hint: string
}

export interface CategoryPreference {
  category: string
  book_count: number
  note_count: number
  share: number
}

export interface ReadingTimeRankItem {
  id: number
  title: string
  author: string
  category: string
  note_count: number
  reviewed_count: number
  last_read_date: string
  reading_time: string
  reading_time_minutes: number
  cover: string
}

export interface PreferenceRadarItem {
  label: string
  score: number
  book_count: number
  note_count: number
}

export interface HighValueMatrixItem {
  id: number
  title: string
  category: string
  note_count: number
  reviewed_count: number
  x: number
  y: number
  value_score: number
}

export interface TopicRankItem {
  topic: string
  count: number
  share: number
}

export interface ReviewFunnelItem {
  label: string
  value: number
  hint: string
}

export interface AnalyticsReviewProgress {
  due_count: number
  streak_days: number
  mastery_rate: string
  reviewed_count: number
  total_notes: number
}

export interface ReadingTimelineItem {
  period: string
  book_count: number
  books: string[]
}

export interface AuthorCloudItem {
  author: string
  book_count: number
  note_count: number
  weight: number
}

export interface ActivityHeatmapItem {
  date: string
  label: string
  count: number
  level: number
}

export interface LongTermMetric {
  label: string
  value: string
  score: number
  hint: string
}

export interface AnalyticsOverview {
  metrics: AnalyticsMetric[]
  category_preferences: CategoryPreference[]
  preference_radar: PreferenceRadarItem[]
  reading_time_rank: ReadingTimeRankItem[]
  high_value_matrix: HighValueMatrixItem[]
  topic_rank: TopicRankItem[]
  review_funnel: ReviewFunnelItem[]
  review_progress: AnalyticsReviewProgress
  reading_timeline: ReadingTimelineItem[]
  author_cloud: AuthorCloudItem[]
  activity_heatmap: ActivityHeatmapItem[]
  long_term_metrics: LongTermMetric[]
}
