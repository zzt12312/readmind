import { defineStore } from 'pinia'
import { fetchDashboardOverview } from '@/api/modules/dashboard'
import type { DashboardMetric, DashboardOverview, DashboardRecentBook } from '@/types/dashboard'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    metrics: [] as DashboardMetric[],
    recentBooks: [] as DashboardRecentBook[],
    activeTopics: [] as string[],
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
      } finally {
        this.loading = false
      }
    },
  },
})
