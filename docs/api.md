# API 接口文档

所有接口基址：`http://localhost:8001/api/v1`

## 统一响应格式

```json
{
  "code": 0,
  "msg": "ok",
  "data": {}
}
```

## 错误码

| code  | 含义 |
|-------|------|
| `0`   | 成功 |
| `40001` | 参数校验失败（文本为空、分页参数越界等） |
| `40004` | 资源不存在（流式 token 无效/已过期，或历史记录不存在） |
| `50001` | edge-tts 服务不可用（网络问题） |
| `50002` | RAGFlow 服务不可用或未配置 |
| `50003` | 音频文件不存在（已被 LRU 缓存清理） |

---

## TTS 模块

### POST `/tts/synthesize` — 完整合成

合成文字为 MP3 音频，结果缓存并写入历史记录。相同参数命中缓存时直接返回已有音频，同样写入历史记录。

**请求体**

```json
{
  "text": "你好，世界",
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "+0%",
  "volume": "+0%",
  "pitch": "+0Hz"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | ✅ | 合成文本，不能为空，**最多 5000 字，超出部分自动截断**（响应 `truncated` 字段标记） |
| `voice` | string | 否 | 语音短名，默认 `zh-CN-XiaoxiaoNeural` |
| `rate` | string | 否 | 语速，格式 `+25%` / `-10%`，默认 `+0%` |
| `volume` | string | 否 | 音量，格式同上，默认 `+0%` |
| `pitch` | string | 否 | 音调，格式 `+50Hz` / `-20Hz`，默认 `+0Hz` |

**响应**

```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "audio_url": "/api/v1/audio/abc123.mp3",
    "history_id": 1,
    "truncated": false,
    "file_size": 48620
  }
}
```

| 字段 | 说明 |
|------|------|
| `audio_url` | 音频文件地址，可直接用于 `<audio src>` 或下载 |
| `history_id` | 写入历史记录的 ID，可配合 `/history` 接口使用 |
| `truncated` | 文本是否因超出 5000 字被截断 |
| `file_size` | 音频文件大小（字节） |

---

### POST `/tts/stream-token` — 申请流式播放 Token

请求参数与 `/tts/synthesize` 相同。返回一次性 token，有效期 5 分钟。

**响应**

```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "token": "a1b2c3d4-...",
    "stream_url": "/api/v1/tts/stream/a1b2c3d4-..."
  }
}
```

---

### GET `/tts/stream/{token}` — 流式播放音频

凭 token 流式返回 MP3 音频字节流，**token 一次性消耗**，用后即失效。

**响应**

- 成功：`Content-Type: audio/mpeg`，流式返回 MP3 数据
- token 无效：HTTP 400，返回错误 JSON
- 合成失败：HTTP 500，返回错误 JSON

**使用示例**

```javascript
const { token } = data
const audio = new Audio(`/api/v1/tts/stream/${token}`)
audio.onerror = () => console.error('播放失败')
audio.play()
```

---

## 语音模块

### GET `/voices` — 获取语音列表

返回所有可用语音，支持三维过滤。结果有 1 小时 HTTP 缓存（`Cache-Control: public, max-age=3600`）。

**查询参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| `locale` | string | 语言地区，如 `zh-CN`、`en-US` |
| `gender` | string | 性别，`Male` 或 `Female` |
| `search` | string | 模糊搜索，匹配名称或地区 |

**响应**

```json
{
  "code": 0,
  "msg": "ok",
  "data": [
    {
      "ShortName": "zh-CN-XiaoxiaoNeural",
      "FriendlyName": "Microsoft Xiaoxiao Online (Natural) - Chinese (Mainland)",
      "Locale": "zh-CN",
      "Gender": "Female",
      "ContentCategories": ["General"],
      "VoicePersonalities": ["Warm", "Positive"]
    }
  ]
}
```

---

## 历史记录模块

### GET `/history` — 分页查询历史记录

**查询参数**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | int | 1 | 页码，≥ 1 |
| `page_size` | int | 20 | 每页条数，1~100 |
| `search` | string | - | 文本预览模糊搜索 |
| `order_by` | string | `created_at` | 排序字段：`created_at` / `file_size` |
| `order_dir` | string | `desc` | 排序方向：`asc` / `desc` |

**响应**

```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "total": 42,
    "page": 1,
    "page_size": 20,
    "total_pages": 3,
    "items": [
      {
        "id": 1,
        "text_preview": "你好，世界",
        "voice": "zh-CN-XiaoxiaoNeural",
        "rate": "+0%",
        "volume": "+0%",
        "pitch": "+0Hz",
        "audio_url": "/api/v1/audio/abc123.mp3",
        "audio_available": true,
        "file_size": 48620,
        "created_at": "2025-01-01T12:00:00"
      }
    ]
  }
}
```

> `audio_available: false` 表示音频已被 LRU 缓存清理，`audio_url` 为 `null`。

---

### DELETE `/history/all` — 删除全部历史

删除所有历史记录，并清空 `audio_cache/` 目录下的所有 MP3 文件。

**响应**

```json
{ "code": 0, "msg": "ok", "data": { "deleted_count": 42 } }
```

---

### DELETE `/history/{id}` — 删除单条历史记录

删除指定 ID 的历史记录，同时删除对应的音频文件（如果存在）。

**响应**

```json
{ "code": 0, "msg": "ok", "data": { "deleted_count": 1 } }
```

记录不存在时返回 `code: 40004`。

---

### POST `/history/batch-delete` — 批量删除

**请求体**

```json
{ "ids": [1, 2, 3] }
```

**响应**

```json
{ "code": 0, "msg": "ok", "data": { "deleted_count": 3 } }
```

---

## AI 对话模块

> 需要在 `.env` 中配置 RAGFlow 相关参数，否则接口返回未配置错误。  
> 参阅：[RAGFlow 配置教程](ragflow-setup.md)

### GET `/chat/status` — 查询 RAGFlow 配置状态

**响应**

```json
{ "code": 0, "msg": "ok", "data": { "configured": true } }
```

---

### POST `/chat/stream` — 流式 AI 对话（SSE）

发起 RAGFlow 对话，以 Server-Sent Events（SSE）格式流式返回。可选开启同步 TTS，在返回文本的同时将回复分句合成为音频 base64 数据。

**请求体**

```json
{
  "question": "你好，请介绍一下你自己",
  "session_id": null,
  "tts": false,
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "+0%",
  "volume": "+0%",
  "pitch": "+0Hz"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | string | ✅ | 用户问题 |
| `session_id` | string\|null | 否 | 会话 ID，传 `null` 开启新会话，传上次返回的 ID 续接 |
| `tts` | bool | 否 | 是否开启同步 TTS，默认 `false` |
| `voice` | string | 否 | TTS 语音，默认 `zh-CN-XiaoxiaoNeural` |
| `rate` | string | 否 | TTS 语速，默认 `+0%` |
| `volume` | string | 否 | TTS 音量，默认 `+0%` |
| `pitch` | string | 否 | TTS 音调，默认 `+0Hz` |

**响应格式**

`Content-Type: text/event-stream`，每条 SSE 数据格式：

```
data: {"type": "...", ...}

```

**事件类型**

| type | 说明 | 数据字段 |
|------|------|----------|
| `text` | 文字增量 | `delta`: 增量文本；`session_id`: 会话 ID |
| `audio` | 音频数据（`tts:true` 时） | `data`: Base64 编码的 MP3 字节 |
| `error` | 错误 | `msg`: 错误信息；`code`: 错误码 |
| `done` | 流结束 | - |

**前端消费示例**

```javascript
const resp = await fetch('/api/v1/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: '你好', tts: false })
})

const reader = resp.body.getReader()
const decoder = new TextDecoder()
let buffer = ''

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  buffer += decoder.decode(value, { stream: true })
  const lines = buffer.split('\n\n')
  buffer = lines.pop()
  for (const line of lines) {
    if (!line.startsWith('data:')) continue
    const event = JSON.parse(line.slice(5).trim())
    if (event.type === 'text') console.log(event.delta)
    if (event.type === 'done') console.log('结束')
  }
}
```

---

## 音频文件模块

### GET `/audio/{filename}` — 获取音频文件

获取已合成的 MP3 音频，支持流式传输和断点续传。`audio_url` 字段返回的地址即为此接口。

**响应**

- 成功：`Content-Type: audio/mpeg`，支持 `Accept-Ranges: bytes`（断点续传）
- 文件名格式错误：HTTP 400，`code: 40001`
- 文件不存在（已被 LRU 清理）：HTTP 200，`code: 50003`

**说明**

`filename` 为 MD5 + `.mp3`，例如 `8199...46ff.mp3`。可直接嵌入 `<audio>` 标签播放，也可通过 `Content-Disposition: attachment` 下载（前端已处理）。

---

## 健康检查

### GET `/health` — 健康状态

返回服务运行状态和版本信息，可用于监控和健康检测。

**响应示例**

```json
{
  "status": "ok",
  "version": "1.0.0",
  "ragflow_configured": true
}
```

| 字段 | 说明 |
|------|------|
| `status` | 始终为 `"ok"` |
| `version` | 当前应用版本 |
| `ragflow_configured` | RAGFlow 是否已配置（即 `.env` 中三个参数是否均有值） |
