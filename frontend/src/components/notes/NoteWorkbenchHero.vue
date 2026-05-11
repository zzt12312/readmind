<script setup lang="ts">
defineProps<{
  title: string
  description: string
  total: number
}>()
</script>

<template>
  <AppCard class="note-workbench-hero">
    <div>
      <p class="note-workbench-hero__eyebrow">Reading Notes Studio</p>
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
    </div>
    <div class="note-workbench-hero__stats">
      <span>当前结果</span>
      <strong>{{ total }}</strong>
      <em>条笔记</em>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.note-workbench-hero {
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  padding: 28px;
  background:
    radial-gradient(circle at 92% 16%, rgba(192, 139, 92, 0.22), transparent 30%),
    linear-gradient(135deg, rgba(47, 93, 80, 0.12), rgba(255, 253, 249, 0.96) 58%),
    var(--bg-card);
}

.note-workbench-hero::after {
  content: '';
  position: absolute;
  right: -52px;
  bottom: -68px;
  width: 220px;
  height: 220px;
  border: 1px solid rgba(47, 93, 80, 0.1);
  border-radius: 50%;
  background: rgba(255, 253, 249, 0.34);
}

.note-workbench-hero > * {
  position: relative;
  z-index: 1;
}

.note-workbench-hero__eyebrow {
  margin: 0 0 10px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.note-workbench-hero h2 {
  max-width: 48rem;
  margin: 0 0 10px;
  font-size: clamp(1.5rem, 2vw, 2.1rem);
}

.note-workbench-hero p:last-child {
  max-width: 46rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.note-workbench-hero__stats {
  min-width: 132px;
  padding: 16px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.74);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.note-workbench-hero__stats span,
.note-workbench-hero__stats em {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.82rem;
  font-style: normal;
}

.note-workbench-hero__stats strong {
  display: block;
  margin: 4px 0;
  color: var(--brand-primary);
  font-size: 2rem;
  line-height: 1;
}

@media (max-width: 768px) {
  .note-workbench-hero {
    align-items: flex-start;
    flex-direction: column;
    padding: 22px;
  }

  .note-workbench-hero__stats {
    width: 100%;
    text-align: left;
  }
}
</style>
