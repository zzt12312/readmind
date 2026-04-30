<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import BookCover from '@/components/common/BookCover.vue'
import { useAnalyticsStore } from '@/stores/analytics'

const router = useRouter()
const analyticsStore = useAnalyticsStore()
const {
  metrics,
  categoryPreferences,
  preferenceRadar,
  readingTimeRank,
  highValueMatrix,
  topicRank,
  reviewFunnel,
  reviewProgress,
  readingTimeline,
  authorCloud,
  activityHeatmap,
  longTermMetrics,
  recommendations,
  loading,
} = storeToRefs(analyticsStore)

onMounted(() => {
  void analyticsStore.load()
})

const maxCategoryBooks = computed(() =>
  Math.max(...categoryPreferences.value.map((item) => item.book_count), 1),
)
const maxReadingMinutes = computed(() =>
  Math.max(...readingTimeRank.value.map((item) => item.reading_time_minutes), 1),
)
const maxTopicCount = computed(() =>
  Math.max(...topicRank.value.map((item) => item.count), 1),
)
const maxFunnelValue = computed(() =>
  Math.max(...reviewFunnel.value.map((item) => item.value), 1),
)
const reviewCoverage = computed(() => {
  if (!reviewProgress.value.total_notes) return 0
  return Math.round((reviewProgress.value.reviewed_count / reviewProgress.value.total_notes) * 100)
})
const heatmapTotalActivity = computed(() =>
  activityHeatmap.value.reduce((total, day) => total + day.count, 0),
)
const heatmapActiveDays = computed(() => activityHeatmap.value.filter((day) => day.count > 0).length)
const matrixListBooks = computed(() => highValueMatrix.value.slice(0, 4))
const matrixTopBook = computed(() => matrixListBooks.value[0])
const radarPoints = computed(() => {
  const items = preferenceRadar.value
  if (!items.length) return ''
  const center = 140
  const radius = 82
  return items.map((item, index) => {
    const angle = (Math.PI * 2 * index) / items.length - Math.PI / 2
    const scaledRadius = radius * (item.score / 100)
    return `${center + Math.cos(angle) * scaledRadius},${center + Math.sin(angle) * scaledRadius}`
  }).join(' ')
})
const radarAxisPoints = computed(() => {
  const items = preferenceRadar.value
  const center = 140
  const radius = 88
  return items.map((item, index) => {
    const angle = (Math.PI * 2 * index) / items.length - Math.PI / 2
    return {
      ...item,
      x: center + Math.cos(angle) * radius,
      y: center + Math.sin(angle) * radius,
      labelX: center + Math.cos(angle) * 118,
      labelY: center + Math.sin(angle) * 118,
    }
  })
})
function clampMatrixPosition(value: number) {
  return Math.min(90, Math.max(10, value))
}

function openRecommendation(path: string) {
  void router.push(path)
}
</script>

