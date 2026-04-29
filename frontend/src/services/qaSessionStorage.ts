import type { QaAskPayload, QaMessage, QaSession } from '@/types/qa'

const QA_HISTORY_KEY = 'readmind.qa.sessions'
const MAX_QA_SESSIONS = 12

export function createSessionTitle(question: string) {
  return question.trim().slice(0, 20) || '新对话'
}

export function createSessionId() {
  return `qa-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function createMessageId() {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
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

