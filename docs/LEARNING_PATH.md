# ReadMind 学习路线

这份路线面向第一次阅读 ReadMind 代码的人。建议不要从某个大页面或某个接口直接扎进去，而是按“产品闭环 -> 数据流 -> 后端服务 -> 前端页面 -> 工程化”的顺序理解。

## 1. 先理解产品闭环

先读：

- `README.md`
- `DEMO_SITE_GUIDE.md`
- `docs/API.md`

要理解的问题：

- ReadMind 解决的是“微信读书划线进入 Obsidian 后，如何继续整理、追问、复习”的问题。
- 核心链路是：导入/同步 -> 解析 Markdown -> 缓存书籍和笔记 -> 检索 -> AI 总结/问答 -> 复习。
- 项目是 local-first，本地 SQLite 是缓存和进度存储，不是云端多用户数据库。

## 2. 看后端入口和路由层

先读：

- `backend/app/__init__.py`
- `backend/app/routes/books.py`
- `backend/app/routes/notes.py`
- `backend/app/routes/qa.py`
- `backend/app/routes/review.py`
- `backend/app/routes/imports.py`
- `backend/app/routes/jobs.py`

阅读重点：

- 路由层主要负责读取 HTTP 参数、调用 service、返回 JSON。
- 统一错误响应在 `backend/app/routes/errors.py`。
- `/api/qa/stream` 是 SSE 流式接口，前端通过 `qaStreamClient.ts` 解析。
- `/api/jobs` 是异步任务中心，书籍摘要、笔记洞察、图谱分析都会进入任务系统。

建议先不要深入所有 service，先弄清楚“一个请求会调用哪个 service”。

## 3. 理解 Vault 数据如何进入系统

核心文件：

- `backend/app/services/vault_parser.py`
- `backend/app/services/vault/parser.py`
- `backend/app/services/payloads/notes.py`
- `backend/tests/test_vault_parser.py`

数据流：

1. `VaultRepository.load()` 判断是否可以复用内存或 SQLite 缓存。
2. 如果缓存过期，则扫描 `VAULT_ROOT` 下的 Markdown 文件。
3. `parse_markdown_book()` 把微信读书 Markdown 解析成 book 和 notes。
4. Repository 把结果写入 SQLite，并组装成接口使用的 `data = { books, notes, stats }`。

阅读重点：

- `vault_parser.py` 是有状态边界，负责本地文件和 SQLite。
- `vault/parser.py` 是纯解析逻辑，更适合作为学习和测试入口。
- 如果你要支持新的 Markdown 格式，优先改 `vault/parser.py` 并补测试。

## 4. 理解检索和问答

核心文件：

- `backend/app/services/search/ranker.py`
- `backend/app/services/qa_service.py`
- `backend/app/routes/qa.py`
- `frontend/src/services/qaStreamClient.ts`
- `frontend/src/stores/qa.ts`

数据流：

1. 用户问题进入 `/api/qa/ask` 或 `/api/qa/stream`。
2. `answer_question()` 先用 ranker 从笔记里找引用。
3. `qa_service.py` 把引用整理成 evidence 和 LLM messages。
4. 如果 LLM 可用，后端生成模型回答；如果不可用，返回基于引用的 fallback。
5. 前端 `qaStreamClient.ts` 解析 SSE，`stores/qa.ts` 更新对话状态。

阅读重点：

- `ranker.py` 是“关键词 + ngram + embedding”的混合检索。
- query rewrite 用于把抽象概念扩展成更多召回词。
- QA 回答必须可溯源，所以排序会优先奖励明确字段命中，而不是只看语义相似。

## 5. 理解异步任务

核心文件：

- `backend/app/services/task_runner.py`
- `backend/app/services/job_repository.py`
- `frontend/src/utils/jobPolling.ts`
- `frontend/src/composables/useJobPolling.ts`
- `frontend/src/stores/books.ts`
- `frontend/src/stores/import.ts`

数据流：

1. 前端触发一个耗时任务，例如书籍摘要或 AI 洞察。
2. 后端创建 job，写入 SQLite。
3. `task_runner.py` 用本地线程池执行任务。
4. 前端通过 `pollAsyncJob()` 或 `useJobPolling()` 轮询 job 状态。

重要限制：

- 当前任务队列适合本地单进程使用。
- 它不是生产级分布式队列，进程重启后不能恢复正在运行的线程任务。
- 如果将来要部署多人服务，应把 `task_runner.py` 抽象成可替换的队列接口。

## 6. 理解复习系统

核心文件：

- `backend/app/services/review/scheduler.py`
- `backend/app/services/review/payloads.py`
- `backend/app/routes/review.py`
- `frontend/src/stores/review.ts`
- `frontend/src/views/review/ReviewCenterView.vue`
- `backend/tests/test_review_scheduler.py`

数据流：

1. 前端请求 `/api/review/today`。
2. `review/payloads.py` 根据 notes 和 SQLite 中的 review progress 找出到期卡片。
3. 用户评分后，`VaultRepository.record_review_result()` 更新掌握度和下次复习时间。
4. `scheduler.py` 定义间隔、掌握度、连续复习规则。

阅读重点：

- 复习规则是纯函数，适合先读测试再读实现。
- UI payload 和调度规则已分离，调规则时尽量只改 `scheduler.py`。

## 7. 理解前端结构

建议顺序：

- `frontend/src/router/index.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/modules/*`
- `frontend/src/stores/*`
- `frontend/src/views/dashboard/DashboardView.vue`
- `frontend/src/views/books/BookLibraryView.vue`
- `frontend/src/views/notes/NoteWorkbenchView.vue`
- `frontend/src/views/qa/QaCenterView.vue`

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

## 8. 推荐调试路径

如果你想跟一次完整流程：

1. 启动后端和前端。
2. 打开导入中心，触发本地同步。
3. 看 `backend/app/services/vault_parser.py` 如何加载数据。
4. 打开笔记工作台，搜索一个关键词。
5. 看 `backend/app/services/search/ranker.py` 如何打分。
6. 点击 AI 再整理。
7. 看 `task_runner.py` 创建并执行异步任务。
8. 打开 QA 页面，问一个单本书问题。
9. 看 `routes/qa.py` 和 `qaStreamClient.ts` 如何完成流式回答。
10. 打开复习中心，评分一张卡片。
11. 看 `review/scheduler.py` 如何计算下次复习时间。

## 9. 推荐贡献入口

适合初次贡献：

- 给 `vault/parser.py` 增加新的 Markdown 样例测试。
- 给 `search/ranker.py` 增加固定 notes 的排序测试。
- 给 `docs/API.md` 补充更具体的响应示例。
- 拆分 `TopicGraphView.vue` 的筛选面板和详情面板。
- 给 `backend/app/services/graph/payloads.py` 增加图谱 payload 测试。

不建议初次贡献直接改：

- SQLite schema。
- 任务队列执行模型。
- QA 流式协议。
- 大范围字段重命名。

这些改动影响面更大，最好先补测试或开 issue 讨论。

