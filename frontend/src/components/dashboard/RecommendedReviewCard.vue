<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import BookCover from '@/components/common/BookCover.vue'
import type { DashboardRecommendedReview } from '@/types/dashboard'

defineProps<{
  review: DashboardRecommendedReview
}>()

defineEmits<{
  navigate: [path: string]
}>()
</script>

<template>
  <AppCard class="recommended-review">
    <div class="recommended-review__copy">
      <p class="recommended-review__eyebrow">Worth revisiting</p>
      <h3>值得回看：{{ review.title || '最近笔记' }}</h3>
      <p>{{ review.reason }}</p>
      <div class="recommended-review__tags">
        <span v-for="topic in review.topics" :key="topic">{{ topic }}</span>
      </div>
      <button type="button" @click="$emit('navigate', review.path)">
        {{ review.book ? '打开这本书' : '进入笔记工作台' }}
      </button>
    </div>
    <div
      v-if="review.book"
      class="recommended-review__book"
      role="button"
      tabindex="0"
      @click="$emit('navigate', review.path)"
      @keydown.enter.prevent="$emit('navigate', review.path)"
      @keydown.space.prevent="$emit('navigate', review.path)"
    >
      <BookCover
        :src="review.book.cover"
        :title="review.book.title"
      />
      <div>
        <strong>{{ review.book.title }}</strong>
        <span>{{ review.book.author || '未知作者' }}</span>
        <em>{{ review.book.notes }} 条笔记</em>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.recommended-review {
  padding: 24px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 22px;
  align-items: center;
  background:
    radial-gradient(circle at 0% 20%, rgba(47, 93, 80, 0.12), transparent 34%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(238, 228, 211, 0.52));
}

.recommended-review__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.recommended-review h3 {
  margin: 0 0 10px;
  font-size: 1.55rem;
}

.recommended-review__copy > p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.recommended-review__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.recommended-review__tags span {
  padding: 9px 12px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.72);
  color: var(--brand-primary);
  font-size: 0.84rem;
  font-weight: 800;
}

.recommended-review__copy button {
  margin-top: 18px;
  padding: 11px 16px;
  border: 0;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

.recommended-review__book {
  padding: 14px;
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.7);
  cursor: pointer;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease,
    transform 0.16s ease;
}

.recommended-review__book:hover,
.recommended-review__book:focus-visible {
  border-color: rgba(47, 93, 80, 0.28);
  box-shadow: 0 16px 28px rgba(47, 93, 80, 0.1);
  outline: 0;
  transform: translateY(-2px);
}

.recommended-review__book :deep(.book-cover) {
  width: 92px;
  height: 124px;
}

.recommended-review__book strong,
.recommended-review__book span,
.recommended-review__book em {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recommended-review__book strong {
  white-space: nowrap;
}

.recommended-review__book span,
.recommended-review__book em {
  margin-top: 8px;
  color: var(--text-tertiary);
  font-size: 0.88rem;
  font-style: normal;
}

@media (max-width: 1100px) {
  .recommended-review {
    grid-template-columns: 1fr;
  }
}
</style>
