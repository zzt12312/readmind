<script setup lang="ts">
import { computed } from 'vue'
import qianqianDefault from '@/assets/mascot/qianqian-default.webp'
import qianqianHappy from '@/assets/mascot/qianqian-happy.webp'
import qianqianReminder from '@/assets/mascot/qianqian-reminder.webp'
import qianqianThinking from '@/assets/mascot/qianqian-thinking.webp'

const props = withDefaults(defineProps<{
  mood?: 'default' | 'happy' | 'thinking' | 'reminder'
  message: string
  compact?: boolean
  portrait?: boolean
  actionText?: string
  celebrating?: boolean
}>(), {
  mood: 'default',
  compact: false,
  portrait: false,
  actionText: '',
  celebrating: false,
})

const emit = defineEmits<{
  action: []
}>()

const mascotImage = computed(() => ({
  default: qianqianDefault,
  happy: qianqianHappy,
  thinking: qianqianThinking,
  reminder: qianqianReminder,
})[props.mood])
</script>

<template>
  <aside
    class="mascot-bubble"
    :class="[`is-${mood}`, { 'is-compact': compact, 'is-portrait': portrait, 'is-celebrating': celebrating }]"
  >
    <div class="mascot-bubble__avatar" aria-hidden="true">
      <img :src="mascotImage" alt="" />
    </div>
    <div class="mascot-bubble__content">
      <span>签签</span>
      <p>{{ message }}</p>
      <button v-if="actionText" type="button" @click="emit('action')">
        {{ actionText }}
      </button>
    </div>
  </aside>
</template>

<style scoped lang="scss">
.mascot-bubble {
  position: relative;
  overflow: hidden;
  padding: 12px;
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  border: 1px solid rgba(216, 207, 191, 0.68);
  border-radius: 22px;
  background:
    radial-gradient(circle at 0% 0%, rgba(47, 93, 80, 0.1), transparent 42%),
    rgba(255, 253, 249, 0.78);
  box-shadow: 0 16px 34px rgba(47, 93, 80, 0.1);
  animation: mascot-enter 0.36s ease-out both;
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
}

.mascot-bubble:hover,
.mascot-bubble:focus-within {
  border-color: rgba(47, 93, 80, 0.2);
  box-shadow: 0 20px 44px rgba(47, 93, 80, 0.14);
  transform: translateY(-2px);
}

.mascot-bubble::before,
.mascot-bubble::after {
  content: '';
  position: absolute;
  pointer-events: none;
}

.mascot-bubble::before {
  top: 12px;
  right: 14px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(197, 139, 92, 0.45);
  box-shadow:
    -18px 16px 0 rgba(47, 93, 80, 0.16),
    16px 26px 0 rgba(197, 139, 92, 0.2);
  animation: mascot-sparkle 3.8s ease-in-out infinite;
}

.mascot-bubble::after {
  inset: 0;
  opacity: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255, 255, 255, 0.42) 46%, transparent 72%);
  transform: translateX(-120%);
}

.mascot-bubble.is-happy {
  background:
    radial-gradient(circle at 0% 0%, rgba(197, 139, 92, 0.16), transparent 42%),
    rgba(255, 253, 249, 0.8);
}

.mascot-bubble.is-happy .mascot-bubble__avatar {
  animation:
    mascot-float 4.8s ease-in-out infinite,
    mascot-happy-pop 1.8s ease-out 0.25s 1;
}

.mascot-bubble.is-happy::before {
  background: rgba(197, 139, 92, 0.6);
  box-shadow:
    -20px 18px 0 rgba(47, 93, 80, 0.2),
    16px 28px 0 rgba(197, 139, 92, 0.28),
    -42px 4px 0 rgba(231, 197, 133, 0.34),
    38px 8px 0 rgba(47, 93, 80, 0.14);
  animation: mascot-confetti 2.8s ease-in-out infinite;
}

.mascot-bubble.is-happy::after {
  animation: mascot-shine 3.8s ease-in-out infinite;
}

.mascot-bubble.is-celebrating {
  border-color: rgba(197, 139, 92, 0.32);
}

