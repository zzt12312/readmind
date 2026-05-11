<script setup lang="ts">
import type { HighValueMatrixItem } from '@/types/analytics'

defineProps<{
  books: HighValueMatrixItem[]
  matrixListBooks: HighValueMatrixItem[]
  matrixTopBook?: HighValueMatrixItem
  clampPosition: (value: number) => number
}>()

const emit = defineEmits<{
  openBook: [bookId: number]
}>()
</script>

<template>
  <AppCard class="value-matrix analytics-panel">
    <div class="analytics-panel__head">
      <div>
        <p class="analytics-panel__eyebrow">Value matrix</p>
        <h3>高价值书籍矩阵</h3>
      </div>
      <span>横轴笔记密度，纵轴复习回看</span>
    </div>
    <div class="value-matrix__layout">
      <div class="value-matrix__canvas">
        <span class="value-matrix__axis is-y">高复习</span>
        <span class="value-matrix__axis is-x">高笔记</span>
        <button
          v-for="book in books"
          :key="book.id"
          type="button"
          :style="{ left: `${clampPosition(book.x)}%`, bottom: `${clampPosition(book.y)}%` }"
          :title="`${book.title}: ${book.note_count} 条笔记 / ${book.reviewed_count} 次复习`"
          @click="emit('openBook', book.id)"
        >
          {{ book.title.slice(0, 2) }}
        </button>
      </div>
      <div class="value-matrix__list">
        <article
          v-for="book in matrixListBooks"
          :key="book.id"
          @click="emit('openBook', book.id)"
        >
          <strong>{{ book.title }}</strong>
          <span>{{ book.note_count }} 条笔记 · {{ book.reviewed_count }} 次复习</span>
          <i :style="{ width: `${Math.min(100, Math.max(8, book.value_score))}%` }" />
        </article>
        <div v-if="matrixTopBook" class="value-matrix__note">
          <span>下一本优先回看</span>
          <strong>{{ matrixTopBook.title }}</strong>
          <p>这本书同时拥有较高摘录密度和复习痕迹，适合作为近期知识复盘入口。</p>
        </div>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.analytics-panel {
  padding: 22px;
}

.analytics-panel__head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.analytics-panel__head h3 {
  margin: 0;
}

.analytics-panel__head > span {
  color: var(--text-tertiary);
  font-size: 0.88rem;
}

.analytics-panel__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.value-matrix__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 210px;
  gap: 14px;
  align-items: stretch;
}

.value-matrix__canvas {
  position: relative;
  min-height: 220px;
  overflow: hidden;
  margin-bottom: 0;
  border: 1px solid rgba(216, 207, 191, 0.7);
  border-radius: 22px;
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(47, 93, 80, 0.08) 1px, transparent 1px),
    radial-gradient(circle at 80% 20%, rgba(197, 139, 92, 0.16), transparent 28%),
    rgba(255, 253, 249, 0.64);
  background-size:
    25% 100%,
    100% 25%,
    auto,
    auto;
}

.value-matrix__canvas button {
  position: absolute;
  translate: -50% 50%;
  width: 42px;
  height: 42px;
  border: 2px solid rgba(255, 253, 249, 0.92);
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 900;
  box-shadow: 0 14px 28px rgba(47, 93, 80, 0.2);
}

.value-matrix__axis {
  position: absolute;
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.value-matrix__axis.is-y {
  top: 12px;
  left: 14px;
}

.value-matrix__axis.is-x {
  right: 14px;
  bottom: 12px;
}

.value-matrix__list {
  display: grid;
  gap: 10px;
  align-content: start;
}

.value-matrix__list article,
.value-matrix__note {
  padding: 12px;
  overflow: hidden;
  border: 1px solid rgba(216, 207, 191, 0.64);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.72);
}

.value-matrix__list article {
  cursor: pointer;
}

.value-matrix__list strong,
.value-matrix__list span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.value-matrix__list span {
  margin-top: 4px;
  color: var(--text-tertiary);
  font-size: 0.82rem;
}

.value-matrix__list i {
  display: block;
  height: 6px;
  max-width: 100%;
  margin-top: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--brand-primary), #c58b5c);
}

.value-matrix__note {
  background:
    radial-gradient(circle at 100% 0%, rgba(197, 139, 92, 0.14), transparent 46%),
    rgba(47, 93, 80, 0.06);
}

.value-matrix__note span {
  color: var(--brand-primary);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.value-matrix__note strong {
  display: block;
  margin-top: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.value-matrix__note p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.55;
}

@media (max-width: 768px) {
  .value-matrix__layout {
    grid-template-columns: 1fr;
  }
}
</style>
