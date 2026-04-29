import type { ImportSyncFeedback } from '@/types/import'
import type { ReviewLevel } from '@/types/review'

export type MascotMood = 'default' | 'happy' | 'thinking' | 'reminder'

export interface MascotCue {
  mood: MascotMood
  message: string
  celebrating?: boolean
}

export function buildDashboardMascotCue(firstActionTitle?: string): MascotCue {
  if (firstActionTitle) {
    return {
      mood: 'happy',
      message: `今天先从「${firstActionTitle}」开始就好，我会帮你把后面的想法夹好。`,
    }
  }

  return {
    mood: 'default',
    message: '今天也慢慢来，我会陪你把读过的内容整理成不会丢失的想法。',
  }
}

export function buildImportMascotCue(feedback: ImportSyncFeedback): MascotCue {
  if (feedback.status === 'success') {
    return {
      mood: 'happy',
      message: `整理好了，${feedback.book_count} 本书和 ${feedback.note_count} 条笔记已经回到工作台。`,
      celebrating: true,
    }
  }

  if (feedback.status === 'failed') {
    return {
      mood: 'reminder',
      message: '好像没找到书架，我们一起检查一下路径和目录权限。',
    }
  }

  if (feedback.status === 'processing') {
    return {
      mood: 'thinking',
      message: '我正在翻你的书架，稍等一下。',
    }
  }

  return {
    mood: 'default',
    message: '准备好后点一下同步，我会帮你把书和摘录整理回来。',
  }
}

export function buildReviewRatingMascotCue(level?: ReviewLevel | null): MascotCue {
  if (level === 'high') {
    return {
      mood: 'happy',
      message: '这条想法已经更牢了，下次可以晚一点再见。',
      celebrating: true,
    }
  }

  if (level === 'medium') {
    return {
      mood: 'reminder',
      message: '已经有印象了，我们再多见几次就会稳。',
    }
  }

  if (level === 'low') {
    return {
      mood: 'thinking',
      message: '没关系，这张我会帮你早点放回来。',
    }
  }

  return {
    mood: 'default',
    message: '先看答案，再按真实感觉评分就好。忘记不是失败，只是下一次复习的线索。',
  }
}

export function buildReviewCompletionMascotCue(completedCount: number, total: number): MascotCue {
  const reviewedText = total ? `${completedCount}/${total}` : `${completedCount}`

  return {
    mood: 'happy',
    message: `这组复习完成了，今天已经认真见过 ${reviewedText} 张卡片。休息一下也很好。`,
    celebrating: true,
  }
}

export function buildNoteInsightMascotCue(options: {
  refreshing: boolean
  hasGeneratedInsight: boolean
  status: '' | 'queued' | 'processing' | 'success' | 'failed' | 'canceled'
}): MascotCue {
  if (options.status === 'queued' || options.status === 'processing' || options.refreshing) {
    return {
      mood: 'thinking',
      message: '我正在把这些摘录串成一条线，等会儿会把重点和可复习的问题整理出来。',
    }
  }

  if (options.status === 'failed') {
    return {
      mood: 'reminder',
      message: '这次整理没有成功，换一个更具体的筛选范围再试试也可以。',
    }
  }

  if (options.hasGeneratedInsight) {
    return {
      mood: 'happy',
      message: '我找到了一些反复出现的想法，你可以先从核心结论和复习问题看起。',
      celebrating: options.status === 'success',
    }
  }

  return {
    mood: 'default',
    message: '选一本书、一个标签或搜索关键词后，我可以帮你把这组笔记整理成洞察。',
  }
}

export function buildEmptyNotesMascotCue(): MascotCue {
  return {
    mood: 'reminder',
    message: '没有搜到结果也没关系，换个更短的关键词，或者点一个标签，我再帮你找找。',
  }
}

export function buildQaMascotCue(options: {
  loading: boolean
  hasAnswer: boolean
  scopedBookTitle?: string
}): MascotCue {
  if (options.loading) {
    return {
      mood: 'thinking',
      message: '我正在你的笔记里找证据，找到可靠引用后再回答你。',
    }
  }

  if (options.hasAnswer) {
    return {
      mood: 'happy',
      message: '这次回答已经带上引用了，你可以点开原笔记核对。',
      celebrating: true,
    }
  }

  if (options.scopedBookTitle) {
    return {
      mood: 'default',
      message: `我会只翻《${options.scopedBookTitle}》这本书，帮你找出里面的想法。`,
    }
  }

  return {
    mood: 'default',
    message: '你可以像聊天一样问我，我会先检索你的书摘，再整理成回答。',
  }
}
