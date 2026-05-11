<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import AppCard from '@/components/base/AppCard.vue'
import AppStatusBadge from '@/components/base/AppStatusBadge.vue'
import ImportHero from '@/components/import/ImportHero.vue'
import { buildImportMascotCue } from '@/constants/mascotMessages'
import { useAppStore } from '@/stores/app'
import { useImportStore } from '@/stores/import'
import { useQaStore } from '@/stores/qa'

const importStore = useImportStore()
const appStore = useAppStore()
const qaStore = useQaStore()
const router = useRouter()
const { jobs, loading, uploading, meta, syncFeedback } = storeToRefs(importStore)
const { llmHealth } = storeToRefs(appStore)
const uploadDisabled = computed(() => !meta.value.demo_mode)

onMounted(() => {
  void importStore.load()
  void appStore.loadLlmHealth()
})

async function handleUpload(options: UploadRequestOptions) {
  if (!meta.value.demo_mode) {
    const message = '当前版本请使用“同步本地书库”，直接上传导入还没有开放。'
    ElMessage.warning(message)
    const uploadError = Object.assign(new Error(message), {
      status: 501,
      method: 'POST',
      url: '/api/import/jobs',
    })
    options.onError?.(uploadError)
    return
  }

  const normalized = [options.file as File]

  try {
    await importStore.upload(normalized)
    ElMessage.success('导入任务已创建')
    options.onSuccess?.({})
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '导入失败，请稍后重试')
    const uploadError = Object.assign(new Error('Upload failed'), {
      status: 500,
      method: 'POST',
      url: '/api/import/jobs',
    })
    options.onError?.(uploadError)
  }
}

async function handleSyncLocal() {
  try {
    await importStore.syncLocal()
    ElMessage.success(meta.value.demo_mode ? '演示数据已经就绪' : '已经重新扫描本地 Obsidian 书库')
  } catch {
    ElMessage.error('同步本地书库失败')
  }
}

function openNextStep(path: string) {
  void router.push(path)
}

const mascotCue = computed(() => buildImportMascotCue(syncFeedback.value))
const privacyItems = computed(() => [
  {
    label: '本地读取',
    value: meta.value.demo_mode ? '演示缓存' : (meta.value.vault_root || '未配置'),
    detail: meta.value.demo_mode
      ? '演示模式不会扫描你的真实 Obsidian 目录。'
      : '同步时只扫描 VAULT_ROOT 指向的 Markdown 阅读笔记目录。',
  },
  {
    label: '模型请求',
    value: llmHealth.value?.demo_mode
      ? '演示模式不调用模型'
      : llmHealth.value?.connected
        ? `${llmHealth.value.provider} / ${llmHealth.value.model}`
        : '模型不可用，使用本地回退',
    detail: '只有主动触发摘要、洞察或问答时，命中的摘录片段才会进入模型请求上下文。',
  },
  {
    label: '导出位置',
    value: meta.value.export_root || 'exports/qa',
    detail: '问答 Markdown 导出会写入独立 exports 目录，导出内容默认不会提交到 Git。',
  },
  {
    label: '浏览器痕迹',
    value: '问答历史与收藏回答',
    detail: '这些内容保存在当前浏览器 localStorage 中，可在这里一键清理。',
  },
])

async function clearLocalQaData() {
  try {
    await ElMessageBox.confirm(
      '这会清空当前浏览器里的问答历史和收藏回答，不会删除 Obsidian 原始笔记，也不会删除已导出的 Markdown 文件。',
      '清理本地问答痕迹',
      {
        confirmButtonText: '清理',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
    qaStore.clearLocalQaData()
    ElMessage.success('本地问答历史和收藏回答已清理')
  } catch {
    // 用户取消时不需要提示。
  }
}
</script>

<template>
  <div class="import-view">
    <ImportHero
      :meta="meta"
      :uploading="uploading"
      :upload-disabled="uploadDisabled"
      :sync-feedback="syncFeedback"
      :mascot-cue="mascotCue"
      :handle-upload="handleUpload"
      @sync-local="handleSyncLocal"
      @open-next-step="openNextStep"
    />

    <AppCard class="import-view__privacy">
      <div class="import-view__privacy-head">
        <div>
          <p class="import-view__eyebrow">Privacy Boundary</p>
          <h3>数据边界与本地痕迹</h3>
        </div>
        <el-button round type="warning" plain @click="clearLocalQaData">清理问答痕迹</el-button>
      </div>
      <div class="import-view__privacy-grid">
        <article v-for="item in privacyItems" :key="item.label">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.detail }}</p>
        </article>
      </div>
    </AppCard>

    <AppCard v-loading="loading">
      <div class="import-view__table-header">
        <h3>导入任务</h3>
        <el-button text @click="importStore.load">刷新</el-button>
      </div>

      <div class="import-view__job-list">
        <article v-for="job in jobs" :key="job.id" class="import-view__job-item">
          <div>
            <strong>{{ job.file_name }}</strong>
            <p>{{ job.created_at ? `创建时间 ${job.created_at}` : '解析状态实时同步到工作台' }}</p>
          </div>
          <div class="import-view__job-meta">
            <AppStatusBadge :status="job.status" />
            <span>{{ job.progress }}%</span>
            <span>{{ job.result }}</span>
          </div>
        </article>
      </div>
    </AppCard>
  </div>
</template>

<style scoped lang="scss">
.import-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.import-view__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.import-view__privacy {
  padding: 22px;
  background:
    radial-gradient(circle at 92% 0%, rgba(47, 93, 80, 0.12), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(244, 238, 228, 0.72));
}

.import-view__privacy-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 16px;
}

.import-view__privacy-head h3 {
  margin: 0;
}

.import-view__privacy-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.import-view__privacy-grid article {
  min-width: 0;
  padding: 14px;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 18px;
  background: rgba(255, 253, 249, 0.76);
}

.import-view__privacy-grid span,
.import-view__privacy-grid strong {
  display: block;
}

.import-view__privacy-grid span {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
}

.import-view__privacy-grid strong {
  overflow: hidden;
  margin-top: 8px;
  color: var(--text-primary);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.import-view__privacy-grid p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.6;
}

.import-view__table-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.import-view__table-header h3 {
  margin: 0;
}

.import-view__job-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.import-view__job-item {
  padding: 16px 0;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  border-bottom: 1px solid var(--border-light);
}

.import-view__job-item:last-child {
  border-bottom: 0;
}

.import-view__job-item p {
  margin: 6px 0 0;
  color: var(--text-tertiary);
}

.import-view__job-meta {
  display: flex;
  align-items: center;
  gap: 18px;
}

@media (max-width: 960px) {
  .import-view__job-item,
  .import-view__job-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .import-view__privacy-head {
    flex-direction: column;
  }

  .import-view__privacy-grid {
    grid-template-columns: 1fr;
  }
}
</style>
