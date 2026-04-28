<template>
  <div class="login-view">
    <section class="login-view__hero">
      <p class="login-view__eyebrow">ReadMind</p>
      <h1>把碎片书摘，整理成长期可复用的知识资产。</h1>
      <p class="login-view__description">
        导入你的 Obsidian 阅读笔记，自动分类、生成摘要、围绕单本书问答，并建立复习节奏。
      </p>
      <div class="login-view__highlights">
        <span>Markdown 导入</span>
        <span>AI 整理</span>
        <span>可溯源问答</span>
      </div>
    </section>

    <AppCard class="login-view__card">
      <h2>欢迎回来</h2>
      <p>继续整理你的阅读知识库</p>
      <el-form label-position="top">
        <el-form-item label="邮箱">
          <el-input placeholder="tao@example.com" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <RouterLink to="/dashboard">
          <el-button type="primary" class="login-view__submit" round>进入工作台</el-button>
        </RouterLink>
      </el-form>
    </AppCard>
  </div>
</template>

<script lang="ts">
import AppCard from '@/components/base/AppCard.vue'

export default {
  components: {
    AppCard,
  },
}
</script>

<style scoped lang="scss">
.login-view {
  width: min(1120px, 100%);
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(360px, 420px);
  gap: 32px;
  align-items: center;
}

.login-view__hero {
  padding: 32px;
}

.login-view__eyebrow {
  margin: 0 0 12px;
  color: var(--brand-primary);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.login-view h1 {
  margin: 0 0 18px;
  font-size: clamp(2.6rem, 5vw, 4.4rem);
  line-height: 1.08;
}

.login-view__description {
  max-width: 44rem;
  color: var(--text-secondary);
  font-size: 1.06rem;
  line-height: 1.8;
}

.login-view__highlights {
  margin-top: 24px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.login-view__highlights span {
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.82);
  color: var(--brand-primary);
  box-shadow: var(--shadow-sm);
}

.login-view__card h2 {
  margin: 0 0 6px;
}

.login-view__card p {
  margin: 0 0 20px;
  color: var(--text-secondary);
}

.login-view__submit {
  width: 100%;
}

@media (max-width: 960px) {
  .login-view {
    grid-template-columns: 1fr;
  }

  .login-view__hero,
  .login-view__card {
    padding: 24px;
  }
}
</style>
