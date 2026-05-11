<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import ReviewCompletionCard from '@/components/review/ReviewCompletionCard.vue'
import ReviewPlanCockpit from '@/components/review/ReviewPlanCockpit.vue'
import ReviewSummaryGrid from '@/components/review/ReviewSummaryGrid.vue'
import ReviewWeakCardsPanel from '@/components/review/ReviewWeakCardsPanel.vue'
import { buildReviewCompletionMascotCue, buildReviewRatingMascotCue } from '@/constants/mascotMessages'
import { useBooksStore } from '@/stores/books'
import { useReviewStore } from '@/stores/review'
import type { ReviewQueue } from '@/types/review'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()
const reviewStore = useReviewStore()
const { loading, submitting } = storeToRefs(reviewStore)
const customGoal = ref<number | null>(null)
const selectedBookId = ref<number | null>(null)
const selectedTag = ref('')
const summary = computed(() => reviewStore.dynamicSummary.length ? reviewStore.dynamicSummary : reviewStore.summary)
const card = computed(() => reviewStore.card)
const plan = computed(() => reviewStore.plan)
const progressText = computed(() => reviewStore.progressText)
const answerVisible = computed(() => reviewStore.answerVisible)
const hasCards = computed(() => reviewStore.total > 0 && reviewStore.completedCount < reviewStore.total)
const sessionComplete = computed(() => reviewStore.sessionComplete)
const feedbackMessage = computed(() => reviewStore.feedbackMessage)
const ratingFeedback = computed(() => reviewStore.ratingFeedback)
const activeScope = computed(() => reviewStore.scope)
const queueOptions = computed(() => reviewStore.queueOptions)
const weakCards = computed(() => reviewStore.weakCards)
const bookOptions = computed(() =>
  [...booksStore.items].sort((left, right) => left.title.localeCompare(right.title, 'zh-Hans-CN')),
)
const tagOptions = computed(() => {
  const tags = new Set<string>()
  ;[...reviewStore.cards, ...reviewStore.weakCards].forEach((item) => {
    item.tags.forEach((tag) => {
      if (tag.trim()) tags.add(tag)
    })
  })
  return [...tags].sort((left, right) => left.localeCompare(right, 'zh-Hans-CN'))
})
const activeBookTitle = computed(() => {
  if (!activeScope.value.book_id) return ''
  return booksStore.findById(activeScope.value.book_id)?.title ?? `书籍 #${activeScope.value.book_id}`
})
const activeQueueOption = computed(() => (
  queueOptions.value.find((option) => option.value === reviewStore.queue)
))
const isPresetGoal = computed(() => plan.value.daily_goal_options.includes(plan.value.selected_daily_goal))
const completionStats = computed(() => [
  { label: '完成卡片', value: `${reviewStore.completedCount} 张` },
  { label: '薄弱卡片', value: `${reviewStore.weakCompletedCount} 张` },
  { label: '跳过', value: `${reviewStore.skippedCount} 张` },
])
const guidanceByLevel = computed(() => Object.fromEntries(
  reviewStore.levelGuidance.map((item) => [item.level, item.hint]),
))
const reviewMeta = computed(() => {
  if (!card.value.id) {
    return []
  }
  return [
    card.value.review_count
      ? `已复习 ${card.value.review_count} 次`
      : '新卡片',
    card.value.mastery_score >= 2
      ? '掌握度较高'
      : card.value.mastery_score === 1
        ? '还需要再巩固'
        : '建议重点回顾',
    card.value.next_review_at
      ? `计划下次复习：${card.value.next_review_at.slice(0, 10)}`
      : '评分后自动安排下次复习',
  ]
})
const mascotCue = computed(() => {
  if (sessionComplete.value) {
    return buildReviewCompletionMascotCue(reviewStore.completedCount, reviewStore.total)
  }
  return buildReviewRatingMascotCue(ratingFeedback.value?.level)
})

async function loadScopedReview() {
  const tag = route.query.tag ? String(route.query.tag) : undefined
  const bookId = route.query.bookId ? Number(route.query.bookId) : undefined
  const dailyGoal = route.query.goal ? Number(route.query.goal) : undefined
  const queue = route.query.queue ? String(route.query.queue) as ReviewQueue : undefined
  selectedBookId.value = Number.isNaN(bookId) ? null : bookId ?? null
  selectedTag.value = tag ?? ''
  await reviewStore.load({
    tag,
    book_id: Number.isNaN(bookId) ? undefined : bookId,
    daily_goal: Number.isNaN(dailyGoal) ? undefined : dailyGoal,
    queue,
  })
}

