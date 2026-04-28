import { apiClient } from '@/api/client'
import type { DashboardOverview } from '@/types/dashboard'

export async function fetchDashboardOverview() {
  const { data } = await apiClient.get<DashboardOverview>('/dashboard/overview')
  return data
}
