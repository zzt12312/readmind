# AI 阅读笔记整理与复习系统技术方案

## 1. 项目定位

### 1.1 项目名称
`ReadMind`（暂定）

### 1.2 项目目标
面向有 Obsidian 知识管理习惯的重度阅读用户，提供一套“导入微信读书笔记 -> 自动解析 -> AI 整理 -> 检索问答 -> 复习回顾”的完整工作流，解决笔记堆积、难整理、难复用的问题。

### 1.3 核心价值
- 将分散的 Markdown 读书笔记结构化
- 用 AI 自动完成分类、摘要、标签提取与主题聚合
- 提供基于个人历史笔记的问答与引用溯源
- 建立复习机制，提高笔记二次利用率

### 1.4 目标用户
- 微信读书 + Obsidian 用户
- 喜欢做摘录但缺少整理时间的学生和知识工作者
- 希望形成长期知识库的个人用户

## 2. MVP 范围

### 2.1 第一阶段必须完成的功能
1. 支持本地 Obsidian Markdown 文件批量导入
2. 自动解析书籍、章节、摘录、评论、时间等结构化信息
3. AI 自动生成摘要、标签、分类结果
4. 提供笔记列表、搜索、筛选和详情查看
5. 支持基于个人笔记库的问答，并返回引用来源
6. 支持生成复习卡片与今日待复习列表

### 2.2 暂不纳入 MVP 的功能
- 多用户协作
- 实时在线编辑 Markdown
- 复杂知识图谱可视化
- 移动端 App
- 多模型切换配置中心
- 云端对象存储

### 2.3 MVP 成功标准
- 能稳定导入 500 到 3000 条笔记
- 单本书解析成功率高，异常文件可识别
- AI 整理结果可人工修正
- 问答结果能附带来源笔记
- 系统具备连续使用价值，而不是一次性演示

## 3. 用户核心流程

### 3.1 导入流程
1. 用户选择 Obsidian 中的 Markdown 文件或目录
2. 前端上传文件到后端
3. 后端创建导入任务
4. 解析 Markdown，提取书籍、章节、摘录、评论、时间、标签
5. 生成结构化数据并入库
6. 异步触发 AI 整理任务

### 3.2 整理流程
1. 读取未处理的笔记内容
2. 生成分类、标签、摘要、主题关键词
3. 计算向量并建立检索索引
4. 产出复习卡片
5. 将结果回写数据库

### 3.3 检索问答流程
1. 用户输入问题
2. 后端对问题向量化
3. 召回相关笔记片段
4. 拼接上下文并调用大模型生成回答
5. 返回答案 + 引用片段 + 对应书籍

### 3.4 复习流程
1. 系统根据复习策略生成今日待复习卡片
2. 用户查看卡片并反馈掌握程度
3. 后端更新复习间隔和下次复习时间

## 4. 技术选型

### 4.1 前端
- `Vue 3`
- `TypeScript`
- `Vite`
- `Element Plus`
- `Pinia`
- `Vue Router`
- `Axios`
- `ECharts` 用于阅读统计和趋势展示

### 4.2 后端
- `Flask`
- `Flask-RESTX` 或 `Blueprint + Marshmallow`
- `SQLAlchemy`
- `Alembic`
- `Redis`
- `Celery`
- `PostgreSQL`

### 4.3 AI 与文本处理
- `LangChain` 或自定义轻量封装
- 向量模型 + LLM 接口
- `pgvector` 存储向量
- `markdown-it-py` 或 `mistune` 解析 Markdown
- `jieba` 或更优中文分词方案做关键词辅助处理

### 4.4 部署
- 前端部署在 `Vercel` 或 `Netlify`
- 后端部署在云服务器 / `Railway` / `Render`
- PostgreSQL 与 Redis 独立部署

## 5. 系统架构设计

### 5.1 总体架构
系统分为五层：

1. 表现层
   - Vue 页面
   - 文件上传、工作台、问答页、复习页、统计页

2. 接口层
   - Flask REST API
   - 统一鉴权、参数校验、错误处理

3. 业务层
   - 导入服务
   - 解析服务
   - AI 整理服务
   - 问答服务
   - 复习调度服务

4. 数据层
   - PostgreSQL 结构化数据
   - pgvector 向量索引
   - Redis 缓存与任务状态

5. 异步任务层
   - Celery Worker 处理导入、摘要、聚类、问答预处理

### 5.2 模块划分

#### 前端模块
- `import-center` 导入中心
- `book-library` 书籍库
- `note-workbench` 笔记工作台
- `qa-center` 智能问答
- `review-center` 复习中心
- `dashboard` 数据看板

#### 后端模块
- `auth` 认证模块
- `importer` 导入模块
- `parser` Markdown 解析模块
- `notes` 笔记管理模块
- `books` 书籍管理模块
- `ai_tasks` AI 整理模块
- `retrieval` 检索问答模块
- `review` 复习模块

## 6. 数据模型设计

### 6.1 核心实体

#### users
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| username | varchar(64) | 用户名 |
| email | varchar(128) | 邮箱 |
| password_hash | varchar(255) | 密码哈希 |
| created_at | timestamp | 创建时间 |

#### import_jobs
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| source_type | varchar(32) | 来源类型，默认 obsidian |
| file_name | varchar(255) | 文件名 |
| status | varchar(32) | pending/processing/success/failed |
| total_count | int | 文件或笔记总数 |
| success_count | int | 成功数 |
| failed_count | int | 失败数 |
| error_message | text | 错误信息 |
| created_at | timestamp | 创建时间 |
| finished_at | timestamp | 完成时间 |

#### books
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| title | varchar(255) | 书名 |
| author | varchar(255) | 作者 |
| category | varchar(128) | 分类 |
| source_path | varchar(500) | 原始文件路径 |
| note_count | int | 笔记数 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### notes
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| book_id | bigint | 所属书籍 |
| chapter | varchar(255) | 章节 |
| note_type | varchar(32) | highlight/comment/summary |
| raw_content | text | 原始内容 |
| cleaned_content | text | 清洗后内容 |
| source_time | timestamp | 原始记录时间 |
| source_order | int | 在原文中的顺序 |
| ai_summary | text | AI 简述 |
| ai_category | varchar(64) | AI 分类 |
| importance_score | numeric(5,2) | 重要度 |
| review_due_at | timestamp | 下次复习时间 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

