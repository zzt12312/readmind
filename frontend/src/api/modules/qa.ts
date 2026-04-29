import { apiClient } from '@/api/client'
import { streamQuestion } from '@/services/qaStreamClient'
import type { QaAskPayload, QaResponse } from '@/types/qa'

export { streamQuestion }

export async function askQuestion(payload: QaAskPayload) {
  const { data } = await apiClient.post<QaResponse>('/qa/ask', payload)
  return data
}
