from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.services.voice_service import get_voices
from typing import Optional

router = APIRouter(prefix="/voices", tags=["Voices"])

_CACHE_HEADERS = {"Cache-Control": "public, max-age=3600"}


@router.get("")
async def list_voices(
    locale: Optional[str] = None,
    gender: Optional[str] = None,
    search: Optional[str] = None,
):
    """获取语音列表，支持 locale/gender/search 三维过滤"""
    voices = await get_voices(locale=locale, gender=gender, search=search)
    # 只返回需要的字段
    result = [
        {
            "ShortName": v.get("ShortName", ""),
            "FriendlyName": v.get("FriendlyName", ""),
            "Locale": v.get("Locale", ""),
            "Gender": v.get("Gender", ""),
            "ContentCategories": v.get("VoiceTag", {}).get("ContentCategories", []),
            "VoicePersonalities": v.get("VoiceTag", {}).get("VoicePersonalities", []),
        }
        for v in voices
    ]
    return JSONResponse(
        content={"code": 0, "msg": "ok", "data": result},
        headers=_CACHE_HEADERS,
    )
