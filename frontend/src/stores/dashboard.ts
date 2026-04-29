import { defineStore } from 'pinia'
import { fetchDashboardOverview } from '@/api/modules/dashboard'
import type { DashboardMetric, DashboardOverview, DashboardRecentBook, DashboardReviewSummary } from '@/types/dashboard'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    metrics: [] as DashboardMetric[],
    recentBooks: [] as DashboardRecentBook[],
    activeTopics: [] as string[],
    reviewSummary: {
      suggested_count: 0,
      due_count: 0,
      streak_days: 0,
      mastery_rate: '0%',
    } as DashboardReviewSummary,
    loading: false,
  }),
  actions: {
    async load() {
      this.loading = true
      try {
        const data: DashboardOverview = await fetchDashboardOverview()
        this.metrics = data.metrics
        this.recentBooks = data.recent_books
        this.activeTopics = data.active_topics
        this.reviewSummary = data.review_summary
      } finally {
        this.loading = false
      }
    },
  },
})
