<script setup lang="ts">
const props = defineProps<{
  status: 'processing' | 'success' | 'failed' | 'scheduled'
}>()

const statusMap = {
  processing: '处理中',
  success: '已完成',
  failed: '失败',
  scheduled: '待复习',
}
</script>

<template>
  <span class="status-badge" :class="`is-${props.status}`">
    {{ statusMap[props.status] }}
  </span>
</template>

<style scoped lang="scss">
.status-badge {
  padding: 6px 10px;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 600;
}

.is-processing {
  background: rgba(86, 113, 137, 0.12);
  color: var(--info);
}

.is-success {
  background: rgba(76, 122, 98, 0.14);
  color: var(--success);
}

.is-failed {
  background: rgba(184, 92, 79, 0.14);
  color: var(--danger);
}

.is-scheduled {
  background: rgba(192, 139, 92, 0.16);
  color: var(--warning);
}
</style>
