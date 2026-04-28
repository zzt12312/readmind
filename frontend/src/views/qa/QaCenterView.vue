<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import { useBooksStore } from '@/stores/books'
import { useQaStore } from '@/stores/qa'
import { highlightText } from '@/utils/text'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()
const qaStore = useQaStore()
const { messages, loading, sessions, currentSession, stopped, status, generationMode, retrievalMode, fallbackReason, errorMessage } = storeToRefs(qaStore)
const draft = ref('我在《认知觉醒》的笔记里，关于长期主义和行动系统记录了哪些内容？')
const scope = ref<'all-books' | 'current-book'>('all-books')
const scopedBookId = ref<number | undefined>()
const conversationRef = ref<HTMLElement | null>(null)

const currentScopedBook = computed(() => {
  if (!scopedBookId.value) return null
  return booksStore.findById(scopedBookId.value)
})

const selectableBooks = computed(() =>
  [...booksStore.items].sort((left, right) => left.title.localeCompare(right.title, 'zh-Hans-CN')),
)

const latestQuestion = computed(() => {
  const userMessages = messages.value.filter((message) => message.role === 'user')
  return userMessages[userMessages.length - 1]?.content ?? draft.value
})

const latestAssistantMessage = computed(() => {
  const assistantMessages = messages.value.filter((message) => message.role === 'assistant' && message.content)
  return assistantMessages[assistantMessages.length - 1] ?? null
})

const latestReferences = computed(() => latestAssistantMessage.value?.references ?? [])
const statusTone = computed(() => {
  if (status.value.phase === 'failed') return 'danger'
  if (status.value.phase === 'fallback') return 'warning'
  if (status.value.phase === 'success') return generationMode.value === 'fallback' ? 'warning' : 'success'
  return 'primary'
})

const followupPrompts = computed(() => {
  if (scope.value === 'current-book' && currentScopedBook.value) {
    return [
      `继续追问《${currentScopedBook.value.title}》里最值得执行的 3 个建议`,
      `从《${currentScopedBook.value.title}》里挑出最容易忽略的一个观点`,
      `结合这本书的笔记，帮我整理一个复习清单`,
    ]
  }

  return [
    '把刚才的回答改写成 3 条可执行建议',
    '继续比较这些观点之间的共性和差异',
    '基于这些笔记，帮我列出 3 个值得复习的问题',
  ]
})

const currentBookPrompts = computed(() => {
  if (!currentScopedBook.value) return []
  return [
    `《${currentScopedBook.value.title}》里最值得复习的 5 个观点是什么？`,
    `《${currentScopedBook.value.title}》里有哪些可以直接执行的建议？`,
    `只基于《${currentScopedBook.value.title}》，帮我整理 3 个复习问题`,
  ]
})

async function handleAsk() {
  if (!draft.value.trim()) {
    ElMessage.warning('先输入一个问题吧')
    return
  }

  if (scope.value === 'current-book' && !scopedBookId.value) {
    ElMessage.warning('当前还没有指定书籍范围')
    return
  }

  await qaStore.ask({
    question: draft.value.trim(),
    scope: scope.value,
    book_id: scope.value === 'current-book' ? scopedBookId.value : undefined,
  })
  draft.value = ''
}

function usePrompt(prompt: string) {
  draft.value = prompt
}

async function useFollowupPrompt(prompt: string) {
  draft.value = prompt
  await handleAsk()
}

function jumpToNote(bookId: number, noteId: number) {
  void router.push({
    path: '/notes',
    query: {
      bookId: String(bookId),
      noteId: String(noteId),
    },
  })
}

function syncPreset() {
  const preset = route.query.preset ? String(route.query.preset) : ''
  const bookId = route.query.bookId ? Number(route.query.bookId) : undefined
  const queryScope =
    route.query.scope === 'current-book' || route.query.scope === 'all-books'
      ? (route.query.scope as 'all-books' | 'current-book')
      : undefined

  if (preset) {
    draft.value = preset
  }
  scopedBookId.value = Number.isNaN(bookId) ? undefined : bookId
  scope.value = scopedBookId.value ? queryScope ?? 'current-book' : 'all-books'
}

function restoreSession(sessionId: string) {
  qaStore.restoreSession(sessionId)
  scopedBookId.value = qaStore.bookId ?? undefined
  scope.value = qaStore.scope
}

async function renameSession(sessionId: string, currentTitle: string) {
  try {
    const { value } = await ElMessageBox.prompt('给这个会话起一个更容易回想的名字', '重命名会话', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: currentTitle,
      inputPlaceholder: '例如：认知觉醒里的长期主义',
    })
    qaStore.renameSession(sessionId, value)
    ElMessage.success('会话名称已更新')
  } catch {
    // 用户取消时不需要提示。
  }
}

