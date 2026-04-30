<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { exportNoteInsight, summarizeFilteredNotes } from '@/api/modules/notes-summary'
import AppCard from '@/components/base/AppCard.vue'
import AppEmpty from '@/components/base/AppEmpty.vue'
import NoteCard from '@/components/notes/NoteCard.vue'
import NoteInsightPanel from '@/components/notes/NoteInsightPanel.vue'
import NoteToolbar from '@/components/notes/NoteToolbar.vue'
import QueryRewriteTip from '@/components/notes/QueryRewriteTip.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import { buildEmptyNotesMascotCue } from '@/constants/mascotMessages'
import { useJobPolling } from '@/composables/useJobPolling'
import { useAppStore } from '@/stores/app'
import { useBooksStore } from '@/stores/books'
import { useNotesStore } from '@/stores/notes'
import type { NoteInsightReference, NoteInsightSections, QueryRewriteSummary } from '@/types/note'

const keyword = ref('')
const selectedCategory = ref('')
const selectedTag = ref('')
const selectedChapter = ref('')
const selectedSort = ref('relevance')
const searchScope = ref<'current-book' | 'all-books'>('current-book')
const refreshingInsight = ref(false)
const insightSummary = ref('')
const insightReferences = ref<NoteInsightReference[]>([])
const insightSections = ref<NoteInsightSections | null>(null)
const insightJobStatus = ref<'' | 'queued' | 'processing' | 'success' | 'failed' | 'canceled'>('')
const insightJobMessage = ref('')
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const booksStore = useBooksStore()
const notesStore = useNotesStore()
const { pollJob } = useJobPolling()
const { items, insight, filters, pagination, loading, activeBookId, activeNoteId } = storeToRefs(notesStore)
const { items: bookItems } = storeToRefs(booksStore)

const notes = computed(() => items.value)
const queryRewrite = computed<QueryRewriteSummary | null>(() => insight.value.query_rewrite ?? null)
const emptyNotesMascotCue = computed(() => buildEmptyNotesMascotCue())

// The route query is the source of truth for the workbench. Local refs mirror
// it so form controls feel instant, then `submitSearch()` writes changes back
// into the URL. This makes filtered note views shareable and restorable.
const hasActiveFilters = computed(
  () =>
    Boolean(keyword.value.trim()) ||
    Boolean(selectedCategory.value) ||
    Boolean(selectedTag.value) ||
    Boolean(selectedChapter.value) ||
    selectedSort.value !== 'relevance',
)
const hasInsightContext = computed(
  () =>
    Boolean(route.query.bookId) ||
    Boolean(keyword.value.trim()) ||
    Boolean(selectedCategory.value) ||
    Boolean(selectedTag.value) ||
    Boolean(selectedChapter.value),
)
const hasGeneratedInsight = computed(() => Boolean(insightSummary.value.trim()))
const insightState = computed(() => {
  if (!hasInsightContext.value) {
    return {
      tone: 'idle',
      label: '等待你先缩小笔记范围',
      detail: '先搜索一个观点，或者选择书籍、标签、章节后，再让 AI 帮你总结，这样结果会更准确。',
    }
  }
  if (insightJobStatus.value === 'queued') {
    return {
      tone: 'primary',
      label: '洞察任务已进入队列',
      detail: insightJobMessage.value || '任务已经创建完成，后台会继续整理当前筛选范围。',
    }
  }
  if (insightJobStatus.value === 'processing') {
    return {
      tone: 'primary',
      label: 'AI 正在整理当前范围',
      detail: insightJobMessage.value || '正在读取当前筛选到的笔记，并归纳共性主题。',
    }
  }
  if (insightJobStatus.value === 'failed') {
    return {
      tone: 'danger',
      label: 'AI 洞察生成失败',
      detail: insightJobMessage.value || '这次生成没有成功，可以稍后重试。',
    }
  }
  if (hasGeneratedInsight.value) {
    return {
      tone: 'success',
      label: 'AI 洞察已生成',
      detail: '当前结果已经和右侧筛选条件同步，你可以继续调整范围后重新生成。',
    }
  }
  return {
    tone: 'ready',
    label: '当前范围已准备好',
    detail: '点击“生成总结”，基于当前筛选结果生成更聚焦的 AI 洞察。',
  }
})

