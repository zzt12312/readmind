import { apiClient } from '@/api/client'
import type { ReviewLevel, ReviewRateResponse, ReviewTodayResponse } from '@/types/review'

export async function fetchTodayReview(params?: { daily_goal?: number; queue?: string }) {
  const { data } = await apiClient.get<ReviewTodayResponse>('/review/today', { params })
  return data
}

export async function fetchScopedReview(params: { tag?: string; book_id?: number; daily_goal?: number; queue?: string }) {
  const { data } = await apiClient.get<ReviewTodayResponse>('/review/today', { params })
  return data
}

export async function submitReviewRating(noteId: number, level: ReviewLevel) {
  const { data } = await apiClient.post<ReviewRateResponse>('/review/rate', {
    note_id: noteId,
    level,
  })
  return data
}
