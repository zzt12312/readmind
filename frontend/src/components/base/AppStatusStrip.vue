<script setup lang="ts">
defineProps<{
  items: Array<{
    label: string
    value: string
  }>
}>()
</script>

<template>
  <div class="app-status-strip">
    <div v-for="item in items" :key="item.label" class="app-status-strip__item">
      <span>{{ item.label }}</span>
      <strong>{{ item.value }}</strong>
    </div>
  </div>
</template>

<style scoped lang="scss">
.app-status-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  width: 100%;
  min-width: 0;
  border: 1px solid rgba(216, 207, 191, 0.54);
  border-radius: 14px;
  background: rgba(255, 253, 249, 0.68);
}

.app-status-strip__item {
  min-width: 0;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.app-status-strip__item + .app-status-strip__item {
  border-left: 1px solid rgba(216, 207, 191, 0.54);
}

.app-status-strip__item span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 800;
}

.app-status-strip__item strong {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

@media (max-width: 768px) {
  .app-status-strip {
    grid-template-columns: 1fr;
  }

  .app-status-strip__item + .app-status-strip__item {
    border-top: 1px solid rgba(216, 207, 191, 0.54);
    border-left: 0;
  }
}
</style>
