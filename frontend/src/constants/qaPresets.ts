import type { BookItem } from '@/types/book'

export const DEFAULT_QA_DRAFT = '我最近的阅读笔记里，哪些观点最值得复习？'

export const QA_QUICK_PROMPTS = [
  '这本书里关于长期主义提到了什么',
  '帮我总结最近三本书共同观点',
  '只检索当前书籍，总结其中关于行动系统的内容',
]

export function buildFollowupPrompts(scope: 'all-books' | 'current-book', book: BookItem | null) {
  if (scope === 'current-book' && book) {
    return [
      `继续追问《${book.title}》里最值得执行的 3 个建议`,
      `从《${book.title}》里挑出最容易忽略的一个观点`,
      `结合这本书的笔记，帮我整理一个复习清单`,
    ]
  }

  return [
    '把刚才的回答改写成 3 条可执行建议',
    '继续比较这些观点之间的共性和差异',
    '基于这些笔记，帮我列出 3 个值得复习的问题',
  ]
}

export function buildCurrentBookPrompts(book: BookItem | null) {
  if (!book) return []
  return [
    `《${book.title}》里最值得复习的 5 个观点是什么？`,
    `《${book.title}》里有哪些可以直接执行的建议？`,
    `只基于《${book.title}》，帮我整理 3 个复习问题`,
  ]
}

export function buildDemoQaDefaults() {
  return {
    scope: 'current-book' as const,
    bookId: 3,
    draft: '《南明史》里最值得回看的 3 个观点是什么？',
  }
}

export function buildPersonalQaDefaults(books: BookItem[]) {
  const latestBook = [...books].sort((left, right) =>
    (right.last_read_date || right.reading_date || '').localeCompare(left.last_read_date || left.reading_date || ''),
  )[0]

  if (!latestBook) {
    return {
      scope: 'all-books' as const,
      bookId: undefined,
      draft: '帮我总结最近三本书共同观点',
    }
  }

  return {
    scope: 'current-book' as const,
    bookId: latestBook.id,
    draft: `《${latestBook.title}》里最值得回看的 3 个观点是什么？`,
  }
}