<template>
  <div v-loading="loading" class="analytics-view">
    <AppCard class="analytics-view__hero">
      <div>
        <p class="analytics-view__eyebrow">Reading analytics</p>
        <h2>把阅读偏好、阅读时长和复习进展放到一张工作台里。</h2>
        <p>
          看板会优先使用微信读书导出的 readingTime 字段生成阅读时长榜，
          并结合笔记、主题与复习记录观察你的长期阅读偏好。
        </p>
      </div>
      <div class="analytics-view__coverage">
        <strong>{{ reviewCoverage }}%</strong>
        <span>复习覆盖率</span>
      </div>
    </AppCard>

    <section class="analytics-view__metrics">
      <AppMetricCard
        v-for="metric in metrics"
        :key="metric.label"
        :label="metric.label"
        :value="metric.value"
        :hint="metric.hint"
      />
    </section>

    <AppCard v-if="recommendations.length" class="analytics-view__recommendations">
      <div class="analytics-view__recommendations-head">
        <div>
          <p class="analytics-view__eyebrow">Next best actions</p>
          <h3>看板给你的下一步建议</h3>
        </div>
        <span>基于高价值书籍、主题密度和复习压力生成</span>
      </div>
      <div class="analytics-view__recommendation-list">
        <article
          v-for="item in recommendations"
          :key="`${item.type}-${item.title}`"
          :class="`is-${item.priority}`"
        >
          <span>{{ item.priority === 'high' ? '优先' : item.priority === 'medium' ? '建议' : '观察' }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.reason }}</p>
          <button type="button" @click="openRecommendation(item.path)">
            {{ item.action_label }}
          </button>
        </article>
      </div>
    </AppCard>

    <section class="analytics-view__grid">
      <AppCard class="analytics-view__panel">
        <div class="analytics-view__panel-head">
          <div>
            <p class="analytics-view__eyebrow">Preference map</p>
            <h3>阅读偏好方向</h3>
          </div>
          <span>按书籍分类与摘录量综合观察</span>
        </div>
        <div class="analytics-view__bar-list">
          <article v-for="item in categoryPreferences" :key="item.category" class="analytics-view__bar-item">
            <div class="analytics-view__bar-meta">
              <strong>{{ item.category }}</strong>
              <span>{{ item.book_count }} 本 / {{ item.note_count }} 条笔记</span>
            </div>
            <div class="analytics-view__bar-track">
              <i :style="{ width: `${Math.max(8, (item.book_count / maxCategoryBooks) * 100)}%` }" />
            </div>
            <em>{{ item.share }}%</em>
          </article>
        </div>
      </AppCard>

      <AppCard class="analytics-view__panel">
        <div class="analytics-view__panel-head">
          <div>
            <p class="analytics-view__eyebrow">Review progress</p>
            <h3>复习进展漏斗</h3>
          </div>
          <span>{{ reviewProgress.streak_days }} 天连续复习</span>
        </div>
        <div class="analytics-view__funnel">
          <article v-for="item in reviewFunnel" :key="item.label">
            <div>
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </div>
            <p>{{ item.hint }}</p>
            <i :style="{ width: `${Math.max(10, (item.value / maxFunnelValue) * 100)}%` }" />
          </article>
        </div>
      </AppCard>
    </section>

    <section class="analytics-view__insight-grid">
      <AppCard class="analytics-view__panel analytics-view__radar-panel">
        <div class="analytics-view__panel-head">
          <div>
            <p class="analytics-view__eyebrow">Preference radar</p>
            <h3>阅读方向雷达图</h3>
          </div>
          <span>分类数量与笔记密度综合评分</span>
        </div>
        <div class="analytics-view__radar">
          <svg viewBox="0 0 280 280" role="img" aria-label="阅读方向雷达图">
            <defs>
              <radialGradient id="analyticsRadarGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(47, 93, 80, 0.16)" />
                <stop offset="100%" stop-color="rgba(47, 93, 80, 0)" />
              </radialGradient>
            </defs>
            <circle cx="140" cy="140" r="118" class="analytics-view__radar-glow" />
            <circle cx="140" cy="140" r="88" />
            <circle cx="140" cy="140" r="58" />
            <circle cx="140" cy="140" r="28" />
            <g v-for="axis in radarAxisPoints" :key="axis.label">
              <line x1="140" y1="140" :x2="axis.x" :y2="axis.y" />
              <text :x="axis.labelX" :y="axis.labelY">{{ axis.label }}</text>
            </g>
            <polygon v-if="radarPoints" :points="radarPoints" />
          </svg>
          <div class="analytics-view__radar-legend">
            <span v-for="item in preferenceRadar" :key="item.label">
              <strong>{{ item.score }}</strong>{{ item.label }}
            </span>
          </div>
        </div>
      </AppCard>

      <AppCard class="analytics-view__panel">
        <div class="analytics-view__panel-head">
          <div>
            <p class="analytics-view__eyebrow">Activity heatmap</p>
            <h3>知识投入热力图</h3>
          </div>
          <span>每个方块代表 1 天，颜色越深表示当天摘录/复习越多</span>
        </div>
        <div class="analytics-view__heatmap-summary">
          <article>
            <strong>{{ heatmapActiveDays }}</strong>
            <span>活跃天数</span>
          </article>
          <article>
            <strong>{{ heatmapTotalActivity }}</strong>
            <span>总活动次数</span>
          </article>
          <p>用于观察最近 35 天是否保持稳定输入，而不是单纯追求某一天的峰值。</p>
        </div>
        <div class="analytics-view__heatmap-board">
          <div class="analytics-view__heatmap-weekdays" aria-hidden="true">
            <span>周一</span>
            <span>周三</span>
            <span>周五</span>
          </div>
          <div>
            <div class="analytics-view__heatmap">
              <span
                v-for="day in activityHeatmap"
                :key="day.date"
                :class="`is-level-${day.level}`"
                :title="`${day.date}: ${day.count} 次摘录/复习`"
              />
            </div>
            <div class="analytics-view__heatmap-caption">
              <span>35 天前</span>
              <div class="analytics-view__heatmap-legend" aria-label="热力图颜色图例">
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
    </section>

    <section class="analytics-view__insight-grid">
      <AppCard class="analytics-view__panel">
        <div class="analytics-view__panel-head">
          <div>
            <p class="analytics-view__eyebrow">Value matrix</p>
            <h3>高价值书籍矩阵</h3>
          </div>
          <span>横轴笔记密度，纵轴复习回看</span>
        </div>
        <div class="analytics-view__matrix-layout">
          <div class="analytics-view__matrix">
            <span class="analytics-view__matrix-axis is-y">高复习</span>
            <span class="analytics-view__matrix-axis is-x">高笔记</span>
            <button
              v-for="book in highValueMatrix"
              :key="book.id"
              type="button"
              :style="{ left: `${clampMatrixPosition(book.x)}%`, bottom: `${clampMatrixPosition(book.y)}%` }"
              :title="`${book.title}: ${book.note_count} 条笔记 / ${book.reviewed_count} 次复习`"
              @click="router.push(`/books/${book.id}`)"
            >
              {{ book.title.slice(0, 2) }}
            </button>
          </div>
          <div class="analytics-view__matrix-list">
            <article
              v-for="book in matrixListBooks"
              :key="book.id"
              @click="router.push(`/books/${book.id}`)"
            >
              <strong>{{ book.title }}</strong>
              <span>{{ book.note_count }} 条笔记 · {{ book.reviewed_count }} 次复习</span>
              <i :style="{ width: `${Math.min(100, Math.max(8, book.value_score))}%` }" />
            </article>
            <div v-if="matrixTopBook" class="analytics-view__matrix-note">
              <span>下一本优先回看</span>
              <strong>{{ matrixTopBook.title }}</strong>
              <p>这本书同时拥有较高摘录密度和复习痕迹，适合作为近期知识复盘入口。</p>
            </div>
          </div>
        </div>
      </AppCard>

      <AppCard class="analytics-view__panel">
        <div class="analytics-view__panel-head">
          <div>
            <p class="analytics-view__eyebrow">Long-term index</p>
            <h3>长期主义指标</h3>
          </div>
          <span>持续复习、覆盖率与掌握沉淀</span>
        </div>
        <div class="analytics-view__long-term">
          <article v-for="item in longTermMetrics" :key="item.label">
            <div>
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </div>
            <p>{{ item.hint }}</p>
            <i :style="{ width: `${item.score}%` }" />
          </article>
        </div>
      </AppCard>
    </section>

    <section class="analytics-view__wide-grid">
      <div class="analytics-view__left-stack">
        <AppCard class="analytics-view__panel analytics-view__rank-panel">
          <div class="analytics-view__panel-head">
            <div>
              <p class="analytics-view__eyebrow">Reading time rank</p>
              <h3>阅读时长排行榜</h3>
            </div>
            <span>共 {{ readingTimeRank.length }} 本，可滚动查看更多</span>
          </div>
          <div class="analytics-view__book-rank">
            <article
              v-for="(book, index) in readingTimeRank"
              :key="book.id"
              @click="router.push(`/books/${book.id}`)"
            >
              <span class="analytics-view__rank-index">{{ index + 1 }}</span>
              <BookCover :src="book.cover" :title="book.title" />
              <div class="analytics-view__rank-copy">
                <strong>{{ book.title }}</strong>
                <span>{{ book.category }} · {{ book.reading_time || '暂无阅读时长' }}</span>
                <div class="analytics-view__score-track">
                  <i :style="{ width: `${Math.max(8, (book.reading_time_minutes / maxReadingMinutes) * 100)}%` }" />
                </div>
              </div>
              <div class="analytics-view__rank-stat">
                <strong>{{ book.reading_time_minutes }}</strong>
                <span>分钟</span>
              </div>
              <div class="analytics-view__rank-stat">
                <strong>{{ book.note_count }}</strong>
                <span>笔记</span>
              </div>
            </article>
          </div>
        </AppCard>

        <AppCard class="analytics-view__panel analytics-view__author-panel">
          <div class="analytics-view__panel-head">
            <div>
              <p class="analytics-view__eyebrow">Author cloud</p>
              <h3>喜欢的作者</h3>
            </div>
            <span>按书籍数与笔记数加权</span>
          </div>
          <div class="analytics-view__author-cloud">
            <span
              v-for="author in authorCloud"
              :key="author.author"
              :style="{ fontSize: `${0.82 + author.weight / 180}rem` }"
              :title="`${author.author}: ${author.book_count} 本 / ${author.note_count} 条笔记`"
            >
              {{ author.author }}
            </span>
          </div>
        </AppCard>
      </div>

      <div class="analytics-view__side-stack">
        <AppCard class="analytics-view__panel">
          <div class="analytics-view__panel-head">
            <div>
              <p class="analytics-view__eyebrow">Topic rank</p>
              <h3>主题关注榜</h3>
            </div>
          </div>
          <div class="analytics-view__topic-rank">
            <article v-for="topic in topicRank" :key="topic.topic">
              <span>{{ topic.topic }}</span>
              <strong>{{ topic.count }}</strong>
              <i :style="{ width: `${Math.max(8, (topic.count / maxTopicCount) * 100)}%` }" />
            </article>
          </div>
        </AppCard>

        <AppCard class="analytics-view__panel">
          <div class="analytics-view__panel-head">
            <div>
              <p class="analytics-view__eyebrow">Timeline</p>
              <h3>阅读整理时间线</h3>
            </div>
          </div>
          <div class="analytics-view__timeline">
            <article v-for="item in readingTimeline" :key="item.period">
              <strong>{{ item.period }}</strong>
              <span>{{ item.book_count }} 本</span>
              <p>{{ item.books.join('、') || '暂无书名' }}</p>
            </article>
          </div>
        </AppCard>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.analytics-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analytics-view__hero {
  padding: 28px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24px;
  background:
    radial-gradient(circle at 8% 12%, rgba(47, 93, 80, 0.14), transparent 32%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(238, 228, 211, 0.58));
}

