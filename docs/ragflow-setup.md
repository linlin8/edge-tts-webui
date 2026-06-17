# RAGFlow 配置教程

本教程说明如何配置 RAGFlow 以启用 edge-tts-webui 的 AI 对话功能。

> **不使用 AI 对话？** RAGFlow 配置完全可选。不配置时，TTS 合成、流式播放、历史记录等功能照常使用，仅 AI 对话 Tab 会显示"RAGFlow 未配置"提示。

---

## RAGFlow 是什么？

[RAGFlow](https://github.com/infiniflow/ragflow) 是一个开源的 RAG（检索增强生成）框架，支持基于私有知识库的 AI 问答。edge-tts-webui 通过 RAGFlow 的 API 实现流式 AI 对话，并可将回复实时转换为语音朗读。

官方文档：https://ragflow.io/docs

---

## 前提条件

你需要有一个正在运行的 RAGFlow 实例，并且：
1. 已创建至少一个**对话助手（Chat）**
2. 可以访问 RAGFlow 的 Web 控制台

---

## 第一步：获取 API Key

1. 打开 RAGFlow Web 控制台
2. 点击右上角**头像**
3. 选择 **"API Key"** 菜单
4. 点击 **"Create new key"** 创建一个新 API Key
5. 复制生成的 Key（格式类似 `ragflow-xxxxxxxxxxxxxxxxx`）

> API Key 只显示一次，请立即保存！

---

## 第二步：获取 Chat ID

Chat ID 是某个对话助手的唯一标识，从浏览器地址栏获取：

1. 在 RAGFlow 控制台点击 **"Chat"** 菜单
2. 进入你想使用的对话助手
3. 查看浏览器地址栏，URL 格式类似：
   ```
   http://your-ragflow-server/chat/2465ed30634311f1acb15d0a47337c68
   ```
4. 末尾的 `2465ed30634311f1acb15d0a47337c68` 即为 Chat ID

---

## 第三步：填写到 `.env`

在 `backend/.env` 文件中填写以下内容：

```ini
# RAGFlow 服务地址（注意：不含末尾斜杠）
RAGFLOW_API_URL=http://your-ragflow-server:80

# 第一步获取的 API Key
RAGFLOW_API_KEY=ragflow-xxxxxxxxxxxxxxxxx

# 第二步获取的 Chat ID
RAGFLOW_CHAT_ID=2465ed30634311f1acb15d0a47337c68
```

---

## 第四步：重启后端并验证

重启后端服务：

```bash
# 停止当前后端，然后重新启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

打开 http://localhost:5173，切换到 **AI 对话** Tab：

- ✅ **配置成功**：输入框可用，可以发送消息
- ❌ **配置有误**：显示 "RAGFlow 未配置" 或报错提示

---

## 常见问题

**Q: 提示 "RAGFlow 未配置" 但我已经填写了 .env**  
A: 检查以下几点：
- `.env` 文件位置是否正确（应在 `backend/.env`，不是项目根目录）
- 填写的是 `.env` 还是 `.env.example`（必须是 `.env`）
- 修改 `.env` 后是否重启了后端服务

**Q: Chat ID 在哪里找？URL 里没有**  
A: 确认是进入了某个具体的对话助手详情页，而不是列表页。点击对话助手名称进入详情，URL 末尾即为 Chat ID。

**Q: 显示 "RAGFlow 服务不可用"**  
A: 
- 确认 RAGFlow 服务正在运行且可访问
- 检查 `RAGFLOW_API_URL` 地址是否正确（包括端口号）
- 网络防火墙是否允许后端访问该地址

**Q: AI 回复正常但没有语音**  
A: 确认在 AI 对话 Tab 中已开启"回复转语音"开关（输入框上方的切换按钮）。
