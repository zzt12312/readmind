# AI 生成任务异步化方案

## 1. 目标

当前项目里的 AI 能力已经可用，但书籍摘要、AI 洞察、Embedding 预热、图谱分析大多还是“请求时即时计算”。
这会带来几个问题：

- 首次进入书籍详情时，摘要生成会阻塞首屏体验
- 笔记工作台点击“重新总结”时，用户必须同步等待
- Embedding / 图谱分析这类重任务不适合挂在普通请求里
- 后续如果接更多模型能力，请求链路会越来越重

异步化的目标不是“为了复杂而复杂”，而是把这些生成任务从同步请求里拆出来，变成：

1. 创建任务
2. 后台执行
3. 前端轮询或订阅任务状态
4. 任务完成后回填结果

这样项目会更像真实产品，也更适合在面试里讲工程设计。

---

## 2. 最值得先异步化的任务

第一阶段只做 4 类任务，不要一上来把所有逻辑都扔进队列。

### 2.1 书籍摘要生成

当前入口：

- `GET /api/books/:id/summary`
- `POST /api/books/:id/summary/regenerate`

建议改成：

- 首次请求时，如果没有缓存，直接创建任务并返回 `pending`
- 前端显示“摘要生成中”
- 后端完成后写入缓存

这是最优先的一类，因为它最影响用户对“第一次打开很慢”的感知。

### 2.2 笔记工作台 AI 洞察

当前入口：

- `POST /api/notes/summarize`

建议改成：

- 创建一条 `notes_insight` 任务
- 任务参数包含当前筛选条件
- 任务完成后返回结构化洞察

这类任务比较适合异步，因为模型生成时间不可控，而且用户已经有“点击重新总结”的预期。

### 2.3 本地书库同步后的 Embedding 预计算

当前入口：

- `POST /api/import/sync-local`

建议改成：

- 本地书库同步成功后，不在主请求里做 embedding
- 同步任务完成后，自动触发 `embedding_rebuild` 子任务
- 子任务负责对新增 / 变更笔记生成 embedding 并持久化

这是检索层的基础设施，应该放到后台。

### 2.4 图谱 / 聚类预分析

当前入口：

- `GET /api/insights/topics`

建议改成：

- 用户第一次打开图谱页时，如果没有缓存，触发图谱分析任务
- 任务完成后把主题簇和关系图缓存起来
- 后续按条件变化再重新分析

这类任务适合预生成，因为它本质上是“分析结果”，不是用户每次都必须即时生成的内容。

---

## 3. 技术方案选择

### 3.1 推荐方案

结合你当前项目栈，我建议使用：

- `Flask`
- `Redis`
- `Celery`
- `SQLite` 先继续保留业务缓存

原因：

- 你当前后端已经是 Flask，接 Celery 很自然
- Redis 适合做 broker 和任务状态缓存
- Celery 能比较清晰地讲任务队列、重试、状态机
- 面试里也更容易解释成“标准异步任务体系”

### 3.2 为什么不直接继续用线程

你现在已有一些后台 warmup / 本地缓存逻辑，短期靠线程可以跑，但不适合成为长期方案：

- Flask 进程重启后任务会丢
- 没有统一任务状态
- 不能方便重试
- 难以扩展多个 worker

所以线程可以做过渡，但正式方案还是应落到 `Celery + Redis`。

---

## 4. 任务模型设计

建议新增一张任务表，统一管理所有后台任务。

### 4.1 表名

`async_jobs`

### 4.2 建议字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | TEXT / UUID | 任务 ID |
| `job_type` | TEXT | 任务类型，如 `book_summary` |
| `status` | TEXT | `queued / processing / success / failed / canceled` |
| `resource_type` | TEXT | 资源类型，如 `book / note_scope / vault / graph` |
| `resource_id` | TEXT | 资源 ID，如 `book_id` |
| `payload_json` | TEXT | 请求参数快照 |
| `result_json` | TEXT | 成功结果 |
| `error_message` | TEXT | 失败原因 |
| `progress` | INTEGER | 0 - 100 |
| `retry_count` | INTEGER | 已重试次数 |
| `created_at` | TEXT | 创建时间 |
| `started_at` | TEXT | 开始执行时间 |
| `finished_at` | TEXT | 完成时间 |

### 4.3 任务类型枚举

- `book_summary`
- `notes_insight`
- `embedding_rebuild`
- `topic_graph_analysis`
- `vault_sync`

---

## 5. 状态机设计

所有异步任务统一走这套状态机：

`queued -> processing -> success / failed / canceled`

补充约束：

- `queued`：任务已创建，等待 worker 消费
- `processing`：worker 已开始执行
- `success`：结果写入缓存或任务表
- `failed`：执行失败，记录错误
- `canceled`：用户主动取消，第一期可以不实现 UI，但表结构先预留

建议同时记录：

- `progress`
- `message`

例如：

- `15%`: 正在加载书籍上下文
- `45%`: 正在调用大模型
- `80%`: 正在解析模型结果
- `100%`: 已完成

---

## 6. API 设计

### 6.1 创建任务

#### 书籍摘要

`POST /api/jobs/book-summary`

请求体：

```json
{
  "book_id": 12,
  "force": false
}
```

返回：

```json
{
  "job_id": "job_xxx",
  "status": "queued"
}
```

#### 笔记 AI 洞察

`POST /api/jobs/notes-insight`