function pickDefaultBookId() {
  if (appStore.llmHealth?.demo_mode) {
    return 3
  }

  const sorted = [...bookItems.value].sort((left, right) =>
    (right.last_read_date || right.reading_date || '').localeCompare(left.last_read_date || left.reading_date || ''),
  )
  return sorted[0]?.id
}

async function loadFromRoute() {
  const isAllScope = route.query.scope === 'all'
  const hasExplicitScope =
    isAllScope ||
    Boolean(route.query.bookId) ||
    Boolean(route.query.noteId) ||
    Boolean(route.query.q) ||
    Boolean(route.query.category) ||
    Boolean(route.query.tag) ||
    Boolean(route.query.chapter)

  if (!hasExplicitScope) {
    // 演示模式默认落到《南明史》，真实模式优先落到最近阅读的一本书。
    const defaultBookId = pickDefaultBookId()
    await router.replace({
      path: '/notes',
      query: defaultBookId ? { bookId: String(defaultBookId) } : { scope: 'all' },
    })
    return
  }

  const bookId = route.query.bookId ? Number(route.query.bookId) : undefined
  const noteId = route.query.noteId ? Number(route.query.noteId) : undefined
  const q = route.query.q ? String(route.query.q) : ''
  const category = route.query.category ? String(route.query.category) : ''
  const tag = route.query.tag ? String(route.query.tag) : ''
  const chapter = route.query.chapter ? String(route.query.chapter) : ''
  const sort = route.query.sort ? String(route.query.sort) : 'relevance'
  const page = route.query.page ? Number(route.query.page) : 1
  keyword.value = q
  selectedCategory.value = category
  selectedTag.value = tag
  selectedChapter.value = chapter
  selectedSort.value = sort
  searchScope.value = bookId && route.query.scope !== 'all' ? 'current-book' : 'all-books'
  await notesStore.load({ book_id: bookId, note_id: noteId, q, category, tag, chapter, sort, page, per_page: 30 })
  insightSummary.value = ''
  insightReferences.value = []
  insightSections.value = null
  insightJobStatus.value = ''
  insightJobMessage.value = ''

  if (noteId) {
    await nextTick()
    document.querySelector<HTMLElement>(`[data-note-id="${noteId}"]`)?.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    })
  }
}

onMounted(() => {
  void (async () => {
    if (bookItems.value.length === 0) {
      await booksStore.load()
    }
    if (!appStore.llmHealth) {
      await appStore.loadLlmHealth()
    }
    await loadFromRoute()
  })()
})

watch(
  () => route.query,
  () => {
    void loadFromRoute()
  },
)

const currentBook = computed(() => {
  if (!activeBookId.value) return null
  return booksStore.findById(activeBookId.value)
})
const noteHeroTitle = computed(() => {
  const query = keyword.value.trim()
  if (query) {
    const scopeText = searchScope.value === 'current-book' && currentBook.value
      ? `《${currentBook.value.title}》`
      : '全部书籍'
    return `在${scopeText}中搜索「${query}」`
  }
  if (currentBook.value) {
    return `正在整理《${currentBook.value.title}》`
  }
  if (selectedTag.value) {
    return `正在浏览「${selectedTag.value}」主题笔记`
  }
  if (selectedCategory.value) {
    return `正在浏览「${selectedCategory.value}」分类笔记`
  }
  return '从书摘里重新发现你的想法'
})
const noteHeroDescription = computed(() => {
  const filtersText = [
    selectedCategory.value ? `分类：${selectedCategory.value}` : '',
    selectedTag.value ? `标签：${selectedTag.value}` : '',
    selectedChapter.value ? `章节：${selectedChapter.value}` : '',
  ].filter(Boolean)

  if (keyword.value.trim()) {
    return filtersText.length
      ? `已叠加 ${filtersText.join('、')}，当前命中结果会优先展示和关键词最相关的摘录。`
      : '当前结果会优先展示和关键词最相关的摘录，你可以继续叠加分类、标签或章节缩小范围。'
  }
  if (currentBook.value) {
    return '围绕这本书筛选摘录、追问观点、生成洞察，并把值得回看的内容送进复习。'
  }
  if (filtersText.length) {
    return `已按 ${filtersText.join('、')} 缩小范围，可以继续搜索关键词或生成 AI 洞察。`
  }
  return '搜索关键词、主题标签或章节，把分散在 Obsidian 里的微信读书划线整理成可复用的知识线索。'
})

