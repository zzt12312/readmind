import { computed, type Ref } from 'vue'
import type {
  ActivityHeatmapItem,
  AnalyticsReviewProgress,
  CategoryPreference,
  HighValueMatrixItem,
  PreferenceRadarItem,
  ReadingTimeRankItem,
  ReviewFunnelItem,
  TopicRankItem,
} from '@/types/analytics'

interface AnalyticsDerivedDataSources {
  categoryPreferences: Ref<CategoryPreference[]>
  preferenceRadar: Ref<PreferenceRadarItem[]>
  readingTimeRank: Ref<ReadingTimeRankItem[]>
  highValueMatrix: Ref<HighValueMatrixItem[]>
  topicRank: Ref<TopicRankItem[]>
  reviewFunnel: Ref<ReviewFunnelItem[]>
  reviewProgress: Ref<AnalyticsReviewProgress>
  activityHeatmap: Ref<ActivityHeatmapItem[]>
}

export function useAnalyticsDerivedData(sources: AnalyticsDerivedDataSources) {
  const maxCategoryBooks = computed(() =>
    Math.max(...sources.categoryPreferences.value.map((item) => item.book_count), 1),
  )
  const maxReadingMinutes = computed(() =>
    Math.max(...sources.readingTimeRank.value.map((item) => item.reading_time_minutes), 1),
  )
  const maxTopicCount = computed(() =>
    Math.max(...sources.topicRank.value.map((item) => item.count), 1),
  )
  const maxFunnelValue = computed(() =>
    Math.max(...sources.reviewFunnel.value.map((item) => item.value), 1),
  )
  const reviewCoverage = computed(() => {
    if (!sources.reviewProgress.value.total_notes) return 0
    return Math.round((sources.reviewProgress.value.reviewed_count / sources.reviewProgress.value.total_notes) * 100)
  })
  const heatmapTotalActivity = computed(() =>
    sources.activityHeatmap.value.reduce((total, day) => total + day.count, 0),
  )
  const heatmapActiveDays = computed(() =>
    sources.activityHeatmap.value.filter((day) => day.count > 0).length,
  )
  const matrixListBooks = computed(() => sources.highValueMatrix.value.slice(0, 4))
  const matrixTopBook = computed(() => matrixListBooks.value[0])

  // Convert category scores into SVG polygon points for the custom radar chart.
  // Keeping the math here makes the page template easier to scan.
  const radarPoints = computed(() => {
    const items = sources.preferenceRadar.value
    if (!items.length) return ''
    const center = 140
    const radius = 82
    return items.map((item, index) => {
      const angle = (Math.PI * 2 * index) / items.length - Math.PI / 2
      const scaledRadius = radius * (item.score / 100)
      return `${center + Math.cos(angle) * scaledRadius},${center + Math.sin(angle) * scaledRadius}`
    }).join(' ')
  })

  const radarAxisPoints = computed(() => {
    const items = sources.preferenceRadar.value
    const center = 140
    const radius = 88
    return items.map((item, index) => {
      const angle = (Math.PI * 2 * index) / items.length - Math.PI / 2
      return {
        ...item,
        x: center + Math.cos(angle) * radius,
        y: center + Math.sin(angle) * radius,
        labelX: center + Math.cos(angle) * 118,
        labelY: center + Math.sin(angle) * 118,
      }
    })
  })

  function clampMatrixPosition(value: number) {
    return Math.min(90, Math.max(10, value))
  }

  return {
    maxCategoryBooks,
    maxReadingMinutes,
    maxTopicCount,
    maxFunnelValue,
    reviewCoverage,
    heatmapTotalActivity,
    heatmapActiveDays,
    matrixListBooks,
    matrixTopBook,
    radarPoints,
    radarAxisPoints,
    clampMatrixPosition,
  }
}
