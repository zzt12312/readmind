import type { AxiosRequestConfig } from 'axios'
import type { QaAskPayload, QaResponse } from '@/types/qa'
import { demoBooks, demoNotes, graphClusters, noteFilters, reviewCards } from './data'

// Payload builders translate raw demo records into the same shapes returned by the backend.
export function buildDashboard() {
  return {
    metrics: [
      { label: '书籍总数', value: demoBooks.length, hint: '演示缓存中的阅读书籍' },
      { label: '笔记总数', value: demoNotes.length, hint: '已解析的高亮与想法' },
      { label: '活跃主题', value: 12, hint: '跨书出现的高频主题' },
      { label: '待复习', value: reviewCards.length, hint: '今天可以轻量回看的卡片' },
    ],
    recent_books: demoBooks.map((book) => ({ id: book.id, title: book.title, notes: book.notes, updated: book.last_read_date, cover: book.cover })),
    active_topics: ['长期主义', '制度', '复利', '组织', '注意力', '判断力', '多元思维', '数据', '叙事'],
    review_summary: {
      suggested_count: 6,
      due_count: 6,
      streak_days: 2,
      mastery_rate: '58%',
    },
    activation_report: {
      title: '演示书库已经整理完成',
      summary: '当前演示缓存包含书籍、笔记、主题、复习卡片和预生成问答结果，可以直接体验从浏览到追问再到复习的完整闭环。',
      asset_cards: [
        { label: '可浏览书籍', value: `${demoBooks.length} 本`, hint: '覆盖历史、心理、商业、经济等方向' },
        { label: '结构化笔记', value: `${demoNotes.length} 条`, hint: '已提取章节、标签和原文摘录' },
        { label: '可复习卡片', value: `${reviewCards.length} 张`, hint: '适合快速体验评分反馈' },
      ],
      top_topics: ['长期主义', '制度', '组织', '判断力', '复利'],
      recent_books: demoBooks.slice(0, 4).map((book) => book.title),
      recommended_questions: [
        '这些书里如何理解长期主义？',
        '《南明史》和《置身事内》有哪些共同主题？',
        '哪些笔记适合加入今天的复习？',
      ],
      primary_action: {
        label: '开始 5 分钟回看',
        path: '/review',
      },
      secondary_action: {
        label: '问自己的笔记',
        path: '/qa',
      },
    },
    daily_brief: {
      title: '今天可以从一小组复习开始',
      summary: '演示数据已经准备好。你可以先看笔记工作台，再问签签一个关于长期主义或制度的问题。',
      feedback_items: [
        { label: '推荐复习', value: '6 张', hint: '先回看一小组，不需要一次做完。' },
        { label: '最活跃主题', value: '制度', hint: '历史和经济笔记之间有明显关联。' },
        { label: '值得追问', value: '长期主义', hint: '可以让签签从全库里找证据。' },
        { label: '演示状态', value: '已就绪', hint: '当前为静态演示缓存，不会上传真实数据。' },
      ],
      suggested_actions: [
        { label: '体验智能问答', type: 'notes', path: '/qa' },
        { label: '查看笔记工作台', type: 'notes', path: '/notes' },
        { label: '开始复习', type: 'review', path: '/review' },
      ],
      highlights: {
        topics: ['长期主义', '制度', '复利'],
        book: { id: 3, title: '南明史' },
        author: '顾诚',
      },
    },
    action_queue: [
      { label: 'Ask', title: '问签签一个问题', hint: '例如：这些书里如何理解长期主义？', path: '/qa', accent: 'primary' },
      { label: 'Review', title: '完成 6 张卡片', hint: '用评分反馈把重点想法放回记忆里。', path: '/review', accent: 'warm' },
      { label: 'Graph', title: '查看主题关系', hint: '看看制度、组织和长期主义如何跨书连接。', path: '/graph', accent: 'calm' },
    ],
    recommended_review: {
      title: '制度与组织',
      reason: '《南明史》和《置身事内》都反复出现制度、组织、激励这些主题，适合今天一起回看。',
      path: '/graph',
      topics: ['制度', '组织', '激励'],
      book: demoBooks.find((book) => book.id === 3) ?? null,
    },
  }
}

