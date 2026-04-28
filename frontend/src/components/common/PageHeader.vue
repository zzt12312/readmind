<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <section class="page-header">
    <div>
      <h2>{{ title }}</h2>
      <p v-if="description">{{ description }}</p>
    </div>
    <slot />
  </section>
</template>

<style scoped lang="scss">
.page-header {
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 1.55rem;
}

.page-header p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}
</style>
