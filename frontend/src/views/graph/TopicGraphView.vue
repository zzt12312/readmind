<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppCard from '@/components/base/AppCard.vue'
import AppSection from '@/components/base/AppSection.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { getTopicGraph } from '@/api/modules/insights'
import { useJobPolling } from '@/composables/useJobPolling'
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
const { pollJob } = useJobPolling()

const palette = ['#2f5d50', '#c58b5c', '#557f73', '#8c6f5a', '#4f7388', '#9a7650']

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
        borderWidth: isSelectedNode ? 5 : 2,
        borderColor: isSelectedNode ? '#fffdf9' : 'rgba(255, 253, 249, 0.92)',
        shadowBlur: isSelectedNode ? 28 : 14,
        shadowColor: isSelectedNode ? 'rgba(47, 93, 80, 0.28)' : 'rgba(47, 93, 80, 0.16)',
      },
      label: {
        show: true,
        color: '#24312d',
        fontSize: isSelectedNode ? 15 : selectedMode.value === 'category' ? 14 : 13,
        fontWeight: isSelectedNode ? 800 : 700,
        backgroundColor: 'rgba(255, 253, 249, 0.78)',
        borderColor: 'rgba(216, 207, 191, 0.5)',
        borderWidth: 1,
        borderRadius: 10,
        padding: [4, 7],
      },
      emphasis: {
        scale: true,
        itemStyle: {
          borderColor: '#fffdf9',
          borderWidth: 5,
          shadowBlur: 30,
          shadowColor: 'rgba(47, 93, 80, 0.3)',
        },
        label: {
          color: '#1f3932',
          fontWeight: 900,
        },
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
        color: isSelectedLink ? 'rgba(47, 93, 80, 0.48)' : 'rgba(47, 93, 80, 0.18)',
        width: Math.max(1, Math.min(link.value, selectedMode.value === 'category' ? 8 : 5)),
        opacity: isSelectedLink ? 0.95 : 0.62,
        curveness: selectedMode.value === 'category' ? 0.22 : 0.12,
      },
      emphasis: {
        lineStyle: {
          color: 'rgba(47, 93, 80, 0.58)',
          opacity: 1,
          width: Math.max(2, Math.min(link.value + 1, selectedMode.value === 'category' ? 9 : 6)),
        },
      },
    }
  })

  return {
    backgroundColor: 'transparent',
    color: palette,
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(36, 49, 45, 0.94)',
      borderColor: 'rgba(255, 253, 249, 0.16)',
      borderWidth: 1,
      extraCssText: 'border-radius: 14px; box-shadow: 0 16px 34px rgba(36, 49, 45, 0.24);',
      padding: [10, 12],
      textStyle: {
        color: '#f6f1e7',
        fontSize: 13,
      },
      formatter: (params: { dataType?: string; data?: Record<string, unknown> }) => {
        if (params.dataType === 'edge') {
          return `<strong>${String(params.data?.source)} ↔ ${String(params.data?.target)}</strong><br/>关联强度：${String(params.data?.value)}`
        }
        return `<strong>${String(params.data?.name)}</strong><br/>关联笔记：${String(params.data?.value)}`
      },
    },
    series: [
      {
        type: 'graph',
        layout: selectedMode.value === 'category' ? 'circular' : 'force',
        roam: false,
        draggable: true,
        focusNodeAdjacency: true,
        edgeSymbol: ['none', 'circle'],
        edgeSymbolSize: [0, 5],
        force: {
          repulsion: selectedMode.value === 'category' ? 520 : 340,
          edgeLength: selectedMode.value === 'category' ? [170, 280] : [110, 200],
          gravity: selectedMode.value === 'category' ? 0.02 : 0.04,
          friction: 0.18,
        },
        circular: {
          rotateLabel: false,
        },
        left: 36,
        right: 36,
        top: 44,
        bottom: 40,
        data: nodes,
        links,
        categories: clusters.value.map((cluster) => ({
          name: cluster.name,
          itemStyle: { color: clusterColor(cluster.id) },
        })),
        lineStyle: {
          cap: 'round',
        },
        emphasis: {
          focus: 'adjacency',
          blurScope: 'coordinateSystem',
        },
        blur: {
          itemStyle: {
            opacity: 0.28,
          },
          lineStyle: {
            opacity: 0.12,
          },
          label: {
            opacity: 0.35,
          },
        },
        animationDuration: 900,
        animationDurationUpdate: 700,
        animationEasingUpdate: 'cubicOut',
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

    <AppCard class="topic-graph-view__control-panel">
      <div class="topic-graph-view__control-glow" aria-hidden="true" />
      <div class="topic-graph-view__control-header">
        <div>
          <p>Graph Controls</p>
          <h3>图谱筛选</h3>
        </div>
        <div class="topic-graph-view__filter-status" :class="{ 'is-active': activeFilterCount }">
          <span>{{ activeFilterCount ? `${activeFilterCount} 个筛选` : '全量视图' }}</span>
          <strong>{{ selectedMode === 'category' ? '领域聚类' : '主题共现' }}</strong>
        </div>
      </div>
      <div class="topic-graph-view__control-grid">
        <label class="topic-graph-view__control-field is-mode">
          <span>分析方式</span>
          <el-segmented v-model="selectedMode" :options="availableModes" />
        </label>
        <label class="topic-graph-view__control-field">
          <span>分类</span>
          <el-select
            v-model="selectedCategory"
            clearable
            placeholder="全部分类"
            @change="handleCategoryChange"
          >
            <el-option v-for="category in availableCategories" :key="category" :label="category" :value="category" />
          </el-select>
        </label>
        <label class="topic-graph-view__control-field">
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
        <label class="topic-graph-view__control-field">
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
        <div class="topic-graph-view__control-actions">
          <el-button round @click="resetFilters">重置</el-button>
          <el-button type="primary" round @click="loadGraph">重新分析</el-button>
        </div>
      </div>
    </AppCard>

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
      <AppCard>
        <AppSection
          :title="`主题簇：${selectedCluster.name}`"
          description="这里展示这个主题簇最常一起出现的书和代表性摘录，方便你继续追溯原始上下文。"
        />
        <div v-if="selectedCluster.actions?.length" class="topic-graph-view__actions">
          <article
            v-for="action in selectedCluster.actions"
            :key="`${selectedCluster.id}-${action.type}`"
            :class="`is-${action.type}`"
          >
            <strong>{{ action.label }}</strong>
            <p>{{ action.description }}</p>
            <button type="button" @click="openClusterAction(action.path)">开始</button>
          </article>
        </div>
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

.topic-graph-view__layout {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
}

.topic-graph-view__control-panel {
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

.topic-graph-view__control-panel::before {
  content: '';
  position: absolute;
  inset: 12px;
  border: 1px solid rgba(255, 253, 249, 0.74);
  border-radius: 24px;
  pointer-events: none;
}

.topic-graph-view__control-glow {
  position: absolute;
  right: -48px;
  top: -76px;
  width: 190px;
  height: 190px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(197, 139, 92, 0.18), transparent 68%);
  pointer-events: none;
}

.topic-graph-view__control-header {
  position: relative;
  z-index: 1;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.topic-graph-view__control-header p {
  margin: 0 0 4px;
  color: var(--brand-accent);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.topic-graph-view__control-header h3 {
  margin: 0;
  color: var(--brand-primary);
}

.topic-graph-view__filter-status {
  min-width: 136px;
  padding: 9px 12px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.72);
  box-shadow: 0 10px 24px rgba(47, 93, 80, 0.08);
  text-align: right;
}

.topic-graph-view__filter-status span {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.76rem;
  font-weight: 800;
}

.topic-graph-view__filter-status strong {
  display: block;
  margin-top: 3px;
  color: var(--brand-primary);
  font-size: 0.95rem;
}

.topic-graph-view__filter-status.is-active {
  border-color: rgba(47, 93, 80, 0.24);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.86)),
    rgba(255, 253, 249, 0.86);
}

.topic-graph-view__control-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(220px, 1.1fr) minmax(150px, 0.8fr) minmax(220px, 1fr) minmax(150px, 0.7fr) auto;
  gap: 14px;
  align-items: end;
}

