import { defineStore } from 'pinia'
import { streamQuestion } from '@/api/modules/qa'
import type { QaAskPayload, QaMessage, QaReference, QaSession, QaStatusPayload, QueryRewriteSummary } from '@/types/qa'

const QA_HISTORY_KEY = 'readmind.qa.sessions'

function createSessionTitle(question: string) {
  return question.trim().slice(0, 20) || '新对话'
}

function createSessionId() {
  return `qa-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function createMessageId() {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function sortSessions(sessions: QaSession[]) {
  return [...sessions].sort((left, right) => {
    if (Boolean(left.pinned) !== Boolean(right.pinned)) {
      return left.pinned ? -1 : 1
    }
    return new Date(right.updated_at).getTime() - new Date(left.updated_at).getTime()
  })
}

function normalizeMessage(message: Partial<QaMessage>): QaMessage {
  return {
    id: message.id ?? createMessageId(),
    role: message.role === 'assistant' ? 'assistant' : 'user',
    content: message.content ?? '',
    references: message.references ?? [],
    feedback: message.feedback ?? null,
  }
}

// 历史结构会随着功能演进扩展，读取时统一补齐默认字段，避免旧数据导致页面异常。
function normalizeSession(session: Partial<QaSession>): QaSession {
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

// 历史会话保存在本地，用户刷新页面后仍能恢复最近的问答上下文。
function safeLoadSessions(): QaSession[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(QA_HISTORY_KEY)
    return raw ? (JSON.parse(raw) as Partial<QaSession>[]).map((session) => normalizeSession(session)) : []
  } catch {
    return []
  }
}

export const useQaStore = defineStore('qa', {
  state: () => ({
    question: '',
    answer: '',
    references: [] as QaReference[],
    messages: [] as QaMessage[],
    sessions: [] as QaSession[],
    currentSessionId: null as string | null,
    loading: false,
    stopped: false,
    scope: 'all-books' as 'all-books' | 'current-book',
    bookId: null as number | null,
    abortController: null as AbortController | null,
    status: {
      phase: 'idle',
      label: '等待提问',
      detail: '从你的个人读书笔记中提问，系统会先检索引用，再组织回答。',
    } as QaStatusPayload,
    generationMode: 'llm' as 'llm' | 'fallback',
    retrievalMode: 'hybrid' as string,
    fallbackReason: '',
    errorMessage: '',
    queryRewrite: null as QueryRewriteSummary | null,
  }),
  getters: {
    currentSession(state) {
      return state.sessions.find((session) => session.id === state.currentSessionId) ?? null
    },
  },
  actions: {
    hydrateSessions() {
      this.sessions = sortSessions(safeLoadSessions())
    },
    persistSessions() {
      if (typeof window === 'undefined') return
      this.sessions = sortSessions(this.sessions).slice(0, 12)
      window.localStorage.setItem(QA_HISTORY_KEY, JSON.stringify(this.sessions))
    },
    // 会话在首次提问时创建，后续连续追问都复用同一个 session，便于恢复上下文。
    ensureSession(payload: QaAskPayload) {
      if (this.currentSessionId) return this.currentSessionId

      const session: QaSession = {
        id: createSessionId(),
        title: createSessionTitle(payload.question),
        scope: payload.scope ?? 'all-books',
        book_id: payload.book_id,
        updated_at: new Date().toISOString(),
        pinned: false,
        messages: [],
      }
      this.sessions = [session, ...this.sessions]
      this.currentSessionId = session.id
      this.persistSessions()
      return session.id
    },
    updateSessionMessages(messages: QaMessage[], payload?: QaAskPayload) {
      if (!this.currentSessionId) return
      this.sessions = this.sessions.map((session) =>
        session.id === this.currentSessionId
          ? {
              ...session,
              title: createSessionTitle(payload?.question ?? session.title),
              scope: payload?.scope ?? session.scope,
              book_id: payload?.book_id ?? session.book_id,
              updated_at: new Date().toISOString(),
              messages,
            }
          : session,
      )
      this.persistSessions()
    },
    renameSession(sessionId: string, title: string) {
      const nextTitle = title.trim()
      if (!nextTitle) return
      this.sessions = this.sessions.map((session) =>
        session.id === sessionId ? { ...session, title: nextTitle, updated_at: new Date().toISOString() } : session,
      )
      this.persistSessions()
    },
    togglePinSession(sessionId: string) {
      this.sessions = this.sessions.map((session) =>
        session.id === sessionId
          ? { ...session, pinned: !session.pinned, updated_at: new Date().toISOString() }
          : session,
      )
      this.persistSessions()
    },
    deleteSession(sessionId: string) {
      const nextSessions = this.sessions.filter((session) => session.id !== sessionId)
      this.sessions = nextSessions
      if (this.currentSessionId === sessionId) {
        const nextActiveSession = nextSessions[0]
        if (nextActiveSession) {
          this.restoreSession(nextActiveSession.id)
          this.persistSessions()
        } else {
          this.resetConversation()
        }
      } else {
        this.persistSessions()
      }
    },
    restoreSession(sessionId: string) {
      const session = this.sessions.find((item) => item.id === sessionId)
      if (!session) return
      this.currentSessionId = session.id
      this.messages = session.messages
      this.scope = session.scope
      this.bookId = session.book_id ?? null
      const lastUser = [...session.messages].reverse().find((message) => message.role === 'user')
      const lastAssistant = [...session.messages].reverse().find((message) => message.role === 'assistant')
      this.question = lastUser?.content ?? ''
      this.answer = lastAssistant?.content ?? ''
      this.references = lastAssistant?.references ?? []
      this.errorMessage = ''
      this.fallbackReason = ''
      this.queryRewrite = null
      this.generationMode = 'llm'
      this.status = {
        phase: lastAssistant?.content ? 'success' : 'idle',
        label: lastAssistant?.content ? '已恢复历史会话' : '等待提问',
        detail: lastAssistant?.content
          ? '这是之前的问答结果，你可以继续追问或重新生成。'
          : '从你的个人读书笔记中提问，系统会先检索引用，再组织回答。',
      }
    },
    setMessageFeedback(messageId: string, feedback: 'up' | 'down') {
      const nextMessages = this.messages.map((message) =>
        message.id === messageId
          ? {
              ...message,
              feedback: message.feedback === feedback ? null : feedback,
            }
          : message,
      )
      this.messages = nextMessages
      this.updateSessionMessages(nextMessages)
    },
    async ask(payload: QaAskPayload) {
      this.loading = true
      this.stopped = false
      this.errorMessage = ''
      this.fallbackReason = ''
      this.queryRewrite = null
      this.generationMode = 'llm'
      this.status = {
        phase: 'retrieving',
        label: '正在检索相关笔记',
        detail: '先从你的个人笔记里找出最相关的摘录。',
      }
      this.abortController = new AbortController()
      try {
        this.ensureSession(payload)
        const history = payload.history ?? this.messages
        // 先把“用户问题 + 空助手气泡”插入界面，保证流式回答开始前页面就有即时反馈。
        const nextMessages: QaMessage[] = [
          ...history,
          { id: createMessageId(), role: 'user', content: payload.question, references: [], feedback: null },
          { id: createMessageId(), role: 'assistant', content: '', references: [], feedback: null },
        ]
        this.messages = nextMessages
        this.updateSessionMessages(nextMessages, payload)
        await streamQuestion(
          {
            ...payload,
            history,
          },
          {
            onMeta: (data) => {
              this.question = data.question
              this.references = data.references
              this.scope = payload.scope ?? 'all-books'
              this.bookId = payload.book_id ?? null
              this.retrievalMode = data.retrieval_mode ?? 'hybrid'
              this.queryRewrite = data.query_rewrite ?? null
            },
            onStatus: (data) => {
              this.status = data
            },
            onDelta: (data) => {
              const assistantMessage = this.messages[this.messages.length - 1]
              if (assistantMessage?.role === 'assistant') {
                assistantMessage.content += data.content
                this.updateSessionMessages([...this.messages], payload)
              }
            },
            onDone: (data) => {
              this.question = data.question
              this.answer = data.answer
              this.references = data.references
              this.generationMode = data.generation_mode ?? 'llm'
              this.retrievalMode = data.retrieval_mode ?? this.retrievalMode
              this.fallbackReason = data.fallback_reason ?? ''
              this.queryRewrite = data.query_rewrite ?? this.queryRewrite
              this.status = {
                phase: 'success',
                label: data.generation_mode === 'fallback' ? '已生成回退回答' : '回答生成完成',
                detail:
                  data.generation_mode === 'fallback'
                    ? '本轮回答基于检索结果回退生成，引用仍然有效。'
                    : '你可以继续追问，或者查看右侧引用来源。',
              }
              const assistantMessage = this.messages[this.messages.length - 1]
              if (assistantMessage?.role === 'assistant') {
                assistantMessage.content = data.answer
                assistantMessage.references = data.references
                assistantMessage.feedback = assistantMessage.feedback ?? null
              }
              this.updateSessionMessages([...this.messages], payload)
            },
            onError: (error) => {
              this.errorMessage = error.message
              this.status = {
                phase: 'failed',
                label: '问答生成失败',
                detail: '这次回答没有顺利完成，你可以稍后重试或重新生成。',
              }
            },
          },
          this.abortController.signal,
        )
      } catch (error) {
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
          throw error
        }
        this.status = {
          phase: 'idle',
          label: '已停止本轮生成',
          detail: '你可以继续追问，也可以点击“重新生成”恢复这一轮回答。',
        }
      } finally {
        this.loading = false
        this.abortController = null
      }
    },
    stopStreaming() {
      if (!this.loading || !this.abortController) return
      this.stopped = true
      this.abortController.abort()
    },
    // 重新生成只保留“上一轮用户提问之前”的历史，再基于同一问题重新走一遍流式回答。
    async regenerateLastAnswer() {
      const lastUserIndex = [...this.messages]
        .map((message, index) => ({ message, index }))
        .reverse()
        .find((entry) => entry.message.role === 'user')

      if (!lastUserIndex) return

      const question = lastUserIndex.message.content
      const history = this.messages.slice(0, lastUserIndex.index)
      this.messages = history
      this.updateSessionMessages(history, {
        question,
        scope: this.scope,
        book_id: this.bookId ?? undefined,
      })
      await this.ask({
        question,
        scope: this.scope,
        book_id: this.bookId ?? undefined,
        history,
      })
    },
    resetConversation() {
      this.stopStreaming()
      this.question = ''
      this.answer = ''
      this.references = []
      this.messages = []
      this.currentSessionId = null
      this.stopped = false
      this.errorMessage = ''
      this.fallbackReason = ''
      this.generationMode = 'llm'
      this.retrievalMode = 'hybrid'
      this.queryRewrite = null
      this.status = {
        phase: 'idle',
        label: '等待提问',
        detail: '从你的个人读书笔记中提问，系统会先检索引用，再组织回答。',
      }
    },
  },
})
