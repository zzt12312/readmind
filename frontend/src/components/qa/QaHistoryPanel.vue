<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import type { QaQuestionWorkspace, QaSavedAnswer, QaSession, QaWorkspaceAction, QaWorkspaceStatus } from '@/types/qa'

defineProps<{
  sessions: QaSession[]
  savedAnswers: QaSavedAnswer[]
  questionWorkspaces: QaQuestionWorkspace[]
  currentSessionId?: string | null
}>()

defineEmits<{
  newConversation: []
  restore: [sessionId: string]
  togglePin: [sessionId: string]
  rename: [sessionId: string, currentTitle: string]
  delete: [sessionId: string]
  restoreSaved: [savedAnswerId: string]
  deleteSaved: [savedAnswerId: string]
  restoreWorkspace: [workspaceId: string]
  deleteWorkspace: [workspaceId: string]
  updateWorkspaceStatus: [workspaceId: string, status: QaWorkspaceStatus]
  workspaceAction: [workspaceId: string, action: QaWorkspaceAction]
}>()

function formatSessionTime(value: string) {
  return new Date(value).toLocaleString()
}

function statusLabel(status: QaWorkspaceStatus) {
  if (status === 'writing') return '写作中'
  if (status === 'reviewing') return '待复习'
  return '追问中'
}
</script>

<template>
  <AppCard class="qa-history">
    <div class="qa-history__header">
      <h3>问答历史</h3>
      <el-button text @click="$emit('newConversation')">新对话</el-button>
    </div>
    <div v-if="sessions.length" class="qa-history__list">
      <article
        v-for="session in sessions"
        :key="session.id"
        class="qa-history__item"
        :class="{ 'is-active': currentSessionId === session.id }"
      >
        <button type="button" class="qa-history__main" @click="$emit('restore', session.id)">
          <div class="qa-history__title">
            <strong>{{ session.title }}</strong>
            <el-tag v-if="session.pinned" size="small" round effect="plain">置顶</el-tag>
          </div>
          <span>{{ session.scope === 'current-book' ? '单本书' : '全库' }} · {{ formatSessionTime(session.updated_at) }}</span>
        </button>
        <div class="qa-history__actions">
          <el-button text size="small" @click.stop="$emit('togglePin', session.id)">
            {{ session.pinned ? '取消置顶' : '置顶' }}
          </el-button>
          <el-button text size="small" @click.stop="$emit('rename', session.id, session.title)">重命名</el-button>
          <el-button text size="small" type="danger" @click.stop="$emit('delete', session.id)">删除</el-button>
        </div>
      </article>
    </div>
    <p v-else class="qa-history__empty">还没有历史会话，问一个问题后会自动保存。</p>

    <div class="qa-history__saved-header">
      <h3>问题工作台</h3>
      <el-tag round effect="plain">{{ questionWorkspaces.length }} 个</el-tag>
    </div>
    <div v-if="questionWorkspaces.length" class="qa-history__workspace-list">
      <article
        v-for="item in questionWorkspaces"
        :key="item.id"
        class="qa-history__workspace-item"
      >
        <button type="button" class="qa-history__main" @click="$emit('restoreWorkspace', item.id)">
          <div class="qa-history__title">
            <strong>{{ item.title }}</strong>
            <el-tag size="small" round effect="plain">{{ statusLabel(item.status) }}</el-tag>
          </div>
          <span>{{ item.evidence_count }} 条引用 · {{ formatSessionTime(item.updated_at) }}</span>
          <p>{{ item.next_action }}</p>
        </button>
        <div class="qa-history__actions">
          <el-button text size="small" @click.stop="$emit('workspaceAction', item.id, 'followup')">追问</el-button>
          <el-button text size="small" @click.stop="$emit('workspaceAction', item.id, 'writing')">写作</el-button>
          <el-button text size="small" @click.stop="$emit('workspaceAction', item.id, 'reviewing')">复习</el-button>
          <el-button text size="small" type="danger" @click.stop="$emit('deleteWorkspace', item.id)">删除</el-button>
        </div>
      </article>
    </div>
    <p v-else class="qa-history__empty">把重要回答沉淀为问题后，会在这里持续追问和整理证据。</p>

    <div class="qa-history__saved-header">
      <h3>收藏回答</h3>
      <el-tag round effect="plain">{{ savedAnswers.length }} 条</el-tag>
    </div>
    <div v-if="savedAnswers.length" class="qa-history__saved-list">
      <article
        v-for="item in savedAnswers"
        :key="item.id"
        class="qa-history__saved-item"
      >
        <button type="button" class="qa-history__main" @click="$emit('restoreSaved', item.id)">
          <strong>{{ item.title }}</strong>
          <span>{{ item.scope === 'current-book' ? '单本书' : '全库' }} · {{ formatSessionTime(item.saved_at) }}</span>
          <p>{{ item.answer }}</p>
        </button>
        <div class="qa-history__actions">
          <el-button text size="small" type="danger" @click.stop="$emit('deleteSaved', item.id)">取消收藏</el-button>
        </div>
      </article>
    </div>
    <p v-else class="qa-history__empty">遇到值得保留的回答，可以在回答下方点击收藏。</p>
  </AppCard>