#### note_tags
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| name | varchar(64) | 标签名 |
| tag_type | varchar(32) | manual/ai |
| created_at | timestamp | 创建时间 |

#### note_tag_relations
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| note_id | bigint | 笔记 ID |
| tag_id | bigint | 标签 ID |

#### note_embeddings
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| note_id | bigint | 笔记 ID |
| vector | vector | 向量数据 |
| model_name | varchar(64) | 向量模型名 |
| created_at | timestamp | 创建时间 |

#### topic_clusters
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| topic_name | varchar(128) | 聚类主题 |
| summary | text | 主题总结 |
| created_at | timestamp | 创建时间 |

#### review_cards
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| note_id | bigint | 来源笔记 |
| question | text | 复习问题 |
| answer | text | 复习答案 |
| review_level | int | 复习等级 |
| interval_days | int | 间隔天数 |
| due_at | timestamp | 到期时间 |
| last_reviewed_at | timestamp | 上次复习时间 |
| created_at | timestamp | 创建时间 |

#### qa_histories
| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| user_id | bigint | 用户 ID |
| question | text | 提问 |
| answer | text | 回答 |
| source_note_ids | jsonb | 引用的笔记 ID 列表 |
| created_at | timestamp | 创建时间 |

## 7. Markdown 解析设计

### 7.1 输入假设
输入为你从微信读书导出后保存到 Obsidian 的 Markdown 文件。不同导出模板可能存在格式差异，因此解析器应设计为“规则 + 容错”的方式。

### 7.2 解析目标
- 识别书名
- 识别章节标题
- 识别摘录内容
- 识别个人评论
- 识别时间戳
- 识别 Obsidian 标签和双向链接

### 7.3 建议方案
解析链路分三层：

1. 文件级解析
   - 读取文件名、路径、元数据
   - 提取 YAML frontmatter

2. Markdown 结构解析
   - 标题层级
   - 引用块
   - 列表项
   - 段落

3. 语义归一化
   - 将导出格式映射为统一 note_type
   - 清理多余符号、空白、重复摘录

### 7.4 容错策略
- 单个文件解析失败不影响整体任务
- 保留原始内容字段，便于人工回看
- 将异常文件记录到 import_jobs 错误明细中

## 8. AI 能力设计

### 8.1 笔记分类
将笔记归入如下类别：
- 观点
- 金句
- 方法论
- 案例
- 疑问
- 行动项
- 待复习

### 8.2 标签生成
根据内容自动生成 3 到 5 个标签，例如：
- 认知升级
- 时间管理
- 产品思维
- 心理学
- 写作表达

### 8.3 摘要生成
摘要分两层：
- 单条笔记摘要
- 单本书总结

### 8.4 主题聚合
利用向量相似度把跨书籍、跨时间的相似观点聚合成专题，例如：
- 延迟满足
- 刻意练习
- 系统思维

### 8.5 问答设计
采用 RAG 模式：
- Query 重写
- 召回 TopK 笔记
- 拼接引用上下文
- 生成答案
- 输出来源列表

### 8.6 复习卡片生成
从高价值笔记中生成问答对：
- Q: 这条笔记讲了什么核心观点？
- A: 总结后的关键内容

## 9. 后端接口设计

### 9.1 导入模块

#### `POST /api/import/jobs`
创建导入任务，支持上传单个文件或压缩包。

#### `GET /api/import/jobs`
获取导入任务列表。

#### `GET /api/import/jobs/:id`
获取导入任务详情与错误信息。

### 9.2 书籍模块

#### `GET /api/books`
分页获取书籍列表，支持按关键词和分类筛选。

#### `GET /api/books/:id`
获取书籍详情，包括统计信息。

#### `GET /api/books/:id/summary`
获取该书 AI 总结。

### 9.3 笔记模块

#### `GET /api/notes`
分页获取笔记列表，支持书籍、分类、标签、时间筛选。

#### `GET /api/notes/:id`
获取单条笔记详情。

#### `PATCH /api/notes/:id`
编辑笔记分类、标签、备注等信息。

#### `POST /api/notes/search`
全文检索和混合检索入口。

### 9.4 AI 模块

#### `POST /api/ai/notes/:id/analyze`
对单条笔记重新执行 AI 分析。

#### `POST /api/ai/books/:id/summarize`
对整本书重新生成摘要。

#### `POST /api/ai/topics/cluster`
手动触发主题聚类任务。

### 9.5 问答模块

#### `POST /api/qa/ask`
提交问题，返回回答、引用片段与书籍来源。

#### `GET /api/qa/history`
获取问答历史。

### 9.6 复习模块

#### `GET /api/review/today`
获取今日待复习卡片。

#### `POST /api/review/cards/:id/feedback`
提交掌握反馈，更新下次复习时间。

### 9.7 看板模块

#### `GET /api/dashboard/overview`
返回阅读总数、笔记总数、标签数、复习数等概览。

#### `GET /api/dashboard/trends`
返回阅读与笔记增长趋势。

## 10. 前端页面设计

### 10.1 页面结构

#### 1. 登录页
- 用户登录
- 快速体验入口

#### 2. 导入中心
- 上传区域
- 导入任务列表
- 失败明细弹窗

#### 3. 书籍库
- 书籍卡片列表
- 分类筛选
- 搜索框
- 阅读统计概览

#### 4. 笔记工作台
- 左侧筛选面板
- 中间笔记列表
- 右侧笔记详情和 AI 结果

#### 5. 问答中心
- 输入问题
- 流式输出回答
- 引用笔记卡片

#### 6. 复习中心
- 今日待复习
- 历史完成情况
- 复习热力图

#### 7. 数据看板
- 月度阅读趋势
- 书籍类别分布
- 高价值标签排行
- 最近活跃主题

### 10.2 前端目录建议

```text
src/
  api/
  assets/
  components/
  composables/
  layouts/
  router/
  stores/
  styles/
  utils/
  views/
    import/
    books/
    notes/
    qa/
    review/
    dashboard/
```

