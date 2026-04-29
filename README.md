# ReadMind

面向 `Obsidian + 微信读书` 工作流的 AI 阅读笔记整理、问答、洞察与复习系统。
An AI-powered reading knowledge workspace for `Obsidian + WeRead` notes, with note organization, grounded QA, insight generation, knowledge graphs, analytics, and spaced review.

ReadMind 试图解决一个很常见的问题：读了很多书、划了很多线、写了很多摘录，但后续很少再系统整理，也很难把过去的笔记重新用起来。这个项目把本地 Markdown 阅读笔记接入进来，通过结构化解析、混合检索、AI 总结、可溯源问答、主题图谱、数据看板和复习机制，把分散书摘变成一个可以持续回看的个人知识工作台。

ReadMind solves a familiar problem for heavy readers: you highlight, export, and collect a lot of notes, but those notes rarely become reusable knowledge. It connects local Markdown reading notes, parses them into structured data, and turns scattered excerpts into a searchable, reviewable, and AI-assisted personal knowledge system.

## 在线体验 / Live Demo

[打开 ReadMind 演示站 / Open the ReadMind demo](http://43.139.112.45:3000)

演示站使用静态演示缓存，不会读取或上传你的真实 Obsidian 数据，但可以体验书库、笔记工作台、签签问答、AI 洞察、知识图谱、复习中心和数据看板。
The demo uses built-in static sample data. It does not read or upload your real Obsidian vault, but it lets you try the library, note workspace, Qianqian AI chat, insight generation, knowledge graph, review center, and analytics dashboard.

## 核心能力 / Features

- 本地 `Obsidian` 读书笔记同步与微信读书 Markdown 解析
- Local `Obsidian` reading-note sync and WeRead Markdown parsing
- 书库、书籍详情、笔记工作台、智能问答、复习中心、知识图谱、数据看板
- Library, book details, note workspace, AI chat, review center, knowledge graph, and analytics dashboard
- 基于个人阅读笔记的 AI 摘要、AI 洞察、流式问答与引用来源回溯
- AI summaries, insight cards, streaming QA, and traceable references based on your own notes
- 支持单本书问答、全库问答、搜索高亮、主题筛选、章节筛选和跳转原笔记
- Supports single-book QA, whole-library QA, highlighted search, topic/chapter filters, and source-note navigation
- 支持阅读偏好、阅读时长排行、主题雷达图、阅读热力图、高价值书籍矩阵等数据洞察
- Analytics for reading preferences, reading-time ranking, topic radar, activity heatmap, and high-value book matrix
- 支持复习目标、自定义每日卡片数、到期/薄弱/新卡片队列和评分反馈
- Review goals, custom daily card count, due/weak/new queues, and rating feedback
- 支持异步任务体系：书籍摘要、AI 洞察、图谱分析、书库同步、任务轮询和失败重试
- Async task center for summaries, insights, graph analysis, vault sync, polling, and failed-task retry
- 内置小书签精灵“签签”，在导入、问答、洞察、复习等关键节点提供温柔反馈
- Built-in bookmark fairy mascot “Qianqian”, offering warm feedback during import, QA, insights, and review

## 技术栈 / Tech Stack

- 前端 / Frontend: `Vue 3` + `TypeScript` + `Vite` + `Element Plus` + `Pinia` + `Vue Router` + `ECharts`
- 后端 / Backend: `Flask` + `Python`
- AI: `DeepSeek`
- 检索与缓存 / Retrieval and cache: `SQLite` + local embedding cache
- 数据来源 / Data source: WeRead Markdown notes stored in a local `Obsidian Vault`

## 运行模式 / Run Modes

- 本地真实模式：读取 `.env` 中配置的 `VAULT_ROOT`，并在需要时调用 `DeepSeek`
- Local real-data mode: reads `VAULT_ROOT` from `.env` and calls `DeepSeek` when AI features are triggered
- 公开演示模式：设置 `DEMO_DATA_ONLY=1`，使用预置缓存数据，不读取真实 Vault，也不调用外部模型
- Public backend demo mode: set `DEMO_DATA_ONLY=1` to use bundled demo data without reading a real vault or calling external models
- 前端静态演示模式：设置 `VITE_STATIC_DEMO=1` 构建纯前端演示站
- Static frontend demo mode: build with `VITE_STATIC_DEMO=1` to run a frontend-only demo with cached sample data

## 界面预览 / Screenshots

### 首页总览 / Dashboard

![ReadMind Dashboard](docs/screenshots/dashboard.png)

首页展示今日阅读回顾、行动队列、阅读指标、最近整理书籍和签签的温柔提醒。
The dashboard shows today’s reading brief, action queue, metrics, recent books, and Qianqian’s gentle prompts.

### 数据看板 / Analytics

![ReadMind Analytics](docs/screenshots/analytics.png)

数据看板展示阅读时长排行、偏好主题、长期阅读节奏、阅读热力图和高价值书籍矩阵。
The analytics view visualizes reading-time ranking, topic preference, long-term rhythm, activity heatmap, and high-value book matrix.

### 书库与封面视图 / Library

![ReadMind Books](docs/screenshots/books.png)

书库页展示书籍封面、作者、分类、标签和笔记规模，支持按关键词和分类快速浏览。
The library displays covers, authors, categories, tags, and note counts, with keyword and category browsing.

### 书籍详情与 AI 摘要 / Book Detail and AI Summary

![ReadMind Book Detail](docs/screenshots/book-detail.png)

书籍详情页展示封面、元信息、AI 总结、章节笔记、高频主题和摘要生成状态。
The book detail page combines metadata, AI summary, chapter notes, frequent topics, and summary-generation status.

### 笔记工作台 / Note Workspace

![ReadMind Notes](docs/screenshots/notes.png)

笔记工作台支持按书籍、标签、章节、分类、关键词和排序浏览笔记，并生成当前筛选范围的 AI 洞察。
The note workspace supports filtering by book, tag, chapter, category, keyword, and sort order, then generates scoped AI insights.

### 智能问答 / AI Chat

![ReadMind QA](docs/screenshots/qa.png)

智能问答由“签签”作为回答人格，支持单本书/全库问答、连续追问、检索状态提示、结构化回答和引用来源联动。
AI chat is answered by Qianqian, supporting single-book or whole-library QA, follow-up questions, retrieval status, structured answers, and references.

### 复习中心 / Review Center

![ReadMind Review](docs/screenshots/review.png)

复习中心支持每日目标、自定义卡片数、到期/薄弱/新卡片队列、评分反馈、复习完成反馈和跳转原笔记。
The review center supports daily goals, custom card count, due/weak/new queues, rating feedback, completion feedback, and source-note navigation.

### 知识图谱 / Knowledge Graph

![ReadMind Graph](docs/screenshots/graph.png)

知识图谱支持领域聚类和知识主题两种视角，展示主题簇、主题关系图、关联书籍和代表性摘录。
The knowledge graph supports domain-cluster and topic views, showing topic clusters, relationships, related books, and representative excerpts.

### 导入中心 / Import Center

![ReadMind Import](docs/screenshots/import.png)

导入中心负责同步本地 Obsidian 阅读目录，并展示同步状态、目录检测、演示模式提示和下一步行动建议。
The import center syncs the local Obsidian reading directory and shows sync status, vault checks, demo-mode hints, and next actions.

### 任务中心 / Task Center

![ReadMind Jobs](docs/screenshots/jobs.png)

任务中心统一展示书籍摘要、AI 洞察、本地同步、图谱分析等后台任务，支持状态筛选、类型筛选、进度查看和失败重试。
The task center lists background jobs for summaries, insights, sync, and graph analysis, with filters, progress, and retry support.

## 快速启动 / Quick Start

### 1. 启动后端 / Start Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

默认地址 / Default URL:

- `http://127.0.0.1:5000`

### 2. 启动前端 / Start Frontend

```bash
cd frontend
npm install
npm run dev
```

默认地址 / Default URL:

- `http://127.0.0.1:5173`
- 如果 `5173` 被占用，Vite 会自动切到 `5174` 或下一个可用端口
- If `5173` is occupied, Vite will automatically use `5174` or the next available port

## 首次启动检查清单 / First-Run Checklist

1. `Node.js` 版本满足当前 Vite 需求，`npm run dev` 能正常启动 / Your `Node.js` version satisfies the current Vite requirement, and `npm run dev` works
2. `Python 3`、虚拟环境和 `pip install -r requirements.txt` 已完成 / `Python 3`, virtual environment, and `pip install -r requirements.txt` are ready
3. `backend/.env` 已配置，尤其是 `VAULT_ROOT` 和 `DEEPSEEK_API_KEY` / `backend/.env` is configured, especially `VAULT_ROOT` and `DEEPSEEK_API_KEY`
4. `VAULT_ROOT` 指向你自己的 Obsidian 阅读目录，而不是作者机器上的示例路径 / `VAULT_ROOT` points to your own Obsidian reading-note directory, not the author’s local path
5. 先启动后端，再启动前端；前端开发环境会把 `/api` 代理到 Flask / Start the backend before the frontend; the frontend dev server proxies `/api` to Flask
6. 如果你只是想体验界面，可以将 `DEMO_DATA_ONLY=1` 写入 `.env`，使用演示数据模式启动 / If you only want to try the UI, set `DEMO_DATA_ONLY=1` in `.env` to use demo data

## 环境变量 / Environment Variables

后端 `.env` 参考 / Backend `.env` example:

```env
SECRET_KEY=readmind-dev-secret
DEEPSEEK_API_KEY=replace_with_your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
VAULT_ROOT=/path/to/your/Obsidian/Vault/reading-notes
DEMO_DATA_ONLY=0
```

公开演示站如果不连接后端 API，可以使用前端静态演示构建。
To run a frontend-only public demo without a backend API, build with static demo mode:

```bash
cd frontend
VITE_STATIC_DEMO=1 npm run build
npm run preview -- --host 0.0.0.0 --port 3000
```

这个模式会在浏览器内使用 `frontend/src/mock/staticDemo.ts` 的缓存数据，展示书库、笔记、签签问答、AI 洞察、知识图谱、复习中心和数据看板，不会读取真实 Vault，也不会调用外部模型。
This mode serves cached demo data from `frontend/src/mock/staticDemo.ts` in the browser. It does not read a real vault or call external models.

## 目录结构 / Project Structure

```text
readmind/
├── frontend/                # Vue3 frontend
│   ├── src/
│   │   ├── api/             # API request layer
│   │   ├── assets/          # Mascot illustrations and static assets
│   │   ├── components/      # Shared, QA, note, and graph components
│   │   ├── composables/     # Reusable composition logic such as polling
│   │   ├── config/          # Frontend runtime/build flags
│   │   ├── constants/       # Routes, QA presets, mascot messages
│   │   ├── layouts/         # Main and auth layouts
│   │   ├── mock/            # Static demo data
│   │   ├── router/          # Route configuration
│   │   ├── stores/          # Pinia stores
│   │   ├── styles/          # Theme, animations, variables
│   │   ├── types/           # TypeScript types
│   │   └── views/           # Page views
│   └── package.json
├── backend/                 # Flask backend
│   ├── app/
│   │   ├── routes/          # dashboard / analytics / books / notes / qa / review / jobs ...
│   │   ├── services/        # Parsing, retrieval, graph, async jobs, LLM, review services
│   │   ├── config.py
│   │   └── __init__.py
│   ├── tests/               # Backend tests
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
├── docs/                    # API docs, learning path, screenshots
├── private/                 # Private planning/review docs; avoid publishing sensitive content
└── DEMO_SITE_GUIDE.md       # Demo-site guide
```

## 当前已完成模块 / Completed Modules

- 真实 Obsidian 书库接入与本地同步
- Real Obsidian library integration and local sync
- 书库页、书籍详情页、首页书架与行动队列
- Library, book detail page, dashboard shelf, and action queue
- 数据看板：阅读排行、偏好主题、热力图、雷达图、高价值书籍矩阵
- Analytics: reading ranking, topic preferences, heatmap, radar chart, and high-value book matrix
- 笔记工作台：按书籍 / 标签 / 章节 / 分类 / 关键词检索
- Note workspace: search by book, tag, chapter, category, and keyword
- AI 洞察：基于当前筛选范围生成结构化总结、复习问题和引用依据
- AI insights: structured summaries, review questions, and references based on current filters
- 智能问答：连续对话、流式输出、书籍范围限制、引用跳转
- AI chat: multi-turn conversation, streaming output, book scope, and reference navigation
- 复习中心：卡片复习、评分反馈、队列筛选、自定义目标、服务端持久化进度
- Review center: card review, rating feedback, queue filters, custom goals, and persisted progress
- 主题图谱：领域聚类、知识主题、主题关系图、关联书籍与摘录
- Knowledge graph: domain clusters, knowledge topics, relationships, related books, and excerpts
- 异步任务中心：任务列表、状态筛选、失败任务重试
- Async task center: job list, status filters, and failed-task retry
- LLM / embedding 状态检测与自动 embedding 预热
- LLM / embedding health checks and automatic embedding warmup
- 小书签精灵“签签”：正式插画、状态动画、统一文案系统和关键节点反馈
- “Qianqian” mascot: formal illustrations, state animations, unified copy system, and key-moment feedback

## 隐私与数据边界 / Privacy and Data Boundaries

- 本地真实模式下，系统会读取 `VAULT_ROOT` 指向的 Markdown 笔记目录
- In local real-data mode, the system reads Markdown notes from `VAULT_ROOT`
- 书库、笔记、图谱、复习等基础能力主要依赖本地缓存数据库
- Library, notes, graph, and review features mainly rely on a local cache database
- 当你主动触发摘要、AI 洞察或智能问答时，系统只会将当前命中的摘录片段发送给 `DeepSeek`
- When you trigger summaries, AI insights, or QA, only the matched excerpts are sent to `DeepSeek`
- 如果你不希望任何内容离开本机，可以启用 `DEMO_DATA_ONLY=1` 或关闭模型调用链路
- If you do not want any content to leave your machine, use `DEMO_DATA_ONLY=1` or disable model calls

## 当前能力边界 / Current Limitations

- 真实模式下，导入中心以“同步本地 Obsidian 目录”为主；直接上传 Markdown/zip 仍是演示模式交互
- In real mode, import focuses on syncing a local Obsidian directory; direct Markdown/zip upload is still a demo interaction
- 异步任务使用本地线程池和 SQLite 记录状态，适合个人本地运行；如果要做多人生产服务，建议替换为 Celery/RQ 等队列
- Async jobs use a local thread pool and SQLite, suitable for personal local use; for multi-user production, replace it with Celery/RQ or another queue
- 复习中心已经具备基础队列和评分反馈，但长期间隔算法仍可继续增强
- The review center has basic queues and feedback, but the long-term scheduling algorithm can still be improved
- 演示模式使用预置缓存数据，适合公开展示，不适合承载真实多人数据
- Demo mode uses built-in sample data and is intended for public showcasing, not real multi-user data storage

## 主要接口 / Main APIs

- `GET /api/health`
- `GET /api/dashboard/overview`
- `GET /api/analytics/overview`
- `GET /api/books`
- `GET /api/books/:id`
- `GET /api/books/:id/summary`
- `POST /api/books/:id/summary/regenerate`
- `GET /api/notes`
- `POST /api/notes/summarize`
- `POST /api/qa/stream`
- `GET /api/review/today`
- `GET /api/review/scoped`
- `POST /api/review/rate`
- `GET /api/insights/topics`
- `GET /api/import/jobs`
- `POST /api/import/sync-local`
- `GET /api/jobs`
- `POST /api/jobs/:id/retry`
- `GET /api/llm/health`

更完整的接口说明见 [docs/API.md](docs/API.md)。
See [docs/API.md](docs/API.md) for the full API reference.

## 推荐阅读顺序 / Recommended Reading Path

如果你是第一次看这个仓库，建议按下面顺序了解：
If this is your first time exploring the repository, start here:

1. [DEMO_SITE_GUIDE.md](DEMO_SITE_GUIDE.md)
2. [docs/LEARNING_PATH.md](docs/LEARNING_PATH.md)
3. [docs/API.md](docs/API.md)
4. 阅读本 README 中的功能说明与界面预览 / Read the feature overview and screenshots in this README
5. 直接运行演示模式体验核心流程 / Run the demo mode and try the core workflow

## 适合对外介绍的一句话 / One-Line Pitch

ReadMind 是一个面向长期阅读者的本地优先 AI 阅读工作台，它把 Obsidian 中沉睡的微信读书摘录重新组织成可检索、可追问、可复习、可洞察的个人知识系统。

ReadMind is a local-first AI reading workspace for long-term readers. It turns dormant WeRead highlights inside Obsidian into a searchable, askable, reviewable, and insight-generating personal knowledge system.

## License

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
This project is released under the MIT License. See [LICENSE](LICENSE) for details.
