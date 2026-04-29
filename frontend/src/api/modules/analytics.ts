import { apiClient } from '@/api/client'
import type { AnalyticsOverview } from '@/types/analytics'

export async function fetchAnalyticsOverview() {
  const { data } = await apiClient.get<AnalyticsOverview>('/analytics/overview')
  return data
}
