<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import type { NoteItem } from '@/types/note'
import { highlightText } from '@/utils/text'

const props = defineProps<{
  note: NoteItem
  active: boolean
  keyword: string
}>()

function renderHighlight(text: string) {
  return highlightText(text, props.keyword)
}
</script>

<template>
  <AppCard
    class="note-card"
    :class="{ 'is-active-note': active }"
    :data-note-id="note.id"
  >
    <header class="note-card__header">
      <div>
        <p class="note-card__chapter">{{ note.chapter || '未分章节' }}</p>
        <strong class="note-card__book-title">{{ note.book_title }}</strong>
      </div>
      <span class="note-card__marker">摘录</span>
    </header>

    <blockquote>
      <span class="note-card__quote-mark">“</span>
      <p v-html="renderHighlight(note.excerpt)" />
    </blockquote>

    <section v-if="note.comment" class="note-card__comment">
      <span>我的想法</span>
      <p v-html="renderHighlight(note.comment)" />
    </section>
    <div class="note-card__tag-list">
      <el-tag v-for="tag in note.tags" :key="tag" round effect="plain">{{ tag }}</el-tag>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.note-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px 24px;
  border-color: rgba(216, 207, 191, 0.82);
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.05), transparent 28%),
    rgba(255, 253, 249, 0.96);
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.note-card::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: linear-gradient(180deg, var(--brand-primary), var(--brand-accent));
  opacity: 0.62;
}

.note-card:hover {
  transform: translateY(-2px);
  border-color: rgba(47, 93, 80, 0.28);
  box-shadow: var(--shadow-md);
}

.note-card.is-active-note {
  border-color: rgba(47, 93, 80, 0.45);
  box-shadow:
    0 0 0 2px rgba(47, 93, 80, 0.12),
    var(--shadow-md);
}

.note-card__header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.note-card__chapter {
  margin: 0 0 6px;
  color: var(--text-tertiary);
  font-size: 0.82rem;
  letter-spacing: 0.02em;
}

.note-card__book-title {
  color: var(--brand-primary);
  font-size: 0.96rem;
}

.note-card__marker {
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(192, 139, 92, 0.12);
  color: var(--brand-accent);
  font-size: 0.78rem;
  font-weight: 700;
}

.note-card blockquote {
  position: relative;
  margin: 0;
  padding: 18px 18px 18px 44px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 18px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(251, 248, 242, 0.82)),
    var(--bg-panel);
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.85;
}

.note-card blockquote p {
  margin: 0;
}

.note-card__quote-mark {
  position: absolute;
  left: 16px;
  top: 8px;
  color: rgba(192, 139, 92, 0.42);
  font-family: Georgia, serif;
  font-size: 3.2rem;
  line-height: 1;
}

.note-card__comment {
  margin: 0;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(47, 93, 80, 0.07);
  color: var(--text-secondary);
  line-height: 1.8;
}

.note-card__comment span {
  display: block;
  margin-bottom: 6px;
  color: var(--brand-primary);
  font-size: 0.8rem;
  font-weight: 700;
}

.note-card__comment p {
  margin: 0;
}

.note-card__tag-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

:deep(mark) {
  padding: 0 2px;
  border-radius: 4px;
  background: rgba(192, 139, 92, 0.22);
}
</style>
