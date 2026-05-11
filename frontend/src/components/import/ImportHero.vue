<script setup lang="ts">
import type { UploadRequestOptions } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import MascotBubble from '@/components/mascot/MascotBubble.vue'
import type { MascotCue } from '@/constants/mascotMessages'
import type { ImportMeta, ImportSyncFeedback } from '@/types/import'

defineProps<{
  meta: ImportMeta
  uploading: boolean
  uploadDisabled: boolean
  syncFeedback: ImportSyncFeedback
  mascotCue: MascotCue
  handleUpload: (options: UploadRequestOptions) => Promise<void>
}>()

defineEmits<{
  syncLocal: []
  openNextStep: [path: string]
}>()
</script>

<template>
  <AppCard class="import-hero">
    <div>
      <p class="import-hero__eyebrow">Import Pipeline</p>
      <h2>{{ meta.demo_mode ? '演示数据已经准备好' : '把你的 Obsidian 阅读笔记放进来' }}</h2>
      <p>
        {{
          meta.demo_mode
            ? meta.description
            : '当前开源版本优先支持本地 Obsidian 目录同步。配置 VAULT_ROOT 后点击同步，系统会扫描 Markdown 笔记并更新缓存。'
        }}
      </p>

      <div class="import-hero__actions">
        <el-button type="primary" round :loading="uploading" @click="$emit('syncLocal')">
          {{ meta.demo_mode ? '刷新演示数据' : '同步本地书库' }}
        </el-button>
        <span>{{ meta.source_label }}</span>
      </div>

      <div class="import-hero__vault-status" :class="`is-${meta.vault_status || 'ready'}`">
        <strong>当前读取目录</strong>
        <code>{{ meta.vault_root || '未配置' }}</code>
        <p>{{ meta.vault_message }}</p>
      </div>

      <div
        v-if="syncFeedback.status !== 'idle'"
        class="import-hero__sync-feedback"
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

        <div v-if="syncFeedback.status === 'success'" class="import-hero__sync-stats">
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

        <div v-if="syncFeedback.status === 'success'" class="import-hero__sync-actions">
          <button type="button" @click="$emit('openNextStep', '/notes')">整理笔记</button>
          <button type="button" @click="$emit('openNextStep', '/analytics')">查看看板</button>
          <button type="button" @click="$emit('openNextStep', '/review')">开始复习</button>
        </div>
      </div>
    </div>

    <div class="import-hero__upload-panel" :class="{ 'is-disabled': uploadDisabled }">
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
</template>

<style scoped lang="scss">
.import-hero {
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

.import-hero__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.import-hero h2 {
  margin: 0 0 10px;
}

.import-hero p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.8;
}

.import-hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  margin-top: 18px;
}

.import-hero__actions span {
  color: var(--text-tertiary);
  font-size: 0.9rem;
}

.import-hero__vault-status {
  margin-top: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(47, 93, 80, 0.08);
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
}

.import-hero__vault-status strong,
.import-hero__vault-status code,
.import-hero__vault-status p {
  display: block;
}

.import-hero__vault-status code {
  margin-top: 8px;
  padding: 6px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  color: var(--text-secondary);
  word-break: break-all;
}

.import-hero__vault-status p {
  margin: 10px 0 0;
  color: var(--text-tertiary);
}

.import-hero__vault-status.is-missing,
.import-hero__vault-status.is-invalid,
.import-hero__vault-status.is-empty {
  border-color: rgba(190, 76, 60, 0.14);
  background: rgba(190, 76, 60, 0.08);
}

.import-hero__sync-feedback {
  display: grid;
  gap: 12px;
  margin-top: 14px;
  padding: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 18px;
  background:
    radial-gradient(circle at 100% 0%, rgba(47, 93, 80, 0.1), transparent 40%),
    rgba(255, 253, 249, 0.74);
}

.import-hero__sync-feedback.is-failed {
  border-color: rgba(190, 76, 60, 0.18);
  background:
    radial-gradient(circle at 100% 0%, rgba(190, 76, 60, 0.1), transparent 40%),
    rgba(255, 253, 249, 0.74);
}

.import-hero__sync-feedback > div:first-child > span {
  color: var(--brand-primary);
  font-size: 0.76rem;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.import-hero__sync-feedback > div:first-child > strong {
  display: block;
  margin-top: 5px;
}

.import-hero__sync-feedback > div:first-child > p {
  margin-top: 6px;
  line-height: 1.7;
}

.import-hero__sync-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.import-hero__sync-stats article {
  padding: 10px;
  border-radius: 14px;
  background: rgba(47, 93, 80, 0.06);
}

.import-hero__sync-stats strong,
.import-hero__sync-stats span {
  display: block;
}

.import-hero__sync-stats strong {
  color: var(--brand-primary);
  font-size: 1.35rem;
}

.import-hero__sync-stats span {
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

.import-hero__sync-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.import-hero__sync-actions button {
  padding: 9px 12px;
  border: 1px solid rgba(47, 93, 80, 0.16);
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 900;
}

.import-hero__sync-actions button:first-child {
  background: var(--brand-primary);
  color: #fff;
}

.import-hero__upload-panel {
  padding: 14px;
  border: 1px solid rgba(216, 207, 191, 0.72);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.76);
}

.import-hero__upload-panel > p {
  margin: 0 0 10px;
  color: var(--brand-primary);
  font-weight: 800;
}

.import-hero__upload-panel > span {
  display: block;
  margin-top: 10px;
  color: var(--text-tertiary);
  font-size: 0.84rem;
  line-height: 1.6;
}

.import-hero__upload-panel.is-disabled {
  opacity: 0.86;
}

@media (max-width: 960px) {
  .import-hero {
    grid-template-columns: 1fr;
  }

  .import-hero__sync-stats {
    grid-template-columns: 1fr;
  }
}
</style>
