import { apiClient } from '@/api/client'
import type { AsyncJob } from '@/types/job'

export async function fetchJobList(params?: {
  status?: string
  job_type?: string
  limit?: number
}) {
  const { data } = await apiClient.get<{ items: AsyncJob[] }>('/jobs', { params })
  return data
}

export async function fetchJobDetail(jobId: string) {
  const { data } = await apiClient.get<AsyncJob>(`/jobs/${jobId}`)
  return data
}

export async function retryJob(jobId: string) {
  const { data } = await apiClient.post<AsyncJob>(`/jobs/${jobId}/retry`)
  return data
}