export function buildAnalytics() {
  const readingTimeMinutes = demoBooks.reduce((total, book) => total + parseReadingMinutes(book.reading_time), 0)

  return {
    metrics: [
      { label: '累计阅读时长', value: `${Math.round(readingTimeMinutes / 60)}h`, hint: '来自演示书籍 readingTime 缓存' },
      { label: '高价值书籍', value: 5, hint: '笔记密度和复习价值较高' },
      { label: '偏好方向', value: '历史/心理/商业', hint: '主题雷达中最突出的方向' },
      { label: '复习连续', value: '2 天', hint: '演示复习进度' },
    ],
    category_preferences: buildCategoryPreferences(),
    preference_radar: [
      { label: '历史', score: 92, book_count: 1, note_count: 83 },
      { label: '心理', score: 78, book_count: 2, note_count: 71 },
      { label: '经济', score: 70, book_count: 1, note_count: 51 },
      { label: '商业', score: 64, book_count: 1, note_count: 36 },
      { label: '成长', score: 82, book_count: 2, note_count: 78 },
    ],
    reading_time_rank: demoBooks
      .map((book) => ({
        id: book.id,
        title: book.title,
        author: book.author,
        category: book.category,
        note_count: book.notes,
        reviewed_count: Math.floor(book.notes / 3),
        last_read_date: book.last_read_date,
        reading_time: book.reading_time,
        reading_time_minutes: parseReadingMinutes(book.reading_time),
        cover: book.cover,
      }))
      .sort((a, b) => b.reading_time_minutes - a.reading_time_minutes),
    high_value_matrix: demoBooks.map((book, index) => ({
      id: book.id,
      title: book.title,
      category: book.category,
      note_count: book.notes,
      reviewed_count: Math.floor(book.notes / 3),
      x: 24 + (index % 5) * 15,
      y: 36 + Math.floor(index / 5) * 26 + (index % 2) * 6,
      value_score: 68 + index * 3,
    })),
    topic_rank: [
      { topic: '制度', count: 16, share: 16 },
      { topic: '长期主义', count: 14, share: 14 },
      { topic: '组织', count: 12, share: 12 },
      { topic: '判断力', count: 11, share: 11 },
      { topic: '注意力', count: 10, share: 10 },
      { topic: '多元思维', count: 8, share: 8 },
      { topic: '数据', count: 7, share: 7 },
    ],
    review_funnel: [
      { label: '全部卡片', value: 9, hint: '可复习笔记' },
      { label: '今日到期', value: 6, hint: '建议今天回看' },
      { label: '薄弱卡片', value: 2, hint: '需要更快再见' },
      { label: '已掌握', value: 3, hint: '可以延长间隔' },
    ],
    review_progress: { due_count: 6, streak_days: 2, mastery_rate: '58%', reviewed_count: 18, total_notes: demoNotes.length },
    reading_timeline: [
      { period: '2026-01', book_count: 1, books: ['南明史'] },
      { period: '2026-02', book_count: 3, books: ['纳瓦尔宝典', '原则', '穷查理宝典'] },
      { period: '2026-03', book_count: 3, books: ['认知觉醒', '置身事内', '事实'] },
      { period: '2026-04', book_count: 3, books: ['被讨厌的勇气', '深度工作', '人类简史'] },
    ],
    author_cloud: demoBooks.map((book) => ({
      author: book.author,
      book_count: 1,
      note_count: book.notes,
      weight: Math.min(96, 42 + book.notes),
    })),
    activity_heatmap: Array.from({ length: 28 }, (_, index) => ({
      date: `2026-04-${String(index + 1).padStart(2, '0')}`,
      label: `4月${index + 1}日`,
      count: index % 5 === 0 ? 4 : index % 3,
      level: index % 5 === 0 ? 4 : index % 3,
    })),
    long_term_metrics: [
      { label: '持续复习', value: '2 天', score: 54, hint: '已经开始形成回看节奏' },
      { label: '跨书连接', value: '12 个主题', score: 78, hint: '历史、经济、心理之间有明显关联' },
      { label: '整理完成度', value: '高', score: 82, hint: '笔记已经可以被检索和问答复用' },
    ],
    recommendations: [
      {
        type: 'review',
        title: '先完成一小组复习',
        reason: '演示数据里有 6 张今日到期卡片，能快速体验从回想到评分的完整流程。',
        action_label: '去复习',
        path: '/review',
        priority: 'high',
      },
      {
        type: 'topic',
        title: '查看制度与组织主题',
        reason: '《南明史》和《置身事内》围绕制度、组织、激励形成了清晰的跨书连接。',
        action_label: '看图谱',
        path: '/graph',
        priority: 'medium',
      },
      {
        type: 'book',
        title: '回看《南明史》',
        reason: '这本书笔记密度最高，适合作为公开演示里的重点样例。',
        action_label: '查看书籍',
        path: '/books/3',
        priority: 'medium',
      },
    ],
  }
}

