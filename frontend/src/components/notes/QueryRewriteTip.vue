<script setup lang="ts">
import type { QueryRewriteSummary } from '@/types/note'

defineProps<{
  queryRewrite: QueryRewriteSummary
}>()
</script>

<template>
  <section class="query-rewrite-tip">
    <strong>检索扩展</strong>
    <p>系统识别到你在问 <span>{{ queryRewrite.applied_rules.join('、') }}</span>，所以补充检索了这些相关概念：</p>
    <div class="query-rewrite-tip__tag-list">
      <el-tag
        v-for="term in queryRewrite.expansion_terms.slice(0, 6)"
        :key="term"
        round
        effect="plain"
        type="success"
      >
        {{ term }}
      </el-tag>
    </div>
  </section>
</template>

<style scoped lang="scss">
.query-rewrite-tip {
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  background: rgba(47, 93, 80, 0.06);
}

.query-rewrite-tip strong {
  display: block;
  margin-bottom: 6px;
}

.query-rewrite-tip p {
  margin: 0 0 10px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.query-rewrite-tip span {
  color: var(--text-primary);
  font-weight: 600;
}

.query-rewrite-tip__tag-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>

