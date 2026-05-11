<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import type { MascotCue } from '@/constants/mascotMessages'
import type { DashboardActionItem, DashboardActivationReport, DashboardDailyBrief } from '@/types/dashboard'

defineProps<{
  dailyBrief: DashboardDailyBrief
  activationReport: DashboardActivationReport
  actionQueue: DashboardActionItem[]
  modeLabel: string
  modeDetail: string
  mascotCue: MascotCue
}>()

defineEmits<{
  navigate: [path: string]
}>()
</script>

<template>
  <AppCard class="dashboard-hero">
    <div class="dashboard-hero__copy">
      <p class="dashboard-hero__eyebrow">Today in your reading workspace</p>
      <h2>{{ dailyBrief.title }}</h2>
      <p>{{ dailyBrief.summary }}</p>
      <div class="dashboard-hero__tags">
        <span v-for="topic in dailyBrief.highlights.topics" :key="topic">{{ topic }}</span>
        <span v-if="dailyBrief.highlights.author">常读作者：{{ dailyBrief.highlights.author }}</span>
      </div>
      <div class="dashboard-hero__actions-main">
        <button type="button" @click="$emit('navigate', activationReport.primary_action.path)">
          {{ activationReport.primary_action.label }}
        </button>
        <button type="button" @click="$emit('navigate', activationReport.secondary_action.path)">
          {{ activationReport.secondary_action.label }}
        </button>
      </div>
      <MascotBubble
        class="dashboard-hero__mascot"
        :mood="mascotCue.mood"
        :message="mascotCue.message"
        :celebrating="mascotCue.celebrating"
        compact
        action-text="开始今日行动"
        @action="$emit('navigate', actionQueue[0]?.path || '/review')"
      />
    </div>

    <div class="dashboard-hero__brief-panel">
      <div class="dashboard-hero__mode-card">
        <span>当前模式</span>
        <strong>{{ modeLabel }}</strong>
        <p>{{ modeDetail }}</p>
      </div>
      <div class="dashboard-hero__brief-stats">
        <article v-for="item in dailyBrief.feedback_items" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.hint }}</p>
        </article>
      </div>
      <div class="dashboard-hero__brief-actions">
        <button
          v-for="action in dailyBrief.suggested_actions"
          :key="`${action.type}-${action.path}`"
          type="button"
          @click="$emit('navigate', action.path)"
        >
          {{ action.label }}
        </button>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.dashboard-hero {
  padding: 28px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 0.72fr);
  align-items: stretch;
  gap: 24px;
  background:
    radial-gradient(circle at 8% 8%, rgba(47, 93, 80, 0.14), transparent 34%),
    radial-gradient(circle at 92% 16%, rgba(192, 139, 92, 0.18), transparent 30%),
    linear-gradient(120deg, rgba(47, 93, 80, 0.08), rgba(192, 139, 92, 0.12)),
    rgba(255, 253, 249, 0.94);
}

.dashboard-hero__copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.dashboard-hero__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dashboard-hero h2 {
  max-width: 52rem;
  margin: 0 0 10px;
  font-size: clamp(2rem, 3vw, 3.1rem);
  line-height: 1.1;
}

.dashboard-hero__copy > p {
  max-width: 48rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.dashboard-hero__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.dashboard-hero__tags span {
  padding: 9px 12px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.72);
  color: var(--brand-primary);
  font-size: 0.84rem;
  font-weight: 800;
}

.dashboard-hero__actions-main {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.dashboard-hero__actions-main button {
  padding: 12px 16px;
  border: 1px solid rgba(47, 93, 80, 0.2);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.84);
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 900;
}

.dashboard-hero__actions-main button:first-child {
  border-color: var(--brand-primary);
  background: var(--brand-primary);
  color: #fff;
}

.dashboard-hero__mascot {
  max-width: 560px;
  margin-top: 18px;
}

.dashboard-hero__brief-panel {
  padding: 16px;
  display: grid;
  gap: 14px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 26px;
  background: rgba(255, 253, 249, 0.72);
  box-shadow: 0 18px 42px rgba(47, 93, 80, 0.1);
}

.dashboard-hero__mode-card {
  padding: 14px;
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: 20px;
  background: rgba(47, 93, 80, 0.07);
}

.dashboard-hero__mode-card span {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 900;
}

.dashboard-hero__mode-card strong {
  display: block;
  margin-top: 6px;
  color: var(--brand-primary);
  font-size: 1.12rem;
}

.dashboard-hero__mode-card p {
  margin: 7px 0 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.dashboard-hero__brief-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.dashboard-hero__brief-stats article {
  min-width: 0;
  padding: 13px;
  border: 1px solid rgba(216, 207, 191, 0.56);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.68);
}

.dashboard-hero__brief-stats span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 800;
}

.dashboard-hero__brief-stats strong {
  display: block;
  overflow: hidden;
  margin-top: 5px;
  color: var(--brand-primary);
  font-size: 1.28rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-hero__brief-stats p {
  display: -webkit-box;
  overflow: hidden;
  min-height: 2.8em;
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.4;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.dashboard-hero__brief-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.dashboard-hero__brief-actions button {
  padding: 10px 14px;
  border: 1px solid rgba(47, 93, 80, 0.16);
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 900;
  transition:
    background 0.16s ease,
    color 0.16s ease,
    transform 0.16s ease;
}

.dashboard-hero__brief-actions button:first-child {
  background: var(--brand-primary);
  color: #fff;
}

.dashboard-hero__brief-actions button:hover {
  transform: translateY(-1px);
}

@media (max-width: 1100px) {
  .dashboard-hero {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-hero__brief-stats {
    grid-template-columns: 1fr;
  }
}
</style>
