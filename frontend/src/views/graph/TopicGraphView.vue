<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppCard from '@/components/base/AppCard.vue'
import AppSection from '@/components/base/AppSection.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import TopicClusterDetail from '@/components/graph/TopicClusterDetail.vue'
import TopicGraphControls from '@/components/graph/TopicGraphControls.vue'
import { getTopicGraph } from '@/api/modules/insights'
import { useJobPolling } from '@/composables/useJobPolling'
import { useTopicGraphOption } from '@/composables/useTopicGraphOption'
import type { TopicGraphPayload } from '@/types/insights'

const TopicGraphChart = defineAsyncComponent(() => import('@/components/graph/TopicGraphChart.vue'))

const router = useRouter()
const loading = ref(false)
const payload = ref<TopicGraphPayload | null>(null)
const selectedClusterId = ref<number | null>(null)
const selectedMode = ref<'category' | 'topic'>('category')
const selectedCategory = ref('')
const selectedBookId = ref<number | undefined>()
const selectedTimeScope = ref('all')
const detailRef = ref<HTMLElement | null>(null)
const selectedGraphNodeName = ref('')
const graphJobStatus = ref<'' | 'queued' | 'processing' | 'success' | 'failed' | 'canceled'>('')
const graphJobMessage = ref('')
const { pollJob } = useJobPolling()

const overviewMetrics = computed(() => {
  const overview = payload.value?.overview
  if (!overview) return []

  return [
    {
      label: selectedMode.value === 'category' ? '领域节点' : '主题节点',
      value: overview.topic_count,
      hint: selectedMode.value === 'category' ? '按阅读领域建立一级聚类' : '从真实高亮与章节中提炼',
    },
    {
      label: selectedMode.value === 'category' ? '领域簇' : '主题簇',
      value: overview.cluster_count,
      hint: selectedMode.value === 'category' ? '历史、经济、心理等阅读板块' : '按主题共现自动聚合',
    },
    {
      label: '关联边',
      value: overview.edge_count,
      hint: selectedMode.value === 'category' ? '表示不同领域之间的话题重叠' : '表示主题之间的共读关系',
    },
    { label: '涉及书籍', value: overview.book_count, hint: '可直接回溯到原书和原笔记' },
  ]
})

const clusters = computed(() => payload.value?.clusters ?? [])
const graphNodes = computed(() => payload.value?.graph.nodes ?? [])
const graphLinks = computed(() => payload.value?.graph.links ?? [])
const availableCategories = computed(() => payload.value?.filters?.categories ?? [])
const availableBooks = computed(() => payload.value?.filters?.books ?? [])
const availableTimeScopes = computed(() => payload.value?.filters?.time_scopes ?? [])
const availableModes = computed(() => payload.value?.filters?.modes ?? [])
// 书籍选择器会跟随分类联动，避免用户选了“历史”分类，却仍然看到“哲学”书籍。
const filteredBooks = computed(() =>
  selectedCategory.value
    ? availableBooks.value.filter((book) => book.category === selectedCategory.value)
    : availableBooks.value,
)

const pageDescription = computed(() =>
  selectedMode.value === 'category'
    ? '先按历史、经济、心理、文学等阅读领域聚类，再展示每个领域内部的高频主题。'
    : '基于你真实读书笔记中的标签、章节和高亮共现关系，自动聚合出跨书知识主题网络。',
)
const activeFilterCount = computed(
  () => [selectedCategory.value, selectedBookId.value, selectedTimeScope.value !== 'all' ? selectedTimeScope.value : ''].filter(Boolean).length,
)

const selectedCluster = computed(() => {
  if (!clusters.value.length) return null
  if (selectedClusterId.value === null) return clusters.value[0]
  return clusters.value.find((cluster) => cluster.id === selectedClusterId.value) ?? clusters.value[0]
})

const graphLegend = computed(() => clusters.value.slice(0, 6))

const { clusterColor, graphOption } = useTopicGraphOption({
  graphNodes,
  graphLinks,
  clusters,
  selectedMode,
  selectedGraphNodeName,
})

async function loadGraph() {
  loading.value = true
  try {
    const response = await getTopicGraph({
      mode: selectedMode.value,
      category: selectedCategory.value || undefined,
      book_id: selectedBookId.value,
      time_scope: selectedTimeScope.value,
    })
    if (response.overview) {
      payload.value = response
      graphJobStatus.value = 'success'
      graphJobMessage.value = ''
      selectedClusterId.value = response.clusters[0]?.id ?? null
      selectedGraphNodeName.value = response.clusters[0]?.name ?? ''
      return
    }

    graphJobStatus.value = response.status || 'queued'
    graphJobMessage.value = response.message || '图谱分析任务已创建'
    payload.value = null
    selectedClusterId.value = null
    selectedGraphNodeName.value = ''
    if (response.job_id) {
      await pollGraphJob(response.job_id)
    }
  } catch (error) {
    graphJobStatus.value = 'failed'
    graphJobMessage.value = error instanceof Error ? error.message : '图谱分析失败'
    payload.value = null
  } finally {
    loading.value = false
  }
}

