<script setup lang="ts">
import type { PreferenceRadarItem } from '@/types/analytics'

interface RadarAxisPoint extends PreferenceRadarItem {
  x: number
  y: number
  labelX: number
  labelY: number
}

defineProps<{
  items: PreferenceRadarItem[]
  radarPoints: string
  radarAxisPoints: RadarAxisPoint[]
}>()
</script>

<template>
  <AppCard class="analytics-radar analytics-panel">
    <div class="analytics-panel__head">
      <div>
        <p class="analytics-panel__eyebrow">Preference radar</p>
        <h3>阅读方向雷达图</h3>
      </div>
      <span>分类数量与笔记密度综合评分</span>
    </div>
    <div class="analytics-radar__body">
      <svg viewBox="0 0 280 280" role="img" aria-label="阅读方向雷达图">
        <defs>
          <radialGradient id="analyticsRadarGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="rgba(47, 93, 80, 0.16)" />
            <stop offset="100%" stop-color="rgba(47, 93, 80, 0)" />
          </radialGradient>
        </defs>
        <circle cx="140" cy="140" r="118" class="analytics-radar__glow" />
        <circle cx="140" cy="140" r="88" />
        <circle cx="140" cy="140" r="58" />
        <circle cx="140" cy="140" r="28" />
        <g v-for="axis in radarAxisPoints" :key="axis.label">
          <line x1="140" y1="140" :x2="axis.x" :y2="axis.y" />
          <text :x="axis.labelX" :y="axis.labelY">{{ axis.label }}</text>
        </g>
        <polygon v-if="radarPoints" :points="radarPoints" />
      </svg>
      <div class="analytics-radar__legend">
        <span v-for="item in items" :key="item.label">
          <strong>{{ item.score }}</strong>{{ item.label }}
        </span>
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

.analytics-radar__body {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
}

.analytics-radar__body svg {
  width: 280px;
  height: 280px;
  overflow: visible;
}

.analytics-radar__body circle,
.analytics-radar__body line {
  fill: none;
  stroke: rgba(47, 93, 80, 0.14);
  stroke-width: 1;
}

.analytics-radar__glow {
  fill: url('#analyticsRadarGlow');
  stroke: none !important;
}

.analytics-radar__body polygon {
  fill: rgba(47, 93, 80, 0.2);
  stroke: var(--brand-primary);
  stroke-width: 2.5;
}

.analytics-radar__body text {
  fill: var(--text-secondary);
  font-size: 11px;
  font-weight: 800;
  paint-order: stroke;
  stroke: rgba(255, 253, 249, 0.92);
  stroke-width: 4px;
  stroke-linejoin: round;
  text-anchor: middle;
}

.analytics-radar__legend {
  display: grid;
  gap: 10px;
}

.analytics-radar__legend span {
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
  color: var(--text-secondary);
}

.analytics-radar__legend strong {
  color: var(--brand-primary);
}

@media (max-width: 768px) {
  .analytics-radar__body {
    grid-template-columns: 1fr;
  }
}
</style>