onMounted(() => {
  void (async () => {
    if (booksStore.items.length === 0) {
      await booksStore.load()
    }
    await loadScopedReview()
  })()
})

watch(
  () => route.query,
  () => {
    void loadScopedReview()
  },
)

watch(
  () => plan.value.selected_daily_goal,
  (goal) => {
    customGoal.value = plan.value.daily_goal_options.includes(goal) ? null : goal
  },
)

function jumpToNote() {
  if (!card.value.book_id || !card.value.note_id) return
  void router.push({
    path: '/notes',
    query: {
      bookId: String(card.value.book_id),
      noteId: String(card.value.note_id),
    },
  })
}

function reviewByTag(tag: string) {
  void router.push({
    path: '/review',
    query: {
      tag,
    },
  })
}

function applyReviewScope() {
  const query = {
    ...(selectedTag.value ? { tag: selectedTag.value } : {}),
    ...(selectedBookId.value ? { bookId: String(selectedBookId.value) } : {}),
    ...(route.query.goal ? { goal: String(route.query.goal) } : {}),
    ...(reviewStore.queue !== 'due' ? { queue: reviewStore.queue } : {}),
  }
  void router.push({
    path: '/review',
    query,
  })
}

function askAboutWeakCards() {
  const weakSource = weakCards.value[0]?.source || card.value.source || '今天复习的内容'
  void router.push({
    path: '/qa',
    query: {
      preset: `帮我总结一下「${weakSource}」里我最需要巩固的观点，并给出可复习的问题。`,
      ...(weakCards.value[0]?.book_id || card.value.book_id
        ? { bookId: String(weakCards.value[0]?.book_id || card.value.book_id), scope: 'current-book' }
        : {}),
    },
  })
}

function clearScope() {
  selectedBookId.value = null
  selectedTag.value = ''
  void router.push({
    path: '/review',
  })
}

function setDailyGoal(goal: number, options?: { keepCustom?: boolean }) {
  if (!options?.keepCustom) {
    customGoal.value = null
  }
  void router.push({
    path: '/review',
    query: {
      ...(activeScope.value.tag ? { tag: activeScope.value.tag } : {}),
      ...(activeScope.value.book_id ? { bookId: String(activeScope.value.book_id) } : {}),
      ...(reviewStore.queue !== 'due' ? { queue: reviewStore.queue } : {}),
      goal: String(goal),
    },
  })
}

function applyCustomGoal() {
  const normalizedGoal = Number(customGoal.value)
  if (!Number.isFinite(normalizedGoal)) return
  const goal = Math.min(50, Math.max(1, Math.round(normalizedGoal)))
  customGoal.value = goal
  setDailyGoal(goal, { keepCustom: true })
}

async function setQueue(queue: ReviewQueue) {
  const query = {
    ...(activeScope.value.tag ? { tag: activeScope.value.tag } : {}),
    ...(activeScope.value.book_id ? { bookId: String(activeScope.value.book_id) } : {}),
    ...(route.query.goal ? { goal: String(route.query.goal) } : {}),
    ...(queue !== 'due' ? { queue } : {}),
  }

  await reviewStore.setQueue(queue)

  void router.replace({
    path: '/review',
    query,
  })
}
</script>

