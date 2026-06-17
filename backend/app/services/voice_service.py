import asyncio
import time
from typing import Optional
from app.config import AUDIO_CACHE_DIR

_voices_cache: list = []
_cache_time: float = 0.0
_CACHE_TTL = 3600  # 1 小时
_lock = asyncio.Lock()


async def _load_voices() -> list:
    import edge_tts
    voices = await edge_tts.list_voices()
    return voices


async def get_all_voices() -> list:
    global _voices_cache, _cache_time
    now = time.time()
    if _voices_cache and (now - _cache_time) < _CACHE_TTL:
        return _voices_cache
    async with _lock:
        # 双重检查
        now = time.time()
        if _voices_cache and (now - _cache_time) < _CACHE_TTL:
            return _voices_cache
        _voices_cache = await _load_voices()
        _cache_time = time.time()
    return _voices_cache


async def get_voices(
    locale: Optional[str] = None,
    gender: Optional[str] = None,
    search: Optional[str] = None,
) -> list:
    voices = await get_all_voices()
    result = voices

    if locale:
        result = [v for v in result if v.get("Locale", "").lower() == locale.lower()]

    if gender:
        result = [v for v in result if v.get("Gender", "").lower() == gender.lower()]

    if search:
        kw = search.lower()
        result = [
            v for v in result
            if kw in v.get("ShortName", "").lower()
            or kw in v.get("FriendlyName", "").lower()
            or kw in v.get("Locale", "").lower()
        ]

    return result


async def preload_voices():
    """lifespan 启动时预加载"""
    await get_all_voices()
