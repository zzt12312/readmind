import { apiClient } from '@/api/client'
import type { ReviewLevel, ReviewRateResponse, ReviewTodayResponse } from '@/types/review'

export async function fetchTodayReview() {
  const { data } = await apiClient.get<ReviewTodayResponse>('/review/today')
  return data
}

export async function submitReviewRating(noteId: number, level: ReviewLevel) {
  const { data } = await apiClient.post<ReviewRateResponse>('/review/rate', {
    note_id: noteId,
    level,
  })
  return data
}
