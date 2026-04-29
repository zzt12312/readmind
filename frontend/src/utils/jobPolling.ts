import { fetchJobDetail } from '@/api/modules/jobs'
import type { AsyncJob } from '@/types/job'

export interface PollAsyncJobOptions {
  intervalMs?: number
  maxAttempts?: number
  throwOnFailed?: boolean
  shouldCancel?: () => boolean
  onProgress?: (job: AsyncJob) => void
  onSuccess?: (job: AsyncJob) => void
  onFailed?: (job: AsyncJob) => void
  onTimeout?: () => void
}

function delay(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}

export async function pollAsyncJob(jobId: string, options: PollAsyncJobOptions = {}) {
  const intervalMs = options.intervalMs ?? 1500
  const maxAttempts = options.maxAttempts ?? 40
  const throwOnFailed = options.throwOnFailed ?? true

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    if (options.shouldCancel?.()) return null

    const job = await fetchJobDetail(jobId)
    options.onProgress?.(job)

    if (job.status === 'success') {
      options.onSuccess?.(job)
      return job
    }

    if (job.status === 'failed') {
      options.onFailed?.(job)
      if (throwOnFailed) {
        throw new Error(job.error_message || job.message || '后台任务执行失败')
      }
      return job
    }

    await delay(intervalMs)
  }

  options.onTimeout?.()
  return null
}
