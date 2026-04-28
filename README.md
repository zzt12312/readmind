# ReadMind

AI 阅读笔记整理与复习系统。当前仓库已经包含第一版前后端骨架：

- `frontend`: `Vue 3 + TypeScript + Vite + Element Plus`
- `backend`: `Flask`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

默认地址：

- `http://127.0.0.1:5173`

## Backend

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 然后编辑 .env，填入你自己的 DeepSeek 配置
python run.py
```

默认地址：

- `http://127.0.0.1:5000`

## Available API

- `GET /api/health`
- `GET /api/dashboard/overview`
- `GET /api/import/jobs`
- `GET /api/books`
- `GET /api/books/<id>/summary`
- `GET /api/notes`
- `POST /api/qa/ask`
- `GET /api/review/today`
- `GET /api/llm/health`

## Current Progress

当前已经完成：

- 前端全局布局、主题样式和核心页面壳子
- 登录页、首页、导入中心、书库、笔记工作台、问答页、复习页
- Flask app factory 和核心业务路由骨架
- 演示数据返回，便于前后端联调

下一步建议：

1. 接入真实后端 API 到前端页面
2. 接入数据库模型和迁移
3. 实现 Markdown 导入与解析链路
4. 接入 AI 摘要、分类和问答服务
