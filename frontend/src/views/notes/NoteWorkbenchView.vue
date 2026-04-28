<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { fetchJobDetail } from '@/api/modules/jobs'
import { summarizeFilteredNotes } from '@/api/modules/notes-summary'
import AppCard from '@/components/base/AppCard.vue'
import AppEmpty from '@/components/base/AppEmpty.vue'
import AppSearchInput from '@/components/base/AppSearchInput.vue'
import { useBooksStore } from '@/stores/books'
import { useNotesStore } from '@/stores/notes'
import type { NoteInsightReference, NoteInsightSections, QueryRewriteSummary } from '@/types/note'
import { highlightText } from '@/utils/text'

const keyword = ref('')
const selectedCategory = ref('')
const selectedTag = ref('')
const selectedChapter = ref('')
const selectedSort = ref('relevance')
const refreshingInsight = ref(false)
const insightSummary = ref('')
const insightReferences = ref<NoteInsightReference[]>([])
const insightSections = ref<NoteInsightSections | null>(null)
const insightJobStatus = ref<'' | 'queued' | 'processing' | 'success' | 'failed' | 'canceled'>('')
const insightJobMessage = ref('')
const route = useRoute()
const router = useRouter()
const booksStore = useBooksStore()
const notesStore = useNotesStore()
const { items, insight, filters, pagination, loading, activeBookId, activeNoteId } = storeToRefs(notesStore)
const { items: bookItems } = storeToRefs(booksStore)

const notes = computed(() => items.value)
const queryRewrite = computed<QueryRewriteSummary | null>(() => insight.value.query_rewrite ?? null)
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

