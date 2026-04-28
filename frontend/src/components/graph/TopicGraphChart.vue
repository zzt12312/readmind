<script setup lang="ts">
import { use } from 'echarts/core'
import { GraphChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

use([CanvasRenderer, GraphChart, TooltipComponent])

defineProps<{
  option: Record<string, unknown>
}>()

defineEmits<{
  click: [params: unknown]
}>()
</script>

<template>
  <VChart class="topic-graph-chart" :option="option" autoresize @click="$emit('click', $event)" />
</template>

<style scoped lang="scss">
.topic-graph-chart {
  width: 100%;
  height: 600px;
}
</style>
