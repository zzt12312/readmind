<script setup lang="ts">
import {
  CollectionTag,
  DataAnalysis,
  DocumentAdd,
  Histogram,
  Notebook,
  Reading,
  ChatLineRound,
  Expand,
  Fold,
  Share,
  List,
} from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { routes } from '@/constants/routes'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const { sidebarCollapsed } = storeToRefs(appStore)

const items = [
  { label: '首页', to: routes.dashboard, icon: DataAnalysis },
  { label: '看板', to: routes.analytics, icon: Histogram },
  { label: '导入', to: routes.import, icon: DocumentAdd },
  { label: '书库', to: routes.books, icon: Reading },
  { label: '笔记', to: routes.notes, icon: Notebook },
  { label: '图谱', to: routes.graph, icon: Share },
  { label: '任务', to: routes.jobs, icon: List },
  { label: '问答', to: routes.qa, icon: ChatLineRound },
  { label: '复习', to: routes.review, icon: CollectionTag },
]
</script>

<template>
  <aside class="sidebar" :class="{ 'is-collapsed': sidebarCollapsed }">
    <RouterLink class="sidebar__brand" :to="routes.dashboard" title="ReadMind">
      <div class="sidebar__brand-mark">RM</div>
      <div class="sidebar__brand-copy">
        <strong>ReadMind</strong>
        <span>Reading cockpit</span>
      </div>
    </RouterLink>

    <button
      class="sidebar__toggle"
      type="button"
      :aria-label="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
      :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
      @click="appStore.toggleSidebar"
    >
      <el-icon><component :is="sidebarCollapsed ? Expand : Fold" /></el-icon>
      <span>{{ sidebarCollapsed ? '展开目录' : '沉浸模式' }}</span>
    </button>

    <nav class="sidebar__nav">
      <RouterLink
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="sidebar__nav-item"
        active-class="is-active"
        :title="item.label"
      >
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </RouterLink>
    </nav>
  </aside>
</template>

<style scoped lang="scss">
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 28px;
  background: rgba(251, 248, 242, 0.88);
  border-right: 1px solid var(--border-light);
  backdrop-filter: blur(14px);
  transition:
    padding 0.2s ease,
    gap 0.2s ease;
}

.sidebar__brand {
  padding: 14px;
  display: flex;
  gap: 12px;
  align-items: center;
  color: inherit;
  text-decoration: none;
  border-radius: var(--radius-md);
  background: rgba(255, 253, 249, 0.86);
  box-shadow: var(--shadow-sm);
}

.sidebar__brand-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--brand-primary), #457867);
  color: #fff;
  font-weight: 700;
}

.sidebar__brand-copy {
  display: flex;
  flex-direction: column;
}

.sidebar__brand-copy strong {
  font-size: 1rem;
}

.sidebar__brand-copy span {
  color: var(--text-tertiary);
  font-size: 0.78rem;
}

.sidebar__toggle {
  width: 100%;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: var(--radius-sm);
  background: rgba(47, 93, 80, 0.07);
  color: var(--brand-primary);
  cursor: pointer;
  font: inherit;
  font-weight: 800;
  transition:
    background 0.18s ease,
    transform 0.18s ease;
}

.sidebar__toggle:hover {
  background: rgba(47, 93, 80, 0.12);
  transform: translateX(2px);
}

.sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar__nav-item {
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease-out;
}

.sidebar__nav-item:hover,
.sidebar__nav-item.is-active {
  color: var(--brand-primary);
  background: var(--brand-primary-light);
  transform: translateX(2px);
}

.sidebar.is-collapsed {
  padding-inline: 14px;
  gap: 20px;
}

.sidebar.is-collapsed .sidebar__brand,
.sidebar.is-collapsed .sidebar__toggle,
.sidebar.is-collapsed .sidebar__nav-item {
  justify-content: center;
}

.sidebar.is-collapsed .sidebar__brand {
  padding-inline: 10px;
}

.sidebar.is-collapsed .sidebar__brand-copy,
.sidebar.is-collapsed .sidebar__toggle span,
.sidebar.is-collapsed .sidebar__nav-item span {
  display: none;
}

.sidebar.is-collapsed .sidebar__nav-item {
  padding-inline: 12px;
}

@media (max-width: 1100px) {
  .sidebar__brand-copy,
  .sidebar__toggle span,
  .sidebar__nav-item span {
    display: none;
  }

  .sidebar__nav-item {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
}
</style>
