import os
import math
from typing import Optional, Literal
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, desc, asc

from app.database import get_db
from app.models import History
from app.schemas import ResponseBase, BatchDeleteRequest
from app.config import AUDIO_CACHE_DIR

router = APIRouter(prefix="/history", tags=["History"])


@router.get("")
async def get_history(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    order_by: Literal["created_at", "file_size"] = "created_at",
    order_dir: Literal["asc", "desc"] = "desc",
    db: AsyncSession = Depends(get_db),
):
    """分页获取历史记录，支持搜索和排序"""
    # 参数边界校验
    if page < 1:
        return ResponseBase(code=40001, msg="page 必须 >= 1")
    if page_size < 1 or page_size > 100:
        return ResponseBase(code=40001, msg="page_size 必须在 1~100 之间")
    query = select(History)
    count_query = select(func.count(History.id))

    if search:
        like_expr = f"%{search}%"
        query = query.where(History.text_preview.like(like_expr))
        count_query = count_query.where(History.text_preview.like(like_expr))

    # 排序
    col = History.created_at if order_by == "created_at" else History.file_size
    sort_fn = desc if order_dir == "desc" else asc
    query = query.order_by(sort_fn(col))

    # 分页
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    result = await db.execute(query)
    rows = result.scalars().all()

    items = [
        {
            "id": r.id,
            "text_preview": r.text_preview,
            "voice": r.voice,
            "rate": r.rate,
            "volume": r.volume,
            "pitch": r.pitch,
            "audio_url": f"/api/v1/audio/{os.path.basename(r.audio_path)}" if r.audio_path else None,
            "audio_available": r.audio_path is not None,
            "file_size": r.file_size,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return ResponseBase(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, math.ceil(total / page_size)) if page_size > 0 else 1,
        "items": items,
    })


@router.delete("/all")
async def delete_all_history(db: AsyncSession = Depends(get_db)):
    """
    删除全部历史记录 + 清空 audio_cache 目录。
    路由必须注册在 /{id} 之前，防止 FastAPI 将 'all' 匹配为 {id}。
    """
    result = await db.execute(select(func.count(History.id)))
    count = result.scalar_one()

    await db.execute(delete(History))
    await db.commit()

    # 清空音频文件
    for f in AUDIO_CACHE_DIR.glob("*.mp3"):
        try:
            f.unlink()
        except Exception:
            pass

    return ResponseBase(data={"deleted_count": count})


@router.delete("/{history_id}")
async def delete_history(history_id: int, db: AsyncSession = Depends(get_db)):
    """删除单条历史记录 + 音频文件"""
    result = await db.execute(select(History).where(History.id == history_id))
    row = result.scalar_one_or_none()
    if not row:
        return ResponseBase(code=40004, msg="记录不存在")

    audio_path = row.audio_path
    await db.delete(row)
    await db.commit()

    if audio_path:
        try:
            os.remove(audio_path)
        except FileNotFoundError:
            pass

    return ResponseBase(data={"deleted_count": 1})


@router.post("/batch-delete")
async def batch_delete_history(
    req: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
):
    """批量删除指定历史记录 + 对应音频文件"""
    result = await db.execute(select(History).where(History.id.in_(req.ids)))
    rows = result.scalars().all()

    deleted = 0
    for row in rows:
        if row.audio_path:
            try:
                os.remove(row.audio_path)
            except FileNotFoundError:
                pass
        await db.delete(row)
        deleted += 1

    await db.commit()
    return ResponseBase(data={"deleted_count": deleted})
