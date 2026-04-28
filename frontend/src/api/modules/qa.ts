import { apiClient } from '@/api/client'
import type { QaAskPayload, QaResponse, QaStreamEventHandlers } from '@/types/qa'

export async function askQuestion(payload: QaAskPayload) {
  const { data } = await apiClient.post<QaResponse>('/qa/ask', payload)
  return data
}

export async function streamQuestion(
  payload: QaAskPayload,
  handlers: QaStreamEventHandlers,
  signal?: AbortSignal,
) {
  try {
    const response = await fetch(`${apiClient.defaults.baseURL}/qa/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal,
    })

    if (!response.ok || !response.body) {
      throw new Error(`Streaming request failed: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // 后端按 SSE 格式分块推送，这里把不完整片段先留在 buffer 中，等下一次继续拼接。
      const blocks = buffer.split('\n\n')
      buffer = blocks.pop() ?? ''

      for (const block of blocks) {
        const lines = block.split('\n')
        const eventLine = lines.find((line) => line.startsWith('event:'))
        const dataLine = lines.find((line) => line.startsWith('data:'))
        if (!eventLine || !dataLine) continue

        const event = eventLine.replace('event:', '').trim()
        const payloadText = dataLine.replace('data:', '').trim()
        const parsed = JSON.parse(payloadText)

        if (event === 'meta') handlers.onMeta?.(parsed)
        if (event === 'status') handlers.onStatus?.(parsed)
        if (event === 'delta') handlers.onDelta?.(parsed)
        if (event === 'done') handlers.onDone?.(parsed)
      }
    }
  } catch (error) {
    handlers.onError?.(error as Error)
    throw error
  }
}
