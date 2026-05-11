import { demoNotes } from './data'

export const demoJobs = [
  {
    id: 'demo-summary',
    job_type: 'book_summary',
    status: 'success',
    resource_type: 'book',
    resource_id: '1',
    payload: {},
    result: { book_id: 1, summary: '演示摘要已生成' },
    error_message: '',
    progress: 100,
    message: '《认知觉醒》摘要已从演示缓存返回',
    created_at: '2026-04-29 10:00',
    started_at: '2026-04-29 10:00',
    finished_at: '2026-04-29 10:01',
  },
  {
    id: 'demo-insight',
    job_type: 'notes_insight',
    status: 'success',
    resource_type: 'notes',
    resource_id: 'demo',
    payload: {},
    result: { references: demoNotes.slice(0, 2).map((note) => ({ book: note.book_title, chapter: note.chapter, excerpt: note.excerpt })) },
    error_message: '',
    progress: 100,
    message: 'AI 洞察已生成',
    created_at: '2026-04-29 10:03',
    started_at: '2026-04-29 10:03',
    finished_at: '2026-04-29 10:04',
  },
]
