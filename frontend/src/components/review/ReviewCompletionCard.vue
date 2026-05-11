<script setup lang="ts">
interface CompletionStat {
  label: string
  value: string
}

defineProps<{
  stats: CompletionStat[]
}>()

const emit = defineEmits<{
  restart: []
  weak: []
  ask: []
}>()
</script>

<template>
  <AppCard class="review-completion">
    <div>
      <p class="review-completion__eyebrow">本轮复习完成</p>
      <h2>今天这组卡片已经收尾了</h2>
      <p>可以重新练习当前这组卡片，也可以切换到待巩固队列继续回看。</p>
    </div>
    <div class="review-completion__side">
      <div class="review-completion__stats">
        <span v-for="item in stats" :key="item.label">
          <strong>{{ item.value }}</strong>
          {{ item.label }}
        </span>
      </div>
      <div class="review-completion__actions">
        <el-button type="primary" round @click="emit('restart')">再练一遍</el-button>
        <el-button round @click="emit('weak')">练待巩固</el-button>
        <el-button round @click="emit('ask')">带着薄弱点去追问</el-button>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.review-completion {
  display: flex;
  justify-content: space-between;
  gap: 22px;
  align-items: center;
  padding: 24px;
  border: 1px solid rgba(47, 93, 80, 0.16);
  background:
    radial-gradient(circle at 12% 18%, rgba(47, 93, 80, 0.13), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(238, 228, 211, 0.58));
}

.review-completion h2 {
  margin: 0 0 8px;
}

.review-completion p:last-child {
  margin: 0;
  color: var(--text-secondary);
}

.review-completion__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
}

.review-completion__side {
  display: grid;
  gap: 12px;
  min-width: 300px;
}

.review-completion__stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(82px, 1fr));
  gap: 10px;
}

.review-completion__stats span {
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.7);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.78);
  color: var(--text-tertiary);
  text-align: center;
}

.review-completion__stats strong {
  display: block;
  margin-bottom: 4px;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.review-completion__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .review-completion {
    align-items: flex-start;
    flex-direction: column;
  }

  .review-completion__stats,
  .review-completion__side {
    grid-template-columns: 1fr;
    min-width: 0;
    width: 100%;
  }

  .review-completion__actions {
    justify-content: flex-start;
  }
}
</style>
