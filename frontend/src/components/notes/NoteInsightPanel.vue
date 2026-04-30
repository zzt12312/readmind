<script setup lang="ts">
import { computed } from 'vue'
import AppCard from '@/components/base/AppCard.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import { buildNoteInsightMascotCue } from '@/constants/mascotMessages'
import type { NoteInsightReference, NoteInsightSections, QueryRewriteSummary } from '@/types/note'

const props = defineProps<{
  refreshing: boolean
  hasGeneratedInsight: boolean
  insightState: {
    tone: string
    label: string
    detail: string
  }
  insightSummary: string
  insightSections: NoteInsightSections | null
  relatedTopics: string[]
  queryRewrite: QueryRewriteSummary | null
  insightReferences: NoteInsightReference[]
  insightJobStatus: '' | 'queued' | 'processing' | 'success' | 'failed' | 'canceled'
}>()

defineEmits<{
  refresh: []
  exportInsight: []
  reviewByTopic: [topic: string]
  jumpToReference: [reference: NoteInsightReference]
}>()

const mascotCue = computed(() => buildNoteInsightMascotCue({
  refreshing: props.refreshing,
  hasGeneratedInsight: props.hasGeneratedInsight,
  status: props.insightJobStatus,
}))
</script>

<template>
  <AppCard class="note-insight-panel">
    <div class="note-insight-panel__header">
      <div>
        <p>Insight</p>
        <h3>AI 洞察</h3>
      </div>
      <el-button text :loading="refreshing" @click="$emit('refresh')">
        {{ hasGeneratedInsight ? '重新总结' : '生成总结' }}
      </el-button>
    </div>
    <div v-if="hasGeneratedInsight" class="note-insight-panel__tools">
      <el-button round size="small" @click="$emit('exportInsight')">导出洞察</el-button>
    </div>
    <section class="note-insight-panel__state" :class="`is-${insightState.tone}`">
      <strong>{{ insightState.label }}</strong>
      <p>{{ insightState.detail }}</p>
    </section>
    <MascotBubble
      class="note-insight-panel__mascot"
      :mood="mascotCue.mood"
      :message="mascotCue.message"
      :celebrating="mascotCue.celebrating"
      compact
    />
    <div class="note-insight-panel__scroll">
      <template v-if="hasGeneratedInsight">
        <section class="note-insight-panel__section">
          <strong>核心结论</strong>
          <p>{{ insightSummary }}</p>
        </section>
        <section v-if="insightSections?.reasoning" class="note-insight-panel__section">
          <strong>为什么值得关注</strong>
          <p>{{ insightSections.reasoning }}</p>
        </section>
        <section class="note-insight-panel__section">
          <strong>关联主题</strong>
          <div class="note-insight-panel__tag-list">
            <el-tag
              v-for="topic in (insightSections?.key_themes?.length ? insightSections.key_themes : relatedTopics)"
              :key="topic"
              round
              @click="$emit('reviewByTopic', topic)"
            >
              {{ topic }}
            </el-tag>
          </div>
        </section>
        <section v-if="insightSections?.review_questions?.length" class="note-insight-panel__section">
          <strong>值得复习的问题</strong>
          <ul class="note-insight-panel__list">
            <li v-for="question in insightSections.review_questions" :key="question">{{ question }}</li>
          </ul>
        </section>
        <section v-if="insightSections?.action_suggestions?.length" class="note-insight-panel__section">
          <strong>可执行建议</strong>
          <ul class="note-insight-panel__list">
            <li v-for="suggestion in insightSections.action_suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </section>
        <section v-if="queryRewrite" class="note-insight-panel__section">
          <strong>本次检索如何扩展问题</strong>
          <p>为了更稳地召回相关笔记，系统额外补充了以下概念词。</p>
          <div class="note-insight-panel__tag-list">
            <el-tag v-for="term in queryRewrite.expansion_terms.slice(0, 8)" :key="term" round effect="plain">
              {{ term }}
            </el-tag>
          </div>
        </section>
        <section v-if="insightReferences.length" class="note-insight-panel__section">
          <strong>引用依据</strong>
          <div class="note-insight-panel__references">
            <article
              v-for="reference in insightReferences"
              :key="reference.book + reference.chapter + reference.excerpt"
              class="note-insight-panel__reference"
              @click="$emit('jumpToReference', reference)"
            >
              <p class="note-insight-panel__reference-title">{{ reference.book }} · {{ reference.chapter }}</p>
              <blockquote>{{ reference.excerpt }}</blockquote>
            </article>
          </div>
        </section>
      </template>
      <section
        v-else-if="insightJobStatus === 'queued' || insightJobStatus === 'processing'"
        class="note-insight-panel__section note-insight-panel__section--placeholder"
      >
        <strong>{{ insightState.label }}</strong>
        <p>{{ insightState.detail }}</p>
      </section>
      <section
        v-else-if="insightJobStatus === 'failed'"
        class="note-insight-panel__section note-insight-panel__section--placeholder note-insight-panel__section--error"
      >
        <strong>{{ insightState.label }}</strong>
        <p>{{ insightState.detail }}</p>
      </section>
      <section v-else class="note-insight-panel__section note-insight-panel__section--placeholder">
        <strong>{{ insightState.label }}</strong>
        <p>{{ insightState.detail }}</p>
      </section>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.note-insight-panel {
  position: sticky;
  top: 106px;
  max-height: calc(100vh - 126px);
  padding: 18px;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 92% 8%, rgba(47, 93, 80, 0.12), transparent 24%),
    rgba(255, 253, 249, 0.95);
}

