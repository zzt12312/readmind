<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppCard from '@/components/base/AppCard.vue'
import AppSection from '@/components/base/AppSection.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { fetchJobDetail } from '@/api/modules/jobs'
import { getTopicGraph } from '@/api/modules/insights'
import type { TopicGraphLink, TopicGraphNode, TopicGraphPayload } from '@/types/insights'

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

const palette = ['#2f5d50', '#c08b5c', '#4d7487', '#7e685a', '#8f5b48', '#5f7b6c']

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

const selectedCluster = computed(() => {
  if (!clusters.value.length) return null
  if (selectedClusterId.value === null) return clusters.value[0]
  return clusters.value.find((cluster) => cluster.id === selectedClusterId.value) ?? clusters.value[0]
})

function clusterColor(clusterId: number) {
  return palette[((clusterId % palette.length) + palette.length) % palette.length]
}

// 图谱可视化用 cluster_id 做颜色分层，所有节点默认都保持清晰，
// 只在用户选中某个节点时用描边和阴影给出明确反馈，避免画面忽明忽暗。
const graphOption = computed(() => {
  const nodes = graphNodes.value.map((node: TopicGraphNode) => {
    const isSelectedNode = selectedGraphNodeName.value === node.name
    return {
      id: node.id,
      name: node.name,
      value: node.value,
      symbolSize:
        selectedMode.value === 'category'
          ? 44 + Math.min(node.book_count * 2.2, 24)
          : 22 + Math.min(node.note_count * 1.5, 28),
      category: node.cluster_id,
      itemStyle: {
        color: clusterColor(node.cluster_id),
        opacity: 0.96,
        borderWidth: isSelectedNode ? 4 : 0,
        borderColor: isSelectedNode ? 'rgba(36, 49, 45, 0.9)' : 'transparent',
        shadowBlur: isSelectedNode ? 20 : 10,
        shadowColor: isSelectedNode ? 'rgba(36, 49, 45, 0.22)' : 'rgba(47, 93, 80, 0.12)',
      },
      label: {
        show: true,
        color: '#24312d',
        fontSize: isSelectedNode ? 15 : selectedMode.value === 'category' ? 14 : 13,
        fontWeight: isSelectedNode ? 700 : 500,
      },
    }
  })

  const links = graphLinks.value.map((link: TopicGraphLink) => {
    const isSelectedLink =
      selectedGraphNodeName.value &&
      (String(link.source) === selectedGraphNodeName.value || String(link.target) === selectedGraphNodeName.value)
    return {
      ...link,
      lineStyle: {
        color: isSelectedLink ? 'rgba(36, 49, 45, 0.42)' : 'rgba(47, 93, 80, 0.22)',
        width: Math.max(1, Math.min(link.value, selectedMode.value === 'category' ? 8 : 5)),
        opacity: isSelectedLink ? 0.95 : 0.78,
        curveness: selectedMode.value === 'category' ? 0.18 : 0.08,
      },
    }
  })

  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(36, 42, 39, 0.92)',
      borderWidth: 0,
      textStyle: {
        color: '#f6f1e7',
      },
      formatter: (params: { dataType?: string; data?: Record<string, unknown> }) => {
        if (params.dataType === 'edge') {
          return `${String(params.data?.source)} ↔ ${String(params.data?.target)}<br/>关联强度：${String(params.data?.value)}`
        }
        return `${String(params.data?.name)}<br/>关联笔记：${String(params.data?.value)}`
      },
    },
    series: [
      {
        type: 'graph',
        layout: selectedMode.value === 'category' ? 'circular' : 'force',
        roam: false,
        draggable: true,
        focusNodeAdjacency: true,
        force: {
          repulsion: selectedMode.value === 'category' ? 420 : 280,
          edgeLength: selectedMode.value === 'category' ? [160, 260] : [90, 180],
          gravity: selectedMode.value === 'category' ? 0.02 : 0.04,
        },
        circular: {
          rotateLabel: false,
        },
        left: 24,
        right: 24,
        top: 24,
        bottom: 24,
        data: nodes,
        links,
      },
    ],
  }
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
  // 图谱分析是最重的一类总结任务之一，因此这里采用与摘要/洞察一致的后台任务轮询模式。
  for (let index = 0; index < 80; index += 1) {
    const job = await fetchJobDetail(jobId)
    graphJobStatus.value = job.status
    graphJobMessage.value = job.message || ''

    if (job.status === 'success' && job.result) {
      payload.value = job.result as TopicGraphPayload
      selectedClusterId.value = payload.value.clusters[0]?.id ?? null
      selectedGraphNodeName.value = payload.value.clusters[0]?.name ?? ''
      ElMessage.success('图谱分析完成')
      return
    }

    if (job.status === 'failed') {
      throw new Error(job.error_message || '图谱分析失败')
    }

    await new Promise((resolve) => window.setTimeout(resolve, 1500))
  }
  graphJobMessage.value = '图谱仍在分析中，请稍后再看'
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

