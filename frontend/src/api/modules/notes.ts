import { apiClient } from '@/api/client'
import type { NoteListResponse } from '@/types/note'

export async function fetchNoteList(params?: {
  book_id?: number
  q?: string
  note_id?: number
  category?: string
  tag?: string
  chapter?: string
  sort?: string
  page?: number
  per_page?: number
}) {
  const { data } = await apiClient.get<NoteListResponse>('/notes', { params })
  return data
}
