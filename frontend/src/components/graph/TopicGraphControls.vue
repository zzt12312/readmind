<script setup lang="ts">
import type { TopicGraphBookOption, TopicGraphFilterOption } from '@/types/insights'

defineProps<{
  activeFilterCount: number
  availableModes: TopicGraphFilterOption[]
  availableCategories: string[]
  filteredBooks: TopicGraphBookOption[]
  availableTimeScopes: TopicGraphFilterOption[]
}>()

const selectedMode = defineModel<'category' | 'topic'>('selectedMode', { required: true })
const selectedCategory = defineModel<string>('selectedCategory', { required: true })
const selectedBookId = defineModel<number | undefined>('selectedBookId', { required: true })
const selectedTimeScope = defineModel<string>('selectedTimeScope', { required: true })

const emit = defineEmits<{
  categoryChange: []
  reset: []
  reload: []
}>()
</script>

<template>
  <AppCard class="topic-graph-controls">
    <div class="topic-graph-controls__glow" aria-hidden="true" />
    <div class="topic-graph-controls__header">
      <div>
        <p>Graph Controls</p>
        <h3>图谱筛选</h3>
      </div>
      <div class="topic-graph-controls__filter-status" :class="{ 'is-active': activeFilterCount }">
        <span>{{ activeFilterCount ? `${activeFilterCount} 个筛选` : '全量视图' }}</span>
        <strong>{{ selectedMode === 'category' ? '领域聚类' : '主题共现' }}</strong>
      </div>
    </div>
    <div class="topic-graph-controls__grid">
      <label class="topic-graph-controls__field is-mode">
        <span>分析方式</span>
        <el-segmented v-model="selectedMode" :options="availableModes" />
      </label>
      <label class="topic-graph-controls__field">
        <span>分类</span>
        <el-select
          v-model="selectedCategory"
          clearable
          placeholder="全部分类"
          @change="emit('categoryChange')"
        >
          <el-option v-for="category in availableCategories" :key="category" :label="category" :value="category" />
        </el-select>
      </label>
      <label class="topic-graph-controls__field">
        <span>书籍</span>
        <el-select
          v-model="selectedBookId"
          clearable
          filterable
          placeholder="全部书籍"
        >
          <el-option v-for="book in filteredBooks" :key="book.id" :label="book.title" :value="book.id" />
        </el-select>
      </label>
      <label class="topic-graph-controls__field">
        <span>时间</span>
        <el-select v-model="selectedTimeScope">
          <el-option
            v-for="option in availableTimeScopes"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
      </label>
      <div class="topic-graph-controls__actions">
        <el-button round @click="emit('reset')">重置</el-button>
        <el-button type="primary" round @click="emit('reload')">重新分析</el-button>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.topic-graph-controls {
  position: relative;
  overflow: hidden;
  padding: 22px;
  border-color: rgba(216, 207, 191, 0.72);
  border-radius: 28px;
  background:
    radial-gradient(circle at 8% 0%, rgba(47, 93, 80, 0.14), transparent 28%),
    radial-gradient(circle at 92% 16%, rgba(197, 139, 92, 0.16), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(248, 242, 232, 0.92));
}

.topic-graph-controls::before {
  content: '';
  position: absolute;
  inset: 12px;
  border: 1px solid rgba(255, 253, 249, 0.74);
  border-radius: 24px;
  pointer-events: none;
}

.topic-graph-controls__glow {
  position: absolute;
  right: -48px;
  top: -76px;
  width: 190px;
  height: 190px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(197, 139, 92, 0.18), transparent 68%);
  pointer-events: none;
}