.analytics-view__hero h2 {
  max-width: 56rem;
  margin: 0 0 10px;
}

.analytics-view__hero p:last-child {
  max-width: 52rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.analytics-view__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.analytics-view__coverage {
  min-width: 136px;
  padding: 18px;
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: 24px;
  background: rgba(255, 253, 249, 0.78);
  text-align: center;
}

.analytics-view__coverage strong {
  display: block;
  color: var(--brand-primary);
  font-size: 2.2rem;
}

.analytics-view__coverage span {
  color: var(--text-tertiary);
}

.analytics-view__metrics {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
}

.analytics-view__recommendations {
  padding: 22px;
  background:
    radial-gradient(circle at 8% 0%, rgba(47, 93, 80, 0.12), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(244, 238, 228, 0.74));
}

.analytics-view__recommendations-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.analytics-view__recommendations-head h3 {
  margin: 0;
}

.analytics-view__recommendations-head > span {
  color: var(--text-tertiary);
  font-size: 0.88rem;
  line-height: 1.6;
}

.analytics-view__recommendation-list {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.analytics-view__recommendation-list article {
  min-width: 0;
  padding: 16px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.76);
}

.analytics-view__recommendation-list article.is-high {
  border-color: rgba(47, 93, 80, 0.22);
  background:
    linear-gradient(180deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.82)),
    var(--bg-card);
}

