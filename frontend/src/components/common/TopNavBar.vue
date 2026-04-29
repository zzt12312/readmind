<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'

withDefaults(defineProps<{
  title: string
  eyebrow?: string
  contextLabel?: string
  contextValue?: string
}>(), {
  eyebrow: 'Personal knowledge workspace',
  contextLabel: '当前页',
  contextValue: '阅读工作台',
})

const appStore = useAppStore()
const authStore = useAuthStore()
const { llmHealth, llmLoading, embeddingWarming } = storeToRefs(appStore)
const { user } = storeToRefs(authStore)
let embeddingPollTimer: number | null = null

const providerLabel = computed(() => {
  return llmHealth.value?.demo_mode ? '演示模式' : 'DeepSeek'
})

const embeddingLabel = computed(() => {
  if (!llmHealth.value) return 'Embedding 未知'
  if (llmHealth.value.demo_mode && llmHealth.value.embedding_status !== 'ready') return '演示检索已就绪'
  if (embeddingWarming.value) return 'Embedding 自动预热中'
  if (llmHealth.value.embedding_status === 'ready') return 'Embedding 已就绪'
  if (llmHealth.value.embedding_status === 'loading') return 'Embedding 预热中'
  if (llmHealth.value.embedding_status === 'fallback') return 'Embedding 降级中'
  return 'Embedding 未预热'
})

const embeddingClass = computed(() => {
  if (!llmHealth.value) return 'is-missing'
  if (llmHealth.value.embedding_status === 'ready') return 'is-connected'
  if (llmHealth.value.embedding_status === 'loading') return 'is-checking'
  if (llmHealth.value.embedding_status === 'fallback') return 'is-fallback'
  return 'is-missing'
})

onMounted(async () => {
  if (!llmLoading.value) {
    await appStore.loadLlmHealth()
  }
  await startAutomaticEmbeddingWarmup()
})

onBeforeUnmount(() => {
  if (embeddingPollTimer !== null) {
    window.clearInterval(embeddingPollTimer)
  }
})

const llmLabel = computed(() => {
  if (llmLoading.value) {
    return '模型检查中'
  }
  if (!llmHealth.value) {
    return '模型状态未知'
  }
  if (llmHealth.value.demo_mode) {
    return '演示模式（已禁用 DeepSeek）'
  }
  if (!llmHealth.value.api_key_loaded) {
    return `未配置 ${providerLabel.value}`
  }
  if (llmHealth.value.connected) {
    return `${providerLabel.value} 已连接`
  }
  return '本地回退中'
})

const llmClass = computed(() => {
  if (llmLoading.value) return 'is-checking'
  if (!llmHealth.value?.api_key_loaded) return 'is-missing'
  if (llmHealth.value.connected) return 'is-connected'
  return 'is-fallback'
})

function pollEmbeddingStatus() {
  if (embeddingPollTimer !== null) {
    window.clearInterval(embeddingPollTimer)
  }
  embeddingPollTimer = window.setInterval(async () => {
    await appStore.loadLlmHealth()
    if (appStore.llmHealth?.embedding_status === 'ready' || appStore.llmHealth?.embedding_status === 'fallback') {
      if (embeddingPollTimer !== null) {
        window.clearInterval(embeddingPollTimer)
        embeddingPollTimer = null
      }
    }
  }, 3000)
}

async function startAutomaticEmbeddingWarmup() {
  const started = await appStore.ensureEmbeddingWarmup()
  if (started || appStore.llmHealth?.embedding_status === 'loading') {
    pollEmbeddingStatus()
  }
}
</script>

<template>
  <header class="topbar">
    <div class="topbar__title">
      <p class="topbar__eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
    </div>

    <div class="topbar__actions">
      <div class="topbar__status-row">
        <div class="topbar__llm" :class="llmClass" :title="llmHealth?.detail || ''">
          <span class="topbar__llm-dot" />
          <strong>{{ llmLabel }}</strong>
          <span v-if="llmHealth?.model" class="topbar__llm-model">{{ llmHealth.model }}</span>
        </div>
        <div
          class="topbar__llm"
          :class="embeddingClass"
          :title="llmHealth?.embedding_error || llmHealth?.embedding_model || ''"
        >
          <span class="topbar__llm-dot" />
          <strong>{{ embeddingLabel }}</strong>
          <span v-if="llmHealth?.embedding_provider" class="topbar__llm-model">{{ llmHealth.embedding_provider }}</span>
        </div>
      </div>
      <div class="topbar__meta-row">
        <div class="topbar__page-context">
          <span>{{ contextLabel }}</span>
          <strong>{{ contextValue }}</strong>
        </div>
        <div class="topbar__user">
          <span class="topbar__user-avatar">{{ (user.name || '本地用户').slice(0, 1) }}</span>
          <strong>{{ user.name || '本地用户' }}</strong>
          <span>{{ user.email || 'Obsidian reader' }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
.topbar {
  padding: 16px 24px;
  display: grid;
  grid-template-columns: minmax(420px, 1fr) minmax(0, 520px);
  align-items: center;
  gap: 18px;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(12px);
  background: rgba(245, 241, 232, 0.78);
  border-bottom: 1px solid rgba(231, 223, 209, 0.7);
}

.topbar__title {
  min-width: 420px;
}

.topbar h1 {
  margin: 4px 0 0;
  font-size: 1.8rem;
}

.topbar__eyebrow {
  margin: 0;
  font-size: 0.82rem;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.topbar__page-context {
  padding: 8px 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.07);
  white-space: nowrap;
}

.topbar__page-context span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
}

.topbar__page-context strong {
  color: var(--brand-primary);
  font-size: 0.9rem;
}

.topbar__actions {
  display: grid;
  gap: 8px;
  justify-content: flex-end;
  min-width: 0;
}

.topbar__status-row,
.topbar__meta-row {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  min-width: 0;
}

.topbar__meta-row {
  opacity: 0.96;
}

.topbar__llm {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.92);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
  max-width: 190px;
}

.topbar__llm-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: currentColor;
}

.topbar__llm-model {
  overflow: hidden;
  max-width: 72px;
  color: var(--text-tertiary);
  font-size: 0.78rem;
  text-overflow: ellipsis;
}

.topbar__llm.is-checking {
  color: var(--info);
}

.topbar__llm.is-missing {
  color: var(--warning);
}

.topbar__llm.is-connected {
  color: var(--success);
}

.topbar__llm.is-fallback {
  color: var(--danger);
}

.topbar__user {
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 190px;
  border: 1px solid var(--border-light);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.92);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
}

.topbar__user-avatar {
  width: 22px;
  height: 22px;
  display: inline-grid;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.1);
  color: var(--brand-primary);
  font-size: 0.82rem;
  font-weight: 900;
}

.topbar__user strong,
.topbar__user span:not(.topbar__user-avatar) {
  overflow: hidden;
  text-overflow: ellipsis;
}

.topbar__user span:not(.topbar__user-avatar) {
  max-width: 72px;
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

@media (max-width: 1240px) {
  .topbar__llm-model,
  .topbar__user span:not(.topbar__user-avatar) {
    display: none;
  }
}

@media (max-width: 900px) {
  .topbar {
    padding-inline: 16px;
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .topbar__title {
    min-width: 0;
    max-width: none;
  }

  .topbar__actions {
    justify-content: flex-start;
  }

  .topbar__status-row,
  .topbar__meta-row {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}
</style>
