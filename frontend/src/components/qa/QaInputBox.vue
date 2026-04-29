<script setup lang="ts">
const draft = defineModel<string>('draft', { required: true })
const scope = defineModel<'all-books' | 'current-book'>('scope', { required: true })

defineProps<{
  loading: boolean
  stopped: boolean
  hasMessages: boolean
  bookId?: number
  books?: Array<{
    id: number
    title: string
    author?: string
    category?: string
  }>
}>()

defineEmits<{
  ask: []
  regenerate: []
  stop: []
  scopeChange: [scope: 'all-books' | 'current-book']
  bookChange: [bookId: number | undefined]
}>()
</script>

<template>
  <div class="qa-input-box">
    <div class="qa-input-box__prompt">
      <strong>问问签签</strong>
      <span>她会先从你的笔记里找证据，再整理成回答。</span>
    </div>
    <div v-if="scope === 'current-book'" class="qa-input-box__book-picker">
      <span>当前只翻这本书</span>
      <el-select
        :model-value="bookId"
        filterable
        clearable
        placeholder="选择你要提问的书"
        @update:model-value="$emit('bookChange', $event as number | undefined)"
      >
        <el-option
          v-for="book in books || []"
          :key="book.id"
          :label="book.title"
          :value="book.id"
        >
          <div class="qa-input-box__book-option">
            <span>{{ book.title }}</span>
            <small>{{ book.author || book.category || '未分类' }}</small>
          </div>
        </el-option>
      </el-select>
    </div>
    <el-input v-model="draft" type="textarea" :rows="4" placeholder="例如：签签，帮我总结最近关于长期主义的笔记" />
    <div class="qa-input-box__actions">
      <el-select
        v-model="scope"
        placeholder="检索范围"
        style="width: 180px"
        @change="$emit('scopeChange', scope)"
      >
        <el-option label="当前书籍" value="current-book" />
        <el-option label="全部书籍" value="all-books" />
      </el-select>
      <el-button round :disabled="!hasMessages || loading" @click="$emit('regenerate')">重新生成</el-button>
      <el-button round :disabled="!loading" @click="$emit('stop')">停止生成</el-button>
      <el-button type="primary" round :loading="loading" @click="$emit('ask')">发送问题</el-button>
    </div>
    <p v-if="stopped" class="qa-input-box__status-tip">本轮回答已手动停止，你可以继续追问或点击“重新生成”。</p>
  </div>
</template>

<style scoped lang="scss">
.qa-input-box {
  margin-top: 24px;
  padding: 16px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 22px;
  background:
    radial-gradient(circle at 0% 0%, rgba(47, 93, 80, 0.08), transparent 34%),
    rgba(255, 253, 249, 0.9);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.qa-input-box__prompt {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
}

.qa-input-box__prompt strong {
  color: var(--brand-primary);
}

.qa-input-box__prompt span {
  color: var(--text-tertiary);
  font-size: 0.84rem;
}

.qa-input-box__book-picker {
  padding: 10px 12px;
  display: grid;
  grid-template-columns: 132px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 16px;
  background: rgba(47, 93, 80, 0.06);
}

.qa-input-box__book-picker > span {
  color: var(--brand-primary);
  font-size: 0.84rem;
  font-weight: 900;
}

.qa-input-box__book-option {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.qa-input-box__book-option small {
  color: var(--text-tertiary);
}

.qa-input-box :deep(.el-textarea__inner) {
  min-height: 112px;
  padding: 14px 16px;
  border-color: rgba(216, 207, 191, 0.72);
  border-radius: 20px;
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.08) 0 5px, transparent 5px),
    rgba(255, 253, 249, 0.96);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.78);
  color: var(--text-primary);
  line-height: 1.7;
}

.qa-input-box :deep(.el-textarea__inner:focus) {
  border-color: rgba(47, 93, 80, 0.32);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.78),
    0 0 0 3px rgba(47, 93, 80, 0.08);
}

.qa-input-box :deep(.el-textarea__inner::placeholder) {
  color: rgba(124, 111, 91, 0.72);
}

.qa-input-box__actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.qa-input-box__status-tip {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.84rem;
}

@media (max-width: 768px) {
  .qa-input-box__prompt,
  .qa-input-box__actions {
    flex-direction: column;
  }

  .qa-input-box__book-picker {
    grid-template-columns: 1fr;
  }
}
</style>