### 10.3 关键组件
- `ImportUploader`
- `ImportJobTable`
- `BookCard`
- `NoteFilterPanel`
- `NoteList`
- `NoteDetailDrawer`
- `AiSummaryPanel`
- `QaChatWindow`
- `ReferenceNoteList`
- `ReviewCardPanel`

## 11. 异步任务设计

### 11.1 Celery 任务列表
- `parse_markdown_file`
- `batch_import_notes`
- `analyze_note_ai`
- `summarize_book`
- `generate_note_embedding`
- `cluster_topics`
- `generate_review_card`

### 11.2 任务执行顺序
1. 创建导入任务
2. 批量解析文件
3. 写入 books / notes
4. 生成 embedding
5. 执行 AI 分类和摘要
6. 生成复习卡片
7. 更新任务状态

## 12. 检索方案设计

### 12.1 检索类型
- 关键词检索
- 标签检索
- 语义检索
- 混合检索

### 12.2 检索策略
- 先根据用户过滤条件限定书籍范围
- 全文检索召回候选
- 向量相似度召回补充
- 按关键词命中、相似度、重要度综合排序

### 12.3 引用溯源
问答必须返回：
- 对应书名
- 对应笔记内容片段
- 命中的标签或章节

## 13. 复习算法设计

### 13.1 MVP 策略
先不实现完整 Anki 算法，使用轻量版间隔复习：
- 第 1 次复习后：1 天
- 第 2 次复习后：3 天
- 第 3 次复习后：7 天
- 第 4 次复习后：14 天
- 后续根据反馈动态调整

### 13.2 反馈维度
- 不会
- 模糊记得
- 熟练掌握

### 13.3 更新规则
- 不会：间隔回退
- 模糊记得：小幅增加
- 熟练掌握：大幅增加

## 14. 安全与工程规范

### 14.1 基础安全
- JWT 鉴权
- 上传文件类型限制
- 文件大小限制
- 接口限流
- 输入内容清洗

### 14.2 工程规范
- 前端 ESLint + Prettier
- 后端 Black + isort + flake8
- 类型注释与接口文档同步维护

### 14.3 可观测性
- 导入任务日志
- Celery 任务状态跟踪
- 接口错误日志
- AI 调用耗时与失败率统计

## 15. 开发排期建议

### 第 1 周
- 完成项目初始化
- 完成数据库设计
- 完成 Markdown 导入和解析
- 完成书籍库与笔记列表基础页

### 第 2 周
- 接入 AI 摘要、标签、分类
- 完成问答接口与前端问答页
- 完成复习卡片生成与展示

### 第 3 周
- 完成数据看板
- 优化搜索体验和筛选能力
- 补充异常处理、日志和部署脚本

## 16. 简历包装建议

### 16.1 项目一句话描述
基于 Vue3、TypeScript、Element Plus 和 Flask 实现的 AI 阅读笔记整理平台，面向 Obsidian 读书笔记场景，支持 Markdown 导入、智能分类、摘要生成、语义检索问答与复习提醒。

### 16.2 可突出亮点
- 针对本地 Markdown 知识库设计结构化解析链路，完成非结构化笔记到可检索知识单元的转换
- 基于 Flask + Celery 构建异步 AI 处理流水线，实现大批量笔记的分类、摘要和向量化入库
- 使用 Vue3 + TypeScript + Element Plus 搭建知识工作台，支持检索筛选、卡片化展示与引用溯源问答
- 结合复习机制实现个人知识回顾闭环，增强读书笔记的长期使用价值

## 17. 后续扩展方向

- Obsidian 插件联动，支持本地一键同步
- 本地图谱视图
- 书籍主题演化分析
- 多轮问答与专题报告生成
- 生成周报、月报和年度阅读洞察
- 多端适配和 PWA 离线支持

## 18. 前端 UI / UX 设计方案

### 18.1 设计目标
前端界面不采用传统后台管理系统风格，而是围绕“阅读、整理、复盘”三个动作，设计为具有内容产品气质的知识工作台。

界面目标如下：
- 看起来像个人知识产品，而不是课程作业
- 兼顾高信息密度和较强的阅读沉浸感
- 支持长时间浏览笔记，不产生明显视觉疲劳
- AI 功能与阅读界面自然融合，不突兀

### 18.2 风格关键词
- 安静
- 克制
- 书卷感
- 层次清晰
- 卡片化
- 现代知识工具

### 18.3 视觉方向
建议采用“暖灰纸张底色 + 深色正文 + 墨绿点缀色”的方案，营造轻阅读产品感。

避免的方向：
- 纯后台风的蓝白表格界面
- 默认 Element Plus 组件直接堆叠
- 过度炫技的玻璃拟态、重阴影、花哨渐变

推荐方向：
- 大面积浅暖底色
- 局部深色文字形成阅读重心
- 点缀色只服务于状态、交互和重点信息
- 页面结构稳，留白足，组件统一

### 18.4 设计 Token 建议

#### 颜色
```css
:root {
  --bg-page: #f5f1e8;
  --bg-panel: #fbf8f2;
  --bg-card: #fffdf9;
  --bg-soft: #f0e9dc;

  --text-primary: #2f2a24;
  --text-secondary: #5f584f;
  --text-tertiary: #8a8278;

  --border-light: #e7dfd1;
  --border-medium: #d8cfbf;

  --brand-primary: #2f5d50;
  --brand-primary-light: #e1eee8;
  --brand-accent: #c08b5c;

  --success: #4c7a62;
  --warning: #b98239;
  --danger: #b85c4f;
  --info: #567189;
}
```

#### 阴影
```css
--shadow-sm: 0 2px 8px rgba(57, 45, 31, 0.06);
--shadow-md: 0 10px 30px rgba(57, 45, 31, 0.08);
--shadow-lg: 0 18px 40px rgba(57, 45, 31, 0.12);
```

#### 圆角
```css
--radius-xs: 8px;
--radius-sm: 12px;
--radius-md: 18px;
--radius-lg: 24px;
```

#### 间距
```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
```

### 18.5 字体建议
如果部署环境允许，可优先考虑如下字体组合：
- 中文正文：`Noto Serif SC` 或 `Source Han Serif SC`
- 中文 UI：`MiSans` 或 `Source Han Sans SC`
- 英文与数字：`IBM Plex Sans`

