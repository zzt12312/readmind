<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import type { QaReference } from '@/types/qa'
import { highlightText } from '@/utils/text'

const props = defineProps<{
  references: QaReference[]
  highlightQuery: string
}>()

defineEmits<{
  jumpToNote: [bookId: number, noteId: number]
}>()

function renderReferenceHighlight(text: string) {
  return highlightText(text, props.highlightQuery)
}
</script>

<template>
  <AppCard class="qa-reference-panel">
    <div class="qa-reference-panel__header">
      <div>
        <h3>引用来源</h3>
        <p>回答中最核心的证据片段会集中展示在这里。</p>
      </div>
      <el-tag round effect="plain">{{ references.length }} 条</el-tag>
    </div>
    <div class="qa-reference-panel__list">
      <article
        v-for="reference in references"
        :key="reference.book + reference.chapter + reference.note_id"
        class="qa-reference-panel__card"
      >
        <div class="qa-reference-panel__head">
          <strong>{{ reference.book }}</strong>
          <span>{{ reference.chapter }}</span>
        </div>
        <p v-html="renderReferenceHighlight(reference.excerpt)" />
        <el-button text @click="$emit('jumpToNote', reference.book_id, reference.note_id)">跳转原笔记</el-button>
      </article>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.qa-reference-panel {
  min-height: 720px;
  height: 100%;
  padding: 22px;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 96% 8%, rgba(192, 139, 92, 0.13), transparent 24%),
    rgba(255, 253, 249, 0.95);
}

.qa-reference-panel__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 14px;
}

.qa-reference-panel__header h3 {
  margin: 0 0 4px;
}

.qa-reference-panel__header p {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.84rem;
  line-height: 1.6;
}

.qa-reference-panel__list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.qa-reference-panel__card {
  padding: 15px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 16px;
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.045), transparent 34%),
    rgba(251, 248, 242, 0.76);
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.qa-reference-panel__card:hover {
  transform: translateY(-1px);
  border-color: rgba(47, 93, 80, 0.24);
  box-shadow: var(--shadow-sm);
}

.qa-reference-panel__head {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.qa-reference-panel__head span {
  color: var(--text-tertiary);
  font-size: 0.84rem;
}

.qa-reference-panel__card p {
  margin: 8px 0 10px;
  color: var(--text-secondary);
  line-height: 1.75;
  display: -webkit-box;
  -webkit-line-clamp: 5;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

:deep(mark) {
  padding: 0 2px;
  border-radius: 4px;
  background: rgba(192, 139, 92, 0.22);
}

@media (max-width: 1180px) {
  .qa-reference-panel {
    min-height: auto;
    height: auto;
  }
}
</style>