function parseReadingMinutes(value = '') {
  const hourMatch = value.match(/(\d+)小时/)
  const minuteMatch = value.match(/(\d+)分钟/)
  return Number(hourMatch?.[1] ?? 0) * 60 + Number(minuteMatch?.[1] ?? 0)
}

function buildCategoryPreferences() {
  const totalNotes = demoBooks.reduce((sum, book) => sum + book.notes, 0)
  const grouped = demoBooks.reduce<Record<string, { category: string; book_count: number; note_count: number }>>(
    (result, book) => {
      const current = result[book.category] ?? { category: book.category, book_count: 0, note_count: 0 }
      current.book_count += 1
      current.note_count += book.notes
      result[book.category] = current
      return result
    },
    {},
  )

  return Object.values(grouped)
    .map((item) => ({
      ...item,
      share: Math.round((item.note_count / totalNotes) * 100),
    }))
    .sort((a, b) => b.note_count - a.note_count)
}

export function buildNoteList(config: AxiosRequestConfig) {
  const params = config.params ?? {}
  const bookId = Number(params.book_id || 0)
  const keyword = String(params.q || '').trim()
  const category = String(params.category || '')
  const tag = String(params.tag || '')
  const notes = demoNotes.filter((note) => {
    const book = demoBooks.find((item) => item.id === note.book_id)
    if (bookId && note.book_id !== bookId) return false
    if (category && book?.category !== category) return false
    if (tag && !note.tags.includes(tag)) return false
    if (keyword) {
      const haystack = `${note.book_title} ${note.chapter} ${note.excerpt} ${note.comment} ${note.tags.join(' ')}`
      if (!haystack.includes(keyword)) return false
    }
    return true
  })

  return {
    items: notes,
    insight: {
      summary: '这组笔记反复出现“长期积累”和“制度约束”两个方向：一边关注个人如何通过注意力、行动力和复利持续成长，另一边关注组织如何被激励结构塑造。',
      related_topics: ['长期主义', '制度', '组织', '复利'],
      related_note: '可以追问：这些笔记如何解释长期主义？',
      references: notes.slice(0, 3).map((note) => ({ book: note.book_title, chapter: note.chapter, excerpt: note.excerpt })),
      retrieval_mode: 'static-demo',
      query_rewrite: keyword
        ? {
            original: keyword,
            applied_rules: ['静态演示：扩展相近主题词'],
            expansion_terms: ['长期主义', '制度', '复利', '组织'],
            variants: [keyword, `${keyword} 复利`, `${keyword} 制度`],
          }
        : null,
      sections: {
        core_conclusion: '这组笔记最值得关注的是：个人成长和组织运行都依赖反馈机制，长期结果往往来自持续被奖励的行为。',
        key_themes: ['长期主义', '制度', '组织', '复利'],
        review_questions: ['哪些笔记说明了复利的价值？', '制度惯性如何影响组织行动？', '个人成长为什么需要反馈闭环？'],
        action_suggestions: ['先复习 6 张卡片', '向签签追问“长期主义”', '打开知识图谱查看制度主题'],
        reasoning: '演示缓存中，历史、经济和成长类笔记都多次出现制度、反馈、复利等关键词，因此适合被放在同一条思考线中理解。',
      },
    },
    filters: noteFilters,
    pagination: {
      page: 1,
      per_page: 30,
      total: notes.length,
      total_pages: 1,
      has_more: false,
    },
  }
}

