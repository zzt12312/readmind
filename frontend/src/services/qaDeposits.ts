import { createQaDeposit } from '@/api/modules/qa'
import {
  createInsightCardId,
  createQuestionWorkspaceId,
  createReviewSeedId,
  createSessionTitle,
  createUnderstandingId,
} from '@/services/qaSessionStorage'
import type {
  QaInsightCard,
  QaMessage,
  QaQuestionWorkspace,
  QaReviewSeed,
  QaUnderstanding,
} from '@/types/qa'

export interface QaAnswerContext {
  question: string
  title: string
  answer: string
  references: NonNullable<QaMessage['references']>
}

interface DepositScope {
  scope: 'all-books' | 'current-book'
  bookId: number | null
}

export function getQaAnswerContext(messages: QaMessage[], messageId: string, fallbackTitle = '未命名问题'): QaAnswerContext {
  const assistantIndex = messages.findIndex((message) => message.id === messageId)
  const assistantMessage = messages[assistantIndex]
  if (!assistantMessage || assistantMessage.role !== 'assistant' || !assistantMessage.content.trim()) {
    throw new Error('当前没有可沉淀的回答')
  }

  const userMessage = [...messages.slice(0, assistantIndex)]
    .reverse()
    .find((message) => message.role === 'user')
  const question = userMessage?.content.trim() || fallbackTitle

  return {
    question,
    title: createSessionTitle(question),
    answer: assistantMessage.content,
    references: assistantMessage.references ?? [],
  }
}

export function buildQuestionWorkspace(
  context: QaAnswerContext,
  scope: DepositScope,
  existing?: QaQuestionWorkspace,
): QaQuestionWorkspace {
  const now = new Date().toISOString()
  return {
    id: existing?.id ?? createQuestionWorkspaceId(),
    title: existing?.title || context.title,
    question: context.question,
    latest_answer: context.answer,
    references: context.references,
    scope: scope.scope,
    book_id: scope.bookId,
    status: existing?.status ?? 'open',
    evidence_count: context.references.length,
    next_action: context.references.length >= 3
      ? '证据已经比较充分，可以整理成写作素材或进入复习。'
      : '继续追问，补充更多引用证据。',
    created_at: existing?.created_at ?? now,
    updated_at: now,
  }
}

export async function createInsightCardFromAnswer(
  context: QaAnswerContext,
  scope: DepositScope,
): Promise<QaInsightCard> {
  const payload = {
    deposit_type: 'insight_card' as const,
    title: `洞察：${context.title}`,
    question: context.question,
    content: buildInsightSummary(context.answer),
    references: context.references,
    scope: scope.scope,
    book_id: scope.bookId,
  }
  await createQaDeposit(payload)
  return {
    id: createInsightCardId(),
    title: payload.title,
    question: payload.question,
    summary: payload.content,
    references: payload.references,
    created_at: new Date().toISOString(),
  }
}

export async function createUnderstandingFromAnswer(
  context: QaAnswerContext,
  scope: DepositScope,
  existing?: QaUnderstanding,
): Promise<QaUnderstanding> {
  const now = new Date().toISOString()
  const payload = {
    deposit_type: 'understanding' as const,
    title: existing?.title || `我的理解：${context.title}`,
    question: context.question,
    content: context.answer,
    references: context.references,
    scope: scope.scope,
    book_id: scope.bookId,
  }
  await createQaDeposit(payload)
  return {
    id: existing?.id ?? createUnderstandingId(),
    title: payload.title,
    question: payload.question,
    content: payload.content,
    references: payload.references,
    created_at: existing?.created_at ?? now,
    updated_at: now,
  }
}

export async function createReviewSeedFromAnswer(
  context: QaAnswerContext,
  scope: DepositScope,
): Promise<QaReviewSeed> {
  if (!context.references.length) {
    throw new Error('当前回答没有引用，暂时无法加入复习')
  }
  const noteIds = [...new Set(context.references.map((reference) => reference.note_id))]
  const payload = {
    deposit_type: 'review_seed' as const,
    title: `复习：${context.title}`,
    question: context.question,
    content: context.answer,
    references: context.references,
    scope: scope.scope,
    book_id: context.references[0]?.book_id ?? scope.bookId,
    note_ids: noteIds,
    status: 'queued',
  }
  await createQaDeposit(payload)
  return {
    id: createReviewSeedId(),
    title: payload.title,
    question: payload.question,
    references: payload.references,
    book_id: payload.book_id,
    note_ids: noteIds,
    created_at: new Date().toISOString(),
  }
}

function buildInsightSummary(answer: string) {
  const normalized = answer.replace(/\s+/g, ' ').trim()
  if (normalized.length <= 220) return normalized
  return `${normalized.slice(0, 220)}...`
}