.analytics-view__recommendation-list span {
  display: inline-flex;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  font-size: 0.76rem;
  font-weight: 900;
}

.analytics-view__recommendation-list strong {
  display: block;
  margin-top: 10px;
  line-height: 1.45;
}

.analytics-view__recommendation-list p {
  margin: 8px 0 14px;
  color: var(--text-secondary);
  font-size: 0.86rem;
  line-height: 1.6;
}

.analytics-view__recommendation-list button {
  padding: 9px 12px;
  border: 0;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

.analytics-view__grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 16px;
}

.analytics-view__wide-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.8fr);
  gap: 16px;
}

.analytics-view__insight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.analytics-view__side-stack {
  display: grid;
  gap: 16px;
}

.analytics-view__left-stack {
  display: grid;
  gap: 16px;
  align-content: start;
}

.analytics-view__panel {
  padding: 22px;
}

.analytics-view__panel-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.analytics-view__panel-head h3 {
  margin: 0;
}

.analytics-view__panel-head > span {
  color: var(--text-tertiary);
  font-size: 0.88rem;
}

.analytics-view__bar-list,
.analytics-view__funnel,
.analytics-view__topic-rank,
.analytics-view__timeline {
  display: grid;
  gap: 12px;
}

.analytics-view__bar-item {
  display: grid;
  grid-template-columns: minmax(120px, 1fr) minmax(140px, 1.4fr) 42px;
  gap: 12px;
  align-items: center;
}

