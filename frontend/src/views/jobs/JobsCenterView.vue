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
    >
      <div class="jobs-center__actions">
        <el-select v-model="selectedStatus" clearable placeholder="按状态筛选" style="width: 160px">
          <el-option label="排队中" value="queued" />
          <el-option label="处理中" value="processing" />
          <el-option label="已完成" value="success" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-select v-model="selectedJobType" clearable placeholder="按类型筛选" style="width: 180px">
          <el-option label="书籍摘要" value="book_summary" />
          <el-option label="笔记洞察" value="notes_insight" />
          <el-option label="本地同步" value="vault_sync" />
          <el-option label="图谱分析" value="graph_analysis" />
        </el-select>
        <el-button round @click="loadJobs">刷新任务</el-button>
      </div>
    </PageHeader>

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

.jobs-center__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
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
    justify-content: stretch;
  }
}
</style>
