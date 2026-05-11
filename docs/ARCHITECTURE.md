# ReadMind 架构导览

这份文档解释项目的数据怎么流、模块怎么分工。它不是完整技术规格，而是给新人快速建立地图。

## 1. 总体结构

```text
Obsidian / Markdown
  -> backend parser
  -> SQLite / cache
  -> Flask API
  -> frontend api modules
  -> Pinia stores
  -> Vue views + components
```

静态演示模式的数据流不同：

```text
VITE_STATIC_DEMO=1
  -> Axios static demo adapter
  -> frontend/src/mock/staticDemo.ts
  -> Pinia stores
  -> Vue views + components
```

## 2. 前端层次

### 2.1 `views/`

页面组合层。

页面应该负责：

- 加载 store 数据。
- 组合多个区块组件。
- 做页面级路由跳转。
- 保留少量页面级布局。

页面不应该长期负责：

- 大段图表配置。
- 大段 CSS。
- 复杂 localStorage 读写。
- 复杂数据转换。

### 2.2 `components/`

UI 组件层。

例如首页已经拆成：

```text
components/dashboard/DashboardHero.vue
components/dashboard/FirstRunGuide.vue
components/dashboard/FirstValueReport.vue
components/dashboard/DashboardActionQueue.vue
components/dashboard/RecommendedReviewCard.vue
components/dashboard/RecentBookShelf.vue
components/dashboard/ActiveTopicList.vue
```

组件应该有清楚的名字，让新人看到文件名就知道它负责页面哪一块。

### 2.3 `stores/`

跨页面状态层。

Pinia store 负责：

- 页面需要共享的数据。
- 请求结果缓存。
- 用户当前操作状态。

store 不应该直接承担太多副作用。如果逻辑和 localStorage、SSE、导出文件有关，优先放到 `services/`。

### 2.4 `services/`

副作用和协议层。

典型例子：

- `qaSessionStorage.ts`：问答会话本地保存。
- `qaStreamClient.ts`：SSE 流式问答协议解析。

### 2.5 `composables/`

可复用交互逻辑。

例如：

- `useBookShelfDrag.ts`：首页最近书籍书架的拖拽和边缘阴影状态。
- `useJobPolling.ts`：后台任务轮询。

## 3. 后端层次

### 3.1 `routes/`

HTTP 接口层。

它应该负责：

- 读取请求参数。
- 调用 service。
- 返回 JSON。
- 处理 HTTP 错误码。

不要在 routes 里写太多业务规则。

### 3.2 `services/`

业务逻辑层。

常见目录：

```text
services/search/       检索和重排
services/review/       复习计划和 payload
services/graph/        图谱 payload
services/payloads/     页面聚合数据
```

### 3.3 `tests/`

测试层。

后端已有测试覆盖：

- 解析器
- 检索排序
- 复习调度
- 首页 payload
- 看板 payload
- 图谱 payload
- QA 导出和沉淀

改后端业务规则时，优先补对应测试。

## 4. 核心功能数据流

### 4.1 首页

```text
DashboardView.vue
  -> useDashboardStore()
  -> fetchDashboardOverview()
  -> GET /dashboard/overview
  -> backend/app/services/payloads/dashboard.py
```

静态演示模式：

```text
DashboardView.vue
  -> useDashboardStore()
  -> fetchDashboardOverview()
  -> staticDemo buildDashboard()
```

### 4.2 问答

```text
QaCenterView.vue
  -> useQaStore()
  -> streamQuestion()
  -> POST /qa/ask/stream
  -> retrieve references
  -> generate answer
  -> SSE meta / status / delta / done
  -> update assistant message
  -> persist session
```

问答沉淀：

```text
回答
  -> 保存为洞察卡片 / 加入复习 / 变成我的理解
  -> frontend store update
  -> POST /qa/deposits
  -> SQLite qa_deposits
```

### 4.3 笔记工作台

```text
NoteWorkbenchView.vue
  -> route query as source of truth
  -> useNotesStore()
  -> GET /notes
  -> notes payload + filters + insight
```

### 4.4 图谱

```text
TopicGraphView.vue
  -> getTopicGraph()
  -> backend graph payload
  -> TopicGraphChart.vue
```

图谱目前还需要继续重构：ECharts option 构造应该从页面抽到 composable。

### 4.5 复习

```text
ReviewCenterView.vue
  -> useReviewStore()
  -> GET /review/today
  -> rate card
  -> POST /review/rate
```

## 5. 演示模式和真实模式

ReadMind 有三种常见运行方式：

1. 静态演示模式  
   `VITE_STATIC_DEMO=1`，前端浏览器内使用 mock 数据。

2. 后端演示模式  
   `DEMO_DATA_ONLY=1`，后端使用预置缓存，不读取真实 Vault，也不调用外部模型。

3. 真实本地模式  
   后端读取本地 `VAULT_ROOT`，可调用外部模型。

写 UI 时要注意：不要假设所有模式都有真实后端任务，也不要假设所有模式都会调用模型。

## 6. 注释原则

需要注释的地方：

- 模块边界。
- 复杂业务规则。
- 兼容旧数据的迁移。
- 非直观图表或算法计算。

不需要注释的地方：

- 变量名已经说明清楚的简单赋值。
- 模板里明显的 UI 循环。

## 7. 健康边界

建议保持这些上限：

- 页面文件：尽量小于 500 行。
- 组件文件：尽量小于 350 行。
- store 文件：超过 400 行要考虑拆 service/composable。
- mock 文件：超过 500 行要按 domain 拆。

这些不是硬规则，但超过以后要有理由。

