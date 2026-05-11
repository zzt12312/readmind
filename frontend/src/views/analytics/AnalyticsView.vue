<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import ActivityHeatmapPanel from '@/components/analytics/ActivityHeatmapPanel.vue'
import AnalyticsHero from '@/components/analytics/AnalyticsHero.vue'
import AnalyticsRecommendationList from '@/components/analytics/AnalyticsRecommendationList.vue'
import BookCover from '@/components/common/BookCover.vue'
import PreferenceRadarPanel from '@/components/analytics/PreferenceRadarPanel.vue'
import ValueMatrixPanel from '@/components/analytics/ValueMatrixPanel.vue'
import { useAnalyticsDerivedData } from '@/composables/useAnalyticsDerivedData'
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

const {
  maxCategoryBooks,
  maxReadingMinutes,
  maxTopicCount,
  maxFunnelValue,
  reviewCoverage,
  heatmapTotalActivity,
  heatmapActiveDays,
  matrixListBooks,
  matrixTopBook,
  radarPoints,
  radarAxisPoints,
  clampMatrixPosition,
} = useAnalyticsDerivedData({
  categoryPreferences,
  preferenceRadar,
  readingTimeRank,
  highValueMatrix,
  topicRank,
  reviewFunnel,
  reviewProgress,
  activityHeatmap,
})

function openRecommendation(path: string) {
  void router.push(path)
}

function openBook(bookId: number) {
  void router.push(`/books/${bookId}`)
}
</script>

<template>
  <div v-loading="loading" class="analytics-view">
    <AnalyticsHero :review-coverage="reviewCoverage" />

    <section class="analytics-view__metrics">
      <AppMetricCard
        v-for="metric in metrics"
        :key="metric.label"
        :label="metric.label"
        :value="metric.value"
        :hint="metric.hint"
      />
    </section>

    <AnalyticsRecommendationList
      :recommendations="recommendations"
      @open="openRecommendation"
    />

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
      <PreferenceRadarPanel
        :items="preferenceRadar"
        :radar-points="radarPoints"
        :radar-axis-points="radarAxisPoints"
      />

      <ActivityHeatmapPanel
        :activity-heatmap="activityHeatmap"
        :active-days="heatmapActiveDays"
        :total-activity="heatmapTotalActivity"
      />
    </section>

    <section class="analytics-view__insight-grid">
      <ValueMatrixPanel
        :books="highValueMatrix"
        :matrix-list-books="matrixListBooks"
        :matrix-top-book="matrixTopBook"
        :clamp-position="clampMatrixPosition"
        @open-book="openBook"
      />

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

.analytics-view__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.analytics-view__metrics {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 14px;
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
  .analytics-view__wide-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .analytics-view__metrics,
  .analytics-view__bar-item,
  .analytics-view__book-rank article {
    grid-template-columns: 1fr;
  }

  .analytics-view__rank-stat {
    text-align: left;
  }
}
</style>
