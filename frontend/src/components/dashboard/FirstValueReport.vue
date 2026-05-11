<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import type { DashboardActivationReport } from '@/types/dashboard'

defineProps<{
  report: DashboardActivationReport
}>()

defineEmits<{
  askQuestion: [question: string]
}>()
</script>

<template>
  <AppCard class="first-value-report">
    <div class="first-value-report__copy">
      <p class="first-value-report__eyebrow">First Value Report</p>
      <h3>{{ report.title }}</h3>
      <p>{{ report.summary }}</p>
      <div class="first-value-report__topics">
        <span v-for="topic in report.top_topics" :key="topic">{{ topic }}</span>
      </div>
    </div>
    <div class="first-value-report__side">
      <div class="first-value-report__cards">
        <article v-for="card in report.asset_cards" :key="card.label">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <p>{{ card.hint }}</p>
        </article>
      </div>
      <div class="first-value-report__question-list">
        <strong>可以立刻追问</strong>
        <button
          v-for="question in report.recommended_questions"
          :key="question"
          type="button"
          @click="$emit('askQuestion', question)"
        >
          {{ question }}
        </button>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.first-value-report {
  display: grid;
  grid-template-columns: minmax(0, 0.86fr) minmax(420px, 1fr);
  gap: 22px;
  align-items: stretch;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(244, 239, 230, 0.76)),
    var(--bg-card);
}

.first-value-report__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.first-value-report__copy h3 {
  margin: 0 0 10px;
  font-size: 1.55rem;
}

.first-value-report__copy p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.first-value-report__topics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.first-value-report__topics span {
  padding: 8px 11px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  font-size: 0.84rem;
  font-weight: 800;
}

.first-value-report__side {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: 14px;
}

.first-value-report__cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.first-value-report__cards article {
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.74);
}

.first-value-report__cards span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 900;
}

.first-value-report__cards strong {
  display: block;
  margin-top: 7px;
  color: var(--text-primary);
  font-size: 1.45rem;
}

.first-value-report__cards p {
  margin: 5px 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.45;
}

.first-value-report__question-list {
  padding: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 20px;
  background: rgba(47, 93, 80, 0.06);
}

.first-value-report__question-list strong {
  display: block;
  margin-bottom: 10px;
  color: var(--brand-primary);
}

.first-value-report__question-list button {
  display: block;
  width: 100%;
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 14px;
  background: rgba(255, 253, 249, 0.82);
  color: var(--text-primary);
  cursor: pointer;
  line-height: 1.55;
  text-align: left;
}

@media (max-width: 1100px) {
  .first-value-report,
  .first-value-report__side {
    grid-template-columns: 1fr;
  }
}
</style>
