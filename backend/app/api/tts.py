import re
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import TTSRequest, ResponseBase
from app.services import tts_service
from app.config import AUDIO_CACHE_DIR

router = APIRouter(prefix="/tts", tags=["TTS"])

_FILENAME_RE = re.compile(r"^[a-f0-9]{32}\.mp3$")


@router.post("/synthesize")
async def synthesize(req: TTSRequest, db: AsyncSession = Depends(get_db)):
    """
    完整合成 TTS。
    副作用：同时写入一条历史记录（有意为之，缓存命中时也写入）。
    """
    if not req.text or not req.text.strip():
        return ResponseBase(code=40001, msg="文本不能为空")
    try:
        result = await tts_service.synthesize(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
            volume=req.volume,
            pitch=req.pitch,
            db=db,
        )
        return ResponseBase(data=result)
    except Exception as e:
        return ResponseBase(code=50001, msg=f"edge-tts 合成失败：{e}")


@router.post("/stream-token")
async def create_stream_token(req: TTSRequest):
    """申请一次性流式播放 token（TTL 5分钟）"""
    if not req.text or not req.text.strip():
        return ResponseBase(code=40001, msg="文本不能为空")
    token = await tts_service.create_stream_token(
        text=req.text,
        voice=req.voice,
        rate=req.rate,
        volume=req.volume,
        pitch=req.pitch,
    )
    stream_url = f"/api/v1/tts/stream/{token}"
    return ResponseBase(data={"token": token, "stream_url": stream_url})


@router.get("/stream/{token}")
async def stream_audio(token: str, request: Request):
    """
    凭 token 流式播放 MP3。token 一次性消耗。
    先在路由层完成 token 校验和消耗，再构造 StreamingResponse，
    确保错误可被路由层 try/except 捕获。
    """
    try:
        params = tts_service.consume_stream_token(token)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"code": 40004, "msg": "token 无效或已过期", "data": None},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"code": 50001, "msg": f"流式合成失败：{e}", "data": None},
        )

    async def audio_generator():
        async for chunk in tts_service.stream_audio_with_params(params):
            yield chunk

    return StreamingResponse(
        audio_generator(),
        media_type="audio/mpeg",
        headers={"Accept-Ranges": "none", "X-Accel-Buffering": "no"},
    )