.topic-graph-view__control-field {
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

.topic-graph-view__control-field > span {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.03em;
}

.topic-graph-view__control-field :deep(.el-select),
.topic-graph-view__control-field :deep(.el-segmented) {
  width: 100%;
}

.topic-graph-view__control-field :deep(.el-select__wrapper),
.topic-graph-view__control-field :deep(.el-segmented) {
  min-height: 42px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.92);
  box-shadow: none;
}

.topic-graph-view__control-field :deep(.el-select__wrapper) {
  border: 1px solid rgba(216, 207, 191, 0.66);
}

.topic-graph-view__control-field :deep(.el-select__wrapper.is-focused) {
  border-color: rgba(47, 93, 80, 0.34);
  box-shadow: 0 0 0 3px rgba(47, 93, 80, 0.08);
}

.topic-graph-view__control-field :deep(.el-segmented) {
  padding: 3px;
  border: 1px solid rgba(216, 207, 191, 0.66);
  border-radius: 999px;
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(248, 242, 232, 0.76));
}

.topic-graph-view__control-field :deep(.el-segmented__group) {
  gap: 3px;
}

.topic-graph-view__control-field :deep(.el-segmented__item) {
  border-radius: 999px;
  color: var(--text-secondary);
  font-weight: 800;
  transition:
    color 0.18s ease,
    transform 0.18s ease,
    background 0.18s ease;
}

