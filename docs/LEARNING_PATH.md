# ReadMind 学习路线

这份路线面向第一次阅读 ReadMind 代码的人。建议不要从某个大页面或某个接口直接扎进去，而是按“产品体验 -> 数据来源 -> 后端服务 -> 前端页面 -> 关键闭环 -> 可贡献入口”的顺序理解。

ReadMind 现在已经不只是一个阅读笔记展示工具，而是一个包含导入、解析、检索、AI 总结、智能问答、复习、知识图谱、数据看板、异步任务和吉祥物反馈的个人知识工作台。

## 1. 先从产品体验建立全局地图

先读：

- `README.md`
- `DEMO_SITE_GUIDE.md`
- `docs/API.md`

建议先实际跑一遍演示模式：

```bash
cd backend
cp .env.example .env
# 将 DEMO_DATA_ONLY=1 写入 .env
python run.py

cd frontend
npm install
npm run dev
```

需要先理解的问题：

- ReadMind 解决的是“微信读书划线进入 Obsidian 后，如何继续整理、追问、复习”的问题。
- 核心链路是：同步本地笔记 -> 解析 Markdown -> 缓存书籍和笔记 -> 检索 -> AI 总结/问答 -> 图谱/数据看板 -> 复习。
- 项目偏 local-first，本地 SQLite 是缓存、任务和复习进度存储，不是云端多用户数据库。
- `DEMO_DATA_ONLY=1` 是公开演示模式，不读取真实 Vault，也不调用外部模型。

## 2. 先看目录分层

前端主要目录：

- `frontend/src/api/`：接口请求模块
- `frontend/src/assets/`：签签插画等静态资源
- `frontend/src/components/`：通用组件、笔记组件、问答组件、图谱组件、签签组件
- `frontend/src/composables/`：轮询等组合式逻辑
- `frontend/src/constants/`：路由、问答预设、签签文案
- `frontend/src/services/`：SSE、localStorage 等客户端服务
- `frontend/src/stores/`：Pinia 状态管理
- `frontend/src/types/`：接口类型定义
- `frontend/src/views/`：页面级视图

后端主要目录：

- `backend/app/routes/`：HTTP 路由层
- `backend/app/services/vault/`：Markdown 解析
- `backend/app/services/search/`：检索排序
- `backend/app/services/review/`：复习调度
- `backend/app/services/graph/`：图谱 payload
- `backend/app/services/payloads/`：页面 payload 组装
- `backend/app/services/task_runner.py`：本地异步任务执行
- `backend/app/services/job_repository.py`：任务状态持久化
- `backend/tests/`：后端核心逻辑测试

## 3. 看后端入口和路由层

先读：

- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/routes/__init__.py`
- `backend/app/routes/dashboard.py`
- `backend/app/routes/analytics.py`
- `backend/app/routes/books.py`
- `backend/app/routes/notes.py`
- `backend/app/routes/qa.py`
- `backend/app/routes/review.py`
- `backend/app/routes/imports.py`
- `backend/app/routes/jobs.py`
- `backend/app/routes/errors.py`

阅读重点：

- 路由层主要负责读取 HTTP 参数、调用 service、返回 JSON。
- 统一错误响应在 `backend/app/routes/errors.py`。
- `/api/qa/stream` 是 SSE 流式接口，前端通过 `qaStreamClient.ts` 解析。
- `/api/jobs` 是异步任务中心，书籍摘要、笔记洞察、图谱分析、书库同步都会进入任务系统。
- `/api/dashboard/overview` 和 `/api/analytics/overview` 是理解首页和数据看板的好入口。

建议先不要深入所有 service，先弄清楚“一个请求会调用哪个 service”。

## 4. 理解 Vault 数据如何进入系统

核心文件：

- `backend/app/services/vault_parser.py`
- `backend/app/services/vault/parser.py`
- `backend/app/services/import_service.py`
- `backend/app/services/payloads/notes.py`
- `backend/tests/test_vault_parser.py`

数据流：

1. 导入中心调用同步接口。
2. `import_service.py` 判断是否处于演示模式，并检查 `VAULT_ROOT`。
3. `VaultRepository.load()` 判断是否可以复用内存或 SQLite 缓存。
4. 如果缓存过期，则扫描 `VAULT_ROOT` 下的 Markdown 文件。
5. `parse_markdown_book()` 把微信读书 Markdown 解析成 book 和 notes。
6. Repository 把结果写入 SQLite，并组装成接口使用的 `data = { books, notes, stats }`。

阅读重点：

- `vault_parser.py` 是有状态边界，负责本地文件、缓存和 SQLite。
- `vault/parser.py` 是纯解析逻辑，更适合作为学习和测试入口。
- 如果你要支持新的 Markdown 格式，优先改 `vault/parser.py` 并补测试。

## 5. 理解检索、AI 洞察和问答

核心文件：

- `backend/app/services/search/ranker.py`
- `backend/app/services/qa_service.py`
- `backend/app/services/note_insight_service.py`
- `backend/app/services/llm_client.py`
- `backend/app/routes/qa.py`
- `frontend/src/services/qaStreamClient.ts`
- `frontend/src/stores/qa.ts`
- `frontend/src/components/qa/*`
- `frontend/src/views/qa/QaCenterView.vue`

问答数据流：

1. 用户问题进入 `/api/qa/stream`。
2. `qa_service.py` 先用 ranker 从笔记里找引用。
3. 服务端把引用整理成 evidence 和 LLM messages。
4. 如果 LLM 可用，后端生成模型回答；如果不可用，返回基于引用的 fallback。
5. 前端 `qaStreamClient.ts` 解析 SSE，`stores/qa.ts` 更新对话状态。
6. `components/qa/*` 负责输入框、会话、引用、状态面板和历史会话。

AI 洞察数据流：

1. 笔记工作台按当前筛选范围调用 `POST /api/notes/summarize`。
2. 后端创建异步任务。
3. `note_insight_service.py` 基于筛选结果生成结构化总结、复习问题和引用依据。
4. 前端通过任务轮询拿到结果，并在 `NoteInsightPanel.vue` 展示。

阅读重点：

- `ranker.py` 是“关键词 + ngram + embedding”的混合检索。
- query rewrite 用于把抽象概念扩展成更多召回词。
- QA 回答必须可溯源，所以排序会优先奖励明确字段命中，而不是只看语义相似。
- 问答 UI 已经拆到 `components/qa/`，不要直接把复杂逻辑继续堆到页面里。

## 6. 理解首页和数据看板

核心文件：

- `backend/app/services/payloads/dashboard.py`
- `backend/app/services/payloads/analytics.py`
- `backend/app/routes/dashboard.py`
- `backend/app/routes/analytics.py`
- `frontend/src/stores/dashboard.ts`
- `frontend/src/stores/analytics.ts`
- `frontend/src/views/dashboard/DashboardView.vue`
- `frontend/src/views/analytics/AnalyticsView.vue`
- `frontend/src/types/dashboard.ts`
- `frontend/src/types/analytics.ts`

阅读重点：

- 首页回答“今天我应该从哪里开始？”。
- 数据看板回答“我的阅读偏好和长期积累是什么样？”。
- Dashboard payload 偏行动导向，包括今日回顾、行动队列、推荐复习。
- Analytics payload 偏洞察导向，包括阅读排行、雷达图、热力图、高价值矩阵和长期主义指标。

如果要继续加可视化指标，建议先改 `payloads/analytics.py`，再补 `types/analytics.ts` 和 `AnalyticsView.vue`。

## 7. 理解复习系统

核心文件：

- `backend/app/services/review/scheduler.py`
- `backend/app/services/review/payloads.py`
- `backend/app/routes/review.py`
- `frontend/src/api/modules/review.ts`
- `frontend/src/stores/review.ts`
- `frontend/src/views/review/ReviewCenterView.vue`
- `backend/tests/test_review_scheduler.py`
- `backend/tests/test_review_payloads.py`

数据流：

1. 前端请求 `/api/review/today` 或 `/api/review/scoped`。
2. `review/payloads.py` 根据 notes 和 SQLite 中的 review progress 找出到期、薄弱、新卡片。
3. 用户评分后，`VaultRepository.record_review_result()` 更新掌握度和下次复习时间。
4. `scheduler.py` 定义间隔、掌握度、连续复习规则。
5. 前端 store 根据评分生成即时反馈、薄弱队列和完成状态。

阅读重点：

- 复习规则是纯函数，适合先读测试再读实现。
- UI payload 和调度规则已分离，调规则时尽量只改 `scheduler.py`。
- `ReviewCenterView.vue` 有较多产品交互，可以后续继续拆组件。

## 8. 理解知识图谱

核心文件：

- `backend/app/services/graph_analysis_service.py`
- `backend/app/services/graph/payloads.py`
- `backend/app/routes/analytics.py`
- `backend/app/routes/jobs.py`
- `frontend/src/views/graph/TopicGraphView.vue`
- `frontend/src/components/graph/TopicGraphChart.vue`
- `frontend/src/types/insights.ts`

阅读重点：

- 图谱支持 `category` 和 `topic` 两种模式。
- 主题簇来自书籍、分类、标签、章节和笔记共现关系。
- ECharts 只负责展示，真正的数据结构来自后端 payload。
- 图谱分析可以走异步任务，因此需要理解 `task_runner.py` 和 `job_repository.py`。

如果要继续优化图谱，建议优先拆分 `TopicGraphView.vue` 的筛选面板、聚类列表、详情面板和图表舞台。

## 9. 理解异步任务

核心文件：

- `backend/app/services/task_runner.py`
- `backend/app/services/job_repository.py`
- `backend/app/routes/jobs.py`
- `frontend/src/utils/jobPolling.ts`
- `frontend/src/composables/useJobPolling.ts`
- `frontend/src/stores/books.ts`
- `frontend/src/stores/import.ts`
- `frontend/src/views/jobs/JobsCenterView.vue`

数据流：

1. 前端触发耗时任务，例如书籍摘要、AI 洞察、图谱分析、本地同步。
2. 后端创建 job，写入 SQLite。
3. `task_runner.py` 用本地线程池执行任务。
4. 前端通过 `pollAsyncJob()` 或 `useJobPolling()` 轮询 job 状态。
5. 任务中心读取 `/api/jobs` 展示任务列表，并支持失败重试。

重要限制：

- 当前任务队列适合本地单进程使用。
- 它不是生产级分布式队列，进程重启后不能恢复正在运行的线程任务。
- 如果将来要部署多人服务，应把 `task_runner.py` 抽象成可替换的队列接口。

## 10. 理解前端页面组合

建议顺序：

1. `frontend/src/router/index.ts`
2. `frontend/src/api/client.ts`
3. `frontend/src/api/modules/*`
4. `frontend/src/types/*`
5. `frontend/src/stores/*`
6. `frontend/src/layouts/MainLayout.vue`
7. `frontend/src/components/common/SidebarNav.vue`
8. `frontend/src/components/common/TopNavBar.vue`
9. `frontend/src/views/dashboard/DashboardView.vue`
10. `frontend/src/views/notes/NoteWorkbenchView.vue`
11. `frontend/src/views/qa/QaCenterView.vue`
12. `frontend/src/views/review/ReviewCenterView.vue`

前端分层：

- `api/` 只负责请求后端。
- `types/` 定义接口数据结构。
- `stores/` 负责跨页面状态和异步 action。
- `services/` 放可独立演进的客户端逻辑，例如 QA SSE 和 localStorage。
- `components/` 放可复用 UI 块。
- `views/` 尽量只做页面组合、路由同步和少量局部状态。

已拆出的重点组件：

- QA：`frontend/src/components/qa/*`
- 笔记工作台：`frontend/src/components/notes/*`
- 图谱：`frontend/src/components/graph/TopicGraphChart.vue`
- 签签：`frontend/src/components/mascot/MascotBubble.vue`

## 11. 理解签签系统

核心文件：

- `private/MASCOT_DESIGN_PLAN.md`
- `frontend/src/components/mascot/MascotBubble.vue`
- `frontend/src/constants/mascotMessages.ts`
- `frontend/src/assets/mascot/`

阅读重点：

- `MascotBubble.vue` 只负责展示和动画。
- `mascotMessages.ts` 负责集中管理签签在首页、导入、复习、洞察、问答、空状态里的文案。
- 签签不是装饰图，而是关键节点反馈系统：同步成功、问答完成、复习完成、洞察生成都会给用户可感知的回应。
- 前端实际引用 WebP 资产，PNG 作为源资产留档。

如果要继续扩展签签，建议先增加 `MascotCue` 场景，而不是在页面里硬写文案。

## 12. 推荐调试路径

如果你想跟一次完整流程：

1. 启动后端和前端。
2. 打开导入中心，触发本地同步。
3. 看 `backend/app/services/import_service.py` 和 `vault_parser.py` 如何加载数据。
4. 打开首页，理解 `payloads/dashboard.py` 如何组装行动队列。
5. 打开数据看板，理解 `payloads/analytics.py` 如何生成阅读指标。
6. 打开笔记工作台，搜索一个关键词。
7. 看 `backend/app/services/search/ranker.py` 如何打分。
8. 点击 AI 洞察，观察异步任务如何创建和轮询。
9. 打开 QA 页面，问一个单本书问题。
10. 看 `routes/qa.py` 和 `qaStreamClient.ts` 如何完成流式回答。
11. 打开复习中心，评分一张卡片。
12. 看 `review/scheduler.py` 如何计算下次复习时间。
13. 打开知识图谱，切换领域聚类和知识主题。
14. 打开任务中心，查看后台任务状态。

## 13. 推荐贡献入口

适合初次贡献：

- 给 `vault/parser.py` 增加新的 Markdown 样例测试。
- 给 `search/ranker.py` 增加固定 notes 的排序测试。
- 给 `docs/API.md` 补充更具体的响应示例。
- 给 `payloads/analytics.py` 增加新的数据看板指标。
- 拆分 `TopicGraphView.vue` 的筛选面板和详情面板。
- 给 `backend/app/services/graph/payloads.py` 增加图谱 payload 测试。
- 给 `mascotMessages.ts` 增加更细的签签反馈场景。

不建议初次贡献直接改：

- SQLite schema。
- 任务队列执行模型。
- QA 流式协议。
- 大范围字段重命名。
- 全局视觉主题变量。

这些改动影响面更大，最好先补测试或开 issue 讨论。

## 14. 推荐测试顺序

后端：

```bash
cd backend
.venv/bin/python -m pytest
```

前端：

```bash
cd frontend
npm run typecheck
npm run build
```

如果你只改了纯后端 payload，至少跑相关 `pytest`。如果你改了接口字段，还要同步检查 `frontend/src/types/` 和对应 store。