<template>
  <div class="review-view">
    <ReviewSummaryGrid :loading="loading" :summary="summary" />

    <ReviewPlanCockpit
      v-model:custom-goal="customGoal"
      v-model:selected-book-id="selectedBookId"
      v-model:selected-tag="selectedTag"
      :loading="loading"
      :plan="plan"
      :is-preset-goal="isPresetGoal"
      :queue="reviewStore.queue"
      :queue-options="queueOptions"
      :book-options="bookOptions"
      :tag-options="tagOptions"
      @set-daily-goal="setDailyGoal"
      @apply-custom-goal="applyCustomGoal"
      @set-queue="setQueue"
      @apply-scope="applyReviewScope"
    />

    <ReviewCompletionCard
      v-if="sessionComplete"
      :stats="completionStats"
      @restart="reviewStore.restartSession"
      @weak="setQueue('weak')"
      @ask="askAboutWeakCards"
    />

    <AppCard v-if="!sessionComplete" v-loading="loading" class="review-view__card">
      <div v-if="activeScope.tag || activeScope.book_id" class="review-view__scope-tip">
        <div>
          <strong>当前复习范围</strong>
          <p v-if="activeScope.tag">按主题复习：{{ activeScope.tag }}</p>
          <p v-else-if="activeScope.book_id">按单本书复习：{{ activeBookTitle }}</p>
        </div>
        <el-button text @click="clearScope">查看全部复习卡片</el-button>
      </div>
      <template v-if="hasCards">
        <p class="review-view__eyebrow">{{ progressText }}</p>
        <div v-if="activeQueueOption" class="review-view__queue-hint">
          正在复习：{{ activeQueueOption.label }} · 共 {{ activeQueueOption.count }} 张可选
          <small>{{ activeQueueOption.description }}</small>
        </div>
        <div v-if="card.reason.label" class="review-view__reason">
          <span>{{ card.reason.label }}</span>
          <div>
            <strong>为什么今天复习它</strong>
            <p>{{ card.reason.detail }}</p>
            <em>{{ card.reason.next_action }}</em>
          </div>
        </div>
        <h2>{{ card.question }}</h2>
        <p class="review-view__source">来源：{{ card.source }}</p>
        <div class="review-view__meta">
          <span v-for="item in reviewMeta" :key="item">{{ item }}</span>
        </div>
        <div v-if="card.tags.length" class="review-view__tags">
          <el-tag
            v-for="tag in card.tags.slice(0, 6)"
            :key="tag"
            round
            effect="plain"
            @click="reviewByTag(tag)"
          >
            {{ tag }}
          </el-tag>
        </div>

        <div class="review-view__answer" :class="{ 'is-hidden': !answerVisible }">
          <strong>参考答案</strong>
          <p v-if="answerVisible">{{ card.answer }}</p>
          <p v-else>先回想一下，再点击“显示答案”。</p>
        </div>

        <p v-if="feedbackMessage" class="review-view__feedback">{{ feedbackMessage }}</p>
        <div
          v-if="ratingFeedback"
          class="review-view__rating-feedback"
          :class="`is-${ratingFeedback.level}`"
        >
          <div>
            <strong>{{ ratingFeedback.title }}</strong>
            <p>{{ ratingFeedback.message }}</p>
          </div>
          <div class="review-view__rating-feedback-meta">
            <span>掌握度 {{ ratingFeedback.masteryScore }}</span>
            <span>下次 {{ ratingFeedback.nextReviewDate }}</span>
            <span v-if="ratingFeedback.movedToWeak">待巩固</span>
          </div>
          <MascotBubble
            class="review-view__rating-mascot"
            :mood="mascotCue.mood"
            :message="mascotCue.message"
            :celebrating="mascotCue.celebrating"
            compact
          />
        </div>

        <div class="review-view__actions">
          <el-button round :disabled="submitting" @click="reviewStore.revealAnswer">显示答案</el-button>
          <el-button round :disabled="submitting" @click="jumpToNote">查看原笔记</el-button>
          <el-button round :disabled="submitting" @click="reviewStore.skipCurrent">跳过这张</el-button>
          <el-tooltip :content="guidanceByLevel.low" placement="top">
            <el-button round :loading="submitting" :disabled="!answerVisible || submitting" @click="reviewStore.rateCurrent('low')">不会</el-button>
          </el-tooltip>
          <el-tooltip :content="guidanceByLevel.medium" placement="top">
            <el-button round :loading="submitting" :disabled="!answerVisible || submitting" @click="reviewStore.rateCurrent('medium')">模糊记得</el-button>
          </el-tooltip>
          <el-tooltip :content="guidanceByLevel.high" placement="top">
            <el-button type="primary" round :loading="submitting" :disabled="!answerVisible || submitting" @click="reviewStore.rateCurrent('high')">熟练掌握</el-button>
          </el-tooltip>
        </div>
      </template>
      <template v-else>
        <p class="review-view__eyebrow">复习中心</p>
        <h2>今天的复习已经完成了</h2>
        <p class="review-view__source">你可以去书库继续阅读，或者重新同步本地笔记。</p>
        <MascotBubble
          class="review-view__completion-mascot"
          :mood="mascotCue.mood"
          :message="mascotCue.message"
          :celebrating="mascotCue.celebrating"
          compact
        />
      </template>
    </AppCard>

    <ReviewWeakCardsPanel :cards="weakCards" @review-weak="setQueue('weak')" />
  </div>
