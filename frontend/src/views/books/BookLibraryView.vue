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

const books = computed(() => {
  const query = keyword.value.trim().toLowerCase()

  if (!query) {
    return items.value
  }

  return items.value.filter(
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
    <div class="book-library__toolbar">
      <AppSearchInput v-model="keyword" />
      <div class="book-library__actions">
        <el-select placeholder="分类" style="width: 140px">
          <el-option label="全部分类" value="all" />
        </el-select>
        <el-button round>卡片视图</el-button>
      </div>
    </div>

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

.book-library__toolbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.book-library__actions {
  display: flex;
  gap: 12px;
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
  .book-library__card {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
