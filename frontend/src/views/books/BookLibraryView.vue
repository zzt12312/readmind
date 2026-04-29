<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import AppCard from '@/components/base/AppCard.vue'
import AppEmpty from '@/components/base/AppEmpty.vue'
import AppSearchInput from '@/components/base/AppSearchInput.vue'
import BookCover from '@/components/common/BookCover.vue'
import { useBooksStore } from '@/stores/books'

const keyword = ref('')
const booksStore = useBooksStore()
const { items, loading } = storeToRefs(booksStore)
const categories = computed(() => Array.from(new Set(items.value.map((book) => book.category).filter(Boolean))))
const selectedCategory = ref('')

const books = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  const scopedBooks = selectedCategory.value
    ? items.value.filter((book) => book.category === selectedCategory.value)
    : items.value

  if (!query) {
    return scopedBooks
  }

  return scopedBooks.filter(
    (book) =>
      book.title.toLowerCase().includes(query) ||
      book.author.toLowerCase().includes(query) ||
      book.tags.some((tag) => tag.toLowerCase().includes(query)),
  )
})

onMounted(() => {
  void booksStore.load()
})

function prewarmBookSummary(bookId: number) {
  void booksStore.prewarmSummary(bookId)
}
</script>

<template>
  <div class="book-library">
    <AppCard class="book-library__hero">
      <div>
        <p class="book-library__eyebrow">Library Explorer</p>
        <h2>{{ keyword ? `搜索「${keyword}」` : '把书库变成可继续整理的阅读档案' }}</h2>
        <p>按书名、作者、标签或分类快速定位，再进入摘要、笔记和问答工作流。</p>
      </div>
      <div class="book-library__hero-stat">
        <span>当前书籍</span>
        <strong>{{ books.length }}</strong>
      </div>
    </AppCard>

    <AppCard class="book-library__toolbar">
      <AppSearchInput v-model="keyword" class="book-library__search" />
      <div class="book-library__actions">
        <el-select v-model="selectedCategory" clearable placeholder="全部分类">
          <el-option v-for="category in categories" :key="category" :label="category" :value="category" />
        </el-select>
        <el-button round>卡片视图</el-button>
      </div>
    </AppCard>

    <section v-loading="loading" class="book-library__grid">
      <AppCard
        v-for="(book, index) in books"
        :key="book.id"
        class="book-library__card"
        @mouseenter="prewarmBookSummary(book.id)"
      >
        <div class="book-library__cover">
          <BookCover
            :src="book.cover"
            :title="book.title"
            :eager="index < 4"
          />
        </div>
        <div class="book-library__content">
          <div>
            <h3>{{ book.title }}</h3>
            <p>{{ book.author }}</p>
          </div>
          <div class="book-library__meta">
            <span>{{ book.notes }} 条笔记</span>
            <div class="book-library__tags">
              <el-tag v-for="tag in book.tags" :key="tag" round effect="plain">{{ tag }}</el-tag>
            </div>
          </div>
          <div class="book-library__footer">
            <RouterLink :to="`/books/${book.id}`">
              <el-button text>查看摘要</el-button>
            </RouterLink>
            <RouterLink :to="`/notes?bookId=${book.id}`">
              <el-button type="primary" plain round>进入笔记</el-button>
            </RouterLink>
          </div>
        </div>
      </AppCard>

      <AppEmpty
        v-if="!loading && books.length === 0"
        title="还没有匹配的书"
        description="换个关键词试试，或者先去导入新的阅读笔记。"
      />
    </section>
  </div>
</template>

<style scoped lang="scss">
.book-library {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.book-library__hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  padding: 26px 28px;
  background:
    radial-gradient(circle at 90% 12%, rgba(192, 139, 92, 0.2), transparent 28%),
    linear-gradient(135deg, rgba(47, 93, 80, 0.1), rgba(255, 253, 249, 0.96) 58%),
    var(--bg-card);
}

.book-library__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.book-library__hero h2 {
  margin: 0 0 10px;
  font-size: clamp(1.5rem, 2.2vw, 2.2rem);
  letter-spacing: -0.04em;
}

.book-library__hero p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.book-library__hero-stat {
  min-width: 132px;
  padding: 15px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 22px;
  text-align: center;
  background: rgba(255, 253, 249, 0.74);
}

.book-library__hero-stat span {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.82rem;
}

.book-library__hero-stat strong {
  display: block;
  margin-top: 4px;
  color: var(--brand-primary);
  font-size: 2rem;
  line-height: 1;
}

.book-library__toolbar {
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.book-library__search {
  flex: 1;
  min-width: 260px;
}

.book-library__actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.book-library__actions :deep(.el-select) {
  width: 180px;
}

.book-library__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.book-library__card {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  gap: 18px;
}

.book-library__cover {
  height: 148px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 16px 28px rgba(40, 70, 61, 0.18);
}

.book-library__content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.book-library__content h3 {
  margin: 0;
}

.book-library__content p {
  margin: 6px 0 0;
  color: var(--text-tertiary);
}

.book-library__meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: var(--text-secondary);
}

.book-library__tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.book-library__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 1024px) {
  .book-library__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .book-library__toolbar,
  .book-library__actions,
  .book-library__hero,
  .book-library__card {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .book-library__hero-stat {
    text-align: left;
  }
}
</style>
