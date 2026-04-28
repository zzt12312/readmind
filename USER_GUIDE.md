# ReadMind 使用说明

## 1. 项目简介

ReadMind 是一个面向个人阅读笔记的 AI 整理系统。  
它会读取你本地 Obsidian 里的微信读书导出笔记，并提供：

- 书库浏览
- 笔记工作台
- AI 问答
- 书籍摘要
- 复习卡片

当前项目已经接入本地书库目录：

`/Users/taozhang/Documents/Obsidian Vault/书籍阅读`

## 2. 启动前准备

请确认本机已经安装：

- `Node.js`
- `npm`
- `Python 3`

并确认你已经在后端 `.env` 中配置好模型密钥，例如：

```env
SECRET_KEY=readmind-dev-secret
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

后端配置文件位置：

`/Users/taozhang/Desktop/maybe/backend/.env`

## 3. 启动命令

### 3.1 启动后端

```bash
cd /Users/taozhang/Desktop/maybe/backend
. .venv/bin/activate
python run.py
```

默认地址：

`http://127.0.0.1:5000`

### 3.2 启动前端

```bash
cd /Users/taozhang/Desktop/maybe/frontend
npm run dev
```

默认地址通常是：

`http://127.0.0.1:5173`

## 4. 首次使用流程

推荐你第一次按下面顺序操作：

1. 启动后端服务
2. 启动前端服务
3. 打开浏览器访问前端地址
4. 进入首页后，先看顶栏模型状态
5. 进入“导入中心”
6. 点击“同步本地书库”
7. 等待导入任务完成
8. 再去“我的书库”或“笔记工作台”查看内容

## 5. 页面说明

### 5.1 首页

首页会显示：

- 当前书籍总数
- 笔记总数
- 分类数
- 待复习数量
- 最近整理的书
- 当前活跃主题

适合快速确认系统是否已经正确读到你的本地书库。

### 5.2 导入中心

这里可以做两件事：

1. 点击“同步本地书库”
   系统会直接重新扫描：
   `/Users/taozhang/Documents/Obsidian Vault/书籍阅读`

2. 上传单个 Markdown 或压缩包
   用于测试额外导入能力

如果你的 Obsidian 书库有新增内容，优先使用“同步本地书库”。

### 5.3 我的书库

书库页会显示：

- 书名
- 作者
- 笔记条数
- 标签

你可以：

- 浏览自己的全部书籍
- 按关键词搜索书名、作者或标签
- 点击进入某本书的笔记

### 5.4 笔记工作台

这里会展示真实解析出的高亮内容，包括：

- 章节名
- 摘录内容
- 标签
- AI 洞察

适合集中查看某本书里你到底划了什么、关注了哪些主题。

### 5.5 智能问答

这是项目最核心的功能之一。

你可以直接提问，例如：

- “《纳瓦尔宝典》里关于财富和杠杆提到了什么？”
- “我关于长期主义记录过哪些内容？”
- “《乡土中国》里有哪些关于差序格局的摘录？”

系统会：

1. 在你的真实笔记中检索相关内容
2. 调用模型生成回答
3. 返回引用来源

右侧会显示引用卡片，帮助你追溯答案依据。

### 5.6 复习中心

复习中心会根据已解析的笔记生成待复习内容。

它适合做：

- 快速回顾高价值摘录
- 检查自己最近读书的吸收情况

## 6. 如何判断 AI 是否正常工作

看页面顶栏的模型状态徽章：

- `DeepSeek 已连接`
  表示当前模型连通正常，问答和摘要会优先走真实模型

- `本地回退中`
  表示模型当前不可用，系统会退回本地规则检索

- `未配置 DeepSeek`
  表示后端没有读到 `DEEPSEEK_API_KEY`

- `模型检查中`
  表示前端正在请求模型健康状态

## 7. 常见问题

### 7.1 页面打开了，但没有书

先去“导入中心”，点击：

`同步本地书库`

如果仍然没有内容，请检查目录是否存在：

`/Users/taozhang/Documents/Obsidian Vault/书籍阅读`

### 7.2 顶栏显示“未配置 DeepSeek”

检查：

`/Users/taozhang/Desktop/maybe/backend/.env`

是否包含：

```env
DEEPSEEK_API_KEY=你的key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

修改后要重启后端。

### 7.3 顶栏显示“本地回退中”

说明后端已经启动，但模型调用失败。常见原因：

- key 无效
- 余额或权限问题
- 网络问题
- 模型名错误

可以先确认后端 `.env` 配置是否正确，再重启服务。

### 7.4 后端启动失败

重新执行：

```bash
cd /Users/taozhang/Desktop/maybe/backend
. .venv/bin/activate
pip install -r requirements.txt
python run.py
```

### 7.5 前端启动失败

重新执行：

```bash
cd /Users/taozhang/Desktop/maybe/frontend
npm install
npm run dev
```

## 8. 推荐使用方式

比较顺的使用节奏是：

1. 每次更新 Obsidian 笔记后，先同步本地书库
2. 在书库里快速浏览最近读完或正在读的书
3. 在笔记工作台里查看高亮和主题
4. 在问答页围绕某一本书或某个主题提问
5. 在复习中心做回顾

## 9. 当前已知限制

当前版本仍然有这些限制：

- 数据主要来自微信读书导出的高亮 Markdown
- 解析器还不是完整的通用 Markdown 引擎
- 问答依赖当前已解析的摘录，不是完整知识图谱
- 复习逻辑目前是轻量版，不是完整 Anki 算法

## 10. 最重要的两个命令

后端：

```bash
cd /Users/taozhang/Desktop/maybe/backend && . .venv/bin/activate && python run.py
```

前端：

```bash
cd /Users/taozhang/Desktop/maybe/frontend && npm run dev
```