.mascot-bubble.is-celebrating .mascot-bubble__content p::after {
  content: '';
  display: inline-block;
  width: 0.56em;
  height: 0.56em;
  margin-left: 0.42em;
  border-radius: 999px;
  background: rgba(197, 139, 92, 0.58);
  box-shadow:
    0.8em -0.18em 0 rgba(47, 93, 80, 0.24),
    1.45em 0.08em 0 rgba(231, 197, 133, 0.72);
  transform-origin: center;
  animation: mascot-inline-celebrate 1.7s ease-in-out infinite;
}

.mascot-bubble.is-thinking {
  background:
    radial-gradient(circle at 0% 0%, rgba(77, 116, 146, 0.12), transparent 42%),
    rgba(255, 253, 249, 0.8);
}

.mascot-bubble.is-thinking .mascot-bubble__content span::after {
  content: '...';
  display: inline-block;
  width: 1.4em;
  overflow: hidden;
  vertical-align: bottom;
  animation: mascot-thinking-dots 1.3s steps(4, end) infinite;
}

.mascot-bubble.is-thinking .mascot-bubble__avatar::after {
  opacity: 1;
  animation: mascot-orbit-dot 1.8s linear infinite;
}

.mascot-bubble.is-reminder {
  background:
    radial-gradient(circle at 0% 0%, rgba(47, 93, 80, 0.14), transparent 42%),
    rgba(255, 253, 249, 0.8);
  animation:
    mascot-enter 0.36s ease-out both,
    mascot-reminder-pulse 3.2s ease-in-out infinite;
}

.mascot-bubble.is-reminder .mascot-bubble__avatar::before {
  opacity: 1;
  animation: mascot-bookmark-wiggle 1.8s ease-in-out infinite;
}

.mascot-bubble__avatar {
  position: relative;
  isolation: isolate;
  width: 72px;
  height: 72px;
  overflow: hidden;
  border: 2px solid rgba(255, 253, 249, 0.9);
  border-radius: 24px;
  background: rgba(255, 253, 249, 0.92);
  box-shadow: 0 10px 24px rgba(47, 93, 80, 0.12);
  animation: mascot-float 4.8s ease-in-out infinite;
}

.mascot-bubble__avatar::before,
.mascot-bubble__avatar::after {
  content: '';
  position: absolute;
  pointer-events: none;
}

.mascot-bubble__avatar::before {
  z-index: 2;
  top: 8px;
  right: 9px;
  width: 10px;
  height: 18px;
  opacity: 0;
  border-radius: 4px 4px 2px 2px;
  background: linear-gradient(180deg, rgba(197, 139, 92, 0.92), rgba(231, 197, 133, 0.92));
  clip-path: polygon(0 0, 100% 0, 100% 100%, 50% 74%, 0 100%);
  box-shadow: 0 4px 10px rgba(197, 139, 92, 0.22);
}

.mascot-bubble__avatar::after {
  z-index: 3;
  top: 9px;
  left: 10px;
  width: 8px;
  height: 8px;
  opacity: 0;
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.72);
  box-shadow: 0 0 0 5px rgba(47, 93, 80, 0.08);
}

.mascot-bubble__avatar img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 18%;
  transition: transform 0.24s ease;
}

.mascot-bubble:hover .mascot-bubble__avatar img,
.mascot-bubble:focus-within .mascot-bubble__avatar img {
  transform: scale(1.035);
}

.mascot-bubble__content {
  min-width: 0;
}

