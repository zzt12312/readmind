<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  hint: string
}>()
</script>

<template>
  <AppCard class="metric-card">
    <p class="metric-card__label">{{ label }}</p>
    <strong class="metric-card__value">{{ value }}</strong>
    <span class="metric-card__hint">{{ hint }}</span>
  </AppCard>
</template>

<script lang="ts">
import AppCard from './AppCard.vue'

export default {
  components: {
    AppCard,
  },
}
</script>

<style scoped lang="scss">
.metric-card {
  min-height: 132px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.metric-card__label {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.88rem;
}

.metric-card__value {
  font-size: 2rem;
  color: var(--text-primary);
}

.metric-card__hint {
  color: var(--brand-primary);
  font-size: 0.88rem;
}
</style>
