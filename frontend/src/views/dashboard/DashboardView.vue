<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import ActiveTopicList from '@/components/dashboard/ActiveTopicList.vue'
import DashboardActionQueue from '@/components/dashboard/DashboardActionQueue.vue'
import DashboardHero from '@/components/dashboard/DashboardHero.vue'
import FirstRunGuide from '@/components/dashboard/FirstRunGuide.vue'
import FirstValueReport from '@/components/dashboard/FirstValueReport.vue'
import RecentBookShelf from '@/components/dashboard/RecentBookShelf.vue'
import RecommendedReviewCard from '@/components/dashboard/RecommendedReviewCard.vue'
import { isStaticDemoMode } from '@/config/demo'
import { buildDashboardMascotCue } from '@/constants/mascotMessages'
import { useAppStore } from '@/stores/app'
import { useBooksStore } from '@/stores/books'
import { useDashboardStore } from '@/stores/dashboard'

// DashboardView composes homepage sections only.
// Section UI lives in components/dashboard so the product entry stays easy to scan.
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
const onboardingCollapsed = ref(false)

onMounted(() => {
  void dashboardStore.load()
  void appStore.loadLlmHealth()
})

function prewarmBookSummary(bookId: number) {
  void booksStore.prewarmSummary(bookId)
}

function navigate(path: string) {
  void router.push(path)
}

function askQuestion(question: string) {
  void router.push({ path: '/qa', query: { preset: question } })
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
    <DashboardHero
      :daily-brief="dailyBrief"
      :activation-report="activationReport"
      :action-queue="actionQueue"
      :mode-label="modeLabel"
      :mode-detail="modeDetail"
      :mascot-cue="mascotCue"
      @navigate="navigate"
    />

    <FirstRunGuide
      v-if="shouldShowOnboarding"
      :steps="onboardingSteps"
      @dismiss="onboardingCollapsed = true"
      @navigate="navigate"
    />

    <FirstValueReport
      :report="activationReport"
      @ask-question="askQuestion"
    />

    <section v-loading="loading" class="dashboard-view__metrics">
      <AppMetricCard
        v-for="metric in metrics"
        :key="metric.label"
        :label="metric.label"
        :value="metric.value"
        :hint="metric.hint"
      />
    </section>

    <DashboardActionQueue
      :items="actionQueue"
      @navigate="navigate"
    />

    <RecommendedReviewCard
      :review="recommendedReview"
      @navigate="navigate"
    />

    <section class="dashboard-view__grid">
      <RecentBookShelf
        :books="recentBooks"
        @navigate="navigate"
        @prewarm="prewarmBookSummary"
      />
      <ActiveTopicList :topics="activeTopics" />
    </section>
  </div>
</template>

<style scoped lang="scss">
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

@media (max-width: 1100px) {
  .dashboard-view__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-view__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-view__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
