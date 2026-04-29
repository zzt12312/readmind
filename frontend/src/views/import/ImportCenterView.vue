<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import AppCard from '@/components/base/AppCard.vue'
import AppStatusBadge from '@/components/base/AppStatusBadge.vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import { buildImportMascotCue } from '@/constants/mascotMessages'
import { useImportStore } from '@/stores/import'

const importStore = useImportStore()
const router = useRouter()
const { jobs, loading, uploading, meta, syncFeedback } = storeToRefs(importStore)
const uploadDisabled = computed(() => !meta.value.demo_mode)

onMounted(() => {
  void importStore.load()
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
</script>

<template>
  <div class="import-view">
    <AppCard class="import-view__hero">
      <div>
        <p class="import-view__eyebrow">Import Pipeline</p>
        <h2>{{ meta.demo_mode ? '演示数据已经准备好' : '把你的 Obsidian 阅读笔记放进来' }}</h2>
        <p>
          {{
            meta.demo_mode
              ? meta.description
              : '当前开源版本优先支持本地 Obsidian 目录同步。配置 VAULT_ROOT 后点击同步，系统会扫描 Markdown 笔记并更新缓存。'
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
        <div
          v-if="syncFeedback.status !== 'idle'"
          class="import-view__sync-feedback"
          :class="`is-${syncFeedback.status}`"
        >
          <div>
            <span>{{ syncFeedback.status === 'processing' ? '同步进行中' : '同步反馈' }}</span>
            <strong>{{ syncFeedback.title }}</strong>
            <p>{{ syncFeedback.message }}</p>
          </div>
          <MascotBubble
            :mood="mascotCue.mood"
            :message="mascotCue.message"
            :celebrating="mascotCue.celebrating"
            compact
          />
          <div v-if="syncFeedback.status === 'success'" class="import-view__sync-stats">
            <article>
              <strong>{{ syncFeedback.book_count }}</strong>
              <span>本书</span>
            </article>
            <article>
              <strong>{{ syncFeedback.note_count }}</strong>
              <span>条笔记</span>
            </article>
            <article>
              <strong>{{ syncFeedback.category_count }}</strong>
              <span>个分类</span>
            </article>
          </div>
          <div v-if="syncFeedback.status === 'success'" class="import-view__sync-actions">
            <button type="button" @click="openNextStep('/notes')">整理笔记</button>
            <button type="button" @click="openNextStep('/analytics')">查看看板</button>
            <button type="button" @click="openNextStep('/review')">开始复习</button>
          </div>
        </div>
      </div>
      <div class="import-view__upload-panel" :class="{ 'is-disabled': uploadDisabled }">
        <p>{{ meta.demo_mode ? '演示上传' : '本地同步优先' }}</p>
        <el-upload drag :http-request="handleUpload" :show-file-list="false" :multiple="true" :disabled="uploadDisabled">
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            {{
              uploading
                ? '正在创建导入任务...'
                : (meta.demo_mode ? '拖拽文件体验模拟导入流程' : '直接上传暂未开放')
            }}
          </div>
        </el-upload>
        <span>{{ meta.demo_mode ? '不会写入真实用户数据' : '请使用左侧按钮扫描 VAULT_ROOT' }}</span>
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

.import-view__hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 24px;
  align-items: center;
  padding: 26px 28px;
  background:
    radial-gradient(circle at 92% 12%, rgba(192, 139, 92, 0.2), transparent 28%),
    linear-gradient(135deg, rgba(47, 93, 80, 0.1), rgba(255, 253, 249, 0.96) 58%),
    var(--bg-card);
}

.import-view__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
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

.import-view__upload-panel {
  padding: 14px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.76);
}

.import-view__upload-panel > p {
  margin: 0 0 10px;
  color: var(--brand-primary);
  font-weight: 800;
}

.import-view__upload-panel > span {
  display: block;
  margin-top: 10px;
  color: var(--text-tertiary);
  font-size: 0.84rem;
  line-height: 1.6;
}

.import-view__upload-panel.is-disabled {
  opacity: 0.86;
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

.import-view__sync-feedback {
  margin-top: 14px;
  padding: 14px;
  display: grid;
  gap: 12px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 18px;
  background:
    radial-gradient(circle at 100% 0%, rgba(47, 93, 80, 0.1), transparent 40%),
    rgba(255, 253, 249, 0.74);
}

.import-view__sync-feedback.is-failed {
  border-color: rgba(190, 76, 60, 0.18);
  background:
    radial-gradient(circle at 100% 0%, rgba(190, 76, 60, 0.1), transparent 40%),
    rgba(255, 253, 249, 0.74);
}

.import-view__sync-feedback > div:first-child > span {
  color: var(--brand-primary);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.import-view__sync-feedback > div:first-child > strong {
  display: block;
  margin-top: 5px;
}

.import-view__sync-feedback > div:first-child > p {
  margin-top: 6px;
  line-height: 1.7;
}

.import-view__sync-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.import-view__sync-stats article {
  padding: 10px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
}

.import-view__sync-stats strong,
.import-view__sync-stats span {
  display: block;
}

.import-view__sync-stats strong {
  color: var(--brand-primary);
  font-size: 1.35rem;
}

.import-view__sync-stats span {
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.import-view__sync-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.import-view__sync-actions button {
  padding: 9px 12px;
  border: 1px solid rgba(47, 93, 80, 0.16);
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 900;
}

.import-view__sync-actions button:first-child {
  background: var(--brand-primary);
  color: #fff;
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

  .import-view__sync-stats {
    grid-template-columns: 1fr;
  }
}
</style>
