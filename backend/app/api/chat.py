import asyncio
import base64
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest
from app.services import ragflow_service
from app.services.ragflow_service import RagflowUnavailableError
from app.services.tts_service import synthesize_to_bytes

router = APIRouter(prefix="/chat", tags=["Chat"])

_PUNCT = set("。！？.!?")
_MAX_SENTENCE_LEN = 80
_ID_TAG_RE = __import__("re").compile(r"\[ID:\d+\]")  # RAGFlow 引用标记


def _should_break(buf: str) -> bool:
    """判断是否应该断句发送 TTS"""
    if not buf:
        return False
    if buf[-1] in _PUNCT:
        return True
    if len(buf) >= _MAX_SENTENCE_LEN:
        return True
    return False


async def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _generate(req: ChatRequest) -> AsyncGenerator[str, None]:
    buf = ""  # 待断句缓冲区
    try:
        async for chunk in ragflow_service.chat_stream(
            question=req.question,
            session_id=req.session_id,
        ):
            delta: str = chunk.get("delta", "")
            session_id: str = chunk.get("session_id", "")

            # 发送文字增量
            yield await _sse_event({"type": "text", "delta": delta, "session_id": session_id})

            # TTS 断句逻辑（去除引用标记，避免语音读出 [ID:0]）
            if req.tts:
                buf += _ID_TAG_RE.sub("", delta)
                if _should_break(buf):
                    sentence = _ID_TAG_RE.sub("", buf).strip()
                    buf = ""
                    if sentence:
                        try:
                            audio_bytes = await synthesize_to_bytes(
                                text=sentence,
                                voice=req.voice,
                                rate=req.rate or "+0%",
                                volume=req.volume or "+0%",
                                pitch=req.pitch or "+0Hz",
                            )
                            audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                            yield await _sse_event({"type": "audio", "data": audio_b64})
                        except Exception as e:
                            yield await _sse_event({"type": "error", "msg": str(e), "code": 50001})

        # 处理末尾未断句的缓冲
        if req.tts and buf.strip():
            try:
                audio_bytes = await synthesize_to_bytes(
                    text=_ID_TAG_RE.sub("", buf).strip(),
                    voice=req.voice,
                    rate=req.rate or "+0%",
                    volume=req.volume or "+0%",
                    pitch=req.pitch or "+0Hz",
                )
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                yield await _sse_event({"type": "audio", "data": audio_b64})
            except Exception as e:
                yield await _sse_event({"type": "error", "msg": str(e), "code": 50001})

    except RagflowUnavailableError as e:
        yield await _sse_event({"type": "error", "msg": str(e), "code": 50002})
    except asyncio.CancelledError:
        # 客户端断开，优雅退出
        return
    except Exception as e:
        yield await _sse_event({"type": "error", "msg": f"未知错误：{e}", "code": 50002})

    yield await _sse_event({"type": "done"})


@router.get("/status")
async def chat_status():
    """
    返回 RAGFlow 配置状态
    """
    from app.schemas import ResponseBase
    return ResponseBase(data={"configured": ragflow_service.is_configured()})


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """
    RAGFlow 对话 SSE 流式端点。
    事件类型：text / audio / error / done
    """
    if not ragflow_service.is_configured():
        async def _not_configured():
            yield await _sse_event({"type": "error", "msg": "RAGFlow 未配置，请在 .env 中填写相关参数", "code": 50002})
            yield await _sse_event({"type": "done"})

        return StreamingResponse(
            _not_configured(),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )

    return StreamingResponse(
        _generate(req),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
