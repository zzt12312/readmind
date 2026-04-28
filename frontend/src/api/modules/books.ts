import { apiClient } from '@/api/client'
import type { BookDetailResponse, BookListResponse, BookSummaryResponse } from '@/types/book'

export async function fetchBookList() {
  const { data } = await apiClient.get<BookListResponse>('/books')
  return data
}

export async function fetchBookDetail(id: number) {
  const { data } = await apiClient.get<BookDetailResponse>(`/books/${id}`)
  return data
}

export async function fetchBookSummary(id: number) {
  const { data } = await apiClient.get<BookSummaryResponse>(`/books/${id}/summary`)
  return data
}

export async function regenerateBookSummary(id: number) {
  const { data } = await apiClient.post<BookSummaryResponse>(`/books/${id}/summary/regenerate`)
  return data
}
