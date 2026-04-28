import { apiClient } from '@/api/client'
import type { TopicGraphPayload } from '@/types/insights'

export async function getTopicGraph(params?: {
  category?: string
  book_id?: number
  time_scope?: string
  mode?: 'category' | 'topic'
}) {
  const { data } = await apiClient.get<TopicGraphPayload>('/insights/topics', {
    params,
  })
  return data
}