async function deleteSession(sessionId: string) {
  try {
    await ElMessageBox.confirm('删除后这段问答历史将无法恢复，是否继续？', '删除会话', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    qaStore.deleteSession(sessionId)
    ElMessage.success('会话已删除')
  } catch {
    // 用户取消时不需要提示。
  }
}

function formatSessionTime(value: string) {
  return new Date(value).toLocaleString()
}

function handleScopeChange(nextScope: 'all-books' | 'current-book') {
  if (nextScope === 'current-book' && !scopedBookId.value && selectableBooks.value.length > 0) {
    scopedBookId.value = selectableBooks.value[0].id
  }
}

function renderReferenceHighlight(text: string) {
  return highlightText(text, latestQuestion.value)
}

async function scrollConversationToBottom() {
  await nextTick()
  const element = conversationRef.value
  if (!element) return
  element.scrollTo({
    top: element.scrollHeight,
    behavior: 'smooth',
  })
}

onMounted(() => {
  if (booksStore.items.length === 0) {
    void booksStore.load()
  }
  qaStore.hydrateSessions()
  syncPreset()
  if (route.query.preset || route.query.bookId) return
  if (qaStore.sessions.length > 0) {
    restoreSession(qaStore.sessions[0].id)
    return
  }
  qaStore.resetConversation()
})

watch(
  () => route.query,
  () => {
    syncPreset()
  },
)

watch(
  () => messages.value.length,
  () => {
    void scrollConversationToBottom()
  },
)

watch(
  () => loading.value,
  () => {
    void scrollConversationToBottom()
  },
)
</script>

<template>
  <div class="qa-view">
    <section class="qa-view__layout">
      <AppCard class="qa-view__history">
        <div class="qa-view__history-header">
          <h3>问答历史</h3>
          <el-button text @click="qaStore.resetConversation">新对话</el-button>
        </div>
        <div v-if="sessions.length" class="qa-view__history-list">
          <article
            v-for="session in sessions"
            :key="session.id"
            class="qa-view__history-item"
            :class="{ 'is-active': currentSession?.id === session.id }"
          >
            <button type="button" class="qa-view__history-main" @click="restoreSession(session.id)">
              <div class="qa-view__history-title">
                <strong>{{ session.title }}</strong>
                <el-tag v-if="session.pinned" size="small" round effect="plain">置顶</el-tag>
              </div>
              <span>{{ session.scope === 'current-book' ? '单本书' : '全库' }} · {{ formatSessionTime(session.updated_at) }}</span>
            </button>
            <div class="qa-view__history-actions">
              <el-button text size="small" @click.stop="qaStore.togglePinSession(session.id)">
                {{ session.pinned ? '取消置顶' : '置顶' }}
              </el-button>
              <el-button text size="small" @click.stop="renameSession(session.id, session.title)">重命名</el-button>
              <el-button text size="small" type="danger" @click.stop="deleteSession(session.id)">删除</el-button>
            </div>
          </article>
        </div>
        <p v-else class="qa-view__history-empty">还没有历史会话，问一个问题后会自动保存。</p>
      </AppCard>

      <AppCard class="qa-view__main">
        <div class="qa-view__chips">
          <el-tag round @click="usePrompt('这本书里关于长期主义提到了什么')">这本书里关于长期主义提到了什么</el-tag>
          <el-tag round @click="usePrompt('帮我总结最近三本书共同观点')">帮我总结最近三本书共同观点</el-tag>
          <el-tag round @click="usePrompt('只检索《认知觉醒》，总结其中关于行动系统的内容')">只检索《认知觉醒》</el-tag>
        </div>

        <div v-if="scope === 'current-book'" class="qa-view__scope-tip">
          <strong>当前范围</strong>
          <span>{{ currentScopedBook ? `仅检索《${currentScopedBook.title}》` : '仅检索指定书籍' }}</span>
        </div>

        <div v-if="scope === 'current-book'" class="qa-view__book-picker">
          <strong>选择书籍</strong>
          <el-select
            v-model="scopedBookId"
            filterable
            clearable
            placeholder="选择你要提问的书"
            style="width: 100%"
          >
            <el-option
              v-for="book in selectableBooks"
              :key="book.id"
              :label="book.title"
              :value="book.id"
            >
              <div class="qa-view__book-option">
                <span>{{ book.title }}</span>
                <small>{{ book.author || book.category || '未分类' }}</small>
              </div>
            </el-option>
          </el-select>
          <div v-if="currentBookPrompts.length" class="qa-view__book-prompts">
            <el-button v-for="prompt in currentBookPrompts" :key="prompt" round @click="usePrompt(prompt)">
              {{ prompt }}
            </el-button>
          </div>
        </div>

        <div class="qa-view__meta-row">
          <div class="qa-view__meta-card">
            <strong>当前模式</strong>
            <span>{{ scope === 'current-book' ? '单本书追问' : '全库问答' }}</span>
          </div>
          <div class="qa-view__meta-card">
            <strong>{{ scope === 'current-book' ? '当前书籍' : '引用数量' }}</strong>
            <span>{{ scope === 'current-book' ? (currentScopedBook?.title ?? '未选择') : `${latestAssistantMessage?.references?.length ?? 0} 条` }}</span>
          </div>
        </div>

        <div class="qa-view__status-panel" :class="`is-${statusTone}`">
          <div>
            <strong>{{ status.label }}</strong>
            <p>{{ status.detail }}</p>
          </div>
          <div class="qa-view__status-meta">
            <el-tag round effect="plain">{{ retrievalMode === 'hybrid' ? '混合检索' : retrievalMode }}</el-tag>
            <el-tag round effect="plain" :type="generationMode === 'fallback' ? 'warning' : 'success'">
              {{ generationMode === 'fallback' ? '本地回退' : '模型生成' }}
            </el-tag>
          </div>
        </div>

        <p v-if="fallbackReason" class="qa-view__status-tip qa-view__status-tip--warning">
          模型暂时不可用，当前已自动切换到回退回答。{{ fallbackReason }}
        </p>
        <p v-else-if="errorMessage" class="qa-view__status-tip qa-view__status-tip--warning">
          {{ errorMessage }}
        </p>

        <div ref="conversationRef" class="qa-view__conversation">
          <template v-if="messages.length">
            <article
              v-for="(message, index) in messages"
              :key="`${message.role}-${index}`"
              class="qa-view__bubble"
              :class="[
                message.role === 'user' ? 'is-user' : 'is-assistant',
                message.role === 'assistant' && !message.content && loading ? 'is-thinking' : '',
              ]"
            >
              <p>{{ message.content || status.detail || '正在结合你的读书笔记整理答案...' }}</p>
              <div v-if="message.role === 'assistant' && message.references?.length" class="qa-view__bubble-references">
                <article
                  v-for="reference in message.references"
                  :key="reference.book + reference.chapter + reference.note_id"
                  class="qa-view__inline-reference"
                >
                  <strong>{{ reference.book }} · {{ reference.chapter }}</strong>
                  <p v-html="renderReferenceHighlight(reference.excerpt)" />
                  <el-button text @click="jumpToNote(reference.book_id, reference.note_id)">跳转原笔记</el-button>
                </article>
              </div>
            </article>
          </template>
          <article v-else class="qa-view__bubble is-assistant" v-loading="loading">
            <p>从你的个人阅读笔记中提问，答案会连同引用来源一起返回。</p>
          </article>
        </div>

        <div v-if="latestAssistantMessage" class="qa-view__followups">
          <div class="qa-view__answer-actions">
            <strong>回答反馈</strong>
            <div class="qa-view__feedback-actions">
              <el-button
                round
                :type="latestAssistantMessage.feedback === 'up' ? 'primary' : 'default'"
                @click="qaStore.setMessageFeedback(latestAssistantMessage.id, 'up')"
              >
                有帮助
              </el-button>
              <el-button
                round
                :type="latestAssistantMessage.feedback === 'down' ? 'warning' : 'default'"
                @click="qaStore.setMessageFeedback(latestAssistantMessage.id, 'down')"
              >
                不够准确
              </el-button>
              <el-button round :disabled="loading" @click="qaStore.regenerateLastAnswer">重新生成这一轮</el-button>
            </div>
          </div>
          <strong>继续追问</strong>
          <div class="qa-view__followup-list">
            <el-button v-for="prompt in followupPrompts" :key="prompt" round @click="useFollowupPrompt(prompt)">
              {{ prompt }}
            </el-button>
          </div>
        </div>

        <div class="qa-view__input">
          <el-input v-model="draft" type="textarea" :rows="4" placeholder="输入你想围绕读书笔记提的问题" />
          <div class="qa-view__input-actions">
            <el-select v-model="scope" placeholder="检索范围" style="width: 180px" @change="handleScopeChange">
              <el-option label="当前书籍" value="current-book" />
              <el-option label="全部书籍" value="all-books" />
            </el-select>
            <el-button round :disabled="!messages.length || loading" @click="qaStore.regenerateLastAnswer">重新生成</el-button>
            <el-button round :disabled="!loading" @click="qaStore.stopStreaming">停止生成</el-button>
            <el-button type="primary" round :loading="loading" @click="handleAsk">发送问题</el-button>
          </div>
          <p v-if="stopped" class="qa-view__status-tip">本轮回答已手动停止，你可以继续追问或点击“重新生成”。</p>
        </div>
      </AppCard>

      <AppCard class="qa-view__side">
        <h3>引用来源</h3>
        <div class="qa-view__reference-list">
          <article
            v-for="reference in latestReferences"
            :key="reference.book + reference.chapter + reference.note_id"
            class="qa-view__reference-card"
          >
            <strong>{{ reference.book }} · {{ reference.chapter }}</strong>
            <p v-html="renderReferenceHighlight(reference.excerpt)" />
            <el-button text @click="jumpToNote(reference.book_id, reference.note_id)">跳转原笔记</el-button>
          </article>
        </div>
      </AppCard>
    </section>
  </div>
