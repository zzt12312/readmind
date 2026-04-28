<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import AppCard from '@/components/base/AppCard.vue'
import AppSearchInput from '@/components/base/AppSearchInput.vue'
import BookCover from '@/components/common/BookCover.vue'
import { fetchNoteList } from '@/api/modules/notes'
import { useBooksStore } from '@/stores/books'
import type { NoteItem } from '@/types/note'

const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()
const { currentBook, currentSummary, detailLoading, summaryLoading, regenerating, summaryJobStatus, summaryJobMessage } = storeToRefs(booksStore)

const bookId = computed(() => Number(route.params.id))
const bookNotes = ref<NoteItem[]>([])
const notesLoading = ref(false)
const noteKeyword = ref('')
const notePage = ref(1)
const noteTotal = ref(0)
const notePerPage = 8

onMounted(() => {
  if (!Number.isNaN(bookId.value)) {
    void booksStore.loadDetail(bookId.value)
    void loadBookNotes(bookId.value)
  }
})

watch(bookId, (nextId) => {
  if (!Number.isNaN(nextId)) {
    void booksStore.loadDetail(nextId)
    void loadBookNotes(nextId)
  }
})

function askThisBook() {
  if (!currentBook.value) return
  void router.push({
    path: '/qa',
    query: {
      bookId: String(bookId.value),
      scope: 'current-book',
      preset: `《${currentBook.value.title}》里最值得回看的 5 个观点是什么？`,
    },
  })
}

async function loadBookNotes(id: number) {
  notesLoading.value = true
  try {
    const data = await fetchNoteList({
      book_id: id,
      q: noteKeyword.value.trim() || undefined,
      page: notePage.value,
      per_page: notePerPage,
      sort: 'time_desc',
    })
    bookNotes.value = data.items
    noteTotal.value = data.pagination.total
  } finally {
    notesLoading.value = false
  }
}

function searchBookNotes() {
  notePage.value = 1
  void loadBookNotes(bookId.value)
}

function handlePageChange(page: number) {
  notePage.value = page
  void loadBookNotes(bookId.value)
}
</script>

<template>
  <div class="book-detail">
    <AppCard v-if="currentBook" v-loading="detailLoading" class="book-detail__hero">
      <div class="book-detail__cover">
        <BookCover
          :src="currentBook.cover"
          :title="currentBook.title"
          eager
        />
      </div>
      <div class="book-detail__meta">
        <p class="book-detail__eyebrow">{{ currentBook.category }}</p>
        <h2>{{ currentBook.title }}</h2>
        <p>{{ currentBook.author }}</p>
        <div class="book-detail__chips">
          <el-tag v-for="tag in currentBook.tags" :key="tag" round effect="plain">{{ tag }}</el-tag>
        </div>
        <div class="book-detail__stats">
          <span>{{ currentBook.notes }} 条笔记</span>
          <span v-if="currentBook.progress">阅读进度 {{ currentBook.progress }}</span>
          <span v-if="currentBook.last_read_date">最近阅读 {{ currentBook.last_read_date }}</span>
        </div>
        <div class="book-detail__actions">
          <el-button type="primary" round :loading="regenerating" @click="booksStore.regenerateSummary(bookId)">AI 总结重新生成</el-button>
          <RouterLink :to="`/notes?bookId=${bookId}`">
            <el-button round>查看原笔记</el-button>
          </RouterLink>
          <el-button round @click="askThisBook">问这本书</el-button>
        </div>
      </div>
    </AppCard>

    <AppCard v-if="currentBook" class="book-detail__summary-card" v-loading="summaryLoading">
      <h3>AI 总结</h3>
      <p v-if="currentSummary" class="book-detail__summary">{{ currentSummary }}</p>
      <div v-else-if="summaryJobStatus === 'failed'" class="book-detail__summary-placeholder is-error">
        <strong>摘要生成失败</strong>
        <p>{{ summaryJobMessage || '这次生成没有成功，可以稍后重新尝试。' }}</p>
      </div>
      <div v-else class="book-detail__summary-placeholder">
        <strong>{{ summaryJobStatus === 'processing' ? '正在生成这本书的摘要' : '摘要任务已创建' }}</strong>
        <p>{{ summaryJobMessage || '书籍内容已经可以先看，AI 总结会在后台补全，不会再卡住整页。' }}</p>
      </div>
    </AppCard>

    <AppCard v-if="currentBook?.reading_notes">
      <h3>读书笔记</h3>
      <pre class="book-detail__notes">{{ currentBook.reading_notes }}</pre>
    </AppCard>

    <AppCard v-if="currentBook" v-loading="notesLoading">
      <div class="book-detail__section-header">
        <h3>本书高亮</h3>
        <RouterLink :to="`/notes?bookId=${bookId}`">查看全部</RouterLink>
      </div>
      <div class="book-detail__search">
        <AppSearchInput v-model="noteKeyword" @submit="searchBookNotes" />
        <el-button round @click="searchBookNotes">搜索高亮</el-button>
      </div>
      <div class="book-detail__note-list">
        <article v-for="note in bookNotes" :key="note.id" class="book-detail__note-item">
          <p>{{ note.chapter || '未分章节' }}</p>
          <blockquote>{{ note.excerpt }}</blockquote>
          <RouterLink :to="`/notes?bookId=${bookId}&noteId=${note.id}`">跳转原笔记</RouterLink>
        </article>
      </div>
      <el-pagination
        v-if="noteTotal > notePerPage"
        class="book-detail__pagination"
        layout="prev, pager, next"
        :page-size="notePerPage"
        :total="noteTotal"
        :current-page="notePage"
        @current-change="handlePageChange"
      />
    </AppCard>
  </div>
</template>

<style scoped lang="scss">
.book-detail {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.book-detail__hero {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 24px;
}

.book-detail__cover {
  width: 180px;
  height: 240px;
  overflow: hidden;
  border-radius: 24px;
}

.book-detail__eyebrow {
  margin: 0 0 10px;
  color: var(--brand-primary);
}

.book-detail__meta h2 {
  margin: 0 0 10px;
}

.book-detail__meta > p {
  margin: 0 0 12px;
  color: var(--text-secondary);
}

.book-detail__chips,
.book-detail__stats,
.book-detail__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.book-detail__stats {
  color: var(--text-tertiary);
}

.book-detail__summary,
.book-detail__notes {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.9;
  white-space: pre-wrap;
}

.book-detail__summary-placeholder {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: var(--text-secondary);
}

.book-detail__summary-placeholder.is-error {
  color: #b2523c;
}

.book-detail__summary-placeholder p {
  margin: 0;
}

.book-detail__section-header {
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.book-detail__section-header h3 {
  margin: 0;
}

.book-detail__search {
  margin-bottom: 14px;
  display: flex;
  gap: 12px;
}

.book-detail__note-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.book-detail__note-item {
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-sm);
  background: rgba(251, 248, 242, 0.7);
}

.book-detail__note-item p {
  margin: 0 0 10px;
  color: var(--text-tertiary);
}

.book-detail__note-item blockquote {
  margin: 0 0 10px;
  padding-left: 14px;
  border-left: 3px solid var(--brand-accent);
  color: var(--text-primary);
  line-height: 1.8;
}

.book-detail__pagination {
  margin-top: 18px;
  justify-content: center;
}

@media (max-width: 900px) {
  .book-detail__hero {
    grid-template-columns: 1fr;
  }

  .book-detail__cover {
    width: 140px;
    height: 188px;
  }

  .book-detail__search {
    flex-direction: column;
  }
}
</style>