export function buildReviewResponse(config: AxiosRequestConfig) {
  const queue = String(config.params?.queue || 'due')
  const cards = queue === 'weak'
    ? reviewCards.slice(0, 2)
    : queue === 'new'
      ? reviewCards.filter((card) => card.review_count === 0)
      : reviewCards

  return {
    summary: [
      { label: '待复习', value: String(cards.length) },
      { label: '已完成', value: '0' },
      { label: '连续复习', value: '2 天' },
      { label: '掌握率', value: '58%' },
    ],
    plan: {
      default_daily_goal: 10,
      selected_daily_goal: Number(config.params?.daily_goal || 10),
      daily_goal_options: [5, 10, 20],
      suggested_today: Math.min(cards.length, 10),
      due_count: cards.length,
      batch_size: 50,
      message: '演示模式下可以自由切换队列和评分，系统会展示即时反馈。',
    },
    level_guidance: [
      { level: 'low', label: '不会', hint: '更快再次出现' },
      { level: 'medium', label: '模糊记得', hint: '进入待巩固队列' },
      { level: 'high', label: '熟练掌握', hint: '拉长下次复习间隔' },
    ],
    queue_options: [
      { value: 'due', label: '今日到期', description: '今天建议回看的卡片', count: reviewCards.length },
      { value: 'weak', label: '薄弱卡片', description: '不会或模糊记得的卡片', count: 2 },
      { value: 'new', label: '新卡片', description: '还没有复习记录的卡片', count: reviewCards.filter((card) => card.review_count === 0).length },
    ],
    card: cards[0] ?? {
      id: 0,
      book_id: 0,
      note_id: 0,
      question: '',
      source: '',
      answer: '',
      tags: [],
      review_count: 0,
      mastery_score: 0,
      last_reviewed_at: '',
      next_review_at: '',
    },
    cards,
    weak_cards: reviewCards.slice(0, 2),
    scope: { tag: '', book_id: null, queue },
  }
}

export function buildGraph() {
  return {
    overview: { topic_count: 20, cluster_count: graphClusters.length, edge_count: 9, book_count: demoBooks.length },
    filters: {
      selected: { category: '', book_id: null, time_scope: 'all', mode: 'category' },
      categories: noteFilters.categories,
      books: demoBooks.map((book) => ({ id: book.id, title: book.title, category: book.category })),
      time_scopes: [
        { label: '全部时间', value: 'all' },
        { label: '最近 30 天', value: '30d' },
        { label: '最近 90 天', value: '90d' },
      ],
      modes: [
        { label: '领域聚类', value: 'category' },
        { label: '知识主题', value: 'topic' },
      ],
    },
    clusters: graphClusters,
    graph: {
      nodes: [
        { id: '长期成长', name: '长期成长', value: 4, note_count: 4, book_count: 2, cluster_id: 0 },
        { id: '复利', name: '复利', value: 3, note_count: 3, book_count: 2, cluster_id: 0 },
        { id: '制度与组织', name: '制度与组织', value: 5, note_count: 5, book_count: 2, cluster_id: 1 },
        { id: '激励', name: '激励', value: 3, note_count: 3, book_count: 2, cluster_id: 1 },
        { id: '自我与关系', name: '自我与关系', value: 3, note_count: 3, book_count: 2, cluster_id: 2 },
        { id: '自由', name: '自由', value: 2, note_count: 2, book_count: 1, cluster_id: 2 },
        { id: '决策与模型', name: '决策与模型', value: 6, note_count: 6, book_count: 4, cluster_id: 3 },
        { id: '多元思维', name: '多元思维', value: 4, note_count: 4, book_count: 2, cluster_id: 3 },
        { id: '数据理性', name: '数据理性', value: 3, note_count: 3, book_count: 1, cluster_id: 3 },
      ],
      links: [
        { source: '长期成长', target: '复利', value: 4, co_occurrence: 4, shared_books: 2 },
        { source: '制度与组织', target: '激励', value: 5, co_occurrence: 5, shared_books: 2 },
        { source: '自我与关系', target: '自由', value: 3, co_occurrence: 3, shared_books: 1 },
        { source: '长期成长', target: '制度与组织', value: 2, co_occurrence: 2, shared_books: 1 },
        { source: '制度与组织', target: '自我与关系', value: 1, co_occurrence: 1, shared_books: 1 },
        { source: '决策与模型', target: '多元思维', value: 5, co_occurrence: 5, shared_books: 2 },
        { source: '决策与模型', target: '数据理性', value: 3, co_occurrence: 3, shared_books: 1 },
        { source: '长期成长', target: '决策与模型', value: 2, co_occurrence: 2, shared_books: 2 },
        { source: '制度与组织', target: '决策与模型', value: 2, co_occurrence: 2, shared_books: 1 },
      ],
    },
    status: 'success',
    message: '',
  }
}

