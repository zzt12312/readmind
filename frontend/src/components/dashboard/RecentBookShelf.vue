<script setup lang="ts">
import { onMounted } from 'vue'
import AppCard from '@/components/base/AppCard.vue'
import BookCover from '@/components/common/BookCover.vue'
import { useBookShelfDrag } from '@/composables/useBookShelfDrag'
import type { DashboardRecentBook } from '@/types/dashboard'
import type { ComponentPublicInstance } from 'vue'

defineProps<{
  books: DashboardRecentBook[]
}>()

const emit = defineEmits<{
  navigate: [path: string]
  prewarm: [bookId: number]
}>()

const {
  shelfRef,
  shelfClass,
  updateShelfMask,
  startShelfDrag,
  moveShelfDrag,
  endShelfDrag,
} = useBookShelfDrag()

function setShelfElement(element: Element | ComponentPublicInstance | null) {
  shelfRef.value = element instanceof HTMLElement ? element : null
}

onMounted(() => {
  requestAnimationFrame(updateShelfMask)
})
</script>

<template>
  <AppCard>
    <h3>最近整理的书</h3>
    <div class="recent-book-shelf" :class="shelfClass">
      <div
        :ref="setShelfElement"
        class="recent-book-shelf__list"
        @scroll="updateShelfMask"
        @mousedown="startShelfDrag"
        @mousemove="moveShelfDrag"
        @mouseleave="endShelfDrag"
        @mouseup="endShelfDrag"
      >
        <article
          v-for="(book, index) in books"
          :key="book.id"
          class="recent-book-shelf__item"
          @click="emit('navigate', `/books/${book.id}`)"
          @mouseenter="emit('prewarm', book.id)"
        >
          <div class="recent-book-shelf__cover">
            <BookCover
              :src="book.cover"
              :title="book.title"
              :eager="index < 3"
            />
          </div>
          <strong class="recent-book-shelf__title">{{ book.title }}</strong>
          <p>{{ book.notes }} 条笔记</p>
          <span class="recent-book-shelf__updated">{{ book.updated }}</span>
        </article>
      </div>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.recent-book-shelf {
  position: relative;
}

.recent-book-shelf::before,
.recent-book-shelf::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 4px;
  width: 28px;
  z-index: 1;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.recent-book-shelf::before {
  left: 0;
  background: linear-gradient(90deg, rgba(255, 253, 249, 0.95), rgba(255, 253, 249, 0));
}

.recent-book-shelf::after {
  right: 0;
  background: linear-gradient(270deg, rgba(255, 253, 249, 0.95), rgba(255, 253, 249, 0));
}

.recent-book-shelf.is-at-start::before,
.recent-book-shelf.is-at-end::after {
  opacity: 0;
}

.recent-book-shelf__list {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 4px;
  scroll-snap-type: x proximity;
}

.recent-book-shelf__list::-webkit-scrollbar {
  height: 8px;
}

.recent-book-shelf__list::-webkit-scrollbar-thumb {
  background: rgba(47, 93, 80, 0.18);
  border-radius: 999px;
}

.recent-book-shelf__item {
  display: flex;
  flex: 0 0 132px;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start;
  cursor: pointer;
  scroll-snap-align: start;
  user-select: none;
}

.recent-book-shelf__cover {
  width: 132px;
  height: 176px;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 12px 24px rgba(41, 74, 64, 0.18);
}

.recent-book-shelf__title {
  line-height: 1.5;
}

.recent-book-shelf__item p,
.recent-book-shelf__updated {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 0.86rem;
}

.recent-book-shelf.is-dragging .recent-book-shelf__list {
  cursor: grabbing;
}
</style>