请求体：

```json
{
  "book_id": 12,
  "q": "行动系统",
  "tag": "习惯",
  "chapter": "",
  "sort": "relevance"
}
```

### 6.2 查询任务状态

`GET /api/jobs/:job_id`

返回：

```json
{
  "id": "job_xxx",
  "job_type": "book_summary",
  "status": "processing",
  "progress": 60,
  "message": "正在生成摘要",
  "result": null
}
```

### 6.3 查询任务列表

`GET /api/jobs?job_type=book_summary&status=processing`

用于导入中心或后续“任务中心”。

### 6.4 任务结果读取

这里有两种方式：

#### 方式 A：任务完成后直接在状态接口里返回 `result`

适合摘要 / 洞察这类结果不大的任务。

#### 方式 B：任务完成后前端再调用原资源接口

比如：

- 轮询发现 `book_summary` 任务成功
- 再请求 `GET /api/books/:id/summary`

当前项目更推荐 **方式 B**，因为它和现在的前端结构更兼容。

---

## 7. 前端交互设计

### 7.1 书籍详情页

当前行为：

- 页面直接请求摘要

异步化后建议：

1. 页面先加载书基础信息
2. 如果摘要存在，直接显示
3. 如果摘要不存在，触发创建任务
4. 显示骨架屏和“正在生成摘要”
5. 轮询任务状态
6. 成功后刷新摘要区

### 7.2 笔记工作台 AI 洞察

当前行为：

- 点击“重新总结”后同步等待

异步化后建议：

1. 点击“重新总结”
2. 创建 `notes_insight` 任务
3. 右侧显示独立 loading 卡片
4. 轮询状态
5. 成功后替换右侧洞察内容

### 7.3 导入中心

当前行为：

- `sync-local` 同步后直接成功

异步化后建议：

- 显示“同步本地书库”与“Embedding 建索引”两个阶段
- 进度从单任务升级成链式任务展示

---

## 8. 后端代码拆分建议

为了让异步体系更清楚，建议新增这些文件：

### 8.1 Celery 入口

`backend/app/celery_app.py`

职责：

- 创建 Celery app
- 注入 Flask config
- 注册任务

### 8.2 任务仓储

`backend/app/services/job_repository.py`

职责：

- 创建任务
- 更新状态
- 保存结果
- 查询任务

### 8.3 任务定义

`backend/app/tasks/generation_tasks.py`

职责：

- `generate_book_summary_task`
- `generate_notes_insight_task`
- `rebuild_embeddings_task`
- `analyze_topic_graph_task`

### 8.4 任务接口

`backend/app/routes/jobs.py`

职责：

- 创建任务
- 查询任务状态
- 查询任务列表

---

## 9. 结果缓存策略

异步不是替代缓存，而是和缓存配合。

### 9.1 书籍摘要

- 任务完成后写入 `book_summaries`
- 同一本书再次打开优先读缓存
- 只有用户点击“重新生成”才创建新任务

### 9.2 AI 洞察

建议引入 `note_insights` 缓存表，主键可以是筛选条件的 hash：

- `book_id`
- `q`
- `tag`
- `chapter`
- `sort`

这样同一个筛选范围重复查看时，不需要每次重新生成。

### 9.3 图谱分析

图谱页也适合缓存，key 由这些条件组成：

- `mode`
- `category`
- `book_id`
- `time_scope`

---

## 10. 第一阶段落地顺序

不要一次实现全部，建议按下面顺序推进。

### Phase 1

先异步化 `book_summary`

原因：

- 改动面最小
- 用户收益最明显
- 最容易验证任务链路是否通畅

### Phase 2

异步化 `notes_insight`

原因：

- 这是第二个最典型的生成任务
- 可以直接复用同一套任务状态与轮询逻辑

### Phase 3

异步化 `embedding_rebuild`

原因：

- 它更偏底层能力
- 接入后可以显著改善导入和检索链路

### Phase 4

异步化 `topic_graph_analysis`

原因：

- 图谱已经可用，但不是当前第一痛点
- 放在后面最稳

---

## 11. 推荐的最小实现版本

如果你希望我们下一步直接开工，我建议先做一个“最小但完整”的异步版本：

### 后端

- 接入 `Celery + Redis`
- 新增 `async_jobs` 表
- 新增 `POST /api/jobs/book-summary`
- 新增 `GET /api/jobs/:job_id`
- 将 `POST /api/books/:id/summary/regenerate` 改成创建任务

### 前端

- 书籍详情页支持摘要任务轮询
- 增加“摘要生成中”状态
- 任务完成后自动刷新结果

做到这一步，异步任务体系就算真正落地了。

---

## 12. 面试里怎么讲

这块如果做出来，面试时可以这样描述：

> 项目早期所有 AI 能力都挂在同步请求里，导致首屏和交互容易被模型耗时阻塞。后面我把书籍摘要、笔记洞察、Embedding 预计算这类能力抽象成后台异步任务，通过任务状态表和统一状态机管理生成过程，前端只负责发起任务和轮询结果。这样既改善了用户等待体验，也让模型能力具备了可重试、可追踪、可缓存的工程基础。

这个表达会很像真实业务系统，而不是课程作业。

---

## 13. 下一步建议

下一步最值得直接实现的是：

1. 先落 `book_summary` 异步任务
2. 再复用这套机制做 `notes_insight`

这样风险最小，收益最大。
