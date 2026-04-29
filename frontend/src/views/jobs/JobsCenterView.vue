<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AppCard from '@/components/base/AppCard.vue'
import AppEmpty from '@/components/base/AppEmpty.vue'
import AppMetricCard from '@/components/base/AppMetricCard.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { fetchJobList, retryJob } from '@/api/modules/jobs'
import type { AsyncJob } from '@/types/job'

const loading = ref(false)
const retryingJobId = ref('')
const jobs = ref<AsyncJob[]>([])
const selectedStatus = ref('')
const selectedJobType = ref('')

const overview = computed(() => {
  const queued = jobs.value.filter((job) => job.status === 'queued').length
  const processing = jobs.value.filter((job) => job.status === 'processing').length
  const success = jobs.value.filter((job) => job.status === 'success').length
  const failed = jobs.value.filter((job) => job.status === 'failed').length
  return [
    { label: '排队中', value: queued, hint: '等待后台 worker 开始处理' },
    { label: '处理中', value: processing, hint: '正在生成摘要、洞察、图谱或索引' },
    { label: '已完成', value: success, hint: '结果已经写入缓存，可直接复用' },
    { label: '失败', value: failed, hint: '可在任务中心重试失败任务' },
  ]
})

const filteredJobs = computed(() =>
  jobs.value.filter((job) => {
    if (selectedStatus.value && job.status !== selectedStatus.value) return false
    if (selectedJobType.value && job.job_type !== selectedJobType.value) return false
    return true
  }),
)
const activeFilterCount = computed(() => [selectedStatus.value, selectedJobType.value].filter(Boolean).length)

const jobTypeLabelMap: Record<string, string> = {
  book_summary: '书籍摘要',
  notes_insight: '笔记洞察',
  vault_sync: '本地同步',
  graph_analysis: '图谱分析',
}

function jobTypeLabel(jobType: string) {
  return jobTypeLabelMap[jobType] ?? jobType
}

function statusLabel(status: AsyncJob['status']) {
  if (status === 'queued') return '排队中'
  if (status === 'processing') return '处理中'
  if (status === 'success') return '已完成'
  if (status === 'failed') return '失败'
  return '已取消'
}

function statusTagType(status: AsyncJob['status']) {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'danger'
  if (status === 'processing') return 'warning'
  return 'info'
}

async function loadJobs() {
  loading.value = true
  try {
    const data = await fetchJobList({ limit: 80 })
    jobs.value = data.items
  } finally {
    loading.value = false
  }
}

async function retryFailedJob(jobId: string | number) {
  const normalizedId = String(jobId)
  retryingJobId.value = normalizedId
  try {
    await retryJob(normalizedId)
    ElMessage.success('任务已重新加入队列')
    await loadJobs()
  } finally {
    retryingJobId.value = ''
  }
}

onMounted(() => {
  void loadJobs()
})
</script>

<template>
  <div class="jobs-center">
    <PageHeader
      title="任务中心"
      description="统一查看书籍摘要、AI 洞察、本地同步与图谱分析的后台任务状态，也可以在这里重试失败任务。"
    />

    <AppCard class="jobs-center__filter-panel">
      <div class="jobs-center__filter-glow" aria-hidden="true" />
      <div class="jobs-center__filter-header">
        <div>
          <p>Task Filters</p>
          <h3>任务筛选</h3>
        </div>
        <div class="jobs-center__filter-status" :class="{ 'is-active': activeFilterCount }">
          <span>{{ activeFilterCount ? `${activeFilterCount} 个筛选` : '全部任务' }}</span>
          <strong>{{ filteredJobs.length }} / {{ jobs.length }}</strong>
        </div>
      </div>
      <div class="jobs-center__actions">
        <label>
          <span>状态</span>
          <el-select v-model="selectedStatus" clearable placeholder="全部状态">
          <el-option label="排队中" value="queued" />
          <el-option label="处理中" value="processing" />
          <el-option label="已完成" value="success" />
          <el-option label="失败" value="failed" />
        </el-select>
        </label>
        <label>
          <span>类型</span>
          <el-select v-model="selectedJobType" clearable placeholder="全部类型">
          <el-option label="书籍摘要" value="book_summary" />
          <el-option label="笔记洞察" value="notes_insight" />
          <el-option label="本地同步" value="vault_sync" />
          <el-option label="图谱分析" value="graph_analysis" />
        </el-select>
        </label>
        <div class="jobs-center__filter-buttons">
          <el-button round @click="selectedStatus = ''; selectedJobType = ''">重置</el-button>
          <el-button type="primary" round @click="loadJobs">刷新任务</el-button>
        </div>
      </div>
    </AppCard>

    <section class="jobs-center__metrics">
      <AppMetricCard
        v-for="metric in overview"
        :key="metric.label"
        :label="metric.label"
        :value="metric.value"
        :hint="metric.hint"
      />
    </section>

    <AppCard v-loading="loading">
      <div v-if="filteredJobs.length" class="jobs-center__list">
        <article v-for="job in filteredJobs" :key="job.id" class="jobs-center__item">
          <div class="jobs-center__main">
            <div class="jobs-center__title">
              <strong>{{ jobTypeLabel(job.job_type) }}</strong>
              <el-tag round :type="statusTagType(job.status)">{{ statusLabel(job.status) }}</el-tag>
            </div>
            <p class="jobs-center__message">{{ job.message || '暂无任务说明' }}</p>
            <p class="jobs-center__meta">
              资源：{{ job.resource_type }} / {{ job.resource_id }} · 创建时间：{{ job.created_at }}
            </p>
            <p v-if="job.error_message" class="jobs-center__error">错误：{{ job.error_message }}</p>
          </div>

          <div class="jobs-center__side">
            <el-progress
              :percentage="job.progress"
              :status="job.status === 'failed' ? 'exception' : job.status === 'success' ? 'success' : undefined"
              :stroke-width="8"
            />
            <el-button
              v-if="job.status === 'failed'"
              round
              :loading="retryingJobId === String(job.id)"
              @click="retryFailedJob(job.id)"
            >
              重试任务
            </el-button>
          </div>
        </article>
      </div>
      <AppEmpty
        v-else
        title="当前没有符合条件的任务"
        description="当你触发摘要生成、AI 洞察、本地同步或图谱分析时，任务会出现在这里。"
      />
    </AppCard>
  </div>
