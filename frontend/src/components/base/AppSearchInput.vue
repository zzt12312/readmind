<script setup lang="ts">
const model = defineModel<string>({ default: '' })
defineEmits<{
  submit: []
}>()
</script>

<template>
  <el-input v-model="model" class="app-search-input" placeholder="搜索" @keyup.enter="$emit('submit')">
    <template #prefix>
      <el-icon><Search /></el-icon>
    </template>
  </el-input>
</template>

<script lang="ts">
import { Search } from '@element-plus/icons-vue'

export default {
  components: {
    Search,
  },
}
</script>