function submitSearch() {
  const nextQuery: Record<string, string> = {}
  if (searchScope.value === 'all-books') {
    nextQuery.scope = 'all'
  } else if (activeBookId.value) {
    nextQuery.bookId = String(activeBookId.value)
  }
  if (keyword.value.trim()) nextQuery.q = keyword.value.trim()
  if (selectedCategory.value) nextQuery.category = selectedCategory.value
  if (selectedTag.value) nextQuery.tag = selectedTag.value
  if (selectedChapter.value) nextQuery.chapter = selectedChapter.value
  if (selectedSort.value && selectedSort.value !== 'relevance') nextQuery.sort = selectedSort.value

  void router.push({
    path: '/notes',
    query: nextQuery,
  })
}

function resetFilters() {
  keyword.value = ''
  selectedCategory.value = ''
  selectedTag.value = ''
  selectedChapter.value = ''
  selectedSort.value = 'relevance'

  const nextQuery: Record<string, string> = {}
  if (searchScope.value === 'current-book' && activeBookId.value) {
    nextQuery.bookId = String(activeBookId.value)
  } else {
    nextQuery.scope = 'all'
  }

  void router.push({
    path: '/notes',
    query: nextQuery,
  })
}

function showAllNotes() {
  keyword.value = ''
  selectedCategory.value = ''
  selectedTag.value = ''
  selectedChapter.value = ''
  selectedSort.value = 'relevance'
  searchScope.value = 'all-books'

  // 给一个显式 scope，避免“无查询参数时默认跳到《南明史》”这条首次引导逻辑再次触发。
  void router.push({
    path: '/notes',
    query: {
      scope: 'all',
    },
  })
}

function askCurrentBook() {
  if (!currentBook.value) return
  void router.push({
    path: '/qa',
    query: {
      bookId: String(currentBook.value.id),
      scope: 'current-book',
      preset: `《${currentBook.value.title}》里最值得回看的 5 个观点是什么？`,
    },
  })
}

function reviewByTopic(topic: string) {
  void router.push({
    path: '/review',
    query: {
      tag: topic,
    },
  })
}

function jumpToInsightReference(reference: NoteInsightReference) {
  const matched = notes.value.find(
    (note) =>
      note.book_title === reference.book &&
      note.chapter === reference.chapter &&
      note.excerpt === reference.excerpt,
  )
  if (!matched) return
  void router.push({
    path: '/notes',
    query: {
      ...(route.query.bookId ? { bookId: String(route.query.bookId) } : {}),
      noteId: String(matched.id),
      ...(keyword.value.trim() ? { q: keyword.value.trim() } : {}),
      ...(selectedCategory.value ? { category: selectedCategory.value } : {}),
      ...(selectedTag.value ? { tag: selectedTag.value } : {}),
      ...(selectedChapter.value ? { chapter: selectedChapter.value } : {}),
    },
  })
}

