<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import SidebarNav from '@/components/common/SidebarNav.vue'
import TopNavBar from '@/components/common/TopNavBar.vue'

const route = useRoute()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    dashboard: '阅读中台',
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
</script>

<template>
  <div class="main-layout">
    <SidebarNav />
    <div class="main-layout__content">
      <TopNavBar :title="pageTitle" />
      <main class="main-layout__page">
        <RouterView />
      </main>
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

@media (max-width: 1100px) {
  .main-layout {
    grid-template-columns: 88px minmax(0, 1fr);
  }
}

@media (max-width: 768px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .main-layout__page {
    padding: 16px;
  }
}
</style>
