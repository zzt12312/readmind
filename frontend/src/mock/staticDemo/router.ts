import type { AxiosRequestConfig } from 'axios'
import type { QaAskPayload } from '@/types/qa'
import { demoBooks, demoNotes } from './data'
import { demoJobs } from './jobs'
import { buildAnalytics, buildBookSummary, buildDashboard, buildGraph, buildImportMeta, buildInsightSummary, buildNoteList, buildQaResponse, buildReviewResponse } from './payloads'

// Static demo mode replaces Axios requests in the browser.
// Keep URL routing here so page code does not need to know whether data is live or cached.
export function resolveStaticDemoResponse(config: AxiosRequestConfig) {
  const method = (config.method || 'get').toLowerCase()
  const url = String(config.url || '').split('?')[0]
  const normalizedUrl = url.replace(/^\/api/, '')

  if (normalizedUrl === '/llm/health') {
    return {
      provider: 'Static Demo',
      demo_mode: true,
      base_url: 'static-demo',
      model: 'cached-ai-preview',
      api_key_loaded: false,
      connected: false,
      fallback_mode: true,
      detail: '当前为静态演示模式，页面使用内置缓存展示 AI 效果。',
      embedding_model: 'static-cache',
      embedding_provider: 'static',
      embedding_status: 'ready',
      embedding_error: '',
    }
  }

  if (normalizedUrl === '/llm/embedding/warmup') {
    return { started: false, embedding_model: 'static-cache', embedding_provider: 'static', embedding_status: 'ready', embedding_error: '' }
  }

  if (normalizedUrl === '/dashboard/overview') return buildDashboard()
  if (normalizedUrl === '/analytics/overview') return buildAnalytics()
  if (normalizedUrl === '/books') return { items: demoBooks }

  const bookDetailMatch = normalizedUrl.match(/^\/books\/(\d+)$/)
  if (bookDetailMatch) {
    const book = demoBooks.find((item) => item.id === Number(bookDetailMatch[1])) ?? demoBooks[0]
    return { book, summary: buildBookSummary(book.id).summary }
  }

  const bookSummaryMatch = normalizedUrl.match(/^\/books\/(\d+)\/summary(?:\/regenerate)?$/)
  if (bookSummaryMatch) return buildBookSummary(Number(bookSummaryMatch[1]))

  if (normalizedUrl === '/notes') return buildNoteList(config)
  if (normalizedUrl === '/notes/summarize' && method === 'post') return buildInsightSummary()
  if (normalizedUrl === '/qa/ask' && method === 'post') return buildQaResponse((config.data ? JSON.parse(String(config.data)) : {}) as QaAskPayload)
  if (normalizedUrl === '/review/today') return buildReviewResponse(config)
  if (normalizedUrl === '/review/rate' && method === 'post') {
    return {
      progress: {
        note_id: 101,
        review_count: 2,
        mastery_score: 2,
        last_result: 'high',
        last_reviewed_at: new Date().toISOString(),
        next_review_at: '2026-05-03T09:00:00',
      },
      summary: [
        { label: '待复习', value: '5' },
        { label: '已完成', value: '1' },
        { label: '连续复习', value: '2 天' },
        { label: '掌握率', value: '67%' },
      ],
    }
  }

  if (normalizedUrl === '/insights/topics') return buildGraph()
  if (normalizedUrl === '/import/jobs' && method === 'post') {
    return {
      items: [
        {
          id: 'static-demo-upload',
          file_name: '模拟上传文件.md',
          status: 'success',
          progress: 100,
          result: '演示模式已模拟解析完成',
          source: 'static-demo',
          created_at: '2026-04-29 10:05',
          finished_at: '2026-04-29 10:05',
        },
      ],
      meta: buildImportMeta(),
    }
  }

  if (normalizedUrl === '/import/jobs') {
    return {
      items: [
        {
          id: 'static-demo-import',
          file_name: '静态演示缓存',
          status: 'success',
          progress: 100,
          result: `${demoBooks.length} 本 / ${demoNotes.length} 条`,
          source: 'static-demo',
          created_at: '2026-04-29 10:00',
          finished_at: '2026-04-29 10:00',
        },
      ],
      meta: buildImportMeta(),
    }
  }

  if (normalizedUrl === '/import/sync-local' && method === 'post') {
    return {
      item: {
        id: 'static-demo-sync',
        file_name: '静态演示缓存',
        status: 'success',
        progress: 100,
        result: `${demoBooks.length} 本 / ${demoNotes.length} 条`,
        source: 'static-demo',
        created_at: '2026-04-29 10:00',
        finished_at: '2026-04-29 10:00',
      },
      meta: buildImportMeta(),
    }
  }

  if (normalizedUrl === '/jobs') return { items: demoJobs }
  if (/^\/jobs\/[^/]+$/.test(normalizedUrl)) return demoJobs[0]
  if (/^\/jobs\/[^/]+\/retry$/.test(normalizedUrl)) return { ...demoJobs[0], status: 'processing', progress: 20, message: '演示任务已重新加入队列' }

  return undefined
}
