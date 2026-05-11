<script setup lang="ts">
import type { ReviewSummaryItem } from '@/types/review'

defineProps<{
  loading: boolean
  summary: ReviewSummaryItem[]
}>()
</script>

<template>
  <section v-loading="loading" class="review-summary">
    <AppCard v-for="item in summary" :key="item.label" class="review-summary__card">
      <p>{{ item.label }}</p>
      <strong>{{ item.value }}</strong>
    </AppCard>
  </section>
</template>

<style scoped lang="scss">
.review-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.review-summary__card p {
  margin: 0;
  color: var(--text-tertiary);
}

.review-summary__card strong {
  display: inline-block;
  margin-top: 12px;
  font-size: 1.8rem;
}

@media (max-width: 768px) {
  .review-summary {
    grid-template-columns: 1fr;
  }
}
</style>
