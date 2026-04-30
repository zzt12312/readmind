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

const evidenceLevel = computed(() => {
  if (!props.evidence) {
    return null
  }
  if (props.evidence.reference_count >= 3 && props.evidence.sufficient) {
    return {
      tone: 'strong',
      label: '证据充分',
      action: '可以继续追问细节，或从右侧引用回到原始摘录。',
    }
  }
  if (props.evidence.reference_count > 0) {
    return {
      tone: 'partial',
      label: '证据一般',
      action: '更适合回答局部重点；想要更完整答案，可以切换到全库或换一个更具体的问题。',
    }
  }
  return {
    tone: 'weak',
    label: '证据不足',
    action: '当前没有可用引用，建议放宽检索范围、换关键词，或先去笔记工作台确认相关摘录。',
  }
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

  <div
    v-if="evidence && evidenceLevel"
    class="qa-status-panel__evidence"
    :class="`is-${evidenceLevel.tone}`"
  >
    <div class="qa-status-panel__evidence-head">
      <strong>{{ evidenceLevel.label }}</strong>
      <span>{{ evidence.reference_count }} 条引用</span>
    </div>
    <p>{{ evidence.message }}</p>
    <div class="qa-status-panel__evidence-meta">
      <span>建议回答 {{ evidence.suggested_points }} 个重点</span>
      <span>{{ evidenceLevel.action }}</span>
    </div>
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

.qa-status-panel__evidence.is-partial {
  background: rgba(192, 139, 92, 0.08);
  border-color: rgba(192, 139, 92, 0.2);
}

.qa-status-panel__evidence.is-weak {
  background: rgba(190, 76, 60, 0.07);
  border-color: rgba(190, 76, 60, 0.18);
}

.qa-status-panel__evidence-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.qa-status-panel__evidence-head span {
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.82);
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  white-space: nowrap;
}

.qa-status-panel__evidence-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.qa-status-panel__evidence-meta span {
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.78);
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 700;
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
