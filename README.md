# ReadMind

[English README](README_EN.md)

面向 `Obsidian + 微信读书` 工作流的 AI 阅读笔记整理、问答、洞察与复习系统。

ReadMind 试图解决一个很常见的问题：读了很多书、划了很多线、写了很多摘录，但后续很少再系统整理，也很难把过去的笔记重新用起来。这个项目把本地 Markdown 阅读笔记接入进来，通过结构化解析、混合检索、AI 总结、可溯源问答、主题图谱、数据看板和复习机制，把分散书摘变成一个可以持续回看的个人知识工作台。

## 在线体验

[打开 ReadMind 演示站](https://readmind.site)

演示站使用静态演示缓存，不会读取或上传你的真实 Obsidian 数据，但可以体验书库、笔记工作台、签签问答、AI 洞察、知识图谱、复习中心和数据看板。

## 核心能力

- 本地 `Obsidian` 读书笔记同步与微信读书 Markdown 解析
- 书库、书籍详情、笔记工作台、智能问答、复习中心、知识图谱、数据看板
- 基于个人阅读笔记的 AI 摘要、AI 洞察、流式问答与引用来源回溯
- 支持单本书问答、全库问答、搜索高亮、主题筛选、章节筛选和跳转原笔记
- 支持阅读偏好、阅读时长排行、主题雷达图、阅读热力图、高价值书籍矩阵等数据洞察
- 支持复习目标、自定义每日卡片数、到期/薄弱/新卡片队列和评分反馈
- 支持异步任务体系：书籍摘要、AI 洞察、图谱分析、书库同步、任务轮询和失败重试
- 内置小书签精灵“签签”，在导入、问答、洞察、复习等关键节点提供温柔反馈

## 技术栈

- 前端：`Vue 3` + `TypeScript` + `Vite` + `Element Plus` + `Pinia` + `Vue Router` + `ECharts`
- 后端：`Flask` + `Python`
- AI：`DeepSeek`
- 检索与缓存：`SQLite` + 本地 embedding 缓存
- 数据来源：本地 `Obsidian Vault` 中的微信读书 Markdown 笔记

## 运行模式

- 本地真实模式：读取 `.env` 中配置的 `VAULT_ROOT`，并在需要时调用 `DeepSeek`
- 公开演示模式：设置 `DEMO_DATA_ONLY=1`，使用预置缓存数据，不读取真实 Vault，也不调用外部模型
- 前端静态演示模式：设置 `VITE_STATIC_DEMO=1`，构建纯前端演示站

## 界面预览

### 首页总览

![ReadMind Dashboard](docs/screenshots/dashboard.png)

首页展示今日阅读回顾、行动队列、阅读指标、最近整理书籍和签签的温柔提醒，适合快速进入复习、整理或问答流程。

### 数据看板

![ReadMind Analytics](docs/screenshots/analytics.png)

数据看板展示阅读时长排行、偏好主题、长期阅读节奏、阅读热力图和高价值书籍矩阵，让用户能看到自己的阅读积累正在形成结构。

### 书库与封面视图

![ReadMind Books](docs/screenshots/books.png)

书库页展示真实书籍封面、作者、分类、标签和笔记规模，支持按关键词和分类快速浏览。

### 书籍详情与 AI 摘要

![ReadMind Book Detail](docs/screenshots/book-detail.png)

书籍详情页展示封面、元信息、AI 总结、章节笔记、高频主题和摘要生成状态，是单本书整理的核心页面。

### 笔记工作台

![ReadMind Notes](docs/screenshots/notes.png)

笔记工作台支持按书籍、标签、章节、分类、关键词和排序浏览真实笔记内容，并在右侧生成当前筛选范围的 AI 洞察。

### 智能问答

![ReadMind QA](docs/screenshots/qa.png)

智能问答由“签签”作为回答人格，支持单本书/全库问答、连续追问、检索状态提示、结构化回答和引用来源联动。

### 复习中心

![ReadMind Review](docs/screenshots/review.png)

复习中心支持每日目标、自定义卡片数、到期/薄弱/新卡片队列、评分反馈、复习完成反馈和跳转原笔记。

### 知识图谱

![ReadMind Graph](docs/screenshots/graph.png)

知识图谱支持领域聚类和知识主题两种视角，展示主题簇、主题关系图、关联书籍和代表性摘录。

### 导入中心

![ReadMind Import](docs/screenshots/import.png)

导入中心负责同步本地 Obsidian 阅读目录，并展示同步状态、目录检测、演示模式提示和下一步行动建议。

### 任务中心

![ReadMind Jobs](docs/screenshots/jobs.png)

任务中心统一展示书籍摘要、AI 洞察、本地同步、图谱分析等后台任务，支持状态筛选、类型筛选、进度查看和失败重试。

## 快速启动

### 1. 启动后端

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

默认地址：

- `http://127.0.0.1:5000`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：

- `http://127.0.0.1:5173`
- 如果 `5173` 被占用，Vite 会自动切到 `5174` 或下一个可用端口

## 首次启动检查清单

1. `Node.js` 版本满足当前 Vite 需求，`npm run dev` 能正常启动
2. `Python 3`、虚拟环境和 `pip install -r requirements.txt` 已完成
3. `backend/.env` 已配置，尤其是 `VAULT_ROOT` 和 `DEEPSEEK_API_KEY`
4. `VAULT_ROOT` 指向你自己的 Obsidian 阅读目录，而不是作者机器上的示例路径
5. 先启动后端，再启动前端；前端开发环境会把 `/api` 代理到 Flask
6. 如果你只是想体验界面，可以将 `DEMO_DATA_ONLY=1` 写入 `.env`，使用演示数据模式启动

## 环境变量

后端 `.env` 参考：

```env
SECRET_KEY=readmind-dev-secret
DEEPSEEK_API_KEY=replace_with_your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
VAULT_ROOT=/path/to/your/Obsidian/Vault/书籍阅读
DEMO_DATA_ONLY=0
```

公开演示站如果不连接后端 API，可以使用前端静态演示构建：

```bash
cd frontend
VITE_STATIC_DEMO=1 npm run build
npm run preview -- --host 0.0.0.0 --port 3000
```

这个模式会在浏览器内使用 `frontend/src/mock/staticDemo.ts` 的缓存数据，展示书库、笔记、签签问答、AI 洞察、知识图谱、复习中心和数据看板，不会读取真实 Vault，也不会调用外部模型。

## 目录结构

```text
readmind/
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── api/             # 接口请求层
│   │   ├── assets/          # 签签插画等静态资源
│   │   ├── components/      # 通用组件、问答组件、笔记组件、图谱组件
│   │   ├── composables/     # 轮询等组合式逻辑
│   │   ├── config/          # 前端运行/构建开关
│   │   ├── constants/       # 路由、问答预设、签签文案
│   │   ├── layouts/         # 主布局与认证布局
│   │   ├── mock/            # 静态演示数据
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── styles/          # 主题、动效、样式变量
│   │   ├── types/           # 类型定义
│   │   └── views/           # 页面视图
│   └── package.json
├── backend/                 # Flask 后端
│   ├── app/
│   │   ├── routes/          # dashboard / analytics / books / notes / qa / review / jobs ...
│   │   ├── services/        # 解析、检索、图谱、异步任务、LLM、复习等服务
│   │   ├── config.py
│   │   └── __init__.py
│   ├── tests/               # 后端测试
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
├── docs/                    # API、学习路线与截图
├── private/                 # 私有规划与评审文档，不建议对外发布敏感内容
└── DEMO_SITE_GUIDE.md       # 演示站使用说明
```

## 当前已完成模块

- 真实 Obsidian 书库接入与本地同步
- 书库页、书籍详情页、首页书架与行动队列
- 数据看板：阅读排行、偏好主题、热力图、雷达图、高价值书籍矩阵
- 笔记工作台：按书籍 / 标签 / 章节 / 分类 / 关键词检索
- AI 洞察：基于当前筛选范围生成结构化总结、复习问题和引用依据
- 智能问答：连续对话、流式输出、书籍范围限制、引用跳转
- 复习中心：卡片复习、评分反馈、队列筛选、自定义目标、服务端持久化进度
- 主题图谱：领域聚类、知识主题、主题关系图、关联书籍与摘录
- 异步任务中心：任务列表、状态筛选、失败任务重试
- LLM / embedding 状态检测与自动 embedding 预热
- 小书签精灵“签签”：正式插画、状态动画、统一文案系统和关键节点反馈

## 隐私与数据边界

- 本地真实模式下，系统会读取 `VAULT_ROOT` 指向的 Markdown 笔记目录
- 书库、笔记、图谱、复习等基础能力主要依赖本地缓存数据库
- 当你主动触发摘要、AI 洞察或智能问答时，系统只会将当前命中的摘录片段发送给 `DeepSeek`
- 如果你不希望任何内容离开本机，可以启用 `DEMO_DATA_ONLY=1` 或关闭模型调用链路

## 当前能力边界

- 真实模式下，导入中心以“同步本地 Obsidian 目录”为主；直接上传 Markdown/zip 仍是演示模式交互
- 异步任务使用本地线程池和 SQLite 记录状态，适合个人本地运行；如果要做多人生产服务，建议替换为 Celery/RQ 等队列
- 复习中心已经具备基础队列和评分反馈，但长期间隔算法仍可继续增强
- 演示模式使用预置缓存数据，适合公开展示，不适合承载真实多人数据

## 主要接口

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

## 推荐阅读顺序

如果你是第一次看这个仓库，建议按下面顺序了解：

1. [docs/CONTRIBUTOR_START.md](docs/CONTRIBUTOR_START.md)
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. [DEMO_SITE_GUIDE.md](DEMO_SITE_GUIDE.md)
4. [docs/LEARNING_PATH.md](docs/LEARNING_PATH.md)
5. [docs/API.md](docs/API.md)
6. 直接运行演示模式体验核心流程

## 适合对外介绍的一句话

ReadMind 是一个面向长期阅读者的本地优先 AI 阅读工作台，它把 Obsidian 中沉睡的微信读书摘录重新组织成可检索、可追问、可复习、可洞察的个人知识系统。

## License

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
