<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { routes } from '@/constants/routes'

defineProps<{
  title: string
}>()

const router = useRouter()
const appStore = useAppStore()
const { llmHealth, llmLoading, embeddingWarming } = storeToRefs(appStore)
const globalKeyword = ref('')
let embeddingPollTimer: number | null = null

const providerLabel = computed(() => {
  return llmHealth.value?.demo_mode ? '演示站' : 'DeepSeek'
})

const embeddingLabel = computed(() => {
  if (!llmHealth.value) return 'Embedding 未知'
  if (llmHealth.value.demo_mode && llmHealth.value.embedding_status !== 'ready') return '演示检索已就绪'
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

const showEmbeddingWarmup = computed(() => {
  if (!llmHealth.value) return false
  if (llmHealth.value.demo_mode) return false
  return llmHealth.value.embedding_status !== 'ready'
})

onMounted(() => {
  if (!llmLoading.value) {
    void appStore.loadLlmHealth()
  }
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
    return '演示站已就绪'
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

function submitGlobalSearch() {
  const query = globalKeyword.value.trim()
  if (!query) {
    void router.push(routes.notes)
    return
  }

  void router.push({
    path: routes.notes,
    query: {
      q: query,
    },
  })
}

function goToImport() {
  void router.push(routes.import)
}

async function startEmbeddingWarmup() {
  await appStore.startEmbeddingWarmup()
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
  ElMessage.success('已触发 embedding 预热，状态会自动刷新。')
}
</script>

<template>
  <header class="topbar">
    <div>
      <p class="topbar__eyebrow">Personal knowledge workspace</p>
      <h1>{{ title }}</h1>
    </div>

    <div class="topbar__actions">
      <el-input v-model="globalKeyword" class="topbar__search" placeholder="搜索书籍、标签、观点" @keyup.enter="submitGlobalSearch">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button @click="submitGlobalSearch">搜索</el-button>
        </template>
      </el-input>
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
      <el-button
        v-if="showEmbeddingWarmup"
        round
        :loading="embeddingWarming"
        @click="startEmbeddingWarmup"
      >
        预热 Embedding
      </el-button>
      <el-button type="primary" round @click="goToImport">导入笔记</el-button>
      <div class="topbar__user">
        <strong>Tao</strong>
        <span>Obsidian reader</span>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
.topbar {
  padding: 22px 24px 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(12px);
  background: rgba(245, 241, 232, 0.78);
  border-bottom: 1px solid rgba(231, 223, 209, 0.7);
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

.topbar__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.topbar__search {
  width: 280px;
}

.topbar__llm {
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.92);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
}

.topbar__llm-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: currentColor;
}

.topbar__llm-model {
  color: var(--text-tertiary);
  font-size: 0.78rem;
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
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-sm);
  background: rgba(255, 253, 249, 0.88);
  box-shadow: var(--shadow-sm);
}

.topbar__user span {
  color: var(--text-tertiary);
  font-size: 0.8rem;
}

@media (max-width: 900px) {
  .topbar {
    padding-inline: 16px;
    flex-direction: column;
    align-items: stretch;
  }

  .topbar__actions {
    flex-wrap: wrap;
  }

  .topbar__search {
    width: 100%;
  }
}
</style>
