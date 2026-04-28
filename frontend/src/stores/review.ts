import { defineStore } from 'pinia'
import { fetchScopedReview, fetchTodayReview, submitReviewRating } from '@/api/modules/review'
import type { ReviewCard, ReviewLevel, ReviewScope, ReviewSummaryItem } from '@/types/review'

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
}

export const useReviewStore = defineStore('review', {
  state: () => ({
    summary: [] as ReviewSummaryItem[],
    cards: [] as ReviewCard[],
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
    scope: {
      tag: '',
      book_id: null,
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
  },
  actions: {
    async load(filters?: { tag?: string; book_id?: number }) {
      this.loading = true
      try {
        const data = filters?.tag || filters?.book_id ? await fetchScopedReview(filters) : await fetchTodayReview()
        this.summary = data.summary
        this.cards = data.cards.length > 0 ? data.cards : data.card.id ? [data.card] : []
        this.scope = data.scope
        this.currentIndex = 0
        this.completedCount = 0
        this.mastery = { low: 0, medium: 0, high: 0 }
        this.answerVisible = false
        this.feedbackMessage = ''
      } finally {
        this.loading = false
      }
    },
    revealAnswer() {
      this.answerVisible = true
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
        recorded = true
      } finally {
        this.submitting = false
      }

      if (!recorded) return
      this.mastery[level] += 1
      this.completedCount += 1
      this.answerVisible = false
      if (this.currentIndex < this.cards.length - 1) {
        this.currentIndex += 1
      } else {
        this.currentIndex = this.cards.length
      }
    },
  },
})
