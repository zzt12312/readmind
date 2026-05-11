<script setup lang="ts">
import type { AnalyticsRecommendation } from '@/types/analytics'

defineProps<{
  recommendations: AnalyticsRecommendation[]
}>()

const emit = defineEmits<{
  open: [path: string]
}>()
</script>

<template>
  <AppCard v-if="recommendations.length" class="analytics-recommendations">
    <div class="analytics-recommendations__head">
      <div>
        <p class="analytics-recommendations__eyebrow">Next best actions</p>
        <h3>看板给你的下一步建议</h3>
      </div>
      <span>基于高价值书籍、主题密度和复习压力生成</span>
    </div>
    <div class="analytics-recommendations__list">
      <article
        v-for="item in recommendations"
        :key="`${item.type}-${item.title}`"
        :class="`is-${item.priority}`"
      >
        <span>{{ item.priority === 'high' ? '优先' : item.priority === 'medium' ? '建议' : '观察' }}</span>
        <strong>{{ item.title }}</strong>
        <p>{{ item.reason }}</p>
        <button type="button" @click="emit('open', item.path)">
          {{ item.action_label }}
        </button>
      </article>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.analytics-recommendations {
  padding: 22px;
  background:
    radial-gradient(circle at 8% 0%, rgba(47, 93, 80, 0.12), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(244, 238, 228, 0.74));
}

.analytics-recommendations__head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.analytics-recommendations__head h3 {
  margin: 0;
}

.analytics-recommendations__head > span {
  color: var(--text-tertiary);
  font-size: 0.88rem;
  line-height: 1.6;
}

.analytics-recommendations__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.analytics-recommendations__list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.analytics-recommendations__list article {
  min-width: 0;
  padding: 16px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.76);
}

.analytics-recommendations__list article.is-high {
  border-color: rgba(47, 93, 80, 0.22);
  background:
    linear-gradient(180deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.82)),
    var(--bg-card);
}

.analytics-recommendations__list span {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  font-size: 0.76rem;
  font-weight: 900;
}

.analytics-recommendations__list strong {
  display: block;
  margin-top: 10px;
  line-height: 1.45;
}

.analytics-recommendations__list p {
  margin: 8px 0 14px;
  color: var(--text-secondary);
  font-size: 0.86rem;
  line-height: 1.6;
}

.analytics-recommendations__list button {
  padding: 9px 12px;
  border: 0;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

@media (max-width: 1180px) {
  .analytics-recommendations__list {
    grid-template-columns: 1fr;
  }
}
</style>
