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

## ✨ 功能

- 🎙️ **TTS 合成**：400+ 种语音，支持语速/音量/音调调节，智能缓存
- ⚡ **流式播放**：边合成边播放，无需等待完整文件
- 📜 **历史记录**：自动保存，支持搜索、排序、批量删除
- 🤖 **AI 对话**（可选）：接入 RAGFlow 知识库，回复实时朗读
- 🌙 **暗色模式**：自动检测系统主题

## ⚙️ 环境变量配置（可选）

在 Spaces Settings → Variables 中配置以下变量以启用 AI 对话功能：

| 变量 | 说明 |
|------|------|
| `RAGFLOW_API_URL` | RAGFlow 服务地址 |
| `RAGFLOW_API_KEY` | RAGFlow API Key |
| `RAGFLOW_CHAT_ID` | RAGFlow 对话助手 ID |

## 🔗 项目主页

[GitHub - edge-tts-webui](https://github.com/your-username/edge-tts-webui)

属于 [OpenAvatarLab · 开源数字人实验室](https://github.com/your-username/OpenAvatarLab) 系列项目。
