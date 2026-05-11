<script setup lang="ts">
import type { ActivityHeatmapItem } from '@/types/analytics'

defineProps<{
  activityHeatmap: ActivityHeatmapItem[]
  activeDays: number
  totalActivity: number
}>()
</script>

<template>
  <AppCard class="activity-heatmap analytics-panel">
    <div class="analytics-panel__head">
      <div>
        <p class="analytics-panel__eyebrow">Activity heatmap</p>
        <h3>知识投入热力图</h3>
      </div>
      <span>每个方块代表 1 天，颜色越深表示当天摘录/复习越多</span>
    </div>
    <div class="activity-heatmap__summary">
      <article>
        <strong>{{ activeDays }}</strong>
        <span>活跃天数</span>
      </article>
      <article>
        <strong>{{ totalActivity }}</strong>
        <span>总活动次数</span>
      </article>
      <p>用于观察最近 35 天是否保持稳定输入，而不是单纯追求某一天的峰值。</p>
    </div>
    <div class="activity-heatmap__board">
      <div class="activity-heatmap__weekdays" aria-hidden="true">
        <span>周一</span>
        <span>周三</span>
        <span>周五</span>
      </div>
      <div>
        <div class="activity-heatmap__grid">
          <span
            v-for="day in activityHeatmap"
            :key="day.date"
            :class="`is-level-${day.level}`"
            :title="`${day.date}: ${day.count} 次摘录/复习`"
          />
        </div>
        <div class="activity-heatmap__caption">
          <span>35 天前</span>
          <div class="activity-heatmap__legend" aria-label="热力图颜色图例">
            <span>少</span>
            <i class="is-level-0" />
            <i class="is-level-1" />
            <i class="is-level-2" />
            <i class="is-level-3" />
            <i class="is-level-4" />
            <span>多</span>
          </div>
          <span>今天</span>
        </div>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.analytics-panel {
  padding: 22px;
}

.analytics-panel__head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.analytics-panel__head h3 {
  margin: 0;
}

.analytics-panel__head > span {
  color: var(--text-tertiary);
  font-size: 0.88rem;
}

.analytics-panel__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.activity-heatmap__summary {
  display: grid;
  grid-template-columns: 104px 104px minmax(0, 1fr);
  gap: 10px;
  align-items: stretch;
  margin-bottom: 14px;
}

.activity-heatmap__summary article,
.activity-heatmap__summary p {
  margin: 0;
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.58);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.68);
}

.activity-heatmap__summary strong {
  display: block;
  color: var(--brand-primary);
  font-size: 1.35rem;
}

.activity-heatmap__summary span,
.activity-heatmap__summary p {
  color: var(--text-tertiary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.activity-heatmap__board {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 10px;
}

.activity-heatmap__weekdays {
  display: grid;
  grid-template-rows: repeat(7, minmax(0, 1fr));
  min-height: 182px;
  color: var(--text-tertiary);
  font-size: 0.72rem;
}

.activity-heatmap__weekdays span:nth-child(1) {
  grid-row: 2;
}

.activity-heatmap__weekdays span:nth-child(2) {
  grid-row: 4;
}

.activity-heatmap__weekdays span:nth-child(3) {
  grid-row: 6;
}

.activity-heatmap__grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.activity-heatmap__grid span {
  aspect-ratio: 1;
  border-radius: 8px;
  background: rgba(47, 93, 80, 0.06);
  border: 1px solid rgba(216, 207, 191, 0.48);
}

.activity-heatmap__grid .is-level-1,
.activity-heatmap__legend .is-level-1 {
  background: rgba(47, 93, 80, 0.18);
}

.activity-heatmap__grid .is-level-2,
.activity-heatmap__legend .is-level-2 {
  background: rgba(47, 93, 80, 0.34);
}

.activity-heatmap__grid .is-level-3,
.activity-heatmap__legend .is-level-3 {
  background: rgba(47, 93, 80, 0.56);
}

.activity-heatmap__grid .is-level-4,
.activity-heatmap__legend .is-level-4 {
  background: var(--brand-primary);
}

.activity-heatmap__caption {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-top: 10px;
  color: var(--text-tertiary);
  font-size: 0.78rem;
}

.activity-heatmap__legend {
  display: flex;
  gap: 5px;
  align-items: center;
}

.activity-heatmap__legend i {
  width: 14px;
  height: 14px;
  border: 1px solid rgba(216, 207, 191, 0.48);
  border-radius: 5px;
}

.activity-heatmap__legend .is-level-0 {
  background: rgba(47, 93, 80, 0.06);
}

@media (max-width: 768px) {
  .activity-heatmap__summary,
  .activity-heatmap__board {
    grid-template-columns: 1fr;
  }

  .activity-heatmap__weekdays {
    display: none;
  }
}
</style>
