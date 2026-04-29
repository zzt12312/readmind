<script setup lang="ts">
import { computed } from 'vue'
import type { QaEvidenceSummary, QaStatusPayload, QueryRewriteSummary } from '@/types/qa'

const props = defineProps<{
  status: QaStatusPayload
  generationMode: 'llm' | 'fallback'
  retrievalMode: string
  fallbackReason?: string
  errorMessage?: string
  queryRewrite?: QueryRewriteSummary | null
  evidence?: QaEvidenceSummary | null
}>()

defineEmits<{
  reviewByTopic: [topic: string]
}>()

const statusTone = computed(() => {
  if (props.status.phase === 'failed') return 'danger'
  if (props.status.phase === 'fallback') return 'warning'
  if (props.status.phase === 'success') return props.generationMode === 'fallback' ? 'warning' : 'success'
  return 'primary'
})
</script>

<template>
  <div class="qa-status-panel" :class="`is-${statusTone}`">
    <div>
      <strong>{{ status.label }}</strong>
      <p>{{ status.detail }}</p>
    </div>
    <div class="qa-status-panel__meta">
      <el-tag round effect="plain">{{ retrievalMode === 'hybrid' ? '混合检索' : retrievalMode }}</el-tag>
      <el-tag round effect="plain" :type="generationMode === 'fallback' ? 'warning' : 'success'">
        {{ generationMode === 'fallback' ? '本地回退' : '模型生成' }}
      </el-tag>
    </div>
  </div>

  <div v-if="evidence" class="qa-status-panel__evidence" :class="{ 'is-warning': !evidence.sufficient }">
    <strong>证据充足度</strong>
    <p>{{ evidence.message }}</p>
  </div>

  <div v-if="queryRewrite" class="qa-status-panel__rewrite">
    <strong>检索扩展</strong>
    <p>系统识别到你在追问 <span>{{ queryRewrite.applied_rules.join('、') }}</span>，所以额外补充了这些概念来扩大召回：</p>
    <div class="qa-status-panel__rewrite-tags">
      <el-tag
        v-for="term in queryRewrite.expansion_terms.slice(0, 8)"
        :key="term"
        round
        effect="plain"
        type="success"
        @click="$emit('reviewByTopic', term)"
      >
        {{ term }}
      </el-tag>
    </div>
  </div>

  <p v-if="fallbackReason" class="qa-status-panel__tip qa-status-panel__tip--warning">
    模型暂时不可用，当前已自动切换到回退回答。{{ fallbackReason }}
  </p>
  <p v-else-if="errorMessage" class="qa-status-panel__tip qa-status-panel__tip--warning">
    {{ errorMessage }}
  </p>
</template>

<style scoped lang="scss">
.qa-status-panel {
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

.qa-status-panel.is-warning {
  border-color: rgba(192, 139, 92, 0.24);
  background: rgba(192, 139, 92, 0.08);
}

.qa-status-panel.is-success {
  border-color: rgba(47, 93, 80, 0.2);
  background: rgba(47, 93, 80, 0.08);
}

.qa-status-panel.is-danger {
  border-color: rgba(190, 76, 60, 0.22);
  background: rgba(190, 76, 60, 0.08);
}

.qa-status-panel strong,
.qa-status-panel__evidence strong,
.qa-status-panel__rewrite strong {
  display: block;
  margin-bottom: 6px;
}

.qa-status-panel p,
.qa-status-panel__evidence p,
.qa-status-panel__rewrite p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.qa-status-panel__meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.qa-status-panel__evidence,
.qa-status-panel__rewrite {
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
  border: 1px solid rgba(47, 93, 80, 0.08);
}

.qa-status-panel__evidence.is-warning {
  background: rgba(192, 139, 92, 0.08);
  border-color: rgba(192, 139, 92, 0.2);
}

.qa-status-panel__rewrite {
  padding: 14px 16px;
}

.qa-status-panel__rewrite p {
  margin-bottom: 10px;
}

.qa-status-panel__rewrite span {
  color: var(--text-primary);
  font-weight: 600;
}

.qa-status-panel__rewrite-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.qa-status-panel__tip {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.84rem;
}

.qa-status-panel__tip--warning {
  color: #9a6131;
}
</style>

