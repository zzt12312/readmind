<script setup lang="ts">
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import type { MascotCue } from '@/constants/mascotMessages'

defineProps<{
  mascotCue: MascotCue
  scopeLabel: string
  scopeValue: string
}>()
</script>

<template>
  <AppCard class="qa-hero">
    <div>
      <p class="qa-hero__eyebrow">Ask Your Reading Memory</p>
      <h2>让签签陪你追问自己的读书笔记。</h2>
      <p>
        选择全库或单本书范围，签签会先检索相关摘录，再带着引用来源整理回答。每一次追问都能回到原始笔记。
      </p>
      <MascotBubble
        class="qa-hero__mascot"
        :mood="mascotCue.mood"
        :message="mascotCue.message"
        :celebrating="mascotCue.celebrating"
        compact
      />
    </div>
    <div class="qa-hero__meta">
      <span>{{ scopeLabel }}</span>
      <strong>{{ scopeValue }}</strong>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.qa-hero {
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  padding: 28px;
  background:
    radial-gradient(circle at 88% 14%, rgba(47, 93, 80, 0.2), transparent 28%),
    linear-gradient(135deg, rgba(192, 139, 92, 0.13), rgba(255, 253, 249, 0.96) 62%),
    var(--bg-card);
}

.qa-hero__eyebrow {
  margin: 0 0 10px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.qa-hero h2 {
  max-width: 50rem;
  margin: 0 0 10px;
  font-size: clamp(1.6rem, 2.4vw, 2.4rem);
  letter-spacing: -0.04em;
}

.qa-hero p:last-child {
  max-width: 48rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.qa-hero__mascot {
  max-width: 560px;
  margin-top: 16px;
}

.qa-hero__meta {
  min-width: 180px;
  padding: 16px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.76);
  box-shadow: var(--shadow-sm);
}

.qa-hero__meta span {
  display: block;
  margin-bottom: 8px;
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.qa-hero__meta strong {
  color: var(--brand-primary);
  line-height: 1.45;
}

@media (max-width: 768px) {
  .qa-hero {
    align-items: flex-start;
    flex-direction: column;
    padding: 22px;
  }

  .qa-hero__meta {
    width: 100%;
  }
}
</style>