async function refreshInsight() {
  if (!hasInsightContext.value) {
    ElMessage.info('先搜索或筛选一个更具体的范围，再生成 AI 洞察。')
    return
  }

  refreshingInsight.value = true
  try {
    const data = await summarizeFilteredNotes({
      book_id: route.query.bookId ? Number(route.query.bookId) : undefined,
      q: keyword.value.trim() || undefined,
      category: selectedCategory.value || undefined,
      tag: selectedTag.value || undefined,
      chapter: selectedChapter.value || undefined,
      sort: selectedSort.value,
    })
    if (data.summary) {
      // In demo/fallback mode the backend can return a summary immediately.
      // Otherwise it returns a job id and the polling branch below fills state.
      insightSummary.value = data.summary
      insightReferences.value = data.references
      insightSections.value = data.sections
      insightJobStatus.value = 'success'
      insightJobMessage.value = ''
      ElMessage.success('已基于当前筛选条件重新总结')
      return
    }

    insightJobStatus.value = data.status || 'queued'
    insightJobMessage.value = data.message || '洞察任务已创建'
    if (data.job_id) {
      await pollInsightJob(data.job_id)
    }
  } catch (error) {
    insightJobStatus.value = 'failed'
    insightJobMessage.value = error instanceof Error ? error.message : 'AI 洞察生成失败'
  } finally {
    refreshingInsight.value = false
  }
}

async function exportCurrentInsight() {
  if (!hasGeneratedInsight.value) {
    ElMessage.info('先生成 AI 洞察，再导出 Markdown。')
    return
  }
  try {
    const result = await exportNoteInsight({
      title: currentBook.value ? `${currentBook.value.title} - 笔记洞察` : '笔记洞察',
      scope: {
        book_id: activeBookId.value ?? undefined,
        book_title: currentBook.value?.title,
        q: keyword.value.trim() || undefined,
        category: selectedCategory.value || undefined,
        tag: selectedTag.value || undefined,
        chapter: selectedChapter.value || undefined,
        sort: selectedSort.value,
      },
      summary: insightSummary.value,
      sections: insightSections.value,
      references: insightReferences.value,
    })
    ElMessage.success(`已导出到 ${result.relative_path}`)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '导出洞察失败，请稍后重试')
  }
}

async function pollInsightJob(jobId: string) {
  await pollJob(jobId, {
    maxAttempts: 40,
    intervalMs: 1500,
    onProgress: (job) => {
      insightJobStatus.value = job.status
      insightJobMessage.value = job.message || ''
    },
    onSuccess: (job) => {
      insightSummary.value = job.result?.summary || ''
      insightReferences.value = ((job.result as { references?: NoteInsightReference[] } | null)?.references) || []
      insightSections.value = ((job.result as { sections?: NoteInsightSections } | null)?.sections) || null
      ElMessage.success('已基于当前筛选条件重新总结')
    },
    onFailed: (job) => {
      insightJobMessage.value = job.error_message || 'AI 洞察生成失败'
    },
    onTimeout: () => {
      insightJobMessage.value = '洞察仍在生成中，请稍后再看'
    },
  })
}

async function loadMore() {
  await notesStore.loadMore()
}

</script>