export function buildImportMeta() {
  return {
    demo_mode: true,
    source_label: '静态演示缓存',
    description: '当前演示站未连接真实后端 API，页面使用内置缓存数据展示核心功能和 AI 体验。',
    vault_root: 'static-demo://readmind-cache',
    vault_status: 'ready',
    vault_message: '演示缓存已就绪，不会读取或上传你的真实 Obsidian 文件。',
    markdown_count: demoBooks.length,
  }
}

export function buildBookSummary(bookId: number) {
  const book = demoBooks.find((item) => item.id === bookId) ?? demoBooks[0]
  return {
    book_id: book.id,
    cached: true,
    regenerated: false,
    status: 'success',
    summary: `《${book.title}》在演示缓存中的核心价值，是帮助你把「${book.tags.slice(0, 3).join('、')}」这些主题重新组织起来。ReadMind 会先从原始摘录中找到证据，再把它整理成可追问、可复习、可回看的知识线索。`,
  }
}

export function buildInsightSummary() {
  return {
    status: 'success',
    summary: '这组笔记说明：长期主义并不是抽象口号，而是由注意力、反馈、制度环境和复利机制共同支撑的行动方式。',
    references: demoNotes.slice(0, 4).map((note) => ({ book: note.book_title, chapter: note.chapter, excerpt: note.excerpt })),
    sections: {
      core_conclusion: '长期积累需要稳定的反馈系统；无论是个人成长还是组织运行，结果都来自持续被奖励的行为。',
      key_themes: ['长期主义', '复利', '制度', '组织'],
      review_questions: ['为什么注意力是长期主义的起点？', '制度如何影响组织在危机中的行动？', '复利为什么需要稳定反馈？'],
      action_suggestions: ['把这组主题加入复习', '继续追问签签', '打开知识图谱查看关联'],
      reasoning: '演示缓存中，认知成长、财富判断、历史制度和经济激励类笔记出现了共同关键词，因此可以形成一条跨书主题线。',
    },
  }
}

export function buildQaResponse(payload: QaAskPayload): QaResponse {
  const question = payload.question || '这些笔记里最值得回看的观点是什么？'
  const references = demoNotes.slice(0, 4).map((note) => ({
    book: note.book_title,
    book_id: note.book_id,
    note_id: note.id,
    chapter: note.chapter,
    excerpt: note.excerpt,
    source_path: note.source_path,
  }))

  return {
    question,
    answer: `签签先从演示缓存里找了几条证据。我的理解是：这些笔记共同指向一个主题——真正能长期留下来的想法，通常都有稳定反馈和复利结构。\n\n1. 在个人成长里，注意力决定了复利发生在哪里。\n2. 在组织和制度里，激励结构决定了哪些行为会被持续放大。\n3. 在复习系统里，小步回看比一次性整理更容易形成长期记忆。\n\n如果继续追问，可以问：“这些笔记如何解释长期主义？”或者“制度和个人成长有什么共同点？”`,
    references,
    evidence: {
      reference_count: references.length,
      suggested_points: 3,
      sufficient: true,
      message: '演示缓存找到了足够引用，可生成带来源的回答。',
    },
    generation_mode: 'fallback',
    retrieval_mode: 'static-demo',
    fallback_reason: '当前为静态演示站，使用缓存数据模拟 AI 效果。',
    query_rewrite: {
      original: question,
      applied_rules: ['静态演示：补充主题词'],
      expansion_terms: ['长期主义', '复利', '制度', '组织'],
      variants: [question, '长期主义 复利', '制度 组织'],
    },
  }
}