onMounted(() => {
  void loadGraph()
})
</script>

<template>
  <div class="topic-graph-view">
    <PageHeader
      title="知识图谱"
      :description="pageDescription"
    >
      <div class="topic-graph-view__toolbar">
        <el-segmented v-model="selectedMode" :options="availableModes" />
        <el-select
          v-model="selectedCategory"
          clearable
          placeholder="按分类筛选"
          style="width: 180px"
          @change="handleCategoryChange"
        >
          <el-option v-for="category in availableCategories" :key="category" :label="category" :value="category" />
        </el-select>
        <el-select
          v-model="selectedBookId"
          clearable
          filterable
          placeholder="按书籍筛选"
          style="width: 220px"
        >
          <el-option v-for="book in filteredBooks" :key="book.id" :label="book.title" :value="book.id" />
        </el-select>
        <el-select v-model="selectedTimeScope" style="width: 160px">
          <el-option
            v-for="option in availableTimeScopes"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-button round @click="resetFilters">重置</el-button>
        <el-button type="primary" round @click="loadGraph">重新分析</el-button>
      </div>
    </PageHeader>

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
        <TopicGraphChart v-if="clusters.length" :option="graphOption" @click="handleChartClick" />
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
      <AppCard>
        <AppSection
          :title="`主题簇：${selectedCluster.name}`"
          description="这里展示这个主题簇最常一起出现的书和代表性摘录，方便你继续追溯原始上下文。"
        />
        <div class="topic-graph-view__detail-grid">
          <div class="topic-graph-view__books">
            <h4>相关书籍</h4>
            <div class="topic-graph-view__book-list">
              <button
                v-for="book in selectedCluster.sample_books"
                :key="book.id"
                type="button"
                class="topic-graph-view__book-chip"
                @click="jumpToBook(book.id)"
              >
                <img v-if="book.cover" :src="book.cover" :alt="book.title" loading="lazy" />
                <span v-else>{{ book.title.slice(0, 2) }}</span>
                <strong>{{ book.title }}</strong>
              </button>
            </div>
          </div>

          <div class="topic-graph-view__samples">
            <h4>代表性摘录</h4>
            <article
              v-for="sample in selectedCluster.sample_excerpts"
              :key="sample.note_id"
              class="topic-graph-view__sample-card"
            >
              <strong>{{ sample.book_title }}</strong>
              <p>{{ sample.excerpt }}</p>
              <el-button text @click="jumpToNote(sample.book_id, sample.note_id)">跳转原笔记</el-button>
            </article>
          </div>
        </div>
      </AppCard>
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

.topic-graph-view__toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
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

.topic-graph-view__detail-grid {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 16px;
}

.topic-graph-view__books h4,
.topic-graph-view__samples h4 {
  margin: 0 0 12px;
}

.topic-graph-view__book-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.topic-graph-view__book-chip {
  padding: 12px;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.92);
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: left;
  cursor: pointer;
}

.topic-graph-view__book-chip img,
.topic-graph-view__book-chip span {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 12px;
  object-fit: cover;
  background: linear-gradient(135deg, rgba(47, 93, 80, 0.18), rgba(192, 139, 92, 0.24));
  display: grid;
  place-items: center;
  color: var(--brand-primary);
  font-weight: 700;
}

.topic-graph-view__sample-card {
  padding: 16px;
  border-radius: 16px;
  background: rgba(251, 248, 242, 0.78);
}

.topic-graph-view__sample-card + .topic-graph-view__sample-card {
  margin-top: 12px;
}

.topic-graph-view__sample-card p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

@media (max-width: 1180px) {
  .topic-graph-view__layout,
  .topic-graph-view__detail-grid {
    grid-template-columns: 1fr;
  }

  .topic-graph-view__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .topic-graph-view__metrics,
  .topic-graph-view__book-list {
    grid-template-columns: 1fr;
  }

  .topic-graph-view__toolbar {
    justify-content: stretch;
  }

  .topic-graph-view__chart {
    height: 520px;
  }
}
</style>
