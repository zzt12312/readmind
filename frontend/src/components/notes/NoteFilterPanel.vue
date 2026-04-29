<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import type { BookItem } from '@/types/book'
import type { NoteFilters } from '@/types/note'

defineProps<{
  currentBook: BookItem | null
  activeBookId?: number | null
  filters: NoteFilters
  selectedTag: string
}>()

defineEmits<{
  askCurrentBook: []
  selectTag: [tag: string]
}>()
</script>

<template>
  <AppCard class="note-filter-panel">
    <p class="note-filter-panel__eyebrow">Scope</p>
    <h3>筛选范围</h3>
    <div class="note-filter-panel__filters">
      <div class="note-filter-panel__book">
        <strong>书籍</strong>
        <p>{{ currentBook ? currentBook.title : activeBookId ? `已定位到书籍 #${activeBookId}` : '全部书籍' }}</p>
        <el-button v-if="currentBook" text @click="$emit('askCurrentBook')">问这本书</el-button>
      </div>
      <div class="note-filter-panel__section">
        <strong>标签</strong>
        <div class="note-filter-panel__tag-list">
          <el-tag
            v-for="tag in filters.tags.slice(0, 8)"
            :key="tag"
            round
            effect="plain"
            :type="selectedTag === tag ? 'success' : 'info'"
            @click="$emit('selectTag', tag)"
          >
            {{ tag }}
          </el-tag>
        </div>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.note-filter-panel {
  position: sticky;
  top: 106px;
  padding: 22px;
  background:
    linear-gradient(180deg, rgba(255, 253, 249, 0.96), rgba(251, 248, 242, 0.88)),
    var(--bg-card);
}

.note-filter-panel__eyebrow {
  margin: 0 0 6px;
  color: var(--brand-accent);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.note-filter-panel h3 {
  margin: 0 0 18px;
}

.note-filter-panel__filters {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.note-filter-panel__filters p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.note-filter-panel__book,
.note-filter-panel__section {
  padding: 14px;
  border-radius: 18px;
  background: rgba(47, 93, 80, 0.055);
}

.note-filter-panel__book strong,
.note-filter-panel__section strong {
  color: var(--text-primary);
}

.note-filter-panel__tag-list {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.note-filter-panel__tag-list :deep(.el-tag) {
  cursor: pointer;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease;
}

.note-filter-panel__tag-list :deep(.el-tag:hover) {
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(57, 45, 31, 0.08);
}

@media (max-width: 1280px) {
  .note-filter-panel {
    position: static;
  }
}
</style>
