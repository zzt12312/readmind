<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import SidebarNav from '@/components/common/SidebarNav.vue'
import TopNavBar from '@/components/common/TopNavBar.vue'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const appStore = useAppStore()
const { sidebarCollapsed } = storeToRefs(appStore)

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    dashboard: '阅读中台',
    analytics: '数据看板',
    import: '导入中心',
    books: '我的书库',
    notes: '笔记工作台',
    graph: '知识图谱',
    jobs: '任务中心',
    qa: '智能问答',
    review: '复习中心',
  }

  return map[String(route.name)] ?? 'ReadMind'
})
const pageMeta = computed(() => {
  const map: Record<string, { eyebrow: string; contextLabel: string; contextValue: string }> = {
    dashboard: {
      eyebrow: 'Reading Command Center',
      contextLabel: '今日重点',
      contextValue: '复习与整理',
    },
    analytics: {
      eyebrow: 'Reading Analytics',
      contextLabel: '分析对象',
      contextValue: '偏好与进展',
    },
    import: {
      eyebrow: 'Import Pipeline',
      contextLabel: '数据入口',
      contextValue: '本地同步优先',
    },
    books: {
      eyebrow: 'Library Explorer',
      contextLabel: '浏览方式',
      contextValue: '书籍档案',
    },
    'book-detail': {
      eyebrow: 'Reading Archive',
      contextLabel: '当前档案',
      contextValue: '摘要与高亮',
    },
    notes: {
      eyebrow: 'Note Search and Review Workspace',
      contextLabel: '当前页',
      contextValue: '专注筛选与整理',
    },
    graph: {
      eyebrow: 'Knowledge Map Workspace',
      contextLabel: '探索方式',
      contextValue: '跨书主题关系',
    },
    jobs: {
      eyebrow: 'Background Task Monitor',
      contextLabel: '任务视图',
      contextValue: '状态与重试',
    },
    qa: {
      eyebrow: 'Ask Your Reading Memory',
      contextLabel: '回答依据',
      contextValue: '检索引用笔记',
    },
    review: {
      eyebrow: 'Spaced Review Studio',
      contextLabel: '复习节奏',
      contextValue: '今日计划',
    },
  }

  return map[String(route.name)] ?? {
    eyebrow: 'Personal knowledge workspace',
    contextLabel: '当前页',
    contextValue: '阅读工作台',
  }
})
</script>

<template>
  <div class="main-layout" :class="{ 'is-sidebar-collapsed': sidebarCollapsed }">
    <SidebarNav />
    <div class="main-layout__content">
      <TopNavBar
        :title="pageTitle"
        :eyebrow="pageMeta.eyebrow"
        :context-label="pageMeta.contextLabel"
        :context-value="pageMeta.contextValue"
      />
      <main class="main-layout__page">
        <RouterView />
      </main>
      <footer class="main-layout__footer">
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer">粤ICP备2026056029号-1</a>
      </footer>
    </div>
  </div>
</template>

<style scoped lang="scss">
.main-layout {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 232px minmax(0, 1fr);
  background:
    radial-gradient(circle at top left, rgba(192, 139, 92, 0.12), transparent 24%),
    var(--bg-page);
  transition: grid-template-columns 0.22s ease;
}

.main-layout.is-sidebar-collapsed {
  grid-template-columns: 76px minmax(0, 1fr);
}

.main-layout__content {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.main-layout__page {
  flex: 1;
  padding: 24px 24px 32px;
}

.main-layout__footer {
  padding: 0 24px 18px;
  text-align: center;
}

.main-layout__footer a {
  color: var(--text-tertiary);
  font-size: 0.82rem;
  text-decoration: none;
}

.main-layout__footer a:hover {
  color: var(--brand-primary);
}

@media (max-width: 1100px) {
  .main-layout {
    grid-template-columns: 88px minmax(0, 1fr);
  }

  .main-layout.is-sidebar-collapsed {
    grid-template-columns: 76px minmax(0, 1fr);
  }
}

@media (max-width: 768px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .main-layout__page {
    padding: 16px;
  }

  .main-layout__footer {
    padding: 0 16px 16px;
  }
}
</style>