.analytics-view__bar-meta {
  display: grid;
  gap: 3px;
}

.analytics-view__bar-meta span,
.analytics-view__rank-copy span {
  color: var(--text-tertiary);
  font-size: 0.86rem;
}

.analytics-view__bar-track,
.analytics-view__score-track {
  height: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
}

.analytics-view__bar-track i,
.analytics-view__score-track i,
.analytics-view__topic-rank i,
.analytics-view__funnel i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--brand-primary), #c58b5c);
}

.analytics-view__bar-item em {
  color: var(--text-secondary);
  font-style: normal;
  font-weight: 800;
  text-align: right;
}

.analytics-view__funnel article {
  position: relative;
  overflow: hidden;
  padding: 14px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.72);
}

.analytics-view__funnel article > div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
}

.analytics-view__funnel strong {
  font-size: 1.5rem;
}

.analytics-view__funnel p {
  margin: 4px 0 12px;
  color: var(--text-tertiary);
}

.analytics-view__funnel i {
  height: 8px;
}

.analytics-view__radar {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
}

.analytics-view__radar svg {
  width: 280px;
  height: 280px;
  overflow: visible;
}

.analytics-view__radar circle,
.analytics-view__radar line {
  fill: none;
  stroke: rgba(47, 93, 80, 0.14);
  stroke-width: 1;
}

.analytics-view__radar-glow {
  fill: url('#analyticsRadarGlow');
  stroke: none !important;
}

.analytics-view__radar polygon {
  fill: rgba(47, 93, 80, 0.2);
  stroke: var(--brand-primary);
  stroke-width: 2.5;
}

.analytics-view__radar text {
  fill: var(--text-secondary);
  font-size: 11px;
  font-weight: 800;
  paint-order: stroke;
  stroke: rgba(255, 253, 249, 0.92);
  stroke-width: 4px;
  stroke-linejoin: round;
  text-anchor: middle;
}

.analytics-view__radar-legend {
  display: grid;
  gap: 10px;
}

.analytics-view__radar-legend span {
  padding: 10px 12px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
  color: var(--text-secondary);
}

.analytics-view__radar-legend strong {
  color: var(--brand-primary);
}

.analytics-view__heatmap-summary {
  display: grid;
  grid-template-columns: 104px 104px minmax(0, 1fr);
  gap: 10px;
  align-items: stretch;
  margin-bottom: 14px;
}

.analytics-view__heatmap-summary article,
.analytics-view__heatmap-summary p {
  margin: 0;
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.58);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.68);
}

.analytics-view__heatmap-summary strong {
  display: block;
  color: var(--brand-primary);
  font-size: 1.35rem;
}

