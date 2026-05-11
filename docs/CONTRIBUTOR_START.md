# ReadMind 新手上手指南

这份文档给第一次接触项目的人用。目标是：先跑起来，再知道常见改动应该去哪里。

## 1. 项目是什么

ReadMind 是一个个人阅读知识工作台。它把 Obsidian/Markdown 阅读笔记整理成：

- 书库
- 笔记工作台
- AI 问答
- 知识图谱
- 复习中心
- 数据看板

项目分为两部分：

- `frontend/`：Vue 3 + TypeScript + Pinia 前端。
- `backend/`：Flask 后端，负责解析笔记、检索、问答、复习和导出。

## 2. 最快跑前端

```bash
cd frontend
npm install
npm run dev
```

如果只是想看公开演示效果，可以使用静态演示模式：

```bash
cd frontend
VITE_STATIC_DEMO=1 npm run dev
```

静态演示模式不会连接真实后端，也不会读取你的本地 Obsidian 数据。

## 3. 跑后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
flask --app app run --port 5001
```

后端默认读取 `.env` 中的配置。常见配置包括：

```bash
VAULT_ROOT=/path/to/your/obsidian/vault
DEMO_DATA_ONLY=0
```

如果你只想用演示数据：

```bash
DEMO_DATA_ONLY=1 flask --app app run --port 5001
```

## 4. 提交前检查

前端：

```bash
cd frontend
npm run build
```

后端：

```bash
pytest backend/tests
```

## 5. 常见任务应该改哪里

| 想做的事 | 主要位置 |
| --- | --- |
| 改首页 UI | `frontend/src/views/dashboard/` 和 `frontend/src/components/dashboard/` |
| 改书库卡片 | `frontend/src/views/books/BookLibraryView.vue` |
| 改问答页面 | `frontend/src/views/qa/QaCenterView.vue` 和 `frontend/src/components/qa/` |
| 改问答状态 | `frontend/src/stores/qa.ts` |
| 改本地会话保存 | `frontend/src/services/qaSessionStorage.ts` |
| 改静态演示数据 | `frontend/src/mock/staticDemo.ts` |
| 改后端问答接口 | `backend/app/routes/qa.py` |
| 改问答生成逻辑 | `backend/app/services/qa_service.py` |
| 改复习规则 | `backend/app/services/review/` |
| 改图谱数据 | `backend/app/services/graph/` |

## 6. 前端目录怎么理解

```text
frontend/src/api/          接口请求封装
frontend/src/components/   可复用 UI 组件
frontend/src/composables/  可复用交互逻辑
frontend/src/mock/         静态演示模式数据
frontend/src/services/     localStorage、SSE、导出等副作用
frontend/src/stores/       Pinia 状态
frontend/src/types/        TypeScript 类型
frontend/src/views/        页面组合
```

一个简单判断：

- 页面级组合放 `views/`。
- 能复用或能独立命名的 UI 放 `components/`。
- 不直接渲染 UI 的交互逻辑放 `composables/`。
- 会读写浏览器、网络、文件的逻辑放 `services/`。

## 7. 新增页面的推荐写法

页面文件应该尽量短。

推荐结构：

```text
View.vue
  负责加载数据、组合区块、路由跳转

components/<domain>/
  负责具体 UI

composables/
  负责复杂交互或派生计算
```

如果一个 Vue 文件超过 500 行，优先考虑拆组件。

## 8. 注释怎么写

好的注释解释“为什么”，不是重复“做了什么”。

推荐：

```ts
// Static demo mode replaces Axios requests in the browser.
// Keep URL routing here; keep demo payload construction in domain files.
```

不推荐：

```ts
// 设置 loading 为 true
loading.value = true
```

## 9. 现在最适合新人看的入口

建议按这个顺序读：

1. `frontend/src/views/dashboard/DashboardView.vue`
2. `frontend/src/components/dashboard/`
3. `frontend/src/api/client.ts`
4. `frontend/src/mock/staticDemo.ts`
5. `frontend/src/stores/qa.ts`
6. `backend/app/routes/qa.py`
7. `backend/app/services/qa_service.py`