async function pollGraphJob(jobId: string) {
  await pollJob(jobId, {
    maxAttempts: 80,
    intervalMs: 1500,
    onProgress: (job) => {
      graphJobStatus.value = job.status
      graphJobMessage.value = job.message || ''
    },
    onSuccess: (job) => {
      if (!job.result) return
      payload.value = job.result as TopicGraphPayload
      selectedClusterId.value = payload.value.clusters[0]?.id ?? null
      selectedGraphNodeName.value = payload.value.clusters[0]?.name ?? ''
      ElMessage.success('图谱分析完成')
    },
    onFailed: (job) => {
      graphJobMessage.value = job.error_message || '图谱分析失败'
    },
    onTimeout: () => {
      graphJobMessage.value = '图谱仍在分析中，请稍后再看'
    },
  })
}

function handleCategoryChange() {
  if (selectedBookId.value) {
    const matched = filteredBooks.value.some((book) => book.id === selectedBookId.value)
    if (!matched) {
      selectedBookId.value = undefined
    }
  }
}

function resetFilters() {
  selectedMode.value = 'category'
  selectedCategory.value = ''
  selectedBookId.value = undefined
  selectedTimeScope.value = 'all'
  void loadGraph()
}

function selectCluster(clusterId: number) {
  selectedClusterId.value = clusterId
  const cluster = clusters.value.find((item) => item.id === clusterId)
  selectedGraphNodeName.value = cluster?.name ?? ''
}

