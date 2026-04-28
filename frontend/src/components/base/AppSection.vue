<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <div class="app-section">
    <div class="app-section__header">
      <div>
        <h3>{{ title }}</h3>
        <p v-if="description">{{ description }}</p>
      </div>
      <slot name="action" />
    </div>
    <slot />
  </div>
</template>

<style scoped lang="scss">
.app-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.app-section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.app-section__header h3 {
  margin: 0;
  font-size: 1.05rem;
}

.app-section__header p {
  margin: 4px 0 0;
  color: var(--text-tertiary);
  font-size: 0.9rem;
}
</style>
