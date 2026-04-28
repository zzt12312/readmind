# ReadMind

面向 `Obsidian + 微信读书` 工作流的 AI 阅读笔记整理与复习系统。

`ReadMind` 试图解决一个很真实的问题：读了很多、划了很多、记了很多，但后续几乎不会系统整理，也很难把过去的笔记重新利用起来。这个项目把本地 Markdown 笔记接入进来，再通过结构化解析、智能检索、AI 总结、可溯源问答和复习机制，把分散书摘变成可搜索、可追问、可回顾的个人知识库。

## 核心能力

- 本地 `Obsidian` 读书笔记接入与 Markdown 结构化解析
- 书库、书籍详情、笔记工作台、智能问答、复习中心
- 基于个人阅读笔记的 AI 摘要、AI 洞察、流式问答
- 支持单本书问答、全库问答、引用来源展示与跳转原笔记
- 支持关键词 + 混合检索、搜索高亮、主题图谱、复习卡片
- 支持异步任务体系：书籍摘要、AI 洞察、图谱分析、书库同步

## 技术栈

- 前端：`Vue 3` + `TypeScript` + `Vite` + `Element Plus` + `Pinia` + `Vue Router`
- 后端：`Flask` + `Python`
- AI：`DeepSeek`
- 检索与缓存：`SQLite` + 本地 embedding 缓存
- 数据来源：本地 `Obsidian Vault` 中的微信读书 Markdown 笔记

## 项目亮点

- 不是 AI 套壳 demo，而是围绕真实阅读场景构建的完整产品闭环
- 打通了“导入 -> 解析 -> 检索 -> 总结 -> 问答 -> 复习”整条链路
- AI 输出和个人笔记资产强绑定，支持引用来源与原笔记跳转
- 前端页面信息密度高，包含复杂筛选、状态管理、流式输出和多面板联动
- 后端实现了统一异步任务体系，支持任务中心、状态轮询和失败重试

## 界面预览

### 首页总览

![ReadMind Dashboard](docs/screenshots/dashboard.png)

首页展示阅读空间概览、核心指标、最近整理的书和活跃主题，适合快速进入复习与整理流程。

### 书库与封面视图

![ReadMind Books](docs/screenshots/books.png)

书库页重点展示真实书籍封面、标签和笔记规模，支持按关键词和分类快速浏览。

### 书籍详情与 AI 摘要

![ReadMind Book Detail](docs/screenshots/book-detail.png)

书籍详情页展示封面、元信息、AI 总结、读书笔记和本书高亮，是“单本书整理”的核心页面。

### 笔记工作台

![ReadMind Notes](docs/screenshots/notes.png)

笔记工作台支持按书籍、标签、章节和排序浏览真实笔记内容，是做二次整理、筛选和 AI 洞察的主操作区。

### 智能问答

![ReadMind QA](docs/screenshots/qa.png)

问答页支持单本书/全库问答、连续对话、状态提示、流式回答和引用来源联动。

### 复习中心

![ReadMind Review](docs/screenshots/review.png)

复习中心围绕卡片回顾、掌握度反馈和跳转原笔记，形成长期知识回看闭环。

## 目录结构

```text
readmind/
├── frontend/                # Vue3 前端
│   ├── src/
│   │   ├── api/             # 接口请求层
│   │   ├── components/      # 通用组件与图谱组件
│   │   ├── layouts/         # 主布局与认证布局
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── styles/          # 主题、动效、样式变量
│   │   ├── types/           # 类型定义
│   │   └── views/           # 页面视图
│   └── package.json
├── backend/                 # Flask 后端
│   ├── app/
│   │   ├── routes/          # 路由：books / notes / qa / review / jobs ...
│   │   ├── services/        # 解析、检索、图谱、异步任务、LLM 等服务
│   │   ├── config.py
│   │   └── __init__.py
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
├── DEMO_SITE_GUIDE.md       # 演示站使用说明
└── docs/                    # 项目截图等公开展示资源
```

## 当前已完成模块

- 真实 Obsidian 书库接入与本地同步
- 书库页、书籍详情页、首页书架
- 笔记工作台：按书籍 / 标签 / 章节 / 分类 / 关键词检索
- AI 洞察：基于当前筛选范围生成结构化总结
- 智能问答：连续对话、流式输出、书籍范围限制、引用跳转
- 复习中心：卡片复习、评分反馈、服务端持久化复习进度
- 主题图谱 / 主题聚类
- 异步任务中心与失败任务重试
- LLM / embedding 状态检测

## 快速启动

### 1. 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：

- `http://127.0.0.1:5173`

### 2. 启动后端

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

## 环境变量

后端 `.env` 参考：

```env
SECRET_KEY=readmind-dev-secret
DEEPSEEK_API_KEY=replace_with_your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 主要接口

- `GET /api/health`
- `GET /api/dashboard/overview`
- `GET /api/books`
- `GET /api/books/:id/summary`
- `POST /api/books/:id/summary/regenerate`
- `GET /api/notes`
- `POST /api/notes/summarize`
- `POST /api/qa/stream`
- `GET /api/review/today`
- `POST /api/review/rate`
- `GET /api/insights/topics`
- `GET /api/jobs`
- `GET /api/llm/health`

## 推荐阅读顺序

如果你是第一次看这个仓库，建议按下面顺序了解：

1. [DEMO_SITE_GUIDE.md](/Users/taozhang/Desktop/maybe/DEMO_SITE_GUIDE.md:1)
2. 阅读本 README 中的功能说明与界面预览
3. 直接访问演示站体验核心流程

## 当前状态

这个仓库已经不是单纯的原型设计文档，而是一个可运行、可演示、可继续迭代的全栈项目。  
目前最值得继续优化的方向主要集中在：

- AI 链路稳定性与状态体验
- 检索质量进一步增强
- 复习系统长期调度
- 异步任务体系继续完善

## License

当前仓库默认仅作个人学习、求职展示和项目迭代使用。