建议用法：
- 页面标题用无衬线，简洁现代
- 书籍标题和核心摘要可局部使用衬线，增加阅读感
- 正文笔记保持高可读性，行高适当放大

### 18.6 布局规范

#### 全局布局
- 顶部保留固定导航栏，高度 64px
- 左侧可折叠导航，宽度 220px
- 内容区域采用最大宽度限制，避免超宽阅读
- 主内容区优先采用双栏或三栏布局

#### 页面宽度建议
- 主工作区最大宽度：`1440px`
- 内容阅读区理想宽度：`720px - 860px`
- 侧边信息区宽度：`280px - 360px`

#### 栅格建议
- 首页和看板使用 12 栏栅格
- 工作台使用固定三栏布局
- 移动端降级为单栏抽屉式结构

### 18.7 Element Plus 定制建议
为了避免默认后台味道，建议统一覆盖以下组件样式：
- `el-button`
- `el-card`
- `el-input`
- `el-tag`
- `el-drawer`
- `el-tabs`
- `el-menu`
- `el-table`
- `el-empty`
- `el-skeleton`

具体原则：
- 按钮弱化默认实心蓝，主按钮改为品牌墨绿色
- 卡片增加柔和边框和浅阴影
- 输入框边框和背景变柔和
- 标签用低饱和填充色，不用高亮纯色
- 表格尽量少用；能卡片化就卡片化

### 18.8 动效策略
动效要轻，服务于内容理解，不喧宾夺主。

建议加入的动效：
- 页面进入时的轻微上浮淡入
- 卡片 hover 的阴影提升与边框变化
- AI 输出的流式打字效果
- 侧栏筛选切换时的过渡动画
- 抽屉展开收起动画

建议控制在：
- 过渡时长 `160ms - 240ms`
- 缓动函数优先 `ease-out`

### 18.9 页面原型设计

#### 1. 登录页
目标：简洁、安静、像内容产品的入口页。

布局建议：
- 左侧为项目介绍和一句价值主张
- 右侧为登录卡片
- 背景可加入轻微纸张纹理或淡渐变

页面内容：
- Logo / 项目名
- 一句标语：把碎片书摘变成可复用的知识资产
- 登录表单
- 快速体验入口

#### 2. 首页 / Dashboard
目标：让用户一进入系统就感受到这是“我的阅读空间”。

布局建议：
- 顶部 Hero 区
- 中部四个核心统计卡片
- 下方左右分栏

模块组成：
- 欢迎语 + 今日日期 + 待复习数量
- 统计卡片：书籍数、笔记数、主题数、今日复习数
- 最近导入的书
- 最近活跃标签
- 阅读趋势图
- 今日待复习入口

视觉重点：
- Hero 区用浅色渐变背景
- 统计卡片高度统一
- 图表颜色与主视觉一致

#### 3. 导入中心
目标：让用户清楚知道“导入什么、当前状态如何、哪里失败了”。

布局建议：
- 顶部上传区域
- 下方导入任务列表
- 右侧或弹窗展示失败明细

模块组成：
- 拖拽上传区
- 支持类型说明
- 导入进度条
- 历史任务时间线
- 失败文件提示和重试入口

交互重点：
- 文件拖拽高亮态
- 上传后立刻展示任务状态
- 不同状态使用统一色彩系统

#### 4. 书籍库
目标：做出“个人阅读藏书架”的感觉。

布局建议：
- 顶部筛选栏
- 中间卡片墙
- 支持列表/卡片切换

卡片信息建议：
- 书名
- 作者
- 标签
- 笔记数量
- 最近整理时间
- AI 总结入口

交互重点：
- 鼠标悬停出现摘要预览或快捷操作
- 支持按分类、标签、时间过滤

#### 5. 笔记工作台
这是项目最核心、最值得打磨的页面。

推荐采用三栏布局：
- 左栏：筛选与导航
- 中栏：笔记流
- 右栏：AI 整理结果和关联信息

左栏内容：
- 当前书籍信息
- 分类筛选
- 标签筛选
- 时间范围筛选

中栏内容：
- 笔记搜索框
- 笔记卡片列表
- 支持无限滚动

右栏内容：
- 当前选中笔记详情
- AI 摘要
- 自动标签
- 相似笔记
- 引用来源

单条笔记卡片建议包含：
- 章节名
- 摘录正文
- 用户批注
- 标签
- 重要度
- 创建时间

视觉重点：
- 中栏卡片是主角，阅读体验要最好
- 右栏 AI 内容要与原笔记有强关联，不要像独立聊天区

#### 6. 智能问答页
目标：强调“基于个人阅读知识库”的问答能力，而不是泛聊天。

推荐布局：
- 左侧主问答区
- 右侧来源引用区

左侧内容：
- 提问输入框
- 推荐问题快捷入口
- 流式回答内容

右侧内容：
- 命中的书籍列表
- 相关笔记片段
- 可点击回到原始笔记

推荐问题示例：
- 这本书里关于拖延症提到了什么
- 帮我总结最近三本书都提到的共性观点
- 我记录过哪些关于长期主义的内容

交互重点：
- 回答中对关键词高亮
- 引用卡片支持折叠与跳转
- 显示检索范围，例如“当前仅检索《认知觉醒》”

#### 7. 复习中心
目标：让系统形成长期价值，而不只是一次性整理。

布局建议：
- 顶部今日待复习概览
- 中部复习卡片区
- 底部历史统计

模块组成：
- 今日卡片数量
- 当前复习进度
- 复习卡片翻转区
- 掌握反馈按钮
- 最近复习趋势图

交互重点：
- 卡片切换自然流畅
- 反馈按钮明确但不过度干扰
- 支持“显示答案后评分”

#### 8. 数据看板
目标：给用户“我的阅读积累正在发生结构化增长”的感受。

模块建议：
- 月度阅读与笔记增长趋势
- 书籍类型分布
- 高频主题标签
- 高价值书籍排行
- 复习完成率趋势

视觉重点：
- 图表不要太满
- 每个图表旁边配一句解释性文案
- 保持整体和内容页同一视觉体系

### 18.10 移动端适配建议
MVP 不需要单独做移动端 App，但建议保留良好响应式。

适配原则：
- 左侧导航折叠为抽屉
- 三栏工作台在平板以下降为上下结构
- 问答页右侧引用面板改为底部抽屉
- 图表数量减少，优先保留关键指标

