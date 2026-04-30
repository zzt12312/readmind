<script setup lang="ts">
defineProps<{
  actions: Array<{
    id: string
    index: string
    title: string
    type: string
    saved?: boolean
    disabled?: boolean
  }>
}>()

defineEmits<{
  action: [id: string]
}>()
</script>

<template>
  <div class="app-action-grid">
    <button
      v-for="action in actions"
      :key="action.id"
      type="button"
      class="app-action-grid__item"
      :class="{ 'is-saved': action.saved }"
      :disabled="action.disabled"
      @click="$emit('action', action.id)"
    >
      <span>{{ action.index }}</span>
      <strong>{{ action.title }}</strong>
      <em>{{ action.type }}</em>
    </button>
  </div>
</template>

<style scoped lang="scss">
.app-action-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
}

.app-action-grid__item {
  position: relative;
  overflow: hidden;
  width: 100%;
  min-width: 0;
  min-height: 58px;
  padding: 11px 12px;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  grid-template-areas:
    'index title'
    'index type';
  column-gap: 10px;
  align-items: center;
  border: 1px solid rgba(216, 207, 191, 0.7);
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(248, 244, 237, 0.72)),
    var(--bg-card);
  color: var(--text-primary);
  cursor: pointer;
  font: inherit;
  text-align: left;
  transition:
    border-color 0.16s ease,
    background 0.16s ease,
    box-shadow 0.16s ease,
    transform 0.16s ease;
}

.app-action-grid__item span {
  grid-area: index;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  font-size: 0.72rem;
  font-weight: 900;
}

.app-action-grid__item strong {
  grid-area: title;
  overflow: hidden;
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 900;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-action-grid__item em {
  grid-area: type;
  color: var(--text-tertiary);
  font-size: 0.74rem;
  font-style: normal;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.app-action-grid__item:hover:not(:disabled) {
  border-color: rgba(47, 93, 80, 0.24);
  background:
    linear-gradient(135deg, rgba(255, 253, 249, 1), rgba(240, 246, 239, 0.76)),
    var(--bg-card);
  box-shadow: 0 12px 24px rgba(47, 93, 80, 0.08);
  transform: translateY(-1px);
}

.app-action-grid__item.is-saved {
  border-color: rgba(47, 93, 80, 0.24);
  background:
    linear-gradient(135deg, rgba(47, 93, 80, 0.12), rgba(255, 253, 249, 0.82)),
    var(--bg-card);
}

.app-action-grid__item.is-saved span {
  background: var(--brand-primary);
  color: #fff;
}

.app-action-grid__item.is-saved strong {
  color: var(--brand-primary);
}

.app-action-grid__item:disabled {
  cursor: not-allowed;
  opacity: 0.48;
}

@media (max-width: 768px) {
  .app-action-grid {
    grid-template-columns: 1fr;
  }
}
</style>
