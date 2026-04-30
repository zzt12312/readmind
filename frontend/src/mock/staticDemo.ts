import type { AxiosRequestConfig } from 'axios'
import type { QaAskPayload, QaResponse, QaStreamEventHandlers } from '@/types/qa'

function makeDemoCover(title: string, author: string, colors: [string, string], mark: string) {
  const [from, to] = colors
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="520" viewBox="0 0 360 520">
    <defs>
      <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
        <stop offset="0" stop-color="${from}"/>
        <stop offset="1" stop-color="${to}"/>
      </linearGradient>
      <radialGradient id="glow" cx="25%" cy="18%" r="78%">
        <stop offset="0" stop-color="#fff9e8" stop-opacity=".42"/>
        <stop offset=".58" stop-color="#fff9e8" stop-opacity=".08"/>
        <stop offset="1" stop-color="#fff9e8" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <rect width="360" height="520" rx="28" fill="url(#bg)"/>
    <rect width="360" height="520" rx="28" fill="url(#glow)"/>
    <path d="M38 66h284M38 454h284" stroke="#fff8e8" stroke-opacity=".42" stroke-width="2"/>
    <circle cx="282" cy="112" r="48" fill="#fff8e8" fill-opacity=".16"/>
    <text x="46" y="152" fill="#fffaf1" font-family="serif" font-size="42" font-weight="800">${escapeSvg(title)}</text>
    <text x="48" y="205" fill="#fffaf1" fill-opacity=".86" font-family="sans-serif" font-size="19" font-weight="700">${escapeSvg(author)}</text>
    <text x="48" y="390" fill="#fffaf1" fill-opacity=".2" font-family="serif" font-size="112" font-weight="900">${escapeSvg(mark)}</text>
    <text x="48" y="446" fill="#fffaf1" fill-opacity=".76" font-family="sans-serif" font-size="15" letter-spacing="3">READMIND DEMO</text>
  </svg>`
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

function escapeSvg(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

const demoBooks = [
  {
    id: 1,
    title: '认知觉醒',
    author: '周岭',
    notes: 42,
    tags: ['成长', '认知', '长期主义'],
    category: '心理学',
    reading_date: '2026-03-12',
    last_read_date: '2026-04-24',
    reading_time: '9小时18分钟',
    progress: '100%',
    cover: makeDemoCover('认知觉醒', '周岭', ['#3f6f64', '#c08b5c'], '醒'),
    reading_notes: '关于注意力、行动力和长期成长的阅读摘录。',
  },
  {
    id: 2,
    title: '纳瓦尔宝典',
    author: '埃里克·乔根森',
    notes: 36,
    tags: ['财富', '判断力', '幸福'],
    category: '商业',
    reading_date: '2026-02-20',
    last_read_date: '2026-04-18',
    reading_time: '7小时42分钟',
    progress: '100%',
    cover: makeDemoCover('纳瓦尔宝典', '埃里克·乔根森', ['#263f55', '#b98154'], '富'),
    reading_notes: '关于杠杆、复利、专长和自由的摘录。',
  },
  {
    id: 3,
    title: '南明史',
    author: '顾诚',
    notes: 83,
    tags: ['历史', '制度', '权力'],
    category: '历史',
    reading_date: '2026-01-05',
    last_read_date: '2026-04-26',
    reading_time: '18小时36分钟',
    progress: '86%',
    cover: makeDemoCover('南明史', '顾诚', ['#5a2f2d', '#c6a05d'], '史'),
    reading_notes: '关于政治秩序、组织失灵和历史转折的摘录。',
  },
  {
    id: 4,
    title: '置身事内',
    author: '兰小欢',
    notes: 51,
    tags: ['经济', '地方政府', '制度'],
    category: '经济',
    reading_date: '2026-03-28',
    last_read_date: '2026-04-21',
    reading_time: '11小时08分钟',
    progress: '100%',
    cover: makeDemoCover('置身事内', '兰小欢', ['#274f48', '#d2a46d'], '制'),
    reading_notes: '关于地方政府、财政激励和经济结构的摘录。',
  },
  {
    id: 5,
    title: '被讨厌的勇气',
    author: '岸见一郎 / 古贺史健',
    notes: 29,
    tags: ['心理学', '关系', '自我接纳'],
    category: '心理学',
    reading_date: '2026-04-06',
    last_read_date: '2026-04-20',
    reading_time: '5小时26分钟',
    progress: '100%',
    cover: makeDemoCover('被讨厌的勇气', '岸见一郎 / 古贺史健', ['#5b6f8f', '#d7a178'], '勇'),
    reading_notes: '关于课题分离、自由和人际关系的摘录。',
  },
  {
    id: 6,
    title: '原则',
    author: 'Ray Dalio',
    notes: 44,
    tags: ['决策', '反馈', '系统'],
    category: '商业',
    reading_date: '2026-02-08',
    last_read_date: '2026-04-16',
    reading_time: '8小时54分钟',
    progress: '100%',
    cover: makeDemoCover('原则', 'Ray Dalio', ['#233d4d', '#8aa29e'], '则'),
    reading_notes: '关于原则、组织透明度和反馈机制的摘录。',
  },
  {
    id: 7,
    title: '穷查理宝典',
    author: '查理·芒格',
    notes: 58,
    tags: ['投资', '多元思维', '决策'],
    category: '投资',
    reading_date: '2026-01-22',
    last_read_date: '2026-04-13',
    reading_time: '12小时20分钟',
    progress: '100%',
    cover: makeDemoCover('穷查理宝典', '查理·芒格', ['#4a3a2a', '#c49a5a'], '智'),
    reading_notes: '关于多元思维模型、逆向思考和长期决策质量的摘录。',
  },
  {
    id: 8,
    title: '事实',
    author: '汉斯·罗斯林',
    notes: 33,
    tags: ['数据', '世界观', '理性'],
    category: '社会科学',
    reading_date: '2026-03-02',
    last_read_date: '2026-04-11',
    reading_time: '6小时48分钟',
    progress: '100%',
    cover: makeDemoCover('事实', '汉斯·罗斯林', ['#2f5d6b', '#7fb3a8'], '真'),
    reading_notes: '关于数据误判、直觉偏差和更理性的世界观。',
  },
  {
    id: 9,
    title: '人类简史',
    author: '尤瓦尔·赫拉利',
    notes: 67,
    tags: ['历史', '文明', '叙事'],
    category: '历史',
    reading_date: '2026-01-18',
    last_read_date: '2026-04-09',
    reading_time: '13小时12分钟',
    progress: '100%',
    cover: makeDemoCover('人类简史', '尤瓦尔·赫拉利', ['#5c4732', '#839073'], '人'),
    reading_notes: '关于认知革命、共同想象和制度叙事的摘录。',
  },
  {
    id: 10,
    title: '深度工作',
    author: 'Cal Newport',
    notes: 38,
    tags: ['专注', '工作方法', '长期主义'],
    category: '效率',
    reading_date: '2026-04-01',
    last_read_date: '2026-04-27',
    reading_time: '7小时06分钟',
    progress: '100%',
    cover: makeDemoCover('深度工作', 'Cal Newport', ['#263c62', '#6d9a8d'], '深'),
    reading_notes: '关于注意力管理、深度产出和抗干扰工作方式的摘录。',
  },
]

const demoNotes = [
  {
    id: 101,
    book_id: 1,
    book_title: '认知觉醒',
    chapter: '第一章 大脑',
    excerpt: '真正的成长不是突然变强，而是开始看见自己注意力的流向。',
    comment: '注意力是个人成长最底层的资产。',
    tags: ['注意力', '成长', '长期主义'],
    timestamp: '2026-04-24',
    source_path: 'demo/认知觉醒.md',
  },
  {
    id: 102,
    book_id: 1,
    book_title: '认知觉醒',
    chapter: '第三章 行动力',
    excerpt: '先完成一个小闭环，比等待完整计划更能推动真实改变。',
    comment: '可以作为复习系统的产品原则。',
    tags: ['行动力', '反馈', '复利'],
    timestamp: '2026-04-23',
    source_path: 'demo/认知觉醒.md',
  },
  {
    id: 201,
    book_id: 2,
    book_title: '纳瓦尔宝典',
    chapter: '财富',
    excerpt: '利用杠杆和复利，把判断力沉淀成长期可积累的成果。',
    comment: '和阅读笔记系统的长期价值很贴合。',
    tags: ['财富', '复利', '判断力'],
    timestamp: '2026-04-18',
    source_path: 'demo/纳瓦尔宝典.md',
  },
  {
    id: 202,
    book_id: 2,
    book_title: '纳瓦尔宝典',
    chapter: '幸福',
    excerpt: '幸福更多来自减少内在冲突，而不是不断增加外部满足。',
    comment: '适合和心理学类书籍建立图谱关联。',
    tags: ['幸福', '自我接纳'],
    timestamp: '2026-04-17',
    source_path: 'demo/纳瓦尔宝典.md',
  },
  {
    id: 301,
    book_id: 3,
    book_title: '南明史',
    chapter: '弘光政权',
    excerpt: '组织在危机中暴露出的不是单点错误，而是长期制度惯性的总和。',
    comment: '历史阅读里最值得反复回看的判断。',
    tags: ['历史', '制度', '危机'],
    timestamp: '2026-04-26',
    source_path: 'demo/南明史.md',
  },
  {
    id: 302,
    book_id: 3,
    book_title: '南明史',
    chapter: '隆武政权',
    excerpt: '权力分散而缺少共同目标时，局部努力很难汇聚成整体行动。',
    comment: '可和组织管理、协作主题关联。',
    tags: ['权力', '组织', '协作'],
    timestamp: '2026-04-25',
    source_path: 'demo/南明史.md',
  },
  {
    id: 401,
    book_id: 4,
    book_title: '置身事内',
    chapter: '地方政府',
    excerpt: '理解中国经济运行，必须理解地方政府在资源配置中的角色。',
    comment: '解释制度激励非常关键。',
    tags: ['经济', '制度', '地方政府'],
    timestamp: '2026-04-21',
    source_path: 'demo/置身事内.md',
  },
  {
    id: 402,
    book_id: 4,
    book_title: '置身事内',
    chapter: '财政与激励',
    excerpt: '激励结构决定了组织会持续奖励什么，也会持续忽视什么。',
    comment: '和南明史里的制度惯性有互文。',
    tags: ['激励', '制度', '组织'],
    timestamp: '2026-04-19',
    source_path: 'demo/置身事内.md',
  },
  {
    id: 501,
    book_id: 5,
    book_title: '被讨厌的勇气',
    chapter: '课题分离',
    excerpt: '自由不是被所有人喜欢，而是能够承担自己的选择。',
    comment: '适合做复习卡片。',
    tags: ['自由', '关系', '自我接纳'],
    timestamp: '2026-04-20',
    source_path: 'demo/被讨厌的勇气.md',
  },
  {
    id: 601,
    book_id: 6,
    book_title: '原则',
    chapter: '工作原则',
    excerpt: '一个组织最重要的不是避免错误，而是让错误能够被看见、讨论和修正。',
    comment: '这和复习系统里的反馈闭环很像。',
    tags: ['反馈', '组织', '决策'],
    timestamp: '2026-04-16',
    source_path: 'demo/原则.md',
  },
  {
    id: 602,
    book_id: 6,
    book_title: '原则',
    chapter: '生活原则',
    excerpt: '原则是把过去的痛苦和经验，压缩成未来可以复用的判断规则。',
    comment: '适合作为“笔记为什么要复用”的解释。',
    tags: ['原则', '复用', '判断力'],
    timestamp: '2026-04-15',
    source_path: 'demo/原则.md',
  },
  {
    id: 701,
    book_id: 7,
    book_title: '穷查理宝典',
    chapter: '多元思维模型',
    excerpt: '只用一种模型看世界，就像手里只有锤子，看什么都像钉子。',
    comment: '知识图谱应该帮助用户跨学科连接模型。',
    tags: ['多元思维', '模型', '投资'],
    timestamp: '2026-04-13',
    source_path: 'demo/穷查理宝典.md',
  },
  {
    id: 702,
    book_id: 7,
    book_title: '穷查理宝典',
    chapter: '逆向思考',
    excerpt: '要获得好结果，先持续避免那些显而易见的坏决策。',
    comment: '可以转成复习题：哪些错误最值得提前避开？',
    tags: ['逆向思考', '决策', '长期主义'],
    timestamp: '2026-04-12',
    source_path: 'demo/穷查理宝典.md',
  },
  {
    id: 801,
    book_id: 8,
    book_title: '事实',
    chapter: '负面型思维',
    excerpt: '人们容易高估坏消息的比例，因为坏消息更容易被传播和记住。',
    comment: '数据看板要帮助用户看到真实趋势，而不是只凭感觉判断。',
    tags: ['数据', '偏差', '理性'],
    timestamp: '2026-04-11',
    source_path: 'demo/事实.md',
  },
  {
    id: 802,
    book_id: 8,
    book_title: '事实',
    chapter: '单一视角',
    excerpt: '真正理性的判断，往往来自同时保留多个解释框架。',
    comment: '和多元思维模型形成互文。',
    tags: ['世界观', '模型', '理性'],
    timestamp: '2026-04-10',
    source_path: 'demo/事实.md',
  },
  {
    id: 901,
    book_id: 9,
    book_title: '人类简史',
    chapter: '认知革命',
    excerpt: '大规模协作依赖共同想象，制度、货币和组织都建立在共享叙事上。',
    comment: '能与南明史、置身事内里的制度主题建立连接。',
    tags: ['文明', '叙事', '制度'],
    timestamp: '2026-04-09',
    source_path: 'demo/人类简史.md',
  },
  {
    id: 902,
    book_id: 9,
    book_title: '人类简史',
    chapter: '农业革命',
    excerpt: '短期收益可能会把人推向长期更难退出的结构。',
    comment: '适合和长期主义、制度惯性一起复习。',
    tags: ['历史', '长期主义', '结构'],
    timestamp: '2026-04-08',
    source_path: 'demo/人类简史.md',
  },
  {
    id: 1001,
    book_id: 10,
    book_title: '深度工作',
    chapter: '深度工作是有价值的',
    excerpt: '在注意力稀缺的时代，能长时间专注处理复杂问题，本身就是稀缺能力。',
    comment: '和认知觉醒的注意力主题强相关。',
    tags: ['专注', '注意力', '长期主义'],
    timestamp: '2026-04-27',
    source_path: 'demo/深度工作.md',
  },
  {
    id: 1002,
    book_id: 10,
    book_title: '深度工作',
    chapter: '减少浅层工作',
    excerpt: '如果不主动设计工作节奏，浅层任务会自然占满所有时间。',
    comment: '产品上可以提醒用户把复习拆成短而稳定的节奏。',
    tags: ['专注', '反馈', '行动力'],
    timestamp: '2026-04-26',
    source_path: 'demo/深度工作.md',
  },
]

const noteFilters = {
  categories: [...new Set(demoBooks.map((book) => book.category))],
  tags: [...new Set(demoNotes.flatMap((note) => note.tags))],
  chapters: [...new Set(demoNotes.map((note) => note.chapter))],
}

function bookBrief(bookId: number) {
  const book = demoBooks.find((item) => item.id === bookId) ?? demoBooks[0]
  return {
    id: book.id,
    title: book.title,
    cover: book.cover,
    notes: book.notes,
  }
}

const graphClusters = [
  {
    id: 0,
    name: '长期成长',
    topics: ['注意力', '行动力', '复利', '反馈'],
    note_count: 4,
    book_count: 2,
    sample_books: [
      bookBrief(1),
      bookBrief(10),
    ],
    sample_excerpts: [
      { note_id: 101, book_id: 1, book_title: '认知觉醒', excerpt: '真正的成长不是突然变强，而是开始看见自己注意力的流向。' },
      { note_id: 201, book_id: 2, book_title: '纳瓦尔宝典', excerpt: '利用杠杆和复利，把判断力沉淀成长期可积累的成果。' },
    ],
  },
  {
    id: 1,
    name: '制度与组织',
    topics: ['制度', '组织', '激励', '协作', '叙事'],
    note_count: 7,
    book_count: 4,
    sample_books: [
      bookBrief(3),
      bookBrief(4),
      bookBrief(6),
      bookBrief(9),
    ],
    sample_excerpts: [
      { note_id: 301, book_id: 3, book_title: '南明史', excerpt: '组织在危机中暴露出的不是单点错误，而是长期制度惯性的总和。' },
      { note_id: 402, book_id: 4, book_title: '置身事内', excerpt: '激励结构决定了组织会持续奖励什么，也会持续忽视什么。' },
    ],
  },
  {
    id: 2,
    name: '自我与关系',
    topics: ['自由', '幸福', '课题分离', '自我接纳', '理性'],
    note_count: 5,
    book_count: 3,
    sample_books: [
      bookBrief(5),
      bookBrief(2),
      bookBrief(8),
    ],
    sample_excerpts: [
      { note_id: 501, book_id: 5, book_title: '被讨厌的勇气', excerpt: '自由不是被所有人喜欢，而是能够承担自己的选择。' },
      { note_id: 202, book_id: 2, book_title: '纳瓦尔宝典', excerpt: '幸福更多来自减少内在冲突，而不是不断增加外部满足。' },
    ],
  },
  {
    id: 3,
    name: '决策与模型',
    topics: ['多元思维', '决策', '判断力', '模型', '逆向思考'],
    note_count: 6,
    book_count: 4,
    sample_books: [
      bookBrief(7),
      bookBrief(6),
      bookBrief(8),
      bookBrief(2),
    ],
    sample_excerpts: [
      { note_id: 701, book_id: 7, book_title: '穷查理宝典', excerpt: '只用一种模型看世界，就像手里只有锤子，看什么都像钉子。' },
      { note_id: 602, book_id: 6, book_title: '原则', excerpt: '原则是把过去的痛苦和经验，压缩成未来可以复用的判断规则。' },
    ],
  },
]

const reviewCards = demoNotes.slice(0, 10).map((note, index) => ({
  id: note.id,
  book_id: note.book_id,
  note_id: note.id,
  question: `这条来自《${note.book_title}》的笔记，最值得回看的核心判断是什么？`,
  source: `${note.book_title} · ${note.chapter}`,
  answer: note.comment || note.excerpt,
  tags: note.tags,
  review_count: index % 3,
  mastery_score: index % 2,
  last_reviewed_at: index % 2 ? '2026-04-28T10:00:00' : '',
  next_review_at: '2026-04-29T09:00:00',
}))

function buildDashboard() {
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

function buildAnalytics() {
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

function buildNoteList(config: AxiosRequestConfig) {
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

function buildReviewResponse(config: AxiosRequestConfig) {
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

function buildGraph() {
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

const demoJobs = [
  {
    id: 'demo-summary',
    job_type: 'book_summary',
    status: 'success',
    resource_type: 'book',
    resource_id: '1',
    payload: {},
    result: { book_id: 1, summary: '演示摘要已生成' },
    error_message: '',
    progress: 100,
    message: '《认知觉醒》摘要已从演示缓存返回',
    created_at: '2026-04-29 10:00',
    started_at: '2026-04-29 10:00',
    finished_at: '2026-04-29 10:01',
  },
  {
    id: 'demo-insight',
    job_type: 'notes_insight',
    status: 'success',
    resource_type: 'notes',
    resource_id: 'demo',
    payload: {},
    result: { references: demoNotes.slice(0, 2).map((note) => ({ book: note.book_title, chapter: note.chapter, excerpt: note.excerpt })) },
    error_message: '',
    progress: 100,
    message: 'AI 洞察已生成',
    created_at: '2026-04-29 10:03',
    started_at: '2026-04-29 10:03',
    finished_at: '2026-04-29 10:04',
  },
]

export function resolveStaticDemoResponse(config: AxiosRequestConfig) {
  const method = (config.method || 'get').toLowerCase()
  const url = String(config.url || '').split('?')[0]
  const normalizedUrl = url.replace(/^\/api/, '')

  if (normalizedUrl === '/llm/health') {
    return {
      provider: 'Static Demo',
      demo_mode: true,
      base_url: 'static-demo',
      model: 'cached-ai-preview',
      api_key_loaded: false,
      connected: false,
      fallback_mode: true,
      detail: '当前为静态演示模式，页面使用内置缓存展示 AI 效果。',
      embedding_model: 'static-cache',
      embedding_provider: 'static',
      embedding_status: 'ready',
      embedding_error: '',
    }
  }

  if (normalizedUrl === '/llm/embedding/warmup') {
    return { started: false, embedding_model: 'static-cache', embedding_provider: 'static', embedding_status: 'ready', embedding_error: '' }
  }

  if (normalizedUrl === '/dashboard/overview') return buildDashboard()
  if (normalizedUrl === '/analytics/overview') return buildAnalytics()
  if (normalizedUrl === '/books') return { items: demoBooks }

  const bookDetailMatch = normalizedUrl.match(/^\/books\/(\d+)$/)
  if (bookDetailMatch) {
    const book = demoBooks.find((item) => item.id === Number(bookDetailMatch[1])) ?? demoBooks[0]
    return { book, summary: buildBookSummary(book.id).summary }
  }

  const bookSummaryMatch = normalizedUrl.match(/^\/books\/(\d+)\/summary(?:\/regenerate)?$/)
  if (bookSummaryMatch) return buildBookSummary(Number(bookSummaryMatch[1]))

  if (normalizedUrl === '/notes') return buildNoteList(config)
  if (normalizedUrl === '/notes/summarize' && method === 'post') return buildInsightSummary()
  if (normalizedUrl === '/qa/ask' && method === 'post') return buildQaResponse((config.data ? JSON.parse(String(config.data)) : {}) as QaAskPayload)
  if (normalizedUrl === '/review/today') return buildReviewResponse(config)
  if (normalizedUrl === '/review/rate' && method === 'post') {
    return {
      progress: {
        note_id: 101,
        review_count: 2,
        mastery_score: 2,
        last_result: 'high',
        last_reviewed_at: new Date().toISOString(),
        next_review_at: '2026-05-03T09:00:00',
      },
      summary: [
        { label: '待复习', value: '5' },
        { label: '已完成', value: '1' },
        { label: '连续复习', value: '2 天' },
        { label: '掌握率', value: '67%' },
      ],
    }
  }

  if (normalizedUrl === '/insights/topics') return buildGraph()
  if (normalizedUrl === '/import/jobs' && method === 'post') {
    return {
      items: [
        {
          id: 'static-demo-upload',
          file_name: '模拟上传文件.md',
          status: 'success',
          progress: 100,
          result: '演示模式已模拟解析完成',
          source: 'static-demo',
          created_at: '2026-04-29 10:05',
          finished_at: '2026-04-29 10:05',
        },
      ],
      meta: buildImportMeta(),
    }
  }

  if (normalizedUrl === '/import/jobs') {
    return {
      items: [
        {
          id: 'static-demo-import',
          file_name: '静态演示缓存',
          status: 'success',
          progress: 100,
          result: `${demoBooks.length} 本 / ${demoNotes.length} 条`,
          source: 'static-demo',
          created_at: '2026-04-29 10:00',
          finished_at: '2026-04-29 10:00',
        },
      ],
      meta: buildImportMeta(),
    }
  }

  if (normalizedUrl === '/import/sync-local' && method === 'post') {
    return {
      item: {
        id: 'static-demo-sync',
        file_name: '静态演示缓存',
        status: 'success',
        progress: 100,
        result: `${demoBooks.length} 本 / ${demoNotes.length} 条`,
        source: 'static-demo',
        created_at: '2026-04-29 10:00',
        finished_at: '2026-04-29 10:00',
      },
      meta: buildImportMeta(),
    }
  }

  if (normalizedUrl === '/jobs') return { items: demoJobs }
  if (/^\/jobs\/[^/]+$/.test(normalizedUrl)) return demoJobs[0]
  if (/^\/jobs\/[^/]+\/retry$/.test(normalizedUrl)) return { ...demoJobs[0], status: 'processing', progress: 20, message: '演示任务已重新加入队列' }

  return undefined
}

function buildImportMeta() {
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

function buildBookSummary(bookId: number) {
  const book = demoBooks.find((item) => item.id === bookId) ?? demoBooks[0]
  return {
    book_id: book.id,
    cached: true,
    regenerated: false,
    status: 'success',
    summary: `《${book.title}》在演示缓存中的核心价值，是帮助你把「${book.tags.slice(0, 3).join('、')}」这些主题重新组织起来。ReadMind 会先从原始摘录中找到证据，再把它整理成可追问、可复习、可回看的知识线索。`,
  }
}

function buildInsightSummary() {
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

function buildQaResponse(payload: QaAskPayload): QaResponse {
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

export async function streamStaticQuestion(payload: QaAskPayload, handlers: QaStreamEventHandlers, signal?: AbortSignal) {
  const response = buildQaResponse(payload)
  if (signal?.aborted) throw new DOMException('Aborted', 'AbortError')

  handlers.onMeta?.({
    question: response.question,
    references: response.references,
    retrieval_mode: response.retrieval_mode,
    query_rewrite: response.query_rewrite,
    evidence: response.evidence,
  })
  handlers.onStatus?.({
    phase: 'retrieving',
    label: '正在检索演示缓存',
    detail: '静态演示站会从内置阅读摘录里找引用，不会上传你的真实数据。',
  })

  await wait(180)
  handlers.onStatus?.({
    phase: 'fallback',
    label: '正在生成缓存回答',
    detail: '签签会基于演示引用组织一段可追溯回答。',
  })

  for (const chunk of response.answer.match(/.{1,34}/gs) ?? [response.answer]) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError')
    handlers.onDelta?.({ content: chunk })
    await wait(28)
  }

  handlers.onDone?.(response)
}

function wait(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms))
}
