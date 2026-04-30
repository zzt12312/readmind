<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import type { ComponentPublicInstance } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import AppActionGrid from '@/components/base/AppActionGrid.vue'
import AppCard from '@/components/base/AppCard.vue'
import AppStatusStrip from '@/components/base/AppStatusStrip.vue'
import QaConversation from '@/components/qa/QaConversation.vue'
import QaHistoryPanel from '@/components/qa/QaHistoryPanel.vue'
import QaInputBox from '@/components/qa/QaInputBox.vue'
import QaReferencePanel from '@/components/qa/QaReferencePanel.vue'
import QaStatusPanel from '@/components/qa/QaStatusPanel.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import { useAppStore } from '@/stores/app'
import { useBooksStore } from '@/stores/books'
import { useQaStore } from '@/stores/qa'
import { buildQaMascotCue } from '@/constants/mascotMessages'
import type { QaWorkspaceAction, QaWorkspaceStatus } from '@/types/qa'
import {
  DEFAULT_QA_DRAFT,
  QA_QUICK_PROMPTS,
  buildCurrentBookPrompts,
  buildDemoQaDefaults,
  buildFollowupPrompts,
  buildPersonalQaDefaults,
} from '@/constants/qaPresets'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const booksStore = useBooksStore()
const qaStore = useQaStore()
const { messages, loading, sessions, savedAnswers, questionWorkspaces, insightCards, understandings, reviewSeeds, currentSession, stopped, status, generationMode, retrievalMode, fallbackReason, errorMessage } = storeToRefs(qaStore)
const draft = ref(DEFAULT_QA_DRAFT)
const scope = ref<'all-books' | 'current-book'>('all-books')
const scopedBookId = ref<number | undefined>()
const conversationRef = ref<ComponentPublicInstance | null>(null)

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
const hasExportableMessages = computed(() => messages.value.some((message) => message.content.trim()))
const latestAnswerSaved = computed(() =>
  latestAssistantMessage.value ? qaStore.isMessageSaved(latestAssistantMessage.value.id) : false,
)
const latestWorkspace = computed(() => {
  const question = latestQuestion.value.trim()
  return question ? questionWorkspaces.value.find((item) => item.question === question) ?? null : null
})
const latestInsightSaved = computed(() => {
  const question = latestQuestion.value.trim()
  return question ? insightCards.value.some((item) => item.question === question) : false
})
const latestUnderstandingSaved = computed(() => {
  const question = latestQuestion.value.trim()
  return question ? understandings.value.some((item) => item.question === question) : false
})
const latestReviewSeed = computed(() => {
  const question = latestQuestion.value.trim()
  return question ? reviewSeeds.value.find((item) => item.question === question) ?? null : null
})
const queryRewrite = computed(() => qaStore.queryRewrite)
const evidence = computed(() => qaStore.evidence)
const conversationMeta = computed(() => [
  {
    label: '当前模式',
    value: scope.value === 'current-book' ? '单本书追问' : '全库问答',
  },
  {
    label: scope.value === 'current-book' ? '当前书籍' : '引用数量',
    value: scope.value === 'current-book' ? (currentScopedBook.value?.title ?? '未选择') : `${latestReferences.value.length} 条`,
  },
  {
    label: '会话状态',
    value: currentSession.value ? '已恢复历史对话' : '当前新对话',
  },
])
const depositActions = computed(() => [
  {
    id: 'workspace',
    index: '01',
    title: latestWorkspace.value ? '更新问题' : '沉淀问题',
    type: '问题',
    disabled: !latestAssistantMessage.value,
  },
  {
    id: 'insight',
    index: '02',
    title: latestInsightSaved.value ? '已存洞察' : '存洞察',
    type: '洞察',
    saved: latestInsightSaved.value,
    disabled: !latestAssistantMessage.value,
  },
  {
    id: 'understanding',
    index: '03',
    title: latestUnderstandingSaved.value ? '已成理解' : '我的理解',
    type: '理解',
    saved: latestUnderstandingSaved.value,
    disabled: !latestAssistantMessage.value,
  },
  {
    id: 'review',
    index: '04',
    title: latestReviewSeed.value ? '已加复习' : '加入复习',
    type: '复习',
    saved: Boolean(latestReviewSeed.value),
    disabled: !latestReferences.value.length,
  },
])
const followupPrompts = computed(() => {
  return buildFollowupPrompts(scope.value, currentScopedBook.value)
})
const mascotCue = computed(() => buildQaMascotCue({
  loading: loading.value,
  hasAnswer: Boolean(latestAssistantMessage.value),
  scopedBookTitle: scope.value === 'current-book' ? currentScopedBook.value?.title : undefined,
}))

