import { apiClient } from '@/api/client'
import type { ImportJob, ImportJobListResponse } from '@/types/import'

export async function fetchImportJobs() {
  const { data } = await apiClient.get<ImportJobListResponse>('/import/jobs')
  return data
}

export async function createImportJob(files: File[]) {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))

  const { data } = await apiClient.post<ImportJobListResponse>('/import/jobs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return data.items as ImportJob[]
}

export async function syncLocalVault() {
  const { data } = await apiClient.post<{ item: ImportJob; job_id?: string }>('/import/sync-local')
  return data
}
