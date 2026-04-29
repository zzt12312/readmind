<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import BookCover from '@/components/common/BookCover.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import { isStaticDemoMode } from '@/config/demo'
import { buildDashboardMascotCue } from '@/constants/mascotMessages'
import { useBooksStore } from '@/stores/books'
import { useDashboardStore } from '@/stores/dashboard'

const router = useRouter()
const dashboardStore = useDashboardStore()
const booksStore = useBooksStore()
const {
  metrics,
  recentBooks,
  activeTopics,
  dailyBrief,
  actionQueue,
  recommendedReview,
  loading,
} = storeToRefs(dashboardStore)
const shelfRef = ref<HTMLElement | null>(null)
const isDraggingShelf = ref(false)
const shelfAtStart = ref(true)
const shelfAtEnd = ref(false)
const dragState = {
  startX: 0,
  startScrollLeft: 0,
}

onMounted(() => {
  void dashboardStore.load()
  requestAnimationFrame(updateShelfMask)
})

function prewarmBookSummary(bookId: number) {
  void booksStore.prewarmSummary(bookId)
}

const shelfClass = computed(() => ({
  'is-dragging': isDraggingShelf.value,
  'is-at-start': shelfAtStart.value,
  'is-at-end': shelfAtEnd.value,
}))

function updateShelfMask() {
  const element = shelfRef.value
  if (!element) return
  shelfAtStart.value = element.scrollLeft <= 4
  shelfAtEnd.value = element.scrollLeft + element.clientWidth >= element.scrollWidth - 4
}

function startShelfDrag(event: MouseEvent) {
  const element = shelfRef.value
  if (!element) return
  isDraggingShelf.value = true
  dragState.startX = event.clientX
  dragState.startScrollLeft = element.scrollLeft
}

function moveShelfDrag(event: MouseEvent) {
  const element = shelfRef.value
  if (!element || !isDraggingShelf.value) return
  const delta = event.clientX - dragState.startX
  element.scrollLeft = dragState.startScrollLeft - delta
  updateShelfMask()
}

function endShelfDrag() {
  isDraggingShelf.value = false
}

function openBriefAction(path: string) {
  void router.push(path)
}

const mascotCue = computed(() => buildDashboardMascotCue(actionQueue.value[0]?.title))
const demoGuideSteps = [
  {
    label: 'Step 01',
    title: '先逛笔记工作台',
    hint: '搜索“长期主义”或“制度”，看签签如何整理摘录线索。',
    path: '/notes',
  },
  {
    label: 'Step 02',
    title: '问签签一个问题',
    hint: '演示站会返回缓存 AI 效果，也会展示引用来源。',
    path: '/qa',
  },
  {
    label: 'Step 03',
    title: '完成一组复习',
    hint: '用“不会 / 模糊 / 熟练”体验即时反馈。',
    path: '/review',
  },
  {
    label: 'Step 04',
    title: '查看数据看板',
    hint: '阅读排行、偏好雷达、热力图和高价值矩阵都已准备好。',
    path: '/analytics',
  },
]
</script>

