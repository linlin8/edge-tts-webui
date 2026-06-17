import asyncio
import hashlib
import os
import time
import uuid
from pathlib import Path
from typing import AsyncGenerator, Optional

import aiofiles
import edge_tts
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.config import AUDIO_CACHE_DIR, AUDIO_CACHE_MAX_FILES
from app.models import History

# 全局并发信号量，保护所有 edge-tts 调用
_semaphore = asyncio.Semaphore(10)

# 流式 token 存储：{token: (params_dict, expire_time)}
_stream_tokens: dict = {}
_TOKEN_TTL = 300  # 5 分钟


def _make_cache_key(text: str, voice: str, rate: str, volume: str, pitch: str) -> str:
    raw = f"{text}|{voice}|{rate}|{volume}|{pitch}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _cleanup_expired_tokens():
    now = time.time()
    expired = [t for t, (_, exp) in _stream_tokens.items() if now > exp]
    for t in expired:
        _stream_tokens.pop(t, None)


async def _lru_cleanup(db: AsyncSession):
    """超过上限时删除最旧文件，并将 DB 对应记录 audio_path 置 NULL（批量提交，避免循环 commit）"""
    files = sorted(AUDIO_CACHE_DIR.glob("*.mp3"), key=lambda f: f.stat().st_mtime)
    if len(files) <= AUDIO_CACHE_MAX_FILES:
        return
    to_delete = files[: len(files) - AUDIO_CACHE_MAX_FILES]
    # 批量更新 DB
    audio_paths = [str(f) for f in to_delete]
    await db.execute(
        update(History)
        .where(History.audio_path.in_(audio_paths))
        .values(audio_path=None, file_size=0)
    )
    await db.commit()
    # 删除物理文件
    for f in to_delete:
        try:
            f.unlink()
        except FileNotFoundError:
            pass


async def synthesize(
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
    db: AsyncSession,
) -> dict:
    """完整合成，返回 {audio_url, history_id, truncated, file_size}"""
    truncated = False
    if len(text) > 5000:
        text = text[:5000]
        truncated = True

    cache_key = _make_cache_key(text, voice, rate, volume, pitch)
    audio_filename = f"{cache_key}.mp3"
    audio_path = AUDIO_CACHE_DIR / audio_filename
    audio_url = f"/api/v1/audio/{audio_filename}"

    # 缓存未命中：调用 edge-tts
    if not audio_path.exists():
        async with _semaphore:
            communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
            await communicate.save(str(audio_path))

    file_size = audio_path.stat().st_size if audio_path.exists() else 0

    # 无论缓存是否命中，都写入一条新历史记录
    history = History(
        text=text,
        text_preview=text[:50],
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
        audio_path=str(audio_path),
        file_size=file_size,
    )
    db.add(history)
    await db.commit()
    await db.refresh(history)

    # LRU 清理
    await _lru_cleanup(db)

    return {
        "audio_url": audio_url,
        "history_id": history.id,
        "truncated": truncated,
        "file_size": file_size,
    }


async def create_stream_token(
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> str:
    """生成一次性流式播放 token（TTL 5分钟）"""
    _cleanup_expired_tokens()
    token = str(uuid.uuid4()).replace("-", "")
    _stream_tokens[token] = (
        {"text": text, "voice": voice, "rate": rate, "volume": volume, "pitch": pitch},
        time.time() + _TOKEN_TTL,
    )
    return token


def consume_stream_token(token: str) -> dict:
    """
    校验并消耗 token，返回参数字典。
    若 token 无效或已过期，抛出 ValueError。
    必须在构造 StreamingResponse 之前调用，以确保错误可被路由层捕获。
    """
    _cleanup_expired_tokens()
    entry = _stream_tokens.pop(token, None)
    if entry is None:
        raise ValueError("token_invalid")
    params, _ = entry
    return params


async def stream_audio_with_params(params: dict) -> AsyncGenerator[bytes, None]:
    """根据参数流式输出 MP3 字节（不做 token 校验）"""
    async with _semaphore:
        communicate = edge_tts.Communicate(
            params["text"],
            params["voice"],
            rate=params["rate"],
            volume=params["volume"],
            pitch=params["pitch"],
        )
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]


async def synthesize_to_bytes(
    text: str,
    voice: str,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> bytes:
    """供 chat 模块调用，返回完整 MP3 字节"""
    async with _semaphore:
        communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume, pitch=pitch)
        buffer = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.extend(chunk["data"])
        return bytes(buffer)
