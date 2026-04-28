<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>

<template>
  <div class="app-empty">
    <div class="app-empty__icon">RM</div>
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <slot />
  </div>
</template>

<style scoped lang="scss">
.app-empty {
  padding: 36px 20px;
  text-align: center;
  border: 1px dashed var(--border-medium);
  border-radius: var(--radius-md);
  background: rgba(251, 248, 242, 0.72);
}

.app-empty__icon {
  width: 52px;
  height: 52px;
  margin: 0 auto 14px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: var(--brand-primary-light);
  color: var(--brand-primary);
  font-weight: 700;
}

.app-empty h3 {
  margin: 0 0 8px;
}

.app-empty p {
  margin: 0;
  color: var(--text-secondary);
}
</style>