async function focusCluster(clusterId: number, message?: string) {
  selectedClusterId.value = clusterId
  const cluster = clusters.value.find((item) => item.id === clusterId)
  selectedGraphNodeName.value = cluster?.name ?? ''
  if (message) {
    ElMessage.success(message)
  }
  await new Promise((resolve) => requestAnimationFrame(resolve))
  detailRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function handleChartClick(params: unknown) {
  const chartParams = params as {
    dataType?: string
    data?: { category?: number | null; name?: string | null } | null
  }
  if (chartParams.dataType !== 'node') return
  if (typeof chartParams.data?.category !== 'number') return
  selectedGraphNodeName.value = String(chartParams.data?.name ?? '')
  void focusCluster(chartParams.data.category, '已高亮对应主题簇，并定位到下方详情。')
}

function jumpToBook(bookId: number) {
  void router.push(`/books/${bookId}`)
}

function jumpToNote(bookId: number, noteId: number) {
  void router.push({
    path: '/notes',
    query: {
      bookId: String(bookId),
      noteId: String(noteId),
    },
  })
}

function openClusterAction(path: string) {
  void router.push(path)
}

onMounted(() => {
  void loadGraph()
})
</script>

<template>
  <div class="topic-graph-view">
    <PageHeader
      title="知识图谱"
      :description="pageDescription"
    />

    <TopicGraphControls
      v-model:selected-mode="selectedMode"
      v-model:selected-category="selectedCategory"
      v-model:selected-book-id="selectedBookId"
      v-model:selected-time-scope="selectedTimeScope"
      :active-filter-count="activeFilterCount"
      :available-modes="availableModes"
      :available-categories="availableCategories"
      :filtered-books="filteredBooks"
      :available-time-scopes="availableTimeScopes"
      @category-change="handleCategoryChange"
      @reset="resetFilters"
      @reload="loadGraph"
    />

    <section v-if="overviewMetrics.length" class="topic-graph-view__metrics">
      <AppMetricCard
        v-for="metric in overviewMetrics"
        :key="metric.label"
        :label="metric.label"
        :value="metric.value"
        :hint="metric.hint"
      />
    </section>

    <section class="topic-graph-view__layout">
      <AppCard class="topic-graph-view__clusters" v-loading="loading">
        <AppSection
          title="主题聚类"
          description="每个主题簇都能回溯到对应书籍和原始摘录，方便你理解为什么会被聚在一起。"
        />
        <div v-if="clusters.length" class="topic-graph-view__cluster-scroll">
          <div class="topic-graph-view__cluster-list">
            <article
              v-for="cluster in clusters"
              :key="cluster.id"
              class="topic-graph-view__cluster-card"
              :class="{ 'is-active': selectedCluster?.id === cluster.id }"
              @click="selectCluster(cluster.id)"
            >
              <div class="topic-graph-view__cluster-title">
                <span class="topic-graph-view__cluster-dot" :style="{ backgroundColor: clusterColor(cluster.id) }" />
                <strong>{{ cluster.name }}</strong>
              </div>
              <p>{{ cluster.note_count }} 条笔记 · {{ cluster.book_count }} 本书</p>
              <div class="topic-graph-view__topic-tags">
                <el-tag v-for="topic in cluster.topics.slice(0, 6)" :key="topic" round effect="plain">
                  {{ topic }}
                </el-tag>
              </div>
            </article>
          </div>
        </div>
        <div v-else-if="graphJobStatus === 'queued' || graphJobStatus === 'processing'" class="topic-graph-view__placeholder">
          <strong>{{ graphJobStatus === 'processing' ? '图谱正在分析中' : '图谱分析任务已创建' }}</strong>
          <p>{{ graphJobMessage || '你可以稍等片刻，分析完成后会自动展示新的主题聚类。' }}</p>
        </div>
        <div v-else class="topic-graph-view__placeholder">
          <strong>当前范围暂无图谱结果</strong>
          <p>尝试切换分析模式、分类或时间范围后重新分析。</p>
        </div>
      </AppCard>

      <AppCard class="topic-graph-view__graph" v-loading="loading">
        <AppSection
          title="主题关系图"
          description="节点代表主题，连线代表它们在同一条笔记或同一批书里反复共现。点击节点会联动左侧主题簇。"
        />
        <div v-if="clusters.length" class="topic-graph-view__graph-stage">
          <div class="topic-graph-view__graph-orbit" aria-hidden="true" />
          <div class="topic-graph-view__graph-toolbar">
            <div class="topic-graph-view__graph-focus">
              <span>当前聚焦</span>
              <strong>{{ selectedCluster?.name || '全部主题' }}</strong>
            </div>
            <div class="topic-graph-view__graph-legend" aria-label="主题簇颜色说明">
              <button
                v-for="cluster in graphLegend"
                :key="cluster.id"
                type="button"
                :class="{ 'is-active': selectedCluster?.id === cluster.id }"
                @click="selectCluster(cluster.id)"
              >
                <span :style="{ backgroundColor: clusterColor(cluster.id) }" />
                {{ cluster.name }}
              </button>
            </div>
          </div>
          <TopicGraphChart :option="graphOption" @click="handleChartClick" />
          <p class="topic-graph-view__graph-hint">可拖拽节点微调位置，点击节点查看对应主题簇。</p>
        </div>
        <div v-else-if="graphJobStatus === 'queued' || graphJobStatus === 'processing'" class="topic-graph-view__placeholder">
          <strong>{{ graphJobStatus === 'processing' ? '正在构建主题关系图' : '图谱分析任务已创建' }}</strong>
          <p>{{ graphJobMessage || '图谱会在后台分析完成后自动刷新，不会阻塞页面其他操作。' }}</p>
        </div>
        <div v-else class="topic-graph-view__placeholder">
          <strong>还没有可展示的关系图</strong>
          <p>请先选择一个更明确的分析范围，或点击“重新分析”。</p>
        </div>
      </AppCard>
    </section>

    <section v-if="selectedCluster" ref="detailRef" class="topic-graph-view__details">
      <TopicClusterDetail
        :cluster="selectedCluster"
        @open-action="openClusterAction"
        @jump-to-book="jumpToBook"
        @jump-to-note="jumpToNote"
      />
    </section>
  </div>
</template>

<style scoped lang="scss">
.topic-graph-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.topic-graph-view__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.topic-graph-view__layout {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
}

.topic-graph-view__clusters,
.topic-graph-view__graph {
  min-height: 680px;
}

.topic-graph-view__graph {
  position: relative;
  overflow: hidden;
  padding: 22px;
  background:
    radial-gradient(circle at 18% 8%, rgba(197, 139, 92, 0.16), transparent 26%),
    radial-gradient(circle at 88% 12%, rgba(47, 93, 80, 0.13), transparent 28%),
    linear-gradient(145deg, rgba(255, 253, 249, 0.98), rgba(248, 242, 232, 0.9));
}

.topic-graph-view__graph::before {
  content: '';
  position: absolute;
  inset: 18px;
  border: 1px solid rgba(216, 207, 191, 0.36);
  border-radius: 28px;
  pointer-events: none;
}

.topic-graph-view__graph-stage {
  position: relative;
  overflow: hidden;
  margin-top: 16px;
  min-height: 620px;
  border: 1px solid rgba(216, 207, 191, 0.58);
  border-radius: 30px;
  background:
    radial-gradient(circle at 50% 48%, rgba(47, 93, 80, 0.08), transparent 34%),
    linear-gradient(rgba(47, 93, 80, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(47, 93, 80, 0.035) 1px, transparent 1px),
    rgba(255, 253, 249, 0.78);
  background-size:
    auto,
    42px 42px,
    42px 42px,
    auto;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.8),
    0 18px 42px rgba(47, 93, 80, 0.08);
}

.topic-graph-view__graph-orbit {
  position: absolute;
  inset: 86px 12%;
  border: 1px dashed rgba(47, 93, 80, 0.16);
  border-radius: 999px;
  transform: rotate(-8deg);
}

.topic-graph-view__graph-orbit::before,
.topic-graph-view__graph-orbit::after {
  content: '';
  position: absolute;
  border: 1px dashed rgba(197, 139, 92, 0.16);
  border-radius: 999px;
}

.topic-graph-view__graph-orbit::before {
  inset: 34px 12%;
  transform: rotate(16deg);
}

.topic-graph-view__graph-orbit::after {
  inset: 78px 23%;
  transform: rotate(-20deg);
}

.topic-graph-view__graph-toolbar {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  padding: 16px 18px 0;
}

.topic-graph-view__graph-focus {
  min-width: 160px;
  padding: 10px 13px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.82);
  box-shadow: 0 12px 28px rgba(47, 93, 80, 0.08);
}

