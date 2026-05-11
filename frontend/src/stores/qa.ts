import { defineStore } from 'pinia'
import { exportQaSession } from '@/api/modules/qa'
import {
  createMessageId,
  createSession,
  createSessionTitle,
  createSavedAnswerId,
  clearQaLocalData,
  loadInsightCards,
  loadQuestionWorkspaces,
  loadReviewSeeds,
  loadSavedAnswers,
  loadQaSessions,
  loadUnderstandings,
  saveInsightCards,
  saveQuestionWorkspaces,
  saveReviewSeeds,
  saveSavedAnswers,
  saveQaSessions,
  saveUnderstandings,
  sortSessions,
} from '@/services/qaSessionStorage'
import {
  buildQuestionWorkspace,
  createInsightCardFromAnswer,
  createReviewSeedFromAnswer,
  createUnderstandingFromAnswer,
  getQaAnswerContext,
} from '@/services/qaDeposits'
import { streamQuestion } from '@/services/qaStreamClient'
import type { QaAskPayload, QaEvidenceSummary, QaExportResponse, QaInsightCard, QaMessage, QaQuestionWorkspace, QaReference, QaReviewSeed, QaSavedAnswer, QaSession, QaStatusPayload, QaUnderstanding, QueryRewriteSummary } from '@/types/qa'

