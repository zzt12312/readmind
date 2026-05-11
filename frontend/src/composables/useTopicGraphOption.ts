import { computed, type Ref } from 'vue'
import type { TopicCluster, TopicGraphLink, TopicGraphNode } from '@/types/insights'

interface TopicGraphOptionSources {
  graphNodes: Ref<TopicGraphNode[]>
  graphLinks: Ref<TopicGraphLink[]>
  clusters: Ref<TopicCluster[]>
  selectedMode: Ref<'category' | 'topic'>
  selectedGraphNodeName: Ref<string>
}

const palette = ['#2f5d50', '#c58b5c', '#557f73', '#8c6f5a', '#4f7388', '#9a7650']

export function useTopicGraphOption(sources: TopicGraphOptionSources) {
  function clusterColor(clusterId: number) {
    return palette[((clusterId % palette.length) + palette.length) % palette.length]
  }

  // Category mode uses a wider circular layout because it represents broad reading domains.
  // Topic mode uses force layout so dense note-level relationships can settle naturally.
  const graphOption = computed(() => {
    const nodes = sources.graphNodes.value.map((node) => {
      const isSelectedNode = sources.selectedGraphNodeName.value === node.name
      return {
        id: node.id,
        name: node.name,
        value: node.value,
        symbolSize:
          sources.selectedMode.value === 'category'
            ? 44 + Math.min(node.book_count * 2.2, 24)
            : 22 + Math.min(node.note_count * 1.5, 28),
        category: node.cluster_id,
        itemStyle: {
          color: clusterColor(node.cluster_id),
          opacity: 0.96,
          borderWidth: isSelectedNode ? 5 : 2,
          borderColor: isSelectedNode ? '#fffdf9' : 'rgba(255, 253, 249, 0.92)',
          shadowBlur: isSelectedNode ? 28 : 14,
          shadowColor: isSelectedNode ? 'rgba(47, 93, 80, 0.28)' : 'rgba(47, 93, 80, 0.16)',
        },
        label: {
          show: true,
          color: '#24312d',
          fontSize: isSelectedNode ? 15 : sources.selectedMode.value === 'category' ? 14 : 13,
          fontWeight: isSelectedNode ? 800 : 700,
          backgroundColor: 'rgba(255, 253, 249, 0.78)',
          borderColor: 'rgba(216, 207, 191, 0.5)',
          borderWidth: 1,
          borderRadius: 10,
          padding: [4, 7],
        },
        emphasis: {
          scale: true,
          itemStyle: {
            borderColor: '#fffdf9',
            borderWidth: 5,
            shadowBlur: 30,
            shadowColor: 'rgba(47, 93, 80, 0.3)',
          },
          label: {
            color: '#1f3932',
            fontWeight: 900,
          },
        },
      }
    })

    const links = sources.graphLinks.value.map((link) => {
      const isSelectedLink =
        sources.selectedGraphNodeName.value &&
        (String(link.source) === sources.selectedGraphNodeName.value || String(link.target) === sources.selectedGraphNodeName.value)
      return {
        ...link,
        lineStyle: {
          color: isSelectedLink ? 'rgba(47, 93, 80, 0.48)' : 'rgba(47, 93, 80, 0.18)',
          width: Math.max(1, Math.min(link.value, sources.selectedMode.value === 'category' ? 8 : 5)),
          opacity: isSelectedLink ? 0.95 : 0.62,
          curveness: sources.selectedMode.value === 'category' ? 0.22 : 0.12,
        },
        emphasis: {
          lineStyle: {
            color: 'rgba(47, 93, 80, 0.58)',
            opacity: 1,
            width: Math.max(2, Math.min(link.value + 1, sources.selectedMode.value === 'category' ? 9 : 6)),
          },
        },
      }
    })

    return {
      backgroundColor: 'transparent',
      color: palette,
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(36, 49, 45, 0.94)',
        borderColor: 'rgba(255, 253, 249, 0.16)',
        borderWidth: 1,
        extraCssText: 'border-radius: 14px; box-shadow: 0 16px 34px rgba(36, 49, 45, 0.24);',
        padding: [10, 12],
        textStyle: {
          color: '#f6f1e7',
          fontSize: 13,
        },
        formatter: (params: { dataType?: string; data?: Record<string, unknown> }) => {
          if (params.dataType === 'edge') {
            return `<strong>${String(params.data?.source)} ↔ ${String(params.data?.target)}</strong><br/>关联强度：${String(params.data?.value)}`
          }
          return `<strong>${String(params.data?.name)}</strong><br/>关联笔记：${String(params.data?.value)}`
        },
      },
      series: [
        {
          type: 'graph',
          layout: sources.selectedMode.value === 'category' ? 'circular' : 'force',
          roam: false,
          draggable: true,
          focusNodeAdjacency: true,
          edgeSymbol: ['none', 'circle'],
          edgeSymbolSize: [0, 5],
          force: {
            repulsion: sources.selectedMode.value === 'category' ? 520 : 340,
            edgeLength: sources.selectedMode.value === 'category' ? [170, 280] : [110, 200],
            gravity: sources.selectedMode.value === 'category' ? 0.02 : 0.04,
            friction: 0.18,
          },
          circular: {
            rotateLabel: false,
          },
          left: 36,
          right: 36,
          top: 44,
          bottom: 40,
          data: nodes,
          links,
          categories: sources.clusters.value.map((cluster) => ({
            name: cluster.name,
            itemStyle: { color: clusterColor(cluster.id) },
          })),
          lineStyle: {
            cap: 'round',
          },
          emphasis: {
            focus: 'adjacency',
            blurScope: 'coordinateSystem',
          },
          blur: {
            itemStyle: {
              opacity: 0.28,
            },
            lineStyle: {
              opacity: 0.12,
            },
            label: {
              opacity: 0.35,
            },
          },
          animationDuration: 900,
          animationDurationUpdate: 700,
          animationEasingUpdate: 'cubicOut',
        },
      ],
    }
  })

  return {
    clusterColor,
    graphOption,
  }
}
