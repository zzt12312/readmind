# ReadMind Frontend

ReadMind 前端基于 `Vue 3 + TypeScript + Vite + Element Plus` 构建，主要负责书库、笔记工作台、智能问答、主题图谱、复习中心和任务中心这些用户可见页面。

## 本地开发

```bash
cd frontend
npm install
npm run dev
```

说明：

- Vite 默认优先使用 `5173` 端口；如果端口被占用，会自动切到下一个可用端口，例如 `5174`
- 本地开发时，`/api` 会自动代理到 `http://127.0.0.1:5000`
- 启动前请先确认 Flask 后端已经运行

## 构建

```bash
npm run build
```

## 主要目录

```text
src/
├── api/            # 接口请求层
├── components/     # 基础组件、通用组件、图谱组件
├── constants/      # 路由常量等
├── layouts/        # 主布局
├── router/         # 路由配置
├── stores/         # Pinia 状态
├── styles/         # 全局样式和主题变量
├── types/          # TS 类型定义
└── views/          # 各页面视图
```

## 当前重点能力

- 书库与书籍详情
- 笔记工作台与 AI 洞察
- 单本书 / 全库问答
- 引用来源与跳转原笔记
- 复习卡片与主题复习
- 主题图谱与任务中心
