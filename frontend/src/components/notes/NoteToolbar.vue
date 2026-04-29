<script setup lang="ts">
import AppSearchInput from '@/components/base/AppSearchInput.vue'
import type { NoteFilters } from '@/types/note'

const keyword = defineModel<string>('keyword', { required: true })
const searchScope = defineModel<'current-book' | 'all-books'>('searchScope', { required: true })
const selectedCategory = defineModel<string>('category', { required: true })
const selectedTag = defineModel<string>('tag', { required: true })
const selectedChapter = defineModel<string>('chapter', { required: true })
const selectedSort = defineModel<string>('sort', { required: true })

const props = defineProps<{
  filters: NoteFilters
  hasActiveFilters: boolean
  canShowAll: boolean
  currentBookTitle?: string
}>()

const emit = defineEmits<{
  submit: []
  reset: []
  showAll: []
  refreshInsight: []
  askCurrentBook: []
}>()

function toggleTag(tag: string) {
  selectedTag.value = selectedTag.value === tag ? '' : tag
  emit('submit')
}
</script>

<template>
  <div class="note-toolbar">
    <div class="note-toolbar__top">
      <div class="note-toolbar__search-wrap">
        <div class="note-toolbar__search-row">
          <AppSearchInput v-model="keyword" class="note-toolbar__search" @submit="$emit('submit')" />
          <div class="note-toolbar__scope-inline" aria-label="搜索范围">
            <button
              type="button"
              :class="{ 'is-active': searchScope === 'current-book' }"
              @click="searchScope = 'current-book'; $emit('submit')"
            >
              当前书
            </button>
            <button
              type="button"
              :class="{ 'is-active': searchScope === 'all-books' }"
              @click="searchScope = 'all-books'; $emit('submit')"
            >
              全部书籍
            </button>
          </div>
        </div>
      </div>
      <div class="note-toolbar__primary-actions">
        <el-button type="primary" round @click="$emit('submit')">搜索</el-button>
        <el-button v-if="hasActiveFilters" round @click="$emit('reset')">重置</el-button>
      </div>
    </div>

    <div class="note-toolbar__filters">
      <div class="note-toolbar__selects">
        <el-select v-model="selectedCategory" clearable placeholder="分类" @change="$emit('submit')">
          <el-option v-for="category in filters.categories" :key="category" :label="category" :value="category" />
        </el-select>
        <el-select v-model="selectedTag" clearable placeholder="标签" @change="$emit('submit')">
          <el-option v-for="tag in filters.tags" :key="tag" :label="tag" :value="tag" />
        </el-select>
        <el-select v-model="selectedChapter" clearable placeholder="章节" @change="$emit('submit')">
          <el-option v-for="chapter in filters.chapters" :key="chapter" :label="chapter" :value="chapter" />
        </el-select>
        <el-select v-model="selectedSort" placeholder="排序" @change="$emit('submit')">
          <el-option label="默认排序" value="relevance" />
          <el-option label="时间从新到旧" value="time_desc" />
          <el-option label="时间从旧到新" value="time_asc" />
          <el-option label="内容较长优先" value="length_desc" />
        </el-select>
      </div>
      <div class="note-toolbar__secondary-actions">
        <el-button v-if="currentBookTitle" round @click="$emit('askCurrentBook')">问这本书</el-button>
        <el-button v-if="canShowAll" round @click="$emit('showAll')">查看全部</el-button>
        <el-button round @click="$emit('refreshInsight')">AI 再整理</el-button>
      </div>
    </div>

    <div v-if="props.filters.tags.length" class="note-toolbar__quick-tags">
      <span>热门标签</span>
      <button
        v-for="tag in props.filters.tags.slice(0, 10)"
        :key="tag"
        type="button"
        :class="{ 'is-active': selectedTag === tag }"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.note-toolbar {
  display: grid;
  gap: 12px;
  padding: 16px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 253, 249, 0.92), rgba(251, 248, 242, 0.86)),
    var(--bg-card);
  box-shadow: var(--shadow-sm);
}

.note-toolbar__top,
.note-toolbar__filters {
  display: grid;
  gap: 14px;
}

.note-toolbar__top {
  grid-template-columns: minmax(300px, 1fr) auto;
  align-items: center;
}

.note-toolbar__filters {
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
}

.note-toolbar__search-wrap {
  min-width: 0;
}

.note-toolbar__quick-tags > span {
  margin: 0 0 8px 4px;
}

.note-toolbar__quick-tags > span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.note-toolbar__search-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 4px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.82);
}

.note-toolbar__search {
  width: 100%;
}

.note-toolbar__search :deep(.el-input__wrapper) {
  min-height: 36px;
  box-shadow: none;
  background: transparent;
}

.note-toolbar__scope-inline {
  display: inline-flex;
  gap: 4px;
  padding: 4px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.07);
}

.note-toolbar__scope-inline button {
  min-height: 34px;
  padding: 0 13px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-weight: 700;
  white-space: nowrap;
}

.note-toolbar__scope-inline button.is-active {
  background: var(--brand-primary);
  color: #fff;
  box-shadow: 0 6px 12px rgba(47, 93, 80, 0.16);
}

.note-toolbar__primary-actions,
.note-toolbar__secondary-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

.note-toolbar__primary-actions :deep(.el-button),
.note-toolbar__secondary-actions :deep(.el-button) {
  min-height: 44px;
  padding-inline: 18px;
}

.note-toolbar__selects {
  display: grid;
  grid-template-columns: repeat(4, minmax(136px, 1fr));
  gap: 10px;
}

.note-toolbar__selects :deep(.el-select) {
  width: 100%;
}

.note-toolbar__quick-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding-top: 2px;
}

.note-toolbar__quick-tags > span {
  margin: 0 4px 0 0;
}

.note-toolbar__quick-tags button {
  padding: 7px 12px;
  border: 1px solid rgba(216, 207, 191, 0.78);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.76);
  color: var(--text-secondary);
  cursor: pointer;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    background 0.16s ease;
}

.note-toolbar__quick-tags button:hover,
.note-toolbar__quick-tags button.is-active {
  transform: translateY(-1px);
  border-color: rgba(47, 93, 80, 0.35);
  background: rgba(47, 93, 80, 0.1);
  color: var(--brand-primary);
}

@media (max-width: 768px) {
  .note-toolbar__top,
  .note-toolbar__filters {
    grid-template-columns: 1fr;
  }

  .note-toolbar__search-row {
    grid-template-columns: 1fr;
  }

  .note-toolbar__search {
    min-width: 0;
  }

  .note-toolbar__search-wrap {
    min-width: 0;
  }

  .note-toolbar__selects {
    grid-template-columns: 1fr;
  }

  .note-toolbar__primary-actions,
  .note-toolbar__secondary-actions {
    justify-content: flex-start;
  }
}
</style>
