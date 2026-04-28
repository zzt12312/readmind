import { apiClient } from '@/api/client'
import type { NoteInsightReference, NoteInsightSections } from '@/types/note'

export async function summarizeFilteredNotes(payload: {
  book_id?: number
  q?: string
  category?: string
  tag?: string
  chapter?: string
  sort?: string
  prompt?: string
}) {
  const { data } = await apiClient.post<{
    summary: string
    references: NoteInsightReference[]
    sections: NoteInsightSections | null
    status?: 'queued' | 'processing' | 'success'
    job_id?: string
    message?: string
  }>('/notes/summarize', payload)
  return data
}