.topic-graph-view__control-field :deep(.el-segmented__item:hover:not(.is-selected)) {
  background: rgba(47, 93, 80, 0.06);
  color: var(--brand-primary);
  transform: translateY(-1px);
}

.topic-graph-view__control-field :deep(.el-segmented__item-label) {
  padding-inline: 8px;
}

.topic-graph-view__control-field :deep(.el-segmented__item-selected) {
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

.topic-graph-view__control-actions {
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.46);
  border-radius: 20px;
  background: rgba(255, 253, 249, 0.5);
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.topic-graph-view__control-actions :deep(.el-button) {
  min-height: 42px;
  padding-inline: 18px;
  font-weight: 900;
}

.topic-graph-view__control-actions :deep(.el-button--primary) {
  border-color: transparent;
  background:
    linear-gradient(135deg, var(--brand-primary), #447967);
  box-shadow: 0 12px 26px rgba(47, 93, 80, 0.18);
}

.topic-graph-view__control-actions :deep(.el-button:not(.el-button--primary)) {
  border-color: rgba(216, 207, 191, 0.72);
  background: rgba(255, 253, 249, 0.86);
  color: var(--text-secondary);
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

.topic-graph-view__detail-grid {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 16px;
}

.topic-graph-view__actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}

.topic-graph-view__actions article {
  min-width: 0;
  padding: 15px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 18px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.9), rgba(248, 242, 232, 0.68)),
    var(--bg-card);
}

.topic-graph-view__actions article.is-qa {
  border-color: rgba(47, 93, 80, 0.18);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.82)),
    var(--bg-card);
}

.topic-graph-view__actions strong {
  display: block;
  color: var(--brand-primary);
}

.topic-graph-view__actions p {
  min-height: 3.2em;
  margin: 7px 0 12px;
  color: var(--text-secondary);
  font-size: 0.86rem;
  line-height: 1.6;
}

.topic-graph-view__actions button {
  padding: 9px 13px;
  border: 0;
  border-radius: 999px;
  background: var(--brand-primary);
  color: #fff;
  cursor: pointer;
  font-weight: 900;
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
  .topic-graph-view__detail-grid,
  .topic-graph-view__actions,
  .topic-graph-view__control-grid {
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
  .topic-graph-view__metrics,
  .topic-graph-view__book-list {
    grid-template-columns: 1fr;
  }

  .topic-graph-view__control-actions {
    justify-content: flex-start;
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
