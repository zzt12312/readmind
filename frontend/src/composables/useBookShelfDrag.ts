import { computed, ref } from 'vue'

// Keeps horizontal shelf dragging out of page components.
// The caller owns the DOM ref; this composable only tracks drag state and edge masks.
export function useBookShelfDrag() {
  const shelfRef = ref<HTMLElement | null>(null)
  const isDraggingShelf = ref(false)
  const shelfAtStart = ref(true)
  const shelfAtEnd = ref(false)
  const dragState = {
    startX: 0,
    startScrollLeft: 0,
  }

  const shelfClass = computed(() => ({
    'is-dragging': isDraggingShelf.value,
    'is-at-start': shelfAtStart.value,
    'is-at-end': shelfAtEnd.value,
  }))

  function updateShelfMask() {
    const element = shelfRef.value
    if (!element) return
    shelfAtStart.value = element.scrollLeft <= 4
    shelfAtEnd.value = element.scrollLeft + element.clientWidth >= element.scrollWidth - 4
  }

  function startShelfDrag(event: MouseEvent) {
    const element = shelfRef.value
    if (!element) return
    isDraggingShelf.value = true
    dragState.startX = event.clientX
    dragState.startScrollLeft = element.scrollLeft
  }

  function moveShelfDrag(event: MouseEvent) {
    const element = shelfRef.value
    if (!element || !isDraggingShelf.value) return
    const delta = event.clientX - dragState.startX
    element.scrollLeft = dragState.startScrollLeft - delta
    updateShelfMask()
  }

  function endShelfDrag() {
    isDraggingShelf.value = false
  }

  return {
    shelfRef,
    shelfClass,
    updateShelfMask,
    startShelfDrag,
    moveShelfDrag,
    endShelfDrag,
  }
}
