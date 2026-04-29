<script setup lang="ts">
import qianqianImage from '@/assets/mascot/qianqian-default.webp'
import { highlightText } from '@/utils/text'
import type { QaMessage } from '@/types/qa'

const props = defineProps<{
  messages: QaMessage[]
  loading: boolean
  statusDetail: string
  highlightQuery: string
}>()

defineEmits<{
  jumpToNote: [bookId: number, noteId: number]
}>()

interface RenderBlock {
  type: 'paragraph' | 'list'
  lines: string[]
}

function renderReferenceHighlight(text: string) {
  return highlightText(text, props.highlightQuery)
}

function renderMessageBlocks(content: string): RenderBlock[] {
  const normalized = content.trim()
  if (!normalized) return []

  const blocks: RenderBlock[] = []
  let paragraphLines: string[] = []
  let listLines: string[] = []

  const flushParagraph = () => {
    if (!paragraphLines.length) return
    blocks.push({ type: 'paragraph', lines: [paragraphLines.join('\n')] })
    paragraphLines = []
  }
  const flushList = () => {
    if (!listLines.length) return
    blocks.push({ type: 'list', lines: [...listLines] })
    listLines = []
  }

  normalized.split(/\n+/).forEach((rawLine) => {
    const line = rawLine.trim()
    if (!line) {
      flushParagraph()
      flushList()
      return
    }

    const listMatch = line.match(/^(\d+[.)、]|[-*•])\s*(.+)$/)
    if (listMatch) {
      flushParagraph()
      listLines.push(listMatch[2])
      return
    }

    flushList()
    paragraphLines.push(line)
  })

  flushParagraph()
  flushList()
  return blocks
}
</script>

<template>
  <div class="qa-conversation">
    <template v-if="messages.length">
      <article
        v-for="(message, index) in messages"
        :key="`${message.role}-${index}`"
        class="qa-conversation__bubble"
        :class="[
          message.role === 'user' ? 'is-user' : 'is-assistant',
          message.role === 'assistant' && !message.content && loading ? 'is-thinking' : '',
        ]"
      >
        <div v-if="message.role === 'assistant'" class="qa-conversation__mascot-avatar" aria-hidden="true">
          <img :src="qianqianImage" alt="" />
        </div>
        <div class="qa-conversation__bubble-content">
          <span v-if="message.role === 'assistant'" class="qa-conversation__speaker">签签</span>
          <div class="qa-conversation__message-body">
            <template
              v-for="(block, blockIndex) in renderMessageBlocks(message.content || statusDetail || '签签正在结合你的读书笔记整理答案...')"
              :key="`${message.role}-${index}-${blockIndex}`"
            >
              <p v-if="block.type === 'paragraph'">{{ block.lines[0] }}</p>
              <ul v-else>
                <li v-for="line in block.lines" :key="line">{{ line }}</li>
              </ul>
            </template>
          </div>
        </div>
        <div v-if="message.role === 'assistant' && message.references?.length" class="qa-conversation__references">
          <article
            v-for="reference in message.references"
            :key="reference.book + reference.chapter + reference.note_id"
            class="qa-conversation__inline-reference"
          >
            <strong>{{ reference.book }} · {{ reference.chapter }}</strong>
            <p v-html="renderReferenceHighlight(reference.excerpt)" />
            <el-button text @click="$emit('jumpToNote', reference.book_id, reference.note_id)">跳转原笔记</el-button>
          </article>
        </div>
      </article>
    </template>
    <article v-else class="qa-conversation__bubble is-assistant" v-loading="loading">
      <div class="qa-conversation__mascot-avatar" aria-hidden="true">
        <img :src="qianqianImage" alt="" />
      </div>
      <div class="qa-conversation__bubble-content">
        <span class="qa-conversation__speaker">签签</span>
        <p>把问题交给我吧，我会先去你的读书笔记里找证据，再带着引用回来回答。</p>
      </div>
    </article>
  </div>
</template>