<template>
  <div class="dashboard-view">
    <AppCard class="dashboard-view__hero">
      <div class="dashboard-view__hero-copy">
        <p class="dashboard-view__hero-eyebrow">Today in your reading workspace</p>
        <h2>{{ dailyBrief.title }}</h2>
        <p>{{ dailyBrief.summary }}</p>
        <div class="dashboard-view__hero-tags">
          <span v-for="topic in dailyBrief.highlights.topics" :key="topic">{{ topic }}</span>
          <span v-if="dailyBrief.highlights.author">常读作者：{{ dailyBrief.highlights.author }}</span>
        </div>
        <MascotBubble
          class="dashboard-view__mascot"
          :mood="mascotCue.mood"
          :message="mascotCue.message"
          :celebrating="mascotCue.celebrating"
          compact
          action-text="开始今日行动"
          @action="openBriefAction(actionQueue[0]?.path || '/review')"
        />
      </div>

      <div class="dashboard-view__brief-panel">
        <div class="dashboard-view__brief-stats">
          <article v-for="item in dailyBrief.feedback_items" :key="item.label">
            <span>{{ item.label }}</span>
            <strong>{{ item.value }}</strong>
            <p>{{ item.hint }}</p>
          </article>
        </div>
        <div class="dashboard-view__brief-actions">
          <button
            v-for="action in dailyBrief.suggested_actions"
            :key="`${action.type}-${action.path}`"
            type="button"
            @click="openBriefAction(action.path)"
          >
            {{ action.label }}
          </button>
        </div>
      </div>
    </AppCard>

    <AppCard v-if="isStaticDemoMode" class="dashboard-view__demo-guide">
      <div class="dashboard-view__demo-guide-head">
        <p class="dashboard-view__hero-eyebrow">Guided demo</p>
        <h3>3 分钟体验路线</h3>
        <span>当前为静态演示缓存，不会读取或上传你的真实 Obsidian 数据。</span>
      </div>
      <div class="dashboard-view__demo-guide-steps">
        <button
          v-for="step in demoGuideSteps"
          :key="step.path"
          type="button"
          @click="openBriefAction(step.path)"
        >
          <em>{{ step.label }}</em>
          <strong>{{ step.title }}</strong>
          <span>{{ step.hint }}</span>
        </button>
      </div>
    </AppCard>

    <section v-loading="loading" class="dashboard-view__metrics">
      <AppMetricCard
        v-for="metric in metrics"
        :key="metric.label"
        :label="metric.label"
        :value="metric.value"
        :hint="metric.hint"
      />
    </section>

    <section class="dashboard-view__action-grid">
      <AppCard
        v-for="item in actionQueue"
        :key="item.label"
        class="dashboard-view__action-card"
        :class="`is-${item.accent}`"
        @click="openBriefAction(item.path)"
      >
        <span>{{ item.label }}</span>
        <strong>{{ item.title }}</strong>
        <p>{{ item.hint }}</p>
      </AppCard>
    </section>

    <AppCard class="dashboard-view__recommend">
      <div class="dashboard-view__recommend-copy">
        <p class="dashboard-view__hero-eyebrow">Worth revisiting</p>
        <h3>值得回看：{{ recommendedReview.title || '最近笔记' }}</h3>
        <p>{{ recommendedReview.reason }}</p>
        <div class="dashboard-view__hero-tags">
          <span v-for="topic in recommendedReview.topics" :key="topic">{{ topic }}</span>
        </div>
        <button type="button" @click="openBriefAction(recommendedReview.path)">
          {{ recommendedReview.book ? '打开这本书' : '进入笔记工作台' }}
        </button>
      </div>
      <div v-if="recommendedReview.book" class="dashboard-view__recommend-book">
        <BookCover
          :src="recommendedReview.book.cover"
          :title="recommendedReview.book.title"
        />
        <div>
          <strong>{{ recommendedReview.book.title }}</strong>
          <span>{{ recommendedReview.book.author || '未知作者' }}</span>
          <em>{{ recommendedReview.book.notes }} 条笔记</em>
        </div>
      </div>
    </AppCard>

    <section class="dashboard-view__grid">
      <AppCard>
        <h3>最近整理的书</h3>
        <div class="dashboard-view__book-shelf" :class="shelfClass">
        <div
          ref="shelfRef"
          class="dashboard-view__book-list"
          @scroll="updateShelfMask"
          @mousedown="startShelfDrag"
          @mousemove="moveShelfDrag"
          @mouseleave="endShelfDrag"
          @mouseup="endShelfDrag"
        >
          <article
            v-for="(book, index) in recentBooks"
            :key="book.id"
            class="dashboard-view__book-item"
            @click="router.push(`/books/${book.id}`)"
            @mouseenter="prewarmBookSummary(book.id)"
          >
            <div class="dashboard-view__book-cover">
              <BookCover
                :src="book.cover"
                :title="book.title"
                :eager="index < 3"
              />
            </div>
            <strong class="dashboard-view__book-title">{{ book.title }}</strong>
            <p>{{ book.notes }} 条笔记</p>
            <span class="dashboard-view__book-updated">{{ book.updated }}</span>
          </article>
        </div>
        </div>
      </AppCard>

      <AppCard>
        <h3>活跃主题</h3>
        <div class="dashboard-view__topic-list">
          <span v-for="topic in activeTopics" :key="topic">{{ topic }}</span>
        </div>
      </AppCard>
    </section>
  </div>
