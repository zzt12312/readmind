import type { QaAskPayload, QaInsightCard, QaMessage, QaQuestionWorkspace, QaReviewSeed, QaSavedAnswer, QaSession, QaUnderstanding } from '@/types/qa'

const QA_HISTORY_KEY = 'readmind.qa.sessions'
const QA_SAVED_ANSWERS_KEY = 'readmind.qa.savedAnswers'
const QA_WORKSPACES_KEY = 'readmind.qa.questionWorkspaces'
const QA_INSIGHT_CARDS_KEY = 'readmind.qa.insightCards'
const QA_UNDERSTANDINGS_KEY = 'readmind.qa.understandings'
const QA_REVIEW_SEEDS_KEY = 'readmind.qa.reviewSeeds'
const MAX_QA_SESSIONS = 12
const MAX_SAVED_ANSWERS = 24
const MAX_QUESTION_WORKSPACES = 18
const MAX_INSIGHT_CARDS = 36
const MAX_UNDERSTANDINGS = 24
const MAX_REVIEW_SEEDS = 36

export function createSessionTitle(question: string) {
  return question.trim().slice(0, 20) || '新对话'
}

export function createSessionId() {
  return `qa-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createMessageId() {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createSavedAnswerId() {
  return `saved-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createQuestionWorkspaceId() {
  return `qws-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createInsightCardId() {
  return `insight-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createUnderstandingId() {
  return `understanding-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createReviewSeedId() {
  return `review-seed-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createSession(payload: QaAskPayload): QaSession {
  return {
    id: createSessionId(),
    title: createSessionTitle(payload.question),
    scope: payload.scope ?? 'all-books',
    book_id: payload.book_id,
    updated_at: new Date().toISOString(),
    pinned: false,
    messages: [],
  }
}

export function sortSessions(sessions: QaSession[]) {
  return [...sessions].sort((left, right) => {
    if (Boolean(left.pinned) !== Boolean(right.pinned)) {
      return left.pinned ? -1 : 1
    }
    return new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime()
  })
}

export function normalizeMessage(message: Partial<QaMessage>): QaMessage {
  return {
    id: message.id ?? createMessageId(),
    role: message.role === 'assistant' ? 'assistant' : 'user',
    content: message.content ?? '',
    references: message.references ?? [],
    feedback: message.feedback ?? null,
  }
}

// Session storage can outlive app versions, so normalize every field on read.
export function normalizeSession(session: Partial<QaSession>): QaSession {
  return {
    id: session.id ?? createSessionId(),
    title: session.title ?? '新对话',
    scope: session.scope === 'current-book' ? 'current-book' : 'all-books',
    book_id: session.book_id,
    updated_at: session.updated_at ?? new Date().toISOString(),
    pinned: Boolean(session.pinned),
    messages: (session.messages ?? []).map((message) => normalizeMessage(message)),
  }
}

export function loadQaSessions(): QaSession[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(QA_HISTORY_KEY)
    return raw ? (JSON.parse(raw) as Partial<QaSession>[]).map((session) => normalizeSession(session)) : []
  } catch {
    return []
  }
}

export function saveQaSessions(sessions: QaSession[]) {
  if (typeof window === 'undefined') return sortSessions(sessions).slice(0, MAX_QA_SESSIONS)

  const normalized = sortSessions(sessions).slice(0, MAX_QA_SESSIONS)
  window.localStorage.setItem(QA_HISTORY_KEY, JSON.stringify(normalized))
  return normalized
}

export function normalizeSavedAnswer(item: Partial<QaSavedAnswer>): QaSavedAnswer {
  return {
    id: item.id ?? createSavedAnswerId(),
    session_id: item.session_id ?? null,
    message_id: item.message_id ?? createMessageId(),
    title: item.title ?? '收藏回答',
    question: item.question ?? '',
    answer: item.answer ?? '',
    references: item.references ?? [],
    scope: item.scope === 'current-book' ? 'current-book' : 'all-books',
    book_id: item.book_id ?? null,
    saved_at: item.saved_at ?? new Date().toISOString(),
  }
}

export function sortSavedAnswers(items: QaSavedAnswer[]) {
  return [...items].sort((left, right) => new Date(right.saved_at).getTime() - new Date(left.saved_at).getTime())
}

export function loadSavedAnswers(): QaSavedAnswer[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(QA_SAVED_ANSWERS_KEY)
    return raw ? sortSavedAnswers((JSON.parse(raw) as Partial<QaSavedAnswer>[]).map(normalizeSavedAnswer)) : []
  } catch {
    return []
  }
}

export function saveSavedAnswers(items: QaSavedAnswer[]) {
  const normalized = sortSavedAnswers(items).slice(0, MAX_SAVED_ANSWERS)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(QA_SAVED_ANSWERS_KEY, JSON.stringify(normalized))
  }
  return normalized
}