<style scoped lang="scss">
.qa-conversation {
  display: flex;
  flex-direction: column;
  gap: 14px;
  flex: 1;
  min-height: 280px;
  padding: 16px 10px 16px 0;
  overflow-y: auto;
  scroll-behavior: smooth;
  border-radius: 22px;
  background:
    radial-gradient(circle at 10% 0%, rgba(192, 139, 92, 0.08), transparent 22%),
    rgba(251, 248, 242, 0.42);
}

.qa-conversation__bubble {
  max-width: 90%;
  padding: 17px 19px;
  position: relative;
  border-radius: 22px;
  line-height: 1.75;
  box-shadow: 0 8px 20px rgba(57, 45, 31, 0.05);
}

.qa-conversation__bubble-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.qa-conversation__bubble.is-user {
  margin-left: auto;
  max-width: min(78%, 760px);
  border: 1px solid rgba(47, 93, 80, 0.18);
  border-bottom-right-radius: 8px;
  border-top-right-radius: 28px;
  background:
    linear-gradient(90deg, rgba(47, 93, 80, 0.12) 0 6px, transparent 6px),
    radial-gradient(circle at 100% 0%, rgba(197, 139, 92, 0.12), transparent 34%),
    rgba(255, 253, 249, 0.96);
  color: var(--text-primary);
}

.qa-conversation__bubble.is-user .qa-conversation__message-body {
  gap: 8px;
}

.qa-conversation__bubble.is-user .qa-conversation__message-body p {
  color: var(--text-primary);
}

.qa-conversation__bubble.is-assistant {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  gap: 12px;
  border: 1px solid rgba(216, 207, 191, 0.7);
  border-bottom-left-radius: 8px;
  background: rgba(255, 253, 249, 0.92);
}

.qa-conversation__mascot-avatar {
  width: 46px;
  height: 46px;
  overflow: hidden;
  border: 2px solid rgba(255, 253, 249, 0.94);
  border-radius: 16px;
  background: rgba(255, 253, 249, 0.9);
  box-shadow: 0 10px 20px rgba(47, 93, 80, 0.1);
}

.qa-conversation__mascot-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 50% 18%;
}

.qa-conversation__speaker {
  color: var(--brand-primary);
  font-size: 0.78rem;
  font-weight: 900;
  letter-spacing: 0.08em;
}

.qa-conversation__bubble.is-thinking {
  color: var(--text-secondary);
  border: 1px dashed rgba(47, 93, 80, 0.2);
}

.qa-conversation__message-body {
  display: grid;
  gap: 12px;
}

.qa-conversation__message-body p,
.qa-conversation__message-body ul,
.qa-conversation__bubble ol {
  margin: 0;
}

.qa-conversation__message-body p {
  white-space: pre-wrap;
  word-break: break-word;
}

.qa-conversation__message-body ul {
  display: grid;
  gap: 8px;
  padding-left: 0;
  list-style: none;
}

.qa-conversation__message-body li {
  position: relative;
  padding-left: 18px;
  word-break: break-word;
}

.qa-conversation__message-body li::before {
  content: '';
  position: absolute;
  top: 0.82em;
  left: 2px;
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--brand-primary);
}

.qa-conversation__references {
  grid-column: 2;
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.qa-conversation__inline-reference {
  padding: 13px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.58);
  border: 1px solid rgba(47, 93, 80, 0.08);
}

.qa-conversation__inline-reference p {
  margin: 8px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.qa-conversation__bubble ol {
  padding-left: 20px;
}

:deep(mark) {
  padding: 0 2px;
  border-radius: 4px;
  background: rgba(192, 139, 92, 0.22);
}

@media (max-width: 640px) {
  .qa-conversation__bubble {
    max-width: 100%;
  }

  .qa-conversation__bubble.is-assistant {
    grid-template-columns: 38px minmax(0, 1fr);
  }

  .qa-conversation__mascot-avatar {
    width: 38px;
    height: 38px;
    border-radius: 14px;
  }

  .qa-conversation__references {
    grid-column: 1 / -1;
  }
}
</style>
