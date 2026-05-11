<script setup lang="ts">
defineProps<{
  reviewCoverage: number
}>()
</script>

<template>
  <AppCard class="analytics-hero">
    <div>
      <p class="analytics-hero__eyebrow">Reading analytics</p>
      <h2>把阅读偏好、阅读时长和复习进展放到一张工作台里。</h2>
      <p>
        看板会优先使用微信读书导出的 readingTime 字段生成阅读时长榜，
        并结合笔记、主题与复习记录观察你的长期阅读偏好。
      </p>
    </div>
    <div class="analytics-hero__coverage">
      <strong>{{ reviewCoverage }}%</strong>
      <span>复习覆盖率</span>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.analytics-hero {
  padding: 28px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  background:
    radial-gradient(circle at 8% 12%, rgba(47, 93, 80, 0.14), transparent 32%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(238, 228, 211, 0.58));
}

.analytics-hero h2 {
  max-width: 56rem;
  margin: 0 0 10px;
}

.analytics-hero p:last-child {
  max-width: 52rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.analytics-hero__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.analytics-hero__coverage {
  min-width: 136px;
  padding: 18px;
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: 24px;
  background: rgba(255, 253, 249, 0.78);
  text-align: center;
}

.analytics-hero__coverage strong {
  display: block;
  color: var(--brand-primary);
  font-size: 2.2rem;
}

.analytics-hero__coverage span {
  color: var(--text-tertiary);
}

@media (max-width: 768px) {
  .analytics-hero {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