.topic-graph-view__graph-focus span {
  display: block;
  margin-bottom: 4px;
  color: var(--text-tertiary);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.topic-graph-view__graph-focus strong {
  color: var(--brand-primary);
}

.topic-graph-view__graph-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.topic-graph-view__graph-legend button {
  padding: 7px 10px;
  border: 1px solid rgba(216, 207, 191, 0.66);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.72);
  color: var(--text-secondary);
  display: inline-flex;
  gap: 7px;
  align-items: center;
  cursor: pointer;
  font-size: 0.82rem;
  font-weight: 800;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease,
    background 0.16s ease;
}

.topic-graph-view__graph-legend button:hover,
.topic-graph-view__graph-legend button.is-active {
  border-color: rgba(47, 93, 80, 0.24);
  background: rgba(255, 253, 249, 0.94);
  box-shadow: 0 10px 24px rgba(47, 93, 80, 0.1);
  transform: translateY(-1px);
}

.topic-graph-view__graph-legend span {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  box-shadow: 0 0 0 3px rgba(47, 93, 80, 0.08);
}

.topic-graph-view__graph-hint {
  position: absolute;
  right: 18px;
  bottom: 14px;
  z-index: 2;
  margin: 0;
  padding: 8px 11px;
  border: 1px solid rgba(216, 207, 191, 0.54);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.8);
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-weight: 700;
  backdrop-filter: blur(10px);
}

.topic-graph-view__cluster-scroll {
  max-height: 580px;
  overflow-y: auto;
  padding-right: 6px;
}

.topic-graph-view__cluster-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.topic-graph-view__cluster-card {
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: 18px;
  background: rgba(251, 248, 242, 0.72);
  cursor: pointer;
  transition: 0.2s ease;
}

.topic-graph-view__cluster-card.is-active,
.topic-graph-view__cluster-card:hover {
  border-color: rgba(47, 93, 80, 0.35);
  box-shadow: 0 0 0 2px rgba(47, 93, 80, 0.08);
  transform: translateY(-1px);
}

.topic-graph-view__cluster-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.topic-graph-view__cluster-title strong {
  font-size: 1rem;
}

.topic-graph-view__cluster-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
}

.topic-graph-view__cluster-card p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.topic-graph-view__topic-tags {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-graph-view__placeholder {
  min-height: 240px;
  display: grid;
  place-content: center;
  gap: 8px;
  text-align: center;
  color: var(--text-secondary);
}

.topic-graph-view__placeholder p {
  margin: 0;
}

@media (max-width: 1180px) {
  .topic-graph-view__layout {
    grid-template-columns: 1fr;
  }

  .topic-graph-view__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .topic-graph-view__graph-toolbar {
    flex-direction: column;
  }

  .topic-graph-view__graph-legend {
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .topic-graph-view__metrics {
    grid-template-columns: 1fr;
  }

  .topic-graph-view__graph {
    padding: 16px;
  }

  .topic-graph-view__graph-stage {
    min-height: 560px;
    border-radius: 24px;
  }

  .topic-graph-view__graph-focus {
    width: 100%;
  }

  .topic-graph-view__graph-hint {
    position: static;
    width: fit-content;
    margin: -10px 14px 14px;
  }

  .topic-graph-view__chart {
    height: 520px;
  }
}
</style>