</template>

<style scoped lang="scss">
.review-view {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.review-view__card {
  padding: 28px;
}

.review-view__scope-tip {
  margin-bottom: 18px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.review-view__scope-tip p {
  margin: 6px 0 0;
  color: var(--text-secondary);
}

.review-view__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
}

.review-view__card h2 {
  margin: 0 0 10px;
}

.review-view__queue-hint {
  display: inline-flex;
  flex-direction: column;
  gap: 2px;
  margin: 0 0 12px;
  padding: 8px 12px;
  border-radius: 14px;
  background: rgba(197, 131, 76, 0.12);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 700;
}

.review-view__queue-hint small {
  color: var(--text-tertiary);
  font-size: 0.82rem;
  font-weight: 500;
  line-height: 1.45;
}

.review-view__reason {
  display: flex;
  gap: 13px;
  align-items: flex-start;
  margin: 0 0 18px;
  padding: 14px 16px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 18px;
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.72)),
    var(--bg-card);
}

.review-view__reason > span {
  flex: 0 0 auto;
  padding: 7px 10px;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  font-size: 0.78rem;
  font-weight: 900;
  white-space: nowrap;
}

.review-view__reason strong,
.review-view__reason p,
.review-view__reason em {
  display: block;
}

.review-view__reason strong {
  margin-bottom: 5px;
  color: var(--text-primary);
}

.review-view__reason p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.review-view__reason em {
  margin-top: 7px;
  color: var(--brand-primary);
  font-size: 0.86rem;
  font-style: normal;
  font-weight: 800;
  line-height: 1.5;
}

.review-view__source {
  margin: 0 0 24px;
  color: var(--text-tertiary);
}

.review-view__meta {
  margin: 0 0 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.review-view__meta span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.review-view__tags {
  margin: 0 0 18px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.review-view__answer {
  padding: 18px;
  border-radius: var(--radius-sm);
  background: var(--bg-soft);
}

.review-view__answer.is-hidden {
  background: rgba(47, 93, 80, 0.08);
}

.review-view__answer p {
  margin: 10px 0 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.review-view__feedback {
  margin: 16px 0 0;
  color: var(--brand-primary);
}

.review-view__rating-feedback {
  margin-top: 14px;
  padding: 15px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  border: 1px solid rgba(47, 93, 80, 0.14);
  border-radius: 18px;
  background:
    radial-gradient(circle at 8% 0%, rgba(47, 93, 80, 0.12), transparent 38%),
    rgba(255, 253, 249, 0.78);
}

.review-view__rating-feedback.is-low {
  border-color: rgba(191, 97, 74, 0.2);
  background:
    radial-gradient(circle at 8% 0%, rgba(191, 97, 74, 0.12), transparent 38%),
    rgba(255, 253, 249, 0.78);
}

.review-view__rating-feedback.is-medium {
  border-color: rgba(197, 139, 92, 0.24);
  background:
    radial-gradient(circle at 8% 0%, rgba(197, 139, 92, 0.14), transparent 38%),
    rgba(255, 253, 249, 0.78);
}

.review-view__rating-feedback strong {
  color: var(--brand-primary);
}

.review-view__rating-feedback p {
  margin: 6px 0 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.review-view__rating-feedback-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.review-view__rating-feedback-meta span {
  padding: 7px 9px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 800;
  white-space: nowrap;
}

.review-view__rating-mascot {
  grid-column: 1 / -1;
}

.review-view__completion-mascot {
  max-width: 520px;
  margin-top: 16px;
}

.review-view__actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .review-view__actions {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .review-view__rating-feedback {
    grid-template-columns: 1fr;
  }

  .review-view__rating-feedback-meta {
    justify-content: flex-start;
  }

}
</style>