export function normalizeQuestionWorkspace(item: Partial<QaQuestionWorkspace>): QaQuestionWorkspace {
  const statusValues = new Set(['open', 'writing', 'reviewing'])
  return {
    id: item.id ?? createQuestionWorkspaceId(),
    title: item.title ?? createSessionTitle(item.question ?? '问题工作台'),
    question: item.question ?? '',
    latest_answer: item.latest_answer ?? '',
    references: item.references ?? [],
    scope: item.scope === 'current-book' ? 'current-book' : 'all-books',
    book_id: item.book_id ?? null,
    status: statusValues.has(String(item.status)) ? item.status as QaQuestionWorkspace['status'] : 'open',
    evidence_count: Number(item.evidence_count ?? item.references?.length ?? 0),
    next_action: item.next_action ?? '继续追问，补充更多引用证据。',
    created_at: item.created_at ?? new Date().toISOString(),
    updated_at: item.updated_at ?? new Date().toISOString(),
  }
}

export function sortQuestionWorkspaces(items: QaQuestionWorkspace[]) {
  return [...items].sort((left, right) => new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime())
}

export function loadQuestionWorkspaces(): QaQuestionWorkspace[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(QA_WORKSPACES_KEY)
    return raw ? sortQuestionWorkspaces((JSON.parse(raw) as Partial<QaQuestionWorkspace>[]).map(normalizeQuestionWorkspace)) : []
  } catch {
    return []
  }
}

export function saveQuestionWorkspaces(items: QaQuestionWorkspace[]) {
  const normalized = sortQuestionWorkspaces(items).slice(0, MAX_QUESTION_WORKSPACES)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(QA_WORKSPACES_KEY, JSON.stringify(normalized))
  }
  return normalized
}

export function sortByCreatedAt<T extends { created_at: string }>(items: T[]) {
  return [...items].sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime())
}

export function normalizeInsightCard(item: Partial<QaInsightCard>): QaInsightCard {
  return {
    id: item.id ?? createInsightCardId(),
    title: item.title ?? createSessionTitle(item.question ?? '洞察卡片'),
    question: item.question ?? '',
    summary: item.summary ?? '',
    references: item.references ?? [],
    created_at: item.created_at ?? new Date().toISOString(),
  }
}

export function loadInsightCards(): QaInsightCard[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(QA_INSIGHT_CARDS_KEY)
    return raw ? sortByCreatedAt((JSON.parse(raw) as Partial<QaInsightCard>[]).map(normalizeInsightCard)) : []
  } catch {
    return []
  }
}

export function saveInsightCards(items: QaInsightCard[]) {
  const normalized = sortByCreatedAt(items).slice(0, MAX_INSIGHT_CARDS)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(QA_INSIGHT_CARDS_KEY, JSON.stringify(normalized))
  }
  return normalized
}

export function normalizeUnderstanding(item: Partial<QaUnderstanding>): QaUnderstanding {
  return {
    id: item.id ?? createUnderstandingId(),
    title: item.title ?? createSessionTitle(item.question ?? '我的理解'),
    question: item.question ?? '',
    content: item.content ?? '',
    references: item.references ?? [],
    created_at: item.created_at ?? new Date().toISOString(),
    updated_at: item.updated_at ?? item.created_at ?? new Date().toISOString(),
  }
}

export function loadUnderstandings(): QaUnderstanding[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(QA_UNDERSTANDINGS_KEY)
    return raw ? sortByCreatedAt((JSON.parse(raw) as Partial<QaUnderstanding>[]).map(normalizeUnderstanding)) : []
  } catch {
    return []
  }
}

export function saveUnderstandings(items: QaUnderstanding[]) {
  const normalized = sortByCreatedAt(items).slice(0, MAX_UNDERSTANDINGS)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(QA_UNDERSTANDINGS_KEY, JSON.stringify(normalized))
  }
  return normalized
}

export function normalizeReviewSeed(item: Partial<QaReviewSeed>): QaReviewSeed {
  return {
    id: item.id ?? createReviewSeedId(),
    title: item.title ?? createSessionTitle(item.question ?? '复习线索'),
    question: item.question ?? '',
    references: item.references ?? [],
    book_id: item.book_id ?? item.references?.[0]?.book_id ?? null,
    note_ids: item.note_ids ?? [...new Set((item.references ?? []).map((reference) => reference.note_id))],
    created_at: item.created_at ?? new Date().toISOString(),
  }
}

export function loadReviewSeeds(): QaReviewSeed[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(QA_REVIEW_SEEDS_KEY)
    return raw ? sortByCreatedAt((JSON.parse(raw) as Partial<QaReviewSeed>[]).map(normalizeReviewSeed)) : []
  } catch {
    return []
  }
}

export function saveReviewSeeds(items: QaReviewSeed[]) {
  const normalized = sortByCreatedAt(items).slice(0, MAX_REVIEW_SEEDS)
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(QA_REVIEW_SEEDS_KEY, JSON.stringify(normalized))
  }
  return normalized
}

export function clearQaLocalData() {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(QA_HISTORY_KEY)
  window.localStorage.removeItem(QA_SAVED_ANSWERS_KEY)
  window.localStorage.removeItem(QA_WORKSPACES_KEY)
  window.localStorage.removeItem(QA_INSIGHT_CARDS_KEY)
  window.localStorage.removeItem(QA_UNDERSTANDINGS_KEY)
  window.localStorage.removeItem(QA_REVIEW_SEEDS_KEY)
}
