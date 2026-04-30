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
import { useAppStore } from '@/stores/app'
import { useBooksStore } from '@/stores/books'
import { useDashboardStore } from '@/stores/dashboard'

const router = useRouter()
const appStore = useAppStore()
const dashboardStore = useDashboardStore()
const booksStore = useBooksStore()
const {
  metrics,
  recentBooks,
  activeTopics,
  activationReport,
  dailyBrief,
  actionQueue,
  recommendedReview,
  loading,
} = storeToRefs(dashboardStore)
const shelfRef = ref<HTMLElement | null>(null)
const isDraggingShelf = ref(false)
const shelfAtStart = ref(true)
const shelfAtEnd = ref(false)
const onboardingCollapsed = ref(false)
const dragState = {
  startX: 0,
  startScrollLeft: 0,
}

onMounted(() => {
  void dashboardStore.load()
  void appStore.loadLlmHealth()
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
const modeLabel = computed(() => {
  if (isStaticDemoMode) return '静态演示数据'
  if (appStore.llmHealth?.demo_mode) return '后端演示模式'
  return '本地真实书库'
})
const modeDetail = computed(() => {
  if (isStaticDemoMode || appStore.llmHealth?.demo_mode) {
    return '当前不会读取或上传你的真实 Obsidian 数据。'
  }
  if (!appStore.llmHealth) return '正在确认模型和数据边界。'
  return appStore.llmHealth.connected
    ? `读取本地 Vault，AI 功能会调用 ${appStore.llmHealth.provider}。`
    : '读取本地 Vault，模型不可用时会使用本地回退回答。'
})
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
const onboardingSteps = computed(() => [
  {
    key: 'sync',
    label: '01',
    title: metrics.value.length ? '阅读资产已进入工作台' : '先同步你的阅读资产',
    hint: metrics.value.length
      ? '首页已经能看到书籍、笔记和主题概览。'
      : '配置 Obsidian 阅读目录，或先使用演示数据体验完整流程。',
    path: metrics.value.length ? '/notes' : '/import',
    done: metrics.value.length > 0,
  },
  {
    key: 'value',
    label: '02',
    title: '看第一眼价值报告',
    hint: activationReport.value.recommended_questions.length
      ? '挑一个推荐问题，直接问自己的笔记。'
      : '同步后这里会给出主题、问题和今日建议。',
    path: activationReport.value.recommended_questions[0]
      ? `/qa?preset=${encodeURIComponent(activationReport.value.recommended_questions[0])}`
      : '/dashboard',
    done: activationReport.value.top_topics.length > 0,
  },
  {
    key: 'qa',
    label: '03',
    title: '提出第一个问题',
    hint: '回答会保留引用，你可以收藏、导出，或把引用带去复习。',
    path: '/qa',
    done: false,
  },
  {
    key: 'review',
    label: '04',
    title: '完成 5 分钟回看',
    hint: '先复习一小组卡片，不需要一次处理全部笔记。',
    path: '/review?goal=5',
    done: false,
  },
])
const shouldShowOnboarding = computed(() => !onboardingCollapsed.value)
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
        <div class="dashboard-view__hero-actions-main">
          <button type="button" @click="openBriefAction(activationReport.primary_action.path)">
            {{ activationReport.primary_action.label }}
          </button>
          <button type="button" @click="openBriefAction(activationReport.secondary_action.path)">
            {{ activationReport.secondary_action.label }}
          </button>
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
        <div class="dashboard-view__mode-card">
          <span>当前模式</span>
          <strong>{{ modeLabel }}</strong>
          <p>{{ modeDetail }}</p>
        </div>
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

    <AppCard v-if="shouldShowOnboarding" class="dashboard-view__onboarding">
      <div class="dashboard-view__onboarding-head">
        <div>
          <p class="dashboard-view__hero-eyebrow">First run guide</p>
          <h3>第一次使用，按这条路线走</h3>
          <span>从导入到追问，再到复习沉淀，尽量让用户不用自己猜下一步。</span>
        </div>
        <el-button text @click="onboardingCollapsed = true">收起</el-button>
      </div>
      <div class="dashboard-view__onboarding-steps">
        <button
          v-for="step in onboardingSteps"
          :key="step.key"
          type="button"
          :class="{ 'is-done': step.done }"
          @click="openBriefAction(step.path)"
        >
          <em>{{ step.label }}</em>
          <strong>{{ step.title }}</strong>
          <span>{{ step.hint }}</span>
        </button>
      </div>
    </AppCard>

    <AppCard class="dashboard-view__activation">
      <div class="dashboard-view__activation-copy">
        <p class="dashboard-view__hero-eyebrow">First Value Report</p>
        <h3>{{ activationReport.title }}</h3>
        <p>{{ activationReport.summary }}</p>
        <div class="dashboard-view__activation-topics">
          <span v-for="topic in activationReport.top_topics" :key="topic">{{ topic }}</span>
        </div>
      </div>
      <div class="dashboard-view__activation-side">
        <div class="dashboard-view__activation-cards">
          <article v-for="card in activationReport.asset_cards" :key="card.label">
            <span>{{ card.label }}</span>
            <strong>{{ card.value }}</strong>
            <p>{{ card.hint }}</p>
          </article>
        </div>
        <div class="dashboard-view__question-list">
          <strong>可以立刻追问</strong>
          <button
            v-for="question in activationReport.recommended_questions"
            :key="question"
            type="button"
            @click="router.push({ path: '/qa', query: { preset: question } })"
          >
            {{ question }}
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
      <div
        v-if="recommendedReview.book"
        class="dashboard-view__recommend-book"
        role="button"
        tabindex="0"
        @click="openBriefAction(recommendedReview.path)"
        @keydown.enter.prevent="openBriefAction(recommendedReview.path)"
        @keydown.space.prevent="openBriefAction(recommendedReview.path)"
      >
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

.dashboard-view__hero-actions-main {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.dashboard-view__hero-actions-main button {
  padding: 12px 16px;
  border: 1px solid rgba(47, 93, 80, 0.2);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.84);
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 900;
}

.dashboard-view__hero-actions-main button:first-child {
  border-color: var(--brand-primary);
  background: var(--brand-primary);
  color: #fff;
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

.dashboard-view__mode-card {
  padding: 14px;
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: 20px;
  background: rgba(47, 93, 80, 0.07);
}

.dashboard-view__mode-card span {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 900;
}

.dashboard-view__mode-card strong {
  display: block;
  margin-top: 6px;
  color: var(--brand-primary);
  font-size: 1.12rem;
}

.dashboard-view__mode-card p {
  margin: 7px 0 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
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

.dashboard-view__activation {
  display: grid;
  grid-template-columns: minmax(0, 0.86fr) minmax(420px, 1fr);
  gap: 22px;
  align-items: stretch;
  padding: 24px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(244, 239, 230, 0.76)),
    var(--bg-card);
}

.dashboard-view__activation-copy h3 {
  margin: 0 0 10px;
  font-size: 1.55rem;
}

.dashboard-view__activation-copy p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.dashboard-view__activation-topics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.dashboard-view__activation-topics span {
  padding: 8px 11px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  font-size: 0.84rem;
  font-weight: 800;
}

.dashboard-view__activation-side {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: 14px;
}

.dashboard-view__activation-cards {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.dashboard-view__activation-cards article {
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.74);
}

.dashboard-view__activation-cards span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 900;
}

.dashboard-view__activation-cards strong {
  display: block;
  margin-top: 7px;
  color: var(--text-primary);
  font-size: 1.45rem;
}

.dashboard-view__activation-cards p {
  margin: 5px 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.45;
}

.dashboard-view__question-list {
  padding: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 20px;
  background: rgba(47, 93, 80, 0.06);
}

.dashboard-view__question-list strong {
  display: block;
  margin-bottom: 10px;
  color: var(--brand-primary);
}

.dashboard-view__question-list button {
  display: block;
  width: 100%;
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 14px;
  background: rgba(255, 253, 249, 0.82);
  color: var(--text-primary);
  cursor: pointer;
  line-height: 1.55;
  text-align: left;
}

.dashboard-view__demo-guide,
.dashboard-view__onboarding {
  padding: 22px;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
  background:
    radial-gradient(circle at 12% 10%, rgba(192, 139, 92, 0.16), transparent 34%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(239, 230, 214, 0.56));
}

.dashboard-view__onboarding {
  background:
    radial-gradient(circle at 88% 8%, rgba(47, 93, 80, 0.12), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(236, 241, 234, 0.64));
}

.dashboard-view__demo-guide-head,
.dashboard-view__onboarding-head {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: center;
}

.dashboard-view__onboarding-head {
  flex-direction: row;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.dashboard-view__demo-guide-head h3,
.dashboard-view__onboarding-head h3 {
  margin: 0 0 10px;
  font-size: 1.45rem;
}

.dashboard-view__demo-guide-head span,
.dashboard-view__onboarding-head span {
  color: var(--text-secondary);
  line-height: 1.7;
}

.dashboard-view__demo-guide-steps,
.dashboard-view__onboarding-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.dashboard-view__demo-guide-steps button,
.dashboard-view__onboarding-steps button {
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

.dashboard-view__demo-guide-steps button:hover,
.dashboard-view__onboarding-steps button:hover {
  border-color: rgba(47, 93, 80, 0.26);
  box-shadow: 0 14px 26px rgba(47, 93, 80, 0.08);
  transform: translateY(-2px);
}

.dashboard-view__demo-guide-steps em,
.dashboard-view__demo-guide-steps strong,
.dashboard-view__demo-guide-steps span,
.dashboard-view__onboarding-steps em,
.dashboard-view__onboarding-steps strong,
.dashboard-view__onboarding-steps span {
  display: block;
}

.dashboard-view__demo-guide-steps em,
.dashboard-view__onboarding-steps em {
  color: var(--brand-primary);
  font-size: 0.72rem;
  font-style: normal;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.dashboard-view__onboarding-steps button.is-done em {
  color: #2f7d57;
}

.dashboard-view__demo-guide-steps strong,
.dashboard-view__onboarding-steps strong {
  margin-top: 8px;
  font-size: 1rem;
}

.dashboard-view__demo-guide-steps span,
.dashboard-view__onboarding-steps span {
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
  cursor: pointer;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease,
    transform 0.16s ease;
}

.dashboard-view__recommend-book:hover,
.dashboard-view__recommend-book:focus-visible {
  border-color: rgba(47, 93, 80, 0.28);
  box-shadow: 0 16px 28px rgba(47, 93, 80, 0.1);
  outline: 0;
  transform: translateY(-2px);
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
  .dashboard-view__activation,
  .dashboard-view__activation-side,
  .dashboard-view__demo-guide,
  .dashboard-view__onboarding,
  .dashboard-view__grid {
    grid-template-columns: 1fr;
  }

  .dashboard-view__demo-guide-steps,
  .dashboard-view__onboarding-steps {
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

  .dashboard-view__demo-guide-steps,
  .dashboard-view__onboarding-steps {
    grid-template-columns: 1fr;
  }
}
</style>