</template>

<style scoped lang="scss">
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.dashboard-view__hero {
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

.dashboard-view__hero-copy {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}

.dashboard-view__hero-eyebrow {
  margin: 0 0 8px;
  font-size: 0.82rem;
  color: var(--brand-primary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dashboard-view__hero h2 {
  max-width: 52rem;
  margin: 0 0 10px;
  font-size: clamp(2rem, 3vw, 3.1rem);
  line-height: 1.1;
}

.dashboard-view__hero-copy > p {
  max-width: 48rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.dashboard-view__hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.dashboard-view__hero-tags span {
  padding: 9px 12px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.72);
  color: var(--brand-primary);
  font-size: 0.84rem;
  font-weight: 800;
}

.dashboard-view__mascot {
  max-width: 560px;
  margin-top: 18px;
}

.dashboard-view__brief-panel {
  padding: 16px;
  display: grid;
  gap: 14px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 26px;
  background: rgba(255, 253, 249, 0.72);
  box-shadow: 0 18px 42px rgba(47, 93, 80, 0.1);
}

.dashboard-view__brief-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.dashboard-view__brief-stats article {
  min-width: 0;
  padding: 13px;
  border: 1px solid rgba(216, 207, 191, 0.56);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.68);
}

.dashboard-view__brief-stats span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 800;
}

.dashboard-view__brief-stats strong {
  display: block;
  overflow: hidden;
  margin-top: 5px;
  color: var(--brand-primary);
  font-size: 1.28rem;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-view__brief-stats p {
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

.dashboard-view__brief-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}

.dashboard-view__brief-actions button {
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

.dashboard-view__brief-actions button:first-child {
  background: var(--brand-primary);
  color: #fff;
}

.dashboard-view__brief-actions button:hover {
  transform: translateY(-1px);
}

.dashboard-view__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.dashboard-view__demo-guide {
  padding: 22px;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
  background:
    radial-gradient(circle at 12% 10%, rgba(192, 139, 92, 0.16), transparent 34%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(239, 230, 214, 0.56));
}

.dashboard-view__demo-guide-head {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: center;
}

.dashboard-view__demo-guide-head h3 {
  margin: 0 0 10px;
  font-size: 1.45rem;
}

.dashboard-view__demo-guide-head span {
  color: var(--text-secondary);
  line-height: 1.7;
}

.dashboard-view__demo-guide-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.dashboard-view__demo-guide-steps button {
  min-width: 0;
  padding: 15px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.74);
  color: inherit;
  cursor: pointer;
  text-align: left;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease,
    transform 0.16s ease;
}

.dashboard-view__demo-guide-steps button:hover {
  border-color: rgba(47, 93, 80, 0.26);
  box-shadow: 0 14px 26px rgba(47, 93, 80, 0.08);
  transform: translateY(-2px);
}

.dashboard-view__demo-guide-steps em,
.dashboard-view__demo-guide-steps strong,
.dashboard-view__demo-guide-steps span {
  display: block;
}

.dashboard-view__demo-guide-steps em {
  color: var(--brand-primary);
  font-size: 0.72rem;
  font-style: normal;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dashboard-view__demo-guide-steps strong {
  margin-top: 8px;
  font-size: 1rem;
}

.dashboard-view__demo-guide-steps span {
  margin-top: 7px;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

.dashboard-view__action-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.dashboard-view__action-card {
  position: relative;
  overflow: hidden;
  padding: 20px;
  cursor: pointer;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease;
}

.dashboard-view__action-card::after {
  content: '';
  position: absolute;
  right: -36px;
  bottom: -42px;
  width: 112px;
  height: 112px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
}

.dashboard-view__action-card.is-warm::after {
  background: rgba(192, 139, 92, 0.14);
}

.dashboard-view__action-card.is-calm::after {
  background: rgba(77, 116, 146, 0.12);
}

.dashboard-view__action-card:hover {
  border-color: rgba(47, 93, 80, 0.2);
  transform: translateY(-2px);
}

.dashboard-view__action-card span {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.dashboard-view__action-card strong {
  display: block;
  margin-top: 10px;
  font-size: 1.25rem;
}

.dashboard-view__action-card p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.dashboard-view__recommend {
  padding: 24px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 22px;
  align-items: center;
  background:
    radial-gradient(circle at 0% 20%, rgba(47, 93, 80, 0.12), transparent 34%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(238, 228, 211, 0.52));
}

.dashboard-view__recommend h3 {
  margin: 0 0 10px;
  font-size: 1.55rem;
}

.dashboard-view__recommend-copy > p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.dashboard-view__recommend-copy button {
  margin-top: 18px;
  padding: 11px 16px;
  border: 0;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-weight: 900;
}

.dashboard-view__recommend-book {
  padding: 14px;
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.7);
}

.dashboard-view__recommend-book :deep(.book-cover) {
  width: 92px;
  height: 124px;
}

.dashboard-view__recommend-book strong,
.dashboard-view__recommend-book span,
.dashboard-view__recommend-book em {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dashboard-view__recommend-book strong {
  white-space: nowrap;
}

.dashboard-view__recommend-book span,
.dashboard-view__recommend-book em {
  margin-top: 8px;
  color: var(--text-tertiary);
  font-size: 0.88rem;
  font-style: normal;
}

.dashboard-view__grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
}

.dashboard-view__book-list {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
  scroll-snap-type: x proximity;
}

.dashboard-view__book-shelf {
  position: relative;
}

.dashboard-view__book-shelf::before,
.dashboard-view__book-shelf::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 4px;
  width: 28px;
  z-index: 1;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.dashboard-view__book-shelf::before {
  left: 0;
  background: linear-gradient(90deg, rgba(255, 253, 249, 0.95), rgba(255, 253, 249, 0));
}

.dashboard-view__book-shelf::after {
  right: 0;
  background: linear-gradient(270deg, rgba(255, 253, 249, 0.95), rgba(255, 253, 249, 0));
}

.dashboard-view__book-shelf.is-at-start::before,
.dashboard-view__book-shelf.is-at-end::after {
  opacity: 0;
}

.dashboard-view__book-list::-webkit-scrollbar {
  height: 8px;
}

.dashboard-view__book-list::-webkit-scrollbar-thumb {
  background: rgba(47, 93, 80, 0.18);
  border-radius: 999px;
}

.dashboard-view__book-item {
  display: flex;
  flex: 0 0 132px;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
  cursor: pointer;
  scroll-snap-align: start;
  user-select: none;
}

.dashboard-view__book-cover {
  width: 132px;
  height: 176px;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 12px 24px rgba(41, 74, 64, 0.18);
}

.dashboard-view__book-title {
  line-height: 1.5;
}

.dashboard-view__book-item p,
.dashboard-view__book-updated {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.86rem;
}

.dashboard-view__book-shelf.is-dragging .dashboard-view__book-list {
  cursor: grabbing;
}

.dashboard-view__topic-list {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.dashboard-view__topic-list span {
  padding: 10px 12px;
  border-radius: 999px;
  background: var(--bg-soft);
  color: var(--text-secondary);
}

@media (max-width: 1100px) {
  .dashboard-view__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-view__hero,
  .dashboard-view__action-grid,
  .dashboard-view__recommend,
  .dashboard-view__demo-guide,
  .dashboard-view__grid {
    grid-template-columns: 1fr;
  }

  .dashboard-view__demo-guide-steps {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .dashboard-view__hero,
  .dashboard-view__metrics {
    grid-template-columns: 1fr;
  }

  .dashboard-view__brief-stats {
    grid-template-columns: 1fr;
  }

  .dashboard-view__demo-guide-steps {
    grid-template-columns: 1fr;
  }
}
</style>
