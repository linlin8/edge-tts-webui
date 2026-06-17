# 开发环境搭建与运行指南

## 环境要求

| 依赖 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.10+ | 后端运行环境 |
| Node.js | 18+ | 前端构建工具 |
| 网络连接 | - | **必须**，edge-tts 需要连接微软服务器合成语音 |

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/<your-username>/edge-tts-webui.git
cd edge-tts-webui
```

### 2. 配置后端

```bash
cd backend

# 推荐：创建 Python 虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制配置文件并按需修改
# macOS / Linux:
cp .env.example .env
# Windows PowerShell:
Copy-Item .env.example .env
# Windows CMD:
# copy .env.example .env
# 编辑 .env，填写 RAGFlow 相关配置（可选）
```

### 3. 启动后端

```bash
# 开发模式（含自动重载）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 生产模式（多 worker，仅限 Linux / macOS）
# 需额外安装 gunicorn：pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

后端启动后访问 `http://localhost:8001/docs` 查看交互式 API 文档。

### 4. 配置并启动前端

```bash
cd ../frontend

# 安装依赖
npm install

# 开发模式（含热更新）
npm run dev

# 生产构建
npm run build
```

前端默认运行在 `http://localhost:5173`，开发服务器已配置代理将 `/api` 请求转发到 `localhost:8001`。

## 项目目录结构

```
edge-tts-webui/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 路由层
│   │   │   ├── tts.py          # TTS 合成与流式播放
│   │   │   ├── voices.py       # 语音列表
│   │   │   ├── history.py      # 历史记录管理
│   │   │   └── chat.py         # RAGFlow AI 对话
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── tts_service.py  # TTS 合成、缓存、LRU、token
│   │   │   ├── voice_service.py# 语音列表缓存
│   │   │   └── ragflow_service.py # RAGFlow SSE 流式通信
│   │   ├── main.py             # FastAPI 应用入口
│   │   ├── config.py           # 环境变量配置
│   │   ├── database.py         # 数据库连接
│   │   ├── models.py           # SQLAlchemy ORM 模型
│   │   └── schemas.py          # Pydantic 请求/响应模型
│   ├── audio_cache/            # 合成音频缓存（自动创建，已 gitignore）
│   ├── .env                    # 本地环境配置（已 gitignore）
│   ├── .env.example            # 配置模板
│   ├── history.db              # SQLite 数据库（自动创建，已 gitignore）
│   └── requirements.txt        # Python 依赖
│
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js       # Axios 客户端，统一响应解包
│   │   ├── components/
│   │   │   ├── TTSForm.vue     # TTS 合成表单（文本输入、参数滑块）
│   │   │   ├── VoiceSelector.vue # 语音选择器（虚拟列表 + 搜索）
│   │   │   ├── AudioPlayer.vue # 音频播放器组件
│   │   │   ├── HistoryList.vue # 历史记录列表
│   │   │   ├── ChatPanel.vue   # AI 对话面板
│   │   │   └── ConfirmDialog.vue # 通用确认弹窗
│   │   ├── composables/
│   │   │   ├── useVoices.js    # 语音列表数据 hook
│   │   │   ├── useHistory.js   # 历史记录数据 hook
│   │   │   ├── useChat.js      # AI 对话 SSE hook
│   │   │   └── useAudioQueue.js# 音频队列顺序播放 hook
│   │   ├── styles/
│   │   │   └── index.css       # Tailwind 指令 + 自定义样式
│   │   ├── App.vue             # 根组件（Tab 切换、暗色模式）
│   │   └── main.js             # Vue 应用入口
│   ├── vite.config.js          # Vite 配置（含 API 代理）
│   ├── tailwind.config.js      # Tailwind 配置
│   └── package.json
│
├── docs/                       # 项目文档
│   ├── development.md          # 本文件
│   ├── api.md                  # API 接口文档
│   └── ragflow-setup.md        # RAGFlow 配置教程
│
├── .gitignore
├── LICENSE
└── README.md
```

## 开发注意事项

### 前端

- **热更新**：修改 `.vue`、`.js`、`.css` 文件后，浏览器自动刷新，无需手动操作
- **API 代理**：`vite.config.js` 中配置了 `/api` → `localhost:8001` 的代理，开发时无需处理跨域
- **暗色模式**：基于 Tailwind `darkMode: 'class'`，由 `App.vue` 顶层 div 的 `dark` class 控制

### 后端

- **自动重载**：使用 `--reload` 参数启动时，修改 Python 文件后自动重启
- **数据库**：首次启动自动创建 `backend/history.db`，使用 SQLite，无需额外配置
- **音频缓存**：合成结果保存在 `backend/audio_cache/`，相同参数（文本+语音+语速等）MD5 作为文件名，命中缓存仍写入历史记录
- **并发控制**：全局 Semaphore(10)，最多同时处理 10 个 TTS 合成请求

### 常见问题

**Q: TTS 合成失败，提示网络错误**  
A: edge-tts 需要连接微软服务器，请确保网络畅通，必要时配置代理。

**Q: AI 对话 Tab 显示"RAGFlow 未配置"**  
A: 请参阅 [RAGFlow 配置教程](ragflow-setup.md) 填写 `.env` 中的相关配置。

**Q: 修改 `.env` 后配置未生效**  
A: 需要重启后端服务，`.env` 在启动时读取一次。
