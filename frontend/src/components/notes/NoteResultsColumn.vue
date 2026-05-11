<script setup lang="ts">
import AppEmpty from '@/components/base/AppEmpty.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import NoteCard from '@/components/notes/NoteCard.vue'
import QueryRewriteTip from '@/components/notes/QueryRewriteTip.vue'
import type { MascotCue } from '@/constants/mascotMessages'
import type { NoteItem, NotePagination, QueryRewriteSummary } from '@/types/note'

defineProps<{
  loading: boolean
  notes: NoteItem[]
  activeNoteId: number | null
  keyword: string
  scopeTitle: string
  pagination: NotePagination
  queryRewrite: QueryRewriteSummary | null
  emptyMascotCue: MascotCue
}>()

defineEmits<{
  loadMore: []
}>()
</script>

<template>
  <div v-loading="loading" class="note-results-column">
    <div class="note-results-column__result-bar">
      <span>{{ scopeTitle }}</span>
      <strong>{{ pagination.total }} 条笔记</strong>
    </div>

    <QueryRewriteTip v-if="queryRewrite" :query-rewrite="queryRewrite" />

    <NoteCard
      v-for="note in notes"
      :key="note.id"
      :note="note"
      :active="note.id === activeNoteId"
      :keyword="keyword"
    />

    <AppEmpty
      v-if="!loading && notes.length === 0"
      title="没有找到匹配的笔记"
      description="试试搜索章节名、观点关键词或主题标签。"
    >
      <MascotBubble
        class="note-results-column__empty-mascot"
        :mood="emptyMascotCue.mood"
        :message="emptyMascotCue.message"
        compact
      />
    </AppEmpty>

    <div v-else-if="pagination.has_more" class="note-results-column__load-more">
      <el-button round :loading="loading" @click="$emit('loadMore')">加载更多</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.note-results-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.note-results-column__result-bar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.76);
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.note-results-column__result-bar strong {
  color: var(--text-primary);
}

.note-results-column__load-more {
  display: flex;
  justify-content: center;
  padding: 8px 0 4px;
}

.note-results-column__empty-mascot {
  max-width: 460px;
  margin: 18px auto 0;
  text-align: left;
}

@media (max-width: 768px) {
  .note-results-column__result-bar {
    align-items: flex-start;
    border-radius: 18px;
    flex-direction: column;
  }
}
</style>