.analytics-view__heatmap-summary span,
.analytics-view__heatmap-summary p {
  color: var(--text-tertiary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.analytics-view__heatmap-board {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  gap: 10px;
}

.analytics-view__heatmap-weekdays {
  display: grid;
  grid-template-rows: repeat(7, minmax(0, 1fr));
  min-height: 182px;
  color: var(--text-tertiary);
  font-size: 0.72rem;
}

.analytics-view__heatmap-weekdays span:nth-child(1) {
  grid-row: 2;
}

.analytics-view__heatmap-weekdays span:nth-child(2) {
  grid-row: 4;
}

.analytics-view__heatmap-weekdays span:nth-child(3) {
  grid-row: 6;
}

.analytics-view__heatmap {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.analytics-view__heatmap span {
  aspect-ratio: 1;
  border-radius: 8px;
  background: rgba(47, 93, 80, 0.06);
  border: 1px solid rgba(216, 207, 191, 0.48);
}

.analytics-view__heatmap .is-level-1 {
  background: rgba(47, 93, 80, 0.18);
}

.analytics-view__heatmap .is-level-2 {
  background: rgba(47, 93, 80, 0.34);
}

.analytics-view__heatmap .is-level-3 {
  background: rgba(47, 93, 80, 0.56);
}

.analytics-view__heatmap .is-level-4 {
  background: var(--brand-primary);
}

.analytics-view__heatmap-caption {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-top: 10px;
  color: var(--text-tertiary);
  font-size: 0.78rem;
}

.analytics-view__heatmap-legend {
  display: flex;
  gap: 5px;
  align-items: center;
}

.analytics-view__heatmap-legend i {
  width: 14px;
  height: 14px;
  border: 1px solid rgba(216, 207, 191, 0.48);
  border-radius: 5px;
}

.analytics-view__heatmap-legend .is-level-0 {
  background: rgba(47, 93, 80, 0.06);
}

.analytics-view__heatmap-legend .is-level-1 {
  background: rgba(47, 93, 80, 0.18);
}

.analytics-view__heatmap-legend .is-level-2 {
  background: rgba(47, 93, 80, 0.34);
}

.analytics-view__heatmap-legend .is-level-3 {
  background: rgba(47, 93, 80, 0.56);
}

.analytics-view__heatmap-legend .is-level-4 {
  background: var(--brand-primary);
}

.analytics-view__matrix-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 210px;
  gap: 14px;
  align-items: stretch;
}

.analytics-view__matrix {
  position: relative;
  min-height: 220px;
  overflow: hidden;
  margin-bottom: 0;
  border: 1px solid rgba(216, 207, 191, 0.7);
  border-radius: 22px;
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.08) 1px, transparent 1px),
    linear-gradient(0deg, rgba(47, 93, 80, 0.08) 1px, transparent 1px),
    radial-gradient(circle at 80% 20%, rgba(197, 139, 92, 0.16), transparent 28%),
    rgba(255, 253, 249, 0.64);
  background-size:
    25% 100%,
    100% 25%,
    auto,
    auto;
}

.analytics-view__matrix button {
  position: absolute;
  translate: -50% 50%;
  width: 42px;
  height: 42px;
  border: 2px solid rgba(255, 253, 249, 0.92);
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 900;
  box-shadow: 0 14px 28px rgba(47, 93, 80, 0.2);
}

.analytics-view__matrix-axis {
  position: absolute;
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.analytics-view__matrix-axis.is-y {
  top: 12px;
  left: 14px;
}

.analytics-view__matrix-axis.is-x {
  right: 14px;
  bottom: 12px;
}

.analytics-view__matrix-list {
  display: grid;
  gap: 10px;
  align-content: start;
}

.analytics-view__matrix-list article,
.analytics-view__matrix-note {
  padding: 12px;
  overflow: hidden;
  border: 1px solid rgba(216, 207, 191, 0.64);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.72);
}

.analytics-view__matrix-list article {
  cursor: pointer;
}

.analytics-view__matrix-list strong,
.analytics-view__matrix-list span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.analytics-view__matrix-list span {
  margin-top: 4px;
  color: var(--text-tertiary);
  font-size: 0.82rem;
}

.analytics-view__matrix-list i {
  display: block;
  height: 6px;
  max-width: 100%;
  margin-top: 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--brand-primary), #c58b5c);
}

