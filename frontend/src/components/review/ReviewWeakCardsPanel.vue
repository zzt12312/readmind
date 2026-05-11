<script setup lang="ts">
import type { ReviewCard } from '@/types/review'

defineProps<{
  cards: ReviewCard[]
}>()

const emit = defineEmits<{
  reviewWeak: []
}>()
</script>

<template>
  <AppCard v-if="cards.length" class="review-weak">
    <div class="review-weak__header">
      <div>
        <p class="review-weak__eyebrow">待巩固</p>
        <h3>建议近期优先回看</h3>
      </div>
      <el-button round @click="emit('reviewWeak')">只复习待巩固</el-button>
    </div>
    <div class="review-weak__list">
      <article v-for="item in cards" :key="item.note_id">
        <strong>{{ item.source }}</strong>
        <p>{{ item.answer }}</p>
      </article>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.review-weak {
  padding: 22px;
}

.review-weak__header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}

.review-weak__header h3 {
  margin: 0;
}

.review-weak__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
}

.review-weak__list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.review-weak__list article {
  padding: 14px;
  border: 1px solid rgba(216, 207, 191, 0.65);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.72);
}

.review-weak__list strong {
  display: block;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.review-weak__list p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--text-secondary);
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

@media (max-width: 768px) {
  .review-weak__header {
    align-items: flex-start;
    flex-direction: column;
  }

  .review-weak__list {
    grid-template-columns: 1fr;
  }
}
</style>
