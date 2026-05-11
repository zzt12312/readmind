import type { QaAskPayload, QaStreamEventHandlers } from '@/types/qa'
import { buildQaResponse } from './payloads'

export async function streamStaticQuestion(payload: QaAskPayload, handlers: QaStreamEventHandlers, signal?: AbortSignal) {
  const response = buildQaResponse(payload)
  if (signal?.aborted) throw new DOMException('Aborted', 'AbortError')

  handlers.onMeta?.({
    question: response.question,
    references: response.references,
    retrieval_mode: response.retrieval_mode,
    query_rewrite: response.query_rewrite,
    evidence: response.evidence,
  })
  handlers.onStatus?.({
    phase: 'retrieving',
    label: '正在检索演示缓存',
    detail: '静态演示站会从内置阅读摘录里找引用，不会上传你的真实数据。',
  })

  await wait(180)
  handlers.onStatus?.({
    phase: 'fallback',
    label: '正在生成缓存回答',
    detail: '签签会基于演示引用组织一段可追溯回答。',
  })

  for (const chunk of response.answer.match(/.{1,34}/gs) ?? [response.answer]) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError')
    handlers.onDelta?.({ content: chunk })
    await wait(28)
  }

  handlers.onDone?.(response)
}

function wait(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}
