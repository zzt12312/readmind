<template>
  <main class="auth-layout">
    <RouterView />
  </main>
</template>

<style scoped lang="scss">
.auth-layout {
  min-height: 100vh;
  padding: 24px;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top right, rgba(47, 93, 80, 0.15), transparent 30%),
    radial-gradient(circle at bottom left, rgba(192, 139, 92, 0.12), transparent 24%),
    var(--bg-page);
}
</style>