// QA store owns conversation state only. Persistence and SSE parsing live in
// `services/qaSessionStorage` and `services/qaStreamClient` so they can evolve
// independently from Pinia state transitions.
export const useQaStore = defineStore('qa', {
  state: () => ({
    question: '',
    answer: '',
    references: [] as QaReference[],
    messages: [] as QaMessage[],
    sessions: [] as QaSession[],
    savedAnswers: [] as QaSavedAnswer[],
    questionWorkspaces: [] as QaQuestionWorkspace[],
    insightCards: [] as QaInsightCard[],
    understandings: [] as QaUnderstanding[],
    reviewSeeds: [] as QaReviewSeed[],
    currentSessionId: null as string | null,
    loading: false,
    exporting: false,
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
    evidence: null as QaEvidenceSummary | null,
  }),
  getters: {
    currentSession(state) {
      return state.sessions.find((session) => session.id === state.currentSessionId) ?? null
    },
  },
  actions: {
    hydrateSessions() {
      this.sessions = sortSessions(loadQaSessions())
      this.savedAnswers = loadSavedAnswers()
      this.questionWorkspaces = loadQuestionWorkspaces()
      this.insightCards = loadInsightCards()
      this.understandings = loadUnderstandings()
      this.reviewSeeds = loadReviewSeeds()
    },
    persistSessions() {
      this.sessions = saveQaSessions(this.sessions)
    },
    persistSavedAnswers() {
      this.savedAnswers = saveSavedAnswers(this.savedAnswers)
    },
    persistQuestionWorkspaces() {
      this.questionWorkspaces = saveQuestionWorkspaces(this.questionWorkspaces)
    },
    persistInsightCards() {
      this.insightCards = saveInsightCards(this.insightCards)
    },
    persistUnderstandings() {
      this.understandings = saveUnderstandings(this.understandings)
    },
    persistReviewSeeds() {
      this.reviewSeeds = saveReviewSeeds(this.reviewSeeds)
    },
    // 会话在首次提问时创建，后续连续追问都复用同一个 session，便于恢复上下文。
    ensureSession(payload: QaAskPayload) {
      if (this.currentSessionId) return this.currentSessionId

      const session = createSession(payload)
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
      this.evidence = null
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
    isMessageSaved(messageId: string) {
      return this.savedAnswers.some((item) => item.message_id === messageId)
    },
    toggleSaveAnswer(messageId: string) {
      const existing = this.savedAnswers.find((item) => item.message_id === messageId)
      if (existing) {
        this.savedAnswers = this.savedAnswers.filter((item) => item.id !== existing.id)
        this.persistSavedAnswers()
        return false
      }

      const assistantIndex = this.messages.findIndex((message) => message.id === messageId)
      const assistantMessage = this.messages[assistantIndex]
      if (!assistantMessage || assistantMessage.role !== 'assistant' || !assistantMessage.content.trim()) {
        throw new Error('当前没有可收藏的回答')
      }
      const userMessage = [...this.messages.slice(0, assistantIndex)]
        .reverse()
        .find((message) => message.role === 'user')
      const title = createSessionTitle(userMessage?.content || this.currentSession?.title || '收藏回答')
      this.savedAnswers = saveSavedAnswers([
        {
          id: createSavedAnswerId(),
          session_id: this.currentSessionId,
          message_id: assistantMessage.id,
          title,
          question: userMessage?.content ?? '',
          answer: assistantMessage.content,
          references: assistantMessage.references ?? [],
          scope: this.scope,
          book_id: this.bookId,
          saved_at: new Date().toISOString(),
        },
        ...this.savedAnswers,
      ])
      return true
    },
    deleteSavedAnswer(savedAnswerId: string) {
      this.savedAnswers = this.savedAnswers.filter((item) => item.id !== savedAnswerId)
      this.persistSavedAnswers()
    },
    restoreSavedAnswer(savedAnswerId: string) {
      const saved = this.savedAnswers.find((item) => item.id === savedAnswerId)
      if (!saved) return
      this.stopStreaming()
      this.currentSessionId = null
      this.messages = [
        { id: `${saved.id}-question`, role: 'user', content: saved.question, references: [], feedback: null },
        { id: saved.message_id, role: 'assistant', content: saved.answer, references: saved.references, feedback: null },
      ]
      this.question = saved.question
      this.answer = saved.answer
      this.references = saved.references
      this.scope = saved.scope
      this.bookId = saved.book_id ?? null
      this.errorMessage = ''
      this.fallbackReason = ''
      this.queryRewrite = null
      this.evidence = null
      this.generationMode = 'llm'
      this.status = {
        phase: 'success',
        label: '已打开收藏回答',
        detail: '这是你之前收藏的回答，可以继续追问，或导出成 Markdown。',
      }
    },
    saveLatestAnswerToWorkspace(messageId: string) {
      const context = this.getAnswerContext(messageId)
      const existing = this.questionWorkspaces.find((item) => item.question === context.question)
      const workspace = buildQuestionWorkspace(context, { scope: this.scope, bookId: this.bookId }, existing)
      this.questionWorkspaces = saveQuestionWorkspaces([
        workspace,
        ...this.questionWorkspaces.filter((item) => item.id !== workspace.id),
      ])
      return workspace
    },
    updateWorkspaceStatus(workspaceId: string, status: QaQuestionWorkspace['status']) {
      this.questionWorkspaces = this.questionWorkspaces.map((item) =>
        item.id === workspaceId
          ? { ...item, status, updated_at: new Date().toISOString() }
          : item,
      )
      this.persistQuestionWorkspaces()
    },
    deleteWorkspace(workspaceId: string) {
      this.questionWorkspaces = this.questionWorkspaces.filter((item) => item.id !== workspaceId)
      this.persistQuestionWorkspaces()
    },
    restoreWorkspace(workspaceId: string) {
      const workspace = this.questionWorkspaces.find((item) => item.id === workspaceId)
      if (!workspace) return
      this.stopStreaming()
      this.currentSessionId = null
      this.messages = [
        { id: `${workspace.id}-question`, role: 'user', content: workspace.question, references: [], feedback: null },
        { id: `${workspace.id}-answer`, role: 'assistant', content: workspace.latest_answer, references: workspace.references, feedback: null },
      ]
      this.question = workspace.question
      this.answer = workspace.latest_answer
      this.references = workspace.references
      this.scope = workspace.scope
      this.bookId = workspace.book_id ?? null
      this.errorMessage = ''
      this.fallbackReason = ''
      this.queryRewrite = null
      this.evidence = null
      this.generationMode = 'llm'
      this.status = {
        phase: 'success',
        label: '已打开问题工作台',
        detail: '这是围绕同一个问题沉淀的最新回答，可以继续追问或导出。',
      }
    },
    getAnswerContext(messageId: string) {
      return getQaAnswerContext(this.messages, messageId, this.currentSession?.title || '未命名问题')
    },
    async saveLatestAsInsightCard(messageId: string) {
      const context = this.getAnswerContext(messageId)
      const card = await createInsightCardFromAnswer(context, { scope: this.scope, bookId: this.bookId })
      this.insightCards = saveInsightCards([card, ...this.insightCards])
      return card
    },
    async saveLatestAsUnderstanding(messageId: string) {
      const context = this.getAnswerContext(messageId)
      const existing = this.understandings.find((item) => item.question === context.question)
      const understanding = await createUnderstandingFromAnswer(context, { scope: this.scope, bookId: this.bookId }, existing)
      this.understandings = saveUnderstandings([
        understanding,
        ...this.understandings.filter((item) => item.id !== understanding.id),
      ])
      return understanding
    },
    async addLatestToReview(messageId: string) {
      const context = this.getAnswerContext(messageId)
      const seed = await createReviewSeedFromAnswer(context, { scope: this.scope, bookId: this.bookId })
      this.reviewSeeds = saveReviewSeeds([seed, ...this.reviewSeeds])
      return seed
    },
    clearLocalQaData() {
      this.stopStreaming()
      clearQaLocalData()
      this.question = ''
      this.answer = ''
      this.references = []
      this.messages = []
      this.sessions = []
      this.savedAnswers = []
      this.questionWorkspaces = []
      this.insightCards = []
      this.understandings = []
      this.reviewSeeds = []
      this.currentSessionId = null
      this.errorMessage = ''
      this.fallbackReason = ''
      this.queryRewrite = null
      this.evidence = null
      this.status = {
        phase: 'idle',
        label: '等待提问',
        detail: '从你的个人读书笔记中提问，系统会先检索引用，再组织回答。',
      }
    },
    async ask(payload: QaAskPayload) {
      // Flow: create/update session -> append user + empty assistant bubble ->
      // stream meta/status/delta/done events -> persist every visible change.
      this.loading = true
      this.stopped = false
      this.errorMessage = ''
      this.fallbackReason = ''
      this.queryRewrite = null
      this.evidence = null
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
              this.evidence = data.evidence ?? null
            },
            onStatus: (data) => {
              this.status = data
            },
            onDelta: (data) => {
              const assistantMessage = this.messages[this.messages.length - 1]
              if (assistantMessage?.role === 'assistant') {
                // Mutate the active assistant bubble for a natural streaming UI,
                // then persist a shallow copy so restored sessions see progress.
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
              this.evidence = data.evidence ?? this.evidence
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
    async exportCurrentSession(bookTitle = ''): Promise<QaExportResponse> {
      const exportableMessages = this.messages.filter((message) => message.content.trim())
      if (!exportableMessages.length) {
        throw new Error('当前还没有可导出的问答内容')
      }

      this.exporting = true
      try {
        const title = this.currentSession?.title || this.question || '问答导出'
        return await exportQaSession({
          title,
          scope: this.scope,
          book_title: bookTitle,
          messages: exportableMessages,
        })
      } finally {
        this.exporting = false
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
      this.evidence = null
      this.status = {
        phase: 'idle',
        label: '等待提问',
        detail: '从你的个人读书笔记中提问，系统会先检索引用，再组织回答。',
      }
    },
  },
})
