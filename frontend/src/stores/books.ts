import { defineStore } from 'pinia'
import { fetchBookDetail, fetchBookList, fetchBookSummary, regenerateBookSummary } from '@/api/modules/books'
import { fetchJobDetail } from '@/api/modules/jobs'
import type { BookItem } from '@/types/book'

export const useBooksStore = defineStore('books', {
  state: () => ({
    items: [] as BookItem[],
    loading: false,
    currentBook: null as BookItem | null,
    currentSummary: '',
    summaryCache: {} as Record<number, string>,
    summaryWarmups: [] as number[],
    detailLoading: false,
    summaryLoading: false,
    regenerating: false,
    summaryJobId: '',
    summaryJobStatus: '' as '' | 'queued' | 'processing' | 'success' | 'failed' | 'canceled',
    summaryJobMessage: '',
  }),
  actions: {
    async load() {
      this.loading = true
      try {
        const data = await fetchBookList()
        this.items = data.items
      } finally {
        this.loading = false
      }
    },
    async loadDetail(id: number) {
      this.detailLoading = true
      try {
        this.currentBook = null
        this.currentSummary = ''
        const detail = await fetchBookDetail(id)
        this.currentBook = detail.book
        this.currentSummary = detail.summary || this.summaryCache[id] || ''
        if (detail.summary) {
          this.summaryCache[id] = detail.summary
          this.summaryJobId = ''
          this.summaryJobStatus = 'success'
          this.summaryJobMessage = ''
        }
      } finally {
        this.detailLoading = false
      }

      if (!this.currentSummary) {
        await this.ensureSummary(id)
      }
    },
    async regenerateSummary(id: number) {
      this.regenerating = true
      try {
        this.currentSummary = ''
        await this.ensureSummary(id, true)
      } finally {
        this.regenerating = false
      }
    },
    async prewarmSummary(id: number) {
      if (this.summaryCache[id] || this.summaryWarmups.includes(id)) {
        return
      }

      this.summaryWarmups = [...this.summaryWarmups, id]
      try {
        const summary = await fetchBookSummary(id)
        if (summary.summary) {
          this.summaryCache[id] = summary.summary
        }
        if (this.currentBook?.id === id && !this.currentSummary && summary.summary) {
          this.currentSummary = summary.summary
        }
      } finally {
        this.summaryWarmups = this.summaryWarmups.filter((item) => item !== id)
      }
    },
    async ensureSummary(id: number, force = false) {
      this.summaryLoading = true
      try {
        const response = force ? await regenerateBookSummary(id) : await fetchBookSummary(id)
        if (response.summary) {
          this.currentSummary = response.summary
          this.summaryCache[id] = response.summary
          this.summaryJobId = ''
          this.summaryJobStatus = 'success'
          this.summaryJobMessage = ''
          return
        }

        this.summaryJobId = response.job_id || ''
        this.summaryJobStatus = response.status || 'queued'
        this.summaryJobMessage = response.message || '摘要生成中'

        if (response.job_id) {
          await this.pollSummaryJob(response.job_id, id)
        }
      } catch (error) {
        this.summaryJobStatus = 'failed'
        this.summaryJobMessage = error instanceof Error ? error.message : '摘要生成失败'
      } finally {
        this.summaryLoading = false
      }
    },
    async pollSummaryJob(jobId: string, bookId: number) {
      // 轮询只负责等待结果，不阻塞页面其余内容；一旦任务成功，就把摘要写入当前视图和本地缓存。
      for (let index = 0; index < 40; index += 1) {
        const job = await fetchJobDetail(jobId)
        this.summaryJobId = job.id
        this.summaryJobStatus = job.status
        this.summaryJobMessage = job.message || ''

        if (job.status === 'success') {
          const summary = job.result?.summary || ''
          if (summary) {
            this.summaryCache[bookId] = summary
            if (this.currentBook?.id === bookId) {
              this.currentSummary = summary
            }
          }
          return
        }

        if (job.status === 'failed') {
          throw new Error(job.error_message || '摘要生成失败')
        }

        await new Promise((resolve) => window.setTimeout(resolve, 1500))
      }
      this.summaryJobMessage = '摘要仍在生成中，请稍后刷新查看'
    },
    findById(id: number) {
      return this.items.find((item) => item.id === id) ?? null
    },
  },
})
