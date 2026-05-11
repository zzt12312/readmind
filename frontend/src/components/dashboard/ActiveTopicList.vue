<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'

defineProps<{
  topics: string[]
}>()
</script>

<template>
  <AppCard>
    <h3>活跃主题</h3>
    <div class="active-topic-list">
      <span v-for="topic in topics" :key="topic">{{ topic }}</span>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.active-topic-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.active-topic-list span {
  padding: 10px 12px;
  border-radius: 999px;
  background: var(--bg-soft);
  color: var(--text-secondary);
}
</style>
