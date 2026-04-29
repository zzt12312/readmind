<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import type { QaSession } from '@/types/qa'

defineProps<{
  sessions: QaSession[]
  currentSessionId?: string | null
}>()

defineEmits<{
  newConversation: []
  restore: [sessionId: string]
  togglePin: [sessionId: string]
  rename: [sessionId: string, currentTitle: string]
  delete: [sessionId: string]
}>()

function formatSessionTime(value: string) {
  return new Date(value).toLocaleString()
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
  </AppCard>
</template>

<style scoped lang="scss">
.qa-history {
  min-height: 720px;
  height: 100%;
  padding: 22px;
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
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.qa-history__item {
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 16px;
  background: rgba(251, 248, 242, 0.78);
  overflow: hidden;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.qa-history__item:hover {
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
  padding: 14px 14px 8px;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.qa-history__title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qa-history__item strong,
.qa-history__item span,
.qa-history__title {
  display: block;
}

.qa-history__item span,
.qa-history__empty {
  margin-top: 6px;
  color: var(--text-tertiary);
  font-size: 0.84rem;
}

.qa-history__actions {
  display: flex;
  gap: 4px;
  padding: 0 10px 10px;
  flex-wrap: wrap;
}

@media (max-width: 1180px) {
  .qa-history {
    min-height: auto;
    height: auto;
  }
}
</style>
