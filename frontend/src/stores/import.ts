import { defineStore } from 'pinia'
import { createImportJob, fetchImportJobs, syncLocalVault } from '@/api/modules/import'
import type { ImportJob, ImportMeta, ImportSyncFeedback } from '@/types/import'
import { pollAsyncJob } from '@/utils/jobPolling'

export const useImportStore = defineStore('import', {
  state: () => ({
    jobs: [] as ImportJob[],
    meta: {
      demo_mode: false,
      source_label: '本地 Obsidian 书籍阅读目录',
      description: '',
    } as ImportMeta,
    syncFeedback: {
      status: 'idle',
      title: '',
      message: '',
      book_count: 0,
      note_count: 0,
      category_count: 0,
    } as ImportSyncFeedback,
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
      this.syncFeedback = {
        status: 'processing',
        title: '正在同步本地书库',
        message: '系统正在扫描 Obsidian 目录、解析 Markdown，并更新书籍与笔记缓存。',
        book_count: 0,
        note_count: 0,
        category_count: 0,
      }
      try {
        const response = await syncLocalVault()
        this.meta = response.meta
        this.jobs = [response.item, ...this.jobs.filter((job) => job.id !== response.item.id)]
        if (response.job_id) {
          await this.pollSyncJob(response.job_id)
        } else {
          this.syncFeedback = buildSyncFeedback('success', response.item.result)
        }
      } finally {
        this.uploading = false
      }
    },
    async pollSyncJob(jobId: string) {
      await pollAsyncJob(jobId, {
        maxAttempts: 80,
        intervalMs: 1500,
        throwOnFailed: false,
        onProgress: (job) => {
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
        },
        onSuccess: (job) => {
          this.syncFeedback = {
            status: 'success',
            title: '本地书库同步完成',
            message: '书籍、摘录和分类已经更新到工作台。你可以继续查看数据看板，或者进入笔记工作台做二次整理。',
            book_count: job.result?.book_count ?? 0,
            note_count: job.result?.note_count ?? 0,
            category_count: job.result?.category_count ?? 0,
          }
        },
        onFailed: (job) => {
          this.syncFeedback = {
            status: 'failed',
            title: '本地书库同步失败',
            message: job.error_message || job.message || '同步没有成功，请检查 VAULT_ROOT 配置和目录权限后重试。',
            book_count: 0,
            note_count: 0,
            category_count: 0,
          }
        },
        onTimeout: () => {
          this.syncFeedback = {
            status: 'processing',
            title: '同步仍在后台进行',
            message: '书库较大时可能需要更久。你可以稍后刷新任务列表查看最新结果。',
            book_count: 0,
            note_count: 0,
            category_count: 0,
          }
        },
      })
    },
  },
})

function buildSyncFeedback(status: ImportSyncFeedback['status'], resultText: string): ImportSyncFeedback {
  const numbers = resultText.match(/\d+/g) ?? []
  return {
    status,
    title: status === 'success' ? '本地书库同步完成' : '同步状态已更新',
    message: status === 'success'
      ? '书籍和摘录已经更新到工作台。'
      : '同步任务状态已经更新。',
    book_count: Number(numbers[0] ?? 0),
    note_count: Number(numbers[1] ?? 0),
    category_count: 0,
  }
}
