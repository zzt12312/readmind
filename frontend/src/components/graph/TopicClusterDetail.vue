<script setup lang="ts">
import type { TopicCluster } from '@/types/insights'

defineProps<{
  cluster: TopicCluster
}>()

const emit = defineEmits<{
  openAction: [path: string]
  jumpToBook: [bookId: number]
  jumpToNote: [bookId: number, noteId: number]
}>()
</script>

<template>
  <AppCard>
    <AppSection
      :title="`主题簇：${cluster.name}`"
      description="这里展示这个主题簇最常一起出现的书和代表性摘录，方便你继续追溯原始上下文。"
    />
    <div v-if="cluster.actions?.length" class="topic-cluster-detail__actions">
      <article
        v-for="action in cluster.actions"
        :key="`${cluster.id}-${action.type}`"
        :class="`is-${action.type}`"
      >
        <strong>{{ action.label }}</strong>
        <p>{{ action.description }}</p>
        <button type="button" @click="emit('openAction', action.path)">开始</button>
      </article>
    </div>
    <div class="topic-cluster-detail__grid">
      <div class="topic-cluster-detail__books">
        <h4>相关书籍</h4>
        <div class="topic-cluster-detail__book-list">
          <button
            v-for="book in cluster.sample_books"
            :key="book.id"
            type="button"
            class="topic-cluster-detail__book-chip"
            @click="emit('jumpToBook', book.id)"
          >
            <img v-if="book.cover" :src="book.cover" :alt="book.title" loading="lazy" />
            <span v-else>{{ book.title.slice(0, 2) }}</span>
            <strong>{{ book.title }}</strong>
          </button>
        </div>
      </div>

      <div class="topic-cluster-detail__samples">
        <h4>代表性摘录</h4>
        <article
          v-for="sample in cluster.sample_excerpts"
          :key="sample.note_id"
          class="topic-cluster-detail__sample-card"
        >
          <strong>{{ sample.book_title }}</strong>
          <p>{{ sample.excerpt }}</p>
          <el-button text @click="emit('jumpToNote', sample.book_id, sample.note_id)">跳转原笔记</el-button>
        </article>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.topic-cluster-detail__grid {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 16px;
}

.topic-cluster-detail__actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.topic-cluster-detail__actions article {
  min-width: 0;
  padding: 15px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 18px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.9), rgba(248, 242, 232, 0.68)),
    var(--bg-card);
}

.topic-cluster-detail__actions article.is-qa {
  border-color: rgba(47, 93, 80, 0.18);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.82)),
    var(--bg-card);
}

.topic-cluster-detail__actions strong {
  display: block;
  color: var(--brand-primary);
}

.topic-cluster-detail__actions p {
  min-height: 3.2em;
  margin: 7px 0 12px;
  color: var(--text-secondary);
  font-size: 0.86rem;
  line-height: 1.6;
}

.topic-cluster-detail__actions button {
  padding: 9px 13px;
  border: 0;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

.topic-cluster-detail__books h4,
.topic-cluster-detail__samples h4 {
  margin: 0 0 12px;
}

.topic-cluster-detail__book-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.topic-cluster-detail__book-chip {
  padding: 12px;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.92);
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
  cursor: pointer;
}

.topic-cluster-detail__book-chip img,
.topic-cluster-detail__book-chip span {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 12px;
  object-fit: cover;
  background: linear-gradient(135deg, rgba(47, 93, 80, 0.18), rgba(192, 139, 92, 0.24));
  display: grid;
  place-items: center;
  color: var(--brand-primary);
  font-weight: 700;
}

.topic-cluster-detail__sample-card {
  padding: 16px;
  border-radius: 16px;
  background: rgba(251, 248, 242, 0.78);
}

.topic-cluster-detail__sample-card + .topic-cluster-detail__sample-card {
  margin-top: 12px;
}

.topic-cluster-detail__sample-card p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

@media (max-width: 1180px) {
  .topic-cluster-detail__grid,
  .topic-cluster-detail__actions {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .topic-cluster-detail__book-list {
    grid-template-columns: 1fr;
  }
}
</style>