### 18.11 前端实现建议

#### 样式组织
建议建立独立主题文件：

```text
src/styles/
  index.scss
  theme.scss
  element-reset.scss
  variables.scss
```

#### 组件抽象建议
优先抽象以下基础能力：
- 页面容器 `PageShell`
- 统计卡片 `StatCard`
- 内容卡片 `ContentCard`
- 空状态 `EmptyState`
- 过滤栏 `FilterBar`
- 侧边信息面板 `InsightPanel`

#### 开发顺序建议
1. 先搭全局布局和主题变量
2. 再做首页和书籍库，统一卡片样式
3. 然后重点打磨笔记工作台
4. 最后做问答页和复习页的状态细节

### 18.12 页面最值得出效果的地方
如果你的时间有限，优先打磨下面三个视觉高地：
- 首页 Dashboard 的欢迎区和统计卡片
- 笔记工作台的三栏布局和笔记卡片
- 问答页的回答区和引用来源区

只要这三个页面有产品感，整个项目的观感就会被明显拉高。

### 18.13 组件级 UI 设计规范

#### 卡片系统
项目中的绝大多数信息都建议落在卡片上，但卡片要分层，不要全部长得一样。

建议至少区分三类卡片：

1. 数据卡片
   - 用于统计信息
   - 高度较低
   - 数字突出
   - 辅助说明弱化

2. 内容卡片
   - 用于书籍、笔记、引用片段
   - 更强调正文排版
   - 悬停态更明显

3. 洞察卡片
   - 用于 AI 摘要、主题归纳、复习建议
   - 可在头部加入轻色背景区分“系统产出”

推荐样式：
- 背景：`var(--bg-card)`
- 边框：`1px solid var(--border-light)`
- 圆角：`18px`
- 阴影：默认 `shadow-sm`，悬停 `shadow-md`
- 内边距：`20px - 24px`

#### 按钮系统
建议只保留三种主要按钮层级：

1. 主按钮
   - 品牌色填充
   - 用于上传、开始整理、提交问题、确认操作

2. 次按钮
   - 浅背景 + 品牌色文字
   - 用于过滤、切换视图、辅助行为

3. 文本按钮
   - 低视觉权重
   - 用于跳转详情、查看更多

避免：
- 同一页面出现过多主按钮
- 高频使用危险红色按钮
- 用默认蓝色造成视觉割裂

#### 输入框系统
输入框要偏柔和，适合长时间使用：
- 高度 40px 或 44px
- 背景使用 `var(--bg-panel)`
- 边框颜色低对比
- focus 时边框转品牌色，外圈弱高亮

搜索框建议：
- 左侧带搜索图标
- 支持清空按钮
- 支持输入后显示历史记录或推荐词

#### 标签系统
标签是这个项目的高频组件，建议做统一视觉层级。

标签类型：
- 业务标签：如“认知升级”“习惯养成”
- 系统标签：如“AI 生成”“高价值”
- 状态标签：如“待复习”“处理中”

样式建议：
- 使用浅底色 + 深文字
- 不使用高饱和纯色
- 圆角 999px
- 字号 12px 或 13px

#### 抽屉和面板
右侧详情面板和引用面板最好统一成同一种风格：
- 背景比主页面略浅
- 顶部固定标题区
- 内容区可滚动
- 关闭操作明显但不抢眼

#### 空状态
空状态不能像后台系统那样生硬。

建议文案方向：
- “还没有导入任何笔记，先把你的第一本书放进来。”
- “今天没有待复习内容，去看看最近整理过的主题。”

空状态组成：
- 简洁插画或抽象图形
- 一句解释
- 一个明确操作按钮

### 18.14 内容排版规范

#### 笔记正文
- 字号建议 `15px - 16px`
- 行高建议 `1.75 - 1.9`
- 段落间距 `10px - 14px`
- 行宽不要过长

#### 书名与章节
- 书名：`20px - 24px`，字重偏高
- 章节标题：`14px - 15px`，弱于正文标题但强于注释信息

#### 摘录与评论的区分
建议对摘录和评论做明显区分：
- 摘录内容：更像正文，可使用左边框或轻背景
- 评论内容：字体略小，颜色更柔和，强调“这是你的想法”

#### AI 产出内容
AI 产出的摘要、分类结果、主题洞察要有“系统视角”的感觉：
- 模块标题清晰
- 分段简洁
- 不要大段连续文本
- 可以使用编号或短句列表

### 18.15 图标与插画建议

图标建议：
- 使用线性图标体系
- 风格统一，不混搭
- 可选 `Lucide` 或 `IconPark`

插画建议：
- 不必使用重插画
- 可以用抽象书页、卡片、目录、引文形状做装饰
- 只在登录页、空状态、首页 Hero 区少量使用

### 18.16 低保真页面原型草案

以下是便于开发阶段理解结构的线框示意，重点是信息层次，不是最终视觉稿。

#### 1. 首页 Dashboard 线框

```text
+----------------------------------------------------------------------------------+
| Top Nav: Logo | Search | Import | User                                           |
+----------------------------------------------------------------------------------+
| Sidebar       |  Hero: 你好，Tao / 今日待复习 12 条 / 最近持续阅读 7 天             |
| - Dashboard   |------------------------------------------------------------------|
| - Import      |  [书籍数]    [笔记数]    [主题数]    [今日复习数]                  |
| - Books       |------------------------------------------------------------------|
| - Notes       |  最近导入的书                | 阅读趋势                           |
| - QA          |  [Book Card] [Book Card]     | [Line Chart]                       |
| - Review      |  [Book Card] [Book Card]     |                                    |
|               |------------------------------------------------------------------|
|               |  活跃标签                    | 今日待复习                         |
|               |  [Tag Cloud / Topic Cards]   | [Review Card Preview List]         |
+----------------------------------------------------------------------------------+
```

#### 2. 导入中心线框