const currentBookPrompts = computed(() => {
  return buildCurrentBookPrompts(currentScopedBook.value)
})

function applyDemoDefaults() {
  const defaults = buildDemoQaDefaults()
  scope.value = defaults.scope
  scopedBookId.value = defaults.bookId
  draft.value = defaults.draft
}

function applyPersonalDefaults() {
  const defaults = buildPersonalQaDefaults(booksStore.items)
  scope.value = defaults.scope
  scopedBookId.value = defaults.bookId
  draft.value = defaults.draft
}

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

function reviewByTopic(topic: string) {
  void router.push({
    path: '/review',
    query: {
      tag: topic,
    },
  })
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

async function exportConversation() {
  try {
    const result = await qaStore.exportCurrentSession(currentScopedBook.value?.title ?? '')
    ElMessage.success(`已导出到 ${result.relative_path}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '导出失败，请稍后重试')
  }
}

function toggleSaveLatestAnswer() {
  if (!latestAssistantMessage.value) return
  try {
    const saved = qaStore.toggleSaveAnswer(latestAssistantMessage.value.id)
    ElMessage.success(saved ? '已收藏这条回答' : '已取消收藏')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '收藏失败，请稍后重试')
  }
}

function saveLatestToWorkspace() {
  if (!latestAssistantMessage.value) return
  try {
    const workspace = qaStore.saveLatestAnswerToWorkspace(latestAssistantMessage.value.id)
    ElMessage.success(`已沉淀到问题工作台：${workspace.title}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '沉淀失败，请稍后重试')
  }
}

async function saveLatestAsInsight() {
  if (!latestAssistantMessage.value) return
  try {
    const card = await qaStore.saveLatestAsInsightCard(latestAssistantMessage.value.id)
    ElMessage.success(`已保存洞察卡片：${card.title}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存洞察失败，请稍后重试')
  }
}

async function saveLatestAsUnderstanding() {
  if (!latestAssistantMessage.value) return
  try {
    const understanding = await qaStore.saveLatestAsUnderstanding(latestAssistantMessage.value.id)
    ElMessage.success(`已保存为我的理解：${understanding.title}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '保存理解失败，请稍后重试')
  }
}

async function addLatestAnswerToReview() {
  if (!latestAssistantMessage.value) return
  try {
    const seed = await qaStore.addLatestToReview(latestAssistantMessage.value.id)
    const firstReference = seed.references[0]
    if (firstReference) {
      void router.push({
        path: '/review',
        query: {
          bookId: String(firstReference.book_id),
          queue: 'new',
          goal: '5',
        },
      })
    }
    ElMessage.success(`已加入复习线索：${seed.references.length} 条引用`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '加入复习失败，请稍后重试')
  }
}

function handleDepositAction(actionId: string) {
  if (actionId === 'workspace') {
    saveLatestToWorkspace()
    return
  }
  if (actionId === 'insight') {
    void saveLatestAsInsight()
    return
  }
  if (actionId === 'understanding') {
    void saveLatestAsUnderstanding()
    return
  }
  if (actionId === 'review') {
    void addLatestAnswerToReview()
  }
}

function updateWorkspaceStatus(workspaceId: string, nextStatus: QaWorkspaceStatus) {
  qaStore.updateWorkspaceStatus(workspaceId, nextStatus)
  ElMessage.success('问题状态已更新')
}

function handleWorkspaceAction(workspaceId: string, action: QaWorkspaceAction) {
  const workspace = questionWorkspaces.value.find((item) => item.id === workspaceId)
  if (!workspace) return

  if (action === 'followup') {
    qaStore.updateWorkspaceStatus(workspaceId, 'open')
    qaStore.restoreWorkspace(workspaceId)
    scope.value = workspace.scope
    scopedBookId.value = workspace.book_id ?? undefined
    draft.value = `继续围绕这个问题补充新的证据或反例：${workspace.question}`
    ElMessage.success('已打开问题，可以继续追问')
    return
  }

  if (action === 'writing') {
    qaStore.updateWorkspaceStatus(workspaceId, 'writing')
    qaStore.restoreWorkspace(workspaceId)
    scope.value = workspace.scope
    scopedBookId.value = workspace.book_id ?? undefined
    draft.value = `把这个问题的现有回答整理成写作提纲，按“核心判断 / 证据引用 / 可展开段落”输出：${workspace.question}`
    ElMessage.success('已切到写作整理模式')
    return
  }

  qaStore.updateWorkspaceStatus(workspaceId, 'reviewing')
  const reference = workspace.references[0]
  if (reference) {
    void router.push({
      path: '/review',
      query: {
        bookId: String(reference.book_id),
        queue: 'new',
        goal: '5',
      },
    })
    ElMessage.success('已根据引用进入复习中心')
    return
  }

  qaStore.restoreWorkspace(workspaceId)
  draft.value = `请把这个问题整理成 3 张可复习的问题卡：${workspace.question}`
  ElMessage.info('这个问题还没有引用，先生成可复习的问题卡')
}

function handleScopeChange(nextScope: 'all-books' | 'current-book') {
  if (nextScope === 'current-book' && !scopedBookId.value && selectableBooks.value.length > 0) {
    scopedBookId.value = selectableBooks.value[0].id
  }
}

async function scrollConversationToBottom() {
  await nextTick()
  const element = conversationRef.value?.$el as HTMLElement | undefined
  if (!element) return
  element.scrollTo({
    top: element.scrollHeight,
    behavior: 'smooth',
  })
}

onMounted(() => {
  void (async () => {
    if (booksStore.items.length === 0) {
      await booksStore.load()
    }
    if (!appStore.llmHealth) {
      await appStore.loadLlmHealth()
    }
    qaStore.hydrateSessions()
    syncPreset()
    if (route.query.preset || route.query.bookId) return
    if (qaStore.sessions.length > 0) {
      restoreSession(qaStore.sessions[0].id)
      return
    }
    qaStore.resetConversation()
    if (appStore.llmHealth?.demo_mode) {
      applyDemoDefaults()
      return
    }
    applyPersonalDefaults()
  })()
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
    <AppCard class="qa-view__hero">
      <div>
        <p class="qa-view__eyebrow">Ask Your Reading Memory</p>
        <h2>让签签陪你追问自己的读书笔记。</h2>
        <p>
          选择全库或单本书范围，签签会先检索相关摘录，再带着引用来源整理回答。每一次追问都能回到原始笔记。
        </p>
        <MascotBubble
          class="qa-view__mascot"
          :mood="mascotCue.mood"
          :message="mascotCue.message"
          :celebrating="mascotCue.celebrating"
          compact
        />
      </div>
      <div class="qa-view__hero-meta">
        <span>{{ scope === 'current-book' ? '当前书籍' : '检索范围' }}</span>
        <strong>{{ scope === 'current-book' ? (currentScopedBook?.title || '待选择') : '全部书籍' }}</strong>
      </div>
    </AppCard>

    <section class="qa-view__layout">
      <QaHistoryPanel
        :sessions="sessions"
        :saved-answers="savedAnswers"
        :question-workspaces="questionWorkspaces"
        :current-session-id="currentSession?.id"
        @new-conversation="qaStore.resetConversation"
        @restore="restoreSession"
        @toggle-pin="qaStore.togglePinSession"
        @rename="renameSession"
        @delete="deleteSession"
        @restore-saved="qaStore.restoreSavedAnswer"
        @delete-saved="qaStore.deleteSavedAnswer"
        @restore-workspace="qaStore.restoreWorkspace"
        @delete-workspace="qaStore.deleteWorkspace"
        @update-workspace-status="updateWorkspaceStatus"
        @workspace-action="handleWorkspaceAction"
      />

      <AppCard class="qa-view__main">
        <div class="qa-view__chips">
          <el-tag v-for="prompt in QA_QUICK_PROMPTS" :key="prompt" round @click="usePrompt(prompt)">
            {{ prompt }}
          </el-tag>
        </div>

        <div v-if="scope === 'current-book'" class="qa-view__scope-tip">
          <strong>当前范围</strong>
          <span>{{ currentScopedBook ? `仅检索《${currentScopedBook.title}》` : '仅检索指定书籍' }}</span>
        </div>

        <div v-if="scope === 'current-book' && currentBookPrompts.length" class="qa-view__book-prompts">
          <el-button v-for="prompt in currentBookPrompts" :key="prompt" round @click="usePrompt(prompt)">
            {{ prompt }}
          </el-button>
        </div>

        <QaStatusPanel
          :status="status"
          :generation-mode="generationMode"
          :retrieval-mode="retrievalMode"
          :fallback-reason="fallbackReason"
          :error-message="errorMessage"
          :query-rewrite="queryRewrite"
          :evidence="evidence"
          @review-by-topic="reviewByTopic"
        />

        <QaConversation
          ref="conversationRef"
          :messages="messages"
          :loading="loading"
          :status-detail="status.detail"
          :highlight-query="latestQuestion"
          @jump-to-note="jumpToNote"
        />

        <div v-if="latestAssistantMessage" class="qa-view__followups">
          <div class="qa-view__answer-toolbar">
            <AppStatusStrip :items="conversationMeta" />
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
              <el-button
                round
                :type="latestAnswerSaved ? 'success' : 'default'"
                :disabled="loading || !latestAssistantMessage"
                @click="toggleSaveLatestAnswer"
              >
                {{ latestAnswerSaved ? '已收藏' : '收藏回答' }}
              </el-button>
              <el-button
                round
                :type="latestWorkspace ? 'success' : 'default'"
                :disabled="loading || !latestAssistantMessage"
                @click="saveLatestToWorkspace"
              >
                {{ latestWorkspace ? '更新问题' : '沉淀为问题' }}
              </el-button>
              <el-button
                round
                :loading="qaStore.exporting"
                :disabled="loading || !hasExportableMessages"
                @click="exportConversation"
              >
                导出 Markdown
              </el-button>
            </div>
          </div>
          <strong class="qa-view__followup-title">继续追问</strong>
          <div class="qa-view__followup-list">
            <el-button v-for="prompt in followupPrompts" :key="prompt" round @click="useFollowupPrompt(prompt)">
              {{ prompt }}
            </el-button>
          </div>
          <div class="qa-view__deposit">
            <div class="qa-view__deposit-copy">
              <div class="qa-view__deposit-heading">
                <strong>{{ latestWorkspace ? '问题已进入工作台' : '沉淀这次回答' }}</strong>
                <el-tag v-if="latestWorkspace" round effect="plain">
                  {{ latestWorkspace.evidence_count }} 条证据
                </el-tag>
              </div>
              <p>
                {{ latestWorkspace
                  ? `已沉淀为问题。${latestWorkspace.next_action}`
                  : '把这次回答保存成洞察、复习线索或自己的理解，让 AI 结果真正留下来。'
                }}
              </p>
            </div>
            <AppActionGrid :actions="depositActions" @action="handleDepositAction" />
          </div>
        </div>

        <QaInputBox
          v-model:draft="draft"
          v-model:scope="scope"
          :loading="loading"
          :stopped="stopped"
          :has-messages="messages.length > 0"
          :book-id="scopedBookId"
          :books="selectableBooks"
          @ask="handleAsk"
          @regenerate="qaStore.regenerateLastAnswer"
          @stop="qaStore.stopStreaming"
          @scope-change="handleScopeChange"
          @book-change="scopedBookId = $event"
        />
      </AppCard>

      <QaReferencePanel
        :references="latestReferences"
        :highlight-query="latestQuestion"
        @jump-to-note="jumpToNote"
      />
    </section>
  </div>
</template>

<style scoped lang="scss">
.qa-view {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.qa-view__hero {
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  padding: 28px;
  background:
    radial-gradient(circle at 88% 14%, rgba(47, 93, 80, 0.2), transparent 28%),
    linear-gradient(135deg, rgba(192, 139, 92, 0.13), rgba(255, 253, 249, 0.96) 62%),
    var(--bg-card);
}

.qa-view__eyebrow {
  margin: 0 0 10px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.qa-view__hero h2 {
  max-width: 50rem;
  margin: 0 0 10px;
  font-size: clamp(1.6rem, 2.4vw, 2.4rem);
  letter-spacing: -0.04em;
}

.qa-view__mascot {
  max-width: 560px;
  margin-top: 16px;
}

.qa-view__hero p:last-child {
  max-width: 48rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.qa-view__hero-meta {
  min-width: 180px;
  padding: 16px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.76);
  box-shadow: var(--shadow-sm);
}

.qa-view__hero-meta span {
  display: block;
  margin-bottom: 8px;
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.qa-view__hero-meta strong {
  color: var(--brand-primary);
  line-height: 1.45;
}

.qa-view__layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1.4fr) 360px;
  gap: 18px;
  align-items: stretch;
}

.qa-view__main {
  min-height: 720px;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 24px;
  background:
    linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(251, 248, 242, 0.9)),
    var(--bg-card);
}

.qa-view__chips {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}

.qa-view__chips :deep(.el-tag) {
  cursor: pointer;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease;
}

.qa-view__chips :deep(.el-tag:hover) {
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(57, 45, 31, 0.08);
}

.qa-view__book-prompts {
  margin-bottom: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
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

.qa-view__answer-toolbar {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  align-items: start;
  padding: 12px;
  border: 1px solid rgba(47, 93, 80, 0.1);
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.05), rgba(255, 253, 249, 0.72)),
    rgba(255, 253, 249, 0.72);
}

.qa-view__feedback-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-start;
  min-width: 0;
}

.qa-view__followup-title {
  display: block;
}

.qa-view__followup-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.qa-view__deposit {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
  padding: 15px;
  border: 1px solid rgba(47, 93, 80, 0.13);
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.07), rgba(192, 139, 92, 0.06)),
    var(--bg-card);
}

.qa-view__deposit-copy {
  min-width: 0;
}

.qa-view__deposit-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex-wrap: wrap;
}

.qa-view__deposit strong,
.qa-view__deposit p {
  display: block;
}

.qa-view__deposit p {
  margin: 5px 0 0;
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

@media (max-width: 1180px) {
  .qa-view__layout {
    grid-template-columns: 1fr;
  }

  .qa-view__main {
    min-height: auto;
    height: auto;
  }

  .qa-view__answer-toolbar {
    grid-template-columns: 1fr;
  }

}
@media (max-width: 768px) {
  .qa-view__hero {
    align-items: flex-start;
    flex-direction: column;
    padding: 22px;
  }

  .qa-view__hero-meta {
    width: 100%;
  }
}

</style>
