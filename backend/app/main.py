import re
from contextlib import asynccontextmanager
from pathlib import Path

import edge_tts
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, AUDIO_CACHE_DIR
from app.database import init_db
from app.services.voice_service import preload_voices
from app.services import ragflow_service
from app.api import tts, voices, history, chat

# 前端静态文件目录（Vite 构建产物）
# 支持两种部署方式：
#   1. 独立后端（开发/本地）：前端独立运行，此目录不存在，跳过挂载
#   2. 合并部署（HF Spaces）：前端构建后放在此目录，由 FastAPI 托管
_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

_FILENAME_RE = re.compile(r"^[a-f0-9]{32}\.mp3$")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    await init_db()
    await preload_voices()
    await ragflow_service.init_client()
    yield
    # 关闭
    await ragflow_service.close_client()


app = FastAPI(
    title="Edge-TTS API",
    version="1.0.0",
    description="基于 edge-tts 的语音合成 API，支持 RAGFlow 对话集成",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（/api/v1 前缀）
API_PREFIX = "/api/v1"
app.include_router(tts.router, prefix=API_PREFIX)
app.include_router(voices.router, prefix=API_PREFIX)
app.include_router(history.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)


# ── 独立音频文件路由（顶层资源）────────────────────────────────
@app.get("/api/v1/audio/{filename}")
async def get_audio_file(filename: str):
    """
    获取音频文件。filename 只允许 MD5 格式（[a-f0-9]{32}.mp3），防止路径遍历攻击。
    文件不存在（已被 LRU 清理）返回 code=50003。
    """
    if not _FILENAME_RE.match(filename):
        return JSONResponse(
            status_code=400,
            content={"code": 40001, "msg": "非法文件名格式", "data": None},
        )
    file_path = AUDIO_CACHE_DIR / filename
    if not file_path.exists():
        return JSONResponse(
            status_code=200,
            content={"code": 50003, "msg": "音频文件不存在（已被自动清理）", "data": None},
        )
    return FileResponse(
        path=str(file_path),
        media_type="audio/mpeg",
        headers={"Accept-Ranges": "bytes"},
    )


# ── 前端静态文件（仅合并部署时生效）────────────────────────────────
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(_FRONTEND_DIST / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(_FRONTEND_DIST / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """SPA fallback：非 /api 路由一律返回 index.html，由前端路由处理。"""
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})
        file_path = _FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_FRONTEND_DIST / "index.html"))


# ── 健康检查 ─────────────────────────────────────────────────
@app.get("/api/v1/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "ragflow_configured": ragflow_service.is_configured(),
        "edge_tts_version": getattr(edge_tts, "__version__", "unknown"),
    }