</template>

<style scoped lang="scss">
.qa-history {
  min-height: 720px;
  height: 100%;
  padding: 24px 22px;
  display: flex;
  flex-direction: column;
  background:
    linear-gradient(180deg, rgba(255, 253, 249, 0.96), rgba(251, 248, 242, 0.88)),
    var(--bg-card);
}

.qa-history__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 14px;
}

.qa-history__list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 360px;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.qa-history__item,
.qa-history__saved-item,
.qa-history__workspace-item {
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 16px;
  background: rgba(251, 248, 242, 0.78);
  overflow: visible;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.qa-history__item:hover,
.qa-history__saved-item:hover,
.qa-history__workspace-item:hover {
  transform: translateY(-1px);
  border-color: rgba(47, 93, 80, 0.22);
  box-shadow: var(--shadow-sm);
}

.qa-history__item.is-active {
  border-color: rgba(47, 93, 80, 0.35);
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.08);
}

.qa-history__main {
  width: 100%;
  padding: 16px 14px 12px;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.qa-history__title {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  min-width: 0;
}

.qa-history__title strong {
  flex: 1 1 auto;
  overflow: visible;
  white-space: normal;
  overflow-wrap: anywhere;
  line-height: 1.65;
  padding-bottom: 2px;
}

.qa-history__title :deep(.el-tag) {
  flex: 0 0 auto;
  margin-top: 2px;
}

.qa-history__item strong,
.qa-history__item span,
.qa-history__saved-item strong,
.qa-history__saved-item span,
.qa-history__workspace-item strong,
.qa-history__workspace-item span {
  display: block;
  min-width: 0;
  line-height: 1.6;
}

.qa-history__item span,
.qa-history__saved-item span,
.qa-history__workspace-item span,
.qa-history__empty {
  margin-top: 6px;
  color: var(--text-tertiary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.qa-history__saved-header {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  margin: 18px 0 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(216, 207, 191, 0.64);
}

.qa-history__saved-header h3 {
  margin: 0;
}

.qa-history__saved-list,
.qa-history__workspace-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 260px;
  overflow-y: auto;
  padding-right: 4px;
}

.qa-history__saved-item,
.qa-history__workspace-item {
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.06), transparent 46%),
    rgba(251, 248, 242, 0.78);
}

.qa-history__saved-item p,
.qa-history__workspace-item p {
  display: -webkit-box;
  overflow: hidden;
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.qa-history__actions {
  display: flex;
  gap: 4px;
  padding: 2px 10px 12px;
  flex-wrap: wrap;
}

@media (max-width: 1180px) {
  .qa-history {
    min-height: auto;
    height: auto;
  }
}
</style>
