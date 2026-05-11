// Demo data is intentionally realistic enough for the public preview.
// Keep raw records here; put URL behavior and payload shaping in sibling files.
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

export const demoBooks = [
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

export const demoNotes = [
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

export const noteFilters = {
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

export const graphClusters = [
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

export const reviewCards = demoNotes.slice(0, 10).map((note, index) => ({
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