async function loadFromRoute() {
  const hasExplicitScope =
    Boolean(route.query.bookId) ||
    Boolean(route.query.noteId) ||
    Boolean(route.query.q) ||
    Boolean(route.query.category) ||
    Boolean(route.query.tag) ||
    Boolean(route.query.chapter)

  if (!hasExplicitScope) {
    // 笔记工作台默认落到《南明史》，让演示站首次进入就能看到完整内容和历史类真实笔记。
    await router.replace({
      path: '/notes',
      query: {
        bookId: '3',
      },
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
  if (bookItems.value.length === 0) {
    void booksStore.load()
  }
  void loadFromRoute()
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

function submitSearch() {
  const nextQuery: Record<string, string> = {}
  if (route.query.bookId) nextQuery.bookId = String(route.query.bookId)
  if (route.query.noteId) nextQuery.noteId = String(route.query.noteId)
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

function applyFilters() {
  submitSearch()
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

function renderHighlight(text: string) {
  return highlightText(text, keyword.value)
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

async function pollInsightJob(jobId: string) {
  // AI 洞察改成异步后，右侧面板不再被生成请求卡住；这里只轮询后台任务并在完成后回填结果。
  for (let index = 0; index < 40; index += 1) {
    const job = await fetchJobDetail(jobId)
    insightJobStatus.value = job.status
    insightJobMessage.value = job.message || ''

    if (job.status === 'success') {
      insightSummary.value = job.result?.summary || ''
      insightReferences.value = ((job.result as { references?: NoteInsightReference[] } | null)?.references) || []
      insightSections.value = ((job.result as { sections?: NoteInsightSections } | null)?.sections) || null
      ElMessage.success('已基于当前筛选条件重新总结')
      return
    }

    if (job.status === 'failed') {
      throw new Error(job.error_message || 'AI 洞察生成失败')
    }

    await new Promise((resolve) => window.setTimeout(resolve, 1500))
  }

  insightJobMessage.value = '洞察仍在生成中，请稍后再看'
}

async function loadMore() {
  await notesStore.loadMore()
}
</script>

<template>
  <div class="note-workbench">
    <div class="note-workbench__toolbar">
      <AppSearchInput v-model="keyword" @submit="submitSearch" />
      <div class="note-workbench__toolbar-actions">
        <el-button round @click="submitSearch">搜索</el-button>
        <el-select v-model="selectedCategory" clearable placeholder="分类" style="width: 160px" @change="applyFilters">
          <el-option v-for="category in filters.categories" :key="category" :label="category" :value="category" />
        </el-select>
        <el-select v-model="selectedTag" clearable placeholder="标签" style="width: 180px" @change="applyFilters">
          <el-option v-for="tag in filters.tags" :key="tag" :label="tag" :value="tag" />
        </el-select>
        <el-select v-model="selectedChapter" clearable placeholder="章节" style="width: 180px" @change="applyFilters">
          <el-option v-for="chapter in filters.chapters" :key="chapter" :label="chapter" :value="chapter" />
        </el-select>
        <el-select v-model="selectedSort" placeholder="排序" style="width: 160px" @change="applyFilters">
          <el-option label="默认排序" value="relevance" />
          <el-option label="时间从新到旧" value="time_desc" />
          <el-option label="时间从旧到新" value="time_asc" />
          <el-option label="内容较长优先" value="length_desc" />
        </el-select>
        <el-button round @click="refreshInsight">AI 再整理</el-button>
      </div>
    </div>

    <section class="note-workbench__grid">
      <AppCard class="note-workbench__left">
        <h3>筛选</h3>
        <div class="note-workbench__filters">
          <div>
            <strong>书籍</strong>
            <p>{{ currentBook ? currentBook.title : activeBookId ? `已定位到书籍 #${activeBookId}` : '全部书籍' }}</p>
            <el-button v-if="currentBook" text @click="askCurrentBook">问这本书</el-button>
          </div>
          <div>
            <strong>标签</strong>
            <div class="note-workbench__tag-list">
              <el-tag
                v-for="tag in filters.tags.slice(0, 8)"
                :key="tag"
                round
                effect="plain"
                :type="selectedTag === tag ? 'success' : 'info'"
                @click="selectedTag = selectedTag === tag ? '' : tag; applyFilters()"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
      </AppCard>

      <div v-loading="loading" class="note-workbench__center">
        <p class="note-workbench__result-count">当前结果 {{ pagination.total }} 条</p>
        <section v-if="queryRewrite" class="note-workbench__rewrite-tip">
          <strong>检索扩展</strong>
          <p>系统识别到你在问 <span>{{ queryRewrite.applied_rules.join('、') }}</span>，所以补充检索了这些相关概念：</p>
          <div class="note-workbench__tag-list">
            <el-tag
              v-for="term in queryRewrite.expansion_terms.slice(0, 6)"
              :key="term"
              round
              effect="plain"
              type="success"
            >
              {{ term }}
            </el-tag>
          </div>
        </section>
        <AppCard
          v-for="note in notes"
          :key="note.id"
          class="note-workbench__note-card"
          :class="{ 'is-active-note': note.id === activeNoteId }"
          :data-note-id="note.id"
        >
          <p class="note-workbench__chapter">{{ note.chapter }}</p>
          <strong class="note-workbench__book-title">{{ note.book_title }}</strong>
          <blockquote v-html="renderHighlight(note.excerpt)" />
          <p class="note-workbench__comment" v-html="renderHighlight(note.comment)" />
          <div class="note-workbench__tag-list">
            <el-tag v-for="tag in note.tags" :key="tag" round effect="plain">{{ tag }}</el-tag>
          </div>
        </AppCard>

        <AppEmpty
          v-if="!loading && notes.length === 0"
          title="没有找到匹配的笔记"
          description="试试搜索章节名、观点关键词或主题标签。"
        />
        <div v-else-if="pagination.has_more" class="note-workbench__load-more">
          <el-button round :loading="loading" @click="loadMore">加载更多</el-button>
        </div>
      </div>

      <AppCard class="note-workbench__right">
        <div class="note-workbench__insight-header">
          <h3>AI 洞察</h3>
          <el-button text :loading="refreshingInsight" @click="refreshInsight">
            {{ hasGeneratedInsight ? '重新总结' : '生成总结' }}
          </el-button>
        </div>
        <section class="note-workbench__insight-state" :class="`is-${insightState.tone}`">
          <strong>{{ insightState.label }}</strong>
          <p>{{ insightState.detail }}</p>
        </section>
        <div class="note-workbench__insight-scroll">
        <template v-if="hasGeneratedInsight">
        <section class="note-workbench__insight">
          <strong>核心结论</strong>
          <p>{{ insightSummary }}</p>
        </section>
        <section v-if="insightSections?.reasoning" class="note-workbench__insight">
          <strong>为什么值得关注</strong>
          <p>{{ insightSections.reasoning }}</p>
        </section>
        <section class="note-workbench__insight">
          <strong>关联主题</strong>
          <div class="note-workbench__tag-list">
            <el-tag
              v-for="topic in (insightSections?.key_themes?.length ? insightSections.key_themes : insight.related_topics)"
              :key="topic"
              round
            >
              {{ topic }}
            </el-tag>
          </div>
        </section>
        <section v-if="insightSections?.review_questions?.length" class="note-workbench__insight">
          <strong>值得复习的问题</strong>
          <ul class="note-workbench__insight-list">
            <li v-for="question in insightSections.review_questions" :key="question">{{ question }}</li>
          </ul>
        </section>
        <section v-if="insightSections?.action_suggestions?.length" class="note-workbench__insight">
          <strong>可执行建议</strong>
          <ul class="note-workbench__insight-list">
            <li v-for="suggestion in insightSections.action_suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </section>
        <section v-if="queryRewrite" class="note-workbench__insight">
          <strong>本次检索如何扩展问题</strong>
          <p>为了更稳地召回相关笔记，系统额外补充了以下概念词。</p>
          <div class="note-workbench__tag-list">
            <el-tag v-for="term in queryRewrite.expansion_terms.slice(0, 8)" :key="term" round effect="plain">
              {{ term }}
            </el-tag>
          </div>
        </section>
        <section v-if="insightReferences.length" class="note-workbench__insight">
          <strong>引用依据</strong>
          <div class="note-workbench__insight-references">
            <article
              v-for="reference in insightReferences"
              :key="reference.book + reference.chapter + reference.excerpt"
              class="note-workbench__insight-reference"
              @click="jumpToInsightReference(reference)"
            >
              <p class="note-workbench__insight-reference-title">{{ reference.book }} · {{ reference.chapter }}</p>
              <blockquote>{{ reference.excerpt }}</blockquote>
            </article>
          </div>
        </section>
        </template>
        <section
          v-else-if="insightJobStatus === 'queued' || insightJobStatus === 'processing'"
          class="note-workbench__insight note-workbench__insight--placeholder"
        >
          <strong>{{ insightState.label }}</strong>
          <p>{{ insightState.detail }}</p>
        </section>
        <section
          v-else-if="insightJobStatus === 'failed'"
          class="note-workbench__insight note-workbench__insight--placeholder note-workbench__insight--error"
        >
          <strong>{{ insightState.label }}</strong>
          <p>{{ insightState.detail }}</p>
        </section>
        <section v-else class="note-workbench__insight note-workbench__insight--placeholder">
          <strong>{{ insightState.label }}</strong>
          <p>{{ insightState.detail }}</p>
        </section>
        </div>
      </AppCard>
    </section>
  </div>
</template>

<style scoped lang="scss">
.note-workbench {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.note-workbench__toolbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.note-workbench__toolbar-actions {
  display: flex;
  gap: 12px;
}

.note-workbench__grid {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 340px;
  gap: 18px;
  align-items: start;
}

.note-workbench__left,
.note-workbench__right {
  position: sticky;
  top: 106px;
}

.note-workbench__filters {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.note-workbench__filters p {
  margin: 8px 0 0;
  color: var(--text-secondary);
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

.note-workbench__result-count {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.note-workbench__rewrite-tip {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  background: rgba(47, 93, 80, 0.06);
}

.note-workbench__rewrite-tip strong {
  display: block;
  margin-bottom: 6px;
}

.note-workbench__rewrite-tip p {
  margin: 0 0 10px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.note-workbench__rewrite-tip span {
  color: var(--text-primary);
  font-weight: 600;
}

.note-workbench__note-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.note-workbench__note-card.is-active-note {
  border-color: rgba(47, 93, 80, 0.45);
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.12);
}

.note-workbench__chapter {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.88rem;
}

.note-workbench__book-title {
  color: var(--brand-primary);
}

.note-workbench blockquote {
  margin: 0;
  padding-left: 14px;
  border-left: 3px solid var(--brand-accent);
  color: var(--text-primary);
  font-size: 1rem;
  line-height: 1.85;
}

.note-workbench__comment {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

:deep(mark) {
  padding: 0 2px;
  border-radius: 4px;
  background: rgba(192, 139, 92, 0.22);
}

.note-workbench__tag-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.note-workbench__insight {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.note-workbench__insight-scroll {
  max-height: calc(100vh - 190px);
  overflow-y: auto;
  padding-right: 4px;
}

.note-workbench__insight-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.note-workbench__insight-state {
  margin-top: 14px;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  background: rgba(47, 93, 80, 0.05);
}

.note-workbench__insight-state.is-danger {
  border-color: rgba(190, 76, 60, 0.22);
  background: rgba(190, 76, 60, 0.08);
}

.note-workbench__insight-state.is-success {
  border-color: rgba(47, 93, 80, 0.2);
  background: rgba(47, 93, 80, 0.08);
}

.note-workbench__insight-state strong {
  display: block;
  margin-bottom: 6px;
}

.note-workbench__insight-state p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.note-workbench__insight p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.note-workbench__insight-list {
  margin: 0;
  padding-left: 18px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.note-workbench__insight-list li + li {
  margin-top: 6px;
}

.note-workbench__insight--placeholder {
  padding: 16px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
}

.note-workbench__insight--error {
  color: #b2523c;
}

.note-workbench__insight-references {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.note-workbench__insight-reference {
  padding: 12px;
  border-radius: 12px;
  background: rgba(251, 248, 242, 0.72);
  cursor: pointer;
}

.note-workbench__insight-reference-title {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.88rem;
}

.note-workbench__insight-reference blockquote {
  margin: 0;
  padding-left: 12px;
  border-left: 3px solid rgba(192, 139, 92, 0.5);
  color: var(--text-secondary);
  line-height: 1.75;
}

@media (max-width: 1280px) {
  .note-workbench__grid {
    grid-template-columns: 1fr;
  }

  .note-workbench__left,
  .note-workbench__right {
    position: static;
  }
}

@media (max-width: 768px) {
  .note-workbench__toolbar,
  .note-workbench__toolbar-actions {
    flex-direction: column;
  }
}
</style>
