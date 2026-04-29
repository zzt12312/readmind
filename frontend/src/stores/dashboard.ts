import { defineStore } from 'pinia'
import { fetchDashboardOverview } from '@/api/modules/dashboard'
import type {
  DashboardActionItem,
  DashboardDailyBrief,
  DashboardMetric,
  DashboardOverview,
  DashboardRecentBook,
  DashboardRecommendedReview,
  DashboardReviewSummary,
} from '@/types/dashboard'

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
    dailyBrief: {
      title: '今日阅读回顾',
      summary: '正在整理你的阅读状态。',
      feedback_items: [],
      suggested_actions: [],
      highlights: {
        topics: [],
        book: null,
        author: '',
      },
    } as DashboardDailyBrief,
    actionQueue: [] as DashboardActionItem[],
    recommendedReview: {
      title: '',
      reason: '',
      path: '/notes',
      topics: [],
      book: null,
    } as DashboardRecommendedReview,
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
        this.dailyBrief = data.daily_brief
        this.actionQueue = data.action_queue
        this.recommendedReview = data.recommended_review
      } finally {
        this.loading = false
      }
    },
  },
})
