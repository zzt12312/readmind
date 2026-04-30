import { apiClient } from '@/api/client'
import { streamQuestion } from '@/services/qaStreamClient'
import type { QaAskPayload, QaDepositPayload, QaDepositResponse, QaExportPayload, QaExportResponse, QaResponse } from '@/types/qa'

export { streamQuestion }

export async function askQuestion(payload: QaAskPayload) {
  const { data } = await apiClient.post<QaResponse>('/qa/ask', payload)
  return data
}

export async function exportQaSession(payload: QaExportPayload) {
  const { data } = await apiClient.post<QaExportResponse>('/qa/export', payload)
  return data
}

export async function createQaDeposit(payload: QaDepositPayload) {
  const { data } = await apiClient.post<QaDepositResponse>('/qa/deposits', payload)
  return data
}