.topic-graph-controls__header {
  position: relative;
  z-index: 1;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.topic-graph-controls__header p {
  margin: 0 0 4px;
  color: var(--brand-accent);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.topic-graph-controls__header h3 {
  margin: 0;
  color: var(--brand-primary);
}

.topic-graph-controls__filter-status {
  min-width: 136px;
  padding: 9px 12px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.72);
  box-shadow: 0 10px 24px rgba(47, 93, 80, 0.08);
  text-align: right;
}

.topic-graph-controls__filter-status span {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.76rem;
  font-weight: 800;
}

.topic-graph-controls__filter-status strong {
  display: block;
  margin-top: 3px;
  color: var(--brand-primary);
  font-size: 0.95rem;
}

.topic-graph-controls__filter-status.is-active {
  border-color: rgba(47, 93, 80, 0.24);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.86)),
    rgba(255, 253, 249, 0.86);
}

.topic-graph-controls__grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(220px, 1.1fr) minmax(150px, 0.8fr) minmax(220px, 1fr) minmax(150px, 0.7fr) auto;
  gap: 14px;
  align-items: end;
}

.topic-graph-controls__field {
  min-width: 0;
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.5);
  border-radius: 20px;
  background: rgba(255, 253, 249, 0.62);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.62);
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.topic-graph-controls__field > span {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.03em;
}

.topic-graph-controls__field :deep(.el-select),
.topic-graph-controls__field :deep(.el-segmented) {
  width: 100%;
}

.topic-graph-controls__field :deep(.el-select__wrapper),
.topic-graph-controls__field :deep(.el-segmented) {
  min-height: 42px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.92);
  box-shadow: none;
}

.topic-graph-controls__field :deep(.el-select__wrapper) {
  border: 1px solid rgba(216, 207, 191, 0.66);
}

.topic-graph-controls__field :deep(.el-select__wrapper.is-focused) {
  border-color: rgba(47, 93, 80, 0.34);
  box-shadow: 0 0 0 3px rgba(47, 93, 80, 0.08);
}

.topic-graph-controls__field :deep(.el-segmented) {
  padding: 3px;
  border: 1px solid rgba(216, 207, 191, 0.66);
  border-radius: 999px;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(248, 242, 232, 0.76));
}

.topic-graph-controls__field :deep(.el-segmented__group) {
  gap: 3px;
}

.topic-graph-controls__field :deep(.el-segmented__item) {
  border-radius: 999px;
  color: var(--text-secondary);
  font-weight: 800;
  transition:
    color 0.18s ease,
    transform 0.18s ease,
    background 0.18s ease;
}

.topic-graph-controls__field :deep(.el-segmented__item:hover:not(.is-selected)) {
  background: rgba(47, 93, 80, 0.06);
  color: var(--brand-primary);
  transform: translateY(-1px);
}

.topic-graph-controls__field :deep(.el-segmented__item-label) {
  padding-inline: 8px;
}

.topic-graph-controls__field :deep(.el-segmented__item-selected) {
  top: 2px;
  bottom: 2px;
  height: auto;
  border-radius: 999px;
  background:
    radial-gradient(circle at 18% 10%, rgba(255, 253, 249, 0.42), transparent 36%),
    linear-gradient(135deg, rgba(47, 93, 80, 0.9), rgba(76, 126, 109, 0.84));
  color: #fffdf9;
  box-shadow:
    0 8px 18px rgba(47, 93, 80, 0.14),
    inset 0 1px 0 rgba(255, 253, 249, 0.28);
}

.topic-graph-controls__actions {
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.46);
  border-radius: 20px;
  background: rgba(255, 253, 249, 0.5);
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.topic-graph-controls__actions :deep(.el-button) {
  min-height: 42px;
  padding-inline: 18px;
  font-weight: 900;
}

.topic-graph-controls__actions :deep(.el-button--primary) {
  border-color: transparent;
  background:
    linear-gradient(135deg, var(--brand-primary), #447967);
  box-shadow: 0 12px 26px rgba(47, 93, 80, 0.18);
}

.topic-graph-controls__actions :deep(.el-button:not(.el-button--primary)) {
  border-color: rgba(216, 207, 191, 0.72);
  background: rgba(255, 253, 249, 0.86);
  color: var(--text-secondary);
}

@media (max-width: 1180px) {
  .topic-graph-controls__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .topic-graph-controls__actions {
    justify-content: flex-start;
  }
}
</style>
