import { defineStore } from 'pinia'
import { fetchScopedReview, fetchTodayReview, submitReviewRating } from '@/api/modules/review'
import type {
  ReviewCard,
  ReviewLevel,
  ReviewLevelGuidance,
  ReviewPlan,
  ReviewQueue,
  ReviewQueueOption,
  ReviewScope,
  ReviewSummaryItem,
} from '@/types/review'

const emptyCard: ReviewCard = {
  id: 0,
  book_id: 0,
  note_id: 0,
  question: '',
  source: '',
  answer: '',
  tags: [],
  review_count: 0,
  mastery_score: 0,
  last_reviewed_at: '',
  next_review_at: '',
  reason: {
    label: '',
    detail: '',
    next_action: '',
  },
}

const defaultPlan: ReviewPlan = {
  default_daily_goal: 10,
  selected_daily_goal: 10,
  daily_goal_options: [5, 10, 20],
  suggested_today: 0,
  due_count: 0,
  batch_size: 50,
  message: '加载复习计划中...',
}

const defaultLevelGuidance: ReviewLevelGuidance[] = [
  { level: 'low', label: '不会', hint: '更快再次出现' },
  { level: 'medium', label: '模糊记得', hint: '会进入待巩固队列，并安排中等间隔复习' },
  { level: 'high', label: '熟练掌握', hint: '拉长下次复习间隔' },
]

interface ReviewRatingFeedback {
  level: ReviewLevel
  title: string
  message: string
  nextReviewDate: string
  masteryScore: number
  movedToWeak: boolean
}