```text
+----------------------------------------------------------------------------------+
| Header: 导入中心                                                                  |
+----------------------------------------------------------------------------------+
| [ Drag & Drop Upload Area                            ] [导入说明 / 支持格式]      |
| [ 点击上传 / 支持 markdown zip 文件                  ] [Obsidian 目录建议]         |
+----------------------------------------------------------------------------------+
| 导入任务列表                                                                      |
|----------------------------------------------------------------------------------|
| 文件名            状态            进度            成功/失败         操作           |
| notes-1.zip       processing      68%             120 / 3          查看详情        |
| book-a.md         success         100%            32 / 0           查看结果        |
| broken.md         failed          -               0 / 1            查看错误        |
+----------------------------------------------------------------------------------+
| Detail Drawer: 错误日志 / 失败文件 / 重试                                         |
+----------------------------------------------------------------------------------+
```

#### 3. 书籍库线框

```text
+----------------------------------------------------------------------------------+
| Header: 我的书库                  [Search] [Category] [Tag] [Card/List Toggle]    |
+----------------------------------------------------------------------------------+
| [Book Cover] 书名               [Book Cover] 书名               [Book Cover] 书名 |
| 作者 / 笔记数 / 最近整理         作者 / 笔记数 / 最近整理         作者 / 笔记数     |
| 标签 标签 标签                  标签 标签                     标签 标签            |
| [查看摘要] [进入笔记]            [查看摘要] [进入笔记]            [查看摘要]        |
|----------------------------------------------------------------------------------|
| [Book Cover] ...                                                              ... |
+----------------------------------------------------------------------------------+
```

#### 4. 笔记工作台线框

```text
+------------------------------------------------------------------------------------------------+
| Top Filter Bar: 当前书籍 / 搜索 / 分类 / 标签 / 时间范围 / 排序                               |
+------------------------------------------------------------------------------------------------+
| Left Panel                    | Center Notes List                         | Right Insight Panel |
|------------------------------|-------------------------------------------|---------------------|
| 书籍信息                      | [Note Card] 章节                          | 当前笔记详情         |
| 分类筛选                      | 摘录正文两到四行...                        | 原文 / 评论          |
| 标签筛选                      | 评论摘要一行...                            |---------------------|
| 时间筛选                      | 标签 标签 重要度 时间                      | AI 摘要              |
|------------------------------|-------------------------------------------| 主题标签             |
| 快速入口                      | [Note Card] 章节                          | 相似笔记             |
| - 高价值内容                  | 摘录正文...                                | 关联书籍             |
| - 待复习                      | 评论...                                    | 来源信息             |
| - 最近新增                    |                                           |                     |
+------------------------------------------------------------------------------------------------+
```

#### 5. 智能问答页线框

```text
+-----------------------------------------------------------------------------------------------+
| Header: 基于你的阅读笔记提问                [检索范围: 全部书籍 / 当前书籍]                    |
+-----------------------------------------------------------------------------------------------+
| Left Main Area                                              | Right References                |
|------------------------------------------------------------|---------------------------------|
| 推荐问题 chips                                              | 命中来源                         |
| [这本书里关于长期主义提到了什么]                             | [引用卡片 1]                     |
| [帮我总结最近三本书共同观点]                                 | 书名 / 章节 / 片段               |
|------------------------------------------------------------|---------------------------------|
| User Question Bubble                                        | [引用卡片 2]                     |
| Assistant Answer                                            | 书名 / 章节 / 片段               |
| - 分点回答                                                  |---------------------------------|
| - 关键内容高亮                                              | 相关书籍                         |
| - 可展开查看更多                                             | [Book A] [Book B] [Book C]       |
|------------------------------------------------------------|---------------------------------|
| Input Box: 输入你的问题...                  [发送]           |                                 |
+-----------------------------------------------------------------------------------------------+
```

#### 6. 复习中心线框

```text
+----------------------------------------------------------------------------------+
| Header: 今日复习                    已完成 8 / 12                               |
+----------------------------------------------------------------------------------+
| Summary Row: [待复习数] [连续复习天数] [掌握率] [下次高峰]                        |
+----------------------------------------------------------------------------------+
|                              Review Card                                         |
|----------------------------------------------------------------------------------|
| 问题：这条笔记的核心观点是什么？                                                   |
| 来源：认知觉醒 / 第三章                                                            |
|----------------------------------------------------------------------------------|
| [显示答案]                                                                        |
|----------------------------------------------------------------------------------|
| 回答区域展开后：                                                                   |
| 关键答案内容...                                                                    |
|----------------------------------------------------------------------------------|
| [不会]                      [模糊记得]                      [熟练掌握]             |
+----------------------------------------------------------------------------------+
| Bottom: 最近复习趋势图 / 历史记录                                                  |
+----------------------------------------------------------------------------------+
```

### 18.17 页面状态设计

每个核心页面都建议完整覆盖以下状态：
- 初始空状态
- 加载中状态
- 加载成功状态
- 局部失败状态
- 完全失败状态

例如笔记工作台：
- 还没导入书籍时，展示引导空状态
- 正在拉取笔记时，列表区显示骨架屏
- AI 摘要加载失败时，只影响右栏模块，不阻塞笔记浏览

这会让页面更像真实产品，而不是 demo。

### 18.18 微交互建议

适合做且性价比高的微交互：
- 书籍卡片 hover 时封面轻微上浮
- 点击笔记卡片时右栏平滑切换详情
- 问答回答生成时逐段流式出现
- 标签筛选选中后有柔和背景过渡
- 复习卡片翻面时有轻微 3D 效果

不建议做的交互：
- 大面积视差滚动
- 过多悬浮特效
- 长时间复杂动画

### 18.19 页面文案风格建议

文案整体应偏“陪伴型知识工具”，不要过度技术化。

建议风格：
- “今天还有 12 条值得回看”
- “这些内容也许可以归到同一个主题下”
- “从你最近的笔记里，系统找到 6 条相关记录”

避免风格：
- “操作成功”
- “请求失败”
- “暂无数据”

这些文案当然还会存在，但建议做适度润色，让产品更有人味。

### 18.20 开发与设计协同建议

如果你自己一边设计一边开发，建议按这个顺序推进：

1. 先确定全局主题色、字体、卡片样式
2. 先做 Dashboard 和书籍库，建立视觉语言
3. 再做最核心的笔记工作台
4. 最后做问答页和复习页的交互细节

实现时优先沉淀：
- 一套 CSS 变量
- 一套统一卡片组件
- 一套统一状态组件
- 一套统一筛选栏组件

