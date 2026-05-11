<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import type { DashboardActionItem } from '@/types/dashboard'

defineProps<{
  items: DashboardActionItem[]
}>()

defineEmits<{
  navigate: [path: string]
}>()
</script>

<template>
  <section class="dashboard-action-queue">
    <AppCard
      v-for="item in items"
      :key="item.label"
      class="dashboard-action-queue__card"
      :class="`is-${item.accent}`"
      @click="$emit('navigate', item.path)"
    >
      <span>{{ item.label }}</span>
      <strong>{{ item.title }}</strong>
      <p>{{ item.hint }}</p>
    </AppCard>
  </section>
</template>

<style scoped lang="scss">
.dashboard-action-queue {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.dashboard-action-queue__card {
  position: relative;
  overflow: hidden;
  padding: 20px;
  cursor: pointer;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease;
}

.dashboard-action-queue__card::after {
  content: '';
  position: absolute;
  right: -36px;
  bottom: -42px;
  width: 112px;
  height: 112px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
}

.dashboard-action-queue__card.is-warm::after {
  background: rgba(192, 139, 92, 0.14);
}

.dashboard-action-queue__card.is-calm::after {
  background: rgba(77, 116, 146, 0.12);
}

.dashboard-action-queue__card:hover {
  border-color: rgba(47, 93, 80, 0.2);
  transform: translateY(-2px);
}

.dashboard-action-queue__card span {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.dashboard-action-queue__card strong {
  display: block;
  margin-top: 10px;
  font-size: 1.25rem;
}

.dashboard-action-queue__card p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

@media (max-width: 1100px) {
  .dashboard-action-queue {
    grid-template-columns: 1fr;
  }
}
</style>
