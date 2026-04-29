import { onScopeDispose } from 'vue'
import { pollAsyncJob, type PollAsyncJobOptions } from '@/utils/jobPolling'

export function useJobPolling() {
  let canceled = false

  onScopeDispose(() => {
    canceled = true
  })

  async function pollJob(jobId: string, options: PollAsyncJobOptions = {}) {
    return pollAsyncJob(jobId, {
      ...options,
      shouldCancel: () => canceled || Boolean(options.shouldCancel?.()),
    })
  }

  return {
    pollJob,
  }
}
