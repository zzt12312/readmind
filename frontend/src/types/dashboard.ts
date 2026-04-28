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

export interface DashboardOverview {
  metrics: DashboardMetric[]
  recent_books: DashboardRecentBook[]
  active_topics: string[]
}