<template>
  <div class="note-workbench">
    <AppCard class="note-workbench__hero">
      <div>
        <p class="note-workbench__eyebrow">Reading Notes Studio</p>
        <h2>{{ noteHeroTitle }}</h2>
        <p>{{ noteHeroDescription }}</p>
      </div>
      <div class="note-workbench__hero-stats">
        <span>当前结果</span>
        <strong>{{ pagination.total }}</strong>
        <em>条笔记</em>
      </div>
    </AppCard>

    <NoteToolbar
      v-model:keyword="keyword"
      v-model:search-scope="searchScope"
      v-model:category="selectedCategory"
      v-model:tag="selectedTag"
      v-model:chapter="selectedChapter"
      v-model:sort="selectedSort"
      :filters="filters"
      :has-active-filters="hasActiveFilters"
      :can-show-all="Boolean(currentBook || route.query.scope === 'all')"
      :current-book-title="currentBook?.title"
      @submit="submitSearch"
      @reset="resetFilters"
      @show-all="showAllNotes"
      @refresh-insight="refreshInsight"
      @ask-current-book="askCurrentBook"
    />

    <section class="note-workbench__grid">
      <div v-loading="loading" class="note-workbench__center">
        <div class="note-workbench__result-bar">
          <span>{{ currentBook ? currentBook.title : '全部书籍' }}</span>
          <strong>{{ pagination.total }} 条笔记</strong>
        </div>
        <QueryRewriteTip v-if="queryRewrite" :query-rewrite="queryRewrite" />
        <NoteCard
          v-for="note in notes"
          :key="note.id"
          :note="note"
          :active="note.id === activeNoteId"
          :keyword="keyword"
        />

        <AppEmpty
          v-if="!loading && notes.length === 0"
          title="没有找到匹配的笔记"
          description="试试搜索章节名、观点关键词或主题标签。"
        >
          <MascotBubble
            class="note-workbench__empty-mascot"
            :mood="emptyNotesMascotCue.mood"
            :message="emptyNotesMascotCue.message"
            compact
          />
        </AppEmpty>
        <div v-else-if="pagination.has_more" class="note-workbench__load-more">
          <el-button round :loading="loading" @click="loadMore">加载更多</el-button>
        </div>
      </div>

      <NoteInsightPanel
        :refreshing="refreshingInsight"
        :has-generated-insight="hasGeneratedInsight"
        :insight-state="insightState"
        :insight-summary="insightSummary"
        :insight-sections="insightSections"
        :related-topics="insight.related_topics"
        :query-rewrite="queryRewrite"
        :insight-references="insightReferences"
        :insight-job-status="insightJobStatus"
        @refresh="refreshInsight"
        @export-insight="exportCurrentInsight"
        @review-by-topic="reviewByTopic"
        @jump-to-reference="jumpToInsightReference"
      />
    </section>
  </div>
</template>

<style scoped lang="scss">
.note-workbench {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.note-workbench__hero {
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: space-between;
  gap: 24px;
  align-items: flex-end;
  padding: 28px;
  background:
    radial-gradient(circle at 92% 16%, rgba(192, 139, 92, 0.22), transparent 30%),
    linear-gradient(135deg, rgba(47, 93, 80, 0.12), rgba(255, 253, 249, 0.96) 58%),
    var(--bg-card);
}

.note-workbench__hero::after {
  content: '';
  position: absolute;
  right: -52px;
  bottom: -68px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  border: 1px solid rgba(47, 93, 80, 0.1);
  background: rgba(255, 253, 249, 0.34);
}

.note-workbench__hero > * {
  position: relative;
  z-index: 1;
}

.note-workbench__eyebrow {
  margin: 0 0 10px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.note-workbench__hero h2 {
  max-width: 48rem;
  margin: 0 0 10px;
  font-size: clamp(1.5rem, 2vw, 2.1rem);
  letter-spacing: -0.03em;
}

.note-workbench__hero p:last-child {
  max-width: 46rem;
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.note-workbench__hero-stats {
  min-width: 132px;
  padding: 16px;
  border-radius: 22px;
  text-align: center;
  background: rgba(255, 253, 249, 0.74);
  border: 1px solid rgba(216, 207, 191, 0.72);
  box-shadow: var(--shadow-sm);
}

.note-workbench__hero-stats span,
.note-workbench__hero-stats em {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.82rem;
  font-style: normal;
}

.note-workbench__hero-stats strong {
  display: block;
  margin: 4px 0;
  color: var(--brand-primary);
  font-size: 2rem;
  line-height: 1;
}

.note-workbench__grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(390px, 0.42fr);
  gap: 20px;
  align-items: start;
}

.note-workbench__center {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.note-workbench__load-more {
  display: flex;
  justify-content: center;
  padding: 8px 0 4px;
}

.note-workbench__empty-mascot {
  max-width: 460px;
  margin: 18px auto 0;
  text-align: left;
}

.note-workbench__result-bar {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.76);
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.note-workbench__result-bar strong {
  color: var(--text-primary);
}

.note-workbench__tag-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 1280px) {
  .note-workbench__grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .note-workbench__hero {
    align-items: flex-start;
    flex-direction: column;
    padding: 22px;
  }

  .note-workbench__hero-stats {
    width: 100%;
    text-align: left;
  }

  .note-workbench__result-bar {
    align-items: flex-start;
    border-radius: 18px;
    flex-direction: column;
  }
}
</style>
