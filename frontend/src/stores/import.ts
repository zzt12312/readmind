import { defineStore } from 'pinia'
import { fetchJobDetail } from '@/api/modules/jobs'
import { createImportJob, fetchImportJobs, syncLocalVault } from '@/api/modules/import'
import type { ImportJob, ImportMeta } from '@/types/import'

export const useImportStore = defineStore('import', {
  state: () => ({
    jobs: [] as ImportJob[],
    meta: {
      demo_mode: false,
      source_label: '本地 Obsidian 书籍阅读目录',
      description: '',
    } as ImportMeta,
    loading: false,
    uploading: false,
  }),
  actions: {
    async load() {
      this.loading = true
      try {
        const data = await fetchImportJobs()
        this.jobs = data.items
        this.meta = data.meta
      } finally {
        this.loading = false
      }
    },
    async upload(files: File[]) {
      this.uploading = true
      try {
        const created = await createImportJob(files)
        this.jobs = [...created, ...this.jobs]
      } finally {
        this.uploading = false
      }
    },
    async syncLocal() {
      this.uploading = true
      try {
        const response = await syncLocalVault()
        this.meta = response.meta
        this.jobs = [response.item, ...this.jobs.filter((job) => job.id !== response.item.id)]
        if (response.job_id) {
          await this.pollSyncJob(response.job_id)
        }
      } finally {
        this.uploading = false
      }
    },
    async pollSyncJob(jobId: string) {
      for (let index = 0; index < 80; index += 1) {
        const job = await fetchJobDetail(jobId)
        const mapped: ImportJob = {
          id: job.id,
          file_name: '本地 Obsidian 书籍阅读目录',
          status: job.status === 'failed' ? 'failed' : job.status === 'success' ? 'success' : 'processing',
          progress: job.progress,
          result:
            job.status === 'success'
              ? `${job.result?.book_count ?? 0} 本 / ${job.result?.note_count ?? 0} 条`
              : (job.message || job.error_message || '同步中'),
        }
        this.jobs = [mapped, ...this.jobs.filter((item) => item.id !== mapped.id)]

        if (job.status === 'success' || job.status === 'failed') {
          return
        }

        await new Promise((resolve) => window.setTimeout(resolve, 1500))
      }
    },
  },
})
