<template>
  <section class="app-card">
    <slot />
  </section>
</template>

<style scoped lang="scss">
.app-card {
  padding: 20px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: rgba(255, 253, 249, 0.94);
  box-shadow: var(--shadow-sm);
}
</style>
