<script setup lang="ts">
import AppCard from '@/components/base/AppCard.vue'

export interface FirstRunStep {
  key: string
  label: string
  title: string
  hint: string
  path: string
  done: boolean
}

defineProps<{
  steps: FirstRunStep[]
}>()

defineEmits<{
  dismiss: []
  navigate: [path: string]
}>()
</script>

<template>
  <AppCard class="first-run-guide">
    <div class="first-run-guide__head">
      <div>
        <p class="first-run-guide__eyebrow">First run guide</p>
        <h3>第一次使用，按这条路线走</h3>
        <span>从导入到追问，再到复习沉淀，尽量让用户不用自己猜下一步。</span>
      </div>
      <el-button text @click="$emit('dismiss')">收起</el-button>
    </div>
    <div class="first-run-guide__steps">
      <button
        v-for="step in steps"
        :key="step.key"
        type="button"
        :class="{ 'is-done': step.done }"
        @click="$emit('navigate', step.path)"
      >
        <em>{{ step.label }}</em>
        <strong>{{ step.title }}</strong>
        <span>{{ step.hint }}</span>
      </button>
    </div>
  </AppCard>
</template>

<style scoped lang="scss">
.first-run-guide {
  padding: 22px;
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  gap: 18px;
  align-items: stretch;
  background:
    radial-gradient(circle at 88% 8%, rgba(47, 93, 80, 0.12), transparent 30%),
    linear-gradient(135deg, rgba(255, 253, 249, 0.98), rgba(236, 241, 234, 0.64));
}

.first-run-guide__head {
  display: flex;
  min-width: 0;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}

.first-run-guide__eyebrow {
  margin: 0 0 8px;
  color: var(--brand-primary);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.first-run-guide__head h3 {
  margin: 0 0 10px;
  font-size: 1.45rem;
}

.first-run-guide__head span {
  color: var(--text-secondary);
  line-height: 1.7;
}

.first-run-guide__steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.first-run-guide__steps button {
  min-width: 0;
  padding: 15px;
  border: 1px solid rgba(47, 93, 80, 0.12);
  border-radius: 22px;
  background: rgba(255, 253, 249, 0.74);
  color: inherit;
  cursor: pointer;
  text-align: left;
  transition:
    border-color 0.16s ease,
    box-shadow 0.16s ease,
    transform 0.16s ease;
}

.first-run-guide__steps button:hover {
  border-color: rgba(47, 93, 80, 0.26);
  box-shadow: 0 14px 26px rgba(47, 93, 80, 0.08);
  transform: translateY(-2px);
}

.first-run-guide__steps em,
.first-run-guide__steps strong,
.first-run-guide__steps span {
  display: block;
}

.first-run-guide__steps em {
  color: var(--brand-primary);
  font-size: 0.72rem;
  font-style: normal;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.first-run-guide__steps button.is-done em {
  color: #2f7d57;
}

.first-run-guide__steps strong {
  margin-top: 8px;
  font-size: 1rem;
}

.first-run-guide__steps span {
  margin-top: 7px;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
}

@media (max-width: 1100px) {
  .first-run-guide {
    grid-template-columns: 1fr;
  }

  .first-run-guide__steps {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .first-run-guide__steps {
    grid-template-columns: 1fr;
  }
}
</style>
