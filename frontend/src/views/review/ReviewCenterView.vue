<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import { useReviewStore } from '@/stores/review'

const route = useRoute()
const router = useRouter()
const reviewStore = useReviewStore()
const { loading, submitting } = storeToRefs(reviewStore)
const summary = computed(() => reviewStore.dynamicSummary.length ? reviewStore.dynamicSummary : reviewStore.summary)
const card = computed(() => reviewStore.card)
const progressText = computed(() => reviewStore.progressText)
const answerVisible = computed(() => reviewStore.answerVisible)
const hasCards = computed(() => reviewStore.total > 0 && reviewStore.completedCount < reviewStore.total)
const feedbackMessage = computed(() => reviewStore.feedbackMessage)
const activeScope = computed(() => reviewStore.scope)
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
  ]
})

async function loadScopedReview() {
  const tag = route.query.tag ? String(route.query.tag) : undefined
  const bookId = route.query.bookId ? Number(route.query.bookId) : undefined
  await reviewStore.load({
    tag,
    book_id: Number.isNaN(bookId) ? undefined : bookId,
  })
}

onMounted(() => {
  void loadScopedReview()
})

watch(
  () => route.query,
  () => {
    void loadScopedReview()
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

function clearScope() {
  void router.push({
    path: '/review',
  })
}
</script>

<template>
  <div class="review-view">
    <section v-loading="loading" class="review-view__summary">
      <AppCard v-for="item in summary" :key="item.label" class="review-view__summary-card">
        <p>{{ item.label }}</p>
        <strong>{{ item.value }}</strong>
      </AppCard>
    </section>

    <AppCard v-loading="loading" class="review-view__card">
      <div v-if="activeScope.tag || activeScope.book_id" class="review-view__scope-tip">
        <div>
          <strong>当前复习范围</strong>
          <p v-if="activeScope.tag">按主题复习：{{ activeScope.tag }}</p>
          <p v-else-if="activeScope.book_id">按单本书复习</p>
        </div>
        <el-button text @click="clearScope">查看全部复习卡片</el-button>
      </div>
      <template v-if="hasCards">
      <p class="review-view__eyebrow">{{ progressText }}</p>
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

      <div class="review-view__actions">
        <el-button round :disabled="submitting" @click="reviewStore.revealAnswer">显示答案</el-button>
        <el-button round :disabled="submitting" @click="jumpToNote">查看原笔记</el-button>
        <el-button round :loading="submitting" :disabled="!answerVisible || submitting" @click="reviewStore.rateCurrent('low')">不会</el-button>
        <el-button round :loading="submitting" :disabled="!answerVisible || submitting" @click="reviewStore.rateCurrent('medium')">模糊记得</el-button>
        <el-button type="primary" round :loading="submitting" :disabled="!answerVisible || submitting" @click="reviewStore.rateCurrent('high')">熟练掌握</el-button>
      </div>
      </template>
      <template v-else>
        <p class="review-view__eyebrow">复习中心</p>
        <h2>今天的复习已经完成了</h2>
        <p class="review-view__source">你可以去书库继续阅读，或者重新同步本地笔记。</p>
      </template>
    </AppCard>
  </div>
</template>

<style scoped lang="scss">
.review-view {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.review-view__summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.review-view__summary-card p {
  margin: 0;
  color: var(--text-tertiary);
}

.review-view__summary-card strong {
  display: inline-block;
  margin-top: 12px;
  font-size: 1.8rem;
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

.review-view__actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
}

@media (max-width: 768px) {
  .review-view__summary,
  .review-view__actions {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
