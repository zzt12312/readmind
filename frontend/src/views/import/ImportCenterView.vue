<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import AppCard from '@/components/base/AppCard.vue'
import AppStatusBadge from '@/components/base/AppStatusBadge.vue'
import { useImportStore } from '@/stores/import'

const importStore = useImportStore()
const { jobs, loading, uploading, meta } = storeToRefs(importStore)

onMounted(() => {
  void importStore.load()
})

async function handleUpload(options: UploadRequestOptions) {
  const normalized = [options.file as File]

  try {
    await importStore.upload(normalized)
    ElMessage.success('导入任务已创建')
    options.onSuccess?.({})
  } catch (error) {
    ElMessage.error('导入失败，请稍后重试')
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
</script>

<template>
  <div class="import-view">
    <AppCard class="import-view__hero">
      <div>
        <h2>{{ meta.demo_mode ? '演示数据已经准备好' : '把你的 Obsidian 阅读笔记放进来' }}</h2>
        <p>
          {{
            meta.demo_mode
              ? meta.description
              : '支持 markdown 文件和压缩包导入，系统会自动完成结构化解析、标签提取和 AI 整理。'
          }}
        </p>
        <div class="import-view__hero-actions">
          <el-button type="primary" round :loading="uploading" @click="handleSyncLocal">
            {{ meta.demo_mode ? '刷新演示数据' : '同步本地书库' }}
          </el-button>
          <span>{{ meta.source_label }}</span>
        </div>
        <div class="import-view__vault-status" :class="`is-${meta.vault_status || 'ready'}`">
          <strong>当前读取目录</strong>
          <code>{{ meta.vault_root || '未配置' }}</code>
          <p>{{ meta.vault_message }}</p>
        </div>
      </div>
      <el-upload drag :http-request="handleUpload" :show-file-list="false" :multiple="true">
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          {{
            uploading
              ? '正在创建导入任务...'
              : (meta.demo_mode ? '演示模式下会模拟导入流程，便于体验页面交互' : '拖拽文件到这里，或点击上传')
          }}
        </div>
      </el-upload>
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

.import-view__hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
  align-items: center;
}

.import-view__hero h2 {
  margin: 0 0 10px;
}

.import-view__hero p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.import-view__hero-actions {
  margin-top: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.import-view__hero-actions span {
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.import-view__vault-status {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
  border: 1px solid rgba(47, 93, 80, 0.08);
}

.import-view__vault-status strong,
.import-view__vault-status code,
.import-view__vault-status p {
  display: block;
}

.import-view__vault-status code {
  margin-top: 8px;
  padding: 6px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  color: var(--text-secondary);
  word-break: break-all;
}

.import-view__vault-status p {
  margin: 10px 0 0;
  color: var(--text-tertiary);
}

.import-view__vault-status.is-missing,
.import-view__vault-status.is-invalid,
.import-view__vault-status.is-empty {
  background: rgba(190, 76, 60, 0.08);
  border-color: rgba(190, 76, 60, 0.14);
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
  .import-view__hero {
    grid-template-columns: 1fr;
  }

  .import-view__job-item,
  .import-view__job-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
