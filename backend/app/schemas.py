from typing import Any, Optional
from pydantic import BaseModel


# ── 统一响应体 ──────────────────────────────────────────────
class ResponseBase(BaseModel):
    code: int = 0       # 0=成功
    msg: str = "ok"
    data: Any = None

# 错误码约定：
# 0     成功
# 40001 参数校验失败（文本为空/超长/非法字符）
# 40004 token 无效或已过期
# 50001 edge-tts 服务不可用
# 50002 RAGFlow 服务不可用
# 50003 音频文件不存在（已被 LRU 清理）


# ── TTS ─────────────────────────────────────────────────────
class TTSRequest(BaseModel):
    text: str                                    # 1-5000 字，超出自动截断
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"
    volume: str = "+0%"
    pitch: str = "+0Hz"


class StreamTokenResponse(BaseModel):
    token: str
    stream_url: str                              # GET /api/v1/tts/stream/{token}


# ── Chat ────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    tts: bool = False
    voice: Optional[str] = "zh-CN-XiaoxiaoNeural"
    rate: Optional[str] = "+0%"
    volume: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"


# ── History Batch Delete ─────────────────────────────────────
class BatchDeleteRequest(BaseModel):
    ids: list[int]