.analytics-view__matrix-note {
  background:
    radial-gradient(circle at 100% 0%, rgba(197, 139, 92, 0.14), transparent 46%),
    rgba(47, 93, 80, 0.06);
}

.analytics-view__matrix-note span {
  color: var(--brand-primary);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.analytics-view__matrix-note strong {
  display: block;
  margin-top: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.analytics-view__matrix-note p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.55;
}

.analytics-view__long-term {
  display: grid;
  gap: 12px;
}

.analytics-view__long-term article {
  padding: 14px;
  overflow: hidden;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.72);
}

.analytics-view__long-term article > div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
}

.analytics-view__long-term strong {
  font-size: 1.25rem;
}

.analytics-view__long-term p {
  margin: 5px 0 12px;
  color: var(--text-tertiary);
  line-height: 1.5;
}

.analytics-view__long-term i {
  display: block;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--brand-primary), #c58b5c);
}

.analytics-view__rank-panel {
  max-height: 620px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.analytics-view__book-rank {
  flex: 1;
  display: grid;
  gap: 12px;
  min-height: 0;
  overflow-y: auto;
  padding-right: 4px;
}

.analytics-view__book-rank::-webkit-scrollbar {
  width: 6px;
}

.analytics-view__book-rank::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.22);
}

.analytics-view__author-panel {
  background:
    radial-gradient(circle at 12% 20%, rgba(47, 93, 80, 0.12), transparent 34%),
    radial-gradient(circle at 86% 18%, rgba(197, 139, 92, 0.14), transparent 32%),
    rgba(255, 253, 249, 0.94);
}

.analytics-view__author-cloud {
  min-height: 172px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-content: center;
  align-items: center;
}

.analytics-view__author-cloud span {
  padding: 8px 11px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.72);
  color: var(--brand-primary);
  font-weight: 900;
  line-height: 1;
  box-shadow: 0 10px 24px rgba(47, 93, 80, 0.07);
}

.analytics-view__book-rank article {
  display: grid;
  grid-template-columns: 32px 44px minmax(0, 1fr) 64px 64px;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.64);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.68);
  cursor: pointer;
  transition:
    border-color 0.16s ease,
    transform 0.16s ease;
}

.analytics-view__book-rank article:hover {
  border-color: rgba(47, 93, 80, 0.22);
  transform: translateY(-1px);
}

.analytics-view__rank-index {
  color: var(--brand-primary);
  font-weight: 900;
}

.analytics-view__rank-copy {
  display: grid;
  gap: 5px;
  min-width: 0;
}

.analytics-view__rank-copy strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.analytics-view__rank-stat {
  display: grid;
  text-align: right;
}

.analytics-view__rank-stat strong {
  font-size: 1.2rem;
}

.analytics-view__rank-stat span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
}

.analytics-view__topic-rank article {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 40px;
  gap: 10px;
  align-items: center;
  padding-bottom: 10px;
}

.analytics-view__topic-rank article span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.analytics-view__topic-rank i {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 5px;
  opacity: 0.68;
}

.analytics-view__timeline article {
  padding-left: 14px;
  border-left: 3px solid rgba(47, 93, 80, 0.18);
}

.analytics-view__timeline strong {
  margin-right: 8px;
}

.analytics-view__timeline span {
  color: var(--brand-primary);
  font-weight: 800;
}

.analytics-view__timeline p {
  margin: 4px 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

@media (max-width: 1180px) {
  .analytics-view__metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .analytics-view__grid,
  .analytics-view__insight-grid,
  .analytics-view__wide-grid,
  .analytics-view__recommendation-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .analytics-view__hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .analytics-view__metrics,
  .analytics-view__bar-item,
  .analytics-view__heatmap-summary,
  .analytics-view__matrix-layout,
  .analytics-view__radar,
  .analytics-view__book-rank article {
    grid-template-columns: 1fr;
  }

  .analytics-view__heatmap-board {
    grid-template-columns: 1fr;
  }

  .analytics-view__heatmap-weekdays {
    display: none;
  }

  .analytics-view__rank-stat {
    text-align: left;
  }
}
</style>
