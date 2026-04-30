import { apiClient } from '@/api/client'
import type { NoteInsightExportPayload, NoteInsightExportResponse, NoteInsightReference, NoteInsightSections } from '@/types/note'

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

export async function exportNoteInsight(payload: NoteInsightExportPayload) {
  const { data } = await apiClient.post<NoteInsightExportResponse>('/notes/export-insight', payload)
  return data
}