</template>

<style scoped lang="scss">
.jobs-center {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.jobs-center__filter-panel {
  position: relative;
  overflow: hidden;
  padding: 22px;
  border-color: rgba(216, 207, 191, 0.72);
  border-radius: 28px;
  background:
    radial-gradient(circle at 8% 0%, rgba(47, 93, 80, 0.14), transparent 28%),
    radial-gradient(circle at 92% 18%, rgba(197, 139, 92, 0.15), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(248, 242, 232, 0.92));
}

.jobs-center__filter-panel::before {
  content: '';
  position: absolute;
  inset: 12px;
  border: 1px solid rgba(255, 253, 249, 0.74);
  border-radius: 24px;
  pointer-events: none;
}

.jobs-center__filter-glow {
  position: absolute;
  right: -54px;
  top: -78px;
  width: 190px;
  height: 190px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(197, 139, 92, 0.18), transparent 68%);
  pointer-events: none;
}

.jobs-center__filter-header {
  position: relative;
  z-index: 1;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.jobs-center__filter-header p {
  margin: 0 0 4px;
  color: var(--brand-accent);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.jobs-center__filter-header h3 {
  margin: 0;
  color: var(--brand-primary);
}

.jobs-center__filter-status {
  min-width: 122px;
  padding: 9px 12px;
  border: 1px solid rgba(216, 207, 191, 0.62);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.72);
  box-shadow: 0 10px 24px rgba(47, 93, 80, 0.08);
  text-align: right;
}

.jobs-center__filter-status span {
  display: block;
  color: var(--text-tertiary);
  font-size: 0.76rem;
  font-weight: 800;
}

.jobs-center__filter-status strong {
  display: block;
  margin-top: 3px;
  color: var(--brand-primary);
  font-size: 0.95rem;
}

.jobs-center__filter-status.is-active {
  border-color: rgba(47, 93, 80, 0.24);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.08), rgba(255, 253, 249, 0.86)),
    rgba(255, 253, 249, 0.86);
}

.jobs-center__actions {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(180px, 1fr) minmax(200px, 1fr) auto;
  gap: 14px;
  align-items: end;
}

.jobs-center__actions label {
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

.jobs-center__actions label > span {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.03em;
}

.jobs-center__actions :deep(.el-select) {
  width: 100%;
}

.jobs-center__actions :deep(.el-select__wrapper) {
  min-height: 42px;
  border: 1px solid rgba(216, 207, 191, 0.66);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.92);
  box-shadow: none;
}

.jobs-center__actions :deep(.el-select__wrapper.is-focused) {
  border-color: rgba(47, 93, 80, 0.34);
  box-shadow: 0 0 0 3px rgba(47, 93, 80, 0.08);
}

.jobs-center__filter-buttons {
  padding: 12px;
  border: 1px solid rgba(216, 207, 191, 0.46);
  border-radius: 20px;
  background: rgba(255, 253, 249, 0.5);
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.jobs-center__filter-buttons :deep(.el-button) {
  min-height: 42px;
  padding-inline: 18px;
  font-weight: 900;
}

.jobs-center__filter-buttons :deep(.el-button--primary) {
  border-color: transparent;
  background:
    linear-gradient(135deg, var(--brand-primary), #447967);
  box-shadow: 0 12px 26px rgba(47, 93, 80, 0.18);
}

.jobs-center__filter-buttons :deep(.el-button:not(.el-button--primary)) {
  border-color: rgba(216, 207, 191, 0.72);
  background: rgba(255, 253, 249, 0.86);
  color: var(--text-secondary);
}

.jobs-center__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.jobs-center__list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.jobs-center__item {
  padding: 18px;
  border: 1px solid var(--border-light);
  border-radius: 18px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 18px;
  background: rgba(255, 253, 249, 0.88);
}

.jobs-center__title {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.jobs-center__message,
.jobs-center__meta,
.jobs-center__error {
  margin: 8px 0 0;
}

.jobs-center__message {
  color: var(--text-secondary);
}

.jobs-center__meta {
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.jobs-center__error {
  color: #b2523c;
}

.jobs-center__side {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 14px;
}

@media (max-width: 1100px) {
  .jobs-center__metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .jobs-center__item {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .jobs-center__metrics {
    grid-template-columns: 1fr;
  }

  .jobs-center__actions {
    grid-template-columns: 1fr;
  }

  .jobs-center__filter-buttons {
    justify-content: flex-start;
  }
}
</style>