</template>

<style scoped lang="scss">
.qa-view__layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1.4fr) 360px;
  gap: 18px;
  align-items: start;
}

.qa-view__history,
.qa-view__main,
.qa-view__side {
  min-height: 720px;
}

.qa-view__history-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.qa-view__history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qa-view__history-item {
  border: 1px solid var(--border-light);
  border-radius: 14px;
  background: rgba(251, 248, 242, 0.72);
  overflow: hidden;
}

.qa-view__history-item.is-active {
  border-color: rgba(47, 93, 80, 0.35);
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.08);
}

.qa-view__history-main {
  width: 100%;
  padding: 14px 14px 8px;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.qa-view__history-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qa-view__history-item strong,
.qa-view__history-item span,
.qa-view__history-title {
  display: block;
}

.qa-view__history-item span,
.qa-view__history-empty {
  margin-top: 6px;
  color: var(--text-tertiary);
  font-size: 0.84rem;
}

.qa-view__history-actions {
  display: flex;
  gap: 4px;
  padding: 0 10px 10px;
  flex-wrap: wrap;
}

.qa-view__chips {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}

.qa-view__meta-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.qa-view__book-picker {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qa-view__book-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.qa-view__book-option {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.qa-view__book-option small {
  color: var(--text-tertiary);
}

.qa-view__meta-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
}

.qa-view__meta-card span {
  color: var(--text-secondary);
}

.qa-view__status-panel {
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  background: rgba(47, 93, 80, 0.05);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.qa-view__status-panel.is-warning {
  border-color: rgba(192, 139, 92, 0.24);
  background: rgba(192, 139, 92, 0.08);
}

.qa-view__status-panel.is-success {
  border-color: rgba(47, 93, 80, 0.2);
  background: rgba(47, 93, 80, 0.08);
}

.qa-view__status-panel.is-danger {
  border-color: rgba(190, 76, 60, 0.22);
  background: rgba(190, 76, 60, 0.08);
}

.qa-view__status-panel strong {
  display: block;
  margin-bottom: 6px;
}

.qa-view__status-panel p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.qa-view__status-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.qa-view__conversation {
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-height: 640px;
  padding-right: 6px;
  overflow-y: auto;
  scroll-behavior: smooth;
}

.qa-view__scope-tip {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--text-secondary);
}

.qa-view__bubble {
  max-width: 90%;
  padding: 16px 18px;
  border-radius: 18px;
  line-height: 1.75;
}

.qa-view__bubble.is-user {
  margin-left: auto;
  background: var(--brand-primary);
  color: #fff;
}

.qa-view__bubble.is-assistant {
  background: var(--bg-soft);
}

.qa-view__bubble.is-thinking {
  color: var(--text-secondary);
  border: 1px dashed rgba(47, 93, 80, 0.2);
}

.qa-view__bubble p,
.qa-view__bubble ol {
  margin: 0;
}

.qa-view__bubble-references {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qa-view__inline-reference {
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.58);
}

.qa-view__inline-reference p {
  margin: 8px 0;
}

.qa-view__bubble ol {
  padding-left: 20px;
}

.qa-view__input {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.qa-view__status-tip {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.84rem;
}

.qa-view__status-tip--warning {
  color: #9a6131;
}

.qa-view__followups {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qa-view__answer-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
}

.qa-view__feedback-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.qa-view__followup-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.qa-view__input-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.qa-view__reference-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.qa-view__reference-card {
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  background: rgba(251, 248, 242, 0.7);
}

.qa-view__reference-card p {
  margin: 10px 0;
  color: var(--text-secondary);
  line-height: 1.75;
}

:deep(mark) {
  padding: 0 2px;
  border-radius: 4px;
  background: rgba(192, 139, 92, 0.22);
}

@media (max-width: 1180px) {
  .qa-view__layout {
    grid-template-columns: 1fr;
  }

  .qa-view__history,
  .qa-view__main,
  .qa-view__side {
    min-height: auto;
  }
}

@media (max-width: 768px) {
  .qa-view__input-actions {
    flex-direction: column;
  }
}
</style>