export const useReviewStore = defineStore('review', {
  state: () => ({
    summary: [] as ReviewSummaryItem[],
    plan: { ...defaultPlan },
    levelGuidance: [...defaultLevelGuidance],
    queueOptions: [] as ReviewQueueOption[],
    cards: [] as ReviewCard[],
    weakCards: [] as ReviewCard[],
    currentIndex: 0,
    completedCount: 0,
    mastery: {
      low: 0,
      medium: 0,
      high: 0,
    },
    answerVisible: false,
    loading: false,
    submitting: false,
    feedbackMessage: '',
    ratingFeedback: null as ReviewRatingFeedback | null,
    dailyGoal: defaultPlan.default_daily_goal,
    queue: 'due' as ReviewQueue,
    skippedCount: 0,
    scope: {
      tag: '',
      book_id: null,
      queue: 'due',
    } as ReviewScope,
  }),
  getters: {
    card(state) {
      return state.cards[state.currentIndex] ?? emptyCard
    },
    total(state) {
      return state.cards.length
    },
    remaining(state) {
      return Math.max(0, state.cards.length - state.completedCount)
    },
    progressText(state): string {
      if (state.cards.length === 0) return '今日暂无复习卡片'
      return `今日卡片 ${Math.min(state.currentIndex + 1, state.cards.length)} / ${state.cards.length}`
    },
    dynamicSummary(state): ReviewSummaryItem[] {
      const reviewed = state.completedCount
      const masteryRate = reviewed
        ? `${Math.round((state.mastery.high / reviewed) * 100)}%`
        : state.summary.find((item) => item.label === '掌握率')?.value ?? '0%'

      const dueItem = state.summary.find((item) => item.label === '待复习')
      const streakItem = state.summary.find((item) => item.label === '连续复习')
      return [
        { label: '待复习', value: dueItem?.value ?? String(Math.max(0, state.cards.length - reviewed)) },
        { label: '已完成', value: String(reviewed) },
        { label: '连续复习', value: streakItem?.value ?? '0 天' },
        { label: '掌握率', value: masteryRate },
      ]
    },
    sessionComplete(state) {
      return state.cards.length > 0 && state.completedCount >= state.cards.length
    },
    weakCompletedCount(state) {
      return state.mastery.low
    },
  },
  actions: {
    async load(filters?: { tag?: string; book_id?: number; daily_goal?: number; queue?: ReviewQueue }) {
      this.loading = true
      try {
        const dailyGoal = filters?.daily_goal ?? this.dailyGoal
        const queue = filters?.queue ?? this.queue
        const params = { ...(filters ?? {}), daily_goal: dailyGoal, queue }
        const data = params.tag || params.book_id
          ? await fetchScopedReview(params)
          : await fetchTodayReview({ daily_goal: dailyGoal, queue })
        this.summary = data.summary
        this.plan = data.plan
        this.dailyGoal = data.plan.selected_daily_goal
        this.levelGuidance = data.level_guidance
        this.queueOptions = data.queue_options
        this.cards = (data.cards.length > 0 ? data.cards : data.card.id ? [data.card] : []).map(normalizeReviewCard)
        this.weakCards = data.weak_cards.map(normalizeReviewCard)
        this.scope = data.scope
        this.queue = data.scope.queue
        this.currentIndex = 0
        this.completedCount = 0
        this.mastery = { low: 0, medium: 0, high: 0 }
        this.skippedCount = 0
        this.answerVisible = false
        this.feedbackMessage = ''
        this.ratingFeedback = null
      } finally {
        this.loading = false
      }
    },
    revealAnswer() {
      this.answerVisible = true
    },
    restartSession() {
      if (!this.cards.length) return
      this.currentIndex = 0
      this.completedCount = 0
      this.mastery = { low: 0, medium: 0, high: 0 }
      this.skippedCount = 0
      this.answerVisible = false
      this.feedbackMessage = '已重新开始当前这组卡片。'
      this.ratingFeedback = null
    },
    async setDailyGoal(goal: number) {
      this.dailyGoal = goal
      await this.load({
        tag: this.scope.tag || undefined,
        book_id: this.scope.book_id ?? undefined,
        daily_goal: goal,
        queue: this.queue,
      })
    },
    async setQueue(queue: ReviewQueue) {
      this.queue = queue
      await this.load({
        tag: this.scope.tag || undefined,
        book_id: this.scope.book_id ?? undefined,
        daily_goal: this.dailyGoal,
        queue,
      })
    },
    skipCurrent() {
      if (!this.cards.length || this.currentIndex >= this.cards.length) return
      this.feedbackMessage = '已跳过这张卡片，本轮不会记录复习结果。'
      this.ratingFeedback = null
      this.answerVisible = false
      this.completedCount += 1
      this.skippedCount += 1
      if (this.currentIndex < this.cards.length - 1) {
        this.currentIndex += 1
      } else {
        this.currentIndex = this.cards.length
      }
    },
    async rateCurrent(level: ReviewLevel) {
      if (!this.cards.length || this.currentIndex >= this.cards.length) return
      this.submitting = true
      const currentCard = this.cards[this.currentIndex]
      let recorded = false
      try {
        const data = await submitReviewRating(currentCard.note_id, level)
        this.summary = data.summary
        this.feedbackMessage = data.progress?.next_review_at
          ? `已记录本次复习，下次复习时间：${data.progress.next_review_at.slice(0, 10)}`
          : '已记录本次复习'
        if (data.progress) {
          this.ratingFeedback = buildRatingFeedback(level, data.progress.mastery_score, data.progress.next_review_at)
        }
        recorded = true
      } finally {
        this.submitting = false
      }

      if (!recorded) return
      if (level === 'low' || level === 'medium') {
        this.addWeakCard(currentCard)
      }
      this.mastery[level] += 1
      this.completedCount += 1
      this.answerVisible = false
      if (this.currentIndex < this.cards.length - 1) {
        this.currentIndex += 1
      } else {
        this.currentIndex = this.cards.length
      }
    },
    addWeakCard(card: ReviewCard) {
      if (this.weakCards.some((item) => item.note_id === card.note_id)) return
      this.weakCards = [card, ...this.weakCards].slice(0, 5)
      this.queueOptions = this.queueOptions.map((option) => (
        option.value === 'weak'
          ? { ...option, count: option.count + 1 }
          : option
      ))
    },
  },
})

function buildRatingFeedback(level: ReviewLevel, masteryScore: number, nextReviewAt: string): ReviewRatingFeedback {
  const nextReviewDate = nextReviewAt ? nextReviewAt.slice(0, 10) : '待系统安排'
  if (level === 'high') {
    return {
      level,
      title: '这张卡片已进入更长复习间隔',
      message: '系统判断你已经比较熟悉这条内容，会把它安排到更远的日期回看。',
      nextReviewDate,
      masteryScore,
      movedToWeak: false,
    }
  }
  if (level === 'medium') {
    return {
      level,
      title: '已加入待巩固队列',
      message: '模糊记得说明这条内容值得近期再碰一次，系统会保留它作为优先巩固对象。',
      nextReviewDate,
      masteryScore,
      movedToWeak: true,
    }
  }
  return {
    level,
    title: '已安排更快回看',
    message: '不会很正常，这张卡片会更快再次出现，帮助你用更短间隔建立记忆。',
    nextReviewDate,
    masteryScore,
    movedToWeak: true,
  }
}

function normalizeReviewCard(card: ReviewCard): ReviewCard {
  return {
    ...emptyCard,
    ...card,
    tags: card.tags ?? [],
    reason: {
      ...emptyCard.reason,
      ...(card.reason ?? {}),
    },
  }
}
