<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    src?: string
    title: string
    alt?: string
    eager?: boolean
  }>(),
  {
    src: '',
    alt: '',
    eager: false,
  },
)

const rootRef = ref<HTMLElement | null>(null)
const shouldLoad = ref(false)
const loaded = ref(false)
const failed = ref(false)
let observer: IntersectionObserver | null = null

const fallbackText = computed(() => props.title.slice(0, 2))
const canRenderImage = computed(() => Boolean(props.src) && !failed.value && shouldLoad.value)

function beginLoading() {
  shouldLoad.value = true
}

function handleLoad() {
  loaded.value = true
}

function handleError() {
  failed.value = true
  loaded.value = false
}

function resetState() {
  loaded.value = false
  failed.value = false
  shouldLoad.value = props.eager || !props.src
}

watch(
  () => [props.src, props.eager, props.title],
  () => {
    resetState()
    if (props.eager) {
      beginLoading()
    }
  },
)

onMounted(() => {
  resetState()

  if (props.eager || !props.src) {
    beginLoading()
    return
  }

  // 只有当封面真正进入视口附近时才挂载图片请求，能减少书库和书架首次渲染时的无效下载。
  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (!entry?.isIntersecting) return
      beginLoading()
      observer?.disconnect()
      observer = null
    },
    { rootMargin: '180px' },
  )

  if (rootRef.value) {
    observer.observe(rootRef.value)
  }
})

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
})
</script>

<template>
  <div ref="rootRef" class="book-cover" :class="{ 'is-loaded': loaded, 'is-fallback': !canRenderImage }">
    <div v-if="canRenderImage && !loaded" class="book-cover__skeleton" />
    <img
      v-if="canRenderImage"
      class="book-cover__image"
      :class="{ 'is-visible': loaded }"
      :src="src"
      :alt="alt || title"
      :loading="eager ? 'eager' : 'lazy'"
      :fetchpriority="eager ? 'high' : 'auto'"
      decoding="async"
      @load="handleLoad"
      @error="handleError"
    />
    <span v-if="!canRenderImage" class="book-cover__fallback">{{ fallbackText }}</span>
  </div>
</template>

<style scoped lang="scss">
.book-cover {
  position: relative;
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: inherit;
  background: linear-gradient(160deg, #c08b5c, #4d7a6c);
}

.book-cover__skeleton {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(110deg, rgba(255, 255, 255, 0.06) 8%, rgba(255, 255, 255, 0.28) 18%, rgba(255, 255, 255, 0.08) 33%),
    linear-gradient(160deg, rgba(32, 52, 46, 0.24), rgba(92, 69, 48, 0.18));
  background-size: 200% 100%;
  animation: book-cover-shimmer 1.5s linear infinite;
}

.book-cover__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  opacity: 0;
  transform: scale(1.02);
  transition: opacity 0.24s ease, transform 0.32s ease;
}

.book-cover__image.is-visible {
  opacity: 1;
  transform: scale(1);
}

.book-cover__fallback {
  color: #fff;
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

@keyframes book-cover-shimmer {
  to {
    background-position-x: -200%;
  }
}
</style>