这样后面页面越做越统一，不容易散。

## 19. 前端工程结构与组件拆分方案

### 19.1 前端总体目标
前端部分不仅要完成页面展示，还要体现较好的工程组织能力，因此建议从一开始就把以下几件事分清楚：
- 页面负责布局和页面级交互
- 组件负责复用和局部交互
- Store 负责共享状态
- API 层负责请求封装
- 类型定义独立维护

避免出现的问题：
- 页面里直接堆所有接口请求和数据处理
- 一个组件同时负责展示、请求、状态管理和业务逻辑
- 类型和接口字段散落在多个文件里

### 19.2 推荐目录结构

```text
src/
  api/
    client.ts
    modules/
      auth.ts
      import.ts
      books.ts
      notes.ts
      qa.ts
      review.ts
      dashboard.ts

  assets/
    images/
    icons/

  components/
    base/
      AppCard.vue
      AppSection.vue
      AppEmpty.vue
      AppStatusBadge.vue
      AppSearchInput.vue
      AppFilterBar.vue
      AppPanel.vue
      AppMetricCard.vue

    common/
      PageHeader.vue
      SidebarNav.vue
      TopNavBar.vue
      LoadingSkeleton.vue
      ConfirmDialog.vue

    import/
      ImportUploader.vue
      ImportJobList.vue
      ImportJobRow.vue
      ImportErrorDrawer.vue

    books/
      BookCard.vue
      BookGrid.vue
      BookListItem.vue
      BookSummaryDrawer.vue
      BookFilterBar.vue

    notes/
      NoteFilterPanel.vue
      NoteToolbar.vue
      NoteList.vue
      NoteCard.vue
      NoteDetailPanel.vue
      NoteAISummary.vue
      RelatedNotesPanel.vue
      TagGroup.vue

    qa/
      QaInputBox.vue
      QaMessageList.vue
      QaMessageBubble.vue
      QaSuggestionChips.vue
      ReferenceList.vue
      ReferenceCard.vue

    review/
      ReviewSummaryBar.vue
      ReviewCard.vue
      ReviewFeedbackBar.vue
      ReviewTrendChart.vue

    dashboard/
      DashboardHero.vue
      DashboardStats.vue
      RecentBooksPanel.vue
      ActiveTopicsPanel.vue
      ReviewPreviewPanel.vue
      ReadingTrendChart.vue

  composables/
    usePagination.ts
    useQueryFilters.ts
    useDebouncedSearch.ts
    useAsyncTask.ts
    useQaSession.ts
    useReviewActions.ts

  constants/
    colors.ts
    enums.ts
    routes.ts

  layouts/
    MainLayout.vue
    AuthLayout.vue

  router/
    index.ts
    guards.ts

  stores/
    auth.ts
    app.ts
    import.ts
    books.ts
    notes.ts
    qa.ts
    review.ts
    dashboard.ts

  styles/
    index.scss
    theme.scss
    variables.scss
    element-reset.scss
    animation.scss

  types/
    auth.ts
    import.ts
    book.ts
    note.ts
    qa.ts
    review.ts
    dashboard.ts
    common.ts

  utils/
    date.ts
    format.ts
    storage.ts
    markdown.ts
    request.ts

  views/
    auth/
      LoginView.vue

    dashboard/
      DashboardView.vue

    import/
      ImportCenterView.vue

    books/
      BookLibraryView.vue
      BookDetailView.vue

    notes/
      NoteWorkbenchView.vue

    qa/
      QaCenterView.vue

    review/
      ReviewCenterView.vue

  App.vue
  main.ts
```

### 19.3 分层职责说明

#### `views/`
只做页面级事情：
- 页面布局组织
- 调用 store/composable
- 拼装多个业务组件
- 控制页面级弹窗、抽屉、路由切换

不建议在 `views/` 里写：
- 大量重复 UI 结构
- 复杂接口细节
- 可复用业务组件逻辑

#### `components/base/`
沉淀项目基础视觉语言。

比如：
- `AppCard` 统一卡片边框、圆角、阴影
- `AppSection` 统一模块标题和右侧操作区
- `AppEmpty` 统一空状态
- `AppStatusBadge` 统一状态标签

这层非常重要，它决定你页面是不是统一。

#### `components/<feature>/`
放与业务域强相关的组件，例如书籍、笔记、问答、复习模块。

原则：
- 一个组件专注一个局部职责
- 尽量围绕“视觉块”拆分，而不是围绕 HTML 标签拆分

#### `stores/`
负责跨组件共享的业务状态，例如：
- 当前用户
- 当前书籍筛选条件
- 当前选中的笔记
- 当前问答会话
- 导入任务列表

#### `composables/`
负责复用逻辑，而不是状态中心。

适合放：
- 搜索防抖
- 分页逻辑
- 筛选参数同步
- 异步 loading/error/success 控制

#### `api/modules/`
每个业务域一个 API 文件，不要把所有接口写进一个大文件。

### 19.4 路由设计建议

推荐路由结构：

```text
/
  /login
  /dashboard
  /import
  /books
  /books/:id
  /notes
  /qa
  /review
```

说明：
- `/books/:id` 用于单本书概览
- `/notes` 是主工作台，可通过 query 参数带入书籍、标签、分类
- `/qa` 支持 query 参数指定检索范围，例如 `bookId`

### 19.5 Store 设计建议

#### `auth.ts`
负责：
- 登录状态
- 用户信息
- token 管理

#### `books.ts`
负责：
- 书籍列表
- 当前筛选条件
- 当前选中书籍
- 单本书摘要

#### `notes.ts`
负责：
- 笔记列表
- 当前笔记详情
- 分类/标签筛选
- 搜索关键词
- 右侧详情面板状态

#### `qa.ts`
负责：
- 当前问答会话消息
- 当前问题 loading 状态
- 当前引用列表
- 检索范围

#### `review.ts`
负责：
- 今日复习卡片
- 当前卡片索引
- 用户反馈提交状态

#### `dashboard.ts`
负责：
- 首页统计
- 趋势图数据
- 最近书籍
- 活跃主题

### 19.6 API 组织建议

每个模块只暴露清晰函数，不把请求逻辑散到组件里。

示例：

