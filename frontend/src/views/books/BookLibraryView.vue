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
        <RouterLink class="book-library__cover" :to="`/books/${book.id}`" aria-label="查看书籍详情">
          <BookCover
            :src="book.cover"
            :title="book.title"
            :eager="index < 4"
          />
        </RouterLink>
        <div class="book-library__content">
          <div class="book-library__title-block">
            <span class="book-library__index">{{ String(index + 1).padStart(2, '0') }}</span>
            <h3>{{ book.title }}</h3>
            <p>{{ book.author }}</p>
          </div>
          <div class="book-library__meta">
            <span class="book-library__note-count">{{ book.notes }} 条笔记</span>
            <div class="book-library__tags">
              <span v-for="tag in book.tags.slice(0, 3)" :key="tag">{{ tag }}</span>
              <span v-if="book.tags.length > 3" class="book-library__tag-more">+{{ book.tags.length - 3 }}</span>
            </div>
          </div>
          <div class="book-library__footer">
            <RouterLink class="book-library__action" :to="`/books/${book.id}`">
              查看摘要
            </RouterLink>
            <RouterLink class="book-library__action is-primary" :to="`/notes?bookId=${book.id}`">
              笔记工作台
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
  align-items: start;
}

.book-library__card {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 148px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
  padding: 18px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(247, 242, 234, 0.76)),
    var(--bg-card);
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease,
    transform 0.16s ease;
}

.book-library__card::after {
  content: '';
  position: absolute;
  right: -42px;
  bottom: -52px;
  width: 132px;
  height: 132px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.06);
  pointer-events: none;
}

.book-library__card:hover {
  border-color: rgba(47, 93, 80, 0.22);
  box-shadow: 0 16px 32px rgba(57, 45, 31, 0.09);
  transform: translateY(-2px);
}

.book-library__cover {
  position: relative;
  z-index: 1;
  grid-column: 1;
  grid-row: 1;
  display: grid;
  place-items: stretch;
  width: 148px;
  height: 222px;
  min-width: 0;
  border: 1px solid rgba(47, 93, 80, 0.1);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 16px 28px rgba(40, 70, 61, 0.14);
  text-decoration: none;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease,
    transform 0.16s ease;
}

.book-library__cover:hover {
  border-color: rgba(47, 93, 80, 0.24);
  box-shadow: 0 18px 30px rgba(40, 70, 61, 0.18);
  transform: translateY(-1px);
}

.book-library__cover :deep(.book-cover) {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.book-library__cover :deep(.book-cover__image) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-library__content {
  position: relative;
  z-index: 2;
  grid-column: 2;
  grid-row: 1;
  min-width: 0;
  min-height: 222px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.book-library__title-block {
  min-width: 0;
}

.book-library__index {
  display: inline-flex;
  width: 28px;
  height: 28px;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  font-size: 0.72rem;
  font-weight: 900;
}

.book-library__content h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.08rem;
  line-height: 1.38;
  overflow-wrap: anywhere;
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.book-library__content p {
  margin: 4px 0 0;
  color: var(--text-tertiary);
  line-height: 1.4;
}

.book-library__meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--text-secondary);
}

.book-library__note-count {
  width: fit-content;
  padding: 6px 10px;
  border: 1px solid rgba(47, 93, 80, 0.1);
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.07);
  color: var(--brand-primary);
  font-size: 0.82rem;
  font-weight: 900;
}

.book-library__tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.book-library__tags span {
  padding: 4px 8px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.72);
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 800;
}

.book-library__tags .book-library__tag-more {
  border-color: rgba(47, 93, 80, 0.16);
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
}

.book-library__footer {
  position: relative;
  z-index: 1;
  flex: 0 0 auto;
  margin-top: auto;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
}

.book-library__action {
  min-width: 0;
  min-height: 30px;
  padding: 6px 9px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 10px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(248, 244, 237, 0.72)),
    var(--bg-card);
  color: var(--text-primary);
  font-size: 0.78rem;
  font-weight: 900;
  line-height: 1.2;
  text-decoration: none;
  transition:
    border-color 0.16s ease,
    background 0.16s ease,
    transform 0.16s ease;
}

.book-library__action:hover {
  border-color: rgba(47, 93, 80, 0.24);
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 1), rgba(240, 246, 239, 0.76)),
    var(--bg-card);
  transform: translateY(-1px);
}

.book-library__action.is-primary {
  border-color: rgba(47, 93, 80, 0.2);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.1), rgba(255, 253, 249, 0.82)),
    var(--bg-card);
  color: var(--brand-primary);
}

@media (max-width: 1024px) {
  .book-library__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .book-library__toolbar,
  .book-library__actions,
  .book-library__hero {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: stretch;
  }

  .book-library__card {
    grid-template-columns: 128px minmax(0, 1fr);
    gap: 14px;
    padding: 16px;
  }

  .book-library__cover {
    width: 128px;
    height: 192px;
  }

  .book-library__content {
    min-height: 192px;
  }

  .book-library__hero-stat {
    text-align: left;
  }
}
</style>
