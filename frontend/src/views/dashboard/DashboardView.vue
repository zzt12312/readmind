<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import BookCover from '@/components/common/BookCover.vue'
import { useBooksStore } from '@/stores/books'
import { useDashboardStore } from '@/stores/dashboard'

const router = useRouter()
const dashboardStore = useDashboardStore()
const booksStore = useBooksStore()
const { metrics, recentBooks, activeTopics, reviewSummary, loading } = storeToRefs(dashboardStore)
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
</script>

<template>
  <div class="dashboard-view">
    <AppCard class="dashboard-view__hero">
      <div>
        <p class="dashboard-view__hero-eyebrow">Today in your reading workspace</p>
        <h2>今天建议先复习 {{ reviewSummary.suggested_count }} 条笔记，再逐步消化剩余 {{ reviewSummary.due_count }} 条待回看内容。</h2>
        <p>
          你已经连续复习 {{ reviewSummary.streak_days }} 天，当前掌握率为 {{ reviewSummary.mastery_rate }}。先完成一小组复习，再回到书库继续整理，会更轻松。
        </p>
      </div>
      <el-button type="primary" round @click="router.push('/review')">进入复习</el-button>
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
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  background:
    linear-gradient(120deg, rgba(47, 93, 80, 0.08), rgba(192, 139, 92, 0.12)),
    rgba(255, 253, 249, 0.94);
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
}

.dashboard-view__hero p:last-child {
  max-width: 48rem;
  margin: 0;
  color: var(--text-secondary);
}

.dashboard-view__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
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

  .dashboard-view__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-view__hero,
  .dashboard-view__metrics {
    grid-template-columns: 1fr;
  }

  .dashboard-view__hero {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
