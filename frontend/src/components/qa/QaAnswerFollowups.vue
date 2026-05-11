<script setup lang="ts">
import AppActionGrid from '@/components/base/AppActionGrid.vue'
import AppStatusStrip from '@/components/base/AppStatusStrip.vue'
import type { QaMessage, QaQuestionWorkspace } from '@/types/qa'

interface DepositAction {
  id: string
  index: string
  title: string
  type: string
  saved?: boolean
  disabled?: boolean
}

interface StatusItem {
  label: string
  value: string
}

defineProps<{
  latestAssistantMessage: QaMessage
  conversationMeta: StatusItem[]
  followupPrompts: string[]
  depositActions: DepositAction[]
  loading: boolean
  exporting: boolean
  hasExportableMessages: boolean
  latestAnswerSaved: boolean
  latestWorkspace: QaQuestionWorkspace | null
}>()

const emit = defineEmits<{
  feedback: [messageId: string, feedback: 'up' | 'down']
  regenerate: []
  toggleSave: []
  saveWorkspace: []
  exportConversation: []
  useFollowup: [prompt: string]
  depositAction: [actionId: string]
}>()
</script>

<template>
  <div class="qa-followups">
    <div class="qa-followups__toolbar">
      <AppStatusStrip :items="conversationMeta" />
      <div class="qa-followups__feedback-actions">
        <el-button
          round
          :type="latestAssistantMessage.feedback === 'up' ? 'primary' : 'default'"
          @click="emit('feedback', latestAssistantMessage.id, 'up')"
        >
          有帮助
        </el-button>
        <el-button
          round
          :type="latestAssistantMessage.feedback === 'down' ? 'warning' : 'default'"
          @click="emit('feedback', latestAssistantMessage.id, 'down')"
        >
          不够准确
        </el-button>
        <el-button round :disabled="loading" @click="emit('regenerate')">重新生成这一轮</el-button>
        <el-button
          round
          :type="latestAnswerSaved ? 'success' : 'default'"
          :disabled="loading"
          @click="emit('toggleSave')"
        >
          {{ latestAnswerSaved ? '已收藏' : '收藏回答' }}
        </el-button>
        <el-button
          round
          :type="latestWorkspace ? 'success' : 'default'"
          :disabled="loading"
          @click="emit('saveWorkspace')"
        >
          {{ latestWorkspace ? '更新问题' : '沉淀为问题' }}
        </el-button>
        <el-button
          round
          :loading="exporting"
          :disabled="loading || !hasExportableMessages"
          @click="emit('exportConversation')"
        >
          导出 Markdown
        </el-button>
      </div>
    </div>
    <strong class="qa-followups__title">继续追问</strong>
    <div class="qa-followups__list">
      <el-button v-for="prompt in followupPrompts" :key="prompt" round @click="emit('useFollowup', prompt)">
        {{ prompt }}
      </el-button>
    </div>
    <div class="qa-followups__deposit">
      <div class="qa-followups__deposit-copy">
        <div class="qa-followups__deposit-heading">
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
      <AppActionGrid :actions="depositActions" @action="emit('depositAction', $event)" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.qa-followups {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qa-followups__toolbar {
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

.qa-followups__feedback-actions,
.qa-followups__list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.qa-followups__feedback-actions {
  justify-content: flex-start;
  min-width: 0;
}

.qa-followups__title {
  display: block;
}

.qa-followups__deposit {
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

.qa-followups__deposit-copy {
  min-width: 0;
}

.qa-followups__deposit-heading {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex-wrap: wrap;
}

.qa-followups__deposit strong,
.qa-followups__deposit p {
  display: block;
}

.qa-followups__deposit p {
  margin: 5px 0 0;
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}
</style>