```ts
// api/modules/books.ts
export function fetchBookList(params: BookListParams) {}
export function fetchBookDetail(id: number) {}
export function fetchBookSummary(id: number) {}
```

```ts
// api/modules/notes.ts
export function fetchNoteList(params: NoteListParams) {}
export function fetchNoteDetail(id: number) {}
export function updateNote(id: number, payload: UpdateNotePayload) {}
```

推荐统一封装：
- 请求拦截器
- token 注入
- 统一错误提示
- 通用分页响应类型

### 19.7 类型设计建议

建议类型独立维护，避免接口字段写成 `any`。

例如：

```ts
export interface BookItem {
  id: number
  title: string
  author?: string
  noteCount: number
  updatedAt: string
  tags: string[]
}
```

```ts
export interface NoteItem {
  id: number
  bookId: number
  chapter?: string
  rawContent: string
  cleanedContent: string
  aiSummary?: string
  aiCategory?: string
  importanceScore?: number
  tags: string[]
  createdAt: string
}
```

### 19.8 页面级组件拆分建议

#### 1. `DashboardView.vue`
职责：
- 获取首页概览数据
- 组合 Hero、统计卡片、趋势图、最近书籍等模块

建议拆分为：
- `DashboardHero`
- `DashboardStats`
- `RecentBooksPanel`
- `ActiveTopicsPanel`
- `ReadingTrendChart`
- `ReviewPreviewPanel`

#### 2. `ImportCenterView.vue`
职责：
- 文件上传
- 任务状态展示
- 错误详情查看

建议拆分为：
- `ImportUploader`
- `ImportJobList`
- `ImportErrorDrawer`

#### 3. `BookLibraryView.vue`
职责：
- 展示书籍列表
- 筛选和搜索
- 打开书籍摘要

建议拆分为：
- `BookFilterBar`
- `BookGrid`
- `BookCard`
- `BookSummaryDrawer`

#### 4. `NoteWorkbenchView.vue`
这是最核心页面，建议重点拆细。

页面结构：
- 顶部工具栏
- 左侧筛选栏
- 中间笔记列表
- 右侧洞察面板

建议拆分为：
- `NoteToolbar`
- `NoteFilterPanel`
- `NoteList`
- `NoteCard`
- `NoteDetailPanel`
- `NoteAISummary`
- `RelatedNotesPanel`

#### 5. `QaCenterView.vue`
职责：
- 输入问题
- 展示回答
- 展示引用来源

建议拆分为：
- `QaSuggestionChips`
- `QaMessageList`
- `QaMessageBubble`
- `QaInputBox`
- `ReferenceList`
- `ReferenceCard`

#### 6. `ReviewCenterView.vue`
职责：
- 展示今日复习
- 提交掌握反馈
- 展示复习趋势

建议拆分为：
- `ReviewSummaryBar`
- `ReviewCard`
- `ReviewFeedbackBar`
- `ReviewTrendChart`

### 19.9 基础通用组件优先级

如果你时间有限，建议最先抽出这些基础组件：
- `AppCard`
- `AppSection`
- `AppEmpty`
- `AppStatusBadge`
- `AppSearchInput`
- `AppFilterBar`
- `AppPanel`

这几个组件会在几乎所有页面复用，先做好它们，后面效率会高很多。

### 19.10 组件通信建议

推荐优先级：
1. 父子组件 `props + emits`
2. 跨多个页面或多个组件共享时用 `Pinia`
3. 纯逻辑复用用 `composables`

避免：
- 用全局事件总线处理主要业务逻辑
- 一个 store 塞进整个应用所有状态

### 19.11 页面开发顺序建议

建议按“从外到内、从静态到交互”的顺序开发：

1. `MainLayout + SidebarNav + TopNavBar`
2. `AppCard/AppSection/AppEmpty/AppSearchInput` 等基础组件
3. `DashboardView`
4. `BookLibraryView`
5. `NoteWorkbenchView`
6. `QaCenterView`
7. `ImportCenterView`
8. `ReviewCenterView`

原因：
- 先统一骨架和视觉
- 先做静态内容更多的页面建立风格
- 再攻克最复杂的工作台和问答页

### 19.12 Notes 工作台重点实现建议

这个页面建议你投入最多时间，因为它最能体现前端能力。

重点体现：
- 三栏布局组织能力
- 筛选条件与列表状态联动
- 笔记切换时右栏内容平滑更新
- 较长内容的可读性和信息层级
- loading、empty、error 三类局部状态处理

推荐状态流：
- 左侧切换筛选条件
- 触发 notes store 更新 query
- 自动重新拉取列表
- 点击某条笔记后更新当前 note id
- 右栏根据当前 note id 拉取详情和 AI 结果

### 19.13 QA 页重点实现建议

这个页面的关键不在聊天框，而在“回答 + 引用”的双区联动。

需要重点做好：
- 输入状态管理
- 回答生成过程 loading/streaming 展示
- 回答与引用来源同步更新
- 支持切换检索范围

如果第一版不做真正流式，也可以先模拟分段输出，只要交互上看起来自然即可。

### 19.14 样式实现建议

建议采用：
- `SCSS + CSS Variables`
- 每个业务组件局部样式
- 主题变量集中在 `variables.scss`

推荐原则：
- 颜色、圆角、阴影只从变量取
- 不在各组件里写散落的硬编码颜色
- Element Plus 主题覆盖集中到一个文件

### 19.15 前端可讲的工程亮点

这套拆分方式本身就可以成为你的面试亮点，你可以讲：
- 按业务域拆分 API、store 和组件，保证结构清晰
- 通过基础组件沉淀统一视觉语言，减少页面重复实现
- 对高复杂页面采用三栏工作台结构，兼顾信息密度和可读性
- 将页面状态、异步任务状态、问答引用联动拆成独立模块，降低耦合

## 20. 结论

这个项目的优势在于：
- 问题真实，需求明确
- 前端展示空间大
- AI 结合自然
- 后端复杂度可控
- 很适合校招面试讲“为什么做、怎么做、做出了什么价值”

对你来说，最重要的不是把功能做得特别多，而是先把“导入 -> 整理 -> 检索 -> 复习”这条主链路做完整。只要这条主链路能跑通，这个项目就已经足够成为一段很强的校招项目经历。
