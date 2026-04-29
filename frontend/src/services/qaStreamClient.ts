import { apiClient } from '@/api/client'
import type { QaAskPayload, QaStreamEventHandlers } from '@/types/qa'

// The backend streams QA as Server-Sent Events. Keeping the protocol parser in
// a small service keeps Pinia focused on state and makes future SSE tests easy.
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

    await readSseStream(response.body, handlers)
  } catch (error) {
    handlers.onError?.(error as Error)
    throw error
  }
}

export async function readSseStream(stream: ReadableStream<Uint8Array>, handlers: QaStreamEventHandlers) {
  const reader = stream.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE events are separated by a blank line. The last block may be partial,
    // so keep it in `buffer` until the next network chunk arrives.
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      dispatchSseBlock(block, handlers)
    }
  }
}

export function dispatchSseBlock(block: string, handlers: QaStreamEventHandlers) {
  const lines = block.split('\n')
  const eventLine = lines.find((line) => line.startsWith('event:'))
  const dataLine = lines.find((line) => line.startsWith('data:'))
  if (!eventLine || !dataLine) return

  const event = eventLine.replace('event:', '').trim()
  const payloadText = dataLine.replace('data:', '').trim()
  const parsed = JSON.parse(payloadText)

  if (event === 'meta') handlers.onMeta?.(parsed)
  if (event === 'status') handlers.onStatus?.(parsed)
  if (event === 'delta') handlers.onDelta?.(parsed)
  if (event === 'done') handlers.onDone?.(parsed)
}
