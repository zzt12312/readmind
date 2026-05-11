<script setup lang="ts">
import type { BookItem } from '@/types/book'
import type { ReviewPlan, ReviewQueue, ReviewQueueOption } from '@/types/review'

defineProps<{
  loading: boolean
  plan: ReviewPlan
  isPresetGoal: boolean
  queue: ReviewQueue
  queueOptions: ReviewQueueOption[]
  bookOptions: BookItem[]
  tagOptions: string[]
}>()

const customGoal = defineModel<number | null>('customGoal', { required: true })
const selectedBookId = defineModel<number | null>('selectedBookId', { required: true })
const selectedTag = defineModel<string>('selectedTag', { required: true })

const emit = defineEmits<{
  setDailyGoal: [goal: number]
  applyCustomGoal: []
  setQueue: [queue: ReviewQueue]
  applyScope: []
}>()
</script>

<template>
  <AppCard v-loading="loading" class="review-plan">
    <div class="review-plan__intro">
      <p class="review-plan__eyebrow">今日复习计划</p>
      <h2>{{ plan.suggested_today }} 张本轮卡片</h2>
      <span class="review-plan__goal-note">当前目标：{{ plan.selected_daily_goal }} 张/天</span>
      <p>{{ plan.message }}</p>
    </div>
    <div class="review-plan__controls">
      <div class="review-plan__control-row">
        <span>本轮强度</span>
        <div class="review-plan__goal-control">
          <div class="review-plan__options" aria-label="可选日目标">
            <button
              v-for="option in plan.daily_goal_options"
              :key="option"
              type="button"
              :class="{ 'is-active': isPresetGoal && option === plan.selected_daily_goal }"
              @click="emit('setDailyGoal', option)"
            >
              {{ option }} 张/天
            </button>
          </div>
          <div class="review-plan__custom-goal">
            <label class="review-plan__custom-goal-field">
              <span>自定义</span>
              <input
                v-model="customGoal"
                type="number"
                min="1"
                max="50"
                step="1"
                placeholder="1-50"
                @keyup.enter="emit('applyCustomGoal')"
              >
              <em>张</em>
            </label>
            <button type="button" class="review-plan__custom-goal-action" @click="emit('applyCustomGoal')">
              应用
            </button>
          </div>
        </div>
      </div>
      <div class="review-plan__control-row">
        <span>复习队列</span>
        <div class="review-plan__queue-options">
          <button
            v-for="option in queueOptions"
            :key="option.value"
            type="button"
            :class="{ 'is-active': option.value === queue }"
            :title="option.description"
            @click="emit('setQueue', option.value)"
          >
            <span>{{ option.label }}</span>
            <strong>{{ option.count }}</strong>
          </button>
        </div>
      </div>
      <div class="review-plan__control-row review-plan__control-row--scope">
        <span>复习范围</span>
        <div class="review-plan__scope-controls">
          <el-select
            v-model="selectedBookId"
            clearable
            filterable
            placeholder="按书复习"
            size="small"
          >
            <el-option
              v-for="book in bookOptions"
              :key="book.id"
              :label="book.title"
              :value="book.id"
            />
          </el-select>
          <el-select
            v-model="selectedTag"
            clearable
            filterable
            placeholder="按主题复习"
            size="small"
          >
            <el-option
              v-for="tag in tagOptions"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
          <el-button round size="small" @click="emit('applyScope')">应用范围</el-button>
        </div>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.review-plan {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(360px, 0.9fr);
  gap: 22px;
  align-items: stretch;
  padding: 22px 24px;
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.08), rgba(197, 131, 76, 0.08)),
    var(--card-bg);
}

.review-plan__intro {
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.review-plan__intro h2 {
  margin: 0 0 6px;
}

.review-plan__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
}

.review-plan__goal-note {
  display: inline-flex;
  width: fit-content;
  margin-bottom: 10px;
  padding: 5px 9px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--text-secondary);
  font-size: 0.86rem;
  font-weight: 700;
}

.review-plan__intro p:last-child {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.review-plan__controls {
  display: grid;
  gap: 10px;
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 20px;
  background: rgba(255, 253, 249, 0.68);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.review-plan__control-row {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
}

.review-plan__control-row--scope {
  align-items: start;
}

.review-plan__control-row > span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.review-plan__goal-control {
  display: grid;
  gap: 10px;
}

.review-plan__options,
.review-plan__queue-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-start;
}

.review-plan__scope-controls {
  display: grid;
  grid-template-columns: minmax(160px, 1fr) minmax(140px, 0.78fr) auto;
  gap: 8px;
  align-items: center;
}

.review-plan__scope-controls :deep(.el-select) {
  min-width: 0;
}

.review-plan__options button,
.review-plan__queue-options button {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border: 1px solid rgba(216, 207, 191, 0.8);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.9);
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 700;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    background 0.16s ease;
}

.review-plan__queue-options strong {
  min-width: 1.5em;
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.1);
  color: inherit;
  font-size: 0.78rem;
}

.review-plan__options button:hover,
.review-plan__options button.is-active,
.review-plan__queue-options button:hover,
.review-plan__queue-options button.is-active {
  transform: translateY(-1px);
  border-color: rgba(47, 93, 80, 0.35);
  background: var(--brand-primary);
  color: #fff;
}

.review-plan__queue-options button.is-active strong,
.review-plan__queue-options button:hover strong {
  background: rgba(255, 255, 255, 0.18);
}

.review-plan__custom-goal {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  width: fit-content;
  padding: 6px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.72);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.68);
}

.review-plan__custom-goal-field {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 2px 0 8px;
  color: var(--text-tertiary);
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.review-plan__custom-goal-field input {
  width: 58px;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text-primary);
  font: inherit;
  font-size: 0.92rem;
  font-weight: 800;
  text-align: center;
}

.review-plan__custom-goal-field input::placeholder {
  color: rgba(102, 93, 82, 0.42);
}

.review-plan__custom-goal-field input::-webkit-inner-spin-button,
.review-plan__custom-goal-field input::-webkit-outer-spin-button {
  margin: 0;
  appearance: none;
}

.review-plan__custom-goal-field em {
  color: var(--text-secondary);
  font-style: normal;
  font-weight: 700;
}

.review-plan__custom-goal-action {
  padding: 7px 12px;
  border: 0;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-size: 0.84rem;
  font-weight: 800;
  transition:
    transform 0.16s ease,
    box-shadow 0.16s ease;
}

.review-plan__custom-goal-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(47, 93, 80, 0.18);
}

@media (max-width: 768px) {
  .review-plan {
    align-items: flex-start;
    grid-template-columns: 1fr;
  }

  .review-plan__controls,
  .review-plan__scope-controls {
    grid-template-columns: 1fr;
    min-width: 0;
    width: 100%;
  }

  .review-plan__control-row {
    grid-template-columns: 1fr;
  }
}
</style>