.mascot-bubble__content span {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.mascot-bubble__content p {
  margin: 5px 0 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.mascot-bubble__content button {
  margin-top: 10px;
  padding: 8px 11px;
  border: 1px solid rgba(47, 93, 80, 0.16);
  border-radius: 999px;
  background: rgba(47, 93, 80, 0.08);
  color: var(--brand-primary);
  cursor: pointer;
  font-weight: 900;
  transition:
    background 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s ease;
}

.mascot-bubble__content button:hover {
  background: rgba(47, 93, 80, 0.12);
  box-shadow: 0 8px 18px rgba(47, 93, 80, 0.12);
  transform: translateY(-1px);
}

.mascot-bubble__content button:active {
  transform: translateY(0) scale(0.98);
}

.mascot-bubble.is-compact {
  grid-template-columns: 52px minmax(0, 1fr);
  border-radius: 18px;
}

.mascot-bubble.is-compact .mascot-bubble__avatar {
  width: 52px;
  height: 52px;
  border-radius: 18px;
}

.mascot-bubble.is-compact .mascot-bubble__content p {
  font-size: 0.88rem;
}

.mascot-bubble.is-portrait {
  grid-template-columns: minmax(116px, 0.45fr) minmax(0, 1fr);
  align-items: center;
  padding: 14px;
}

.mascot-bubble.is-portrait .mascot-bubble__avatar {
  width: 100%;
  min-width: 112px;
  height: 150px;
  border-radius: 22px;
}

.mascot-bubble.is-portrait .mascot-bubble__avatar img {
  object-fit: contain;
  object-position: 50% 50%;
}

@keyframes mascot-float {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-3px);
  }
}

@keyframes mascot-enter {
  from {
    opacity: 0;
    transform: translateY(6px) scale(0.98);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes mascot-happy-pop {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }

  35% {
    transform: translateY(-6px) rotate(-2deg);
  }

  65% {
    transform: translateY(-2px) rotate(2deg);
  }
}

@keyframes mascot-reminder-pulse {
  0%,
  100% {
    border-color: rgba(216, 207, 191, 0.68);
    box-shadow: 0 16px 34px rgba(47, 93, 80, 0.1);
  }

  50% {
    border-color: rgba(47, 93, 80, 0.22);
    box-shadow: 0 18px 38px rgba(47, 93, 80, 0.16);
  }
}

@keyframes mascot-shine {
  0%,
  55%,
  100% {
    opacity: 0;
    transform: translateX(-120%);
  }

  72% {
    opacity: 1;
    transform: translateX(120%);
  }
}

@keyframes mascot-sparkle {
  0%,
  100% {
    opacity: 0.55;
    transform: translateY(0) scale(1);
  }

  50% {
    opacity: 1;
    transform: translateY(-3px) scale(1.1);
  }
}

@keyframes mascot-thinking-dots {
  from {
    width: 0;
  }

  to {
    width: 1.4em;
  }
}

@keyframes mascot-confetti {
  0%,
  100% {
    opacity: 0.48;
    transform: translateY(0) rotate(0deg) scale(1);
  }

  45% {
    opacity: 1;
    transform: translateY(-5px) rotate(10deg) scale(1.08);
  }
}

@keyframes mascot-orbit-dot {
  0% {
    transform: translate(0, 0) scale(0.82);
  }

  25% {
    transform: translate(42px, 4px) scale(1);
  }

  50% {
    transform: translate(48px, 42px) scale(0.88);
  }

  75% {
    transform: translate(4px, 46px) scale(1);
  }

  100% {
    transform: translate(0, 0) scale(0.82);
  }
}

@keyframes mascot-bookmark-wiggle {
  0%,
  100% {
    transform: rotate(0deg) translateY(0);
  }

  35% {
    transform: rotate(-5deg) translateY(-1px);
  }

  70% {
    transform: rotate(4deg) translateY(1px);
  }
}

@keyframes mascot-inline-celebrate {
  0%,
  100% {
    opacity: 0.5;
    transform: translateY(0) scale(0.92);
  }

  50% {
    opacity: 1;
    transform: translateY(-3px) scale(1.08);
  }
}

@media (prefers-reduced-motion: reduce) {
  .mascot-bubble,
  .mascot-bubble::before,
  .mascot-bubble::after,
  .mascot-bubble__avatar,
  .mascot-bubble__avatar::before,
  .mascot-bubble__avatar::after,
  .mascot-bubble.is-celebrating .mascot-bubble__content p::after,
  .mascot-bubble__content span::after {
    animation: none;
  }

  .mascot-bubble,
  .mascot-bubble__avatar img,
  .mascot-bubble__content button {
    transition: none;
  }
}

@media (max-width: 640px) {
  .mascot-bubble {
    grid-template-columns: 56px minmax(0, 1fr);
  }

  .mascot-bubble__avatar {
    width: 56px;
    height: 56px;
    border-radius: 18px;
  }
}
</style>