.note-insight-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.note-insight-panel__header p {
  margin: 0 0 6px;
  color: var(--brand-accent);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.note-insight-panel__header h3 {
  margin: 0;
}

.note-insight-panel__tools {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.note-insight-panel__state {
  margin-top: 12px;
  padding: 11px 12px;
  border-radius: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.72)),
    rgba(47, 93, 80, 0.05);
}

.note-insight-panel__state.is-danger {
  border-color: rgba(190, 76, 60, 0.22);
  background: rgba(190, 76, 60, 0.08);
}

.note-insight-panel__state.is-success {
  border-color: rgba(47, 93, 80, 0.2);
  background: rgba(47, 93, 80, 0.08);
}

.note-insight-panel__state strong {
  display: block;
  margin-bottom: 4px;
}

.note-insight-panel__mascot {
  margin-top: 10px;
  flex: 0 0 auto;
}

.note-insight-panel__mascot :deep(.mascot-bubble__avatar) {
  width: 42px;
  height: 42px;
  min-width: 42px;
  border-radius: 15px;
}

.note-insight-panel__mascot :deep(.mascot-bubble__content p) {
  display: -webkit-box;
  overflow: hidden;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.note-insight-panel__mascot :deep(.mascot-bubble) {
  padding: 9px 10px;
  gap: 9px;
  box-shadow: none;
}

.note-insight-panel__state p,
.note-insight-panel__section p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.75;
}

.note-insight-panel__scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  margin-top: 12px;
  padding: 0 4px 16px 0;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
}

.note-insight-panel__section {
  margin-top: 10px;
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 14px;
  background: rgba(255, 253, 249, 0.58);
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.note-insight-panel__section > strong {
  color: var(--brand-primary);
  font-size: 0.92rem;
}

.note-insight-panel__section--placeholder {
  padding: 14px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
}

.note-insight-panel__section--error {
  color: #b2523c;
}

.note-insight-panel__tag-list,
.note-insight-panel__references {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.note-insight-panel__references {
  flex-direction: column;
  gap: 10px;
}

.note-insight-panel__list {
  margin: 0;
  padding-left: 17px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.note-insight-panel__list li + li {
  margin-top: 5px;
}

.note-insight-panel__reference {
  padding: 11px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 12px;
  background: rgba(251, 248, 242, 0.82);
  cursor: pointer;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.note-insight-panel__reference:hover {
  transform: translateY(-1px);
  border-color: rgba(47, 93, 80, 0.24);
  box-shadow: var(--shadow-sm);
}

.note-insight-panel__reference-title {
  margin: 0 0 6px;
  color: var(--brand-primary);
  font-size: 0.84rem;
}

.note-insight-panel__reference blockquote {
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid rgba(192, 139, 92, 0.5);
  color: var(--text-secondary);
  line-height: 1.68;
}

@media (max-width: 1280px) {
  .note-insight-panel {
    position: static;
    max-height: none;
  }

  .note-insight-panel__scroll {
    overflow: visible;
    padding-right: 0;
  }
}

@media (max-width: 420px) {
  .note-insight-panel__mascot :deep(.mascot-bubble.is-portrait) {
    grid-template-columns: 1fr;
  }

  .note-insight-panel__mascot :deep(.mascot-bubble__avatar) {
    max-width: 180px;
    margin: 0 auto;
  }
}
</style>
