import { defineStore } from 'pinia'
import { fetchAnalyticsOverview } from '@/api/modules/analytics'
import type {
  AnalyticsMetric,
  AnalyticsRecommendation,
  AnalyticsReviewProgress,
  ActivityHeatmapItem,
  AuthorCloudItem,
  CategoryPreference,
  HighValueMatrixItem,
  LongTermMetric,
  PreferenceRadarItem,
  ReadingTimelineItem,
  ReadingTimeRankItem,
  ReviewFunnelItem,
  TopicRankItem,
} from '@/types/analytics'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    metrics: [] as AnalyticsMetric[],
    categoryPreferences: [] as CategoryPreference[],
    preferenceRadar: [] as PreferenceRadarItem[],
    readingTimeRank: [] as ReadingTimeRankItem[],
    highValueMatrix: [] as HighValueMatrixItem[],
    topicRank: [] as TopicRankItem[],
    reviewFunnel: [] as ReviewFunnelItem[],
    reviewProgress: {
      due_count: 0,
      streak_days: 0,
      mastery_rate: '0%',
      reviewed_count: 0,
      total_notes: 0,
    } as AnalyticsReviewProgress,
    readingTimeline: [] as ReadingTimelineItem[],
    authorCloud: [] as AuthorCloudItem[],
    activityHeatmap: [] as ActivityHeatmapItem[],
    longTermMetrics: [] as LongTermMetric[],
    recommendations: [] as AnalyticsRecommendation[],
    loading: false,
  }),
  actions: {
    async load() {
      this.loading = true
      try {
        const data = await fetchAnalyticsOverview()
        this.metrics = data.metrics
        this.categoryPreferences = data.category_preferences
        this.preferenceRadar = data.preference_radar
        this.readingTimeRank = data.reading_time_rank
        this.highValueMatrix = data.high_value_matrix
        this.topicRank = data.topic_rank
        this.reviewFunnel = data.review_funnel
        this.reviewProgress = data.review_progress
        this.readingTimeline = data.reading_timeline
        this.authorCloud = data.author_cloud
        this.activityHeatmap = data.activity_heatmap
        this.longTermMetrics = data.long_term_metrics
        this.recommendations = data.recommendations ?? []
      } finally {
        this.loading = false
      }
    },
  },
})
