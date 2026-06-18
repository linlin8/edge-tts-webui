---
title: Edge-TTS WebUI
emoji: 🎙️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
short_description: Web UI for edge-tts — TTS synthesis, streaming, AI chat
---
# edge-tts-webui

基于 [edge-tts](https://github.com/rany2/edge-tts) 构建的 Web 界面与 REST API，支持文字转语音合成、流式播放、历史记录管理，并可选集成 [RAGFlow](https://github.com/infiniflow/ragflow) 实现 AI 对话转语音。

> A Web UI and REST API wrapper for edge-tts, with streaming playback, history management, and optional RAGFlow AI chat integration.

## ✨ 功能介绍

### 🎙️ TTS 合成

![TTS 合成页面](https://github.com/user-attachments/assets/677a2653-a589-4999-83d3-5c33cb735a3f)

选择语音 → 输入文字 → 一键合成 MP3。

- **400+ 种语音**：覆盖普通话、粤语、英语、日语等数十种语言，支持按语言/性别/关键词筛选
- **三维参数调节**：语速（-50%~+100%）、音量（-50%~+100%）、音调（-50Hz~+50Hz）实时预览
- **智能缓存**：相同文本+语音+参数组合自动复用缓存文件，无需重复合成
- **试听语音**：在选择语音前可先试听该语音的示例音频

### ⚡ 流式播放

点击「流式播放」，边合成边播放，无需等待完整文件生成。适合长文本场景。

### 📜 历史记录

![历史记录页面](https://github.com/user-attachments/assets/edcb5d45-dfd1-4034-9ff2-aa468b79b074)

每次合成自动保存，方便随时回听和管理。

- 支持按文本内容**搜索**历史记录
- 支持按**创建时间**或**文件大小**排序
- 支持**单条删除**、**勾选批量删除**、**一键清空**
- 历史音频可直接在页面内**在线播放**或**下载**

### 🤖 AI 对话（需配置 RAGFlow）

![AI 对话页面](https://github.com/user-attachments/assets/d6b5511e-f7a9-492e-8c53-9bc6e0b8a5f0)

接入 RAGFlow 知识库，实现基于私有文档的 AI 问答，并可将回复实时朗读。

- 回复以 **Markdown 格式渲染**，代码高亮、列表等格式完整支持
- 开启「回复转语音」后，AI 回复边生成**边自动朗读**，无需等待全文完成
- 语速/音量/音调参数与 TTS 合成页**统一设置，全局生效**
- 支持多轮会话，自动维护对话上下文

### 🌙 暗色模式

自动检测系统主题，也可手动切换。偏好设置本地持久化，刷新后保留。

### 💾 LRU 缓存管理

缓存音频文件数量可配置（默认上限 1000 个），超出后按最旧文件自动清理（近似 LRU），无需手动维护。

## 🏗️ 架构

```
┌─────────────────────────────────────────┐
│              Browser (Vue 3)            │
│  TTS Tab │ History Tab │ AI Chat Tab    │
└──────────────────┬──────────────────────┘
                   │ REST API / SSE
┌──────────────────▼──────────────────────┐
│         FastAPI Backend (port 8001)     │
│  /tts  │ /voices │ /history │ /chat     │
└──────┬───────────────────────┬──────────┘
       │                       │
  edge-tts                 RAGFlow API
  (Microsoft TTS)          (可选)
```

## 🚀 快速开始

### 后端

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
# macOS / Linux:
cp .env.example .env
# Windows PowerShell:
Copy-Item .env.example .env
# 编辑 .env，填写 RAGFlow 相关配置（可选）
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 前端

```bash
# 回到项目根目录后进入前端
cd ../frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

> 详细说明请参阅 [开发文档](docs/development.md)

## 📖 文档

| 文档 | 说明 |
|------|------|
| [开发环境搭建](docs/development.md) | 环境要求、目录结构、运行步骤 |
| [API 接口文档](docs/api.md) | 主要 REST API 端点详细说明 |
| [RAGFlow 配置教程](docs/ragflow-setup.md) | 如何获取 API Key 和 Chat ID |

交互式 API 文档：启动后访问 `http://localhost:8001/docs`

## 🛠️ 技术栈

**后端**
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- [edge-tts](https://github.com/rany2/edge-tts)（Microsoft Edge TTS 免费接口）
- [SQLAlchemy](https://www.sqlalchemy.org/) + aiosqlite（异步 SQLite）
- [httpx](https://www.python-httpx.org/)（异步 HTTP，用于 RAGFlow 通信）

**前端**
- [Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/)
- [TanStack Query](https://tanstack.com/query)（数据请求 & 缓存）
- [Tailwind CSS](https://tailwindcss.com/)
- [marked](https://marked.js.org/) + [DOMPurify](https://github.com/cure53/DOMPurify)（Markdown 安全渲染）

## 📋 配置项

复制 `backend/.env.example` 为 `backend/.env` 并按需修改：

| 变量 | 必填 | 说明 |
|------|------|------|
| `RAGFLOW_API_URL` | 否 | RAGFlow 服务地址 |
| `RAGFLOW_API_KEY` | 否 | RAGFlow API Key |
| `RAGFLOW_CHAT_ID` | 否 | RAGFlow 对话助手 ID |
| `CORS_ORIGINS` | 否 | 允许跨域的前端地址（逗号分隔） |
| `AUDIO_CACHE_MAX_FILES` | 否 | 缓存音频数量上限，默认 1000 |

## 📄 License

[MIT](LICENSE)

---

# edge-tts-webui

A Web UI and REST API wrapper built on [edge-tts](https://github.com/rany2/edge-tts), supporting TTS synthesis, streaming playback, history management, and optional [RAGFlow](https://github.com/infiniflow/ragflow) AI chat integration.

## ✨ Features

### 🎙️ TTS Synthesis

Select a voice → Enter text → Synthesize MP3 in one click.

- **400+ voices** across Mandarin, Cantonese, English, Japanese and more; filter by language, gender, or keyword
- **3-axis parameter control**: speed (-50%~+100%), volume (-50%~+100%), pitch (-50Hz~+50Hz) with live preview
- **Smart cache**: identical text+voice+param combos reuse cached files automatically
- **Voice preview**: listen to a sample before selecting

### ⚡ Streaming Playback

Click "Stream" to start playback while synthesis is still in progress — no waiting for the full file. Great for long texts.

### 📜 History

Every synthesis is saved automatically for easy replay and management.

- **Search** history by text content
- **Sort** by creation time or file size
- **Delete** individually, in bulk, or all at once
- **Play or download** audio directly in the page

### 🤖 AI Chat (requires RAGFlow)

Connect to a RAGFlow knowledge base for private-document Q&A with real-time TTS narration.

- Responses rendered as **Markdown** with syntax highlighting
- Enable "Read aloud" to have replies **narrated as they stream in**
- Speed/volume/pitch settings are **shared globally** with the TTS tab
- Multi-turn conversation with automatic context tracking

### 🌙 Dark Mode

Auto-detects system theme; manually toggle at any time. Preference is persisted locally.

### 💾 LRU Cache

Configurable audio file cache limit (default: 1000). Oldest files are cleaned up automatically (approximate LRU) — no manual maintenance needed.

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
# macOS / Linux:
cp .env.example .env
# Windows PowerShell:
Copy-Item .env.example .env
# Edit .env to add RAGFlow config (optional)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend

```bash
# From the backend directory, go back to project root first
cd ../frontend
npm install
npm run dev
# Open http://localhost:5173
```

> For detailed setup, see [Development Guide](docs/development.md)

## 📖 Documentation

| Doc | Description |
|-----|-------------|
| [Development Guide](docs/development.md) | Requirements, project structure, running steps |
| [API Reference](docs/api.md) | Main REST API endpoints with examples |
| [RAGFlow Setup](docs/ragflow-setup.md) | How to get API Key and Chat ID |

Interactive API docs: `http://localhost:8001/docs` (after starting backend)

## 🛠️ Tech Stack

**Backend**: FastAPI · edge-tts · SQLAlchemy · aiosqlite · httpx

**Frontend**: Vue 3 · Vite · TanStack Query · Tailwind CSS · marked · DOMPurify

## 📄 License

[MIT](LICENSE)
